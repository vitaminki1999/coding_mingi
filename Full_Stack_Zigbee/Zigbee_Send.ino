int sensor = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.print("Temp=");
  int sensorValue = analogRead(sensor);
  double temperature = GetTemperature(sensorValue);
  Serial.println(temperature, 2); // Print temperature with 2 decimal places
  delay(1000);
}

double GetTemperature(int value) {
  double Temp;
  Temp = log(10000.0 / (1024.0 / value - 1));
  Temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * Temp * Temp)) * Temp);
  Temp = Temp - 273.15;
  return Temp;
}
