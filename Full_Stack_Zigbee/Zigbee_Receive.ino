#include <Arduino.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    float temperature;
    if (Serial.read() == 'T') {
      while (Serial.available() < 5); // Wait for the full temperature string
      temperature = Serial.parseFloat(); // Read the float value from the serial
      Serial.print("Received temperature: ");
      Serial.println(temperature, 2); // Print temperature with 2 decimal places
    }
  }
}
