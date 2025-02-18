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
f_c = 10e9 # center frequency
bw = 1e9 # bandwidth
t_chirp = 16e-6 # chirp time
prp=40e-6 # Pulse Repetition Period

r_max = (c * t_chirp) / 2 # calculate the maximum range
delta_R = c / (2 * bw)  # Calculate range resolution (meters / bin)

print(f"max range: {r_max}m; range resolution: {delta_R}m")

wavelength = c / f_c

N_tx = 1
N_rx = 1

tx_channels = []
tx_channels.append(
    dict(
        location=(0, -N_rx / 2 * wavelength / 2, 0),
    )
)

# tx_channels.append(
#     dict(
#         location=(0, wavelength * N_rx / 2 - N_rx / 2 * wavelength / 2, 0),
#     )
# )

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
    tx_power=150,
    prp=prp,
    pulses=512,
    channels=tx_channels,
)

rx = Receiver(
    fs=20e6,
    noise_figure=8,
    rf_gain=20,
    load_resistor=500,
    baseband_gain=30,
    channels=rx_channels,
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

true_theta = [-5, -4, 45]

target_1 = dict(
    location=(
        #10 * np.cos(np.radians(true_theta[0])),
        #10 * np.sin(np.radians(true_theta[0])),
        0,
        10,
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)
target_2 = dict(
    location=(
        40 * np.cos(np.radians(true_theta[1])),
        40 * np.sin(np.radians(true_theta[1])),
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)
target_3 = dict(
    location=(
        #40 * np.cos(np.radians(true_theta[2])),
        #40 * np.sin(np.radians(true_theta[2])),
        0,
        40,
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)

targets = [target_1, target_3] #, target_2


data = sim_radar(radar, targets)
timestamp = data["timestamp"]
baseband = data["baseband"]+data["noise"]


range_window = signal.windows.chebwin(radar.sample_prop["samples_per_pulse"], at=80)
doppler_window = signal.windows.chebwin(
    radar.radar_prop["transmitter"].waveform_prop["pulses"], at=60
)

range_doppler = proc.range_doppler_fft(baseband, rwin=range_window, dwin=doppler_window)

doppler_bins = len(range_window)
range_bins = len(range_window)

shifted = fft.fftshift(range_doppler[0], axes=(0,))
results = 20 * np.log10(np.abs(shifted))

# Compute range axis
range_axis = np.arange(range_bins) * delta_R  # Convert bin index to meters

doppler_max = ((wavelength * (1 / (2 * prp))) / 2)
doppler_axis = np.linspace(-doppler_max, doppler_max, doppler_bins)

print(f"range bin count: {range_bins}, max range: {range_axis[-1]} m")
print(f"doppler bin count: {doppler_bins}, max velocity: {doppler_axis[-1]} m/s")


# Plot the 2D array
plt.imshow(results, cmap='viridis', aspect='auto', extent=[range_axis[0], range_axis[-1], doppler_axis[0], doppler_axis[-1]])
plt.colorbar(label='Amplitude (dB)')
plt.xlabel('Range (m)')
plt.ylabel('Velocity (m/s)')
plt.title('Range-Doppler Map')
plt.show()

exit()

det_idx = [np.argmax(np.mean(np.abs(range_doppler[:, 0, :]), axis=0))]

bv = range_doppler[:, 0, det_idx[0]]
bv = bv / linalg.norm(bv)

# snapshots = 20

# bv_snapshot = np.zeros((N_tx * N_rx - snapshots, snapshots), dtype=complex)

# for idx in range(0, snapshots):
#     bv_snapshot[:, idx] = bv[idx : (idx + N_tx * N_rx - snapshots)]

# covmat = np.cov(bv_snapshot.conjugate())

fft_spec = 20 * np.log10(np.abs(fft.fftshift(fft.fft(bv.conjugate(), n=1024))))

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=np.arcsin(np.linspace(-1, 1, 1024, endpoint=False)) / np.pi * 180,
        y=fft_spec,
        name="FFT",
    )
)

fig.update_layout(
    title="FFT",
    yaxis=dict(title="Amplitude (dB)"),
    xaxis=dict(title="Angle (deg)"),
    margin=dict(l=10, r=10, b=10, t=40),
)

# uncomment this to display interactive plot
fig.show()

# display static image to reduce size on radarsimx.com
# img_bytes = fig.to_image(format="jpg", scale=2)
# display(Image(img_bytes))