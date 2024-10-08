import robot_controller as rc

import numpy as np 
import random
import time

# ip address to connect to robot
drive_path_beaker = "172.29.208.124"  # beaker
drive_path_bunsen = "172.29.208.123"
# set/connect to beaker robot
crx10_beaker = rc.robot(drive_path_beaker)
crx10_bunsen = rc.robot(drive_path_bunsen)

# set robot move speed to 200 mm/s
crx10_beaker.set_speed(200)
crx10_bunsen.set_speed(200)


def main():
    home_beak_joint = [0, 0, 0, 0, -90, 30]
    home_bun_joint = [0, 0, 0, 0, -90, 30]
    #Homing Beaker and Bunsen
    print("HOMING Beaker and Bunsen")
    crx10_beaker.write_joint_pose(home_beak_joint)
    crx10_bunsen.write_joint_pose(home_bun_joint)
