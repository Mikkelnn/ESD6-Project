import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import stft
import re

fs = 61.440e6 # 245.760 * 1e6 # MHz 

windowsSize = 32
overlapFrac = 7/10 # 1/2 = 50% windows overlap

# Load rx_data from CSV
rx_data = np.loadtxt('chirps_12_data_tx_rx_ant_20db_tx.csv', delimiter=',', skiprows=1)
tx_data = np.loadtxt('chirps_12_data_tx.csv', delimiter=',', skiprows=1)

# rx_data = []
# # resample rx_data
# factor = int(245.760e6 / fs)
# for idx, i in enumerate(rx_data_raw):
#     if(idx % factor == 0):
#         rx_data.append(i)
# rx_data = np.array(rx_data)

print(f"rx_data shape: {rx_data.shape}")

shape = rx_data.shape
print(shape)
# int(shape[0]/2)
# Separate real and imaginary parts
# rx_real_parts = rx_data[:, 0] #rx_data[0]
# rx_imag_parts = rx_data[:, 1] #rx_data[1]

rx_complex_data = rx_data[:, 0] + 1j*rx_data[:, 1]
tx_complex_data = np.tile(tx_data[:, 0] + 1j*tx_data[:, 1], 12) # repeat chirp count = 12

# delayed rx
# delay = 50
# delayed_rx = np.pad(carr[:singleChirp-delay], (delay, 0), 'constant', constant_values=0)

sizeDiff = rx_complex_data.shape[0] - tx_complex_data.shape[0]
if (sizeDiff > 0):
    tx_complex_data = np.pad(tx_complex_data, (0, sizeDiff), 'constant', constant_values=0)

mixed = rx_complex_data * np.conjugate(tx_complex_data)

tx_f, tx_t, tx_Zxx = stft(tx_complex_data, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac, nfft=4096)
tx_f /= 1e6
tx_t *= 1e6

rx_f, rx_t, rx_Zxx = stft(rx_complex_data, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac, nfft=4096)
rx_f /= 1e6
rx_t *= 1e6

mix_f, mix_t, mix_Zxx = stft(mixed, fs=fs, nperseg=windowsSize, noverlap=windowsSize*overlapFrac, nfft=4096)
mix_f /= 1e6
mix_t *= 1e6

# maxPlotFreq = (20) * 1.3
# lastIndex = np.argwhere(f > maxPlotFreq)[0][0]
# f = f[:lastIndex]
# Zxx = Zxx[:lastIndex,:]

plt.figure(layout="constrained")
plt.subplot(511)
plt.plot(rx_complex_data.real)
plt.ylabel('Amplitude')
plt.xlabel('Rx Sample (I)')

plt.subplot(512)
plt.plot(rx_complex_data.imag)
plt.ylabel('Amplitude')
plt.xlabel('Rx Sample (Q)')

plt.subplot(513)
plt.pcolormesh(tx_t, tx_f, np.abs(tx_Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('Tx $\mu$s')

plt.subplot(514)
plt.pcolormesh(rx_t, rx_f, np.abs(rx_Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('Rx $\mu$s')

plt.subplot(515)
plt.pcolormesh(mix_t, mix_f, np.abs(mix_Zxx), shading='gouraud')
plt.ylabel('MHz')
plt.xlabel('mix $\mu$s')

plt.show()