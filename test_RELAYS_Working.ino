const int relay1 = 16;
const int relay2 = 17;

void setup() {
  Serial.begin(9600);  // Comunicación UART con Raspberry
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);


  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "R1_ON") {
      digitalWrite(relay1, LOW);
      Serial.println("Relay 1 encendido");
    } 
    else if (command == "R1_OFF") {
      digitalWrite(relay1, HIGH);
      Serial.println("Relay 1 apagado");
    }
    else if (command == "R2_ON") {
      digitalWrite(relay2, LOW);
      Serial.println("Relay 2 encendido");
    }
    else if (command == "R2_OFF") {
      digitalWrite(relay2, HIGH);
      Serial.println("Relay 2 apagado");
    }
  }
}