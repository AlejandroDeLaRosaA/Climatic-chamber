/* includes */
#include <WiFi.h>
#include <time.h>
#include <DHT.h>
#include <DHT_U.h>

/* === Relays === */
#define RELAY1_PIN 33
#define RELAY2_PIN 26
#define RELAY3_PIN 27
#define RELAY4_PIN 13

/* === Ground Humidity Sensors === */
#define HUM_SENSOR1_PIN 36
#define HUM_SENSOR2_PIN 39
#define HUM_SENSOR3_PIN 34
#define HUM_SENSOR4_PIN 35

/* === ADC === */
#define ADC_PIN 32
uint16_t sensorValue = 0;
float voltage = 0.0;

/* === DAC out === */
#define DAC_PIN 25
float dacValue = 0.0;

/* === DHT11 === */
DHT dht1(21, DHT11);   // GPIO21
DHT dht2(19, DHT11);   // GPIO19
DHT dht3(17, DHT11);   // GPIO17
DHT dht4(16, DHT11);   // GPIO16

/* variables para almacenar datos de DHT11 */
float temp1, temp2, temp3, temp4;
float tempAvg;

/* humedad en tierra */
uint16_t gndHum1, gndHum2, gndHum3, gndHum4;
uint16_t gndHumAvg;
float gndHumAvg_percent;
int16_t gndHum1_mapped; 

/* Control del tiempo para ejecucion no bloqueante */
unsigned long currentTime  = 0;
unsigned long lastDHTReadTime = 0;
unsigned long lastADCReadTime = 0;
unsigned long lastHUMReadTime = 0;
unsigned long lastTimeUpdate = 0;

/* Intervalos de lectura */
const unsigned long ADC_INTERVAL = 1000;  // 1s
const unsigned long DHT_INTERVAL = 2000;  
const unsigned long HUM_INTERVAL = 2000;  
const unsigned long TIME_UPDATE_INTERVAL = 60000; // 1 minuto

/* Control de riego no bloqueante relay 3 */
bool irrigationIsActive = false;
unsigned long irrigationStartTime = 0;
const uint16_t IRRIGATION_DURATION = 7000;

/* config WiFi y NTP */ //"INFINITUM6667_2.4"; //"Py8gEB84up";
const char* ssid     = "Alumnos";        
const char* password = "30L0x!4Lu$";

/* NTP y GMT */
const long gmtOffset_sec = -6 * 3600;   // UTC-6 (CDMX, GDL)
const int daylightOffset_sec = 0;
const char *ntpServer = "pool.ntp.org";

/* actualizacion de zona horaria */
uint8_t currentHour;
uint8_t currentMinute;
uint8_t currentSecond;

/* Relays setup */
void relaysInit()
{
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(RELAY3_PIN, OUTPUT);
  pinMode(RELAY4_PIN, OUTPUT);

  digitalWrite(RELAY1_PIN, HIGH);
  digitalWrite(RELAY2_PIN, HIGH);
  digitalWrite(RELAY3_PIN, HIGH);
  digitalWrite(RELAY4_PIN, HIGH);
}

/* Main setup ***********************************************************/
void setup() 
{
  Serial.begin(115200);

  /* ADC setup */
  analogReadResolution(12);  // 0-4095

  /* relays setup*/
  relaysInit();

  /* DHT11 setup */
  dht1.begin();
  dht2.begin();
  dht3.begin();
  dht4.begin();

  /* WiFi setup */
  WiFi.begin(ssid, password);
  Serial.print("Conectando...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi conectado");

  /* NTP Setup init y espera a sincronizar hora */
  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org", "time.nist.gov");
  struct tm timeinfo;
  Serial.println("Esperando hora NTP...");
  while (!getLocalTime(&timeinfo))
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nHora sincronizada");
}


