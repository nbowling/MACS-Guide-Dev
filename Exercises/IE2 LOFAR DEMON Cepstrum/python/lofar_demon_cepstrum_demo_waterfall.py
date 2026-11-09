#!/usr/bin/env python3
"""LOFAR, DEMON and real-cepstrum teaching exercise.

Waterfall convention used here:
    x-axis = frequency (Hz)
    y-axis = time (s)

The supplied synthetic_propeller_shaft.wav is expected in the same folder.
"""

from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal

WAV_FILE = "synthetic_propeller_shaft.wav"

# Known teaching-signal parameters
SHAFT_HZ = 1.30
BLADES = 5
BLADE_HZ = SHAFT_HZ * BLADES

# LOFAR settings
LOFAR_WINDOW_S = 8.0
LOFAR_OVERLAP = 0.75
LOFAR_MAX_HZ = 1000.0
LOFAR_DISPLAY_MAX_HZ = 1000.0

# DEMON settings
DEMON_BAND_HZ = (100.0, 1000.0)
DEMON_MAX_HZ = 40.0
DEMON_DISPLAY_MAX_HZ = 15.0
DEMON_SAMPLE_HZ = 200.0
DEMON_WINDOW_S = 8.0

EPS = 1e-12


def load_wav(path):
    fs, x = wavfile.read(path)
    if x.ndim == 2:
        x = x.astype(np.float64).mean(axis=1)
    else:
        x = x.astype(np.float64)
    peak = np.max(np.abs(x))
    if peak > 0:
        x /= peak
    x -= np.mean(x)
    return float(fs), x


def stft_magnitude(x, fs, window_s, overlap, max_hz):
    nperseg = max(16, int(round(window_s * fs)))
    nperseg = min(nperseg, len(x))
    noverlap = int(round(nperseg * overlap))
    noverlap = min(noverlap, nperseg - 1)

    f, t, z = signal.stft(
        x,
        fs=fs,
        window="hann",
        nperseg=nperseg,
        noverlap=noverlap,
        nfft=nperseg,
        boundary=None,
        padded=False,
        detrend=False,
    )
    keep = f <= max_hz
    return f[keep], t, np.abs(z[keep, :])


def db20(mag):
    return 20.0 * np.log10(np.maximum(mag, EPS))


def percentile_limits(a, low=5.0, high=99.5):
    finite = a[np.isfinite(a)]
    if finite.size == 0:
        return -60.0, 0.0
    vmin, vmax = np.percentile(finite, [low, high])
    if vmax <= vmin:
        vmax = vmin + 1.0
    return float(vmin), float(vmax)


def save_waveform(x, fs):
    t = np.arange(len(x)) / fs
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(t, x, linewidth=0.55)
    ax.set(title="Synthetic propeller/shaft waveform", xlabel="Time (s)", ylabel="Normalised amplitude")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("01_waveform.png", dpi=160)
    plt.close(fig)


def save_lofar(x, fs):
    f, t, mag = stft_magnitude(x, fs, LOFAR_WINDOW_S, LOFAR_OVERLAP, LOFAR_MAX_HZ)
    raw_db = db20(mag)

    # Display fix: remove each time slice's broadband median. This stops the
    # strong low-frequency/background energy from setting the entire colour scale.
    relative_db = raw_db - np.median(raw_db, axis=0, keepdims=True)
    vmin, vmax = percentile_limits(relative_db)

    fig, ax = plt.subplots(figsize=(11, 7))
    # Traditional waterfall orientation: frequency on x, time on y.
    mesh = ax.pcolormesh(f, t, relative_db.T, shading="auto", cmap="viridis", vmin=vmin, vmax=vmax)
    ax.set(title="LOFAR-style waterfall", xlabel="Frequency (Hz)", ylabel="Time (s)")
    ax.set_xlim(0, LOFAR_DISPLAY_MAX_HZ)
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label("Relative magnitude (dB)")
    fig.tight_layout()
    fig.savefig("02_lofar_spectrogram.png", dpi=160)
    plt.close(fig)

    mean_mag = np.mean(mag, axis=1)
    mean_db = db20(mean_mag / max(np.max(mean_mag), EPS))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(f, mean_db, linewidth=0.8)
    ax.set(title="Mean LOFAR spectrum", xlabel="Frequency (Hz)", ylabel="Relative magnitude (dB)")
    ax.set_xlim(0, LOFAR_DISPLAY_MAX_HZ)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("03_mean_lofar_spectrum.png", dpi=160)
    plt.close(fig)


def bandpass(x, fs, lo, hi):
    nyq = fs / 2.0
    hi = min(hi, nyq * 0.98)
    if not (0 < lo < hi):
        raise ValueError("DEMON band must lie inside the WAV Nyquist frequency.")
    sos = signal.butter(6, [lo, hi], btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)


