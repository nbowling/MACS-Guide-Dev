#!/usr/bin/env python3
"""Educational LOFAR -> DEMON -> cepstrum demonstration for the MACS Guide."""
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal

WAV_FILE = "synthetic_propeller_shaft.wav"
SHAFT_HZ = 1.30
BLADES = 5
BLADE_HZ = SHAFT_HZ * BLADES
LOFAR_WINDOW_S = 8.0
LOFAR_OVERLAP = 0.75
LOFAR_MAX_HZ = 1000.0
DEMON_BAND_HZ = (100.0, 1000.0)
DEMON_FS = 200.0
DEMON_MAX_HZ = 40.0
DEMON_WINDOW_S = 8.0


def load_wav(path):
    fs, x = wavfile.read(path)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if np.issubdtype(x.dtype, np.integer):
        info = np.iinfo(x.dtype)
        x = x.astype(np.float64) / max(abs(info.min), info.max)
    else:
        x = x.astype(np.float64)
    x -= np.mean(x)
    return float(fs), x


def stft_db(x, fs, window_s, overlap, max_hz):
    nperseg = int(round(window_s * fs))
    noverlap = int(round(nperseg * overlap))
    f, t, z = signal.stft(x, fs=fs, window="hann", nperseg=nperseg,
                          noverlap=noverlap, detrend=False, boundary=None,
                          padded=False)
    mag = np.abs(z)
    db = 20.0 * np.log10(np.maximum(mag, 1e-12))
    keep = f <= max_hz
    return f[keep], t, db[keep], mag[keep]


def save_spectrogram(f, t, db, title, filename, vmax_span=60):
    plt.figure(figsize=(11, 6))
    vmax = np.percentile(db, 99)
    plt.pcolormesh(t, f, db, shading="auto", cmap="viridis",
                   vmin=vmax-vmax_span, vmax=vmax)
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.title(title)
    plt.colorbar(label="Magnitude (dB)")
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close()


def save_mean_spectrum(f, mag, title, filename, xlim):
    mean_mag = np.mean(mag, axis=1)
    db = 20*np.log10(np.maximum(mean_mag, 1e-12))
    plt.figure(figsize=(11, 5))
    plt.plot(f, db)
    plt.xlim(*xlim)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Mean magnitude (dB)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close()
    return mean_mag


def bandpass(x, fs, low, high):
    nyq = fs/2
    high = min(high, nyq*0.98)
    sos = signal.butter(6, [low, high], btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)


def demon_envelope(x, fs):
    # Isolate higher-frequency acoustic energy before envelope detection.
    y = bandpass(x, fs, *DEMON_BAND_HZ)
    # The magnitude of the analytic signal is its amplitude envelope.
    env = np.abs(signal.hilbert(y))
    env -= np.mean(env)
    # Retain only modulation frequencies of interest before resampling.
    sos = signal.butter(6, DEMON_MAX_HZ, btype="lowpass", fs=fs, output="sos")
    env = signal.sosfiltfilt(sos, env)
    # Polyphase resampling supplies anti-alias filtering and supports arbitrary rates.
    from fractions import Fraction
    ratio = Fraction(int(round(DEMON_FS)), int(round(fs))).limit_denominator()
    env_ds = signal.resample_poly(env, ratio.numerator, ratio.denominator)
    fs_ds = fs * ratio.numerator / ratio.denominator
    return fs_ds, env_ds


def find_demon_peaks(f, mean_mag):
    db = 20*np.log10(np.maximum(mean_mag, 1e-12))
    mask = (f >= 0.2) & (f <= DEMON_MAX_HZ)
    ff, dd = f[mask], db[mask]
    peaks, properties = signal.find_peaks(dd, prominence=3.0, distance=max(1, int(len(ff)/300)))
    rows = sorted(zip(ff[peaks], dd[peaks], properties["prominences"]),
                  key=lambda r: r[1], reverse=True)[:20]
    with open("demon_peaks.csv", "w", newline="") as fp:
        w = csv.writer(fp)
        w.writerow(["frequency_hz", "magnitude_db", "prominence_db"])
        w.writerows(rows)
    return rows


def real_cepstrum(x, fs):
    # Use the full recording for this simple teaching example.
    n = len(x)
    spec = np.fft.fft(x * np.hanning(n))
    log_mag = np.log(np.maximum(np.abs(spec), 1e-12))
    cep = np.real(np.fft.ifft(log_mag))
    q = np.arange(n)/fs
    return q, cep


def main():
    path = Path(WAV_FILE)
    if not path.exists():
        raise SystemExit(f"Cannot find {WAV_FILE!r}. Put it in the same folder as this script.")

    fs, x = load_wav(path)
    duration = len(x)/fs
    print(f"Loaded {path}: {fs:.0f} Hz, {duration:.2f} s")
    print(f"Expected shaft rate: {SHAFT_HZ:.2f} Hz ({SHAFT_HZ*60:.1f} rpm)")
    print(f"Expected blade rate: {BLADE_HZ:.2f} Hz ({BLADES} blades)")

    # 1. Waveform
    t = np.arange(len(x))/fs
    plt.figure(figsize=(11, 4))
    plt.plot(t, x, linewidth=0.6)
    plt.xlabel("Time (s)"); plt.ylabel("Amplitude")
    plt.title("Synthetic propeller/shaft acoustic signal")
    plt.tight_layout(); plt.savefig("01_waveform.png", dpi=160); plt.close()

    # 2. LOFAR-style STFT
    f, tt, db, mag = stft_db(x, fs, LOFAR_WINDOW_S, LOFAR_OVERLAP, LOFAR_MAX_HZ)
    save_spectrogram(f, tt, db, "LOFAR-style spectrogram", "02_lofar_spectrogram.png")
    save_mean_spectrum(f, mag, "Mean LOFAR spectrum", "03_mean_lofar_spectrum.png", (0, LOFAR_MAX_HZ))

    # 3. DEMON analysis
    dfs, env = demon_envelope(x, fs)
    df, dt, ddb, dmag = stft_db(env, dfs, DEMON_WINDOW_S, LOFAR_OVERLAP, DEMON_MAX_HZ)
    save_spectrogram(df, dt, ddb, "DEMONgram", "04_demongram.png")
    mean_demon = save_mean_spectrum(df, dmag, "Mean DEMON spectrum", "05_mean_demon_spectrum.png", (0, DEMON_MAX_HZ))
    peaks = find_demon_peaks(df, mean_demon)

    # 4. Real cepstrum
    q, cep = real_cepstrum(x, fs)
    qmax = 1.2
    keep = (q > 0.01) & (q <= qmax)
    plt.figure(figsize=(11, 5))
    plt.plot(q[keep], cep[keep])
    plt.axvline(1/BLADE_HZ, color="tab:red", linestyle="--", label=f"Blade quefrency 1/{BLADE_HZ:.2f} Hz")
    plt.axvline(1/SHAFT_HZ, color="tab:orange", linestyle="--", label=f"Shaft quefrency 1/{SHAFT_HZ:.2f} Hz")
    plt.xlabel("Quefrency (s)"); plt.ylabel("Cepstral amplitude")
    plt.title("Real cepstrum")
    plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
    plt.savefig("06_real_cepstrum.png", dpi=160); plt.close()

    print("\nStrongest DEMON peaks:")
    for hz, dbv, prom in peaks[:10]:
        print(f"  {hz:7.3f} Hz   {dbv:8.2f} dB   prominence {prom:5.2f} dB")
    print("\nCreated 01-06 PNG plots and demon_peaks.csv")

if __name__ == "__main__":
    main()
