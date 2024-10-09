import json
import random
from datetime import datetime
import numpy as np
import time

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
# drive_path_bunsen = "172.29.208.123"  # bunsen
# crx10_bunsen = rc.robot(drive_path_bunsen)
# crx10_bunsen.set_speed(200)
drive_path_bunsen = "172.29.208.123"  # bunsen
crx10_bunsen = rc.robot(drive_path_bunsen)
crx10_bunsen.set_speed(300)

handoff_count = 0
max_handoffs = 6  # Can be 7-10 times

home_bun_joint = [0, 0, 0, 0, -90, 30]
Mid_beak_cart = [441.644, 1098.283, 372.238, 89.043, -59.973, -179.287]
Mid_bun_cart = [446.390, -1133.883, 362.92, 89.691, -61.141, -1.357]
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
    # Homing Bunsen
    print("HOMING Bunsen")
    crx10_bunsen.write_joint_pose(home_bun_joint)


def open_grippers():
    # Open Bunsen Gripper
    print("Opening Gripper Tools")
    crx10_bunsen.schunk_gripper("open")

def bunsen_take_beaker(new_rand_beak_cart_arr):
    global handoff_count
    prev_bun_cart = crx10_bunsen.read_current_cartesian_pose()
    prev_bun_cart_arr = np.array(prev_bun_cart)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_beak_cart_arr + mid_bun_offset_arr + bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_beak_cart_arr + mid_bun_offset_arr)

def bunsen_pass_to_beaker(rand_arr):
    crx10_bunsen.write_cartesian_position(mid_bun_cart_arr+rand_arr)

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

    client.subscribe(topic_beaker)


def on_message(client, userdata, message):
    global has_dice, gripper_closed, handoff_count, max_handoffs
    message_json = json.loads(message.payload.decode("utf-8"))
    print(f"Bunsen received message: {message_json}")

    if not has_dice and "location" in message_json:
        # Beaker sent its location, Bunsen moves to that location
        location = message_json["location"]
        print(f"Bunsen moving to meet Beaker at location: {location}")
        new_rand_location_arr = np.array(location)
        bunsen_take_beaker(new_rand_location_arr)  #insert random array
        crx10_bunsen.schunk_gripper("close")
        time.sleep(0.5)
        gripper_closed = True  # Bunsen closes gripper to receive dice
        send_gripper_status(
            client, topic_bunsen, "bunsen", gripper_closed
        )  # Notify Beaker
        has_dice = True
        

    elif has_dice and not message_json.get("gripper_closed"):
        # Beaker's gripper is open, Bunsen can now move to the next location with the dice
        print(
            "Beaker opened its gripper. Bunsen taking the dice and moving to a new location."
        )
        has_dice = True
        #gripper_closed = False  # Open gripper for next handoff
        location = rand_arr()
        bunsen_pass_to_beaker(location)
        send_location(client, topic_bunsen, "bunsen", location)

    elif has_dice and message_json.get("gripper_closed"):
        
        print("Bunsen has closed gripper, opening gripper")
        crx10_bunsen.schunk_gripper("open")
        #time.sleep(0.5)
        gripper_closed = False
        crx10_bunsen.write_cartesian_position(np.array(crx10_bunsen.read_current_cartesian_pose())+bun_safe_offset_arr)
        send_gripper_status(
            client, topic_bunsen, "bunsen", gripper_closed
        )  # Notify Beaker
        has_dice = False
        #time.sleep(1)
        handoff_count += 1
        print(f"handoff_count: {handoff_count}\n")
        if handoff_count > max_handoffs:
            #crx10_bunsen.schunk_gripper("open")
            home_joint()
            print("Program done, Goodbye!")
            client.disconnect()
            return
        
            



def main_bunsen():
    client = mqtt.Client()
    open_grippers()
    home_joint()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(ipAddress, port)

    client.loop_forever()


if __name__ == "__main__":
    main_bunsen()
