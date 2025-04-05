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
t_chirp = 4.6e-6 # chirp time
prp=5e-6 # Pulse Repetition Period
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
    load_resistor=50,
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

# velocity resolution
target_1 = dict(
    location=(
        0,
        500,
        0,
    ),
    speed=(0, 0.5, 0),
    rcs=10,
    phase=0,
)

# velocity resolution
target_2 = dict(
    location=(
        0,
        500,
        0,
    ),
    speed=(0, 0.55, 0),
    rcs=10,
    phase=0,
)

# max velocity towards radar
target_3 = dict(
    location=(
        0,
        500,
        0,
    ),
    speed=(0, -15000.25, 0),
    rcs=10,
    phase=0,
)


# range
target_4 = dict(
    location=(
        #40 * np.cos(np.radians(true_theta[2])),
        #40 * np.sin(np.radians(true_theta[2])),
        0,
        1000,
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)

# angle max
target_5 = dict(
    location=(
        500 * np.cos(np.radians(80)),
        500 * np.sin(np.radians(80)),
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)

# angle max
target_6 = dict(
    location=(
        500 * np.cos(np.radians(-80)),
        500 * np.sin(np.radians(-80)),
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)

# angle res
target_7 = dict(
    location=(
        500 * np.cos(np.radians(35)),
        500 * np.sin(np.radians(35)),
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)

# angle res
target_8 = dict(
    location=(
        500 * np.cos(np.radians(40)),
        500 * np.sin(np.radians(40)),
        0,
    ),
    speed=(0, 0, 0),
    rcs=10,
    phase=0,
)


targets = [target_1, target_2, target_4, target_5, target_6, target_7, target_8] #, target_3
# targets = [target_1, target_3]

data = sim_radar(radar, targets)
timestamp = data["timestamp"]
baseband = data["baseband"] #+ data["noise"]

# Save data to file
with open('radarBaseband-no-t3.npy', 'wb') as f:
    np.save(f, baseband)
