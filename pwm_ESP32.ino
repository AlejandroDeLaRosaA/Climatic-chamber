

const uint8_t pwmChannel = 0;
const uint8_t pwmPin = 18;  
const uint16_t pwmFreq = 3100;
const uint8_t pwmResolution = 12; // 12 bits (0-4095)

void setup() 
{
  ledcSetup(pwmChannel, pwmFreq, pwmResolution);
  ledcAttachPin(pwmPin, pwmChannel);
  ledcWrite(pwmChannel, 2048); // 50% de 4095
}

void loop() 
{

  
}