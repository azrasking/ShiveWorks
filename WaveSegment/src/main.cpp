#include <Arduino.h>    // a library for the Arduino platform
#include "FastLED.h"    // a library for controlling LEDs
#include "ESP32Servo.h" // a library for controlling servos
#include "OneButton.h"  // a library for the push button

#include "mqtt.h" // a library for connecting to an MQTT broker and wirelessly controlling the shiver

//------------------------------------//----pins

const int pin_servo = 19;
const int pin_ledA = 17;
const int pin_ledB = 16;
const int pin_button = 4;

//------------------------------------//---variables
// segment status, more in readme.md
enum SegmentStatus
{
  Initializing,
  Connected,
  Pairing,
  Paired,
  Downloading,
  Ready,
  Running,
  Estop,
  Fault
};

SegmentStatus currSegmentStatus = Initializing;

OneButton button(pin_button, false);

CRGB leds[2]; // an array of 2 LEDs

Servo servo;

//------------------------------------//---MISC

void beginPairing();

//------------------------------------//---UI

void buttonClick()
{
  if (currSegmentStatus != Pairing)
    beginPairing();
  else
    currSegmentStatus = Fault; // change to Connected possibly
}

void buttonDoubleClick()
{
  // cycle through RGB with 1s delay
  leds[0] = CRGB::Red;
  leds[1] = CRGB::Green;
  FastLED.show();
  delay(2000);
  leds[0] = CRGB::Green;
  leds[1] = CRGB::Blue;
  FastLED.show();
  delay(2000);
  leds[0] = CRGB::Blue;
  leds[1] = CRGB::Red;
  FastLED.show();
  delay(2000);

  // turn off LEDs
  leds[0] = CRGB::Black;
  leds[1] = CRGB::Black;
  FastLED.show();
  delay(250);

  // sweep servo from 45 to 135
  for (int i = 45; i < 135; i++)
  {
    servo.write(i);
    delay(50);
  }

  // sweep servo from 135 to 90
  for (int i = 135; i > 90; i--)
  {
    servo.write(i);
    delay(50);
  }

  // return to 90 position
  servo.write(90);
  delay(250);

  Serial.println("Self-test complete");
  sendSegmentStatus("Self-test complete");
  delay(250);
}

void buttonLongPress()
{
  ESP.restart(); // restart the ESP32
}

// display different colors depending on the segment status
const int blinkInterval = 500;
uint32_t lastLEDupdate = 0; // the last time in milliseconds the LEDs were updated
bool isBlinking = false, isCurrentlyOnOff = false;
void updateLED(SegmentStatus segStat)
{
  CRGB color;
  // save resources by only updating the LEDs when the status changes
  // set the color of the LEDs depending on the current segment status
  switch (segStat)
  {
  case Initializing:
    color = CRGB::Blue;
    isBlinking = false;
    break;
  case Connected:
    color = CRGB::Blue;
    isBlinking = true;
    break;
  case Pairing:
    color = CRGB::Purple;
    isBlinking = true;
    break;
  case Paired:
    color = CRGB::Purple;
    isBlinking = false;
    break;
  case Downloading:
    color = CRGB::Yellow;
    isBlinking = true;
    break;
  case Ready:
    color = CRGB::Green;
    isBlinking = true;
    break;
  case Running:
    color = CRGB::Green;
    isBlinking = false;
    break;
  case Estop:
    color = CRGB::Red;
    isBlinking = true;
    break;
  case Fault:
    color = CRGB::DarkRed;
    isBlinking = false;
    break;
  default:
    break;
  }

  // if the LEDs are blinking, check the interval and set them to black if it's time
  if (isBlinking)
  {
    // set the LEDs to black if they're currently supposed to be off in the blinking part
    if (isCurrentlyOnOff)
      color = CRGB::Black;

    // check if it's time to update the LEDs blinking
    if (millis() - lastLEDupdate > blinkInterval)
    {
      lastLEDupdate = millis();             // update the last time the LEDs were updated
      isCurrentlyOnOff = !isCurrentlyOnOff; // toggle the LEDs on/off variable
    }
  }

  // update the LEDs
  leds[0] = color;
  leds[1] = color;
  FastLED.show();
}

// convert the segment status to a string that can be sent over MQTT
String getSegmentStatusString()
{
  String statusString;
  switch (currSegmentStatus)
  {
  case Initializing:
    statusString = "Initializing";
    break;
  case Connected:
    statusString = "Connected";
    break;
  case Pairing:
    statusString = "Pairing";
    break;
  case Paired:
    statusString = "Paired";
    break;
  case Downloading:
    statusString = "Downloading";
    break;
  case Ready:
    statusString = "Ready";
    break;
  case Running:
    statusString = "Running";
    break;
  case Estop:
    statusString = "Estop";
    break;
  case Fault:
    statusString = "Fault";
    break;
  default:
    break;
  }
  return statusString;
}

