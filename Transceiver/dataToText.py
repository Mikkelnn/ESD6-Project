import numpy as np

# Load the raw interleaved phase data (float32, radians)
data = np.fromfile("c:/Users/theil/OneDrive/Skrivebord/ESD6-Project/Transceiver/phaseShift.dat", dtype=np.float32)

# Convert to degrees
data_deg = np.rad2deg(data)

# Number of channels
n_channels = 4

# Reshape: one row per sample, one column per channel
reshaped = data_deg.reshape((-1, n_channels))

# Save as CSV with 4 columns
np.savetxt("c:/Users/theil/OneDrive/Skrivebord/ESD6-Project/Transceiver/phaseShiftFilesV2/phaseShiftData0.csv",
           reshaped,
           delimiter=",",
           fmt="%.6f",
           header="Channel_1,Channel_2,Channel_3,Channel_4",
           comments="")
