/*
  Universidade Federal de Alagoas
  Instituto de Fisica
  Autor: Gean S. Santos
         Tecnico de Laboratorio/Fisica
  Data: 01/2020
 */
 
#define rep(i, n) for(int i = 1; i <= n; ++i)

int a0 = A0;
bool statusKey = LOW;
const int key = 12;
const int led = 13;
int sizeSerial;


void setup() {
  Serial.begin(9600);
  pinMode(key, OUTPUT);
  pinMode(led, OUTPUT);
  digitalWrite(key, LOW);
  digitalWrite(led, LOW);
}

void loop() {
  sizeSerial = Serial.available();
  if (sizeSerial) {  // It can be anything
    rep (i, sizeSerial) {
      Serial.read();  // Clear buffer
    }
    statusKey = !statusKey;
    digitalWrite(key, statusKey);
    digitalWrite(led, statusKey);
  }
}
