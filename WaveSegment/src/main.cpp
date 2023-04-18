#include <Arduino.h>    // a library for the Arduino platform
#include "FastLED.h"    // a library for controlling LEDs
#include "ESP32Servo.h" // a library for controlling servos

#include "mqtt.h" // a library for connecting to an MQTT broker and wirelessly controlling the shiver

//------------------------------------//
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

//------------------------------------//

bool checkInitialize()
{
}

void beginInitialize()
{
}

void beginConnected()
{
}

//------------------------------------//

void setup()
{
  setup_mqtt();
}

//------------------------------------//

void loop()
{
  switch (currSegmentStatus)
  {
  case Initializing:
    if (checkInitialize())
    {
      currSegmentStatus = Connected;
      void beginConnected();
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
    // do stuff
    break;
  default:
    break;
  }
}