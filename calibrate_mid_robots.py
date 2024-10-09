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
    print("Moving Beaker and Bunsen to calibation positions")
    mid_beak_cart = [441.644, 1093.283, 372.238, 89.043, -59.973, -179.287]
    mid_bun_cart = [446.390, -1133.883, 362.92, 89.691, -61.141, -1.357]
    beak_safe_offset_arr = np.array([0, -300, 0, 0, 0, 0])
    bun_safe_offset_arr = np.array([0, 300, 0, 0, 0, 0])
    mid_beak_cart_arr = np.array(mid_beak_cart)
    mid_bun_cart_arr = np.array(mid_bun_cart)
    crx10_beaker.write_cartesian_position(mid_beak_cart_arr)
    crx10_bunsen.write_cartesian_position(mid_bun_cart_arr + bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(mid_bun_cart_arr)

main()