import numpy as np
from numpy.typing import NDArray
from scipy import signal, linalg, fft
import matplotlib.pyplot as plt

import radarsimpy.processing as proc

# load data
baseband = []
with open('radarBaseband.npy', 'rb') as f:
    baseband = np.load(f)

print(f"loaded data shape: {baseband.shape}")

# parameters
c = 3e8
f_c = 6e9 # center frequency
wavelength = c / f_c

bw = 0.02e9 # bandwidth
t_chirp = 4.6e-6 # chirp time
prp=5e-6 # Pulse Repetition Period
angleBins = int(180 / 5)

fs = 46e6 # 50e6 # IF fs

rx_channels, chirps, range_samples = baseband.shape

range_window = signal.windows.chebwin(range_samples, at=90)
doppler_window = signal.windows.chebwin(chirps, at=60)
angle_window = signal.windows.chebwin(rx_channels, at=6)

# baseband = np.ndarray.mean(baseband, axis=0, keepdims=True)

# print(f"shape: {baseband.shape}, rw: {len(range_window)}, dw: {len(doppler_window)}")
# proc.range_doppler_fft(baseband, rwin=range_window, dwin=doppler_window, rn=256, dn=200000)

def range_fft(data: NDArray, rwin: NDArray = None, n: int = None) -> NDArray:
    shape = np.shape(data)

    if rwin is None:
        rwin = 1
    else:
        rwin = np.tile(rwin[np.newaxis, np.newaxis, ...], (shape[0], shape[1], 1))

    return fft.fft(data * rwin, n=n, axis=2)

def doppler_fft(data: NDArray, dwin: NDArray = None, n: int = None) -> NDArray:
    shape = np.shape(data)

    if dwin is None:
        dwin = 1
    else:
        dwin = np.tile(dwin[np.newaxis, ..., np.newaxis], (shape[0], 1, shape[2]))

    return fft.fft(data * dwin, n=n, axis=1)

def angle_fft(data: NDArray, awin: NDArray = None, n: int = None) -> NDArray:
    shape = np.shape(data)

    if awin is None:
        awin = 1
    else:
        awin = np.tile(awin[..., np.newaxis, np.newaxis], (1, shape[1], shape[2]))

    return fft.fft(data * awin, n=n, axis=0)

def range_doppler_angle_fft(data: NDArray, rwin: NDArray = None, dwin: NDArray = None, awin: NDArray = None, rn: int = None, dn: int = None, an: int = None) -> NDArray:
    return angle_fft(doppler_fft(range_fft(data, rwin=rwin, n=rn), dwin=dwin, n=dn), awin=awin, n=an)

angle_doppler_range  = np.abs(range_doppler_angle_fft(np.array(baseband, dtype=np.complex64), rwin=range_window, dwin=doppler_window, awin=angle_window, rn=256, dn=1024, an=angleBins))




















doppler_range_map = np.sum(angle_doppler_range, axis=0) # Sum over angle bins
angle_range_map = np.sum(angle_doppler_range, axis=1)  # Sum over Doppler bins
angle_doppler_map = np.sum(angle_doppler_range, axis=2)  # Sum over Range bins

angle_range_dB = 20 * np.log10(angle_range_map)
doppler_range_dB = 20 * np.log10(doppler_range_map)
angle_doppler_dB = 20 * np.log10(angle_doppler_map)

print(f"angle_doppler_range shape: {angle_doppler_range.shape}")
print(f"doppler_range shape: {doppler_range_map.shape}")
print(f"angle_range_map shape: {angle_range_map.shape}")
print(f"angle_doppler_map shape: {angle_doppler_map.shape}")

# shifted fft
doppler_range_shifted = np.abs(fft.fftshift(doppler_range_map, axes=(0,)))
doppler_range_shifted_dB = 20 * np.log10(doppler_range_shifted)

# Define axis labels
doppler_bins = angle_doppler_range.shape[1]
range_bins = angle_doppler_range.shape[2]

angle_axis = np.linspace(-90, 90, angleBins)  # Assuming angle spans -90 to 90 degrees

max_range = (c * fs * t_chirp / bw / 2)
range_axis = np.linspace(0, max_range, range_bins, endpoint=False)
# range_axis = np.arange(range_bins) * delta_R # np.linspace(0, r_max, range_bins) # (r_max / range_bins)  # Convert bin index to meters

unambiguous_speed = (c / prp / f_c / 2)
doppler_axis = np.linspace(-unambiguous_speed, unambiguous_speed, doppler_bins)

