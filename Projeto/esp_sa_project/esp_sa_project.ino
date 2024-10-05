/*

#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <ESP8266HTTPClient.h>

// Replace with your own WiFi credentials
const char* ssid = "Left";
const char* password = "d86ce9f72c30";

// Replace with your own server details
const char* host = "https://sanda.pedrocas15.repl.co/";
const int httpsPort = 8080; // HTTPS port
const char fingerprint[] PROGMEM = "A6 5A 41 2C 0E DC FF C3 16 E8 57 E9 F2 C3 11 D2 71 58 DF D9"; // Replace with your server's SHA1 fingerprint

void setup() {
  Serial.begin(115200);
  delay(10);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void loop() {
  WiFiClientSecure client;
  client.setInsecure();

  Serial.print("Connecting to ");
  Serial.println(host);

  HTTPClient http;
  Serial.println(http.begin(client, host));

  Serial.println(http.POST());

  http.end();
}*/











#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include <vector>

const char* clientSsid     = "Left";
const char* clientPassword = "d86ce9f72c30";

const char* host = "https://9c1b92b6-4f85-4213-9fee-b6bafecc9c6f.deepnoteproject.com/post/1";
const int httpsPort = 8080; // HTTPS port

WiFiEventHandler probeRequestPrintHandler;

String macToString(const unsigned char* mac) {
  char buf[20];
  snprintf(buf, sizeof(buf), "%02x:%02x:%02x:%02x:%02x:%02x",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(buf);
}

std::vector<WiFiEventSoftAPModeProbeRequestReceived> myList;

void onProbeRequestPrint(const WiFiEventSoftAPModeProbeRequestReceived& evt) {
  myList.push_back(evt);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Hello!");

  // Don't save WiFi configuration in flash - optional
  WiFi.persistent(false);

  WiFi.mode(WIFI_AP_STA);
  WiFi.begin(clientSsid, clientPassword);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(100);
  }
  Serial.println("");
  probeRequestPrintHandler = WiFi.onSoftAPModeProbeRequestReceived(&onProbeRequestPrint);
}

void loop() {

  delay(3000);
  String json = "";
  for(WiFiEventSoftAPModeProbeRequestReceived w : myList){
    json.concat(macToString(w.mac));
    json.concat(";");
    json.concat(w.rssi);
    json.concat("\n");
  }
  

  myList.clear();

  WiFiClientSecure client;
  client.setInsecure();

  Serial.print("Connecting to ");
  Serial.println(host);

  HTTPClient http;
  Serial.println(http.begin(client, host));
  http.addHeader("Content-Type", "application/json");

  Serial.println(http.POST(json));

  http.end();
}