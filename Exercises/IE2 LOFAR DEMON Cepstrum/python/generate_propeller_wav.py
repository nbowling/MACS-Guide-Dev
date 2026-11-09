"""Regenerate the synthetic WAV used by the Octave exercise."""
from pathlib import Path
import numpy as np
from scipy.io import wavfile

FS = 4000
DURATION = 60.0
SHAFT_HZ = 1.30
BLADES = 5
rng = np.random.default_rng(20261021)
t = np.arange(int(FS * DURATION)) / FS
sr_inst = SHAFT_HZ + 0.025 * np.sin(2*np.pi*0.035*t)
shaft_phase = 2*np.pi*np.cumsum(sr_inst) / FS
blade_phase = BLADES * shaft_phase

white = rng.normal(size=t.size)
coloured = np.empty_like(white)
coloured[0] = white[0]
for i in range(1, len(white)):
    coloured[i] = 0.965*coloured[i-1] + white[i]
coloured /= np.std(coloured)
mod = 1 + 0.42*np.sin(shaft_phase) + 0.28*np.sin(blade_phase) + 0.10*np.sin(2*blade_phase)
cavitation = 0.16 * mod * coloured

carriers = np.zeros_like(t)
for f, a, p in [(150, .19, .2), (310, .16, 1.1), (620, .12, 2.0), (900, .07, .6)]:
    local_mod = 1 + .35*np.sin(shaft_phase+p) + .22*np.sin(blade_phase+.5*p)
    carriers += a*local_mod*np.sin(2*np.pi*f*t+p)

low = (.10*np.sin(shaft_phase) + .08*np.sin(blade_phase) +
       .055*np.sin(2*blade_phase) + .075*np.sin(2*np.pi*48*t) +
       .050*np.sin(2*np.pi*96*t))
ambient = .035*rng.normal(size=t.size)
x = cavitation + carriers + low + ambient
x = .92*x/np.max(np.abs(x))
out = Path(__file__).with_name("synthetic_propeller_shaft.wav")
wavfile.write(out, FS, np.int16(np.clip(x, -1, 1)*32767))
print(f"Wrote {out}: {DURATION:.1f} s, {FS} Hz, shaft {SHAFT_HZ} Hz, blade rate {SHAFT_HZ*BLADES:.2f} Hz")
