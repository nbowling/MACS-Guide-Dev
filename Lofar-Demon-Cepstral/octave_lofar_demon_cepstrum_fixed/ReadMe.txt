In Octave (m) build the suggested LOFAR → DEMON → cepstrum analysis exercise in Octave, using an artificial propeller/shaft signal. Provide the source and if possible a .wav file for testing. If you are not able to provide a .wav file provide a python script to generate a suitable .wav file. Provide full documentation so I can understand what is going on.

I’ve built the complete exercise, including the Octave source, a ready-made WAV test signal, the Python generator, and detailed documentation. The Octave program is self-contained and does not require the Octave Signal package.

Complete package

Download the complete LOFAR–DEMON–cepstrum exercise

The ZIP contains:

lofar_demon_cepstrum_demo.m
synthetic_propeller_shaft.wav
generate_propeller_wav.py
README_LOFAR_DEMON_CEPSTRUM.md

You can also download the files separately:

Octave analysis source
Synthetic propeller and shaft WAV file
Python WAV generator
Full exercise documentation
Quick start

Extract the ZIP into a folder, start Octave, and change its working directory to that folder.

Then run:

lofar_demon_cepstrum_demo


The script generates:

01_waveform.png
02_lofar_spectrogram.png
03_mean_lofar_spectrum.png
04_demongram.png
05_mean_demon_spectrum.png
06_real_cepstrum.png
demon_peaks.csv

Signal characteristics

The supplied WAV has known parameters:

Sample rate: 4,000 Hz
Duration: 60 seconds
Mean shaft rate: 1.30 Hz
Shaft speed: 78 rpm
Propeller blades: 5
Blade rate: 6.50 Hz
Second blade-rate harmonic: 13.00 Hz
Machinery carriers: 150, 310, 620 and 900 Hz
Additional machinery tonals: 48 and 96 Hz

The relationship is:

Shaft speed=60×1.30=78 rpm\text{Shaft speed} = 60 \times 1.30 = 78\ \mathrm{rpm}

and:

Blade rate=5×1.30=6.50 Hz\text{Blade rate} = 5 \times 1.30 = 6.50\ \mathrm{Hz}

A small ±0.025 Hz shaft-rate variation is included so the signal is not unrealistically perfect.

What the program demonstrates
LOFAR analysis

The signal is divided into overlapping eight-second sections. Each section is Hann-windowed and transformed using an FFT.

The result is displayed as frequency against time, allowing you to identify:

shaft-rate energy;
blade-rate energy;
blade-rate harmonics;
48 and 96 Hz machinery lines;
carrier tonals at 150, 310, 620 and 900 Hz;
modulation sidebands around some carrier frequencies.

Octave’s fft computes a discrete Fourier transform using an FFT algorithm, with the optional FFT length controlling truncation or zero padding.

DEMON analysis

The DEMON processing chain is:

Original signal
      ↓
100–1000 Hz analysis band
      ↓
Analytic signal
      ↓
Envelope magnitude
      ↓
Remove envelope mean
      ↓
40 Hz low-pass filter
      ↓
Decimate from 4000 Hz to 200 Hz
      ↓
STFT / FFT of envelope
      ↓
DEMONgram and mean DEMON spectrum


You should find prominent modulation components near:

1.30 Hz    shaft rate
6.50 Hz    blade rate
13.00 Hz   second blade-rate harmonic


The program also runs a simple peak detector and writes its results to demon_peaks.csv.

Cepstrum

The real cepstrum is calculated as:

c[n]=real⁡{IFFT⁡(log⁡∣FFT⁡(x)∣)}c[n]=\operatorname{real}\left\{ \operatorname{IFFT} \left( \log\left|\operatorname{FFT}(x)\right| \right) \right\}

Regular frequency spacing becomes a feature on a quefrency axis:

q=1Δfq=\frac{1}{\Delta f}

For the supplied signal:

qblade=16.50=0.1538 sq_{\text{blade}}=\frac{1}{6.50}=0.1538\ \mathrm{s}

and:

qshaft=11.30=0.7692 sq_{\text{shaft}}=\frac{1}{1.30}=0.7692\ \mathrm{s}