def demon_envelope(x, fs):
    y = bandpass(x, fs, *DEMON_BAND_HZ)
    env = np.abs(signal.hilbert(y))
    env -= np.mean(env)

    # Keep only modulation frequencies used by the exercise.
    sos = signal.butter(6, DEMON_MAX_HZ, btype="lowpass", fs=fs, output="sos")
    env = signal.sosfiltfilt(sos, env)

    # Rational resampling to ~200 Hz.
    from fractions import Fraction
    ratio = Fraction(DEMON_SAMPLE_HZ / fs).limit_denominator(10000)
    env = signal.resample_poly(env, ratio.numerator, ratio.denominator)
    dfs = fs * ratio.numerator / ratio.denominator
    env -= np.mean(env)
    return env, dfs


def save_demon(x, fs):
    env, dfs = demon_envelope(x, fs)
    f, t, mag = stft_magnitude(env, dfs, DEMON_WINDOW_S, LOFAR_OVERLAP, DEMON_MAX_HZ)
    raw_db = db20(mag)
    relative_db = raw_db - np.median(raw_db, axis=0, keepdims=True)
    vmin, vmax = percentile_limits(relative_db)

    fig, ax = plt.subplots(figsize=(11, 7))
    mesh = ax.pcolormesh(f, t, relative_db.T, shading="auto", cmap="viridis", vmin=vmin, vmax=vmax)
    ax.set(title="DEMON waterfall", xlabel="Modulation frequency (Hz)", ylabel="Time (s)")
    ax.set_xlim(0, DEMON_DISPLAY_MAX_HZ)
    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label("Relative magnitude (dB)")

    # Expected values are reference markers, not detected classifications.
    ax.axvline(SHAFT_HZ, color="white", linestyle="--", linewidth=1.0, label=f"Expected SR {SHAFT_HZ:.2f} Hz")
    ax.axvline(BLADE_HZ, color="red", linestyle="--", linewidth=1.0, label=f"Expected BR {BLADE_HZ:.2f} Hz")
    ax.axvline(2 * BLADE_HZ, color="orange", linestyle=":", linewidth=1.0, label=f"Expected 2BR {2*BLADE_HZ:.2f} Hz")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig("04_demongram.png", dpi=160)
    plt.close(fig)

    mean_mag = np.mean(mag, axis=1)
    mean_db = db20(mean_mag / max(np.max(mean_mag), EPS))
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(f, mean_db, linewidth=0.9)
    ax.axvline(SHAFT_HZ, color="grey", linestyle="--", linewidth=1)
    ax.axvline(BLADE_HZ, color="red", linestyle="--", linewidth=1)
    ax.axvline(2 * BLADE_HZ, color="orange", linestyle=":", linewidth=1)
    ax.set(title="Mean DEMON spectrum", xlabel="Modulation frequency (Hz)", ylabel="Relative magnitude (dB)")
    ax.set_xlim(0, DEMON_MAX_HZ)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig("05_mean_demon_spectrum.png", dpi=160)
    plt.close(fig)

    # Peak table, excluding DC neighbourhood.
    mask = (f >= 0.5) & (f <= DEMON_MAX_HZ)
    ff = f[mask]
    yy = mean_db[mask]
    peaks, props = signal.find_peaks(yy, prominence=3.0)
    rows = sorted(
        [(float(ff[p]), float(yy[p]), float(props["prominences"][i])) for i, p in enumerate(peaks)],
        key=lambda r: r[2], reverse=True
    )
    with open("demon_peaks.csv", "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["frequency_hz", "magnitude_db", "prominence_db"])
        writer.writerows(rows)


def save_cepstrum(x, fs):
    # Use up to 60 s, Hann-windowed, for the teaching cepstrum.
    n = min(len(x), int(round(60.0 * fs)))
    xx = x[:n] * np.hanning(n)
    spectrum = np.fft.fft(xx)
    cep = np.real(np.fft.ifft(np.log(np.maximum(np.abs(spectrum), EPS))))
    q = np.arange(n) / fs

    keep = (q >= 0.02) & (q <= 1.0)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(q[keep], cep[keep], linewidth=0.75)
    ax.axvline(1.0 / BLADE_HZ, color="red", linestyle="--", linewidth=1.0, label=f"1/BR = {1/BLADE_HZ:.3f} s")
    ax.axvline(1.0 / SHAFT_HZ, color="grey", linestyle="--", linewidth=1.0, label=f"1/SR = {1/SHAFT_HZ:.3f} s")
    ax.set(title="Real cepstrum", xlabel="Quefrency (s)", ylabel="Cepstral amplitude")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig("06_real_cepstrum.png", dpi=160)
    plt.close(fig)


def main():
    path = Path(WAV_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Cannot find {WAV_FILE!r}. Put it in the same directory as this script.")

    fs, x = load_wav(path)
    print(f"Loaded {path.name}: {len(x)/fs:.2f} s at {fs:.0f} Hz")
    print(f"Reference SR={SHAFT_HZ:.2f} Hz, RPM={60*SHAFT_HZ:.1f}, BR={BLADE_HZ:.2f} Hz")

    save_waveform(x, fs)
    save_lofar(x, fs)
    save_demon(x, fs)
    save_cepstrum(x, fs)

    print("Created 01_waveform.png through 06_real_cepstrum.png and demon_peaks.csv")


if __name__ == "__main__":
    main()
