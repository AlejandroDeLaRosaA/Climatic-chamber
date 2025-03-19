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

#define NUM_SENSORS 4
#define NUM_RELAYS 6
#define DELAY_MS 2000

/************* PWM Config */
struct PWM
{
  uint8_t pwmChannel;
  uint8_t pwmPin;
  uint32_t pwmFreq;
  uint8_t pwmRes;
  uint32_t pwmDuty;
};

PWM pwm = {
  .pwmChannel = 0,
  .pwmPin = 18,
  .pwmFreq = 3100,
  .pwmRes = 10,
  .pwmDuty = 512
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
  {DHT(36, DHT11), 36, 0, 0},
  {DHT(39, DHT11), 39, 0, 0},
  {DHT(34, DHT11), 34, 0, 0},
  {DHT(35, DHT11), 35, 0, 0}
};

/************* Relay pins */
const uint8_t relays[] = {14, 27, 26, 25, 33, 32};

/************* ADS1115 config */
Adafruit_ADS1115 ads;

/************* Code execution config */
unsigned long currentTime = 0;
unsigned long previousTime = 0;
bool automaticMode = true;


/************* API */

/**
* Starts the generation of the pwm constant signal to be used
* by the potentiostat circuit.
*/
void startPWM()
{
  ledcAttachChannel(pwm.pwmPin, pwm.pwmFreq, pwm.pwmRes, pwm.pwmChannel);
  ledcWrite(pwm.pwmPin, pwm.pwmDuty);
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
 * as well as a water pump and LED lights inside the bioclimatic chamber.
 * The activation is based on temperature and humidity conditions.
 */
void controlRelays()
{
  float avgTemp = (sensors[0].temperature + sensors[1].temperature +
                    sensors[2].temperature + sensors[3].temperature) / 4;

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

  float avgHumidity = (sensors[0].humidity + sensors[1].humidity +
                       sensors[2].humidity + sensors[3].humidity) / 4;

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
  int16_t adcValue = ads.readADC_SingleEnded(0);
  float voltage = adcValue * (5.0 / 32767.0);

  String message = "";
  for (int i = 0; i < NUM_SENSORS; i++)
  {
    message += "T" + String(i+1) + "=" + String(sensors[i].temperature) + ",";
    message += "H" + String(i+1) + "=" + String(sensors[i].humidity) + ";";
  }

  message += "ADC=" + String(adcValue) + ",";
  message += "V=" + String(voltage, 3) + ";";

  for (int i = 0; i < NUM_RELAYS; i++)
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

    for (int i = 0; i < NUM_RELAYS; i++)
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
  startPWM();
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