The cepstrum plot marks both expected quefrencies.

Recommended first experiments

Once you have run the unmodified version, try these changes individually:

Change the LOFAR window from eight seconds to four and sixteen seconds.
Change the DEMON band from 100–1000 Hz to 100–400 Hz.
Change BLADES = 5 to BLADES = 7 in the Python generator.
Change SHAFT_HZ = 1.30 to SHAFT_HZ = 1.60.
Remove the direct shaft and blade tonals from the Python generator.

The final experiment is particularly informative. It demonstrates that DEMON can recover shaft and blade modulation from the higher-frequency carriers and broadband noise even when those frequencies are not inserted directly as low-frequency sinusoids.

The ZIP archive and WAV structure have been checked successfully. I could not execute the .m file here because GNU Octave is not installed in the execution environment, but the source uses core Octave-compatible functions and includes matching local helper functions.

error: 'hann_local' undefined near line 52, column 7error: called from    lofar_demon_cepstrum_demo at line 52 column 1

You’ve found a compatibility problem in my original file. Some Octave versions do not make helper functions at the bottom of a script available when the script begins executing, so hann_local() was not yet visible at line 52.

I’ve converted the script into a function file, which makes all the helper functions available reliably.

Corrected files
Download the corrected Octave source
Download the complete corrected package

Keep the corrected .m file and WAV file in the same directory, then run:

lofar_demon_cepstrum_demo_fixed


The important structural change is:

function lofar_demon_cepstrum_demo_fixed()

  % Main program code is here

endfunction


function w = hann_local(N)
  if N <= 1
    w = ones(N,1);
  else
    n = (0:N-1)';
    w = 0.5 - 0.5*cos(2*pi*n/(N-1));
  endif
endfunction


The main analysis is now a function, while hann_local, stft_local, analytic_local and the other routines are subfunctions in the same file. I have also checked the corrected ZIP archive for integrity.

This is great - thank you. One thing - can you reproduce the lofar_demon_cepstrum_demo_fixed.m in python. That can then be distributed with the MACS Guide, most people won't have access to Octave / Matlab.

Absolutely. A pure Python version is a very sensible companion for the MACS Guide, particularly because Python is free and much easier for readers to install across Windows, macOS and Linux.

I’ll reproduce the corrected Octave exercise as a Python program, keeping the same processing stages and outputs as closely as possible:

WAV loading
LOFAR/STFT analysis
mean LOFAR spectrum
DEMON envelope extraction
DEMONgram
mean DEMON spectrum and peak detection
real cepstrum
expected shaft/blade quefrency annotations
PNG plot exports
demon_peaks.csv
the same synthetic_propeller_shaft.wav test signal

I’ll also make the Python source heavily commented so that it works as teaching material, rather than merely being a translation of the Octave code.

Provide the complete Python source now, including installation and useage instructions

Absolutely. For distribution with the MACS Guide, I’ve made the Python version deliberately straightforward and educational rather than trying to be overly clever or compact. It follows essentially the same chain as the Octave exercise:

WAV → LOFAR/STFT → bandpass → Hilbert envelope → DEMON → peak detection → cepstrum

Downloads

Download the complete Python source

You can continue using the same test WAV:

Download the synthetic propeller/shaft WAV

And the generator is useful if somebody wants to recreate or modify the test recording:

Download the WAV generator

The Python source has also been syntax-checked successfully.

1. What the program requires

It uses only three third-party Python packages:

NumPy for numerical/FFT operations
SciPy for WAV reading, filtering, STFT, Hilbert transform, resampling and peak detection
Matplotlib for plotting

The DEMON section uses scipy.signal.hilbert() to construct the analytic signal. Taking its magnitude gives the amplitude envelope, which is exactly what we need for detecting modulation imposed on higher-frequency acoustic energy.

2. Installing Python

For the MACS Guide, I'd recommend Python 3.11 or later.

Readers can obtain Python from:

https://www.python.org/downloads/

On Windows, during installation it is useful to select:

Add Python to PATH

They can confirm installation from PowerShell or Command Prompt with:

python --version


or on some systems:

py --version

3. Installing the required packages

Open PowerShell, Command Prompt or a terminal and enter:

