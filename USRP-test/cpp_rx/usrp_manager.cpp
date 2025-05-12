#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/stream.hpp>
#include <iostream>
#include <thread>
#include <vector>
#include <complex>
#include <chrono>

class IUSRPManager {
    public:    
        virtual ~IUSRPManager() = default;

        virtual uhd::time_spec_t usrp_future_time(double from_mow_seconds) = 0;
    
        virtual void setup_usrp() = 0;
    
        virtual void setup_rx(double sample_rate, double center_freq, double rx_gain = 10.0) = 0;
    
        virtual void setup_tx(double sample_rate, double center_freq, double tx_gain = 0.0) = 0;
    

        virtual void issue_stream_cmd(size_t num_samps, uhd::time_spec_t time_spec) = 0;

        virtual size_t receive_samples(const std::vector<void*> &buffs, size_t num_samps, size_t skip_samples = 0) = 0;
    
        virtual size_t transmit_samples(const std::vector<void*> &buffs, size_t num_samps, uhd::time_spec_t time_spec) = 0;
    
        virtual size_t num_channels() = 0;
};


class USRPManager_Mock : public IUSRPManager {
    private:
        std::vector<std::vector<std::complex<int16_t>>> internalBuffer;
        double rx_sample_rate = 0, tx_sample_rate = 0;

    public:
        virtual uhd::time_spec_t usrp_future_time(double from_mow_seconds) override {
            return uhd::time_spec_t(from_mow_seconds);
        }

        virtual void setup_usrp() override {
            std::cout << "[USRPManager_Mock] setup_usrp called...." << std::endl;
        }
    
        virtual void setup_rx(double sample_rate, double center_freq, double rx_gain = 10.0) override {
            rx_sample_rate = sample_rate;

            std::cout << "[USRPManager_Mock] setup_rx called.... params: sample_rate: " << sample_rate << " center_freq:" << center_freq << " rx_gain:" << rx_gain  << std::endl;
        }
    
        virtual void setup_tx(double sample_rate, double center_freq, double tx_gain = 0.0) override {
            tx_sample_rate = sample_rate;

            std::cout << "[USRPManager_Mock] setup_tx called.... params: sample_rate: " << sample_rate << " center_freq:" << center_freq << " tx_gain:" << tx_gain  << std::endl;
        }
    
        virtual void issue_stream_cmd(size_t num_samps, uhd::time_spec_t time_spec) {
            std::cout << "[USRPManager_Mock] issue_stream_cmd called.." << std::endl;
        }

        virtual size_t receive_samples(const std::vector<void*> &buffs, size_t num_samps, size_t skip_samples = 0) override {
            // Ensure internalBuffer has enough sub-vectors
            if (buffs.size() > internalBuffer.size()) {
                internalBuffer.resize(buffs.size());
            }

            // calculate downconversion to simulate actual resampling of baseband signal
            int DDC = 1;
            if (rx_sample_rate != 0 && rx_sample_rate < tx_sample_rate)
                DDC = tx_sample_rate / rx_sample_rate;

            for (size_t i = 0; i < buffs.size(); ++i) {
                // Make sure the internal buffer has enough samples
                if (internalBuffer[i].size() < num_samps)
                    num_samps = internalBuffer[i].size();

                // Cast the void* pointer to a writable sample buffer
                std::complex<int16_t>* out = static_cast<std::complex<int16_t>*>(buffs[i]);
                
                if (DDC != 1) {
                    // write down sampled signal into out
                    // set num_samps to actual "read" samples - the internal buffer might be empty before desired number is reached

                    // Check if downsampled_samples is smaller than the size of internalBuffer[i]
                    size_t downsampled_samples = std::min(num_samps, internalBuffer[i].size() / DDC);

                    // Downsample by picking every DDC-th sample from internalBuffer
                    for (size_t j = 0; j < downsampled_samples; ++j) {
                        out[j] = internalBuffer[i][j * DDC]; // Take every DDC-th sample
                    }

                    // Update num_samps to the downsampled sample count
                    num_samps = downsampled_samples;
                }
                else {
                    // Copy from internal buffer to output buffer
                    std::copy_n(internalBuffer[i].begin(), num_samps, out);
                }

            }
        
            return num_samps;
        }
    
