#include <Wire.h>
#include <Arduino_LSM6DSOX.h>
#include <WiFiNINA.h>

void setup() {
  Serial.begin(115200);  // Inicializa a comunicação serial
  while (!Serial);       // Aguarda a abertura da porta serial (necessário em algumas placas)
  
  if (!IMU.begin()) {
    Serial.println("IMU not found!");
    while (1); // Trava o código se o IMU não for encontrado
  }
  Serial.println("IMU initialized!");
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
}

void loop() {
  int temperature_deg = 0; 

  if (IMU.temperatureAvailable()) {
    IMU.readTemperature(temperature_deg);

    Serial.print("LSM6DSOX Temperature = ");
    Serial.print(temperature_deg);
    Serial.println(" ºC");
    if (temperature_deg <= 25){
      Serial.println("AZUL");
      digitalWrite(LEDB, HIGH); //BLUE ON
      delay(500);
      digitalWrite(LEDB, LOW); //BLUE OFF
    }
    else if (temperature_deg >= 32){
      Serial.println("VERMELHO");
      digitalWrite(LEDR, HIGH); //RED ON
      delay(500);
      digitalWrite(LEDR, LOW); //RED ON
      delay(1000);
    }
    if ((temperature_deg >= 20) && (temperature_deg <= 36)){
      Serial.println("VERDE");
      digitalWrite(LEDG, HIGH); //GREEN ON
      delay(500);
      digitalWrite(LEDG, LOW); //GREEN OFF
    }
  } 
  else { 
    Serial.println("IMU temperature not available");
  }

  delay(500); // Pequeno atraso para evitar sobrecarga na placa
}