python -m pip install numpy scipy matplotlib


On Windows, if python isn't recognised but the Python launcher is:

py -m pip install numpy scipy matplotlib


That's all that is required.

For Linux, depending upon the installation:

python3 -m pip install numpy scipy matplotlib

4. Directory arrangement

Put these two files in the same directory:

MACS_Example/
│
├── lofar_demon_cepstrum_demo.py
└── synthetic_propeller_shaft.wav


For example:

C:\MACS\Python_Demo\


Open a terminal in that directory:

cd C:\MACS\Python_Demo


Then execute:

python lofar_demon_cepstrum_demo.py


or:

py lofar_demon_cepstrum_demo.py


Linux/macOS:

python3 lofar_demon_cepstrum_demo.py

5. What the program expects

The supplied test recording represents a deliberately simplified synthetic vessel.

The important known parameters are:

SHAFT_HZ = 1.30
BLADES = 5


Therefore:

SR=1.30 HzSR=1.30\text{ Hz}

Converting shaft rate to RPM:

RPM=60×1.30RPM=60\times 1.30

giving:

78 RPM\boxed{78\text{ RPM}}

With five propeller blades:

BR=Nb×SRBR=N_b\times SR

so:

BR=5×1.30BR=5\times1.30

and therefore:

BR=6.50 Hz\boxed{BR=6.50\text{ Hz}}

That is useful because we already know the answer. The purpose of the exercise is to see whether our different forms of analysis recover it.

6. Stage 1: Read the recording

The program starts with:

fs, x = load_wav(path)


fs is the sampling frequency.

For the supplied recording:

fs=4000 Hzf_s=4000\text{ Hz}

and x is the actual sequence of acoustic samples.

Stereo recordings are automatically converted to mono:

if x.ndim == 2:
    x = x.mean(axis=1)


The program also converts integer WAV samples into floating-point values and removes the DC component:

x -= np.mean(x)

7. Stage 2: LOFAR-style analysis

The first major analysis is:

f, tt, db, mag = stft_db(
    x,
    fs,
    LOFAR_WINDOW_S,
    LOFAR_OVERLAP,
    LOFAR_MAX_HZ
)


The important parameters are:

LOFAR_WINDOW_S = 8.0
LOFAR_OVERLAP = 0.75
LOFAR_MAX_HZ = 1000.0


The recording is divided into overlapping 8-second windows.

Each window is Hann windowed before its spectrum is calculated.

Conceptually:

Recorded acoustic signal

        ↓

 ┌─────────────┐
 │ 8 s window  │
 └─────────────┘
        ↓
   Hann window
        ↓
       FFT
        ↓
 Frequency bins
        ↓
 Move forward
        ↓
 Repeat


Stacking those spectra against time produces the LOFAR-style display.

8. Why eight seconds?

The window duration gives us an approximate frequency-bin separation of:

Δf=1T\Delta f=\frac{1}{T}

Therefore:

Δf=18\Delta f=\frac{1}{8}

giving:

0.125 Hz\boxed{0.125\text{ Hz}}

This is a rather nice parameter to experiment with.

Try:

LOFAR_WINDOW_S = 4.0


then:

LOFAR_WINDOW_S = 16.0


With 4 seconds:

Δf=0.25 Hz\Delta f=0.25\text{ Hz}

With 16 seconds:

Δf=0.0625 Hz\Delta f=0.0625\text{ Hz}

The student can therefore see the time/frequency-resolution trade-off, rather than merely reading about it.

9. Stage 3: DEMON analysis

This is probably the most interesting part for the MACS Guide.

The processing chain is:

Original acoustic signal
          │
          ▼
    100–1000 Hz
      bandpass
          │
          ▼
  Analytic signal
 Hilbert transform
          │
          ▼
      Magnitude
          │
          ▼
      Envelope
          │
          ▼
   Remove DC mean
          │
          ▼
     40 Hz LPF
          │
          ▼
Resample to 200 Hz
          │
          ▼
        STFT
          │
          ▼
      DEMONgram


The code begins:

y = bandpass(x, fs, *DEMON_BAND_HZ)


with:

DEMON_BAND_HZ = (100.0, 1000.0)


