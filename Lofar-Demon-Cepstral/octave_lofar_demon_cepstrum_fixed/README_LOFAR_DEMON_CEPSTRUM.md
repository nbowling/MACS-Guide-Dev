# LOFAR → DEMON → Cepstrum exercise in GNU Octave

## Purpose

This project is a teaching example, not a calibrated sonar processor. It creates a synthetic underwater-style acoustic signal whose known components can be followed through three related analyses:

1. **LOFAR-style analysis** shows persistent narrowband energy versus time and frequency.
2. **DEMON analysis** extracts low-frequency amplitude modulation from a higher-frequency analysis band.
3. **Real cepstrum** converts regular spacing between spectral components into peaks on a quefrency axis.

## Included files

- `lofar_demon_cepstrum_demo.m` — complete GNU Octave analysis.
- `synthetic_propeller_shaft.wav` — ready-to-use 60-second mono test signal.
- `generate_propeller_wav.py` — optional Python generator for recreating the WAV.

## Known signal truth

- Sample rate: **4000 Hz**
- Duration: **60 seconds**
- Mean shaft rate: **1.30 Hz**
- Shaft speed: **78 rpm**, because `rpm = 60 × shaft rate`
- Blade count: **5**
- Blade rate: **6.50 Hz**, because `blade rate = blade count × shaft rate`
- Machinery carriers: **150, 310, 620 and 900 Hz**
- Additional machinery tonals: **48 and 96 Hz**

The shaft rate varies slowly by ±0.025 Hz. This produces slight broadening rather than mathematically perfect lines.

## Installation

Install GNU Octave. The supplied analysis is intentionally self-contained and does **not** require the Octave `signal` package. It uses `audioread`, `fft`, `ifft`, plotting functions and local helper functions.

## Running the exercise

1. Put all files in one folder.
2. Start Octave.
3. Change Octave's current directory to that folder.
4. Run:

```octave
lofar_demon_cepstrum_demo
```

The script writes:

- `01_waveform.png`
- `02_lofar_spectrogram.png`
- `03_mean_lofar_spectrum.png`
- `04_demongram.png`
- `05_mean_demon_spectrum.png`
- `06_real_cepstrum.png`
- `demon_peaks.csv`

## What the synthetic signal contains

The generator combines four kinds of content.

### 1. Direct shaft and blade tonals

The low-frequency component contains sinusoids at the shaft rate, blade rate and twice the blade rate. These can appear directly in the LOFAR spectrum.

### 2. Amplitude-modulated carrier tonals

The carriers at 150, 310, 620 and 900 Hz are varied in amplitude at the shaft and blade rates. In a conventional spectrum this creates sidebands around each carrier:

```text
carrier ± shaft rate
carrier ± blade rate
```

DEMON discards the carrier frequency and retains the modulation pattern.

### 3. Modulated broadband noise

Coloured noise acts as a simplified cavitation-like broadband source. Its amplitude is modulated at shaft and blade rates. This makes the DEMON result less dependent on one pure carrier.

### 4. Ambient noise and slow rate variation

Random noise and slight shaft-rate variation prevent the example from being unrealistically perfect.

## LOFAR section

The script divides the signal into overlapping eight-second frames and applies a Hann window. Each frame is transformed with an FFT.

The nominal FFT-bin spacing is:

```text
Δf = sample rate / FFT length
```

A long frame gives fine frequency discrimination, but events are localised less precisely in time. The display subtracts the median of each time column. This is a display normalisation only; it helps narrow lines stand out against the broadband background.

Expected observations include the 48 and 96 Hz machinery lines, the carrier lines, and low-frequency energy near 1.30 and 6.50 Hz.

## DEMON section

DEMON means **Detection of Envelope Modulation on Noise**. In this exercise the sequence is:

1. Select the 100–1000 Hz analysis band.
2. Construct the analytic signal.
3. Take its magnitude to recover the amplitude envelope.
4. Remove the envelope mean.
5. Low-pass the envelope to 40 Hz.
6. Decimate from 4000 Hz to 200 Hz.
7. Analyse the envelope with another STFT/FFT.

Low-pass filtering before decimation is essential. Without it, modulation energy above the new Nyquist frequency could alias into the retained band.

The prominent DEMON families should occur near:

- **1.30 Hz**: shaft-rate modulation
- **6.50 Hz**: blade-rate modulation
- **13.00 Hz**: second blade-rate harmonic

Other sum, difference and harmonic components may appear because the signal contains several simultaneous modulation terms and noise.

## Cepstrum section

The script computes the real cepstrum as:

```text
c[n] = real{ IFFT( log( |FFT(x)| + ε ) ) }
```

Its horizontal axis is **quefrency**, measured in seconds. If spectral lines or sidebands are regularly spaced by `Δf`, the related quefrency is approximately:

```text
q = 1 / Δf
```

For this signal:

- blade spacing 6.50 Hz corresponds to about **0.1538 s**
- shaft spacing 1.30 Hz corresponds to about **0.7692 s**

Cepstral peaks should not be interpreted automatically as proof of a particular physical source. They identify periodic spacing. You still need to compare the result with LOFAR, DEMON, operating state and plausible machinery relationships.

## Suggested experiments

### Change blade count

Edit `BLADES` in the Python generator, recreate the WAV, then rerun Octave. If the shaft rate stays at 1.30 Hz:

- 4 blades → 5.20 Hz blade rate
- 5 blades → 6.50 Hz blade rate
- 7 blades → 9.10 Hz blade rate

### Change shaft speed

Edit `SHAFT_HZ`. For 96 rpm:

```text
shaft rate = 96 / 60 = 1.60 Hz
```

With five blades, the blade rate becomes 8.00 Hz.

### Compare LOFAR window lengths

Try four, eight and sixteen seconds. Observe how longer windows sharpen steady frequency lines while reducing time resolution.

### Change the DEMON band

Try `100–400 Hz`, `400–800 Hz` and `100–1000 Hz`. A modulation component may appear strongly in one band and weakly in another, depending on which carriers or noise bands are modulated.

### Remove direct low-frequency tonals

In the Python generator, temporarily remove the shaft and blade terms from `low`. DEMON should still recover modulation from the high-frequency carriers and broadband component. This demonstrates that DEMON is not merely displaying the original low-frequency waveform.

## Important limitations

- The frequency-domain filters are deliberately simple, sharp teaching filters. Production work normally uses carefully designed FIR/IIR filters, transient handling and calibration.
- The signal is synthetic and does not model propagation loss, hydrophone response, sea state, Doppler, multipath or a real cavitation spectrum.
- The automatic DEMON peak picker is intentionally simple.
- A DEMON line is evidence of modulation at that rate, not by itself proof that the line is shaft rate or blade rate.

## Optional WAV regeneration

Python requires NumPy and SciPy. From a terminal in the project folder:

```bash
python generate_propeller_wav.py
```

This overwrites `synthetic_propeller_shaft.wav` with a reproducible signal using a fixed random seed.
