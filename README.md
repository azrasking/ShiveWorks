# ShiveWorks
ShiveWorks - a dynamic material research project at WPI



# How to get started:
## MQTT Broker Installation
* Download and install the latest mosquitto broker (https://mosquitto.org/download/)

## ESP32 Segment Code Upload
* Enter correct local WiFi credential and MQTT broker IP address in credentials.h
* Compile and upload main.c to the ESP32

## Overseer.py
  * This scrips is used as a main translator between the simulation and the segments
  * It is command line based, and any command that is typed in will be sent to the segments accordingly

| Command     | Action                                                           |
| ----------- | ---------------------------------------------------------------- |
| start       | Starts the countdown of 3 seconds                                |
| stop        | Halts the experiment immediately                                 |
| reset       | Resets all segments to pre-experiment stage                      |
| upload      | Uploads the experiment parameters to all segments individually   |
| timesync    | Syncs the time of the segments with NTP, syncs overseer with NTP |
| assign:42   | Assigns any currently available segments to position 42          |
| upload:42   | Uploads the experiment parameters to segment 42                  |
| timesync:42 | Syncs the time of segment 42 with NTP                            |


# Experiment Setup
## Segment Power Up and Identification
* Power up the segment - upon initialization the indicator light should light up blue
* ESP32 will connect to the local MQTT broker - upon connection the indicator light should blink blue
  * If the segment is unable to connect to the MQTT broker, the indicator light will become solid red indicating a fault
* Once connected to the MQTT broker, the segment will automatically subscribe to the topic `shiveworks/masterCommand`
  * This is an equivalent to a command line that all segments will listen to
* For newly flashed segments, the sequence number will have to be assigned
  * Press the button on the segment to initiate the sequence number assignment - the indicator light should start blink purple
  * By typing `assign:42` into the python script command line and sending that to the masterCommand topic, the segment will be assigned to position 42
  * Indicator light will turn purple solid to indicate the sequence number has been received and saved
* Each segment will then subscribe to the topic `shiveworks/segment/42` where 42 is the sequence number of the segment
  * This is an equivalent to a command line that only the segment will listen to
  * Used for sending experiment parameters to the segment, and gathering scientific data 

 
| Segment Status                      | LED Indicator Light |
| ----------------------------------- | ------------------- |
| Initializing                        | Blue Solid          |
| Connected to MQTT Broker            | Blue Blinking       |
| Segment Position Identification     | Purple Blinking     |
| Segment Position Received and Saved | Purple Solid        |
| Downloading Experiment              | Yellow Blinking     |
| Ready for Experiment                | Green Blinking      |
| Experiment Running                  | Green Solid         |
| E-Stop                              | Red Blinking        |
| Fault                               | Red Solid           |
|                                     |                     |

| Button Press      | Action                                   |
| ----------------- | ---------------------------------------- |
| Button Press      | Initiate Segment Position Identification |
| Button Press + 5s | Reset Segment                            |
|                   |                                          |

  

## Running an Experiment
* Run the attached python scrypt and enter the desired experiment parameters
  * The script will automatically connect to the MQTT broker and send the experiment parameters to the ESP32
* Segment should start to light up and the indicator light should blink green indicating it is ready
* Once the countdown sequence is initiated, the indicator light will become solid green for the duration of the experiment
* In case of an E-stop or other fault, the indicator light will blink red