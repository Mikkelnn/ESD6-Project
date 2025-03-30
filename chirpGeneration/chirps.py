import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
import re

fs = 400 * 1e6 # MHz
fmax = 20 * 1e6 # MHz
chirpTime = 2 * 1e-6 # micro seconds
bitRes = 14 # bit resolution, used for scaling

# determine length of array
chirpLength = int(chirpTime * fs)
I = np.zeros(chirpLength, dtype=int)
Q = np.zeros(chirpLength, dtype=int)

#  math is based on: https://dspfirst.gatech.edu/chapters/04samplin/demos/chirpSynthDemo/index.html

alpha = fmax / chirpTime # Hz/s
scale = ((2**bitRes) // 2) - 1
for n in range(chirpLength):
  τ = n / fs  
  I[n] = scale + scale * np.cos(np.pi * alpha * τ**2) # I
  Q[n] = scale + scale * np.sin(np.pi * alpha * τ**2) # Q


print(f"samples: {chirpLength}, scale: {scale}, max_val: {max(max(Q), max(I))}, min_val: {min(min(Q), min(I))}")
I_chirp = ', '.join(str(x) for x in I).removesuffix(', ')
Q_chirp = ', '.join(str(x) for x in Q).removesuffix(', ')

windowsSize = 64
overlapFrac = 1/2 # 1/2 = 50% windows overlap

f, t, Zxx = stft(I, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac)
f /= 1e6
t *= 1e6
plt.figure()
plt.subplot(211)
plt.plot(I)
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