#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/stream.hpp>
#include <iostream>
#include <thread>
#include <vector>
#include <complex>
#include <chrono>

class USRPManager {
public:
    USRPManager(const std::string& device_addr)
        : device_addr_(device_addr), num_channels_(4)
    {}

    void setup_usrp() {
        usrp_ = uhd::usrp::multi_usrp::make(device_addr_);
        usrp_->set_time_now(uhd::time_spec_t(0.0));

        uhd::usrp::subdev_spec_t spec("A:0 A:1 B:0 B:1");
        usrp_->set_rx_subdev_spec(spec, uhd::usrp::multi_usrp::ALL_MBOARDS);
        usrp_->set_tx_subdev_spec(spec, uhd::usrp::multi_usrp::ALL_MBOARDS);

        channel_nums_ = {0, 1, 2, 3};

        std::cout << "[setup_usrp] USRP device created and basic configuration done.\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    void setup_rx(double sample_rate, double center_freq, double rx_gain = 10.0) {
        if (!usrp_) {
            throw std::runtime_error("USRP not initialized. Call setup_usrp() first.");
        }

        usrp_->set_rx_rate(sample_rate);
        for (size_t ch = 0; ch < num_channels_; ch++) {
            usrp_->set_rx_freq(uhd::tune_request_t(center_freq), ch);
            usrp_->set_rx_gain(rx_gain, ch);
            usrp_->set_rx_antenna("RX2", ch);
        }

        uhd::stream_args_t rx_stream_args("fc32");
        rx_stream_args.channels = channel_nums_;
        rx_stream_ = usrp_->get_rx_stream(rx_stream_args);

        std::cout << "[setup_rx] RX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";
    }

    void setup_tx(double sample_rate, double center_freq, double tx_gain = 0.0) {
        if (!usrp_) {
            throw std::runtime_error("USRP not initialized. Call setup_usrp() first.");
        }

        usrp_->set_tx_rate(sample_rate);
        for (size_t ch = 0; ch < num_channels_; ch++) {
            usrp_->set_tx_freq(uhd::tune_request_t(center_freq), ch);
            usrp_->set_tx_gain(tx_gain, ch);
            usrp_->set_tx_antenna("TX/RX", ch);
        }

        uhd::stream_args_t tx_stream_args("fc32");
        tx_stream_args.channels = channel_nums_;
        tx_stream_ = usrp_->get_tx_stream(tx_stream_args);

        std::cout << "[setup_tx] TX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";
    }

    size_t receive_samples(const uhd::rx_streamer::buffs_type &buffs, size_t num_samps) {
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
        stream_cmd.num_samps = num_samps;
        stream_cmd.stream_now = false;
        stream_cmd.time_spec = usrp_->get_time_now() + uhd::time_spec_t(0.1);
        rx_stream_->issue_stream_cmd(stream_cmd);

        uhd::rx_metadata_t md;
        size_t samples_received = rx_stream_->recv(buffs, num_samps, md, 3.0);

        if (md.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE) {
            std::cerr << "Receive error: " << md.strerror() << std::endl;
            return 0;
        }

        return samples_received;
    }

    size_t transmit_samples(void* buffer_ptrs[], size_t num_samps) {
        if (!tx_stream_) {
            std::cerr << "TX stream not initialized!\n";
            return 0;
        }

        uhd::tx_metadata_t md;
        md.start_of_burst = true;
        md.end_of_burst = true;
        md.has_time_spec = false; // Immediate send

        size_t samples_sent = tx_stream_->send(buffer_ptrs, num_samps, md);

        if (samples_sent != num_samps) {
            std::cerr << "Warning: Only sent " << samples_sent << " out of " << num_samps << " samples.\n";
        }

        return samples_sent;
    }

    size_t num_channels() const { return num_channels_; }

// private:
public:
    std::string device_addr_;
    uhd::usrp::multi_usrp::sptr usrp_;
    uhd::rx_streamer::sptr rx_stream_;
    uhd::tx_streamer::sptr tx_stream_;
    std::vector<size_t> channel_nums_;
    size_t num_channels_;
};


#include <fstream>

void save_rx_buffers_to_csv(const std::vector<std::vector<std::complex<float>>>& rx_buffers, const std::string& filename) {
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
    // for (size_t ch = 0; ch < num_channels; ++ch) {
    //     outfile << "ch" << ch << "_real,ch" << ch << "_imag";
    //     if (ch != num_channels - 1) {
    //         outfile << ",";
    //     }
    // }
    // outfile << "\n";

    // // Write data
    // for (size_t samp = 0; samp < num_samples; ++samp) {
    //     for (size_t ch = 0; ch < num_channels; ++ch) {
    //         const std::complex<float>& sample = rx_buffers[ch][samp];
    //         outfile << sample.real() << "," << sample.imag();
    //         if (ch != num_channels - 1) {
    //             outfile << ",";
    //         }
    //     }
    //     outfile << "\n";
    // }

    for (size_t samp = 0; samp < num_samples; ++samp) {
        // Get reference sample (channel 0)
        const std::complex<float>& ref_sample = rx_buffers[0][samp];
        float ref_phase = std::arg(ref_sample); // phase in radians

        for (size_t ch = 0; ch < num_channels; ++ch) {
            const std::complex<float>& sample = rx_buffers[ch][samp];
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



int main() {
    try {
        USRPManager usrp_mgr("addr=192.168.1.2");

        double sample_rate = 2e6;
        double center_freq = 5.8e9;

        // Step 1: General device setup
        usrp_mgr.setup_usrp();

        // Step 2: Specific RX / TX setup
        usrp_mgr.setup_rx(sample_rate, center_freq, 10.0);
        // usrp_mgr.setup_tx(sample_rate, center_freq, 0.0); // Low TX gain for safety

        size_t num_channels = usrp_mgr.num_channels();
        size_t num_samps = 2048;

        std::vector<std::vector<std::complex<float>>> rx_buffers(num_channels, std::vector<std::complex<float>>(num_samps));
        std::vector<void*> rx_buffer_ptrs;
        for (auto& buf : rx_buffers) rx_buffer_ptrs.push_back(buf.data());
        
        size_t samples_received = usrp_mgr.receive_samples(rx_buffer_ptrs, num_samps);
        if (samples_received > 0) {
            std::cout << "Successfully received " << samples_received << " samples on " << num_channels << " channels.\n";
            // std::cout << "Successfully received " << samples_received << " samples.\n";
            save_rx_buffers_to_csv(rx_buffers, "rx_data.csv");
        }

        // Optional TX
        // size_t samples_sent = usrp_mgr.transmit_samples(rx_buffer_ptrs.data(), num_samps);
        // if (samples_sent > 0) {
        //     std::cout << "Successfully transmitted " << samples_sent << " samples on " << num_channels << " channels.\n";
        // }

    } catch (const uhd::exception& e) {
        std::cerr << "UHD Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    } catch (const std::runtime_error& e) {
        std::cerr << "Runtime Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}