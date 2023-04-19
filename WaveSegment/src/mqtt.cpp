#include <mqtt.h>
#include <credentials.h>

WiFiClient wifiClient;
PubSubClient client(wifiClient);

const uint32_t KEEP_ALIVE_INTERVAL = 20; // seconds

uint32_t lastWiFiConnectionAttempt = 0;
uint32_t wifiConnectionRetryInterval = 7000; // milliseconds, do not set to less than 5000
bool isConnecting = false;
uint8_t wifiConnectionAttempts = 0;

uint8_t getConnectionAttemptsWiFi()
{
    return wifiConnectionAttempts;
}

/*
 * Connect to WiFi network
 * @param forceReconnect: if true, force a reconnect
 * @return true if connected, false otherwise
 */

bool wifi_reconnect(bool forceReconnect)
{
    // if we're not connected, try to connect
    if (WiFi.status() != WL_CONNECTED)
    {
        // try to connect, and if we failed try again after a delay
        if (millis() - lastWiFiConnectionAttempt > wifiConnectionRetryInterval || forceReconnect)
        {
            Serial.print("\nMy MAC address is: ");
            Serial.print(WiFi.macAddress());

            Serial.print("\nConnecting to: ");
            Serial.print(ssid);

            // attempt to connect to WiFi network
            lastWiFiConnectionAttempt = millis();
            WiFi.mode(WIFI_STA); // set the ESP32 to be a WiFi client
            WiFi.begin(ssid, password);

            isConnecting = true;
            wifiConnectionAttempts++;
        }

        // if we're still not connected, let us know we're still trying by printing a dot
        static uint32_t lastDot = 0;
        if (millis() - lastDot > 500)
        {
            lastDot = millis();
            Serial.print('.');
        }
    }

    // if we're connected, let us know
    if (WiFi.status() == WL_CONNECTED)
    {
        // if we've been trying to connect, let us know we succeeded
        if (isConnecting)
        {
            Serial.println("Connected with IP address: ");
            Serial.println(WiFi.localIP());

            isConnecting = false;
        }
        return true;
    }
    return false;
}

/*
 * Connect to MQTT broker
 * @param timeout: if timeout is not zero, keep trying to reconnect for the timeout period
 * @return true if connected, false otherwise
 */

uint32_t lastConnectionAttempt = 0;
uint32_t connectionRetryInterval = 2500; // milliseconds, do not set to less than 2000
uint8_t MQTTConnectionAttempts = 0;

uint8_t getConnectionAttemptsMQTT()
{
    return MQTTConnectionAttempts;
}

bool mqtt_reconnect(uint32_t timeout)
{
    // bool wifi_cxn = wifi_reconnect();

    // if (!wifi_cxn)
    // {
    //     if (timeout) // if timeout is not zero, keep trying to reconnect for the timeout period
    //     {
    //         uint32_t startTime = millis();
    //         while (millis() - startTime < timeout)
    //         {
    //             wifi_cxn = wifi_reconnect();
    //             if (wifi_cxn)
    //                 break;
    //         }
    //     }
    // }

    // if (!wifi_cxn)
    //     return false;

    // try to reconnect once to the MQTT broker //78aaf0d82240 //40:22:D8:F0:AA:78
    if (!client.connected())
    {
        if (millis() - lastConnectionAttempt > connectionRetryInterval)
        {
            lastConnectionAttempt = millis();

            client.setServer(mqtt_server, mqtt_port);
            client.setKeepAlive(KEEP_ALIVE_INTERVAL);

            Serial.println("MQTT connecting...");

            // Create a client ID unique to this very chip the code is uploaded to
            String clientId = String(ESP.getEfuseMac(), HEX);

            Serial.print("Connecting as: ");
            Serial.println(clientId);

            // Attempt to connect
            if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD))
            {
                // client.setCallback(callback); // set the callback function that will handle incoming messages               )
                Serial.println("Connected to broker");
                return true;
            }

            else
            {
                Serial.print("Failed, Error = ");
                Serial.print(client.state());
                Serial.println("; will retry");

                MQTTConnectionAttempts++;
                return false;
            }
        }

        return false;
    }

    return true;
}

void callback(char *topic, byte *payload, unsigned int length)
{
    Serial.println(topic);
    Serial.print("||");
    Serial.write(payload, length);
    Serial.println();
}