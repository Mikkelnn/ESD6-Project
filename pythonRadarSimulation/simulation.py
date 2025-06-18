import radarsimpy
from radarsimpy import Radar, Transmitter, Receiver
import radarsimpy.processing as proc
from radarsimpy.simulator import sim_radar

import numpy as np
from scipy import signal, linalg, fft
import plotly.graph_objs as go
from IPython.display import Image
import matplotlib.pyplot as plt
import csv

from tqdm import tqdm
import time


# print("`RadarSimPy` used in this example is version: " + str(radarsimpy.__version__))

c = 3e8
f_c = 5.8e9 # center frequency
wavelength = c / f_c

bw = 20.0e6 # bandwidth
t_chirp = 4.6e-6 # chirp time
prp=5e-6 # Pulse Repetition Period
pulses = 128

fs = 46e6 # 50e6 # IF fs

#initialize simulation parameters
maxRange = 700.0
resRange = 20
stepsRange = int(maxRange/resRange)
maxVelocity = 15000.0
# resVelocity = 5
# stepsVelocity = int(1 + maxVelocity//resVelocity)
stepsVelocity = 1 + 15
maxAngle = 50.0
resAngle = 20
stepsAngle = int(maxAngle/resAngle)

Ranges = []
Velocities = []
Angles = []

for i in range (stepsRange):
    Ranges.append(maxRange*(i+1)/stepsRange)

for i in range (stepsVelocity+1):
    Velocities.append(maxVelocity*i/stepsVelocity)

for i in range (-stepsAngle, stepsAngle+1):
    Angles.append(maxAngle*i/stepsAngle)

r_max = (c * t_chirp) / 2 # calculate the maximum range
delta_R = c / (2 * bw)  # Calculate range resolution (meters / bin)
doppler_max = wavelength / (4 * prp) #((wavelength * (1 / (2 * prp))) / 2)
delta_velocity = wavelength / (2 * pulses * prp)

# print(f"max range: {round(r_max, 2)} m; range resolution: {round(delta_R, 3)} m")
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
    tx_power=40, # 40
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

rcs = 10

print(f"Actual angle: {Angles[2]} Angle 1: {np.cos(np.radians(Angles[2]))} Angle 2: {np.sin(np.radians(Angles[2]))}")
print(f"Range: {Ranges[24]} Velocity: {Velocities[1]}")

# velocity resolution
cos_val = np.float64(Ranges[24]*np.cos(np.radians(Angles[2])))
sin_val = np.float64(Ranges[24]*np.sin(np.radians(Angles[2])))

print(f"cos: {cos_val}, sin: {sin_val}")

target_1 = dict(
    location=(
        cos_val,
        sin_val,
        0,
    ),
    speed=(0, Velocities[1], 0),
    rcs=rcs,
    phase=0,
)

print(target_1)

# velocity resolution
target_2 = dict(
    location=(
        0,
        500,
        0,
    ),
    speed=(0, 0.55, 0),
    rcs=rcs,
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
    rcs=rcs,
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
    rcs=rcs,
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
    rcs=rcs,
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
    rcs=rcs,
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
    rcs=rcs,
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
    rcs=rcs,
    phase=0,
)


targets = [target_1]
# targets = [target_1, target_3]

data = sim_radar(radar, targets)
timestamp = data["timestamp"]
baseband = data["baseband"] #+ data["noise"]

# Save data to file
with open('simData/TestOfManySim.npy', 'wb') as f:
    np.save(f, baseband)



#Do a lot of simulations
# with open('IDValues.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['id', 'range', 'velocity', 'angle'])  # Header

#     for i in tqdm(range(len(Ranges))):
#         for j in range(len(Velocities)):
#             for k in range(len(Angles)):
#                 targetLoop = dict(
#                     location=(
#                         Ranges[i] * np.cos(np.radians(Angles[k])),
#                         Ranges[i] * np.sin(np.radians(Angles[k])),
#                         0,
#                     ),
#                     speed=(0, Velocities[j], 0),
#                     rcs=rcs,
#                     phase=0,
#                 )
                
#                 targets = [targetLoop]      

#                 data = sim_radar(radar, targets)
#                 timestamp = data["timestamp"]
#                 baseband = data["baseband"] #+ data["noise"]

#                 # Save data to file
#                 filename = f'simDataLoopChirp/Target{i}{j}{k}.npy'
#                 with open(filename, 'wb') as f:
#                     np.save(f, baseband)

#                 #Save ids and their respective values for later use
#                 id_str = f"{i}{j}{k}"
#                 row = [id_str, Ranges[i], Velocities[j], Angles[k]]
#                 writer.writerow(row)