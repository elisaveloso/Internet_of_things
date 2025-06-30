#include <Wire.h>
#include <Arduino_LSM6DSOX.h>
#include <WiFiNINA.h>
#include <MadgwickAHRS.h>

Madgwick filter;


const float IDEAL_PITCH = 90.0;  // Ideal posture
const float BAD_POSTURE_THRESHOLD = 80.0;  // Bad posture if pitch < 80°
const float TEMP_HIGH_THRESHOLD = 30.0;  // Temperature too high if >30°C

void setup() {
  Serial.begin(115200);
  while (!Serial);  // Wait for Serial monitor to open

  // Initialize IMU sensor
  if (!IMU.begin()) {
    Serial.println("IMU not found!");
    while (1);  // Halt execution if sensor is not found
  }
  Serial.println("IMU initialized!");

  // Set RGB LED pins as outputs
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);

  // Initialize Madgwick filter
  filter.begin(100);  // Sampling rate of 100 Hz
}

void loop() {
  float ax, ay, az, gx, gy, gz;
  int temperature = 0;
  
  // Read IMU data
  if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);

    // Update the filter with IMU data
    filter.updateIMU(gx, gy, gz, ax, ay, az);

    // Get pitch angle
    float pitch = filter.getPitch();

    // Read temperature
    if (IMU.temperatureAvailable()) {
      IMU.readTemperature(temperature);
    } else {
      Serial.println("IMU temperature not available");
      return;
    }

    // Display data
    Serial.print("Pitch: ");
    Serial.print(pitch);
    Serial.print("° | Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");

    // Check conditions and control LED alarm
    checkConditions(pitch, temperature);
  }

  delay(500);
}

void checkConditions(float pitch, int temperature) {

  if (pitch < BAD_POSTURE_THRESHOLD) {
    digitalWrite(LEDR, HIGH); 
    Serial.println("⚠ Bad posture detected! Fix your back.");
    digitalWrite(LEDR, LOW);  // Red LED ON
  } else if (temperature > TEMP_HIGH_THRESHOLD) {
    digitalWrite(LEDB, HIGH); 
    Serial.println("⚠ High temperature! Consider cooling down.");
    digitalWrite(LEDB, LOW);  // Blue LED ON
  } else {
    digitalWrite(LEDG, HIGH); 
    Serial.println("✅ Good posture and temperature.");
    digitalWrite(LEDG, LOW);  // Green LED ON
  }
}