#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>
#include <cstdint>
#include <complex>
#include "beamSteering.cpp"

#ifndef PI
#define PI 3.141592653589793
#endif

const double AMP = 30000.0;
const int N = 1024;

using namespace std;

// ------------------------------------------------ Unit tests ------------------------------------------- 

// --- Test of basic projection---
void test_basic_projection() {
    // Generate vectors I and Q of length N
    vector<int16_t> I(N), Q(N);
    for (int i = 0; i < N; ++i) {
        // Generate cos and sin values
        I[i] = static_cast<int16_t>(cos(2 * PI * i / N) * AMP);
        Q[i] = static_cast<int16_t>(sin(2 * PI * i / N) * AMP);
    }
    // Initialize output buffer of length N
    std::vector<std::complex<int16_t>> output(N);
    // BeamSteer(1) = simulate for 1 element; with a 90° rotation to IQ
    BeamSteer(1).applyPhaseToIQ(I, Q, 90, output);

    // Check if phase shift was succesfull at each output sample
    for (int i = 0; i < N; ++i) {
        float expected_I = 0;  // ~0
        float expected_Q = Q[i];  // unchanged

        // Allowing a margin of error because of rounding and int conversion
        assert(std::abs(output[i].real() - expected_I) < 100);
        assert(std::abs(output[i].imag() - expected_Q) < 100);
    }

    std::cout << "test_basic_projection passed\n";
}

// --- Test of 0 phase ---
void test_zero_phase() {
    vector<int16_t> I(N, 1234), Q(N, 5678);
    std::vector<std::complex<int16_t>> output(N);
    BeamSteer(1).applyPhaseToIQ(I, Q, 0, output);
    for (int i = 0; i < N; ++i) {
        assert(output[i].real() == I[i] && "zero phase I is the problem child");
        assert(output[i].imag() == 0 && "zero phase Q is the problem child"); // sin(0) * Q = 0
    }
    std::cout << "test_zero_phase passed\n";
}

// --- Test of negative phases ---
void test_negative_phase() {
    vector<int16_t> I(N, 1000), Q(N, 1000);
    std::vector<std::complex<int16_t>> output(N);
    BeamSteer(1).applyPhaseToIQ(I, Q, -90, output);

    for (int i = 0; i < N; ++i) {
        float expected_I = 1000 * cos(-PI / 2); // ~0
        float expected_Q = 1000 * sin(-PI / 2); // -1000
        assert(std::abs(output[i].real() - expected_I) < 50 && "negative_phase I is the problem child");
        assert(std::abs(output[i].imag() - expected_Q) < 50 && "negative_phase Q is the problem child");
    }

    std::cout << "test_negative_phase passed\n";
}

// --- Test of no input---
void test_empty_input() {
    vector<int16_t> I, Q;
    vector<complex<int16_t>> output;
    BeamSteer(1).applyPhaseToIQ(I, Q, 45, output);
    assert(output.empty() && "empty test is the problem child");
    std::cout << "test_empty_input passed\n";
}

// --- Test of length of I, Q, and output ---
void test_length_mismatch() {
    BeamSteer steer(1);

    // Length missmatch between 'I' and 'Q'. Return 1
    vector<int16_t> I(10, 100), Q(11, 100);
    vector<complex<int16_t>> output;
    int status = steer.applyPhaseToIQ(I, Q, 45, output);
    assert(status == 1 && "Did not detect length missmatch between 'I' and 'Q'");

    // Length missmatch between 'I' and 'output'. Return 1
    Q.resize(10);
    output.resize(11);
    status = steer.applyPhaseToIQ(I, Q, 45, output);
    assert(status == 0 && "Did not detect length missmatch between 'I' and 'Output'");

    // No length missmatch between 'I', 'Q', and 'output'. Return 0
    output.resize(10);
    status = steer.applyPhaseToIQ(I, Q, 45, output);
    assert(status == 0 && "There were no length missmatch between 'I', 'Q', and 'Output'");

    Q.resize(10);
    output.resize(3);
    status = steer.applyPhaseToIQ(I, Q, 45, output);
    assert(status == 1 && "Did not detect 'Output' smaller than 'I");
    std::cout << "test_length_mismatch passed (caught size mismatch)\n";
}

// --- Test of output buffer has correct size ---
void test_tx_buffer_size() {
    
    // Setup
    int N = 2; // numer of elements to test with
    vector<int16_t> I(10, 0), Q(10, 0); // initalize test IQ signals
    BeamSteer steer(N); // create an instance of the class under test

    // --- Smaller than N elements test
    std::vector<std::vector<std::complex<int16_t>>> output(N - 1); // should have a size < N
    int status = steer.steer(0, I, Q, output);
    assert(status == 1 && "Buffer is smaller than the antenna elements");

    // --- Larger than N elements test
    output.resize(N + 1); // should have a size > N
    status = steer.steer(0, I, Q, output);
    assert(status == 1 && "Buffer is larger than the antenna elements");
    

    std::cout << "test_tx_buffer_size passed\n";
}

