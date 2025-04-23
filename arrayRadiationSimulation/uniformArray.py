import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import chebwin

# Constants
c = 3e8  # Speed of light in m/s

def optimize_phases_for_hpbw_reduction(num_elements, spacing_factor, frequency):
    """
    Compute element phase shifts to reduce Half-Power Beamwidth (HPBW).
    :param num_elements: Number of elements in the array
    :param spacing_factor: Fraction of wavelength for element spacing
    :param frequency: Frequency in Hz
    :return: Phase shifts for each element in degrees
    """
    wavelength = c / frequency
    d = spacing_factor * wavelength
    k = 2 * np.pi / wavelength
    
    # Taylor or Dolph-Chebyshev weighting can be applied for HPBW reduction
    # Here, we use a simple tapered amplitude weighting as an approximation
    n = np.arange(num_elements)
    tapering = np.hanning(num_elements)  # Hann window for side lobe reduction
    phase_shifts = -k * d * np.sin(np.linspace(-np.pi/2, np.pi/2, num_elements)) * tapering
    
    return np.degrees(phase_shifts)

def array_factor(frequency, spacing_factor, beam_angle, num_elements, sidelobe_level_dB):
    """
    Calculate and plot the radiation pattern of a uniform linear array.
    :param frequency: Frequency in Hz
    :param spacing_factor: Fraction of wavelength for element spacing (e.g., 0.5 for λ/2)
    :param beam_angle: Desired beam angle in degrees (clockwise, 0° is normal to the array)
    :param num_elements: Number of elements in the array
    """
    wavelength = c / frequency
    d = spacing_factor * wavelength  # Element spacing in meters
    k = 2 * np.pi / wavelength  # Wave number
    theta = np.linspace(-180, 180, 10000) * np.pi / 180  # Convert to radians
    
    # Compute Dolph-Chebyshev amplitude weights
    amplitude_weights = chebwin(num_elements, at=sidelobe_level_dB)
    amplitude_weights /= np.max(amplitude_weights)  # Normalize weights
    
    # Compute phase shift per element for beam steering
    phase_shifts = -k * d * np.sin(np.radians(beam_angle)) * np.arange(num_elements)
    
    # Compute array factor with amplitude tapering and phase shifts
    AF = np.zeros_like(theta, dtype=complex)
    for n in range(num_elements):
        AF += np.exp(1j * (n * k * d * np.sin(theta) + phase_shifts[n])) # amplitude_weights[n] *
    AF = np.abs(AF)
    
    # Normalize to max value (convert to dB scale)
    AF_dB = 20 * np.log10(AF / np.max(AF))
    AF_dB[AF_dB < -40] = -40  # Limit minimum value to -40 dB for clarity
    
    # Plot Cartesian
    # plt.figure(figsize=(8, 6))
    # plt.plot(theta * 180 / np.pi, AF_dB)
    # plt.xlabel("Angle (degrees)")
    # plt.ylabel("Normalized Array Factor (dB)")
    # plt.title(f"Uniform Linear Array Radiation Pattern\n" 
    #           f"Frequency: {frequency / 1e9:.2f} GHz, Element Spacing: {d:.3f} m (λ/{1/spacing_factor:.1f}), Beam Angle: {beam_angle}°")
    # plt.ylim(-40, 0)
    # plt.grid()
    # plt.show()
    
    # Plot Polar
    plt.figure(figsize=(8, 8))
    plt.polar(theta, AF_dB)
    plt.title("Polar Radiation Pattern (dB Scale)")
    plt.show()
    
    # Compute phase shift per element
    
    print("Phase shifts used (degrees):", np.degrees(phase_shifts))


# Example usage
frequency = 5.8e9  # 10 GHz
spacing_factor = 1/2 # Half-wavelength spacing (λ/2)
beam_angle = 15  # Steering the main lobe to 30 degrees
num_elements = 4
sidelobe_level_dB = 45
array_factor(frequency, spacing_factor, beam_angle, num_elements, sidelobe_level_dB)
