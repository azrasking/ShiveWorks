import paho.mqtt.client as mqtt

broker = "127.0.0.1"
port = 1884
client = mqtt.Client("Master PC")
client.connect(broker, port)

while True:
    # an infinite loop that waits for a command to control the whole shive machine
    input_str = input("Enter a command: ")
    match input_str.split():
        case ["start"]:
            print("Starting the experiment")
            client.publish("ShiveWorks/overseer", "start")

        case ["stop"]:
            print("Stopping the experiment")
            client.publish("ShiveWorks/overseer", "stop")

        case ["reset"]:
            print("Resetting all segments")
            client.publish("ShiveWorks/overseer", "reset")

        case ["reset", *args] if '-s' in args:  # reset a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Resetting the segment # {}".format(segment_no))

        case ["upload"]:
            print("Uploading data to all segments...")
            client.publish("ShiveWorks/overseer", "upload")

        case ["upload", *args] if '-s' in args:  # upload to a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Uploading data to segment # {}".format(segment_no))

        case ["timesync"]:
            print("Syncing time in all segments")
            client.publish("ShiveWorks/overseer", "timesync")

        case ["timesync", *args] if '-s' in args:  # timesync a specific segment
            segment_no = args[args.index('-s') + 1]
            print("Syncing time in segment # {}".format(segment_no))

        case "exit":
            print("Exiting the program")
            client.publish("ShiveWorks/overseer", "stop")
            quit()

        case _:
            print("Invalid command\nPlease refer to the readme.md")
