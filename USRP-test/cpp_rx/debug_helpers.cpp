#include <vector>
#include <complex>
#include <fstream>
#include <iostream>

void save_rx_buffers_to_csv_complex(const std::vector<std::vector<std::complex<int16_t>>>& rx_buffers, const std::string& filename) {
    if (rx_buffers.empty()) {
        std::cerr << "No data to save.\n";
        return;
    }

    size_t num_channels = rx_buffers.size();
    size_t num_samples = rx_buffers[0].size();

    std::ofstream outfile(filename);
    if (!outfile.is_open()) {
        std::cerr << "Error opening file: " << filename << "\n";
        return;
    }

    // Write header
    for (size_t ch = 0; ch < num_channels; ++ch) {
        outfile << "ch" << ch << "_real,ch" << ch << "_imag";
        if (ch != num_channels - 1) {
            outfile << ",";
        }
    }
    outfile << "\n";

    // Write data
    for (size_t samp = 0; samp < num_samples; ++samp) {
        for (size_t ch = 0; ch < num_channels; ++ch) {
            const std::complex<int16_t>& sample = rx_buffers[ch][samp];
            outfile << sample.real() << "," << sample.imag();
            if (ch != num_channels - 1) {
                outfile << ",";
            }
        }
        outfile << "\n";
    }

    outfile.close();
    std::cout << "Saved " << num_samples << " samples from " << num_channels << " channels to " << filename << "\n";
}

void save_rx_buffers_to_csv_phase_diff(const std::vector<std::vector<std::complex<int16_t>>>& rx_buffers, const std::string& filename) {
    if (rx_buffers.empty()) {
        std::cerr << "No data to save.\n";
        return;
    }

    size_t num_channels = rx_buffers.size();
    size_t num_samples = rx_buffers[0].size();

    std::ofstream outfile(filename);
    if (!outfile.is_open()) {
        std::cerr << "Error opening file: " << filename << "\n";
        return;
    }

    // Write header
    for (size_t ch = 0; ch < num_channels; ++ch) {
        outfile << "ch" << ch << "_phase_deg";
        if (ch != num_channels - 1) {
            outfile << ",";
        }
    }
    outfile << "\n";

    for (size_t samp = 0; samp < num_samples; ++samp) {
        // Get reference sample (channel 0)
        std::complex<float> ref_sample = std::complex<float>(rx_buffers[0][samp].real(), rx_buffers[0][samp].imag());
        float ref_phase = std::arg(ref_sample); // phase in radians

        for (size_t ch = 0; ch < num_channels; ++ch) {
            std::complex<float> sample = std::complex<float>(rx_buffers[ch][samp].real(), rx_buffers[ch][samp].imag());
            float phase = std::arg(sample); // radians
            float phase_diff = phase - ref_phase; // relative to ch0

            // Normalize phase_diff to [-pi, pi] range
            if (phase_diff > M_PI) phase_diff -= 2 * M_PI;
            if (phase_diff < -M_PI) phase_diff += 2 * M_PI;

            // Write phase difference in degrees
            outfile << (phase_diff * 180.0f / static_cast<float>(M_PI));
            if (ch != num_channels - 1) {
                outfile << ",";
            }
        }
        outfile << "\n";
    }

    outfile.close();
    std::cout << "Saved " << num_samples << " samples from " << num_channels << " channels to " << filename << "\n";
}