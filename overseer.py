# Jakub Jandus 2023
# Overseer class for the ShiveWorks project
# This class is responsible for the communication with the segments and the movement of the segments

import paho.mqtt.client as mqtt
import csv
import time

# ---TODO--- #
# 1. servo angle limiter
# 2. upload working


# ---------------------- MQTT Setup----------------------#
# callback function for when a message is received and filter according to topic

segment_count = 100  # number of segments
overseerCommandPath = "ShiveWorks/overseer/command"
overseerReturnPath = "ShiveWorks/overseer/return"

# expanded into ShiveWorks/segment/segmentID/command further below
segmentPath = "ShiveWorks/segment"

broker = "127.0.0.1"
port = 1884
client = mqtt.Client("Master PC")


def main():  # main method where the MQTT client is connected
    # try to connect to the broker, if not successful wait 5 seconds and try again
    while True:
        try:
            client.connect(broker, port)
            break
        except:
            print("Connection to broker failed, retrying in 5 seconds...")
            time.sleep(5)

    client.subscribe(overseerReturnPath, 1)
    client.loop_start()
    client.on_message = on_message
    loadSegmentsID()


# --- MQTT Received Message Callback functions ---#
latestOverseerReturnMessage = ""  # global storage of the latest message received
# list of the status of all segments ordered by segment number
statusList = [None]*segment_count


def on_message(client, userdata, message):
    global latestOverseerReturnMessage  # use the global variable
    print("Message received: " + str(message.payload.decode("utf-8")))
    topic = message.topic
    msgPayload = message.payload.decode("utf-8")

    # filter only the return messages
    if (topic == overseerReturnPath):
        latestOverseerReturnMessage = str(msgPayload)

    # filter only the status messages
    elif (topic.startswith(segmentPath) and topic.endswith("status")):
        # get the segment ID from the topic -> convert it to the segment number
        segment_no = getSegmentNumber(topic.split("/")[2])
        # get the status from the message
        status = str(msgPayload)
        # store the status in the list
        statusList[segment_no - 1] = status

        # special case to confirm pairing
        #   if a segment ID is assigned and a message "Connected" is received, send back an "ack"
        if status == "Connected" and getSegmentID(segment_no) != "Null":
            segmentAck(segment_no)

    # filter only the data return messages
    elif (topic.startswith(segmentPath) and topic.endswith("data")):
        # get the segment ID from the topic -> convert it to the segment number
        segment_no = getSegmentNumber(topic.split("/")[2])
        # get the status from the message
        data = msgPayload
        # store the data in the return list
        # statusList[segment_no - 1] = status


# ---------------------- Dealing with segment identification ----------------------#
segments_ID = []  # an ordered list of all the segments' ID's
# this list is 100 elements long, with each element being a string
filePath = "segmentsID.csv"


# get the ID of a segment from the list and return it as a string (empty string if not found)
def getSegmentID(segment_no):
    try:
        return segments_ID[int(segment_no) - 1]
    except IndexError:
        print("Segment number out of range or non-existent")
        return int(-1)


# get the segment number from the ID and return it as an integer (-1 if not found)
def getSegmentNumber(segmentID):
    for i in range(len(segments_ID)):
        if segments_ID[i] == segmentID:
            return int(i + 1)
    return int(-1)


def addSegmentID(segment_no):  # add a segment ID to the list and save it to a .csv file
    # check if there is a segment available for assignment
    if latestOverseerReturnMessage.startswith('pairing'):

        # check if the segment number is valid
        if int(segment_no) > segment_count or int(segment_no) < 1:
            print("Invalid segment number")
            return
        else:
            ID_str = latestOverseerReturnMessage.split("::")[1]
            segments_ID[int(segment_no) - 1] = ID_str
            saveSegmentsID()

            # subscribe to the status and data return of the new segment
            segmentSub(segment_no)

            # acknowledge to the segment that pairing was successful
            segmentAck(segment_no)

            # print segment number and id that has been added to the list
            print("Segment #{} has been added to the list with ID: {}".format(
                segment_no, ID_str))
    else:
        print("No segment available for assignment")


# remove a segment ID from the list and save it to a .csv file
def removeSegmentID(segment_no):
    # check if the segment number is valid
    if int(segment_no) > segment_count or int(segment_no) < 1:
        print("Invalid segment number")
        return
    else:
        segments_ID[int(segment_no) - 1] = "Null"
        saveSegmentsID()

        # unsubscribe from the status and data return of the segment
        segmentUnSub(segment_no)

        # print segment number and id that has been removed from the list
        print("Segment #{} has been removed from the list".format(segment_no))


def loadSegmentsID():   # load the segments ID from a .csv file
    segments_ID.clear()  # clear the list before loading
    with open(filePath, 'r') as file:
        reader = csv.reader(file, delimiter=' ')
        for row in reader:
            segments_ID.append(row[0])

    # subscribe to the status of all segments if they exist
    for i in range(1, len(segments_ID) + 1):
        if getSegmentID(i) != "Null":
            # subscribe to the status and data return of the new segment
            segmentSub(i)


def saveSegmentsID():   # save the segments ID to a .csv file
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=' ')
        for ID in segments_ID:
            writer.writerow([ID])


def clearSegmentID(segment_no):  # clear a segment ID from the list
    segmentCommand(segment_no, "restart")
    removeSegmentID(segment_no)