We're therefore deliberately looking at higher-frequency acoustic energy.

10. Envelope detection

Next comes the particularly important line:

env = np.abs(signal.hilbert(y))


SciPy's Hilbert function generates an analytic signal from the real acoustic signal. The magnitude of this analytic signal provides its amplitude envelope.

This is enormously useful for DEMON.

Suppose machinery/noise energy at 310 Hz is being amplitude modulated by the propeller blade rate:

fc=310 Hzf_c=310\text{ Hz}

and

fm=6.5 Hzf_m=6.5\text{ Hz}

The raw LOFAR spectrum may primarily show energy around the 310 Hz region and its sidebands.

Envelope detection effectively asks:

How is the strength of this higher-frequency sound varying with time?

The answer may reveal:

6.5 Hz6.5\text{ Hz}

even though we originally isolated the 100–1000 Hz part of the recording.

That's the fundamental idea behind this particular DEMON exercise.

11. Remove the envelope DC component

The envelope has a substantial mean value.

We don't want that dominating the spectrum, so:

env -= np.mean(env)


Conceptually this centres the envelope around zero.

12. Low-pass filtering

The analysis is interested only in modulation frequencies below 40 Hz:

DEMON_MAX_HZ = 40.0


so we apply:

signal.butter(...)
signal.sosfiltfilt(...)


as a low-pass filter.

Our important expected frequencies:

Shaft rate        1.30 Hz
Blade rate        6.50 Hz
2 × blade rate   13.00 Hz


are comfortably inside this bandwidth.

13. Downsampling

The original sampling frequency is:

4000 Hz4000\text{ Hz}

but there is absolutely no need to retain 4,000 samples per second to examine modulation below 40 Hz.

The program therefore resamples the envelope to approximately:

200 Hz200\text{ Hz}

This both reduces the processing burden and makes the DEMON analysis much more natural.

14. The DEMONgram

We now perform another STFT, but crucially it is performed on the envelope, not the original acoustic waveform:

df, dt, ddb, dmag = stft_db(
    env,
    dfs,
    DEMON_WINDOW_S,
    LOFAR_OVERLAP,
    DEMON_MAX_HZ
)


This generates:

04_demongram.png


and:

05_mean_demon_spectrum.png


You should look particularly around:

1.30 Hz1.30\text{ Hz} 6.50 Hz6.50\text{ Hz}

and:

13.00 Hz13.00\text{ Hz}
15. Automatic DEMON peak detection

The program also looks for spectral peaks:

peaks, properties = signal.find_peaks(...)


and prints the strongest candidates.

It also generates:

demon_peaks.csv


containing:

frequency_hz,magnitude_db,prominence_db


This is useful for the MACS exercise because students don't have to rely entirely on visually reading a graph.

The CSV can also be opened directly in Excel.

16. Stage 4: Cepstrum

Finally we perform:

spec = np.fft.fft(x * np.hanning(n))


followed by:

log_mag = np.log(np.maximum(np.abs(spec), 1e-12))


and:

cep = np.real(np.fft.ifft(log_mag))


In compact mathematical notation:

c(τ)=F−1[log⁡∣F(x(t))∣]c(\tau)= \mathcal F^{-1} \left[ \log\left|\mathcal F(x(t))\right| \right]

This moves us away from thinking purely in frequency.

Instead, we now have quefrency.

17. Quefrency

If spectral components have a repeating frequency spacing:

Δf\Delta f

then the associated cepstral quefrency is approximately:

q=1Δfq=\frac{1}{\Delta f}

For blade rate:

qBR=16.50q_{BR}=\frac{1}{6.50}

giving:

0.1538 s\boxed{0.1538\text{ s}}

The program marks that position.

It also marks the expected shaft quefrency:

qSR=11.30q_{SR}=\frac1{1.30}

giving:

0.7692 s\boxed{0.7692\text{ s}}

These are drawn directly onto:

06_real_cepstrum.png

18. Files generated

After successful execution the directory should look something like:

MACS_Example/
│
├── lofar_demon_cepstrum_demo.py
├── synthetic_propeller_shaft.wav
│
├── 01_waveform.png
├── 02_lofar_spectrogram.png
├── 03_mean_lofar_spectrum.png
├── 04_demongram.png
├── 05_mean_demon_spectrum.png
├── 06_real_cepstrum.png
│
└── demon_peaks.csv


