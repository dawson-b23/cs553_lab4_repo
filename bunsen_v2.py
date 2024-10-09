import json
import random
from datetime import datetime

import paho.mqtt.client as mqtt

import robot_controller as rc

## Globals
ipAddress = "172.29.208.119"
port = 1883
topic_beaker = "robot/beaker"
topic_bunsen = "robot/bunsen"

# ip address to connect to robot
# ip address to connect to robot
# drive_path_bunsen = "172.29.208.123"
# crx10_bunsen = rc.robot(drive_path_bunsen)
# crx10_bunsen.set_speed(200)


def get_random_location():
    """Generate a random location for the robot to move to."""
    return {"x": random.randint(0, 10), "y": random.randint(0, 10)}


def get_utc_timestamp():
    """Create a UTC timestamp."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


class Robot:
    def __init__(self, name, initial_role, client, publish_topic, subscribe_topic):
        self.name = name
        self.has_dice = initial_role  # True if the robot starts with the dice
        self.client = client
        self.publish_topic = publish_topic
        self.subscribe_topic = subscribe_topic

    def on_connect(self, client, userdata, flags, rc):
        print(f"{self.name} connected to MQTT broker with result code {rc}")
        # Subscribe to the other robot's location topic
        client.subscribe(self.subscribe_topic)

    def on_message(self, client, userdata, message):
        """Handle incoming messages (locations from the other robot)."""
        message_json = json.loads(message.payload.decode("utf-8"))
        print(f"{self.name} received message: {message_json}")

        if not self.has_dice:
            # If the robot is the follower (without dice), move to the location
            location = message_json["location"]
            print(f"{self.name} moving to location: {location}")

            # Simulate "moving" and sending confirmation
            self.send_confirmation(location)

            # Now this robot has the dice
            self.has_dice = True
        else:
            # If the robot already has the dice, it means the other robot has reached
            print(f"{self.name} has the dice back. Ready to send a new location.")
            # Switch role to dice holder and send a new location
            self.send_location()

    def send_location(self):
        """Send a random location to the other robot."""
        location = get_random_location()
        message = {
            "robot": self.name,
            "location": location,
            "timestamp": get_utc_timestamp(),
        }
        self.client.publish(self.publish_topic, json.dumps(message))
        print(f"{self.name} sent location: {location}")

        # Once sent, this robot no longer has the dice
        self.has_dice = False

    def send_confirmation(self, location):
        """Send confirmation after reaching the location."""
        message = {
            "robot": self.name,
            "location": location,
            "timestamp": get_utc_timestamp(),
        }
        self.client.publish(self.publish_topic, json.dumps(message))
        print(f"{self.name} sent confirmation: {location}")

    def start(self):
        """Connect to MQTT and start the loop."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("mqtt-broker-ip", 1883, 60)
        if self.has_dice:
            # If starting with dice, immediately send a location
            self.send_location()
        self.client.loop_forever()


def robot_bunsen():
    client = mqtt.Client()
    bunsen = Robot(
        name="robot1",
        initial_role=False,
        client=client,
        publish_topic=topic_beaker,
        subscribe_topic=topic_bunsen,
    )
    bunsen.start()


if __name__ == "__main__":
    robot_bunsen()
