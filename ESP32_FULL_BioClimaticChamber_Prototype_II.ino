/******************************************************************************* 
 * Project: Bioclimatic Chamber
 * 
 * Description:
 * This program reads temperature and humidity from four DHT11 sensors, 
 * measures voltage using the ADS1115 ADC, and controls six relays 
 * based on temperature and humidity conditions. It also communicates 
 * with a Raspberry Pi via UART, sending sensor data and receiving commands. 
 * Additionally, it generates a 3.1 kHz PWM signal for external control.
 * 
 * Features:
 * - Reads data from 4 DHT11 sensors (Temperature & Humidity)
 * - Interfaces with ADS1115 ADC for voltage measurement
 * - Controls 6 relays automatically or via UART commands
 * - Sends formatted sensor data to Raspberry Pi via UART
 * - Receives and processes commands from the Raspberry Pi
 * - Generates a 3.1 kHz PWM signal for external use
 * 
 * Hardware Connections:
 * - DHT11 Sensors: GPIO 36, 39, 34, 35
 * - Relays: GPIO 14, 27, 26, 25, 33, 32
 * - ADS1115 (I2C): SDA -> GPIO 21, SCL -> GPIO 22
 * - UART (Raspberry Pi): TX -> GPIO 1, RX -> GPIO 3
 * - PWM Output: GPIO 18 (3.1 kHz)
 * 
 * Author:         [Alejandro De La Rosa A.]
 * Date:           [18/03/2025]
 * Institution:    [ITESO, Electronic engineering & CIATEJ Zapopan, Industrial Biotechnology]
 *******************************************************************************/

/************* Includes */
/* Libraries used*/
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <DHT.h>
#include <DHT_U.h>

/************* Auxiliar macros */
#define NUM_SENSORS 4
#define NUM_RELAYS 6
#define DELAY_MS 2000
#define DUTY_CYCLE_50 512

/* PWM Channels on the ESP32 */
#define PWM_CHANNEL0 0
#define PWM_CHANNEL1 1
#define PWM_CHANNEL2 2
#define PWM_CHANNEL3 3 

/* Used pins in the ESP32 WROOM -> 38 pins version */
/* Right-side */
#define GPIO19 19
#define GPIO18 18
#define GPIO5   5
#define GPIO17 17 
#define GPIO16 16

/* Left-side */
#define GPIO36 36 
#define GPIO39 39
#define GPIO34 34
#define GPIO35 35
#define GPIO32 32
#define GPIO33 33
#define GPIO25 25
#define GPIO26 26
#define GPIO27 27
#define GPIO14 14

/************* PWM for potentiostat 
* and RGB LED Stripe colors Config struct */
struct PWM
{
  /* pwm potentiostat */
  uint8_t  pwm_channel;
  uint8_t  pwm_pin;
  uint32_t pwm_freq;
  uint8_t  pwm_res;
  uint32_t pwm_duty;

  /* pwm led rgb */
  uint8_t  red_pin;
  uint8_t  red_channel;
  uint8_t  green_pin;
  uint8_t  green_channel;
  uint8_t  blue_pin;
  uint8_t  blue_channel;
};

/************* Potentiostat instance */
PWM potentiostat = {  
  .pwm_channel = PWM_CHANNEL0,
  .pwm_pin = GPIO19,
  .pwm_freq = 3100,
  .pwm_res = 10,
  .pwm_duty = DUTY_CYCLE_50,
};

/************* LED Stripe colors instance */
PWM ledrgb = {
  .pwm_freq = 1000,
  .pwm_res = 10,
 
  /* pwm led rgb */
  .red_pin = GPIO5,
  .red_channel = PWM_CHANNEL1,
  .green_pin = GPIO17,
  .green_channel = PWM_CHANNEL2,
  .blue_pin = GPIO16,
  .blue_channel = PWM_CHANNEL3
};




/************* DHT11 Sensors config */
struct DHTSensor
{
  DHT sensor;
  uint8_t pin;
  float temperature;
  float humidity;
};

DHTSensor sensors[NUM_SENSORS] = {
  {DHT(GPIO36, DHT11), GPIO36, 0, 0},
  {DHT(GPIO39, DHT11), GPIO39, 0, 0},
  {DHT(GPIO34, DHT11), GPIO34, 0, 0},
  {DHT(GPIO35, DHT11), GPIO35, 0, 0}
};

float avgTemp = 0;
float avgHumidity = 0;

/************* Relay pins */
const uint8_t relays[] = {GPIO14, GPIO27, GPIO26, 
                          GPIO25, GPIO33, GPIO32};

/************* ADS1115 I2C ADC config */
Adafruit_ADS1115 ads;
int16_t adcValue = 0;
float voltage = 0;

/************* Code execution config */
unsigned long currentTime = 0;
unsigned long previousTime = 0;
bool automaticMode = true;


/************* API */

/**
* Starts the generation of the pwm constant signal to be used
* by the potentiostat circuit.
*/
void start_Potentiostat_PWM()
{
  ledcAttachChannel(potentiostat.pwm_pin, potentiostat.pwm_freq,
                    potentiostat.pwm_res, potentiostat.pwm_channel);

  ledcWrite(potentiostat.pwm_pin, potentiostat.pwm_duty);
}

/**
* Starts the PWM that will be generated based on the circadian cycle, 
* assigning a duty cycle proportional to the light intensity at the expected time 
* on the RGB LED strip
*/
void start_LEDstripe_PWM()
{
  ledcAttachChannel(ledrgb.red_pin, ledrgb.pwm_freq,
                    ledrgb.pwm_res, ledrgb.red_channel); 
                    
  ledcAttachChannel(ledrgb.green_pin, ledrgb.pwm_freq,
                    ledrgb.pwm_res, ledrgb.green_channel); 
                    
  ledcAttachChannel(ledrgb.blue_pin, ledrgb.pwm_freq,
                    ledrgb.pwm_res, ledrgb.blue_channel); 
}

