#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <iostream>

#define PI M_PI

class BeamSteer {
    private:
        unsigned int antenna_elements_;

    public:
        BeamSteer(unsigned int antenna_elements) : antenna_elements_(antenna_elements) {}

        int applyBeamformingAngle(int angle_deg, const std::vector<int16_t>& I_chirp, const std::vector<int16_t>& Q_chirp, std::vector<std::vector<std::complex<int16_t>>>& output, std::vector<float>& calibrations) {
            if (output.size() != antenna_elements_) {
                return 1; // Mismatched input lengths
            }
            
            float theta = angle_deg * PI / 180.0;
            float relative_phase_shift = -PI * sinf(theta);
            // std::cout << "relative_phase_shift:" << relative_phase_shift << "\n";

            for (int antenna = 0; antenna < antenna_elements_; ++antenna) {
                // Phase shift formula: φ = -π * n * sin(θ)
                float absolute_phase_shift = relative_phase_shift * (float)antenna;
                //std::cout << "antenna:" << antenna << " absolute_phase_shift" << absolute_phase_shift << "\n";

                // apply calibration
                absolute_phase_shift += calibrations[antenna];

                // Rad to Deg
                float theta_deg = absolute_phase_shift * 180.0 / PI;
                //std::cout << "theta_deg:" << theta_deg << "\n";
                int phase_status = applyPhaseToIQ(I_chirp, Q_chirp, theta_deg, output[antenna]);

                if (phase_status != 0) {
                    return phase_status;
                }
            }

            return 0;
        }

        int applyPhaseToIQ(const std::vector<int16_t>& I_chirp, const std::vector<int16_t>& Q_chirp, int phase_deg, std::vector<std::complex<int16_t>>& output) {
            if (I_chirp.size() != Q_chirp.size() || output.size() < I_chirp.size()) {
                return 1; // Mismatched input lengths
            }

            double phase_rad = phase_deg * PI / 180.0;
            //std::cout << "phase_deg" << phase_deg << "\n";
            double cos_phi = std::cos(phase_rad);
            double sin_phi = std::sin(phase_rad);
            // std::cout << "cos_phi " << cos_phi << "\n" << "sin_phi " << sin_phi << "\n";

            for (size_t i = 0, len = I_chirp.size(); i < len; ++i) {
                float I = static_cast<float>(I_chirp[i]) * cos_phi;
                float Q = static_cast<float>(Q_chirp[i]) * sin_phi;
                // std::cout << "I:  " << I  << " Q:  " << Q << "\n";
                output[i] = std::complex<int16_t>(
                    static_cast<int16_t>(std::round(I)),
                    static_cast<int16_t>(std::round(Q))
                );
                // std::cout << "I_round: " << output[i].real() << " Q_round: " << output[i].imag() << "\n";
            }
            
            return 0;
        }
};