/* App entry loop ******************************************/
void loop() 
{
  currentTime = millis();
   /*************************** Actualizacion de hora cada minuto */
  if (currentTime - lastTimeUpdate >= TIME_UPDATE_INTERVAL)
  {
    lastTimeUpdate = currentTime;

    struct tm timeinfo;
    if (getLocalTime(&timeinfo))
    {
      currentHour = timeinfo.tm_hour;
      currentMinute = timeinfo.tm_min;
      currentSecond = timeinfo.tm_sec;

      Serial.printf("Hora actual: %02d:%02d:%02d\n", currentHour, currentMinute, currentSecond);

      /* === Control del RELAY 4 (luz RGB blanca) === */
      /* enciende a las 7am, se apaga a las 8pm */
      if (currentHour >= 7 && currentHour < 20)
      {
        digitalWrite(RELAY4_PIN, LOW);  // Encender (activo LOW)
        Serial.println("Luz encendida (RELAY 4 ON)");
      }
      else
      {
        digitalWrite(RELAY4_PIN, HIGH); // Apagar
        Serial.println("Luz apagada (RELAY 4 OFF)");
      }
    }
    else
    {
      Serial.println("Fallo al actualizar hora");
    }
  }

  /*************************** lectura ADC potenciostato de acuerdo al intervalo establecido */
  if (currentTime - lastADCReadTime >= ADC_INTERVAL) 
  {
    // === Lectura ADC ===
    lastADCReadTime = currentTime;
    sensorValue = analogRead(34);
    voltage = sensorValue * (3.3 / 4095.0);
    Serial.print("ADC -> Valor: ");
    Serial.print(sensorValue);
    Serial.print(" - Voltaje: ");
    Serial.println(voltage, 3);
  }

  /**************************** lectura DHT11 de acuerdo al intervalo establecido */
  if (currentTime - lastDHTReadTime >= DHT_INTERVAL) 
  {
    lastDHTReadTime = currentTime;

    // === Lectura DHT11 === //
    temp1 = dht1.readTemperature(); 
    temp2 = dht2.readTemperature();  
    temp3 = dht3.readTemperature();  
    temp4 = dht4.readTemperature();  

    /* Temperatura promedio DHT11 */
    tempAvg = (temp1 + temp2 + temp3 + temp4) / 4.0;
    Serial.print("Temperatura promedio: "); Serial.print(tempAvg); Serial.println(" °C");

    /* Control ante temperatura */
    if(tempAvg < 20.0)
    {
      digitalWrite(RELAY1_PIN, LOW);
      Serial.println("Relay 1 ON");
    }
    else
    {
      digitalWrite(RELAY1_PIN, HIGH);
      Serial.println("Relay 1 OFF");
    }

    if(tempAvg > 30.0)
    {
      digitalWrite(RELAY2_PIN, LOW);
      Serial.println("Relay 2 ON");
    }
    else
    {
      digitalWrite(RELAY2_PIN, HIGH);
      Serial.println("Relay 2 OFF");
    }
  }

  /**************************** lectura humedad en tierra de acuerdo al intervalo establecido */
  if(currentTime - lastHUMReadTime >= HUM_INTERVAL)
  {
    lastHUMReadTime = currentTime;
    /* === Lectura de humedad en tierra === */
    gndHum1 = analogRead(HUM_SENSOR1_PIN);
    //gndHum2 = analogRead(HUM_SENSOR2_PIN);
    //gndHum3 = analogRead(HUM_SENSOR3_PIN);
    //gndHum4 = analogRead(HUM_SENSOR4_PIN);

    // Mapeo de lecturas a porcentaje en cada sensor
    gndHum1_mapped = map(gndHum1, 0, 4095, 100, 0);
  /*gndHum2_mapped = map(gndHum2, 0, 4095, 100, 0);
    gndHum3_mapped = map(gndHum3, 0, 4095, 100, 0);
    gndHum4_mapped = map(gndHum4, 0, 4095, 100, 0); */

    /* Promedio de humedad en tierra de los 4 sensores mapeados */
    //gndHumAvg = (gndHum1_mapped + gndHum2_mapped + gndHum3_mapped + gndHum4_mapped) / 4;
    //gndHumAvg_percent = (gndHumAvg * 100.0) / 4095.0;
    //Serial.print("Humedad en tierra promedio: "); Serial.print(gndHumAvg_percent, 2); Serial.println(" %");
    // PROVISIONAL
    Serial.print("Humedad sensor 1: ");
    Serial.print(gndHum1_mapped);
    Serial.println("%");
    /* Control ante humedad en tierra, activa riego si humedad global baja */
   /* if(!irrigationIsActive && gndHumAvg_percent < 30.0)
    {
      digitalWrite(RELAY3_PIN, LOW);
      irrigationStartTime = currentTime;
      irrigationIsActive = true;
      Serial.println("RELAY 3 ON");
    }*/
  }
  /* riego finaliza tras 7 segundos */
 /* if(irrigationIsActive && (currentTime - irrigationStartTime >= IRRIGATION_DURATION))
  {
    digitalWrite(RELAY3_PIN, LOW);
    irrigationIsActive = false;
    Serial.println("RELAY 3 OFF");
  }*/
}




