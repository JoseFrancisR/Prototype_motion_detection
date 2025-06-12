int ledPin = 13; // You can change this to any digital pin you're using

void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); 
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();

    if (cmd == '1') {
      digitalWrite(ledPin, HIGH); // Turn ON
    } else if (cmd == '0') {
      digitalWrite(ledPin, LOW); // Turn OFF
    }
  }
}