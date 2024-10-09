import json
import random
from datetime import datetime

import paho.mqtt.client as mqtt

import robot_controller as rc

# Globals
# Dawson IP
ipAddress = "172.29.208.119"
# Levi IP
# ipAddress = "192.168.1.120"
port = 1883
topic_beaker = "robot/beaker"
topic_bunsen = "robot/bunsen"
has_dice = False
gripper_closed = False  # Beaker starts with an open gripper

# ip address to connect to robot
<<<<<<< Updated upstream
# drive_path_bunsen = "172.29.208.123"  # bunsen
# crx10_bunsen = rc.robot(drive_path_bunsen)
# crx10_bunsen.set_speed(200)
=======
drive_path_bunsen = "172.29.208.123"  # bunsen
crx10_bunsen = rc.robot(drive_path_bunsen)
crx10_bunsen.set_speed(200)
>>>>>>> Stashed changes

handoff_count = 0
max_handoffs = 7  # Can be 7-10 times


def rand_arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(-150, 150))
    for i in range(n):
        rand_cart.append(0)

    return rand_cart


def get_utc_timestamp():
    # Create a UTC timestamp.
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def send_location(client, publish_topic, robot_name, location):
    # Send the location and gripper status to the other robot.
    message = {
        "robot": robot_name,
        "location": location,
        "timestamp": get_utc_timestamp(),
        "gripper_closed": False,  # Initially open when moving
    }
    client.publish(publish_topic, json.dumps(message))
    print(f"{robot_name} sent location: {location}")


def send_gripper_status(client, publish_topic, robot_name, gripper_closed):
    # Send gripper status update to the other robot.
    message = {
        "robot": robot_name,
        "gripper_closed": gripper_closed,
        "timestamp": get_utc_timestamp(),
    }
    client.publish(publish_topic, json.dumps(message))
    print(f"{robot_name} sent gripper status: {gripper_closed}")


def on_connect(client, userdata, flags, returnCode):
    if returnCode == 0:
        print("Connection Successful.....")
    else:
        print(f"Connection Error: {str(returnCode)}")

    client.subscribe(topic_beaker)


def on_message(client, userdata, message):
    global has_dice, gripper_closed
    message_json = json.loads(message.payload.decode("utf-8"))
    print(f"Bunsen received message: {message_json}")

    if not has_dice and "location" in message_json:
        # Beaker sent its location, Bunsen moves to that location
        location = message_json["location"]
        print(f"Bunsen moving to meet Beaker at location: {location}")

        gripper_closed = True  # Bunsen closes gripper to receive dice
        send_gripper_status(
            client, topic_bunsen, "bunsen", gripper_closed
        )  # Notify Beaker

    elif has_dice and message_json.get("gripper_closed"):
        # Beaker's gripper is open, Bunsen can now move to the next location with the dice
        print(
            "Beaker opened its gripper. Bunsen taking the dice and moving to a new location."
        )
        has_dice = True
        gripper_closed = False  # Open gripper for next handoff
        location = rand_arr()
        send_location(client, topic_bunsen, "bunsen", location)


def main_bunsen():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(ipAddress, port)

    client.loop_forever()


if __name__ == "__main__":
    main_bunsen()
