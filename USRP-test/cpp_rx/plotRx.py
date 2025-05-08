import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
import re

fs = 45 * 1e6 # MHz
fmax = 20 * 1e6 # MHz
chirpTime = 2.4 * 1e-6 # micro seconds
bitRes = 16 # bit resolution, used for scaling

windowsSize = 32
overlapFrac = 7/10 # 1/2 = 50% windows overlap

# Load data from CSV
data = np.loadtxt('tx_rx_data.csv', delimiter=',', skiprows=1)

# Separate real and imaginary parts
real_parts = data[:, 0]
imag_parts = data[:, 1]


f, t, Zxx = stft(real_parts, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac, nfft=4096)
f /= 1e6
t *= 1e6

# maxPlotFreq = (fmax * 1e-6) * 1.3
# lastIndex = np.argwhere(f > maxPlotFreq)[0][0]
# f = f[:lastIndex]
# Zxx = Zxx[:lastIndex,:]

plt.figure(layout="constrained")
plt.subplot(311)
plt.plot(real_parts)
plt.ylabel('Amplitude')
plt.xlabel('Sample (I)')

plt.subplot(312)
plt.plot(imag_parts)
plt.ylabel('Amplitude')
plt.xlabel('Sample (Q)')

plt.subplot(313)
plt.pcolormesh(t, f, np.abs(Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('mus (I)')

plt.show()