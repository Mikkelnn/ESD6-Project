#include <string>
#include <chrono>
#include <future>  // For std::async
// #include <conio.h>
#include <iostream>
#include "usrp_manager.cpp"
#include "../../Beamforming/beamSteering.cpp"
#include "chirp.h"

class FMCWRadar {
private:
    // RF settings
    unsigned int num_channels = 4;
    double rx_sample_rate = 61.440e6;
    double tx_sample_rate = 61.440e6; // 245.760e6;
    double center_freq = 5.8e9;

    // classes used
    std::unique_ptr<IUSRPManager> _usrp_mgr;
    std::unique_ptr<BeamSteer> _beam_steer;

    // "user" settings
    int chirpsInFrame = 12; // 128;
    int startSweepAngleDeg = 0; // -60;
    int endSweepAngleDeg = 0; // 60;
    int sweepResolutionDeg = 5;

    // timings/settings
    double chirp_repetition = 4.8e-6; // micro seconds
    double chirp_time = 3.2e-6; // 10 micro seconds
    int tx_chirp_samples_length = 196; // static from "chirps.h"
    int tx_num_samples_chirp_repetition = chirp_repetition * tx_sample_rate; // samples during a single chirp + tailing spaceing
    int tx_num_samples_frame = chirp_repetition * (double)chirpsInFrame * tx_sample_rate;

    int rx_num_samples_frame = ceil(chirp_repetition * (double)chirpsInFrame * rx_sample_rate);
    int rx_num_samples_chirp_repetition = chirp_repetition * rx_sample_rate; // samples during a single chirp + tailing spaceing
    int rx_num_samples_chirp = chirp_time * rx_sample_rate; // samples of single chirp

    // calibration settings
    int offset_rx_samples = 102;
    std::vector<float> phase_offsets; // per channel phase calibration offset

public:
    // tx and rx buffers
    std::vector<std::vector<std::complex<int16_t>>> beamBuffer;
    // flat storage per channel
    std::vector<std::vector<std::complex<int16_t>>> flat_rx_frame_buffer;
    // pointer-style 3D view - used to access flat_rx_buffers as: rx_buffer_view[chirp_idx][ch_idx][sample_idx]
    std::complex<int16_t>*** rx_buffer_view = nullptr;

public:
    FMCWRadar() {
        _usrp_mgr = std::make_unique<USRPManager>("addr=192.168.1.2", num_channels, tx_num_samples_frame, rx_num_samples_frame);
        // _usrp_mgr = std::make_unique<USRPManager_Mock>();
        _beam_steer = std::make_unique<BeamSteer>(num_channels);

        if (rx_num_samples_frame % 2 != 0)
            rx_num_samples_frame++; // ensure its even number...

        // setup buffers
        beamBuffer = std::vector<std::vector<std::complex<int16_t>>>(num_channels, std::vector<std::complex<int16_t>>(tx_num_samples_chirp_repetition, std::complex<int16_t>(0,0)));
        flat_rx_frame_buffer = std::vector<std::vector<std::complex<int16_t>>>(num_channels, std::vector<std::complex<int16_t>>(rx_num_samples_frame));
        phase_offsets = std::vector<float>(num_channels, 0.0f);

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
        _usrp_mgr->setup_rx(rx_sample_rate, center_freq, 30.0);
        // _usrp_mgr->setup_tx(tx_sample_rate, center_freq, 0.0); // Low TX gain for safety
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

            // correct RX phase
            apply_phase_correction(flat_rx_frame_buffer, phase_offsets);
        }
    }

    void calibrate() {
        // calibrate_rx_sample_offset();
        calibrate_rx_phase();

        std::cout << "[FMCWRdar:Calibration] Plase connect antennas to TX/RX ports" << std::endl;
        std::cout << "Press any key to continue..." << std::endl;
        std::cin.get(); // wait for user response
    }

