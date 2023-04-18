# ShiveWorks 
**ShiveWorks - a dynamic material research project at WPI**

* The purpose of this project is to create a device that demonstrates several concepts from the theory of dynamic materials.
* It has been in researched for a long time

## Contributors
* Project Lead: @[William Sanguinet](https://github.com/williamsanguinet) | wcsanguinet@wpi.edu
* Engineer Lead: @[Jakub Jandus](https://github.com/BambusGS) | jjandus@wpi.edu

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# How to get started:
## MQTT Broker Installation
* Download and install the latest [mosquitto MQTT broker](https://mosquitto.org/download/)
* Linux
  * Run `mosquitto -v --config-file {{path/to/file.conf}}` to start the broker
* Windows
  * Go to the mosquitto installation directory (`cd C:\Program Files\mosquitto`), open terminal and run `mosquitto -v --config-file {{path/to/file.conf}` to start the broker
  * Make sure the network is set to "Private" in the Windows Firewall settings

## Overseer.py
  * Download and install [paho](https://pypi.org/project/paho-mqtt/)
  * This scrips is used as a main translator between the simulation and the segments
  * General MQTT command format is ''{{command}}::{{data}}
  * It is command line based, and any command that is typed in will be sent to the segments accordingly

| Command             | Action                                                           |
| ------------------- | ---------------------------------------------------------------- |
| start               | Starts the countdown of 3 seconds                                |
| stop                | Halts the experiment immediately                                 |
| reset               | Resets all segments to pre-experiment stage                      |
| upload              | Uploads the experiment parameters to all segments individually   |
| timesync            | Syncs the time of the segments with NTP, syncs overseer with NTP |
| clear_pairing       | Clears the pairing of segments                                   |
| debug               | Writes script debug info                                         |
| move 70             | Move all segments to position 70                                 |
| exit                | Exits the script                                                 |
| assign -s 42        | Assigns any currently available segments to position 42          |
| upload -s 42        | Uploads the experiment parameters to segment 42                  |
| timesync -s 42      | Syncs the time of segment 42 with NTP                            |
| clear_pairing -s 42 | Clears the pairing of segment 42                                 |
| debug -s 42         | Writes script debug info for segment number 42                   |
| move 70 -s 42       | Move segment 42 to position 70                                   |

<!-- implement a segment servo offset function -->


# Experiment Setup
## ESP32 Segment Code Upload
* Segments are numbered starting from 1
* All source files are in WaveSegment folder, in the 'src' directory
* Enter correct local WiFi credential and MQTT broker IP address in credentials.h (rename and fill out sample_credentials.h)
* Compile and upload main.c to the ESP32
<!-- * Once the initial sketch has been uploaded through USB, for subsequent uploads an OTA method can be used
  * Compile and upload main.c to the ESP32
  * Run `python3 OTA.py` to upload the sketch to the ESP32 over WiFi -->
![Segment Circuit](./Media/ShiveSegmentCircuit.png)
### Component List
* ESP32 DevKitV1
* MPU6050 Accelerometer/Gyroscope
* WS2812B RGB LED 2x
* MG90D Servo 2x
* Logic Level Converter 3.3V to 5V
* Voltage Regulator to 5V
* Push Button
* LiPo Battery 3.7V 800mAh 2x
  
## Segment Power Up and Identification
* Power up the segment - upon initialization the indicator light should light up blue
* ESP32 will connect to the local MQTT broker - upon connection the indicator light should blink blue
  * If the segment is unable to connect to the MQTT broker, the indicator light will become solid red indicating a fault
* Once connected to the MQTT broker, the segment will automatically subscribe to the topic `ShiveWorks/overseer/command`
  * This is an equivalent to a command line that all segments will listen to
* For newly flashed segments, the sequence number will have to be assigned
  * Press the button on the segment to initiate the sequence number assignment - the indicator light should start blink purple
  * By typing `assign -s 42` into the python script command line and sending that to the overseer topic, the segment will be assigned to position 42
  * Indicator light will turn purple solid to indicate the sequence number has been received and saved
* Each segment will then subscribe to the topic `shiveworks/segment/ID` where ID represents a unique ID for each segment is the sequence number of the segment
  * This is topic with transmit, receive, and status channels for a specific segment
  * Used for sending experiment parameters to the segment, and gathering scientific data 

 
| Segment Status                    | LED Indicator Light |
| --------------------------------- | ------------------- |
| Initializing                      | Blue Blinking       |
| Connected to Wifi and MQTT Broker | Blue Solid          |
| Segment Position Pairing          | Purple Blinking     |
| Segment Position Paired           | Purple Solid        |
| Downloading Experiment            | Yellow Blinking     |
| Ready for Experiment              | Green Blinking      |
| Experiment Running                | Green Solid         |
| E-Stop                            | Red Blinking        |
| Fault                             | Red Solid           |
|                                   |                     |

| Button Press      | Action                               |
| ----------------- | ------------------------------------ |
| Button Press      | Initiate Segment Position Assignment |
| Button Press + 5s | Reset Segment                        |
|                   |                                      |

  

## Running an Experiment
* Run the attached python scrypt and enter the desired experiment parameters
  * The script will automatically connect to the MQTT broker and send the experiment parameters to the ESP32
* Segment should start to light up and the indicator light should blink green indicating it is ready
* Once the countdown sequence is initiated, the indicator light will become solid green for the duration of the experiment
* In case of an E-stop or other fault, the indicator light will blink red
