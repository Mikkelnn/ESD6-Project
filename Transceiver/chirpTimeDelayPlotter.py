import numpy as np
import matplotlib.pyplot as plt

# Parameters
f_start = 10        # Start frequency (Hz)
f_end = 8.2e6         # End frequency (Hz)
T_chirp = 3.6e-6       # Duration of chirp (s)
delay = 0.8e-6         # Delay of second chirp (s)
fs = 10e9             # Sampling frequency (Hz)
dt = 1 / fs            # Time step
t_end = delay + T_chirp + 0.5e-6  # Total signal duration with margin

# Time vector
t = np.arange(0, t_end, dt)

# Chirp rate (slope of frequency vs. time)
k = (f_end - f_start) / T_chirp

# First chirp: from t=0 to t=T_chirp
chirp1 = np.zeros_like(t)
idx1 = (t >= 0) & (t < T_chirp)
chirp1[idx1] = np.cos(2 * np.pi * (f_start * t[idx1] + 0.5 * k * t[idx1]**2))

# Second chirp: from t=delay to t=delay + T_chirp
chirp2 = np.zeros_like(t)
idx2 = (t >= delay) & (t < delay + T_chirp)
t2 = t[idx2] - delay  # Shifted time for second chirp
chirp2[idx2] = np.cos(2 * np.pi * (f_start * t2 + 0.5 * k * t2**2))

# Plotting
plt.figure(figsize=(10, 4))
plt.plot(t * 1e6, chirp1, label='Chirp 1', linewidth=1)
plt.plot(t * 1e6, chirp2, '--', label='Chirp 2', linewidth=1)
plt.xlabel('Time (µs)')
plt.ylabel('Amplitude')
plt.title('Time Delayed Chirp Comparison')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
