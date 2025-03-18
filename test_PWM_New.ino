
#define PWM_PIN 18        // Pin GPIO18
#define PWM_FREQ 3100     // Frecuencia de 3.1 kHz
#define PWM_RESOLUTION 8  // Resolución de 8 bits (valores de 0 a 255)

void setup() 
{
  analogWriteFrequency(PWM_PIN, PWM_FREQ);
  analogWriteResolution(PWM_PIN, PWM_RESOLUTION);
  analogWrite(PWM_PIN, 128);  // 128 es el 50% de 255
}

void loop() 
{
  
}