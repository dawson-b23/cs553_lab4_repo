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

# this module imports source code needed to interface with robot API
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

def randomize_first_three(arr): 
    if len(arr) < 6: 
        raise ValueError("Array must have at least 6 elements.") 
    
    # Generate three random numbers from 0 to 150 
    random_values = random.sample(range(151), 3) 
   
    # Replace the first three elements with the random values 
    arr[:3] = random_values 
    return arr

def rand_Arr():
    rand_cart = []
    n = 3
    for i in range(n):
        rand_cart.append(random.randint(-150,150))
    for i in range(n):
        rand_cart.append(0)
        
    return rand_cart

def open_grippers():
    #Open Beaker and Bunsen Grippers
    print("Opening Gripper Tools")
    crx10_beaker.schunk_gripper("open")
    crx10_bunsen.schunk_gripper("open")

def home_joint(home_beak_joint, home_bun_joint):
    #Homing Beaker and Bunsen
    print("HOMING Beaker and Bunsen")
    crx10_beaker.write_joint_pose(home_beak_joint)
    crx10_bunsen.write_joint_pose(home_bun_joint)

def dice_beak_pickup(dice_cart_beak, dice_cart_beak_offset):
    #Beaker moving to dice cart coords and picking up dice
    print("Beaker picking up die")
    crx10_beaker.write_cartesian_position(dice_cart_beak_offset)
    crx10_beaker.write_cartesian_position(dice_cart_beak)
    crx10_beaker.schunk_gripper("close")
    time.sleep(0.5)

def bunsen_pass2_beaker(mid_bun_cart_arr, mid_beak_offset_arr, beak_safe_offset_arr):
    rand_pos_cart = rand_Arr()
    prev_beak_cart_list = crx10_beaker.read_current_cartesian_pose()
    prev_beak_cart_arr = np.array(prev_beak_cart_list)
    rand_pos_cart_arr = np.array(rand_pos_cart)
    new_rand_bun_cart_arr = mid_bun_cart_arr - rand_pos_cart_arr
    crx10_beaker.write_cartesian_position(prev_beak_cart_arr + beak_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_bun_cart_arr)
    crx10_beaker.write_cartesian_position(new_rand_bun_cart_arr+mid_beak_offset_arr+beak_safe_offset_arr)
    crx10_beaker.write_cartesian_position(new_rand_bun_cart_arr+mid_beak_offset_arr)
    crx10_beaker.schunk_gripper("close")
    time.sleep(0.5)
    crx10_bunsen.schunk_gripper("open")
    time.sleep(0.5)

def beaker_pass2_bunsen(mid_beak_cart_arr, mid_bun_offset_arr, bun_safe_offset_arr):
    rand_pos_cart = rand_Arr()
    prev_bun_cart_list = crx10_bunsen.read_current_cartesian_pose()
    prev_bun_cart_arr = np.array(prev_bun_cart_list)
    rand_pos_cart_arr = np.array(rand_pos_cart)
    new_rand_beak_cart_arr = mid_beak_cart_arr - rand_pos_cart_arr
    crx10_bunsen.write_cartesian_position(prev_bun_cart_arr + bun_safe_offset_arr)
    crx10_beaker.write_cartesian_position(new_rand_beak_cart_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_bun_offset_arr + bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_bun_offset_arr)
    crx10_bunsen.schunk_gripper("close")
    time.sleep(0.5)
    crx10_beaker.schunk_gripper("open")
    time.sleep(0.5)

def bunsen_take_beaker():
    crx10_bunsen.write_cartesian_position(prev_bun_cart_arr + bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_bun_offset_arr + bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart_arr + mid_bun_offset_arr)
    crx10_bunsen.schunk_gripper("close")
    time.sleep(0.5)

