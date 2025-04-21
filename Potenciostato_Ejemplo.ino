// Pines
#define PWM_PIN 18              // PWM de salida (DAC simulado)
#define ADC_PIN 34              // Entrada ADC en GPIO 34 (ADC1_CH6)

// PWM config (ESP32 usa canales)
#define PWM_CHANNEL 0
#define PWM_FREQ 3100
#define PWM_RESOLUTION 8        // 8 bits (0-255)
#define DUTY_CYCLE 128

int val = 0;
float c = 0;
int n = 0;
int pos = 0;
float Potstep = 0.0078;
int vevals[] = {100, 20, 50, 100, 200, 250, 300};
uint8_t const count = 6;
long intervalos[7]; // 0 a 6

void setup() {
  Serial.begin(9600);

  // Configura PWM en ESP32
   analogWriteFrequency(PWM_PIN, PWM_FREQ);
  analogWriteResolution(PWM_PIN, PWM_RESOLUTION);
  analogWrite(PWM_PIN, DUTY_CYCLE); 
  analogReadResolution(12); 

  // Calcula los intervalos
  for (pos = 0; pos < count; pos++) {
    intervalos[pos] = 1000000L / (vevals[pos] * 128L); // en microsegundos
  }
}

void loop() {
  for (pos = 0; pos <= count; pos++) {
    n = 0;
    while (n <= 1) {
      // Forward scan
      for (val = 0; val <= 255; val++) {
        ledcWrite(PWM_CHANNEL, val); // PWM al 0-255
        delay(intervalos[pos] / 1000); // Convertimos a milisegundos
        c = analogRead(ADC_PIN);
        Serial.print(val);
        Serial.print(" ");
        Serial.print(c);
        Serial.print(" ");
        Serial.print(n);
        Serial.print(" ");
        Serial.print(vevals[pos]);
        Serial.print(" ");
        Serial.println(intervalos[pos]);
      }

      // Reverse scan
      for (val = 255; val >= 0; val--) {
        ledcWrite(PWM_CHANNEL, val);
        delay(intervalos[pos] / 1000);
        c = analogRead(ADC_PIN);
        Serial.print(val);
        Serial.print(" ");
        Serial.print(c);
        Serial.print(" ");
        Serial.print(n);
        Serial.print(" ");
        Serial.print(vevals[pos]);
        Serial.print(" ");
        Serial.println(intervalos[pos]);
      }

      n = n + 1;
    }
  }
}
