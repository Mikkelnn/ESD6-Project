import radarsimpy
from radarsimpy import Radar, Transmitter, Receiver
import radarsimpy.processing as proc
from radarsimpy.simulator import sim_radar

import numpy as np
from scipy import signal, linalg, fft
import plotly.graph_objs as go
from IPython.display import Image
import matplotlib.pyplot as plt


# print("`RadarSimPy` used in this example is version: " + str(radarsimpy.__version__))

c = 3e8
f_c = 5.8e9 # center frequency
wavelength = c / f_c

bw = 0.02e9 # bandwidth
t_chirp = 10e-6 # chirp time
prp=12e-6 # Pulse Repetition Period
pulses = 128

fs = 46e6 # 50e6 # IF fs

r_max = (c * t_chirp) / 2 # calculate the maximum range
delta_R = c / (2 * bw)  # Calculate range resolution (meters / bin)
doppler_max = wavelength / (4 * prp) #((wavelength * (1 / (2 * prp))) / 2)
delta_velocity = wavelength / (2 * pulses * prp)

print(f"max range: {round(r_max, 2)} m; range resolution: {round(delta_R, 3)} m")
print(f"max velocity {round(doppler_max, 2)} m/s; velocity resolution: {round(delta_velocity, 3)} m/s")
print(f"tx time: {prp * pulses}s; sampls/chirp: {round(t_chirp * fs, 2)}")

N_tx = 1
N_rx = 4

tx_channels = []
if (N_tx == 1):
    tx_channels.append(dict(location=(0, 0, 0)))
else:
    for idx in range(0, N_tx):
        tx_channels.append(dict(location=(0, wavelength / 2 * idx - (N_tx - 1) * wavelength / 4, 0)))


rx_channels = []
for idx in range(0, N_rx):
    rx_channels.append(
        dict(
            location=(0, wavelength / 2 * idx - (N_rx - 1) * wavelength / 4, 0),
        )
    )

tx = Transmitter(
    f=[f_c - (bw/2), f_c + (bw/2)],
    t=[0, t_chirp],
    tx_power=40,
    prp=prp,
    pulses=pulses,
    channels=tx_channels
)

rx = Receiver(
    fs=fs,
    noise_figure=0, # 8
    rf_gain=20,
    load_resistor=500,
    baseband_gain=30,
    channels=rx_channels
)

radar = Radar(transmitter=tx, receiver=rx)

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=radar.radar_prop["transmitter"].txchannel_prop["locations"][:, 1]
        / wavelength,
        y=radar.radar_prop["transmitter"].txchannel_prop["locations"][:, 2]
        / wavelength,
        mode="markers",
        name="Transmitter",
        opacity=0.7,
        marker=dict(size=10),
    )
)

fig.add_trace(
    go.Scatter(
        x=radar.radar_prop["receiver"].rxchannel_prop["locations"][:, 1] / wavelength,
        y=radar.radar_prop["receiver"].rxchannel_prop["locations"][:, 2] / wavelength,
        mode="markers",
        opacity=1,
        name="Receiver",
    )
)

fig.update_layout(
    title="Array configuration",
    xaxis=dict(title="y (λ)"),
    yaxis=dict(title="z (λ)", scaleanchor="x", scaleratio=1),
)

# uncomment this to display interactive plot
# fig.show()

# display static image to reduce size on radarsimx.com
# img_bytes = fig.to_image(format="jpg", scale=2)
# display(Image(img_bytes))

# true_theta = [-5, -4, 45]

target_1 = dict(
    location=(
        #10 * np.cos(np.radians(true_theta[0])),
        #10 * np.sin(np.radians(true_theta[0])),
        0,
        500,
        0,
    ),
    speed=(0, 10, 0),
    rcs=9,
    phase=0,
)
# target_2 = dict(
#     location=(
#         40 * np.cos(np.radians(true_theta[1])),
#         40 * np.sin(np.radians(true_theta[1])),
#         0,
#     ),
#     speed=(0, 0, 0),
#     rcs=np.pi/9,
#     phase=0,
# )
target_3 = dict(
    location=(
        #40 * np.cos(np.radians(true_theta[2])),
        #40 * np.sin(np.radians(true_theta[2])),
        0,
        1000,
        0,
    ),
    speed=(0, 0, 0),
    rcs=4.5,
    phase=0,
)

targets = [target_1, target_3] #, target_2


data = sim_radar(radar, targets)
timestamp = data["timestamp"]
baseband = data["baseband"] # + data["noise"]


range_window = signal.windows.chebwin(radar.sample_prop["samples_per_pulse"], at=80)
doppler_window = signal.windows.chebwin(radar.radar_prop["transmitter"].waveform_prop["pulses"], at=60)

# baseband = np.ndarray.mean(baseband, axis=0, keepdims=True)

# print(f"shape: {baseband.shape}, rw: {len(range_window)}, dw: {len(doppler_window)}")


range_doppler = proc.range_doppler_fft(baseband, rwin=range_window, dwin=doppler_window)# , rn=1024


# range_doppler = np.sum(range_doppler, axis=0, keepdims=True)

doppler_bins = range_doppler.shape[1]
range_bins = range_doppler.shape[2]

shifted = np.abs(fft.fftshift(range_doppler[0], axes=(0,)))
results = 10 * np.log10(shifted)

cfar = proc.cfar_ca_2d(shifted, guard=2, trailing=10, pfa=0.8e-3)
cfar_db = 10 * np.log10(cfar)
cfar_diff = shifted - cfar
# cfar_diff = results - cfar_db

# Compute range axis
range_axis = np.arange(range_bins) * delta_R # (r_max / range_bins)  # Convert bin index to meters
doppler_axis = np.linspace(-doppler_max, doppler_max, doppler_bins)

print(f"range bin count: {range_bins}, max range: {range_axis[-1]} m")
print(f"doppler bin count: {doppler_bins}, max velocity: {doppler_axis[-1]} m/s")

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

plt.figure(2)
plt.imshow(cfar_diff > 2, cmap="gray", vmin=0, vmax=1, aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[-1], doppler_axis[0]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map with CFAR')

plt.figure(3)
plt.plot(range_axis, shifted[len(shifted)//2], label='radar')
plt.plot(range_axis, cfar[len(shifted)//2], label='cfar')
plt.xlabel('Range (m)')
plt.legend()

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