//--- Test of zero angle = no phase shift ---
void test_zero_angle_preserves_IQ() {
    
    // Setup
    int IQ_length = 10;
    int N = 4;
    vector<int16_t> I(IQ_length, 100), Q(IQ_length, 50); // Initialize IQ 
    BeamSteer steer(N);
    std::vector<std::vector<std::complex<int16_t>>> output(N, vector<std::complex<int16_t>>(IQ_length));
    int status = steer.steer(0, I, Q, output);

    assert(status == 0);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < IQ_length; j++) {
            //std::cout << "I: " << output[0][i].real() << " Q: " << output[0][i].imag() << "\n";
            assert(std::abs(output[0][i].real() - I[i]) <= 1 && "Real part of zero angle");
            assert(std::abs(output[0][i].imag() - 0) <= 1 && "Real part of zero angle");
        }
    }

    std::cout << "test_zero_angle_preserves_IQ passed\n";
}

//--- Test of positive angle applies increasing phase shift ---
void test_positive_beam_angle_shift() {
    int IQ_length = 10;
    int N = 4;
    int beam_angle = 50;
    vector<int16_t> I(IQ_length, 100), Q(IQ_length, 100); // Initialize IQ
    BeamSteer steer(N);
    std::vector<std::vector<std::complex<int16_t>>> output(N, vector<std::complex<int16_t>>(IQ_length));
   
    int status = steer.steer(beam_angle, I, Q, output);
    
    // for (int samples = 0; samples < IQ_length; samples++) {
    //     for (int element = 0; element < N; element++) {
    //         std::cout << "    " << output[element][samples];
    //     }
    //     std::cout << "\n";
    // }
    
    assert(status == 0);
    std::complex<int16_t> ref = output[0][IQ_length-1];
    std::complex<float> ref_float = std::complex<float>(static_cast<float>(ref.real()), static_cast<float>(ref.imag()));

    float angle_rad = beam_angle * PI / 180.0;
    
    auto normalize_phase = [](float deg) -> float {
        while (deg > 180.0f) deg -= 360.0f;
        while (deg < -180.0f) deg += 360.0f;
        return deg;
    };

    for (int i = 0; i < N; i++) {
        std::complex<int16_t> shifted = output[i][IQ_length-1];
        std::complex<float> shifted_float = std::complex<float>(static_cast<float>(shifted.real()), static_cast<float>(shifted.imag()));
        //std::cout << "shifted_float: " << std::arg(shifted_float) << "\n";
        
        float phase_deg = (std::arg(shifted_float) - std::arg(ref_float)) * 180 / PI;
        // std::cout << "Phase deg:" << phase_deg << " i:" << i << "\n";
        float expected_phase = -180.0 * std::sin(angle_rad) * i;
        float diff = normalize_phase(phase_deg - expected_phase);
        assert(std::abs(diff) <= 1);
    }
    

    std::cout << "test_positive_beam_angle_shift passed (" << beam_angle << "deg)\n";
}

void test_negative_angle_phase_shift() {
    int IQ_length = 10;
    int N = 4;
    int beam_angle = -50;
    vector<int16_t> I(IQ_length, 100), Q(IQ_length, 100); // Initialize IQ
    BeamSteer steer(N);
    std::vector<std::vector<std::complex<int16_t>>> output(N, vector<std::complex<int16_t>>(IQ_length));
   
    int status = steer.steer(beam_angle, I, Q, output);
    
    // for (int samples = 0; samples < IQ_length; samples++) {
    //     for (int element = 0; element < N; element++) {
    //         std::cout << "    " << output[element][samples];
    //     }
    //     std::cout << "\n";
    // }
    
    assert(status == 0);
    std::complex<int16_t> ref = output[0][IQ_length-1];
    std::complex<float> ref_float = std::complex<float>(static_cast<float>(ref.real()), static_cast<float>(ref.imag()));

    float angle_rad = beam_angle * PI / 180.0;
    
    auto normalize_phase = [](float deg) -> float {
        while (deg > 180.0f) deg -= 360.0f;
        while (deg < -180.0f) deg += 360.0f;
        return deg;
    };

    for (int i = 0; i < N; i++) {
        std::complex<int16_t> shifted = output[i][IQ_length-1];
        std::complex<float> shifted_float = std::complex<float>(static_cast<float>(shifted.real()), static_cast<float>(shifted.imag()));
        //std::cout << "shifted_float: " << std::arg(shifted_float) << "\n";
        
        float phase_deg = (std::arg(shifted_float) - std::arg(ref_float)) * 180 / PI;
        // std::cout << "Phase deg:" << phase_deg << " i:" << i << "\n";
        float expected_phase = -180.0 * std::sin(angle_rad) * i;
        float diff = normalize_phase(phase_deg - expected_phase);
        assert(std::abs(diff) <= 1);
    }
    

    std::cout << "test_negative_beam_angle_shift passed (" << beam_angle << "deg)\n";
}

