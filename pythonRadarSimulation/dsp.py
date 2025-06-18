import numpy as np
from numpy.typing import NDArray
from scipy import signal, linalg, fft
import matplotlib.pyplot as plt
from scipy.ndimage import binary_dilation

import radarsimpy.processing as proc

# load data
baseband = []
with open('simData/TestOfManySim.npy', 'rb') as f:
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

windowIndex = 6 #Use this to index which window in the switch case you want. 6 is chebyshev

window = signal.windows.barthann(51) 
windowType = 'Bartlett-hann'

range_window = signal.windows.barthann(range_samples) 
doppler_window = signal.windows.barthann(chirps) 
angle_window = signal.windows.barthann(rx_channels) 

# Choose the window function

match windowIndex:
    case 0:
        window = signal.windows.barthann(51) #To display the window function and fourier transform of it
        windowType = 'Bartlett-hann'

        range_window = signal.windows.barthann(range_samples) 
        doppler_window = signal.windows.barthann(chirps) 
        angle_window = signal.windows.barthann(rx_channels) 


    case 1:
        window = signal.windows.bartlett(51)  
        windowType = 'Bartlett'

        range_window = signal.windows.bartlett(range_samples) 
        doppler_window = signal.windows.bartlett(chirps) 
        angle_window = signal.windows.bartlett(rx_channels) 
    
    case 2:
        window = signal.windows.blackman(51)  
        windowType = 'Blackman'

        range_window = signal.windows.blackman(range_samples) 
        doppler_window = signal.windows.blackman(chirps) 
        angle_window = signal.windows.blackman(rx_channels) 

    case 3:
        window = signal.windows.blackmanharris(51)
        windowType = 'Blackman-Harris'

        range_window = signal.windows.blackmanharris(range_samples) 
        doppler_window = signal.windows.blackmanharris(chirps) 
        angle_window = signal.windows.blackmanharris(rx_channels) 

    case 4:
        window = signal.windows.bohman(51)  
        windowType = 'Bohman'

        range_window = signal.windows.bohman(range_samples) 
        doppler_window = signal.windows.bohman(chirps) 
        angle_window = signal.windows.bohman(rx_channels) 
    
    case 5:
        window = signal.windows.boxcar(51)  
        windowType = 'Boxcar'

        range_window = signal.windows.boxcar(range_samples) 
        doppler_window = signal.windows.boxcar(chirps) 
        angle_window = signal.windows.boxcar(rx_channels) 

    case 6:
        window = signal.windows.chebwin(100, at=90)  
        windowType = 'Dolph-Chebyshev'

        range_window = signal.windows.chebwin(range_samples, at=90) 
        doppler_window = signal.windows.chebwin(chirps, at=60) 
        angle_window = signal.windows.chebwin(rx_channels, at=15) 

    case 7:
        window = signal.windows.cosine(51)  
        windowType = 'Cosine'

        range_window = signal.windows.cosine(range_samples) 
        doppler_window = signal.windows.cosine(chirps) 
        angle_window = signal.windows.cosine(rx_channels) 

    case 8:
        window = signal.windows.flattop(51) 
        windowType = 'Flattop'

        range_window = signal.windows.flattop(range_samples) 
        doppler_window = signal.windows.flattop(chirps) 
        angle_window = signal.windows.flattop(rx_channels) 


    case 9:
        window = signal.windows.hamming(51) 
        windowType = 'Hamming'

        range_window = signal.windows.hamming(range_samples) 
        doppler_window = signal.windows.hamming(chirps) 
        angle_window = signal.windows.hamming(rx_channels) 


    case 10:
        window = signal.windows.hann(51) 
        windowType = 'Hann'

        range_window = signal.windows.hann(range_samples) 
        doppler_window = signal.windows.hann(chirps) 
        angle_window = signal.windows.hann(rx_channels) 


    case 11:
        window = signal.windows.kaiser(51,10) 
        windowType = 'Kaiser, beta=10'

        range_window = signal.windows.kaiser(range_samples,10) 
        doppler_window = signal.windows.kaiser(chirps,10) 
        angle_window = signal.windows.kaiser(rx_channels,10) 


    case 12:
        window = signal.windows.lanczos(51) 
        windowType = 'Lanczos'

        range_window = signal.windows.lanczos(range_samples) 
        doppler_window = signal.windows.lanczos(chirps) 
        angle_window = signal.windows.lanczos(rx_channels) 

        
    case 13:
        window = signal.windows.nuttall(51) 
        windowType = 'Nutall'

        range_window = signal.windows.nuttall(range_samples) 
        doppler_window = signal.windows.nuttall(chirps) 
        angle_window = signal.windows.nuttall(rx_channels) 

        
    case 14:
        window = signal.windows.parzen(51) 
        windowType = 'Parzen'

        range_window = signal.windows.parzen(range_samples) 
        doppler_window = signal.windows.parzen(chirps) 
        angle_window = signal.windows.parzen(rx_channels) 

        
    case 15:
        window = signal.windows.taylor(51) 
        windowType = 'Taylor'

        range_window = signal.windows.taylor(range_samples) 
        doppler_window = signal.windows.taylor(chirps) 
        angle_window = signal.windows.taylor(rx_channels) 

        
    case 16:
        window = signal.windows.triang(51) 
        windowType = 'Triangular'

        range_window = signal.windows.triang(range_samples) 
        doppler_window = signal.windows.triang(chirps) 
        angle_window = signal.windows.triang(rx_channels) 
        
        
    case 17:
        window = signal.windows.tukey(51) 
        windowType = 'Tukey'

        range_window = signal.windows.tukey(range_samples) 
        doppler_window = signal.windows.tukey(chirps) 
        angle_window = signal.windows.tukey(rx_channels) 

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





