/*
  Universidade Federal de Alagoas
  Instituto de Fisica
  Autor: Gean S. Santos
         Tecnico de Laboratorio/Fisica
  Data: 24/08/2016
 */
 
#define rep(i, n) for(int i = 1; i <= n; ++i)
#define INIT_MILIKAN "0"
#define CHANGE_KEY "1"
#define INF "2"
#define ACK "3"


int a0 = A0;
bool statusKey = false;
const int key = 12;
const int led = 13;
int sizeSerial;
String command;
char tmp;

void setup() {
  Serial.begin(9600);
  pinMode(key, OUTPUT);
  digitalWrite(key, LOW);
  pinMode(led, OUTPUT);
  digitalWrite(led, LOW);
}

void handle_command(String command){
  if (command == CHANGE_KEY) {
    statusKey = !statusKey;
    if (statusKey) {
      digitalWrite(key, HIGH);
      digitalWrite(led, HIGH);
    }
    else {
      digitalWrite(key, LOW);
      digitalWrite(led, LOW);
    }
  }
  else if (command == INF) {
    Serial.print(ACK);
  }
}

void loop() {
  sizeSerial = Serial.available();
  command = "";
  if (sizeSerial) {
    rep (i, sizeSerial) {
      tmp = Serial.read();
      command += tmp;
    }
    handle_command(command);
  }
}
