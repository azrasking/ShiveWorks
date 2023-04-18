#pragma once

#include <WiFi.h>
#include <PubSubClient.h>

bool wifi_reconnect(bool forceReconnect = false);
bool mqtt_reconnect(uint32_t timeout = 0);
void setup_mqtt(void);

void callback(char* topic, byte *payload, unsigned int length);

extern WiFiClient wifiClient;
extern PubSubClient client;