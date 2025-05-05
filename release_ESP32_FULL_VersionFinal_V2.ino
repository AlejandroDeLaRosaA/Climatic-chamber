/* includes */
#include <WiFi.h>
#include <time.h>
#include <DHT.h>
#include <DHT_U.h>
#include <HTTPClient.h>

/* === Features that need relays === */
#define PELTIER1_HOT_PIN       33
#define PELTIER1_HOT_FANS_PIN  26
#define PELTIER2_HOT_PIN       27
#define PELTIER2_HOT_FANS_PIN  14

#define WATER_PUMP_PIN         13
#define RGB_STRIPE_PIN         23

/* === Relay logic === */
#define ON 0x0
#define OFF 0x1

/* === Ground Humidity Sensors === */
#define HUM_SENSOR1_PIN 36
#define HUM_SENSOR2_PIN 39
#define HUM_SENSOR3_PIN 34
#define HUM_SENSOR4_PIN 35

/* === DHT11 Sensors pins === */
#define DHT11_1_PIN 21
#define DHT11_2_PIN 19
#define DHT11_3_PIN 17
#define DHT11_4_PIN 16

/* === ADC === */
#define ADC_PIN 32
uint16_t sensorValue = 0;
float voltage = 0.0;

/* === DAC out === */
#define DAC_PIN 25
float dacValue = 0.0;

/* === DHT11 === */
DHT dht1(DHT11_1_PIN, DHT11);   
DHT dht2(DHT11_2_PIN, DHT11);   
DHT dht3(DHT11_3_PIN, DHT11);   
DHT dht4(DHT11_4_PIN, DHT11);   

/* DHT11 data acquisition */
float temp1, temp2, temp3, temp4;
float tempAvg;

/* Soil humidity */
uint16_t gndHum1, gndHum2, gndHum3, gndHum4;
uint16_t gndHumAvg;
float gndHumAvg_percent;
int16_t gndHum1_mapped, gndHum2_mapped, gndHum3_mapped, gndHum4_mapped;

/* Time control (non-blocking execution) */
unsigned long currentTime  = 0;

unsigned long lastDHTReadTime = 0;
unsigned long lastADCReadTime = 0;
unsigned long lastHUMReadTime = 0;
unsigned long lastTimeUpdate = 0;

/* Reading intervals */
long DAC_INTERVAL = 0;
const unsigned long DHT_INTERVAL = 2000;  
const unsigned long HUM_INTERVAL = 2000;  
const unsigned long TIME_UPDATE_INTERVAL = 60000; // 1 minute

/* Non-blocking irrigation control */
bool irrigationIsActive = false;
unsigned long irrigationStartTime = 0;
const uint16_t IRRIGATION_DURATION = 7000;

/* WiFi credentials setup */ 
const char* ssid     = "INFINITUM6667_2.4";        
const char* password = "Py8gEB84up";

/* NTP and GMT */
const long gmtOffset_sec = -6 * 3600;   // UTC-6 (CDMX, GDL)
const int daylightOffset_sec = 0;
const char *ntpServer = "pool.ntp.org";

/* GMT Time zone update */
uint8_t currentHour;
uint8_t currentMinute;
uint8_t currentSecond;

/* Scan and Ramp setup for potentiostat */
uint8_t val = 0;
float c = 0;
uint8_t n = 0;
uint16_t pos = 0;
float Potstep = 0.0078;
int vevals[] = {100,20,50,100,200,250,300};
const uint8_t count = 6;
long intervalos[7];

/* status flags to set potentiostat ramp direction */
bool forward = true;
bool scanning = false;

/* This function pre-calculates the intervals needed to
 * perform different scan rates (mV) for the potentiostat ramp 
 * and it setups the initial ramp  
 */
