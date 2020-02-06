import socket
import sys
import numpy as np
import cv2
import math
from image import take_pictures, mapping
from connect import connect2Arm
from detect import *
from trace import *
from helper import *
from packing_gurobi import *

# json implementation, fast
# import json
# f =  open('./obj_data/obj_info.json')
# data = json.load(f)
# f.close()

# csv implementation, clear
# import pandas as pd
# df = pd.read_csv('./obj_data/obj_info.csv', index_col=0)
# print(df['weight'][1]) # 20


A = np.load('./calibration_data/img2actual.npy')
pixel2mm = np.load('./calibration_data/pixel2mm.npy')

number_of_objects = 1
step_by_step = True




def checkPoint(val):
    if step_by_step:
        print(val)
        input()


if __name__ == "__main__":
    pixel2mm -= 0.1
    mc, p_angle, bbox, actual_length_box = take_pictures()
    print(bbox)

    s = connect2Arm()
    inter_pose_register = {}
    xs = []; ys = []; zs = []
    number_of_objects = len(mc)
    isCube = []
    print("Object count: {}".format(number_of_objects))
    for i in range(0, number_of_objects):
        
        # compute the actual position
        img_p = [[mc[i][0]], [mc[i][1]], [1]]
        p_hat = np.matmul(A, img_p)
        p_hat = np.reshape(p_hat, 3)

        # move above the target
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' 0 ' + str(-p_angle[i]) + ' 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # move down to reach the target
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' -190 ' + str(-p_angle[i]) + ' 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # close the gripper
        s.sendall(close_grip.encode('ascii'))
        

        face, grabbing, SN = detect(i, s, actual_length_box[i])
        inter_pose_register[i] = SN
        object_size = GetSizeBySN(SN)
        xs.append(object_size[0]); ys.append(object_size[1]); zs.append(object_size[2])
        print("face: {} grabbing {}".format(face, grabbing))
        if SN not in [18, 19, 10 , 11]:
            traceRoute(s,i, SN, face, grabbing)
        
        # ==========================================
        # ReCalibrating the centroid of object 
        # with the manipulator
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' 0 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
         # move down to reach the target
        
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' -200 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        input()
        s.sendall(open_grip.encode('ascii'))
        s.sendall("GOHOME\n".encode('ascii'))
        s.sendall("MOVJ # # # # # 0\n".encode('ascii'))
        input("press enter when arm is at home")
        mc_temp, p_angle__ , bbox__, actual__ = take_pictures()

        for centroid in mc_temp:

            img_p = [[centroid[0]], [centroid[1]], [1]]
            actual_p = np.matmul(A, img_p)
            actual_p = np.reshape(actual_p, 3)
            x = actual_p[0]
            y = actual_p[1]
            dist = np.sqrt( (p_hat[0] - x)**2 + (p_hat[1] - y)**2)
            if dist < 20:
                p_hat[0] = x
                p_hat[1] = y
                break
        # ==========================================
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' 0 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # move down to reach the target
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' -205 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # close the gripper
        s.sendall(close_grip.encode('ascii'))
        s.sendall(rise_pose.encode('ascii'))
        s.sendall(inter_pos_rise[i].encode('ascii'))
        s.sendall(inter_pos[i].encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall(inter_pos_rise[i].encode('ascii'))
        s.sendall("GOHOME\n".encode('ascii'))

        

    packing_result = packing(container_size, [xs, ys, zs],True, True)
    # packing result returns
    # index of interpose, (x, y, z), mapping for a, b, c to which axis.
    # 3 1.0 10.5 0.0 ['y', 'x', 'z']
    # 0 1.5 13.5 0.0 ['z', 'y', 'x']
    print("******** PACKING RESULT ************")
    for i in packing_result:
        print(i)
    s.sendall(inter_pos_general.encode('ascii'))
    input("****** Intermediate phase completed!...")
    
    for item in packing_result:
        
        s.sendall(inter_pos_general.encode('ascii'))
        seq, packing_x, packing_y, packing_z, [o1, o2, o3] = item
        s.sendall(inter_pos_rise[seq].encode('ascii'))
        s.sendall(inter_pos[seq].encode('ascii'))
        # ======================================================== manipulate the object
        # man pose here
        block_size = 0
        s.sendall(close_grip.encode('ascii'))
        s.sendall(rise_pose.encode('ascii'))
        
        input("Get ready.....")
        if inter_pose_register[seq] not in [18, 19, 10, 11]:
            s.sendall(temp_pose.encode('ascii'))
            s.sendall(man_pose_J_adj.encode('ascii'))
            
            block_size = GetReady(s, inter_pose_register[seq], [o1, o2, o3])
        # ======================================================== calibrate
        else:
            block_size = 50

        # ReCalibrating the centroid of object 
        # with the manipulator
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' 0 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
         # move down to reach the target
        
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' -190 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall("GOHOME\n".encode('ascii'))
        s.sendall("MOVJ # # # # # 0\n".encode('ascii'))
        input("press enter when arm is at home")
        mc_temp, p_angle__ , bbox__, actual__ = take_pictures()

        for centroid in mc_temp:

            img_p = [[centroid[0]], [centroid[1]], [1]]
            actual_p = np.matmul(A, img_p)
            actual_p = np.reshape(actual_p, 3)
            x = actual_p[0]
            y = actual_p[1]
            dist = np.sqrt( (p_hat[0] - x)**2 + (p_hat[1] - y)**2)
            if dist < 20:
                p_hat[0] = x
                p_hat[1] = y
                break
        # ==========================================
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' 0 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # move down to reach the target
        val = 'MOVP ' + str(p_hat[0]) + ' ' + str(p_hat[1]) + ' -200 ' + '90 0 180\n'
        checkPoint(val)
        s.sendall(val.encode('ascii'))
        

        # close the gripper
        s.sendall(close_grip.encode('ascii'))
        s.sendall(rise_pose.encode('ascii'))
        
        # # packing pose
        s.sendall("MOVP {} {} 0 -0.54 2.69 -178.876\n".format(packing_pose_x + packing_x, packing_pose_y + packing_y + 180).encode('ascii'))
        s.sendall(packing_pose.format(packing_pose_x + packing_x, packing_pose_y + packing_y + 180).encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall(close_grip.encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        input()
        s.sendall(rise_packing.encode('ascii'))
        # s.sendall(close_grip.encode('ascii'))
        input()
        s.sendall(packing_pose.format(packing_pose_x + packing_x, packing_pose_y + packing_y + 260).encode('ascii'))
        input("block size is: {}".format(block_size))
        s.sendall("SETPTPSPEED 3\n".encode('ascii'))
        s.sendall("SETLINESPEED 20\n".encode('ascii'))
        input()
        s.sendall(packing_pose.format(packing_pose_x + packing_x, packing_pose_y + packing_y + block_size/2 + 40).encode('ascii'))

        s.sendall("SETPTPSPEED 15\n".encode('ascii'))
        s.sendall("SETLINESPEED 35\n".encode('ascii'))
        input()
        s.sendall(rise_packing.encode('ascii'))
        s.sendall(open_grip.encode('ascii'))
        s.sendall("GOHOME\n".encode('ascii'))
        # # pushing pose
        # # push
        # # GOHOME
        # input("")
    

    # go home
    go_home = 'GOHOME\n'
    s.sendall(go_home.encode('ascii'))
    s.sendall(open_grip.encode('ascii'))
    s.close()
