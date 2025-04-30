import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load CSV
file_path = r'c:/Users/theil/OneDrive/Skrivebord/ESD6-Project/Transceiver/phaseShiftFilesV2/phaseShiftData0.csv'
df = pd.read_csv(file_path)

# Unwrap phase (convert deg to rad, unwrap, then back to deg)
unwrapped_df = pd.DataFrame()
for col in df.columns:
    radians = np.deg2rad(df[col].values)
    unwrapped = np.unwrap(radians)
    unwrapped_deg = np.rad2deg(unwrapped)
    unwrapped_df[col] = unwrapped_deg

# Calculate statistics
stats = {}
for col in unwrapped_df.columns:
    stats[col] = {
        'mean': np.mean(unwrapped_df[col]),
        'variance': np.var(unwrapped_df[col]),
        'std_dev': np.std(unwrapped_df[col])
    }

# Print results
print("=== Phase Analysis (after unwrapping) ===")
for ch, values in stats.items():
    print(f"\n{ch}:")
    for stat_name, val in values.items():
        print(f"  {stat_name.capitalize()}: {val:.2f}°")

# Optional: Plot one of the channels
unwrapped_df.plot(title="Unwrapped Phase per Channel", figsize=(12, 6))
plt.xlabel("Sample Index")
plt.ylabel("Phase (degrees)")
plt.grid(True)
plt.show()
