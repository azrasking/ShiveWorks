#pragma once

#include <WiFi.h>
#include <PubSubClient.h>

//-------------------- MQTT connection setup --------------------
uint8_t getConnectionAttemptsWiFi(void);
uint8_t getConnectionAttemptsMQTT(void);
bool wifi_reconnect(bool forceReconnect = false);
bool mqtt_reconnect();


extern WiFiClient wifiClient;
extern PubSubClient client;

//-------------------- MQTT messages --------------------
extern const char* overseerCommandPath;
extern const char* overseerReturnPath;
extern const char* segmentPathMain;
extern String getSegmentCommandPath();
extern String getSegmentDataPath();

bool sendOverseerMessage(const char* message);
bool sendSegmentStatus(const char* message);
bool sendSegmentData(const char* message);

void callbackMSG(char *topic, byte *payload, unsigned int length); //callback function for MQTT messages
extern String receivedTopic;         //shared buffer for received topic
extern byte* receivedMessage;        //shared buffer for received messages
extern byte* receivedData; //shared buffer for received
extern unsigned int receivedMessageLength; //length of received message
extern unsigned int receivedDataLength; //length of received message
extern bool messageReceived;        //flag for received message
