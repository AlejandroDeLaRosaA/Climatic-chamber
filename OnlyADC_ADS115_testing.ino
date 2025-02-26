#include <Wire.h>              // Comunicación I2C
#include <Adafruit_ADS1X15.h>  // Librería del ADC ADS1115

Adafruit_ADS1115 ads;  // Instancia del ADC

void setup() {
  Serial.begin(115200);
  Wire.begin(); // SDA=GPIO21, SCL=GPIO22 en ESP32

  // Inicializar el ADS1115
  if (!ads.begin()) {
    Serial.println("Error: No se detectó el ADS1115");
    while (1); // Bucle infinito si falla la detección
  }

  // Configurar ganancia para medir voltajes de 0 a 5V
  ads.setGain(GAIN_TWOTHIRDS);
}

void loop() {
  // Leer los 4 canales del ADC (A0-A3)
  for (int i = 0; i < 4; i++) {
    int16_t valorADC = ads.readADC_SingleEnded(i); 
    float voltaje = valorADC * (5.0 / 32767.0); // Conversión a voltaje

    Serial.print("Canal A"); Serial.print(i);
    Serial.print(": "); Serial.print(voltaje, 3); 
    Serial.println(" V");
  }

  Serial.println("---------------------");
  delay(1000); // Esperar 1 segundo entre lecturas
}
