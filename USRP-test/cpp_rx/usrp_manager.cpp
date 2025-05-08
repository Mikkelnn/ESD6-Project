#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/stream.hpp>
#include <iostream>
#include <thread>
#include <vector>
#include <complex>
#include <chrono>

class USRPManager {
public:
    USRPManager(const std::string& device_addr, const unsigned int num_channels)
        : device_addr_(device_addr), num_channels_(num_channels)
    {}

    auto usrp_future_time(double from_mow_seconds) {
        return usrp_->get_time_now() + from_mow_seconds;
    }

    void setup_usrp() {
        usrp_ = uhd::usrp::multi_usrp::make(device_addr_);
        
        // Set clock source to external 10 MHz
        usrp_->set_clock_source("external");

        // Sleep to allow locking
        std::this_thread::sleep_for(std::chrono::seconds(1));

        // Optional: Check if clock is locked
        if (usrp_->get_mboard_sensor("ref_locked").to_bool()) {
            std::cout << "External 10 MHz clock locked." << std::endl;
        } else {
            std::cerr << "WARNING: 10 MHz reference not locked!" << std::endl;
        }

        uhd::usrp::subdev_spec_t spec("A:0 A:1 B:0 B:1");
        usrp_->set_rx_subdev_spec(spec, uhd::usrp::multi_usrp::ALL_MBOARDS);
        usrp_->set_tx_subdev_spec(spec, uhd::usrp::multi_usrp::ALL_MBOARDS);
        
         // Sync hardware time
        usrp_->set_time_now(uhd::time_spec_t(0.0));
        
        channel_nums_.resize(num_channels_);
        for (int i = 0; i < num_channels_; i++)
            channel_nums_[i] = i;

        std::cout << "[setup_usrp] USRP device created and basic configuration done.\n";

        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    void setup_rx(double sample_rate, double center_freq, double rx_gain = 10.0) {
        if (!usrp_) {
            throw std::runtime_error("USRP not initialized. Call setup_usrp() first.");
        }

        // Assume that `usrp` is a multi_usrp object
        // 1) Set a command time in the future, e.g. 500ms from now:
        usrp_->set_command_time(usrp_->get_time_now() + .5);

        // 2) Tune to a new frequency on all channels, e.g., 2 GHz:
        usrp_->set_rx_rate(sample_rate, uhd::usrp::multi_usrp::ALL_CHANS);
                
        for (size_t ch = 0; ch < num_channels_; ch++) {
            usrp_->set_rx_freq(uhd::tune_request_t(center_freq), ch);
            usrp_->set_rx_gain(rx_gain, ch);
            usrp_->set_rx_antenna("RX2", ch);
        }

        // usrp_->set_rx_rate(sample_rate, uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_rx_freq(uhd::tune_request_t(center_freq), uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_rx_gain(rx_gain, uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_rx_antenna("RX2", uhd::usrp::multi_usrp::ALL_CHANS);
        
        // 3) Wait until we're past the command time:
        std::this_thread::sleep_for(std::chrono::milliseconds(700));
        // Channel phases are now at a deterministic offset. Repeating this procedure
        // will lead to the same offset.

        // Clear command time for subsequent API calls
        usrp_->clear_command_time();

        uhd::stream_args_t rx_stream_args(streamType, streamType); // maybe fix so ower the wire uses same type... https://uhd.readthedocs.io/en/latest/page_configuration.html
        rx_stream_args.channels = channel_nums_;
        rx_stream_ = usrp_->get_rx_stream(rx_stream_args);

        std::cout << "[setup_rx] RX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";
    }

    void setup_tx(double sample_rate, double center_freq, double tx_gain = 0.0) {
        if (!usrp_) {
            throw std::runtime_error("USRP not initialized. Call setup_usrp() first.");
        }


        // Assume that `usrp` is a multi_usrp object
        // 1) Set a command time in the future, e.g. 500ms from now:
        usrp_->set_command_time(usrp_->get_time_now() + .5);

        // 2) Tune to a new frequency on all channels, e.g., 2 GHz:
        usrp_->set_tx_rate(sample_rate);
        for (size_t ch = 0; ch < num_channels_; ch++) {
            usrp_->set_tx_freq(uhd::tune_request_t(center_freq), ch);
            usrp_->set_tx_gain(tx_gain, ch);
            usrp_->set_tx_antenna("TX/RX", ch);
        }
        // usrp_->set_tx_rate(sample_rate, uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_tx_freq(uhd::tune_request_t(center_freq), uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_tx_gain(tx_gain, uhd::usrp::multi_usrp::ALL_CHANS);
        // usrp_->set_tx_antenna("TX/RX", uhd::usrp::multi_usrp::ALL_CHANS);
        
        // 3) Wait until we're past the command time:
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        // Channel phases are now at a deterministic offset. Repeating this procedure
        // will lead to the same offset.

        
        uhd::stream_args_t tx_stream_args(streamType, streamType);
        tx_stream_args.channels = channel_nums_;
        tx_stream_ = usrp_->get_tx_stream(tx_stream_args);

        std::cout << "[setup_tx] TX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";
    }

    size_t receive_samples(const uhd::rx_streamer::buffs_type &buffs, size_t num_samps, uhd::time_spec_t time_spec) {
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
        stream_cmd.num_samps = num_samps;
        stream_cmd.stream_now = false;
        stream_cmd.time_spec = time_spec;
        rx_stream_->issue_stream_cmd(stream_cmd);

        uhd::rx_metadata_t md;
        size_t samples_received = rx_stream_->recv(buffs, num_samps, md, 3.0);

        if (md.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE) {
            std::cerr << "Receive error: " << md.strerror() << std::endl;
            return 1;
        }

        return samples_received;
    }

    size_t transmit_samples(const uhd::tx_streamer::buffs_type &buffs, size_t num_samps, uhd::time_spec_t time_spec) {
        if (!tx_stream_) {
            std::cerr << "TX stream not initialized!\n";
            return 0;
        }

        uhd::tx_metadata_t md;
        md.start_of_burst = true;
        md.end_of_burst = true;
        md.has_time_spec = true;
        md.time_spec = time_spec;

        // uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
        // stream_cmd.num_samps = num_samps;
        // stream_cmd.stream_now = false;
        // stream_cmd.time_spec = usrp_->get_time_now() + uhd::time_spec_t(0.1);
        // rx_stream_->issue_stream_cmd(stream_cmd);

        size_t samples_sent = tx_stream_->send(buffs, num_samps, md);

        if (samples_sent != num_samps) {
            std::cerr << "Warning: Only sent " << samples_sent << " out of " << num_samps << " samples.\n";
        }

        return samples_sent;
    }

    size_t transmit_carrier_continuous(const uhd::tx_streamer::buffs_type &buffs, size_t num_samps, double duration_seconds) {
        if (!tx_stream_) {
            std::cerr << "TX stream not initialized!\n";
            return 0;
        }

        uhd::tx_metadata_t md;
        md.start_of_burst = true;
        md.has_time_spec = false; // Transmit immediately

        auto start_time = std::chrono::steady_clock::now();
        size_t total_sent = 0;

        while (std::chrono::steady_clock::now() - start_time < std::chrono::duration<double>(duration_seconds)) {
            // Only first packet gets start_of_burst=true
            if (total_sent > 0) md.start_of_burst = false;

            // Middle packets have end_of_burst=false
            md.end_of_burst = false;

            size_t sent = tx_stream_->send(buffs, num_samps, md);
            if (sent != num_samps) {
                std::cerr << "Partial send: " << sent << " samples\n";
            }

            total_sent += sent;
        }

        // Final packet to mark end of burst
        md.end_of_burst = true;
        size_t final = tx_stream_->send(buffs, num_samps, md);
        total_sent += final;

        std::cout << "Total samples sent: " << total_sent << "\n";
        return total_sent;
    }


    size_t num_channels() const { return num_channels_; }

// private:
private:
    std::string device_addr_;
    uhd::usrp::multi_usrp::sptr usrp_;
    uhd::rx_streamer::sptr rx_stream_;
    uhd::tx_streamer::sptr tx_stream_;
    std::vector<size_t> channel_nums_;
    size_t num_channels_;
    std::string streamType = "sc16"; // "fc32" "sc16"; // complex<int16_t>
};