void Setup_potentiostatRamp_NonBlocking(void) 
{
  dacWrite(DAC_PIN, 0);
  /* scan rate intervals precalculation */
  for(pos = 0; pos < count; pos++)
  {
    intervalos[pos] = 10000L / (vevals[pos] * 128L);
  }
  pos = 0;
  n = 0;
  val = 0;
  scanning = true;
  forward = true;
  lastADCReadTime = millis();
  DAC_INTERVAL = intervalos[pos] / 1000;
}

/* This function executes the forward and reverse scan
 * generating the desired ramp in order to test the 
 * potentiostat and behavior on the electrochemical cells  
 */
void Potentiostat_Scan_NonBlocking(void)
{
  if(scanning)
  {
    if(currentTime - lastADCReadTime >= DAC_INTERVAL)
    {
      lastADCReadTime = currentTime;
      dacWrite(DAC_PIN, val);
      c = analogRead(ADC_PIN);
      Serial.print(val);
      Serial.print(" ");
      Serial.print(c);
      Serial.print(" ");
      Serial.print(n);
      Serial.print(" ");
      Serial.print(vevals[pos]);
      Serial.print(" ");
      Serial.println(DAC_INTERVAL);

      /* Update DAC value */
      if(forward)
      {
        val++;
        if(val > 255)
        {
          val = 255;
          forward = false;
        }
      }
      else
      {
        val--;
        if(val < 0)
        {
          val = 0;
          forward = true;
          n++;
          if(n > 1)
          {
            pos++;
            if(pos >= count)
            {
              pos = 0;             /* to repeat scan */
              //scanning = false;  /* to end scan */
            }
            n = 0;
            DAC_INTERVAL = intervalos[pos] / 1000;
          }
        }
      }
    }
  }
}

/*
 * This function configures and initializes all the relay modules
 * needed to control all boolean logic that ESP32 can handle directly 
 * by its GPIOs
 */
void relaysInit(void)
{
  pinMode(PELTIER1_HOT_PIN,       OUTPUT);
  pinMode(PELTIER1_HOT_FANS_PIN,  OUTPUT);
  pinMode(PELTIER2_HOT_PIN,       OUTPUT);
  pinMode(PELTIER2_HOT_FANS_PIN,  OUTPUT);
  pinMode(WATER_PUMP_PIN,         OUTPUT);
  pinMode(RGB_STRIPE_PIN,         OUTPUT);

  digitalWrite(PELTIER1_HOT_PIN,      OFF);
  digitalWrite(PELTIER1_HOT_FANS_PIN, OFF);
  digitalWrite(PELTIER2_HOT_PIN,      OFF);
  digitalWrite(PELTIER2_HOT_FANS_PIN, OFF);
  digitalWrite(WATER_PUMP_PIN,        OFF);
  digitalWrite(RGB_STRIPE_PIN,        OFF);
}