def main():
    # creating positions
    # coords[X, Y, Z, W, P, R]
    P_HOME_joint = [0, 0, 0, 0, -90, 30]
    home_beak_joint = [0, 0, 0, 0, -90, 30]
    home_bun_joint = [0, 0, 0, 0, -90, 30]
    dice_joint = [15, 12, -60, -8, -23, 25]
    dice_cart_beak = [474, -2.7, -181.07, 179.6, -1.15, 31.13]
    dice_cart_beak_offset = [474, -2.7, 0, 179.6, -1.15, 31.13]
    Rough_mid_beak =[80, 20, -20, -1, 20, 30]
    Rough_mid_buns = [-60, 20, -15, -60, 30, 80]
    Mid_beak_cart = [441.644, 1093.283, 372.238, 89.043, -59.973, -179.287]
    Mid_bun_cart = [446.390, -1133.883, 362.92, 89.691, -61.141, -1.357]
    #Mid_beak_offset = [-14.24, 2249.872, 10.246, 5.608, 2.846, 176.62]
    #Mid_bun_offset = [14.24, -2249.872, -10.246, -5.608, -2.846, -176.62]
    beak_safe_offset_arr = np.array([0, -300, 0, 0, 0, 0])
    bun_safe_offset_arr = np.array([0, 300, 0, 0, 0, 0])

    #creating offset arrays
    mid_beak_cart_arr = np.array(Mid_beak_cart)
    mid_bun_cart_arr = np.array(Mid_bun_cart)
    mid_beak_offset_arr = mid_beak_cart_arr - mid_bun_cart_arr
    mid_bun_offset_arr = mid_bun_cart_arr - mid_beak_cart_arr
    #result =  array1 + array2
    
    
    
    '''
    print("Moving to Middle Position")
    crx10_beaker.write_cartesian_position(Mid_beak_cart)
    crx10_bunsen.write_cartesian_position(result+bun_safe_offset)
    crx10_bunsen.write_cartesian_position(result)
    crx10_bunsen.schunk_gripper("close")
    time.sleep(0.5)
    crx10_beaker.schunk_gripper("open")
    time.sleep(0.5)
    '''
    
    '''
    print("Moving to Random Position")
    rand_pos_cart = rand_Arr()
    
    rand_pos_cart_arr = np.array(rand_cart)
    new_rand_beak_pos_cart_arr = mid_beak_cart_arr + rand_pos_cart_arr
    #crx10_bunsen.write_cartesian_position(result + bun_safe_offset)
    crx10_beaker.write_cartesian_position(new_rand_beak_pos_cart_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_pos_cart_arr+mid_bun_offset_arr+bun_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart+mid_bun_offset_arr)
    crx10_bunsen.schunk_gripper("close")
    time.sleep(0.5)
    crx10_beaker.schunk_gripper("open")
    time.sleep(0.5)

    rand_pos_cart = rand_Arr()
    #prev_beak_cart_list = crx10_beaker.read_current_cartesian_pose()
    prev_beak_cart_list = crx10_beaker.read_current_cartesian_pose()
    #prev_beak_cart = np.array(prev_beak_cart_list)
    prev_beak_cart_arr = np.array(prev_beak_cart_list)
    rand_pos_cart_arr = np.array(rand_pos_cart)
    new_rand_bun_cart_arr = mid_bun_cart_arr - rand_pos_cart_arr
    crx10_beaker.write_cartesian_position(prev_beak_cart_arr + beak_safe_offset_arr)
    crx10_bunsen.write_cartesian_position(new_rand_bun_cart_arr)
    crx10_beaker.write_cartesian_position(new_rand_bun_cart_arr+mid_beak_offset_arr+beak_safe_offset_arr)
    crx10_beaker.write_cartesian_position(new_rand_bun_cart_arr+mid_beak_offset_arr)
    crx10_beaker.schunk_gripper("close")
    time.sleep(0.5)
    crx10_bunsen.schunk_gripper("open")
    time.sleep(0.5)
    
    rand_cart = rand_Arr()
    #prev_beak_cart_list = crx10_beaker.read_current_cartesian_pose()
    prev_bun_cart_list = crx10_bunsen.read_current_cartesian_pose()
    #prev_beak_cart = np.array(prev_beak_cart_list)
    prev_bun_cart = np.array(prev_bun_cart_list)
    array3 = np.array(rand_cart)
    new_rand_beak_cart = array1 + array3
    crx10_bunsen.write_cartesian_position(prev_bun_cart + bun_safe_offset)
    crx10_beaker.write_cartesian_position(new_rand_beak_cart)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart+mid_bun_offset+bun_safe_offset)
    crx10_bunsen.write_cartesian_position(new_rand_beak_cart+mid_bun_offset)
    crx10_bunsen.schunk_gripper("close")
    time.sleep(0.5)
    crx10_beaker.schunk_gripper("open")
    time.sleep(0.5)

    # move to position 1 P[1], this is "home"
    print("Moving to positon 1 P[1]: HOME")
    crx10_beaker.write_joint_pose(home_beak_joint)
    crx10_bunsen.write_joint_pose(P_HOME_joint)
    '''
    
    
main()