That gives the student a nice logical progression:

RAW SIGNAL
    │
    ├────► LOFAR
    │        │
    │        └──► frequency-domain evidence
    │
    ├────► DEMON
    │        │
    │        └──► modulation evidence
    │
    └────► CEPSTRUM
             │
             └──► periodic-spacing evidence

Experiments I'd include in the MACS Guide

I would actually make these part of the exercise rather than simply leaving the program as a demonstration.

Experiment 1: Window length

Change:

LOFAR_WINDOW_S = 8.0


to:

LOFAR_WINDOW_S = 4.0


then:

LOFAR_WINDOW_S = 16.0


Compare the resulting LOFARgrams.

Experiment 2: Find SR

Give the student the DEMONgram without telling them that:

SR=1.30 HzSR=1.30\text{ Hz}

Ask them to estimate SR and convert it to RPM:

RPM=60SRRPM=60SR
Experiment 3: Determine blade count

If they identify:

SR=1.30SR=1.30

and:

BR=6.50BR=6.50

then:

Nb=BRSRN_b=\frac{BR}{SR}

so:

Nb=6.501.30=5N_b=\frac{6.50}{1.30}=5

Thus they have inferred the five-bladed propeller from the acoustic evidence.

Experiment 4: Alter the vessel

Use the supplied:

WAV generator

Change the shaft frequency and number of blades, regenerate the WAV and see whether the analyst can recover the new parameters without looking at the generator values first.

That is probably the most educational exercise of the lot.

I also think Python should become the primary version in the MACS Guide, with the Octave version retained as an alternative/appendix. Python lets us take this much further later, for example automatically marking SR, BR, BR harmonics and sideband families, estimating likely blade count, and eventually feeding the measurements into the sort of reverse acoustic analysis we've been developing.


****
Yes. The heading should be “Installation and Usage Instructions”, not “Useage”.

For the MACS Guide, I’d simplify the reader-facing instructions to this:

Python LOFAR, DEMON and Cepstrum Demonstration

This Python program demonstrates three basic acoustic-analysis techniques using a synthetic propeller/shaft recording:

LOFAR: examines frequency content over time.
DEMON: extracts low-frequency modulation associated with shaft and propeller activity.
Cepstrum: helps identify regularly spaced spectral components.

The supplied test signal represents:

Shaft rate: 1.30 Hz
Shaft speed: 78 RPM
Propeller: 5 blades
Blade rate: 6.50 Hz
1. Install Python

Install Python 3 from the Python website if it is not already installed.

Then install the three required packages:

python -m pip install numpy scipy matplotlib


On macOS or Linux you may need:

python3 -m pip install numpy scipy matplotlib

2. Required files

Place these files in the same directory:

lofar_demon_cepstrum_demo.py
synthetic_propeller_shaft.wav

3. Run the demonstration

Open a terminal or PowerShell in that directory and run:

python lofar_demon_cepstrum_demo.py


Alternatively, on macOS or Linux:

python3 lofar_demon_cepstrum_demo.py

4. Results

The program creates:

01_waveform.png
02_lofar_spectrogram.png
03_mean_lofar_spectrum.png
04_demongram.png
05_mean_demon_spectrum.png
06_real_cepstrum.png
demon_peaks.csv


These show the analysis progressing from the original signal through LOFAR, DEMON and cepstral analysis.

5. What to look for

The important frequencies in the test recording are:

Shaft Rate=1.30 Hz\text{Shaft Rate}=1.30\text{ Hz}

Therefore:

RPM=60×1.30=78 RPMRPM=60\times1.30=78\text{ RPM}

For a five-bladed propeller:

Blade Rate=5×1.30=6.50 Hz\text{Blade Rate}=5\times1.30=6.50\text{ Hz}

You should therefore look for evidence around:

1.30 Hz   Shaft Rate
6.50 Hz   Blade Rate
13.00 Hz  2nd Blade Rate harmonic


The purpose of the exercise is to see how these features appear differently in the LOFAR spectrum, DEMON spectrum and cepstrum.

