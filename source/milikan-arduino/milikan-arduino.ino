/*
  Universidade Federal de Alagoas
  Instituto de Fisica
  Autor: Gean S. Santos
         Tecnico de Laboratorio/Fisica
  Data: 01/2020
 */
 
#define rep(i, n) for(int i = 1; i <= n; ++i)
#define change_key '1'
#define blow_drops '2'
int a0 = A0;
bool statusKey = LOW;
const int blow = 11;
const int key = 12;
const int led = 13;
int sizeSerial;
char cmd;


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
    cmd = Serial.read();  // Clear buffer
    if (cmd == change_key) {
        statusKey = !statusKey;
        digitalWrite(key, statusKey);
    } else if (cmd == blow_drops) {
        digitalWrite(led, HIGH);  // TO TEST
        digitalWrite(blow, HIGH);
        delay(2000);
        digitalWrite(blow, LOW);
        digitalWrite(led, LOW);  // TO TEST
    }
  }
}
