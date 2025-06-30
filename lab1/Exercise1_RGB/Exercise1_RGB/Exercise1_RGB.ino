#include <WiFiNINA.h>


void setup() {

pinMode(LEDR, OUTPUT);
pinMode(LEDG, OUTPUT);
pinMode(LEDB, OUTPUT);

}
void loop() {
  //Loop to turn the LEDs on
  digitalWrite(LEDR, HIGH); //RED ON
  delay(500);
  digitalWrite(LEDR, LOW); //RED ON

  digitalWrite(LEDG, HIGH); //GREEN ON
  delay(500);
  digitalWrite(LEDG, LOW); //GREEN OFF

  digitalWrite(LEDB, HIGH); //BLUE ON
  delay(500);
  digitalWrite(LEDB, LOW); //BLUE OFF

}
