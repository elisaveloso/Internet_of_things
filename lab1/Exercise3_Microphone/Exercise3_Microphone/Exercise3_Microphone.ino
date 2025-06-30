#include <PDM.h>

#include <PDM.h>

#define BUFFER_SIZE 256
short sampleBuffer[BUFFER_SIZE];
volatile int samplesRead = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial);  // Wait for Serial Monitor

  if (!PDM.begin(1, 16000)) {  // Mono channel, 16kHz sample rate
    Serial.println("Failed to initialize PDM microphone!");
    while (1);
  }

  // Set the receive callback
  PDM.onReceive(onPDMdata);

  Serial.println("Microphone initialized. Speak near the board!");
}

void loop() {
  if (samplesRead) {
    // Print audio samples to Serial Plotter
    for (int i = 0; i < samplesRead; i++) {
      Serial.println(sampleBuffer[i]);
    }
    samplesRead = 0; // Reset sample count
  }
}

// Callback function when PDM data is available
void onPDMdata() {
  samplesRead = PDM.read(sampleBuffer, BUFFER_SIZE);
}