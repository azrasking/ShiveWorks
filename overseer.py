import paho.mqtt.client as mqtt
import csv

# ---------------------- MQTT Setup----------------------#
# callback function for when a message is received and filter according to topic


overseerCommandPath = "ShiveWorks/overseer/command"
overseerReturnPath = "ShiveWorks/overseer/return"

segmentStatusPath = "ShiveWorks/segment/status"
segmentCommandPath = "ShiveWorks/segment/command"
segmentReturnPath = "ShiveWorks/segment/return"

broker = "127.0.0.1"
port = 1884
client = mqtt.Client("Master PC")


def main():
    client.connect(broker, port)
    client.subscribe(overseerReturnPath, 1)
    client.loop_start()
    client.on_message = on_message
    loadSegmentsID()


# --- Callback functions ---#
latestOverseerReturnMessage = ""  # global storage of the latest message received
def on_message(client, userdata, message):
    global latestOverseerReturnMessage  # use the global variable
    if (message.topic == overseerReturnPath):  # filter only the return messages
        latestOverseerReturnMessage = str(message.payload.decode("utf-8"))


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
        return ""


def addSegmentID(segment_no):  # add a segment ID to the list and save it to a .csv file
    # check if there is a segment available for assignment
    if latestOverseerReturnMessage.startswith('pairing'):

        # check if the segment number is valid
        if int(segment_no) > 100 or int(segment_no) < 1:
            print("Invalid segment number")
            return
        else:
            ID_str = latestOverseerReturnMessage.split("::")[1]
            segments_ID[int(segment_no) - 1] = ID_str
            saveSegmentsID()
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


def saveSegmentsID():   # save the segments ID to a .csv file
    with open(filePath, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=' ')
        for ID in segments_ID:
            writer.writerow([ID])


# ---------------------- Manual Commands ----------------------#
if __name__ == "__main__":
    main()

while True:
    # an infinite loop that waits for a command to control the whole shive machine
    input_str = input("\nEnter a command: ").lower()
    match input_str.split():
        case ["start"]:
            print("Starting the experiment")
            client.publish(overseerCommandPath, "start", 1)

        case ["stop"]:
            print("Stopping the experiment")
            client.publish(overseerCommandPath, "stop", 1)

        case ["reset"]:
            print("Resetting all segments")
            client.publish(overseerCommandPath, "reset", 1)

        case ["reset", *args] if '-s' in args:  # reset a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Resetting the segment # {}".format(segment_no))

        case ["upload"]:
            print("Uploading data to all segments...")
            client.publish(overseerCommandPath, "upload")

        case ["upload", *args] if '-s' in args:  # upload to a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Uploading data to segment # {}".format(segment_no))

        case ["timesync"]:
            print("Syncing time in all segments")
            client.publish(overseerCommandPath, "timesync", 1)

        case ["timesync", *args] if '-s' in args:  # timesync an individual segment
            segment_no = args[args.index('-s') + 1]
            print("Syncing time in segment # {}".format(segment_no))

        case ["exit" | "quit"]:
            print("Exiting the program")
            client.publish(overseerCommandPath, "stop", 1)
            client.loop_stop()
            quit()

        case ["debug"]:
            print("Latest global message received: {}".format(
                latestOverseerReturnMessage))

        case ["debug", *args] if '-s' in args:  # debug a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Debugging segment # {}:".format(segment_no))
            print(getSegmentID(segment_no))

        case ["assign", *args] if '-s' in args:  # assign a segment an ID
            segment_no = args[args.index('-s') + 1]
            addSegmentID(segment_no)

        case _:
            print("Invalid command\nPlease refer to readme.md")
