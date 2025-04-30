#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <time.h>


#define CHIRP_LENGTH 1024
#define NUM_TX 4
#define NUM_RX 4
#define SPEED_OF_LIGHT 3e8
#define PI M_PI

uint32_t tx_output[NUM_TX]; // Output format: 32-bit word = [I(upper 16) | Q(lower 16)]

// Apply phase shift for a given angle to all TX antennas
void applyBeamformingAngle(int angle_deg) {
    float theta = angle_deg * PI / 180.0;
    float wavelength = 1.0; // normalized to λ = 1
    float d = wavelength / 2.0;

    for (int antenna = 0; antenna < NUM_TX; antenna++) {
        // Phase shift formula: φ = -2πd * sin(θ) * n / λ
        float phase_shift = -2.0 * PI * d * sin(theta) * antenna;

        float A_I = cos(phase_shift);
        float A_Q = sin(phase_shift);

        // Example output: sum over chirp for test output (integration test)
        int32_t I_sum = 0;
        int32_t Q_sum = 0;

        for (int i = 0; i < CHIRP_LENGTH; i++) {
            float I = A_I * (float)I_chirp[i];
            float Q = A_Q * (float)Q_chirp[i];

            I_sum += (int32_t)I;
            Q_sum += (int32_t)Q;
        }

        // Scale and pack I and Q into 32-bit word (upper: I, lower: Q)
        uint16_t I_out = (uint16_t)((I_sum / CHIRP_LENGTH) & 0xFFFF);
        uint16_t Q_out = (uint16_t)((Q_sum / CHIRP_LENGTH) & 0xFFFF);
        tx_output[antenna] = ((uint32_t)I_out << 16) | Q_out;
    }
}
// Utility to extract phase from IQ
float computePhase(int16_t I, int16_t Q) {
    return atan2f((float)Q, (float)I) * 180.0 / PI;
}

void testBeamAngle(int angle_deg) {
    applyBeamformingAngle(angle_deg);

    printf("Beam angle: %d°\n", angle_deg);
    for (int i = 0; i < NUM_TX; i++) {
        int16_t I = (int16_t)(tx_output[i] >> 16);
        int16_t Q = (int16_t)(tx_output[i] & 0xFFFF);
        float phase = computePhase(I, Q);
        printf("TX[%d]: Phase = %.2f°, I = %d, Q = %d\n", i, phase, I, Q);
    }
}

void benchmarkApplyBeamforming(int angle) {
    clock_t start = clock();
    applyBeamformingAngle(angle);
    clock_t end = clock();
    double elapsed_ms = 1000.0 * (end - start) / CLOCKS_PER_SEC;
    printf("Time to compute beamforming for %d°: %.3f ms\n", angle, elapsed_ms);
}
