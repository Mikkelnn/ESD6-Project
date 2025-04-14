#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/types/tune_request.hpp>
#include <uhd/utils/thread.hpp>
#include <iostream>
#include <complex>
#include <vector>
#include <thread>
#include <chrono>

int main() {
    uhd::set_thread_priority_safe();

    // Create the USRP device
    auto usrp = uhd::usrp::multi_usrp::make("");

    // Set TX rate
    double rate = 1e6; // 1 MS/s
    usrp->set_tx_rate(rate);

    // Set TX frequency
    double freq = 915e6; // 915 MHz, for example
    usrp->set_tx_freq(freq);

    // Set TX gain
    usrp->set_tx_gain(30);

    // Set TX antenna
    usrp->set_tx_antenna("TX/RX");

    // Set TX stream args
    uhd::stream_args_t stream_args("fc32"); // complex floats
    auto tx_stream = usrp->get_tx_stream(stream_args);

    // Create a CW signal buffer
    std::vector<std::complex<float>> buffer(tx_stream->get_max_num_samps());
    for (auto& sample : buffer) {
        sample = std::complex<float>(1.0, 0.0); // constant signal (CW)
    }

    // Set metadata
    uhd::tx_metadata_t md;
    md.start_of_burst = true;
    md.end_of_burst = false;
    md.has_time_spec = false;

    // Transmit for a while
    std::cout << "Transmitting CW..." << std::endl;
    for (int i = 0; i < 1000; ++i) {
        tx_stream->send(&buffer.front(), buffer.size(), md);
        md.start_of_burst = false;
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // Send end of burst
    md.end_of_burst = true;
    tx_stream->send("", 0, md);

    std::cout << "Transmission complete." << std::endl;
    return 0;
}
