import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
import re

fs = 245.760 * 1e6 # MHz
fmax = 20 * 1e6 # MHz
chirpTime = 10 * 1e-6 # micro seconds
bitRes = 16 # bit resolution, used for scaling

# determine length of array
chirpLength = int(chirpTime * fs)
I = np.zeros(chirpLength, dtype=int)
Q = np.zeros(chirpLength, dtype=int)

#  math is based on: https://dspfirst.gatech.edu/chapters/04samplin/demos/chirpSynthDemo/index.html

alpha = fmax / chirpTime # Hz/s
scale = ((2**bitRes) // 2) - 1
for n in range(chirpLength):
  τ = n / fs  
  I[n] = scale * np.cos(np.pi * alpha * τ**2) # I
  Q[n] = scale * np.sin(np.pi * alpha * τ**2) # Q


print(f"samples: {chirpLength}, scale: {scale}, max_val: {max(max(Q), max(I))}, min_val: {min(min(Q), min(I))}")
I_chirp = ', '.join(str(x) for x in I).removesuffix(', ')
Q_chirp = ', '.join(str(x) for x in Q).removesuffix(', ')

# print(f"comma count: {I_chirp.count(',')}")

windowsSize = 128
overlapFrac = 7/10 # 1/2 = 50% windows overlap

carr = I + 1j*Q
f, t, Zxx = stft(carr, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac, nfft=4096)
f /= 1e6
t *= 1e6

maxPlotFreq = (fmax * 1e-6) * 1.3
lastIndex = np.argwhere(f > maxPlotFreq)[0][0]
f = f[:lastIndex]
Zxx = Zxx[:lastIndex,:]

plt.figure(layout="constrained")
plt.subplot(311)
plt.plot(I)
plt.ylabel('Amplitude')
plt.xlabel('Sample (I)')

plt.subplot(312)
plt.plot(Q)
plt.ylabel('Amplitude')
plt.xlabel('Sample (Q)')

plt.subplot(313)
plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('$\mu$s (I)')

plt.show()

res = input(f"Save to chirps.h? [Y/n]: ")
if (res.lower() == 'y'):
  path = "./chirp.h"
  content = "#include <stdint.h>\n"
  content += "int16_t I_chirp[] = {" + I_chirp + "};\n"
  content += "int16_t Q_chirp[] = {" + Q_chirp + "};\n"
  open(path, "w").write(content)
  # def newChirp(match_obj):
  #   if match_obj.group(1) is not None:
  #     return I_chirp
  #   if match_obj.group(2) is not None:
  #     return Q_chirp

  # content = open(path, "r").read()
  # content = re.sub("(?<=[I]_chirp\[\] = {)([\d,\s,-]+)(?=};)|(?<=[Q]_chirp\[\] = {)([\d,\s,-]+)(?=};)", newChirp, content)
  # open(path, "w").write(content)