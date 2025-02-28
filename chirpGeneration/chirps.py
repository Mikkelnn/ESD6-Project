import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
import re

fs = 1 * 1e6 # 100MHz
fmax = 100 * 1e3 # 10MHz
chirpTime = 10 * 1e-3 # 10ms second = 1ms
bitRes = 8 # bit resolution, used for scaling

chirpLength = int(chirpTime * fs)
chirp_sin = np.zeros(chirpLength, dtype=int)
chirp_cos = np.zeros(chirpLength, dtype=int)

#  math is based on: https://dspfirst.gatech.edu/chapters/04samplin/demos/chirpSynthDemo/index.html

alpha = fmax / chirpTime # Hz/s
scale = ((2**bitRes) // 2) - 1
for n in range(chirpLength):
  t = n / fs  
  chirp_sin[n] = scale + scale * np.sin(np.pi * alpha * t**2) # scaled to 8bit
  chirp_cos[n] = scale + scale * np.cos(np.pi * alpha * t**2) # scaled to 8bit

print(f"samples: {chirpLength}, scale: {scale}, max_val: {max(max(chirp_sin), max(chirp_cos))}, min_val: {min(min(chirp_sin), min(chirp_cos))}")
I_chirp = ', '.join(str(x) for x in chirp_cos).removesuffix(', ')
Q_chirp = ', '.join(str(x) for x in chirp_sin).removesuffix(', ')

windowsSize = 64
overlapFrac = 1/2 # 1/2 = 50% windows overlap

f, t, Zxx = stft(chirp_cos, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac)
f /= 1e6
t *= 1e3
plt.figure()
plt.subplot(211)
plt.plot(chirp_cos)
plt.ylabel('Amplitude')
plt.xlabel('Sample')

plt.subplot(212)
plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('ms')

plt.show()

res = input(f"Save to chirps.h? [Y/n]: ")
if (res.lower() == 'y'):
  path = "./ESP32_IQ_phaseshifter\phaseShifter\chirp.h"
  def newChirp(match_obj):
    if match_obj.group(1) is not None:
      return I_chirp
    if match_obj.group(2) is not None:
      return Q_chirp

  content = open(path, "r").read()
  content = re.sub("(?<=[I]_chirp\[\] = {)([\d,\s]+)(?=};)|(?<=[Q]_chirp\[\] = {)([\d,\s]+)(?=};)", newChirp, content)
  open(path, "w").write(content)