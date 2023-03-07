#include <ESP8266WiFi.h>

// #define D0 16 /*      user  wake  PULLUP */
#define D1 5
#define D2 4
#define D3 0  /*      flash */
// #define D4 2  /* txd1 */
// #define D5 14 /*      hsclk       PULLUP */
// #define D6 12 /*      hmiso       PULLUP */
// #define D7 13 /* rxd2 hmosi */
// #define D8 15 /* txd2 */
// #define RX 3  /* rxd0 */
// #define TX 1  /* txd0 */
// #define S3 10 /* sdd3             PULLUP */
// #define S2 9  /* sdd2             PULLUP */

#define DEBUG 1
#define mdebug(value) if(DEBUG) Serial.println(value)


// wifi parameters
const char* ssid     = "...";
const char* password = "l@b3n$if";
// const char* ssid     = "network name";
// const char* password = "password";
WiFiServer server(80);

// pin parameters
const char key_pin   = D1;
const char reset_pin = D2;
const char relay_pin = D3;

// global variables parameters
const int memory_size = 1000;
int size_list = 0;
unsigned long ref = 0;
unsigned long time_list[memory_size];
bool key_previous_state = LOW;
bool output_state = LOW;
String html = "ProjMilikan_v3";


void reverse_output_state() {
  output_state = !output_state;
  digitalWrite(relay_pin, output_state);
}


void check_new_client() {
  WiFiClient client = server.available();
  if (client) {
    html = "Times\n";   // Long name
    html += "ms\n";      // Unit
    html += "\n";        // Comments
    for(int i = 0; i < size_list && time_list[i] != 0; ++i) {
      html += time_list[i];
      html += '\n';
    }
    client.println(html);
    mdebug("Print to client.");
  }
}


void reset_times() {
  for(int i = 0; i < memory_size; ++i) time_list[i] = 0;
  size_list = 0;
  mdebug("Reseted list.");
}


void setup() {
  reset_times();
 
  // setup serial
  Serial.begin(115200);
  mdebug("Setup init.");

  // setup pins
  pinMode(key_pin,   INPUT);
  pinMode(reset_pin, INPUT);
  pinMode(relay_pin, OUTPUT);

  digitalWrite(key_pin,   LOW); // turn on pulldown resistors
  digitalWrite(reset_pin, LOW); // turn on pulldown resistors
  digitalWrite(relay_pin, HIGH);

  // setup wifi
  IPAddress ip(192, 168, 0, 10);
  IPAddress gateway(192, 168, 0, 1);
  IPAddress subnet(255, 255, 255, 0);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);  // Connect to the network
  mdebug("Connecting to ");
  mdebug(ssid);
  mdebug("Please, to wait.");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    delay(1000);
    mdebug(++i);
  }

  mdebug('\n');
  mdebug("Connection established!");  
  mdebug("IP address:\t");
  mdebug(WiFi.localIP());  // Send the IP address of the ESP8266 to the computer

  // init server
  server.begin();

}


void loop() {
  // check key pin
  if (digitalRead(key_pin)) {
    if (key_previous_state == LOW) {
      key_previous_state = HIGH;
      reverse_output_state();
      if (size_list == 0) {
        ref = millis();
      }
      time_list[size_list] = millis() - ref;
      mdebug(time_list[size_list]);
      size_list = (size_list + 1) % memory_size;
    }
  }
  else {
    key_previous_state = LOW;
  }

  // check reset pin
  if (digitalRead(reset_pin)) {
    reset_times();
  }

  // check new client
  check_new_client();
  
  // guard time to get just one action from push button
  delay(50);
}
