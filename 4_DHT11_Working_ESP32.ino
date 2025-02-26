#include <DHT.h>
#include <DHT_U.h>

DHT dht1(17, DHT11); // DHT11 en GPIO 17
DHT dht2(5, DHT11);  // DHT11 en GPIO 5
DHT dht3(18, DHT11); // DHT11 en GPIO 18
DHT dht4(19, DHT11); // DHT11 EN GPIO 19

void setup() {
  Serial.begin(115200);
  dht1.begin();
  dht2.begin();
  dht3.begin();
  dht4.begin();
}

void loop() {
  float temp1 = dht1.readTemperature();
  float hum1 = dht1.readHumidity();

  float temp2 = dht2.readTemperature();
  float hum2 = dht2.readHumidity();

  float temp3 = dht3.readTemperature();
  float hum3 = dht3.readHumidity();

  float temp4 = dht4.readTemperature();
  float hum4 = dht4.readHumidity();
  


  Serial.print("Sensor 1 -> Temp: "); Serial.print(temp1); Serial.print(" Hum: "); Serial.println(hum1);
  Serial.print("Sensor 2 -> Temp: "); Serial.print(temp2); Serial.print(" Hum: "); Serial.println(hum2);
  Serial.print("Sensor 3 -> Temp: "); Serial.print(temp3); Serial.print(" Hum: "); Serial.println(hum3);
  Serial.print("Sensor 4 -> Temp: "); Serial.print(temp4); Serial.print(" Hum: "); Serial.println(hum4);

  delay(2000);
}