import socket
import sys
import numpy as np
import cv2
import time
from image import take_pictures, mapping
from connect import connect2Arm

if __name__ == "__main__":

    # [[x, y], [x, y], [x, y]]
    actual_pos = np.array([[-100.0, 380.0], [200.0, 550.0], [100.0, 400.0]])
    img_pos = np.zeros([3, 2])
    s = connect2Arm()

    for i in range(3):

        # move to position
        action = 'MOVP ' + str(actual_pos[i, 0]) + ' ' + str(actual_pos[i, 1]) + ' -170 90 0 180'
        s.sendall(action.encode('ascii'))

        # place the item
        print('Please place the object in the gripper.')
        input('Press any key to continue.')

        # home
        go_home = 'GOHOME'
        s.sendall(go_home.encode('ascii'))
        time.sleep(5)

        # get centroid, store in img_pos
        mc, p_angle = take_pictures()
        img_pos[i, 0] = mc[0][0]
        img_pos[i, 1] = mc[0][1]
        print('mc for calibration: ', img_pos[i, 0], ', ', img_pos[i, 1])
        print('Please remove the object.')
        input('Press any key to continue.')
    
    s.close()

    # compute image pixel to real world mm
    pixel2mm = []
    for [i, j] in [[0, 1], [0, 2], [1, 2]]:
        actual_dis = np.linalg.norm(actual_pos[i] - actual_pos[j])
        img_dis = np.linalg.norm(img_pos[i] - img_pos[j])
        pixel2mm.append(actual_dis / img_dis)
        print(actual_dis / img_dis)
    pixel2mm = sum(pixel2mm) / len(pixel2mm)
    np.save('./calibration_data/pixel2mm.npy', pixel2mm)
    print("pixel2mm: ", pixel2mm)
    print('\'./calibration_data/pixel2mm.npy\' saved')

    # compute and store the mapping matrix
    img2actual = mapping(actual_pos, img_pos)
    np.save('./calibration_data/img2actual.npy', img2actual)
    print('img2actual: ', img2actual)
    print('\'./calibration_data/img2actual.npy\' saved')
    