def clearSegmentsID():  # clear the segments ID list
    segments_ID.clear()
    for i in range(segment_count):
        segments_ID.append("Null")
    saveSegmentsID()
    print("Segments ID list has been cleared, resetting program...")
    client.publish(overseerCommandPath, "stop", 1)
    client.loop_stop()
    quit()


# ---------------------- Individual Segment Functions ----------------------#
# functions to simplify ESP32 messages


def segmentSub(segment_no):
    client.subscribe(segmentPathFn(segment_no, "status"), 1)
    client.subscribe(segmentPathFn(segment_no, "return"), 1)


def segmentUnSub(segment_no):
    client.unsubscribe(segmentPathFn(segment_no, "status"), 1)
    client.unsubscribe(segmentPathFn(segment_no, "return"), 1)


def segmentCommand(segment_no, command):
    client.publish(segmentPathFn(segment_no, "command"), command, 1)


def segmentAck(segment_no):
    segmentCommand(segment_no, "ack")


def segmentSendData(segment_no, data):
    client.publish(segmentPathFn(segment_no, "data"), data, 1)

# ---------------------#


def segmentPathFn(segment_number, whatToDo):
    if whatToDo == "command" or whatToDo == "return" or whatToDo == "status" or whatToDo == "data":
        return segmentPath + "/" + getSegmentID(int(segment_number)) + "/" + whatToDo
    # there are three topics for each segment: command, return, and status


def segment_reset(segment_no):  # reset a specific segment
    segmentCommand(segment_no, "reset")


def segment_restart(segment_no):  # restart a specific segment
    segmentCommand(segment_no, "restart")


def timesync_segment(segment_no):  # timesync a specific segment
    segmentCommand(segment_no, "timesync")


def upload_segment(segment_no, data):  # upload data from a specific segment
    client.publish(segmentPathFn(segment_no, "data"), data, 1)


def move_segment(segment_no, position):  # move a specific segment to a position
    segmentCommand(segment_no, "move::{}".format(position))


def get_segment_status(segment_no):  # get the status of a specific segment
    segmentCommand(segment_no, "status_report")
    time.sleep(0.25)  # wait for the status report to be published
    try:
        return statusList[int(segment_no) - 1]
    except IndexError:
        return ("Segment does not have a reported status yet")


# ---------------------- Manual Commands ----------------------#
if __name__ == "__main__":
    main()

while True:
    # an infinite loop that waits for a command to control the whole shive machine
    input_str = input("\nEnter a command: ").lower()
    match input_str.split():
        # global commands----------------------------overseer topic
        case ["stop"]:
            client.publish(overseerCommandPath, "stop", 1)
            print("Stopping the experiment")

        case ["start"]:
            client.publish(overseerCommandPath, "start", 1)
            print("Starting the experiment")

        case ["reset"]:
            client.publish(overseerCommandPath, "reset", 1)
            print("Resetting all segments")

        # all segment commands----------------------------segment topic

        case ["upload"]:
            print("Uploading data to all segments...")
            # client.publish(overseerCommandPath, "upload::all")

        case ["move", *args] if ('-p' in args and '-s' not in args):
            position = args[args.index('-p') + 1]
            # client.publish(overseerCommandPath, "move::{}".format(position), 1)
            print("Moving all segments")

        case ["timesync"]:
            print("Syncing time in all segments")
            # client.publish(overseerCommandPath, "timesync::all", 1)

        case ["clear_pairing"]:
            print("Clearing all segment IDs")
            clearSegmentsID()

        # individual segment commands----------------------------segment topic

        case ["upload", *args] if '-s' in args:  # upload to a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Uploading data to segment # {}".format(segment_no))
            upload_segment(segment_no, "TEST_DATA_STRING")

        case ["move", *args] if '-s' and '-p' in args:  # move a specific segment
            segment_no = args[args.index('-s') + 1]
            position = args[args.index('-p') + 1]
            move_segment(segment_no, position)
            print("Moving the segment # {} to {}".format(segment_no, position))

        case ["timesync", *args] if '-s' in args:  # timesync an individual segment
            segment_no = args[args.index('-s') + 1]
            print("Syncing time in segment # {}".format(segment_no))

        case ["clear_pairing", *args] if '-s' in args:  # clear a specific segment ID
            segment_no = args[args.index('-s') + 1]
            clearSegmentID(segment_no)
            print("Clearing the segment # {}".format(segment_no))

        case ["reset", *args] if '-s' in args:  # reset a specific segment
            segment_no = args[args.index('-s') + 1]
            segment_reset(segment_no)
            print("Resetting the segment # {}".format(segment_no))

        case ["restart", *args] if '-s' in args:  # restart a specific segment
            segment_no = args[args.index('-s') + 1]
            segment_restart(segment_no)
            print("Restarting the segment # {}".format(segment_no))

        case ["debug", *args] if '-s' in args:  # debug a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Debugging segment # {}:".format(segment_no))
            print(getSegmentID(segment_no))
            print(get_segment_status(segment_no))

        case ["assign", *args] if '-s' in args:  # assign a segment an ID
            segment_no = args[args.index('-s') + 1]
            addSegmentID(segment_no)

        # misc----------------------------

        case ["debug"]:
            print("Latest global message received: {}".format(
                latestOverseerReturnMessage))

        case ["exit" | "quit"]:
            print("Exiting the program")
            client.publish(overseerCommandPath, "stop", 1)
            client.loop_stop()
            quit()

        case _:
            print("Invalid command\nPlease refer to readme.md")
