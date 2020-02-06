import numpy as np
import math

# Serial number
SN = ''
number_of_objects = 3
# Each of inter_pos's elem is a command to move to inter_pos[i]

scan_pos = 'MOVJ -2.5 -3.8 -24.6 9.9 26.7 -8.7\n'
scan_pos_inv = 'MOVJ # # # # # 171.3\n'

inter_pos = ['MOVP -558 -72 -180 0 0 180\n',
            'MOVP -558 38 -180 0 0 180\n',
            'MOVP -558 148 -180 0 0 180\n',
            'MOVP -351 -72 -180 0 0 180\n',
            'MOVP -351 38 -180 0 0 180\n',
            'MOVP -351 148 -180 0 0 180\n']
inter_pos_rise = ['MOVP -558 -72 0 0 0 180\n',
            'MOVP -558 38 0 0 0 180\n',
            'MOVP -558 148 0 0 0 180\n',
            'MOVP -351 -72 0 0 0 180\n',
            'MOVP -351 38 0 0 0 180\n',
            'MOVP -351 148 0 0 0 180\n']


man_pose_J = "MOVJ 40.5 -80.67 39.48 0 -48.24 175.24\n"
man_pose_inv = "MOVJ 40.5 -80.67 39.44 0 -48.27 #\n"
Rotate_gripper_90 = "MOVJ # # # # # 85.25\n"
rise_pose = "MOVP # # -50 # # #\n"
temp_pose = "MOVJ 40.5 -33.8 -22.15 0 -33.53 179.26\n"
woman_pose = 'MOVJ 38.99 -77.32 -10.49 -5.11 79.82 179.29\n'

close_grip = 'OUTPUT 48 ON\n'
open_grip = 'OUTPUT 48 OFF\n'

# 7x5x2