6. Suggested experiment

Once the demonstration is working, change the acoustic parameters in the supplied WAV-generation program and create a new test signal.

Then analyse the new recording without referring to the values used to generate it.

Try to determine:

Shaft rate
Shaft RPM
Blade rate
Number of propeller blades

The blade count can be estimated from:

Nb=Blade RateShaft RateN_b=\frac{\text{Blade Rate}}{\text{Shaft Rate}}

For the supplied example:

Nb=6.501.30=5N_b=\frac{6.50}{1.30}=5

This turns the demonstration into a small acoustic-identification exercise rather than simply producing a set of graphs.

Main changes: I corrected “useage” → “usage”, removed most implementation detail from the installation section, and kept the explanation focused on what the MACS Guide reader needs to install, run, observe and experiment with.

Polished Guide section

Certainly. For the MACS Guide, I’d present it as a self-contained practical section that a reader can follow without needing to understand the Python code beforehand.

Practical Exercise: LOFAR, DEMON and Cepstrum Analysis Using Python
Introduction

This exercise provides a practical introduction to three complementary techniques used in acoustic signal analysis:

LOFAR analysis examines how spectral energy varies with frequency and time.
DEMON analysis examines low-frequency modulation present in higher-frequency acoustic energy.
Cepstrum analysis helps reveal periodic spacing between components in a spectrum.

A synthetic underwater acoustic recording is supplied with the exercise. Because the parameters used to generate the recording are known, the results of the analysis can be compared with the expected shaft and propeller characteristics.

The processing sequence is:

                    Acoustic WAV file
                          │
              ┌───────────┼───────────┐
              │           │           │
              ▼           ▼           ▼
            LOFAR        DEMON      Cepstrum
              │           │           │
              ▼           ▼           ▼
          Spectral     Modulation   Periodicity
          features      features     evidence


The exercise requires only Python and three freely available Python packages.

1. Test Signal

The supplied file:

synthetic_propeller_shaft.wav


represents a simplified synthetic vessel acoustic signature with the following deliberately chosen characteristics:

Parameter	ValueShaft Rate (SR)	1.30 Hz
Shaft speed	78 RPM
Number of propeller blades	5
Blade Rate (BR)	6.50 Hz
Second BR harmonic	13.00 Hz

The relationship between shaft frequency and shaft speed is:

RPM=60×SRRPM = 60 \times SR

Therefore:

RPM=60×1.30=78 RPMRPM = 60 \times 1.30 = \boxed{78\text{ RPM}}

Blade Rate is related to Shaft Rate by:

BR=Nb×SRBR = N_b \times SR

where NbN_b is the number of propeller blades.

For this recording:

BR=5×1.30=6.50 HzBR = 5 \times 1.30 = \boxed{6.50\text{ Hz}}

These known values provide useful reference points when interpreting the results.

2. Software Requirements

The demonstration requires Python 3 together with:

NumPy
SciPy
Matplotlib

If Python is not already installed, install a current Python 3 distribution before continuing.

Install the required packages

On Windows, open PowerShell or Command Prompt and enter:

python -m pip install numpy scipy matplotlib


If the Windows Python launcher is being used:

py -m pip install numpy scipy matplotlib


On macOS or Linux, the command may instead be:

python3 -m pip install numpy scipy matplotlib

3. Exercise Files

Place the following files in the same directory:

lofar_demon_cepstrum_demo.py
synthetic_propeller_shaft.wav


For example:

MACS_Python_Demo/
│
├── lofar_demon_cepstrum_demo.py
└── synthetic_propeller_shaft.wav

4. Running the Analysis

Open a terminal in the directory containing the files.

On Windows:

python lofar_demon_cepstrum_demo.py


or:

py lofar_demon_cepstrum_demo.py


On macOS or Linux:

python3 lofar_demon_cepstrum_demo.py


The program reads the WAV file, performs the three analyses and saves the results as image and data files.

5. Output Files

After the program has completed, the directory will contain:

01_waveform.png
02_lofar_spectrogram.png
03_mean_lofar_spectrum.png
04_demongram.png
05_mean_demon_spectrum.png
06_real_cepstrum.png
demon_peaks.csv


