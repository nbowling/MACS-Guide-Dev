function lofar_demon_cepstrum_demo_fixed()
% lofar_demon_cepstrum_demo.m
% Educational LOFAR -> DEMON -> real-cepstrum exercise for GNU Octave.
% It reads synthetic_propeller_shaft.wav and writes plots and CSV results.
%
% Expected synthetic truth:
%   mean shaft rate = 1.30 Hz = 78 rpm
%   blade count     = 5
%   blade rate      = 6.50 Hz
%
% Run from the folder containing this file and the WAV file:
%   lofar_demon_cepstrum_demo
%
% This script uses core Octave functions only. No signal package is required.

close all; clc;

wav_name = "synthetic_propeller_shaft.wav";
if exist(wav_name, "file") ~= 2
  error("Cannot find %s. Put the WAV file in the current folder.", wav_name);
endif

[x, fs] = audioread(wav_name);
if columns(x) > 1
  x = mean(x, 2);                 % stereo -> mono if needed
endif
x = x(:);
x = x - mean(x);                 % remove DC offset
x = x / (max(abs(x)) + eps);      % normalise safely
N = length(x);
t = (0:N-1)' / fs;
fprintf("Loaded %s: %.1f s at %d Hz, %d samples\n", wav_name, N/fs, fs, N);

% Ground truth used by the supplied generator.
shaft_truth_hz = 1.30;
blade_count = 5;
blade_truth_hz = shaft_truth_hz * blade_count;

%% 1. Time waveform
fig = figure("visible", "off");
plot(t, x, "b"); grid on;
xlabel("Time (s)"); ylabel("Normalised amplitude");
title("Synthetic propeller / machinery waveform");
xlim([0, min(10, t(end))]);
print(fig, "01_waveform.png", "-dpng", "-r150"); close(fig);

%% 2. LOFAR-style spectrogram
% Long windows improve frequency resolution but reduce time resolution.
lofar_win_s = 8.0;
L = round(lofar_win_s * fs);
hop = round(L / 4);               % 75 percent overlap
nfft = 2^nextpow2(L);
win = hann_local(L);
[S, f_lofar, t_lofar] = stft_local(x, fs, L, hop, nfft, win);
Pdb = 20*log10(abs(S) + 1e-12);
% Column-wise median removal makes persistent lines easier to see.
Pdisplay = Pdb - median(Pdb, 1);
keep = f_lofar <= 1000;
fig = figure("visible", "off");
imagesc(t_lofar, f_lofar(keep), Pdisplay(keep,:)); axis xy;
xlabel("Time (s)"); ylabel("Frequency (Hz)");
title(sprintf("LOFAR-style spectrogram, %.3f Hz bin spacing", fs/nfft));
colormap(jet(256)); colorbar; caxis([-45 5]);
hold on;
plot([t_lofar(1), t_lofar(end)], [shaft_truth_hz, shaft_truth_hz], "w--", "linewidth", 1);
plot([t_lofar(1), t_lofar(end)], [blade_truth_hz, blade_truth_hz], "w--", "linewidth", 1);
hold off;
print(fig, "02_lofar_spectrogram.png", "-dpng", "-r150"); close(fig);

%% 3. Average narrowband spectrum
avg_mag = mean(abs(S), 2);
avg_db = 20*log10(avg_mag / (max(avg_mag)+eps) + 1e-12);
fig = figure("visible", "off");
plot(f_lofar(keep), avg_db(keep), "k"); grid on;
xlabel("Frequency (Hz)"); ylabel("Relative magnitude (dB)");
title("Mean LOFAR spectrum"); xlim([0 1000]); ylim([-80 3]);
hold on;
plot([shaft_truth_hz shaft_truth_hz], [-80 3], "r--");
plot([blade_truth_hz blade_truth_hz], [-80 3], "m--");
hold off;
print(fig, "03_mean_lofar_spectrum.png", "-dpng", "-r150"); close(fig);

%% 4. DEMON processing
% DEMON looks for periodic amplitude modulation on higher-frequency energy.
% Steps: analysis band -> analytic signal -> magnitude envelope -> remove mean
% -> low-pass envelope -> decimate -> FFT of envelope.
band_low = 100; band_high = 1000;
xb = fft_bandpass_local(x, fs, band_low, band_high);
z = analytic_local(xb);
env = abs(z);
env = env - mean(env);
env_lp = fft_lowpass_local(env, fs, 40);

% Decimate only after low-pass filtering. 4000/20 = 200 Hz output rate.
decim = 20;
env_d = env_lp(1:decim:end);
fs_d = fs / decim;
t_d = (0:length(env_d)-1)' / fs_d;

% DEMONgram: short-time spectrum of the envelope.
demon_L = round(12 * fs_d);
demon_hop = round(2 * fs_d);
demon_nfft = 4096;
demon_win = hann_local(demon_L);
[D, f_dem, t_dem] = stft_local(env_d, fs_d, demon_L, demon_hop, demon_nfft, demon_win);
Ddb = 20*log10(abs(D)+1e-12);
Ddisplay = Ddb - median(Ddb, 1);
keep_dem = f_dem <= 25;
fig = figure("visible", "off");
imagesc(t_dem, f_dem(keep_dem), Ddisplay(keep_dem,:)); axis xy;
xlabel("Time (s)"); ylabel("Modulation frequency (Hz)");
title("DEMONgram of 100-1000 Hz analysis band");
colormap(jet(256)); colorbar; caxis([-35 8]);
hold on;
plot([t_dem(1), t_dem(end)], [shaft_truth_hz shaft_truth_hz], "w--", "linewidth", 1);
plot([t_dem(1), t_dem(end)], [blade_truth_hz blade_truth_hz], "w--", "linewidth", 1);
hold off;
print(fig, "04_demongram.png", "-dpng", "-r150"); close(fig);

