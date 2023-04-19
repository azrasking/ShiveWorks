#pragma once

#include <WiFi.h>
#include <PubSubClient.h>

//-------------------- MQTT connection setup --------------------
uint8_t getConnectionAttemptsWiFi(void);
uint8_t getConnectionAttemptsMQTT(void);
bool wifi_reconnect(bool forceReconnect = false);
bool mqtt_reconnect(uint32_t timeout = 0);

void callback(char* topic, byte *payload, unsigned int length);

extern WiFiClient wifiClient;
extern PubSubClient client;

//-------------------- MQTT messages --------------------
const char* overseerCommandPath = "ShiveWorks/overseer/command"
const char* overseerReturnPath = "ShiveWorks/overseer/return"
const char* segmentPathMain = "ShiveWorks/segment"