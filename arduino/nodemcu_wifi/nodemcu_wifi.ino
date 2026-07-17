/*
=====================================================
            AquaSentinel AI
        NodeMCU (ESP8266) - Wi-Fi bridge
-----------------------------------------------------
Reads the "PH:.. TEMP:.." line coming from the Arduino
Uno over a software serial link, and serves it as JSON
on the local Wi-Fi network:

    http://<nodemcu-ip>/ph   ->   {"ph":7.24,"temperature":26.5}

The laptop (serial_reader.read_from_nodemcu) fetches this.
The NodeMCU only relays data; it does not control the Uno.

Wiring (level-shift 5V->3.3V on the Uno TX -> NodeMCU RX line!):
  Uno TX (pin 3, SoftwareSerial) -> NodeMCU D5 (via divider / level shifter)
  Uno GND                        -> NodeMCU GND
=====================================================
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <SoftwareSerial.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASS = "YOUR_PASSWORD";

SoftwareSerial unoLink(D5, D6);   // RX, TX (TX to Uno unused here)
ESP8266WebServer server(80);

float g_ph = 7.0;
float g_temp = 25.0;

void parseLine(const String& line) {
  int p = line.indexOf("PH:");
  int t = line.indexOf("TEMP:");
  if (p >= 0) g_ph = line.substring(p + 3).toFloat();
  if (t >= 0) g_temp = line.substring(t + 5).toFloat();
}

void handlePH() {
  String json = "{\"ph\":" + String(g_ph, 2) +
                ",\"temperature\":" + String(g_temp, 1) + "}";
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void setup() {
  Serial.begin(115200);
  unoLink.begin(9600);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("NodeMCU IP: ");
  Serial.println(WiFi.localIP());   // note this IP for the laptop

  server.on("/ph", handlePH);
  server.begin();
}

void loop() {
  if (unoLink.available()) {
    String line = unoLink.readStringUntil('\n');
    line.trim();
    if (line.length()) parseLine(line);
  }
  server.handleClient();
}
