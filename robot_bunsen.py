import json
import random
import time
from datetime import datetime

import numpy as np
import paho.mqtt.client as paho

import robot_controller as rc

ipAddress = "172.29.208.119"
port = 1883
topic_slave = "robot/slave"
topic_master = "robot/master"
gripper_open = True
is_slave = True
in_location = False

# ip address to connect to robot
drive_path_bunsen = "172.29.208.123"
crx10_bunsen = rc.robot(drive_path_bunsen)
crx10_bunsen.set_speed(200)


def get_utc_timestamp():
    # Get the current UTC time
    utc_time = datetime.utcnow()
    # Format the time as a string in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
    utc_timestamp = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    return utc_timestamp


def rand_arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(0, 150))
    for i in range(n):
        rand_cart.append(0)

    return rand_cart


def create_json_message(coordinates):

    timestamp = get_utc_timestamp()

    json_data = {
        "timestamp": timestamp,
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


def slave(client):
    client.subscribe(topic_master)
    coordinates = rc.read_current_cartesian_pose()
    message = create_json_message(coordinates)
    client.publish(topic_slave, message)


def master(client):
    client.subscribe(topic_slave)
    coordinates = rc.read_current_cartesian_pose()
    message = create_json_message(coordinates)
    client.publish(topic_master, message)


def main():
    client = paho.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(ipAddress, port)

    ## init ##

    while True:
        if not is_slave:
            master(client)
            time.sleep(1)

        if is_slave:
            slave(client)
            time.sleep(1)


main()


def old_code():
    client = paho.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(ipAddress, port)
    client.subscribe(topic_slave)

    counter = 0
    while counter <= 60:
        client.loop_start()
        time.sleep(1)
        client.loop_stop()
        counter += 1