//--- Test of negative angle applies decreasing phase shift ---
void test_same_amplitude_multiple_angles() {
    int IQ_length = 10;
    int N = 4;
    std::vector<int> beam_angles = {-45, -30, 0, 30, 45};
    std::vector<int16_t> I(IQ_length, 100), Q(IQ_length, 100); // Same amplitude for both

    BeamSteer steer(N);

    auto normalize_phase = [](float deg) -> float {
        while (deg > 180.0f) deg -= 360.0f;
        while (deg < -180.0f) deg += 360.0f;
        return deg;
    };

    for (int angle : beam_angles) {
        std::vector<std::vector<std::complex<int16_t>>> output(N, std::vector<std::complex<int16_t>>(IQ_length));
        int status = steer.steer(angle, I, Q, output);
        assert(status == 0);

        std::complex<int16_t> ref = output[0][IQ_length - 1];
        std::complex<float> ref_float(static_cast<float>(ref.real()), static_cast<float>(ref.imag()));
        float angle_rad = angle * PI / 180.0f;

        // std::cout << "\n Beam angle = " << angle << " deg\n";

        for (int i = 0; i < N; i++) {
            std::complex<int16_t> shifted = output[i][IQ_length - 1];
            std::complex<float> shifted_float(static_cast<float>(shifted.real()), static_cast<float>(shifted.imag()));

            float phase_deg = (std::arg(shifted_float) - std::arg(ref_float)) * 180.0f / PI;
            float expected_phase = -180.0 * std::sin(angle_rad) * i;
            float diff = normalize_phase(phase_deg - expected_phase);

            // std::cout << "  Element " << i
            //           << " | I: " << shifted.real()
            //           << ", Q: " << shifted.imag()
            //           << ", Amplitude: " << std::abs(shifted_float)
            //           << ", Phase: " << phase_deg
            //           << " deg (Expected: " << expected_phase << " deg)\n";

            assert(std::abs(diff) <= 1);
        }

        // std::cout << "Passed for beam angle: " << angle << " deg\n";
    }
        std::cout << "test_same_amplitude_multiple_angle passed \n";
}

void test_real_signal(){
    
    // Variable Setup
    int N = 4; // Number of elements
    int IQ_length = 4096; // Number of IQ samples
    std::vector<int16_t> I(IQ_length), Q(IQ_length), IQcomp(IQ_length); // Initiliaze IQ
    int amp_desired = 16000; // Desired amplitude
    int angle_desired = 20; // The beam angle
    double phase_expected = 360.0 - 61.56362581; // Expected relative phase shift
    int f = 10; // frequency
    float sample_rate = 10e3;
    
    // Instance Setup; instance with N element
    BeamSteer steer(N); 

    // Generate I & Q signal (I + jQ)
    for (int n = 0; n < IQ_length; n++) {
        float t = static_cast<float>(n) / sample_rate; // Time for each sample
        I[n] = static_cast<int16_t>(std::round(amp_desired * std::cos(2*PI*f*t)));
        Q[n] = static_cast<int16_t>(std::round(amp_desired * std::sin(2*PI*f*t)));
        // std::cout << " I: " << I[n] << " | Q: " << Q[n] << "  t  " << t <<  "\n";
    }

    // Apply beam steering
    std::vector<std::vector<std::complex<int16_t>>> output(N, std::vector<std::complex<int16_t>>(IQ_length));
    int status = steer.steer(angle_desired, I, Q, output);
    assert(status == 0); // Check everything is alright


    for (int i = 0; i < N; i++) {
        int maxIQ = 0;  
        int maxSamp = 0; 
        
        for (int j = 0; j < IQ_length; j++) {
            IQcomp[j]=output[i][j].real()+output[i][j].imag(); // Creating new phase shift signal
            if(IQcomp[j]>maxIQ) {maxIQ = IQcomp[j]; maxSamp = j;} // Checking after a peak amplitude of the IQ signal 
        }

        float phase_actual = (float)(360*maxSamp*f)/(float)(sample_rate); // The calculated phase in degrees
        while (phase_actual > 360) { phase_actual -= 360; }

        int amp_delta = std::abs(maxIQ-amp_desired); // Check difference between the calculated and the expected amplitude
        
        float absolute_phase_expected = (phase_expected*i); // expected phase fir ith antenna
        while (absolute_phase_expected > 360) { absolute_phase_expected -= 360; }
        
        float phase_delta = std::abs(absolute_phase_expected - phase_actual); // Check difference between the calculated and the expected phase 
        std::cout<< "phase_actual: " << phase_actual << "  peak:  " << maxIQ << "  peak sample:  " << maxSamp << "\n";
    
        // Validation
        assert(amp_delta <= 1 && "The beam steered amplitude is not the same as the expected amplitude \n");
        assert(phase_delta <= 1 && "The beam steered phase is not the same as the expected phase \n");
    }       
}




int main() {
    test_zero_phase();
    test_basic_projection();
    test_negative_phase();
    test_empty_input();
    test_length_mismatch();
    test_tx_buffer_size();
    test_zero_angle_preserves_IQ();
    test_positive_beam_angle_shift();
    test_negative_angle_phase_shift();
    test_same_amplitude_multiple_angles();
    test_real_signal();
    std::cout << "🎉 All tests passed!\n";
    return 0;
}