% Average DEMON spectrum and automatic peak list.
dem_mag = mean(abs(D), 2);
dem_db = 20*log10(dem_mag/(max(dem_mag)+eps)+1e-12);
analysis = (f_dem >= 0.3 & f_dem <= 25);
peak_idx = simple_peaks_local(dem_db, analysis, 0.25, f_dem);
[~, ord] = sort(dem_db(peak_idx), "descend");
peak_idx = peak_idx(ord(1:min(12, length(ord))));
[peak_freqs, order2] = sort(f_dem(peak_idx));
peak_levels = dem_db(peak_idx(order2));

fig = figure("visible", "off");
plot(f_dem(keep_dem), dem_db(keep_dem), "b"); grid on;
xlabel("Modulation frequency (Hz)"); ylabel("Relative magnitude (dB)");
title("Mean DEMON spectrum"); xlim([0 25]); ylim([-65 3]);
hold on;
plot(peak_freqs, peak_levels, "ro", "markersize", 5);
plot([shaft_truth_hz shaft_truth_hz], [-65 3], "r--");
plot([blade_truth_hz blade_truth_hz], [-65 3], "m--");
hold off;
print(fig, "05_mean_demon_spectrum.png", "-dpng", "-r150"); close(fig);

fid = fopen("demon_peaks.csv", "w");
fprintf(fid, "frequency_hz,relative_level_db\n");
for k = 1:length(peak_freqs)
  fprintf(fid, "%.6f,%.3f\n", peak_freqs(k), peak_levels(k));
endfor
fclose(fid);

%% 5. Real cepstrum
% The real cepstrum is IFFT(log(|FFT(x)|)). A periodic harmonic spacing of
% Delta-f Hz tends to form a peak near quefrency 1/Delta-f seconds.
cep_nfft = 2^nextpow2(N);
X = fft(x .* hann_local(N), cep_nfft);
log_mag = log(abs(X) + 1e-12);
cep = real(ifft(log_mag));
q = (0:cep_nfft-1)' / fs;         % quefrency in seconds
q_keep = (q >= 0.02 & q <= 1.2);

fig = figure("visible", "off");
plot(q(q_keep), cep(q_keep), "k"); grid on;
xlabel("Quefrency (s)"); ylabel("Real cepstrum amplitude");
title("Real cepstrum: periodic spectral spacing becomes a quefrency peak");
hold on;
plot([1/blade_truth_hz 1/blade_truth_hz], ylim(), "m--");
plot([1/shaft_truth_hz 1/shaft_truth_hz], ylim(), "r--");
hold off;
print(fig, "06_real_cepstrum.png", "-dpng", "-r150"); close(fig);

%% Console summary
fprintf("\nExpected rates\n");
fprintf("  Shaft rate: %.3f Hz = %.1f rpm\n", shaft_truth_hz, 60*shaft_truth_hz);
fprintf("  Blade rate: %.3f Hz (%d blades)\n", blade_truth_hz, blade_count);
fprintf("\nStrong DEMON peaks written to demon_peaks.csv:\n");
for k = 1:length(peak_freqs)
  fprintf("  %8.3f Hz   %7.2f dB\n", peak_freqs(k), peak_levels(k));
endfor
fprintf("\nCreated six PNG plots and demon_peaks.csv.\n");

endfunction

%% Local helper functions
function w = hann_local(N)
  if N <= 1
    w = ones(N,1);
  else
    n = (0:N-1)';
    w = 0.5 - 0.5*cos(2*pi*n/(N-1));
  endif
endfunction

function [S, f, tc] = stft_local(x, fs, L, hop, nfft, win)
  x = x(:); win = win(:);
  starts = 1:hop:(length(x)-L+1);
  S = zeros(nfft/2+1, length(starts));
  for k = 1:length(starts)
    seg = x(starts(k):starts(k)+L-1) .* win;
    Y = fft(seg, nfft);
    S(:,k) = Y(1:nfft/2+1);
  endfor
  f = (0:nfft/2)' * fs/nfft;
  tc = ((starts-1) + (L-1)/2) / fs;
endfunction

function y = fft_bandpass_local(x, fs, flo, fhi)
  N = length(x); X = fft(x);
  f = (0:N-1)' * fs/N;
  mask = ((f >= flo & f <= fhi) | (f >= fs-fhi & f <= fs-flo));
  y = real(ifft(X .* mask));
endfunction

function y = fft_lowpass_local(x, fs, fc)
  N = length(x); X = fft(x);
  f = (0:N-1)' * fs/N;
  mask = (f <= fc | f >= fs-fc);
  y = real(ifft(X .* mask));
endfunction

function z = analytic_local(x)
  N = length(x); X = fft(x); H = zeros(N,1);
  if rem(N,2) == 0
    H(1)=1; H(N/2+1)=1; H(2:N/2)=2;
  else
    H(1)=1; H(2:(N+1)/2)=2;
  endif
  z = ifft(X .* H);
endfunction

function idx = simple_peaks_local(y, allowed, min_sep_hz, f)
  candidates = find(allowed(2:end-1) & y(2:end-1)>y(1:end-2) & y(2:end-1)>=y(3:end)) + 1;
  [~, order] = sort(y(candidates), "descend");
  selected = [];
  for k = 1:length(order)
    c = candidates(order(k));
    if isempty(selected) || all(abs(f(c)-f(selected)) >= min_sep_hz)
      selected(end+1) = c;
    endif
  endfor
  idx = selected(:);
endfunction
