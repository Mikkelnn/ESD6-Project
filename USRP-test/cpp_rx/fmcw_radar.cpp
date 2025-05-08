#include <string>
#include <chrono>
// #include <iostream>
#include "usrp_manager.cpp"
#include "../../Beamforming/beamSteering.cpp"
#include "chirp.h"

class FMCMRadar {
private:
    // RF settings
    int num_channels = 1;
    double rx_sample_rate = 49.152e6;
    double tx_sample_rate = 245.760e6;
    double center_freq = 5.8e9;

    // classes used
    USRPManager _usrp_mgr;
    BeamSteer _beamSteer;

    // "user" settings
    int chirpsInFrame = 128;
    int startSweepAngleDeg = 0; // -60;
    int endSweepAngleDeg = 0; // 60;
    int sweepResolutionDeg = 5;

    // timings/settings
    double chirp_repetition = 11e-6; // 11 micro seconds
    double chirp_time = 10e-6; // 10 micro seconds
    int tx_chirp_samples_length = 2457; // static from "chirps.h"
    int rx_num_samples_frame = chirp_repetition * (double)chirpsInFrame * rx_sample_rate;
    int rx_num_samples_chirp_repetition = chirp_repetition * rx_sample_rate; // samples during a single cchirp + tailing spaceing
    int rx_num_samples_chirp = chirp_time * rx_sample_rate; // samples of single chirp

public:
    // tx and rx buffers
    std::vector<std::vector<std::complex<int16_t>>> beamBuffer;
    // flat storage per channel
    std::vector<std::vector<std::complex<int16_t>>> flat_rx_frame_buffer;
    // pointer-style 3D view - used to access flat_rx_buffers as: rx_buffer_view[chirp_idx][ch_idx][sample_idx]
    std::complex<int16_t>*** rx_buffer_view = nullptr;

public:
    FMCMRadar()
    {
        _usrp_mgr = USRPManager("addr=192.168.1.2", num_channels);
        _beamSteer = BeamSteer(num_channels);
        
        // setup buffers
        beamBuffer = std::vector<std::vector<std::complex<int16_t>>>(num_channels, std::vector<std::complex<int16_t>>(tx_chirp_samples_length));
        flat_rx_frame_buffer = std::vector<std::vector<std::complex<int16_t>>>(num_channels, std::vector<std::complex<int16_t>>(rx_num_samples_frame));


        // Allocate pointer-to-pointer-to-pointer view
        rx_buffer_view = new std::complex<int16_t>**[chirpsInFrame];
        for (int chirp = 0; chirp < chirpsInFrame; ++chirp) {
            rx_buffer_view[chirp] = new std::complex<int16_t>*[num_channels];
            for (int ch = 0; ch < num_channels; ++ch) {
                rx_buffer_view[chirp][ch] = flat_rx_frame_buffer[ch].data() + chirp * rx_num_samples_chirp_repetition;
            }
        }
    }

    void initialize() {
        // Step 1: General device setup
        usrp_mgr.setup_usrp();

        // Step 2: Specific RX / TX setup
        usrp_mgr.setup_rx(rx_sample_rate, center_freq, 20.0);
        usrp_mgr.setup_tx(tx_sample_rate, center_freq, 0.0); // Low TX gain for safety
    }

    void startSweep(/*std::chrono::steady_clock currentTime*/) {
        for (int beamAngle = startSweepAngleDeg; beamAngle <= endSweepAngleDeg; beamAngle += sweepResolutionDeg) {
            // steer beam and write to buffer
            _beamSteer.applyBeamformingAngle(beamAngle, I_chirp, Q_chirp, beamBuffer);

            // transmit frame using single steered chirp from buffer
            startFrame(beamBuffer, flat_rx_frame_buffer);
        }
    }

    // expect provided buffers for tx and rx is ready
    void startFrame(const auto &beamBuffer, const auto &rxFrameBuffer) {
        std::vector<void*> rx_buffer_ptrs;
        for (auto& buf : rxFrameBuffer) rx_buffer_ptrs.push_back(buf.data());

        std::vector<void*> beamBuffer_ptrs;
        for (auto& buf : beamBuffer) beamBuffer_ptrs.push_back(buf.data());

        auto time_spec_100ms_future = _usrp_mgr.usrp_future_time(0.1); // 100ms from now

        for (int i = 0; i < chirpsInFrame; i++) {
            auto chirp_tx_time = time_spec_100ms_future + ((double)i * chirp_repetition); // schedule chirps
            // schedule chirp TX
            _usrp_mgr.transmit_samples(beamBuffer_ptrs, tx_chirp_samples_length, chirp_tx_time);
        }
              
        // schedule simultanious rx, continuous over an enire frame
        int samples_in_frame_recieved = _usrp_mgr.receive_samples(rx_buffer_ptrs, rx_num_samples_frame, time_spec_100ms_future);
        if (samples_in_frame_recieved != rx_num_samples_frame) {
            std::cout << "[FMCW-RADAR] Warning only recieved: " << samples_in_frame_recieved << " samples, expected: " << rx_num_samples_frame << std::endl;
        }
    }
}