/* Main setup ***********************************************************/
void setup() 
{
  /* Serial init */
  Serial.begin(115200);

  /* ADC setup */
  analogReadResolution(12);  // 0-4095

  /* Potentiostat setup */
  Setup_potentiostatRamp_NonBlocking();

  /* relays setup*/
  relaysInit();

  /* DHT11 setup */
  dht1.begin();
  dht2.begin();
  dht3.begin();
  dht4.begin();

  /* WiFi setup */
  WiFi.begin(ssid, password);
  Serial.print("Connecting...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  /* NTP init and wait till time is synced */
  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org", "time.nist.gov");
  struct tm timeinfo;
  Serial.println("Waiting for NTP server...");
  while (!getLocalTime(&timeinfo))
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTime properly sync");
}


/* App entry loop ******************************************/
void loop() 
{
  /* Aactual execution time acquisition in order toperform non-blocking tasks */
  currentTime = millis();

  /*************************** Potentiostat ADC reading according to set interval */
  /* Concurrent potentiostat ramp execution */
  Potentiostat_Scan_NonBlocking();

  /*************************** Time update each minute */
  if (currentTime - lastTimeUpdate >= TIME_UPDATE_INTERVAL)
  {
    lastTimeUpdate = currentTime;
    struct tm timeinfo;
    if (getLocalTime(&timeinfo))
    {
      currentHour = timeinfo.tm_hour;
      currentMinute = timeinfo.tm_min;
      currentSecond = timeinfo.tm_sec;

      Serial.printf("Actual time: %02d:%02d:%02d\n", currentHour, currentMinute, currentSecond);

      /* === RGB LED Stripe control === */
      /* Turns on at 7am, and goes off at 8pm */
      if (currentHour >= 7 && currentHour < 20)
      {
        
        digitalWrite(RGB_STRIPE_PIN, ON); 
        Serial.println("7am, lights on...");
      }
      else
      {
        digitalWrite(RGB_STRIPE_PIN, OFF);
        Serial.println("8pm, lights off...");
      }
    }
    else
    {
      Serial.println("Time sync failed...");
    }
  }

  /**************************** DHT11 reading according to set interval */
  if (currentTime - lastDHTReadTime >= DHT_INTERVAL) 
  {
    lastDHTReadTime = currentTime;

    /* === DHT11 reading === */
    temp1 = dht1.readTemperature(); 
    temp2 = dht2.readTemperature();  
    temp3 = dht3.readTemperature();  
    temp4 = dht4.readTemperature();  

    /* DHT11 average temperature */
    tempAvg = (temp1 + temp2 + temp3 + temp4) / 4.0;
    Serial.print("Average temperature: "); Serial.print(tempAvg); Serial.println(" °C");

    /* Temperature control logic */
    if(tempAvg < 20.0)
    {
      digitalWrite(PELTIER1_HOT_PIN,      ON);
      digitalWrite(PELTIER1_HOT_FANS_PIN, ON);
      digitalWrite(PELTIER2_HOT_PIN,      ON);
      digitalWrite(PELTIER2_HOT_FANS_PIN, ON);
      Serial.println("Warming peltier cells ON...(FAN ON)");
    }
    else
    {
      digitalWrite(PELTIER1_HOT_PIN,      OFF);
      digitalWrite(PELTIER1_HOT_FANS_PIN, OFF);
      digitalWrite(PELTIER2_HOT_PIN,      OFF);
      digitalWrite(PELTIER2_HOT_FANS_PIN, OFF);
      Serial.println("Warming peltier cells OFF....(FAN OFF)");
    }
  }

  /**************************** Soil humidity reading according to set interval */
  if(currentTime - lastHUMReadTime >= HUM_INTERVAL)
  {
    lastHUMReadTime = currentTime;
    /* === Soil moisture reading === */
    gndHum1 = analogRead(HUM_SENSOR1_PIN);
    gndHum2 = analogRead(HUM_SENSOR2_PIN);

    /* Humidity sensors reading mapped to percentage */
    gndHum1_mapped = map(gndHum1, 0, 4095, 100, 0);
    gndHum2_mapped = map(gndHum2, 0, 4095, 100, 0);

    Serial.print("Humidity sensor 1: ");
    Serial.print(gndHum1_mapped); Serial.println("%");
    Serial.print("Humidity sensor 2: ");
    Serial.print(gndHum2_mapped); Serial.println("%");

    gndHumAvg = (gndHum1_mapped + gndHum2_mapped) / 2;
    Serial.print("Average soil humidity: "); Serial.print(gndHumAvg); Serial.println("%");
    
    /* Irrigation control due to soil humidity */
    if(!irrigationIsActive && gndHumAvg < 30.0)
    {
      digitalWrite(WATER_PUMP_PIN, ON);
      irrigationStartTime = currentTime;
      irrigationIsActive = true;
      Serial.println("Watering dry soil...(7s)");
    }
  }
  /* Irrigation ends past 7 seconds */
  if(irrigationIsActive && (currentTime - irrigationStartTime >= IRRIGATION_DURATION))
  {
    digitalWrite(WATER_PUMP_PIN, OFF);
    irrigationIsActive = false;
    Serial.println("Irrigation completed");
  }
}