# CFAR
doppler_range_shifted_cfar = proc.cfar_ca_2d(doppler_range_shifted, guard=2, trailing=10, pfa=0.8e-6)
doppler_range_shifted_cfar_db = 20 * np.log10(doppler_range_shifted_cfar)
doppler_range_shifted_cfar_diff = doppler_range_shifted - doppler_range_shifted_cfar

angle_range_cfar = proc.cfar_ca_2d(angle_range_map, guard=2, trailing=10, pfa=0.8e-6)
angle_range_cfar_db = 20 * np.log10(angle_range_cfar)
angle_range_cfar_diff = angle_range_map - angle_range_cfar


print(f"range bin count: {range_bins}, max range: {round(range_axis[-1], 2)} m, res: {round(range_axis[-1] / range_bins, 2)} m")
print(f"doppler bin count: {doppler_bins}, max velocity: {round(doppler_axis[-1], 2)} m/s, res: {round(doppler_axis[-1]*2 / doppler_bins, 3)} m/s")

remove_firs_range_bins = 5
targets = np.argwhere(doppler_range_shifted_cfar_diff[:, remove_firs_range_bins:] > 2)
targets[:,1] += remove_firs_range_bins # fix indexes 
print(f"targets (range doppler):")
# for target in targets:
#     print(f"conf: {round(doppler_range_shifted_cfar_diff[target[0]][target[1]], 2)}; range: {range_axis[target[1]]} m; velocity: {round(doppler_axis[target[0]], 2)} m/s")

# Plot the 2D array
plt.figure(1)
plt.imshow(doppler_range_shifted_dB, cmap='viridis', aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[0], doppler_axis[-1]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map (sum over angle)')

# plt.figure(2)
# plt.imshow(cfar_diff > 2, cmap="gray", vmin=0, vmax=1, aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[-1], doppler_axis[0]])
# plt.colorbar(label='Amplitude (dB)')
# plt.xlabel('Range (m)')
# plt.ylabel('Velocity (m/s)')
# plt.title('Range-Doppler Map with CFAR')

# plt.figure(3)
# plt.plot(range_axis, doppler_range_shifted[len(doppler_range_shifted)//2], label='radar')
# plt.plot(range_axis, doppler_range_shifted_cfar[len(doppler_range_shifted)//2], label='cfar')
# plt.xlabel('Range (m)')
# plt.title('Range doppler (doppler = 0 m/s)')


# Plot
# angle_doppler_range[:,0,:]
plt.figure(4)
plt.imshow(angle_range_dB, cmap='viridis', aspect='auto', extent=[range_axis[0], range_axis[-1], angle_axis[0], angle_axis[-1]])
plt.colorbar(label="Power (dB)")
plt.xlabel("Range bin")
plt.ylabel("Angle (degrees)")
plt.title("Range-Angle Map (sum over doppler)")

plt.figure(5)
plt.imshow(fft.fftshift(angle_doppler_dB, axes=(1)), cmap='viridis', aspect='auto', extent=[doppler_axis[-1], doppler_axis[0], angle_axis[0], angle_axis[-1]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Velocity (m/s)')
plt.ylabel('Angle (degrees)')
plt.title('Angle-Doppler Map (sum over range)')

# plt.figure(6)
# plt.plot(angle_axis, angle_range_map[:,114], label='radar')
# plt.plot(angle_axis, angle_range_cfar[:,114], label='cfar')
# plt.xlabel('Angle (degrees)')
# plt.title('Angle Range (range = 500)')


# Plot
fig = plt.figure(7)
ax = fig.add_subplot(111, projection='3d')
# Scatter plot
angle_doppler_range_shifted = fft.fftshift(20 * np.log10(angle_doppler_range), axes=(1))
indices  = np.argwhere(angle_doppler_range_shifted > -10) # -30
angles, dopplers, ranges = indices.T
points = angle_doppler_range_shifted[indices[:, 0], indices[:, 1], indices[:, 2]]
sc = ax.scatter(angle_axis[angles], np.flip(doppler_axis)[dopplers], range_axis[ranges], c=points, cmap='viridis', marker='o', alpha=0.7)

# Labels
ax.set_xlabel("Angle (degrees)")
ax.set_ylabel("Velocity (m/s)")
ax.set_zlabel("Range (m)")
ax.set_title("3D Radar Cube Point Cloud")
# Color bar
cbar = plt.colorbar(sc)
cbar.set_label("Intensity")

plt.legend()
plt.show()
