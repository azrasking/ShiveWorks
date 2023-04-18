import paho.mqtt.client as mqtt
import csv
import time

# ---TODO--- #
# 1. get the segment status stored in a list
# 2. get the movement function up and running


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
statusList = []  # list of the status of all segments ordered by segment number


def on_message(client, userdata, message):
    global latestOverseerReturnMessage  # use the global variable
    print("Message received: " + str(message.payload.decode("utf-8")))
    # filter only the return messages
    if (message.topic == overseerReturnPath):
        latestOverseerReturnMessage = str(message.payload.decode("utf-8"))

    # filter only the status messages
    elif (message.topic.startswith(segmentPath)):
        # get the segment ID from the topic -> convert it to the segment number
        segment_no = getSegmentNumber(message.topic.split("/")[2])
        # get the status from the message
        status = str(message.payload.decode("utf-8"))
        # store the status in the list
        statusList[segment_no - 1] = status


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
            return i + 1
    return -1


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
            # acknowledge the pairing
            client.publish(overseerReturnPath, "ack", 1)
            # subscribe to the status and data return of the new segment
            client.subscribe(segmentPathFn(segment_no, "status"), 1)
            client.subscribe(segmentPathFn(segment_no, "return"), 1)
            # print segment number and id that has been added to the list
            print("Segment #{} has been added to the list with ID: {}".format(
                segment_no, ID_str))
    else:
        print("No segment available for assignment")


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
            client.subscribe(segmentPathFn(i, "status"), 1)
            client.subscribe(segmentPathFn(i, "return"), 1)


def saveSegmentsID():   # save the segments ID to a .csv file
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=' ')
        for ID in segments_ID:
            writer.writerow([ID])


def clearSegmentID(segment_no):  # clear a segment ID from the list
    client.unsubscribe(segmentPathFn(segment_no, "status"))
    client.unsubscribe(segmentPathFn(segment_no, "return"))
    addSegmentID(segment_no, "Null")


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
def segmentPathFn(segment_number, whatToDo):
    if whatToDo == "command" or whatToDo == "return" or whatToDo == "status":
        return segmentPath + "/" + getSegmentID(int(segment_number)) + "/" + whatToDo
    # there are three topics for each segment: command, return, and status


def segment_reset(segment_no):  # reset a specific segment
    client.publish(overseerCommandPath, "reset::{}".format(
        getSegmentID(segment_no)), 1)


def timesync_segment(segment_no):  # timesync a specific segment
    client.publish(segmentPathFn(segment_no, "command"), "timesync", 1)


def upload_segment(segment_no, data):  # upload data from a specific segment
    client.publish(segmentPathFn(segment_no, "command"), data, 1)


def get_segment_status(segment_no):  # get the status of a specific segment
    client.publish(segmentPathFn(segment_no, "command"), "status_report", 1)
    time.sleep(0.25)  # wait for the status report to be published
    try:
        return statusList[int(segment_no - 1)]
    except IndexError:
        return ("Segment does not have a reported status yet")


# ---------------------- Manual Commands ----------------------#
if __name__ == "__main__":
    main()

while True:
    # an infinite loop that waits for a command to control the whole shive machine
    input_str = input("\nEnter a command: ").lower()
    match input_str.split():
        case ["start"]:
            print("Starting the experiment")
            client.publish(overseerCommandPath, "start::all", 1)

        case ["stop"]:
            print("Stopping the experiment")
            client.publish(overseerCommandPath, "stop::all", 1)

        case ["reset"]:
            print("Resetting all segments")
            client.publish(overseerCommandPath, "reset::all", 1)

        case ["reset", *args] if '-s' in args:  # reset a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Resetting the segment # {}".format(segment_no))
            segment_reset(segment_no)

        case ["upload"]:
            print("Uploading data to all segments...")
            client.publish(overseerCommandPath, "upload::all")

        case ["upload", *args] if '-s' in args:  # upload to a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Uploading data to segment # {}".format(segment_no))
            upload_segment(segment_no, "TEST_DATA_STRING")

        # case ["move"]:
        #     print("Moving all segments")
        #     client.publish(overseerCommandPath, "move::", 1)

        # case ["move", *args] if '-s' in args:  # move a specific segment
        #     segment_no = args[args.index('-s') + 1]
        #     print("Moving the segment # {}".format(segment_no))

        case ["timesync"]:
            print("Syncing time in all segments")
            client.publish(overseerCommandPath, "timesync::all", 1)

        case ["timesync", *args] if '-s' in args:  # timesync an individual segment
            segment_no = args[args.index('-s') + 1]
            print("Syncing time in segment # {}".format(segment_no))

        case ["exit" | "quit"]:
            print("Exiting the program")
            client.publish(overseerCommandPath, "stop", 1)
            client.loop_stop()
            quit()

        case ["clear_pairing"]:
            print("Clearing all segment IDs")
            clearSegmentsID()

        case ["clear_pairing", *args] if '-s' in args:  # clear a specific segment ID
            segment_no = args[args.index('-s') + 1]
            print("Clearing the segment # {}".format(segment_no))
            clearSegmentID(segment_no)

        case ["debug"]:
            print("Latest global message received: {}".format(
                latestOverseerReturnMessage))

        case ["debug", *args] if '-s' in args:  # debug a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Debugging segment # {}:".format(segment_no))
            print(getSegmentID(segment_no))
            print(get_segment_status(segment_no))

        case ["assign", *args] if '-s' in args:  # assign a segment an ID
            segment_no = args[args.index('-s') + 1]
            addSegmentID(segment_no)

        case _:
            print("Invalid command\nPlease refer to readme.md")
