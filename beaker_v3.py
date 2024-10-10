import json
import random
import time
from datetime import datetime

import numpy as np
import paho.mqtt.client as mqtt

import robot_controller as rc

## Globals
ipAddress = "172.29.208.119"
port = 1883
topic_beaker = "robot/beaker"
topic_bunsen = "robot/bunsen"
has_dice = True
gripper_closed = True  # Beaker starts with an open gripper

# ip address to connect to robot
drive_path_beaker = "172.29.208.124"  # beaker
crx10_beaker = rc.robot(drive_path_beaker)  # set/connect to beaker robot
crx10_beaker.set_speed(300)  # set robot move speed to 200 mm/s


handoff_count = 0
max_handoffs = 6  # Can be 7-10 times


home_beak_joint = [0, 0, 0, 0, -90, 30]
dice_cart_beak = [474, -2.7, -181.07, 179.6, -1.15, 31.13]
dice_cart_beak_offset = [474, -2.7, 0, 179.6, -1.15, 31.13]
Mid_beak_cart = [441.644, 1098.283, 372.238, 89.043, -59.973, -179.287]
Mid_bun_cart = [446.390, -1133.883, 362.92, 89.691, -61.141, -1.357]
beak_safe_offset_arr = np.array([0, -300, 0, 0, 0, 0])
bun_safe_offset_arr = np.array([0, 300, 0, 0, 0, 0])

mid_beak_cart_arr = np.array(Mid_beak_cart)
mid_bun_cart_arr = np.array(Mid_bun_cart)
mid_beak_offset_arr = mid_beak_cart_arr - mid_bun_cart_arr
mid_bun_offset_arr = mid_bun_cart_arr - mid_beak_cart_arr


def rand_arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(-150, 150))
    for i in range(n):
        rand_cart.append(0)

    rand_cart = np.array(rand_cart)
    return rand_cart


def home_joint():
    # Homing Beaker and Bunsen
    print("HOMING Beaker")
    crx10_beaker.write_joint_pose(home_beak_joint)


def open_grippers():
    # Open Beaker and Bunsen Grippers
    print("Opening Gripper Tools")
    crx10_beaker.schunk_gripper("open")


def dice_beak_pickup():
    # Beaker moving to dice cart coords and picking up dice
    print("Beaker picking up die")
    crx10_beaker.write_cartesian_position(dice_cart_beak_offset)
    crx10_beaker.write_cartesian_position(dice_cart_beak)
    crx10_beaker.schunk_gripper("close")
    gripper_closed = True
    time.sleep(0.5)


def put_dice_down():
    print("putting dice down")
    crx10_beaker.write_cartesian_position(dice_cart_beak_offset)
    crx10_beaker.write_cartesian_position(dice_cart_beak)
    crx10_beaker.schunk_gripper("open")
    time.sleep(1)
    home_joint()


def beaker_pass_to_bunsen(rand_arr):
    crx10_beaker.write_cartesian_position(mid_beak_cart_arr + rand_arr)


def beaker_take_bunsen(rand_arr):
    global handoff_count
    crx10_beaker.write_cartesian_position(
        rand_arr + mid_bun_cart_arr + mid_beak_offset_arr + beak_safe_offset_arr
    )
    crx10_beaker.write_cartesian_position(
        rand_arr + mid_bun_cart_arr + mid_beak_offset_arr
    )


def get_utc_timestamp():
    # Create a UTC timestamp.
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def send_location(client, publish_topic, robot_name, location):
    # Send the location and gripper status to the other robot.
    message = {
        "robot": robot_name,
        "location": location.tolist(),
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

    client.subscribe(topic_bunsen)


def on_message(client, userdata, message):
    global has_dice, gripper_closed, handoff_count
    message_json = json.loads(message.payload.decode("utf-8"))
    print(f"Beaker received message: {message_json}")

    if not has_dice and "location" in message_json:
        # Bunsen sent a location
        location = message_json["location"]
        print(f"Beaker moving to meet Bunsen at location: {location}")
        arr = np.array(location)
        beaker_take_bunsen(arr)
        crx10_beaker.schunk_gripper("close")
        time.sleep(0.5)
        gripper_closed = True
        send_gripper_status(
            client, topic_beaker, "beaker", gripper_closed
        )  # Beaker signals it's closing gripper
        handoff_count += 1
        print(f"handoff_count: {handoff_count}\n")
        has_dice = True  # Beaker takes the dice again

    elif has_dice and not message_json.get("gripper_closed"):
        if handoff_count > max_handoffs:
            print(
                "Beaker has completed 7-10 handoffs and is now putting the dice down."
            )
            put_dice_down()
            print("Program done, goodbye!")
            return

        print("Bun open grip. Beak take dice and move")
        location = rand_arr()
        beaker_pass_to_bunsen(location)
        send_location(client, topic_beaker, "beaker", location)

    elif has_dice and message_json.get("gripper_closed"):
        # Bunsen's gripper is closed, Beaker can release the dice
        print("Bunsen's gripper is closed. Beaker opening gripper to release the dice.")
        crx10_beaker.schunk_gripper("open")
        gripper_closed = False  # Beaker opens gripper
        has_dice = False  # Dice handed over
        send_gripper_status(client, topic_beaker, "beaker", gripper_closed)
        print("Dice released.")
        current_cart_pos = np.array(crx10_beaker.read_current_cartesian_pose())
        crx10_beaker.write_cartesian_position(current_cart_pos + beak_safe_offset_arr)


def main_beaker():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    home_joint()
    open_grippers()
    dice_beak_pickup()
    client.connect(ipAddress, port)

    # Beaker picks up the dice and moves to the first location
    location = rand_arr()
    beaker_pass_to_bunsen(location)
    send_location(client, topic_beaker, "beaker", location)

    client.loop_forever()


if __name__ == "__main__":
    main_beaker()
