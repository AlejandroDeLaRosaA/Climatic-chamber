#include <WiFi.h>
#include <time.h>

/* === Config de RED === */
const char* ssid     = "yourSSIDhere"
const char* password = "yourpasswordhere"

/* === Zona Horaria y server NTP === */
// UTC-6 CDMX / GDL
const long gmtOffset_sec = -6 * 3600;
const int daylightOffset_sec = 0;
const char *ntpServer = "pool.ntp.org";

/* Control de tiempo */
unsigned long currentMillis;
unsigned long lastTimeUpdate = 0;
const unsigned long TIME_UPDATE_INTERVAL = 1000;


void setup()
{
  Serial.begin(115200);
  delay(1000);

  // WiFi Setup
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi conectado");

  /* NTP config */
  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org", "time.nist.gov");

  // Espera a sincronizar la hora
  struct tm timeinfo;
  Serial.println("Esperando hora NTP...");
  while (!getLocalTime(&timeinfo))
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println("\nHora sincronizada.");
}

void loop()
{
  currentMillis = millis();
  if(currentMillis - lastTimeUpdate >= TIME_UPDATE_INTERVAL)
  {
    lastTimeUpdate = currentMillis;
    struct tm timeinfo;
    if(getLocalTime(&timeinfo))
    {
      Serial.println(&timeinfo, "%A, %B %d %Y %H:%M:%S");
    }
    else
    {
      Serial.println("Fallo al obtener hora");
    }
  }

}
