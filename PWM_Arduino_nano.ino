const int pwmPin = 9;  // Pin de salida PWM

void setup() {
  // Configura el pin como salida
  pinMode(pwmPin, OUTPUT);

  // Configura Timer1 para generar PWM a 3100 Hz
  noInterrupts();            // Desactiva interrupciones
  TCCR1A = 0;                // Limpia los registros
  TCCR1B = 0;
  
  TCCR1A |= (1 << COM1A1);   // Configura OC1A (Pin 9) para PWM no inverso
  TCCR1A |= (1 << WGM11);    // Modo Fast PWM (modo 14)
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << WGM13);

  TCCR1B |= (1 << CS10);     // Preescaler 1 (sin división)

  ICR1 = 5154;               // Freq = 16MHz / (1 * (ICR1 + 1)) --> 3103 Hz aprox
  OCR1A = ICR1 / 2;          // Duty Cycle 50%

  interrupts();              // Activa interrupciones
}

void loop() 
{} 


