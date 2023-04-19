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

//------------------------------------//---UI

void buttonClick()
{
  if (currSegmentStatus != Pairing)
    currSegmentStatus = Pairing;
  else
    currSegmentStatus = Fault; // change to Connected possibly
}

void buttonDoubleClick()
{
  // PUT SEGMENT SELF-TEST CODE HERE
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
  FastLED.addLeds<WS2812B, pin_ledB, GRB>(leds, 1).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(160); // set the brightness of the LEDs
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
void initializeMQTT(){

hasInitializedMQTT = true;
}

void setup()
{
  Serial.begin(115200);
  initializeHW();
  updateLED(currSegmentStatus); // update the LED state
  initializeMQTT();
}

//------------------------------------//---state machine

bool checkInitialized()
{
  return hasInitializedHW && hasInitializedMQTT;
}

void beginConnection()
{
}

void beginConnected()
{
}

//------------------------------------//---loop

void loop()
{
  button.tick();                // update the button state
  updateLED(currSegmentStatus); // update the LED state

  switch (currSegmentStatus)
  {
  case Initializing:
    if (checkInitialized())
    {
      currSegmentStatus = Connected;
      void beginConnected();
    }
    else
    {
      beginConnection();
    }
    break;
  case Connected:
    // do stuff
    break;
  case Pairing:
    // do stuff
    break;
  case Paired:
    // do stuff
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