# Time-domain plot
# plt.figure(0, figsize=(10, 4))
# plt.subplot(1, 2, 1)
# plt.plot(window, color='teal')
# plt.title(windowType)
# plt.ylabel('amplitude')
# plt.xlabel('samples')
# plt.grid(True)

# Frequency-domain plot (dB)
# plt.subplot(1, 2, 2)
# A = np.fft.fft(window, 2048) / 25.5
# freq = np.fft.fftfreq(len(A), 1.0)
# response = 20 * np.log10(np.abs(np.fft.fftshift(A)))
# response = response - np.max(response)  # Normalize to 0 dB

# plt.plot(np.fft.fftshift(freq), response, color='orange')
# plt.title('Fourier Transform')
# plt.ylabel('decibels')
# plt.xlabel('bins')
# plt.xlim(-0.5, 0.5)
# plt.ylim(-140, 0)
# plt.grid(True)

# plt.tight_layout()






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

unambiguous_speed = (c / (prp * f_c * 4)) #(c / prp / f_c / 2)
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
for target in targets:
    print(f"conf: {round(doppler_range_shifted_cfar_diff[target[0]][target[1]], 2)}; range: {range_axis[target[1]]} m; velocity: {round(doppler_axis[target[0]], 2)} m/s")

# Plot the 2D array
plt.figure(1)
plt.imshow(doppler_range_shifted_dB, cmap='viridis', aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[0], doppler_axis[-1]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map (sum over angle)')

plt.figure(2)
plt.imshow(doppler_range_shifted_cfar_diff, cmap="gray", vmin=0, vmax=1, aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[-1], doppler_axis[0]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map with CFAR')

plt.figure(3)
plt.plot(range_axis, doppler_range_shifted[len(doppler_range_shifted)//2], label='radar')
plt.plot(range_axis, doppler_range_shifted_cfar[len(doppler_range_shifted)//2], label='cfar')
plt.xlabel('Range (m)')
plt.title('Range doppler (doppler = 0 m/s)')


# Plot
angle_doppler_range[:,0,:]
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

plt.figure(6)
plt.plot(angle_axis, angle_range_map[:,114], label='radar')
plt.plot(angle_axis, angle_range_cfar[:,114], label='cfar')
plt.xlabel('Angle (degrees)')
plt.title('Angle Range (range = 500)')


#Plot
fig = plt.figure(7)
ax = fig.add_subplot(111, projection='3d')
# Scatter plot
angle_doppler_range_shifted = fft.fftshift(20 * np.log10(angle_doppler_range), axes=(1))
max_val = np.max(angle_doppler_range_shifted)
threshold = max_val - 3
indices  = np.argwhere(angle_doppler_range_shifted > threshold-2) # -30
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


# baseband = np.ndarray.mean(baseband, axis=0, keepdims=True)

# print(f"shape: {baseband.shape}, rw: {len(range_window)}, dw: {len(doppler_window)}")
# proc.range_doppler_fft(baseband, rwin=range_window, dwin=doppler_window, rn=256, dn=200000)

# Get the index of the maximum value
a_max, d_max, r_max = np.unravel_index(np.argmax(angle_doppler_range_shifted), angle_doppler_range_shifted.shape)

# Helper: Find first failure before/after peak in 1D profile
def find_threshold_failures(data_1d, peak_idx, threshold):
    forward_fail = None
    for i in range(peak_idx, len(data_1d) - 1):
        if data_1d[i] > threshold and data_1d[i + 1] <= threshold:
            forward_fail = i + 1
            break

    backward_fail = None
    for i in range(peak_idx, 0, -1):
        if data_1d[i] > threshold and data_1d[i - 1] <= threshold:
            backward_fail = i - 1
            break

    return backward_fail, forward_fail

# 1. Along angle
angle_profile = angle_doppler_range_shifted[:, d_max, r_max]
fail_angle_back, fail_angle_forward = find_threshold_failures(angle_profile, a_max, threshold)

# 2. Along doppler
doppler_profile = angle_doppler_range_shifted[a_max, :, r_max]
fail_doppler_back, fail_doppler_forward = find_threshold_failures(doppler_profile, d_max, threshold)

# 3. Along range
range_profile = angle_doppler_range_shifted[a_max, d_max, :]
fail_range_back, fail_range_forward = find_threshold_failures(range_profile, r_max, threshold)

# Map to physical coordinates
def safe_map(axis, idx):
    return axis[idx] if idx is not None else None

angle_fail_back = safe_map(angle_axis, fail_angle_back)
angle_fail_forward = safe_map(angle_axis, fail_angle_forward)

doppler_fail_back = safe_map(np.flip(doppler_axis), fail_doppler_back)
doppler_fail_forward = safe_map(np.flip(doppler_axis), fail_doppler_forward)

range_fail_back = safe_map(range_axis, fail_range_back)
range_fail_forward = safe_map(range_axis, fail_range_forward)

# Output
print(f"Max value at: angle={angle_axis[a_max]}, doppler={np.flip(doppler_axis)[d_max]}, range={range_axis[r_max]}")
print("\nThreshold fails at:")
print(f"  Angle:   back={angle_fail_back}, forward={angle_fail_forward}")
print(f"  Doppler: back={doppler_fail_back}, forward={doppler_fail_forward}")
print(f"  Range:   back={range_fail_back}, forward={range_fail_forward}")

plt.show()
