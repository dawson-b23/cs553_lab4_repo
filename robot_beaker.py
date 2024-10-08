import json
import random
import time

import numpy as np
import paho.mqtt.client as paho

import robot_controller as rc

## Globals
ipAddress = "172.29.208.119"
port = 1883
topic_beaker = "robot/beaker"
topic_bunsen = "robot/bunsen"
gripper_open = True
in_location = False
has_dice = True

# ip address to connect to robot
drive_path_beaker = "172.29.208.124"  # beaker
crx10_beaker = rc.robot(drive_path_beaker)  # set/connect to beaker robot
crx10_beaker.set_speed(200)  # set robot move speed to 200 mm/s


def rand_arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(0, 150))
    for i in range(n):
        rand_cart.append(0)

    return rand_cart


def create_json_message(coordinates):

    json_data = {
        "coordinates": coordinates,
        "gripper_status": gripper_open,
        "location_status": in_location,
    }

    # Save the parameters to the JSON file
    with open("robot_data.json", "w") as json_file:
        json.dump(json_data, json_file, indent=4)

    return json_file


def read_json_message(robot_data):
    # load the json file
    with open(robot_data, "r") as json_file:
        json_data = json.load(json_file)

    coordinates = np.array(json_data["json_data"])
    in_location = json_data["location_status"]


def on_connect(client, data, flags, returnCode):
    if returnCode == 0:
        print("Connection Successful.....")
    else:
        print(f"Connection Error: {str(returnCode)}")


def on_message(client, data, message):
    message_text = message.payload.decode("utf-8")

    read_json_message(message_text)


def main():
    client = paho.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(ipAddress, port)

    client.subscribe(topic_bunsen)
    # client.publish(topic_beaker, message)


main()