private:
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

        auto time_spec_future = _usrp_mgr->usrp_future_time(1); // 100ms from now

        _usrp_mgr->issue_stream_cmd(rx_num_samples_frame + offset_rx_samples, time_spec_future);

        // Launch RX in async thread and get future
        auto rx_future = std::async(std::launch::async, [&]() {
            return _usrp_mgr->receive_samples(rx_buffer_ptrs, rx_num_samples_frame, offset_rx_samples);
        });

        // Launch TX in async thread and get future
        auto tx_future = std::async(std::launch::async, [&]() {
            return _usrp_mgr->transmit_samples(beamBuffer_ptrs, tx_num_samples_frame, time_spec_future);
            // return tx_num_samples_frame;
        });

        // Wait for results
        size_t samples_sent = tx_future.get();
        size_t samples_received = rx_future.get();


        if (samples_sent != tx_num_samples_frame) {
            std::cerr << "[FMCW-RADAR] Warning: Only sent " << samples_sent << " out of " << tx_num_samples_frame << " samples.\n";
        }

        if (samples_received != rx_num_samples_frame) {
            std::cout << "[FMCW-RADAR] Warning only recieved: " << samples_received << " samples, expected: " << rx_num_samples_frame << std::endl;
        }
    }

    void apply_phase_correction(std::vector<std::vector<std::complex<int16_t>>>& buffer, std::vector<float>& phase_offset_rad) {
        for (int i = 0; i < buffer.size(); i++) {
            float phase_offset = phase_offset_rad[i];
            
            if (phase_offset == 0.0f) continue;

            std::complex<float> rotator = std::polar(1.0f, -phase_offset);  // e^{-jθ}

            for (std::complex<int16_t>& sample : buffer[i]) {
                std::complex<float> corrected = std::complex<float>(sample.real(), sample.imag()) * rotator;
                sample = std::complex<int16_t>(std::round(corrected.real()), std::round(corrected.imag()));
            }
        }        
    }

    // calibration
    void calibrate_rx_phase() {
        // tell user to hookup cabels, wait for user OK
        std::cout << "[FMCWRdar:calibrate_rx_phase] Plase connect signal generator [" << center_freq + 10e6 << " Hz] with splitter to each RX port" << std::endl;
        std::cout << "Press any key to continue..." << std::endl;
        // std::cin.get(); // wait for user response

        // sample in data
        std::vector<void*> rx_buffer_ptrs;
        for (auto& buf : flat_rx_frame_buffer) rx_buffer_ptrs.push_back(buf.data());

        auto time_spec_future = _usrp_mgr->usrp_future_time(1); // 100ms from now

        int test_samples = 1000;

        _usrp_mgr->issue_stream_cmd(test_samples + offset_rx_samples, time_spec_future);
        int recieved = _usrp_mgr->receive_samples(rx_buffer_ptrs, test_samples, offset_rx_samples);
        if (recieved < test_samples)
            std::cout << "[FMCWRdar:calibrate_rx_phase] Error only received: " << recieved << " of " << test_samples << std::endl;

        // determin phase correction
        for (size_t ch = 1; ch < num_channels; ++ch) {
            std::complex<float> sum = 0.0f;

            for (size_t i = 0; i < test_samples; ++i) {
                auto ref = std::complex<float>(flat_rx_frame_buffer[0][i].real(), flat_rx_frame_buffer[0][i].imag());
                auto cur = std::complex<float>(flat_rx_frame_buffer[ch][i].real(), flat_rx_frame_buffer[ch][i].imag());
                sum += cur * std::conj(ref);
            }

            phase_offsets[ch] = std::arg(sum); // in radians

            std::cout << "[DEBUG] [FMCWRdar:calibrate_rx_phase] calculated phase offset channel: " << ch << " is (deg): " << (phase_offsets[ch] * 180.0 / PI) << std::endl;
        }

        // // for testing...
        // time_spec_future = _usrp_mgr->usrp_future_time(1); // 100ms from now
        // _usrp_mgr->issue_stream_cmd(test_samples + offset_rx_samples, time_spec_future);
        // recieved = _usrp_mgr->receive_samples(rx_buffer_ptrs, test_samples, offset_rx_samples);
        // // try applying phase fix...
        // apply_phase_correction(flat_rx_frame_buffer, phase_offsets);
    }

    void calibrate_rx_sample_offset() {
        // tell user to hookup cabels, wait for user OK
        std::cout << "[FMCWRdar:calibrate_rx_sample_offset] Plase connect loopback cabels between each TX/RX pair" << std::endl;
        std::cout << "Press any key to continue..." << std::endl;
        std::cin.get(); // wait for user response
        
        
        std::cout << "[FMCWRdar:calibrate_rx_sample_offset] Starting calibration of " << num_channels << " RX channels.." << std::endl;

        // transmit frame...
        std::vector<int16_t> I_vec(I_chirp, I_chirp + tx_chirp_samples_length);
        std::vector<int16_t> Q_vec(Q_chirp, Q_chirp + tx_chirp_samples_length);
        
        // steer beam and write to buffer
        int beamAngle = 0; // calibrate using zero shift
        int status = _beam_steer->applyBeamformingAngle(beamAngle, I_vec, Q_vec, beamBuffer);
        if (status != 0)
            std::cerr << "Error while steering beam!" << std::endl;

        // transmit frame using single steered chirp from buffer
        startFrame(beamBuffer, flat_rx_frame_buffer);

        // get offset
        int window_size = ceil(chirp_repetition * rx_sample_rate * 2); // window
        std::cout << "DEBUG] [FMCWRdar:calibrate_rx_sample_offset] window_size: " << window_size << std::endl;

        int offset_sum = 0;
        for (int i = 0; i < num_channels; i++) {
            auto begin = flat_rx_frame_buffer[i].begin();
            std::vector<std::complex<int16_t>> rx_window(begin, begin + window_size);
            int offset = compute_sample_offset(rx_window, beamBuffer[i]);
            offset_sum += offset;

            // make offset
            std::cout << "[DEBUG] [FMCWRdar:calibrate_rx_sample_offset] calculated offset channel: " << i << " is (samples): " << offset << std::endl;
        }

        offset_rx_samples = (int)((double)offset_sum / (double)num_channels);

        std::cout << "[FMCWRdar:calibrate_rx_sample_offset] offset rx samples: " << offset_rx_samples << std::endl;
    }

    // Cross-correlation for complex int16_t signals
    int compute_sample_offset(const std::vector<std::complex<int16_t>>& rx_signal, const std::vector<std::complex<int16_t>>& ref_signal) {
        int ref_size = ref_signal.size();
        int rx_size = rx_signal.size();

        if (rx_size < ref_size) {
            throw std::runtime_error("RX signal must be longer than reference signal");
        }

        int corr_size = rx_size - ref_size + 1;
        std::vector<float> correlation(corr_size, 0.0f);

        // Cross-correlate (dot product with conjugate of ref signal)
        for (int i = 0; i < corr_size; ++i) {
            std::complex<float> acc = 0.0f;
            for (int j = 0; j < ref_size; ++j) {
                auto& rx = rx_signal[i + j];
                auto& ref = ref_signal[j];
                acc += std::complex<float>(rx.real(), rx.imag()) * std::conj(std::complex<float>(ref.real(), ref.imag()));
            }
            correlation[i] = std::abs(acc);
        }

        // Find peak correlation
        auto max_iter = std::max_element(correlation.begin(), correlation.end());
        int peak_index = std::distance(correlation.begin(), max_iter);

        return peak_index;  // Sample offset in rx_signal
    }

};