        virtual size_t transmit_samples(const std::vector<void*> &buffs, size_t num_samps, uhd::time_spec_t time_spec) override {          
            // Ensure internalBuffer has enough sub-vectors
            if (buffs.size() > internalBuffer.size()) {
                internalBuffer.resize(buffs.size());
            }
  
            for (int i = 0; i < buffs.size(); i++) {
                // Cast the void* pointer to the correct type
                std::complex<int16_t>* samples = static_cast<std::complex<int16_t>*>(buffs[i]);

                // Insert the actual sample data into the internal buffer
                internalBuffer[i].insert(internalBuffer[i].begin(), samples, samples + num_samps);
            }

            return num_samps;
        }
    
        virtual size_t num_channels() override { return 1; }
};



class USRPManager : public IUSRPManager {
public:
    USRPManager(const std::string& base_device_addr, const unsigned int num_channels, size_t tx_burst_samples = -1, size_t rx_burst_samples = -1)
        : num_channels_(num_channels),
          tx_burst_samples_(tx_burst_samples),
          rx_burst_samples_(rx_burst_samples) {

        // Calculate buffer sizes (4 bytes per complex int16 sample)
        // Safety margin factor (e.g., 20% more)
        const float safety_margin = 1.2f;

        // Calculate buffer sizes (4 bytes per complex int16 sample)        
        const size_t tx_buffer_bytes = static_cast<size_t>(tx_burst_samples_ * num_channels_ * 4 * safety_margin);
        const size_t rx_buffer_bytes = static_cast<size_t>(rx_burst_samples_ * num_channels_ * 4 * safety_margin);

        std::stringstream ss;
        ss << base_device_addr;
        if (tx_buffer_bytes > 0)
            ss << ",recv_buff_size=" << std::max((int)rx_buffer_bytes, 816000);
        
        if (tx_buffer_bytes > 0)
            ss << ",send_buff_size=" << std::max((int)tx_buffer_bytes, 307200);

        device_addr_ = ss.str();
    }

