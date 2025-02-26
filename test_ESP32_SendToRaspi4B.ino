void setup() {
  Serial.begin(9600);  // Comunicación por USB
}

void loop() {
  Serial.println("Mensaje desde ESP32 por USB");
  delay(1000);
}
