import numpy as np
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
f_c = 5.8e9 # center frequency
wavelength = c / f_c

bw = 0.02e9 # bandwidth
t_chirp = 4.6e-6 # chirp time
prp=5e-6 # Pulse Repetition Period
pulses = 128
angleBins = int(180 / 5)

fs = 46e6 # 50e6 # IF fs

range_window = signal.windows.chebwin(int(fs * t_chirp), at=80)
doppler_window = signal.windows.chebwin(pulses, at=60)


# baseband = np.ndarray.mean(baseband, axis=0, keepdims=True)

# print(f"shape: {baseband.shape}, rw: {len(range_window)}, dw: {len(doppler_window)}")


range_doppler = proc.range_doppler_fft(baseband, rwin=range_window, dwin=doppler_window, rn=256) # 
range_doppler_angle = fft.fft(range_doppler, axis=2, n=angleBins)

# range_doppler = np.sum(range_doppler, axis=0, keepdims=True)

doppler_bins = range_doppler.shape[1]
range_bins = range_doppler.shape[2]

shifted = np.abs(fft.fftshift(range_doppler_angle[0], axes=(0,)))
results = 10 * np.log10(shifted)

cfar = proc.cfar_ca_2d(shifted, guard=2, trailing=10, pfa=0.8e-3)
cfar_db = 10 * np.log10(cfar)
cfar_diff = shifted - cfar
# cfar_diff = results - cfar_db

max_range = (c * fs * t_chirp / bw / 2)
range_axis = np.linspace(0, max_range, range_bins, endpoint=False)

unambiguous_speed = (c / prp / f_c / 2)

# Compute range axis
# range_axis = np.arange(range_bins) * delta_R # np.linspace(0, r_max, range_bins) # (r_max / range_bins)  # Convert bin index to meters
doppler_axis = np.linspace(-unambiguous_speed, unambiguous_speed, doppler_bins)

print(f"range bin count: {range_bins}, max range: {round(range_axis[-1], 2)} m, res: {round(range_axis[-1] / range_bins, 2)} m")
print(f"doppler bin count: {doppler_bins}, max velocity: {round(doppler_axis[-1], 2)} m/s, res: {round(doppler_axis[-1]*2 / doppler_bins, 3)} m/s")

remove_firs_range_bins = 5
targets = np.argwhere(cfar_diff[:, remove_firs_range_bins:] > 2)
targets[:,1] += remove_firs_range_bins # fix indexes 
print(f"targets:")
for target in targets:
    print(f"conf: {round(cfar_diff[target[0]][target[1]], 2)}; range: {range_axis[target[1]]} m; velocity: {round(doppler_axis[target[0]], 2)} m/s")

# Plot the 2D array
plt.figure(1)
plt.imshow(shifted, cmap='viridis', aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[-1], doppler_axis[0]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map Raw')

# plt.figure(2)
# plt.imshow(cfar_diff > 2, cmap="gray", vmin=0, vmax=1, aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[-1], doppler_axis[0]])
# plt.colorbar(label='Amplitude (dB)')
# plt.xlabel('Range (m)')
# plt.ylabel('Velocity (m/s)')
# plt.title('Range-Doppler Map with CFAR')

plt.figure(3)
plt.plot(range_axis, shifted[len(shifted)//2], label='radar')
plt.plot(range_axis, cfar[len(shifted)//2], label='cfar')
plt.xlabel('Range (m)')
plt.legend()

range_angle_map = np.sum(np.abs(shifted), axis=1)  # Sum over Doppler bins

print(f"shape: {range_angle_map.shape}")

# Define axis labels
angle_bins = np.linspace(-90, 90, angleBins)  # Assuming angle spans -90 to 90 degrees

# Plot
plt.figure(figsize=(10, 6))
plt.imshow(20 * np.log10(range_angle_map + 1e-6), aspect='auto', 
           extent=[angle_bins[0], angle_bins[-1], range_axis[-1], range_axis[0]], 
           cmap='jet')

plt.colorbar(label="Power (dB)")
plt.xlabel("Angle (degrees)")
plt.ylabel("Range bin")
plt.title("Range-Angle Heatmap")

plt.show()

exit()

range_window = signal.windows.chebwin(radar.sample_prop["samples_per_pulse"], at=60)
range_profile = proc.range_fft(baseband, range_window)


max_range = (
    3e8
    * radar.radar_prop["receiver"].bb_prop["fs"]
    * radar.radar_prop["transmitter"].waveform_prop["pulse_length"]
    / radar.radar_prop["transmitter"].waveform_prop["bandwidth"]
    / 2
)
range_axis = np.linspace(
    0, max_range, radar.sample_prop["samples_per_pulse"], endpoint=False
)


azimuth = np.arange(-90, 90, 1)

array_loc_x = np.zeros((1, len(radar.array_prop["virtual_array"])))
for va_idx, va in enumerate(radar.array_prop["virtual_array"]):
    array_loc_x[0, va_idx] = va[1] * f_c / c

azimuth_grid, array_loc_grid = np.meshgrid(azimuth, array_loc_x)

A = np.transpose(
    np.exp(1j * 2 * np.pi * array_loc_grid * np.sin(azimuth_grid / 180 * np.pi))
)

bf_window = np.transpose(
    np.array([signal.windows.chebwin(len(radar.array_prop["virtual_array"]), at=50)])
)
AF = np.matmul(
    A,
    range_profile[:, 0, :]
    * np.repeat(bf_window, radar.sample_prop["samples_per_pulse"], axis=1),
)

range_axis = np.linspace(
    0, max_range, radar.sample_prop["samples_per_pulse"], endpoint=False
)

fig = go.Figure()
fig.add_trace(
    go.Surface(
        x=range_axis, y=azimuth, z=20 * np.log10(np.abs(AF) + 0.1), colorscale="Rainbow"
    )
)

fig.update_layout(
    title="Range-Azimuth Map",
    height=600,
    scene=dict(
        xaxis=dict(title="Range (m)"),
        yaxis=dict(title="Azimuth (deg)"),
        zaxis=dict(title="Amplitude (dB)"),
        aspectmode="data",
    ),
    margin=dict(l=0, r=0, b=60, t=100),
)

# uncomment this to display interactive plot
fig.show()