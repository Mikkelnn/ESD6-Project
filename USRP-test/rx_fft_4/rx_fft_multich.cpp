#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/types/tune_request.hpp>
#include <uhd/exception.hpp>
#include <uhd/utils/thread.hpp>

#include <iostream>
#include <complex>
#include <vector>
#include <thread>
#include <cmath>

// #include "matplotlibcpp.h"
// namespace plt = matplotlibcpp;

// void plot_fft(const std::vector<std::complex<float>>& data, double sample_rate, int chan) {
//     size_t N = data.size();
//     std::vector<double> freqs(N), magnitudes(N);

//     for (size_t i = 0; i < N; ++i) {
//         double real = data[i].real();
//         double imag = data[i].imag();
//         magnitudes[i] = 10 * log10(real * real + imag * imag + 1e-12);
//         freqs[i] = (static_cast<double>(i) / N - 0.5) * sample_rate / 1e6; // in MHz
//     }

//     plt::figure(chan + 1);
//     plt::clf();
//     plt::plot(freqs, magnitudes);
//     plt::xlabel("Frequency (MHz)");
//     plt::ylabel("Magnitude (dB)");
//     plt::title("Channel " + std::to_string(chan));
//     plt::grid(true);
//     plt::pause(0.01);  // brief pause to update plot
// }

int main() {
    try {
        std::string device_addr("addr=192.168.1.2");
        auto usrp = uhd::usrp::multi_usrp::make(device_addr);
        usrp->set_time_now(uhd::time_spec_t(0.0));

        // Set sample rate and frequency
        double rate = 20.48e6;
        double freq = 5.8e9;
        double rx_gain = 10; // gain in dB

        // size_t num_channels = 4;
        // std::vector<size_t> channel_nums = {0, 1, 2, 3};
        size_t num_channels = 2;
        std::vector<size_t> channel_nums = {0, 1};

        usrp->set_rx_rate(rate);
        for (size_t ch = 0; ch < num_channels; ch++) {
            usrp->set_rx_freq(uhd::tune_request_t(freq), ch);
            usrp->set_rx_gain(rx_gain, ch);
            usrp->set_rx_antenna("RX2", ch);
        }

        // Wait for things to settle
        std::this_thread::sleep_for(std::chrono::seconds(1));

        // Set up streamer
        uhd::stream_args_t stream_args("fc32");  // 32-bit float complex
        stream_args.channels = channel_nums;
        auto rx_stream = usrp->get_rx_stream(stream_args);

        size_t num_samps = 2048;
        std::vector<std::vector<std::complex<float>>> buffs(num_channels, std::vector<std::complex<float>>(num_samps));
        std::vector<void*> buff_ptrs;
        for (auto& buff : buffs) buff_ptrs.push_back(buff.data());

        // Issue stream command BEFORE calling recv
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
        stream_cmd.num_samps = num_samps;
        stream_cmd.stream_mode = uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE;
        stream_cmd.time_spec = usrp->get_time_now() + uhd::time_spec_t(0.1); // 100ms in future
        rx_stream->issue_stream_cmd(stream_cmd);


        uhd::rx_metadata_t md;
        size_t samps_received = rx_stream->recv(buff_ptrs, num_samps, md, 3.0);

        if (md.error_code == uhd::rx_metadata_t::ERROR_CODE_NONE) {
            std::cout << "Received " << samps_received << " samples on " << num_channels << " channels.\n";
            for (size_t ch = 0; ch < num_channels; ++ch) {
                // plot_fft(buffs[ch], rate, ch);
            }
            // plt::show(); // Hold the window open
        } else {
            std::cerr << "Receive error: " << md.strerror() << "\n";
        }
    } catch (const uhd::exception& e) {
        std::cerr << "UHD Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
