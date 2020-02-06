import cv2
import numpy as np
import queue
from param import *
import pandas as pd
from helper import *

# grabbing (int, int)

def traceRoute(s, ind, SN, face, grabbing):
    # edges = [7, 5, 3], face = (7, 3), grabbing = 3
    df = pd.read_csv("./obj_data/obj_info.csv")
    edges = df.iloc[SN - 1][1:4].to_numpy()
    face = (max(face), min(face))
    
    
    if edges[0] == face[0] and edges[1] == face[1]:
        # 7 5
        if grabbing == face[0]:
            print("***** 1-1 *****")
            
            # grabbing 7
            # do nothing
        else:
            print("***** 1-2 *****")
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            
            # grabbing 5
            # release, rotate, grab
            pass
        
    elif edges[1] == face[0] and edges[2] == face[1]:
        # 53
        if grabbing == face[0]:
            print("***** 2-1 *****")
            # grabbing 5
            # rotate 90, release, woman pose, done
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(temp_pose.encode('ascii'))
            s.sendall(woman_pose.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            
            pass
        else:
            print("***** 2-2 *****")
            # grabbing 3
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(temp_pose.encode('ascii'))
            s.sendall(woman_pose.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            # release, rise, rotate, aprroach, grab, and do grabbing 5
            pass
    else:
        # 73
        if grabbing == face[0]:
            print("***** 3-1 *****")
            # grabbing 7
            # go to woman pose, grab 5, do grabbing 5
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(temp_pose.encode('ascii'))
            s.sendall(woman_pose.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(man_pose_J_adj.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv_adj.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            
        else:
            print("***** 3-2 *****")
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(temp_pose.encode('ascii'))
            s.sendall(woman_pose.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(man_pose_J_adj.encode('ascii'))
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv_adj.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            # grabbing 3
            # rotate to grab 7, do the rest as grabbing 7
            pass

def GetReady(s, SN, matching):
    # matching ['x', 'y', 'z']
    # saying a should match to x axis, and so on.
    # [a , b, c]
    size_of_box = GetSizeBySN(SN)
    return_matching = 0
    for i in range(len(matching)):
        if matching[i] == 'y':
            return_matching = size_of_box[i]
    print("size of box {} matching: {} return_matching: {}".format(size_of_box, matching, return_matching))
    if matching[2] == 'z':
        # easiest part
        if matching[0] == 'y':
            # no rotation
            print("rotate 90")
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv_adj.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            pass
        else:
            # rotate 90
            print("easiest, no rotation\n Done!.")
            
            
            pass
        s.sendall(rise_pose.encode('ascii'))
        # go to packing pose
    elif matching[0] == 'z':
        # go to woman pose
        # release, man pose
        s.sendall(rise_pose.encode('ascii'))
        s.sendall(temp_pose.encode('ascii'))
        s.sendall(woman_pose.encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall(temp_pose.encode('ascii'))
        
        if matching[1] == 'x':
            # no rotation
            s.sendall(man_pose_J.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv.encode('ascii'))
            
            print("z x")
            pass
        else:
            s.sendall(man_pose_J.encode('ascii'))
            # rotate 90
            print("z x 90")
            pass
        s.sendall(close_grip.encode('ascii'))
        s.sendall(rise_pose.encode('ascii'))
        # go to packing pose
    else:
        # go to man pose
        s.sendall(Rotate_gripper_90.encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall(rise_pose.encode('ascii'))
        s.sendall(temp_pose.encode('ascii'))
        s.sendall(woman_pose.encode('ascii'))
        s.sendall(close_grip.encode('ascii'))
        s.sendall(temp_pose.encode('ascii'))
        s.sendall(man_pose_J.encode('ascii'))
        
        # rotate 90
        # woman pose
        if matching[0] == 'x':
            # do nothing
            
            print("x z")
            s.sendall(open_grip.encode('ascii'))
            s.sendall(rise_pose.encode('ascii'))
            s.sendall(Rotate_gripper_90.encode('ascii'))
            s.sendall(man_pose_inv.encode('ascii'))
            s.sendall(close_grip.encode('ascii'))
            
            pass
        else:
            # rotate 90
            print("x z 90")
            
            pass
        # go to packing pose.

        s.sendall(rise_pose.encode('ascii'))
    return return_matching