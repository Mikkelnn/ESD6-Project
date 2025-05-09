#include <string>
#include <chrono>
// #include <iostream>
#include "usrp_manager.cpp"
#include "../../Beamforming/beamSteering.cpp"
#include "chirp.h"

class FMCWRadar {
private:
    // RF settings
    unsigned int num_channels = 1;
    double rx_sample_rate = 61.440e6; // 49.152e6;
    double tx_sample_rate = 245.760e6;
    double center_freq = 5.8e9;

    // classes used
    std::unique_ptr<IUSRPManager> _usrp_mgr;
    std::unique_ptr<BeamSteer> _beam_steer;

    // "user" settings
    int chirpsInFrame = 128; // 128;
    int startSweepAngleDeg = 0; // -60;
    int endSweepAngleDeg = 0; // 60;
    int sweepResolutionDeg = 5;

    // timings/settings
    double chirp_repetition = 11e-6; // 11 micro seconds
    double chirp_time = 10e-6; // 10 micro seconds
    int tx_chirp_samples_length = 2457; // static from "chirps.h"
    int tx_num_samples_chirp_repetition = chirp_repetition * tx_sample_rate; // samples during a single chirp + tailing spaceing
    int tx_num_samples_frame = chirp_repetition * (double)chirpsInFrame * tx_sample_rate;

    int rx_num_samples_frame = ceil(chirp_repetition * (double)chirpsInFrame * rx_sample_rate);
    int rx_num_samples_chirp_repetition = chirp_repetition * rx_sample_rate; // samples during a single chirp + tailing spaceing
    int rx_num_samples_chirp = chirp_time * rx_sample_rate; // samples of single chirp

public:
    // tx and rx buffers
    std::vector<std::vector<std::complex<int16_t>>> beamBuffer;
    // flat storage per channel
    std::vector<std::vector<std::complex<int16_t>>> flat_rx_frame_buffer;
    // pointer-style 3D view - used to access flat_rx_buffers as: rx_buffer_view[chirp_idx][ch_idx][sample_idx]
    std::complex<int16_t>*** rx_buffer_view = nullptr;

public:
    FMCWRadar() {
        // _usrp_mgr = std::make_unique<USRPManager>("addr=192.168.1.2", num_channels);
        _usrp_mgr = std::make_unique<USRPManager_Mock>();
        _beam_steer = std::make_unique<BeamSteer>(num_channels);

        if (rx_num_samples_frame % 2 != 0)
            rx_num_samples_frame++; // ensure its even number...

        // setup buffers
        beamBuffer = std::vector<std::vector<std::complex<int16_t>>>(num_channels, std::vector<std::complex<int16_t>>(tx_num_samples_chirp_repetition, std::complex<int16_t>(0,0)));
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
        _usrp_mgr->setup_usrp();



        // Step 2: Specific RX / TX setup
        _usrp_mgr->setup_rx(rx_sample_rate, center_freq, 20.0);
        _usrp_mgr->setup_tx(tx_sample_rate, center_freq, 0.0); // Low TX gain for safety
    }

    void startSweep(/*std::chrono::steady_clock currentTime*/) {
        std::vector<int16_t> I_vec(I_chirp, I_chirp + tx_chirp_samples_length);
        std::vector<int16_t> Q_vec(Q_chirp, Q_chirp + tx_chirp_samples_length);

        for (int beamAngle = startSweepAngleDeg; beamAngle <= endSweepAngleDeg; beamAngle += sweepResolutionDeg) {
            // steer beam and write to buffer
            int status = _beam_steer->applyBeamformingAngle(beamAngle, I_vec, Q_vec, beamBuffer);
            if (status != 0)
                std::cerr << "Error while steering beam!" << std::endl;

            // transmit frame using single steered chirp from buffer
            startFrame(beamBuffer, flat_rx_frame_buffer);
        }
    }

    // expect provided buffers for tx and rx is ready
    void startFrame(auto& beamBuffer, auto& rxFrameBuffer) {
        std::vector<void*> rx_buffer_ptrs;
        for (auto& buf : rxFrameBuffer) rx_buffer_ptrs.push_back(buf.data());

        std::vector<std::vector<std::complex<int16_t>>> tx_frame_buffer(num_channels);
        for (int ch = 0; ch < num_channels; ch++) {
            auto& frame_ch = tx_frame_buffer[ch];
            const auto& beam_ch = beamBuffer[ch];

            frame_ch.reserve(beam_ch.size() * chirpsInFrame);  // Pre-allocate memory
            
            for (int i = 0; i < chirpsInFrame; i++) {
                frame_ch.insert(frame_ch.end(), beam_ch.begin(), beam_ch.end());
            }
        }

        std::vector<void*> beamBuffer_ptrs;
        for (auto& buf : tx_frame_buffer) beamBuffer_ptrs.push_back(buf.data());

        auto time_spec_100ms_future = _usrp_mgr->usrp_future_time(5); // 100ms from now

        // for (int i = 0; i < chirpsInFrame; i++) {
        //     // auto chirp_tx_time = time_spec_100ms_future + ((double)i * chirp_repetition); // schedule chirps
        //     // schedule chirp TX
        //     // size_t samples_sent = _usrp_mgr->transmit_samples(beamBuffer_ptrs, tx_chirp_samples_length, chirp_tx_time);
        //     // size_t samples_sent = _usrp_mgr->transmit_samples(beamBuffer_ptrs, tx_num_samples_chirp_repetition, chirp_tx_time);

        //     // if (samples_sent != tx_num_samples_chirp_repetition) {
        //     //     std::cerr << "Warning: Only sent " << samples_sent << " out of " << tx_num_samples_chirp_repetition << " samples.\n";
        //     // }            
        // }

        size_t samples_sent = _usrp_mgr->transmit_samples(beamBuffer_ptrs, tx_num_samples_frame, time_spec_100ms_future);
        
        if (samples_sent != tx_num_samples_frame) {
                std::cerr << "Warning: Only sent " << samples_sent << " out of " << tx_num_samples_frame << " samples.\n";
        }


        // send all chirps by repeating single chirp N times, done by setting num_samples = chirps * single_chirp_repition
        // _usrp_mgr->transmit_samples(beamBuffer_ptrs, tx_num_samples_frame, time_spec_100ms_future);

        // schedule simultanious rx, continuous over an enire frame
        int samples_in_frame_recieved = _usrp_mgr->receive_samples(rx_buffer_ptrs, rx_num_samples_frame, time_spec_100ms_future);
        if (samples_in_frame_recieved != rx_num_samples_frame) {
            std::cout << "[FMCW-RADAR] Warning only recieved: " << samples_in_frame_recieved << " samples, expected: " << rx_num_samples_frame << std::endl;
        }
    }
};