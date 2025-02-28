#include <driver/dac_continuous.h>
#include <esp_heap_caps.h>
#include <math.h>
#include <stdlib.h>

#define SAMPLE_RATE 1000000  // 100 kHz sample rate
#define BUFFER_SIZE 2000 // 2048 4096 8192 10240 // Must be a multiple of the waveform cycle length

dac_continuous_handle_t dac_handle;  // Handle for the DAC driver

// Allocate DMA-capable buffer
uint8_t *dma_buffer;

// Configure DAC for continuous output
void initDAC() {
    dac_continuous_config_t dac_config = {
        .chan_mask = DAC_CHANNEL_MASK_ALL,  // Output on both DACs
        .desc_num = 4,  // Number of DMA buffers
        .buf_size = BUFFER_SIZE * 2,  // Buffer size for both channels
        .freq_hz = SAMPLE_RATE,  // Output frequency
        .offset = 0,  // No DC offset
        .clk_src = DAC_DIGI_CLK_SRC_APLL, // DAC_DIGI_CLK_SRC_DEFAULT,  // Default clock source
        .chan_mode = DAC_CHANNEL_MODE_ALTER
    };

    dac_continuous_new_channels(&dac_config, &dac_handle);
    dac_continuous_enable(dac_handle);  // Enable DAC DMA output

    // Allocate memory in DMA-capable region
    dma_buffer = (uint8_t *)heap_caps_malloc(BUFFER_SIZE * 2, MALLOC_CAP_DMA);
    if (!dma_buffer) {
        Serial.println("Failed to allocate DMA buffer!");
        while (1);  // Halt execution if allocation fails
    }
}


// Generate a fixed-frequency, phase-shifted sine wave
void generateFixedFrequency(float frequency, float phase_deg) {
    float phase_rad = phase_deg * M_PI / 180.0;
    float A_I = cos(phase_rad);
    float A_Q = sin(phase_rad);

    for (int i = 0; i < BUFFER_SIZE; i++) {
        float theta = 2.0 * M_PI * frequency * i / SAMPLE_RATE;

        float I = 127 + 127 * A_I * cos(theta);
        float Q = 127 + 127 * A_Q * sin(theta);

        dma_buffer[2 * i] = (uint8_t)(I);  // Left channel (I)
        dma_buffer[2 * i + 1] = (uint8_t)(Q);  // Right channel (Q)
    }
}

// Generate full I/Q chirp buffer
void generateChirp(float stop_freq, float chirp_time, float phase_deg) {
    float phase_rad = phase_deg * M_PI / 180.0;
    float A_I = cos(phase_rad);
    float A_Q = sin(phase_rad);

    for (int i = 0; i < BUFFER_SIZE; i++) {
        float t = (float)i / (float)BUFFER_SIZE;
        float frequency = stop_freq * t;  // Linear sweep
        float theta = (2.0 * M_PI * frequency * i) / SAMPLE_RATE; //2.0 * M_PI * frequency * t;

        float I = 127 + 127 * A_I * cos(theta);
        float Q = 127 + 127 * A_Q * sin(theta);

        dma_buffer[2 * i] = (uint8_t)(I);  // Left channel (I)
        dma_buffer[2 * i + 1] = (uint8_t)(Q);  // Right channel (Q)
    }
}

void setup() {
    Serial.begin(115200);
    initDAC();
    
    pinMode(5, OUTPUT);
    
    // Start a fixed-frequency IQ signal with a 45-degree phase shift
    generateFixedFrequency(1000, 15);

    // Start a chirp from 1kHz to 10kHz in 1 second with a 45-degree phase shift
    // generateChirp(5000, 0.01, 0);

    //dac_continuous_write(dac_handle, (uint8_t *)dma_buffer, BUFFER_SIZE * 2, NULL, -1);

    dac_continuous_write_cyclically(dac_handle, (uint8_t *)dma_buffer, BUFFER_SIZE * 2, NULL);
}

void loop() {
    // No need for loop; DAC DMA continuously plays the buffer.
    //delay(10);
    //dac_continuous_disable(dac_handle);
    //delay(100);
    //dac_continuous_enable(dac_handle);
    //digitalWrite(5, HIGH);
    
    //dac_continuous_write(dac_handle, (uint8_t *)dma_buffer, BUFFER_SIZE * 2, NULL, -1);
    
    
    //delayMicroseconds(11000);
    //digitalWrite(5, LOW);
}




//#include <math.h>
//
//#define DAC_MAX 255      // 8-bit DAC max value
//#define SAMPLE_RATE 100000  // Sample rate in Hz
//#define DAC_I 25  // GPIO for DAC1
//#define DAC_Q 26  // GPIO for DAC2
//
//// Generate sine wave samples
//void generate_sine_wave(uint8_t* buffer, int sample_count, float amplitude, float phase_shift) {
//    for (int i = 0; i < sample_count; i++) {
//        float theta = (2.0 * M_PI * i) / sample_count + phase_shift;
//        buffer[i] = (uint8_t)(127 + amplitude * 127 * sin(theta));  // Centered at 127
//    }
//}
//
//// Set frequency and phase shift
//void set_frequency_phase_shift(float frequency, float phase_deg) {
//    int sample_count = SAMPLE_RATE / frequency;
//    uint8_t i_buffer[sample_count];
//    uint8_t q_buffer[sample_count];
//
//    // Compute amplitude scaling for I and Q
//    float A_I = cos(phase_deg * M_PI / 180.0);
//    float A_Q = sin(phase_deg * M_PI / 180.0);
//
//    // Generate I and Q waveforms with proper amplitudes
//    generate_sine_wave(i_buffer, sample_count, A_I, 0);
//    generate_sine_wave(q_buffer, sample_count, A_Q, M_PI / 2);  // Q is 90° out of phase
//
//    // Output to DACs
//    while (true) {
//      for (int i = 0; i < sample_count; i++) {
//          dacWrite(DAC_I, i_buffer[i]);
//          dacWrite(DAC_Q, q_buffer[i]);
//          delayMicroseconds(1000000 / SAMPLE_RATE);
//      }  
//    }    
//}
//
//void setup() {
//    // Uncomment the one you want to use:
//    //set_frequency_phase_shift(1000.0, 0.0);  // 1 kHz, 45° phase shift
//}
//
//void loop() {
//  // CPU is free! No need to manage the DAC output.
//  set_frequency_phase_shift(1000.0, 15.0);
//}
