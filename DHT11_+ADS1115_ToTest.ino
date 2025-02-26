#include <Wire.h>      // Librería para comunicación I2C
#include <Adafruit_ADS1X15.h>  // Librería para el ADC ADS1115
#include <DHT.h>
#include <DHT_U.h>

#define NUM_SENSORES 4       
#define DELAY_MS 2000 // Tiempo entre lecturas (ms)

// Estructura para almacenar datos de cada sensor DHT11
struct SensorDHT
{
  DHT sensor;
  uint8_t pin;
  float temperatura;
  float humedad;
};

// Instancias de sensores DHT11
SensorDHT sensores[NUM_SENSORES] = {
  {DHT(17, DHT11), 17, 0, 0},
  {DHT(5, DHT11),  5, 0, 0},
  {DHT(18, DHT11), 18, 0, 0},
  {DHT(19, DHT11), 19, 0, 0}
};

// Instancia del ADC ADS1115
Adafruit_ADS1115 ads;

// Tiempo previo para evitar bloqueos con delay()
unsigned long tiempoPrevio = 0;

void setup() 
{
  Serial.begin(115200);
  Wire.begin(); // Iniciar comunicación I2C (SDA=GPIO21, SCL=GPIO22 en ESP32)

  // Iniciar sensores DHT11
  for (int i = 0; i < NUM_SENSORES; i++) 
  {
    sensores[i].sensor.begin();
  }

  // Iniciar ADS1115
  if (!ads.begin()) 
  {
    Serial.println("Error: No se detectó el ADS1115");
    while (1);
  }
  
  ads.setGain(GAIN_TWOTHIRDS); // Rango de 0V a 5V (para señales de 5V)
}

void loop() 
{
  unsigned long tiempoActual = millis(); // Obtener tiempo actual

  if (tiempoActual - tiempoPrevio >= DELAY_MS) 
  {
    tiempoPrevio = tiempoActual; // Actualizar tiempo previo

    // Leer sensores DHT11
    for (int i = 0; i < NUM_SENSORES; i++) 
    {
      sensores[i].temperatura = sensores[i].sensor.readTemperature();
      sensores[i].humedad = sensores[i].sensor.readHumidity();

      Serial.print("Sensor "); Serial.print(i + 1);
      Serial.print(" -> Temp: "); Serial.print(sensores[i].temperatura);
      Serial.print(" °C  Hum: "); Serial.println(sensores[i].humedad);
    }

    // Leer ADC ADS1115 en el canal 0 (A0)
    int16_t valorADC = ads.readADC_SingleEnded(0);
    float voltaje = valorADC * (5.0 / 32767.0); // Convertir lectura a voltaje (0-5V)

    Serial.print("ADS1115 -> Voltaje: "); Serial.print(voltaje, 3);
    Serial.println(" V");

    Serial.println("---------------------");
  }
}
