#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads; // Instancia del ADC (16 bits)

void setup() {
  Serial.begin(115200);
  Wire.begin(); // SDA=GPIO21, SCL=GPIO22 en ESP32

  if (!ads.begin()) {
    Serial.println("Error: No se detectó el ADS1115");
    while (1);
  }

  // Configurar la ganancia para medir de 0 a 5V
  ads.setGain(GAIN_TWOTHIRDS);

  // Iniciar la primera conversión en el canal A0 (modo single-ended)
  ads.startADCReading(ADS1X15_REG_CONFIG_MUX_SINGLE_0, false);
}

void loop() {
  // Si la conversión no ha terminado, salir del loop (no bloquea)
  if (!ads.conversionComplete()) {
    return;
  }

  // Leer el resultado de la última conversión
  int16_t valorADC = ads.getLastConversionResults();
  float voltaje = valorADC * (5.0 / 32767.0); // Conversión a voltaje

  Serial.print("Canal A0: "); Serial.print(voltaje, 3); Serial.println(" V");

  // Iniciar otra conversión en el mismo canal
  ads.startADCReading(ADS1X15_REG_CONFIG_MUX_SINGLE_0, false);
}