/**
* Allows to directly modify the PWM of each RGB color as needed 
* or at the time of day, thus imitating the tonality of the light intensity in the sky.
*/
void setRGB_intensity(uint32_t duty_red, uint32_t duty_green, uint32_t duty_blue)
{
  ledcWrite(ledrgb.red_pin, duty_red);
  ledcWrite(ledrgb.green_pin, duty_green);
  ledcWrite(ledrgb.blue_pin, duty_blue);
}

 /**
 * Reads temperature and humidity data from the DHT11 sensors.
 * The data is stored in the corresponding sensor structure and 
 * printed to the serial console for transmission to the Raspberry Pi.
 */
void readSensors() 
{
  for (int i = 0; i < NUM_SENSORS; i++)
  {
    sensors[i].temperature = sensors[i].sensor.readTemperature();
    sensors[i].humidity = sensors[i].sensor.readHumidity();
    Serial.print("Sensor "); Serial.print(i+1);
    Serial.print(" - Temp: "); Serial.print(sensors[i].temperature);
    Serial.print(" °C, Hum: "); Serial.print(sensors[i].humidity);
    Serial.println(" %");
  }
}

/**
 * Controls the relays that activate TEC1-12706 Peltier cells, 
 * and a water pump inside the bioclimatic chamber.
 * The activation is based on temperature and humidity conditions.
 */
void controlRelays()
{
  avgTemp = (sensors[0].temperature + sensors[1].temperature +
                    sensors[2].temperature + sensors[3].temperature) / 4;
/* Temperature monitor to activate peltier cells */
  if (avgTemp < 10) 
  {
    digitalWrite(relays[0], LOW);
    digitalWrite(relays[1], LOW);
  }
  else 
  {
    digitalWrite(relays[0], HIGH);
    digitalWrite(relays[1], HIGH);
  }

  if (avgTemp > 35) 
  {
    digitalWrite(relays[2], LOW);
    digitalWrite(relays[3], LOW);
  } 
  else 
  {
    digitalWrite(relays[2], HIGH);
    digitalWrite(relays[3], HIGH);
  }

  avgHumidity = (sensors[0].humidity + sensors[1].humidity +
                       sensors[2].humidity + sensors[3].humidity) / 4;

/* Humidity monitor to activate water pump */
  if (avgHumidity < 30) 
  {
    digitalWrite(relays[4], LOW);
  } 
  else 
  {
    digitalWrite(relays[4], HIGH);
  }
}

/**
 * Reads sensor data and ADC voltage, formats it into a structured message,
 * and sends it over UART to the Raspberry Pi.
 */
void sendData()
{
  adcValue = ads.readADC_SingleEnded(0);
  voltage = adcValue * (5.0 / 32767.0);

  String message = "";
  for (uint8_t i = 0; i < NUM_SENSORS; i++)
  {
    message += "T" + String(i+1) + "=" + String(sensors[i].temperature) + ",";
    message += "H" + String(i+1) + "=" + String(sensors[i].humidity) + ";";
  }

  message += "ADC=" + String(adcValue) + ",";
  message += "V=" + String(voltage, 3) + ";";

  for (uint8_t i = 0; i < NUM_RELAYS; i++)
  {
    message += "R" + String(i+1) + "=" + (digitalRead(relays[i]) == LOW ? "1" : "0") + ",";
  }
  
  Serial.println(message);
}

/**
 * Processes incoming commands from the Raspberry Pi.
 * Commands can toggle relays and switch between automatic and manual control modes.
 */
void processCommand(String command)
{
  command.trim();
  if (command == "CMD=AUTO")
  {
    automaticMode = true;
  }
  else if (command.startsWith("CMD=FORCE"))
  {
    automaticMode = false;

    for (uint8_t i = 0; i < NUM_RELAYS; i++)
    {
      if (command.indexOf("R" + String(i+1) + "=1") != -1) 
      {
        digitalWrite(relays[i], LOW);
      } 
      else if (command.indexOf("R" + String(i+1) + "=0") != -1)
      {
        digitalWrite(relays[i], HIGH);
      } 
    }
  }
}



/********************************/
/******* HW initial setup *******/
/********************************/
/**
 * Initializes all hardware components, including:
 * - PWM configuration (3.1 kHz on GPIO 18)
 * - Serial communication (UART)
 * - I2C communication for ADS1115
 * - DHT11 sensors
 * - Relay pins
 */
void setup()
{
  start_Potentiostat_PWM();
  start_LEDstripe_PWM();
  Serial.begin(115200);
  Wire.begin();
  
  for (uint8_t i = 0; i < NUM_SENSORS; i++) 
  {
    sensors[i].sensor.begin();
  }
  
  for (uint8_t i = 0; i < NUM_RELAYS; i++) 
  {
    pinMode(relays[i], OUTPUT);
    digitalWrite(relays[i], HIGH);
  }
  
  if (!ads.begin())
  {
    Serial.println("Error: No ADS1115 detected");
    while (1);
  }
  
  ads.setGain(GAIN_TWOTHIRDS);
}


/************************************************/
/************ Application entry point ***********/
/************************************************/
/**
 * Main execution loop:
 * - Reads and processes UART commands
 * - Periodically reads sensors and controls relays
 * - Sends data to Raspberry Pi
 */
void loop()
{
  if (Serial.available()) 
  {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  currentTime = millis();
  if (currentTime - previousTime >= DELAY_MS) 
  {
    previousTime = currentTime;

    readSensors();
    if (automaticMode)
    {
      controlRelays();
    }
    sendData();
  }
}