//------------------------------------//----setup
bool hasInitializedHW = false;
void initializeHW()
{
  pinMode(pin_button, INPUT_PULLDOWN);
  // initialize the button routines
  button.attachClick(buttonClick);
  button.attachDoubleClick(buttonDoubleClick);
  button.attachLongPressStart(buttonLongPress);
  delay(250);

  // led initialization
  FastLED.addLeds<WS2812B, pin_ledA, GRB>(leds, 1).setCorrection(TypicalLEDStrip); // initialize the LEDs to the FastLED library
  FastLED.addLeds<WS2812B, pin_ledB, GRB>(leds, 1, 1).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(200); // set the brightness of the LEDs
  // set the LEDs to black on startup
  leds[0] = CRGB::White;
  leds[1] = CRGB::White;
  FastLED.show();
  delay(250);

  // servo initialization
  servo.attach(pin_servo);
  servo.write(90); // set the servo to the middle position
  delay(250);

  hasInitializedHW = true;
  delay(250);
}

bool hasInitializedMQTT = false;
void setup()
{
  Serial.begin(115200); // initialize the serial monitor
  initializeHW();       // initialize the LEDs, button, and servo

  // try to connect to the wifi 5 times
  while (!wifi_reconnect(false) && getConnectionAttemptsWiFi() < 5)
  {
    updateLED(currSegmentStatus); // update the LED state
  }
  WiFi.status() == WL_CONNECTED ? currSegmentStatus = Initializing : currSegmentStatus = Fault;
  delay(250);

  // try to connect to the MQTT broker 5 times, code will not proceed if something does not connect
  while (!mqtt_reconnect(false) && getConnectionAttemptsMQTT() < 5)
  {
    updateLED(currSegmentStatus); // update the LED state
  }
  hasInitializedMQTT = true;
  client.connected() == true ? currSegmentStatus = Connected : currSegmentStatus = Fault;
  delay(250);

  // subscribe to the general overseer command topic
  client.subscribe(overseerCommandPath, 1);

  // subscribe to the command topic for this segment
  client.subscribe(getSegmentCommandPath().c_str(), 1); // c_str() converts the String to a char array

  // subscribe to the data topic for this segment
  client.subscribe(getSegmentDataPath().c_str(), 1); // c_str() converts the String to a char array

  // update the segment's status
  sendSegmentStatus("Connected");
}

//------------------------------------//---state machine

void beginPairing()
{
  // send the ID to the overseer
  String message = "pairing::" + String(ESP.getEfuseMac(), HEX);
  client.publish(overseerReturnPath, message.c_str());
  sendSegmentStatus("Pairing");
  currSegmentStatus = Pairing;
}

// a generic function that represents the overseer acknowledging receipt of a message
bool mqttAck = false;
bool checkMQTTAcknowledged()
{
  return mqttAck;
};

//------------------------------------//---loop

void loop()
{
  button.tick();                // update the button state
  updateLED(currSegmentStatus); // update the LED state
  client.loop();                // update the ESP32 MQTT client data and communication

  // check if a message has been received and handle accordingly
  if (messageReceived)
  {
    messageReceived = false;
    // check if the message is a command
    if (receivedTopic == overseerCommandPath)
    {
      // PROGRAM ALL GENERAL COMMANDS HERE
    }

    // command payload will always be a string, while data payload will be a byte array
    else if (receivedTopic == getSegmentCommandPath())
    {
      String commandStr = (char *)receivedBuffer;
      // if the received message payload is "status_report", send the status report
      if (commandStr == "status_report")
      {
        sendSegmentStatus(getSegmentStatusString().c_str());
      }
      if (commandStr == "ack")
      {
        mqttAck = true;
      }
    }

    else if (receivedTopic == getSegmentDataPath())
    {
    }
  }

  switch (currSegmentStatus)
  {
  case Initializing:
    // do nothing, but display a color
    break;
  case Connected:
    // do stuff
    break;
  case Pairing:
    if (checkMQTTAcknowledged())
    {
      sendSegmentStatus("Paired");
      currSegmentStatus = Paired;
      mqttAck = false;
    }
    break;
  case Paired:
    // do nothing, but display a color
    break;
  case Downloading:
    // do stuff
    break;
  case Ready:
    // do stuff
    break;
  case Running:
    // do stuff
    break;
  case Estop:
    // do stuff
    break;
  case Fault:
    // do nothing, but display red
    break;
  default:
    break;
  }
}