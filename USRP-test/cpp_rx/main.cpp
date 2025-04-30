#include "usrp_manager.cpp"
#include "debug_helpers.cpp"

int rx_test() {
    USRPManager usrp_mgr("addr=192.168.1.2");

    double sample_rate = 2e6;
    double center_freq = 5.8e9;

    // Step 1: General device setup
    usrp_mgr.setup_usrp();

    // Step 2: Specific RX / TX setup
    usrp_mgr.setup_rx(sample_rate, center_freq, 10.0);

    size_t num_channels = usrp_mgr.num_channels();
    size_t num_samps = 2048;

    std::vector<std::vector<std::complex<float>>> rx_buffers(num_channels, std::vector<std::complex<float>>(num_samps));
    std::vector<void*> rx_buffer_ptrs;
    for (auto& buf : rx_buffers) rx_buffer_ptrs.push_back(buf.data());
    
    size_t samples_received = usrp_mgr.receive_samples(rx_buffer_ptrs, num_samps);
    if (samples_received > 0) {
        std::cout << "Successfully received " << samples_received << " samples on " << num_channels << " channels.\n";
        // save_rx_buffers_to_csv_phase_diff(rx_buffers, "rx_data.csv");
    }

    return 0;
}

int tx_test() {
    USRPManager usrp_mgr("addr=192.168.1.2");

    double sample_rate = 2e6;
    double center_freq = 5.8e9;

    // Step 1: General device setup
    usrp_mgr.setup_usrp();

    // Step 2: Specific RX / TX setup
    usrp_mgr.setup_tx(sample_rate, center_freq, 0.0); // Low TX gain for safety

    size_t num_channels = usrp_mgr.num_channels();
    size_t num_samps = 20480;

    std::vector<std::vector<std::complex<float>>> tx_buffers(num_channels, std::vector<std::complex<float>>(num_samps, std::complex<float>(1.0f, 0.0f)));
    std::vector<void*> tx_buffer_ptrs;
    for (auto& buf : tx_buffers) tx_buffer_ptrs.push_back(buf.data());

    // Optional TX
    // size_t samples_sent = usrp_mgr.transmit_samples(tx_buffer_ptrs, num_samps);
    size_t samples_sent = usrp_mgr.transmit_carrier_continuous(tx_buffer_ptrs, num_samps, 20.0); // Tx for 20 seconds

    if (samples_sent > 0) {
        std::cout << "Successfully transmitted " << samples_sent << " samples on " << num_channels << " channels.\n";
    }

    return 0;
}

int main() {
    try {
        
        // rx_test();
        // tx_test();        

    } catch (const uhd::exception& e) {
        std::cerr << "UHD Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    } catch (const std::runtime_error& e) {
        std::cerr << "Runtime Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}