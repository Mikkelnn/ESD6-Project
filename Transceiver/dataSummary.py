import pandas as pd
import os

# Folder containing your CSVs
folder = "c:/Users/theil/OneDrive/Skrivebord/ESD6-Project/Transceiver/phaseShiftFiles"
results = []

# Loop over all csv files
for file in sorted(os.listdir(folder)):
    if file.endswith(".csv"):
        path = os.path.join(folder, file)
        df = pd.read_csv(path)

        # Compute per-channel stats
        stats = {"File": file}
        for col in df.columns:
            stats[f"{col}_Mean"] = df[col].mean()
            stats[f"{col}_Var"] = df[col].var()
            stats[f"{col}_Std"] = df[col].std()

        results.append(stats)

# Create summary table
summary_df = pd.DataFrame(results)

# Save summary to a new CSV
summary_df.to_csv("phaseStatsSummary.csv", index=False)

# Also print it
print(summary_df)
