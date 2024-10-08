## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# CS553_DB_ASN5.py
#
# Dawson Burgess
# burg1648@vandals.uidaho.edu
# CS553 Robotics Systems Engineering 1
# Dr. Shovic
# Assignment 5:
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

# need for delay (which just makes program wait)
# import time

import random

import numpy as np

# this module imports source code needed to interface with robot API
import robot_controller as rc

# ip address to connect to robot
drive_path_beaker = "172.29.208.124"  # beaker
drive_path_bunsen = "172.29.208.123"
# set/connect to beaker robot
crx10_beaker = rc.robot(drive_path_beaker)
crx10_bunsen = rc.robot(drive_path_bunsen)

# set robot move speed to 200 mm/s
crx10_beaker.set_speed(200)
crx10_bunsen.set_speed(200)


def randomize_first_three(arr):
    if len(arr) < 6:
        raise valueError("array must have at least 6 elements.")

    # generate three random numbers from 0 to 150
    random_values = random.sample(range(151), 3)

    # replace the first three elements with the random values
    arr[:3] = random_values
    return arr


def rand_arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(0, 150))
    for i in range(n):
        rand_cart.append(0)

    return rand_cart


def main():

    # creating position registers dict
    # coords[x, y, z, w, p, r]
    # position_reg = {
    # "home" or init pos is p[1]
    p_home = [0, 0, 0, 0, -90, 30]
    dice = [15, 12, -60, -8, -23, 25]
    rough_mid_beak = [80, 20, -20, -1, 20, 30]
    rough_mid_buns = [-60, 20, -15, -60, 30, 80]
    mid_beak_cart = [302.053, 1172.618, 419.977, 93.418, -59.463, 179.56]
    mid_bun_cart = [316.293, -1077.254, 409.731, 87.81, -62.309, 2.94]
    mid_beak_offset = [-14.24, 2249.872, 10.246, 5.608, 2.846, 176.62]
    mid_bun_offset = [14.24, -2249.872, -10.246, -5.608, -2.846, -176.62]
    beak_safe_offset = [0, -300, 0, 0, 0, 0]
    bun_safe_offset = [0, 300, 0, 0, 0, 0]

    # }

    print("opening gripper tool")
    crx10_beaker.schunk_gripper("open")
    crx10_bunsen.schunk_gripper("open")

    # move to position 1 p[1], this is "home"
    print("moving to positon 1 p[1]: home")
    crx10_beaker.write_joint_pose(p_home)
    crx10_bunsen.write_joint_pose(p_home)

    # dice pickup
    print("beaker picking up die")
    crx10_beaker.write_joint_pose(dice)
    crx10_beaker.schunk_gripper("close")

    print("moving to positon  p[]: mid")
    crx10_beaker.write_joint_pose(rough_mid_beak)
    crx10_bunsen.write_joint_pose(rough_mid_buns)

    array1 = np.array(mid_beak_cart)
    array2 = np.array(mid_bun_offset)
    result = array1 + array2

    print("moving to middle position")
    crx10_beaker.write_cartesian_position(mid_beak_cart)
    crx10_bunsen.write_cartesian_position(result + bun_safe_offset)
    crx10_bunsen.write_cartesian_position(result - bun_safe_offset)

    print("moving to random position")
    rand_cart = rand_arr()

    array3 = np.array(rand_cart)
    new_rand_beak_cart = array1 + array3
    crx10_bunsen.write_cartesian_position(result + bun_safe_offset)
    crx10_beaker.write_cartesian_position(new_rand_beak_cart)
    crx10_bunsen.write_cartesian_position(
        new_rand_beak_cart + mid_bun_offset + bun_safe_offset
    )
    crx10_bunsen.write_cartesian_position(
        new_rand_beak_cart - mid_bun_offset - bun_safe_offset
    )


main()