    virtual void setup_usrp() override {
        usrp_ = uhd::usrp::multi_usrp::make(device_addr_);
        
        std::cout << "[USRPManager] usrp made with args: " << device_addr_ << std::endl;

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

    virtual uhd::time_spec_t usrp_future_time(double from_mow_seconds) override {
        return usrp_->get_time_now() + from_mow_seconds;
    }

    virtual void setup_rx(double sample_rate, double center_freq, double rx_gain = 10.0) override {
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
        // rx_stream_args.args["spp"] = "4096"; // std::to_string(rx_burst_samples_);

        rx_stream_ = usrp_->get_rx_stream(rx_stream_args);

        std::cout << "[setup_rx] RX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";

    }

    virtual void setup_tx(double sample_rate, double center_freq, double tx_gain = 0.0) override {
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

        // Clear command time for subsequent API calls
        usrp_->clear_command_time();
        
        uhd::stream_args_t tx_stream_args(streamType, streamType);
        tx_stream_args.channels = channel_nums_;
        // tx_stream_args.args["spp"] = "4096"; // std::to_string(tx_burst_samples_);

        tx_stream_ = usrp_->get_tx_stream(tx_stream_args);

        std::cout << "[setup_tx] TX configured: rate = " << sample_rate << ", freq = " << center_freq << "\n";
    }

    virtual void issue_stream_cmd(size_t num_samps, uhd::time_spec_t time_spec) override {
        uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
        stream_cmd.num_samps = num_samps;
        stream_cmd.stream_now = false;
        stream_cmd.time_spec = time_spec;
        rx_stream_->issue_stream_cmd(stream_cmd);
    }

    virtual size_t receive_samples(const std::vector<void*> &buffs, size_t num_samps, size_t skip_samples = 0) override {
        // uhd::rx_metadata_t md;
        // size_t samples_received = rx_stream_->recv(buffs, num_samps, md, 15.0);

        const size_t spp = 360;  // samples per packet (tune as needed)
        uhd::rx_metadata_t md;
        size_t samples_received = 0;
        double timeout = 2.0;  // Increase for large bursts

        while (samples_received < num_samps) {
            size_t samps_to_recv = std::min(spp, num_samps - samples_received);

            std::vector<void*> chunk_ptrs;
            for (size_t ch = 0; ch < buffs.size(); ch++) {
                chunk_ptrs.push_back(
                    static_cast<void*>(static_cast<std::complex<int16_t>*>(buffs[ch]) + samples_received)
                );
            }

            // skip fris N sampls
            if (samples_received == 0 && skip_samples > 0) {
                size_t skipped = rx_stream_->recv(chunk_ptrs, skip_samples, md, timeout);
                skip_samples -= skipped;
                continue;
            }


            size_t rx_count = rx_stream_->recv(chunk_ptrs, samps_to_recv, md, timeout);

            if (md.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE) {
                std::cerr << "Receive error: " << md.strerror() << std::endl;
                break;
            }

            if (rx_count == 0) {
                std::cerr << "Timeout or zero samples received.\n";
                break;
            }

            samples_received += rx_count;
        }


        if (samples_received != num_samps) {
            std::cerr << "Warning: Only received " << samples_received << " of " << num_samps << " samples.\n";
        }

        return samples_received;
    }

    virtual size_t transmit_samples(const std::vector<void*> &buffs, size_t num_samps, uhd::time_spec_t time_spec) override {
        if (!tx_stream_) {
            std::cerr << "TX stream not initialized!\n";
            return 0;
        }

        uhd::tx_metadata_t md;
        md.start_of_burst = true;
        md.end_of_burst = true;
        md.has_time_spec = true;
        md.time_spec = time_spec;
        
        size_t samples_sent = tx_stream_->send(buffs, num_samps, md);
        
        // const size_t max_tx_samps_per_call = 32000;
        // double timeout = 0.1;  // Slightly more forgiving
        // size_t samples_sent = 0;
        // bool first = true;

        // while (samples_sent < num_samps) {
        //     size_t to_send = std::min(max_tx_samps_per_call, num_samps - samples_sent);

        //     uhd::tx_metadata_t md;
        //     md.start_of_burst = first;
        //     md.end_of_burst = (samples_sent + to_send >= num_samps);
        //     md.has_time_spec = first;
        //     if (first) {
        //         md.time_spec = time_spec;
        //         first = false;
        //     }

        //     std::vector<const void*> chunk_ptrs;
        //     for (size_t ch = 0; ch < buffs.size(); ++ch) {
        //         const auto* base = static_cast<const std::complex<int16_t>*>(buffs[ch]);
        //         chunk_ptrs.push_back(base + samples_sent);  // <-- Correct offset!
        //     }

        //     size_t sent = tx_stream_->send(chunk_ptrs.data(), to_send, md, timeout);
        //     samples_sent += sent;
        // }

        if (samples_sent != num_samps) {
            std::cerr << "Warning: Only sent " << samples_sent << " out of " << num_samps << " samples.\n";
        }

        return samples_sent;
    }

    size_t transmit_carrier_continuous(const std::vector<void*> &buffs, size_t num_samps, double duration_seconds) {
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


    virtual size_t num_channels() override { return num_channels_; }

private:
    std::string device_addr_;
    // std::string full_device_addr_;
    size_t num_channels_;
    size_t tx_burst_samples_;
    size_t rx_burst_samples_;
    uhd::usrp::multi_usrp::sptr usrp_;
    uhd::rx_streamer::sptr rx_stream_;
    uhd::tx_streamer::sptr tx_stream_;
    std::vector<size_t> channel_nums_;
    std::string streamType = "sc16"; // "fc32" "sc16"; // complex<int16_t>
};