Each represents a different stage of the analysis.

01_waveform.png

The original acoustic waveform plotted against time.

02_lofar_spectrogram.png

A LOFAR-style time-frequency representation of the recording.

Examine this plot for persistent tonal components and other spectral structure.

03_mean_lofar_spectrum.png

The mean spectrum obtained from the LOFAR analysis.

This makes persistent spectral components easier to identify than in the time-frequency display alone.

04_demongram.png

A time-frequency display of the modulation information extracted from the acoustic signal.

Pay particular attention to activity around the expected Shaft Rate and Blade Rate.

05_mean_demon_spectrum.png

The mean DEMON spectrum.

For the supplied recording, examine the spectrum around:

 1.30 Hz    Shaft Rate
 6.50 Hz    Blade Rate
13.00 Hz    2 × Blade Rate

06_real_cepstrum.png

The real cepstrum of the signal.

Unlike the normal spectrum, its horizontal axis represents quefrency rather than frequency.

demon_peaks.csv

A list of peaks detected in the DEMON spectrum.

The CSV file can be opened in a text editor, spreadsheet or other analysis software.

6. LOFAR Analysis

The first stage divides the recording into short, overlapping sections and performs an FFT on each section.

Conceptually:

Acoustic signal
      │
      ▼
 Divide into windows
      │
      ▼
 Apply Hann window
      │
      ▼
     FFT
      │
      ▼
 Spectrum for each window
      │
      ▼
 Arrange spectra against time
      │
      ▼
 LOFAR-style display


The demonstration uses an 8-second analysis window.

A useful approximation for the associated frequency-bin spacing is:

Δf=1T\Delta f=\frac{1}{T}

so:

Δf=18=0.125 Hz\Delta f=\frac{1}{8}=0.125\text{ Hz}

The significance of the analysis-window length can be explored later in the exercise.

7. DEMON Analysis

DEMON analysis approaches the recording differently.

Rather than concentrating only on individual acoustic frequencies, the demonstration extracts changes in the amplitude of higher-frequency acoustic energy.

The processing sequence is:

          Acoustic signal
                │
                ▼
       100–1000 Hz band
                │
                ▼
        Analytic signal
                │
                ▼
        Extract envelope
                │
                ▼
        Remove DC/mean
                │
                ▼
          Low-pass filter
                │
                ▼
           Downsample
                │
                ▼
         Spectral analysis
                │
                ▼
            DEMONgram


The objective is to expose periodic modulation that may correspond to mechanical or propeller-related activity.

For the supplied recording, important frequencies to investigate are:

SR=1.30 HzSR=1.30\text{ Hz}

and:

BR=6.50 HzBR=6.50\text{ Hz}

together with the second Blade Rate harmonic:

2BR=13.00 Hz2BR=13.00\text{ Hz}
8. Determining Shaft Speed

Once a likely Shaft Rate has been identified, it can be converted to revolutions per minute.

Use:

RPM=60×SRRPM = 60 \times SR

For example, if the analysis indicates:

SR=1.30 HzSR=1.30\text{ Hz}

then:

RPM=60×1.30RPM=60\times1.30

giving:

RPM=78\boxed{RPM=78}

Thus a frequency measurement obtained from the acoustic analysis can be related to a physical characteristic of the propulsion system.

9. Estimating Propeller Blade Count

If both Shaft Rate and Blade Rate can be identified, the number of propeller blades can be estimated from:

Nb=BRSRN_b=\frac{BR}{SR}

For the supplied example:

Nb=6.501.30N_b=\frac{6.50}{1.30}

therefore:

Nb=5\boxed{N_b=5}

This is an important analytical relationship.

It allows three observations to support one another:

Shaft Rate ─────────────► 1.30 Hz
                              │
                              │ × 5
                              ▼
Blade Rate ─────────────► 6.50 Hz
                              │
                              │ × 2
                              ▼
BR harmonic ────────────► 13.00 Hz


A set of related frequencies of this type can provide stronger evidence than treating each tonal independently.

10. Cepstrum Analysis

Cepstral analysis provides another way of looking for repetitive structure.

The real cepstrum can be expressed as:

c(τ)=F−1[log⁡∣F(x(t))∣]c(\tau)= \mathcal{F}^{-1} \left[ \log\left|\mathcal{F}(x(t))\right| \right]

The resulting horizontal axis is conventionally called quefrency.

If spectral components exhibit a regular spacing Δf\Delta f, the corresponding quefrency is approximately:

q=1Δfq=\frac{1}{\Delta f}

For the 6.50 Hz Blade Rate:

qBR=16.50q_{BR}=\frac{1}{6.50}

giving:

qBR≈0.154 s\boxed{q_{BR}\approx0.154\text{ s}}

For the 1.30 Hz Shaft Rate:

qSR=11.30q_{SR}=\frac{1}{1.30}

giving:

qSR≈0.769 s\boxed{q_{SR}\approx0.769\text{ s}}

These expected positions are marked on the cepstrum produced by the demonstration program.

11. Practical Exercises

Once the demonstration has been run successfully, use the following exercises to explore the analysis further.

Exercise 1: Change the LOFAR window

Locate:

LOFAR_WINDOW_S = 8.0


Change it first to:

LOFAR_WINDOW_S = 4.0


Run the program again.

Then try:

LOFAR_WINDOW_S = 16.0


Compare the resulting LOFAR displays.

Calculate the approximate frequency-bin spacing for each window using:

Δf=1T\Delta f=\frac{1}{T}

Consider how changing window duration affects the presentation of the signal.

Exercise 2: Determine shaft speed

Without referring to the known value, examine the DEMON results and estimate the Shaft Rate.

Convert your estimate to RPM using:

RPM=60×SRRPM=60\times SR

Compare your result with the known value of 78 RPM.

Exercise 3: Estimate the number of propeller blades

Identify possible Shaft Rate and Blade Rate components from the analysis.

Calculate:

Nb=BRSRN_b=\frac{BR}{SR}

Round the result only when the acoustic evidence justifies interpreting it as a whole number of blades.

For the supplied recording, the expected result is:

Nb=5\boxed{N_b=5}
Exercise 4: Analyse an Unknown Signal

The most useful extension is to generate another synthetic recording using different shaft and propeller parameters.

Do not examine the values used to generate the recording during the analysis.

Treat it as an unknown contact and attempt to determine:

Shaft Rate
Shaft RPM
Blade Rate
Blade Rate harmonics
Likely number of propeller blades

Compare your estimates with the generating parameters only after completing the analysis.

12. Summary

This exercise demonstrates how several analysis methods can provide complementary information about the same acoustic signal.

                       ACOUSTIC SIGNAL
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
        LOFAR               DEMON              CEPSTRUM
          │                   │                   │
          ▼                   ▼                   ▼
   Spectral features    Modulation rates    Periodic spacing
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                     CORRELATE EVIDENCE
                              │
                              ▼
                 Shaft Rate / Blade Rate
                              │
                              ▼
                    Propulsion inference


The important point is not simply to identify a line at 1.30 Hz or 6.50 Hz, but to recognise relationships between observations.

For this synthetic example:

SR=1.30 HzSR=1.30\text{ Hz} RPM=60SR=78 RPMRPM=60SR=78\text{ RPM} BR=5SR=6.50 HzBR=5SR=6.50\text{ Hz} 2BR=13.00 Hz2BR=13.00\text{ Hz}

and:

Nb=BRSR=5N_b=\frac{BR}{SR}=5

The LOFAR, DEMON and cepstral results can therefore be considered together, giving the analyst several complementary views of the same underlying synthetic propulsion signature.

Editorial changes: I’ve turned the earlier instructions into a guide-ready section with a clear progression from installation to interpretation, reduced programming detail, standardised the terminology and equations, and added practical exercises so the section teaches the analysis rather than only explaining how to run the program.

You're very welcome. I think it fits the MACS Guide particularly well because it gives the reader a chance to apply the theory to a known signal rather than just reading about LOFAR, DEMON and cepstral analysis.

I especially like the progression:

known synthetic signature → observe the acoustic evidence → derive SR → calculate RPM → identify BR → infer blade count

That closes the loop nicely between the mathematics, the plots and the physical machinery that produced the signature.

I'm glad it's useful.
