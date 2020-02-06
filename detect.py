# returns true if QR code is detected
# o.w. false
from pyzbar.pyzbar import decode
import pandas as pd
import cv2
import numpy as np
import queue
from param import *

SN = ""
camera_index = 2
def qrcodeReader():
    data = ""
    cap = cv2.VideoCapture(camera_index)

    ret, frame = cap.read()
    cv2.imshow("contour", frame)
    for i in range(20):
        
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        qrcodes = decode(image)
        # for decodedObject in qrcodes:
        #     print(decodedObject)
        #     points = decodedObject.polygon
        #     pts = np.array(points, np.int32)
        #     pts = pts.reshape((-1, 1, 2))
        #     cv2.polylines(image, [pts], True, (0, 255, 0), 3)
        data = map(lambda bc: bc.data.decode("utf-8"), qrcodes)
        data = list(data)
        print("i = %d" % i)
        if len(data) != 0:
            SN = data[0]
            print("serial number = {}".format(data[0]))
            return data[0]
    
    return False

# 2 scans
def scan_rotate(s):
    s.sendall(scan_pos.encode('ascii'))
    input("press anything when object is in place")
    detected = qrcodeReader()

    # Register "SN"
    if detected:
        return detected

    s.sendall(scan_pos_inv.encode('ascii'))
    input("press anything when object is in place")
    detected = qrcodeReader()
    return detected

def match2database(SN, actual_length):
    df = pd.read_csv("./obj_data/obj_info.csv")
    database_length = df.iloc[SN - 1][1:4].to_numpy()
    print("Matching database length: {}".format(database_length))
    #(a, b), (b, c), (a,c)
    actual_length = (max(actual_length), min(actual_length))
    print("actual: {}".format(actual_length))
    ab = abs(database_length[0] - actual_length[0]) + abs(database_length[1] - actual_length[1])
    bc = abs(database_length[1] - actual_length[0]) + abs(database_length[2] - actual_length[1])
    ac = abs(database_length[0] - actual_length[0]) + abs(database_length[2] - actual_length[1])
    print("(a,b) {}".format(ab))
    print("(b,c) {}".format(bc))
    print("(a,c) {}".format(ac))
    if ab <= bc and ab <= ac:
        return (database_length[0], database_length[1]), database_length[2]
    elif bc <= ab and bc <= ac:
        return (database_length[1], database_length[2]), database_length[0]
    elif ac <= bc and ac <= ab:
        return (database_length[0], database_length[2]), database_length[1]
    pass

# Exit : back to bar code scanning position
# Detecting barcode for 1 object
# actual_length -> (int, int)
def detect(i, s, actual_length):
    SN = ""
    face = (0, 0)
    grabbing = 0
    # First 2 scans
    SN = scan_rotate(s)
    if SN:
        SN = int(SN)
        face,_ = match2database(SN, actual_length)
        grabbing = max(face)
        print("SN is: {}".format(SN))
        s.sendall(scan_pos.encode('ascii')) # go to scan pos
        return face, grabbing, SN
    input()
    # If no QR code detected, grip the next 2 sides of the object
    s.sendall(man_pose_J.encode('ascii'))   # go to man_pose
    s.sendall(open_grip.encode('ascii'))        # open gripper
    input()
    s.sendall(rise_pose.encode('ascii'))  # rise 50mm
    s.sendall(Rotate_gripper_90.encode('ascii')) # rotate 90deg
    input()
    s.sendall(man_pose_inv.encode('ascii'))  # lower 50mm
    s.sendall(close_grip.encode('ascii'))       # close gripper
    input()
    SN = scan_rotate(s)
    if SN:
        SN = int(SN)
        face, _ = match2database(SN, actual_length)
        grabbing = min(face)
        print("SN is: {}".format(SN))
        s.sendall(scan_pos.encode('ascii')) # go to scan pos
        return face, grabbing, SN

    # If no QR code detected, do the roll manoeuver
    input()
    s.sendall(man_pose_J.encode('ascii'))
    input()
    s.sendall(open_grip.encode('ascii'))        # open gripper
    s.sendall(rise_pose.encode('ascii'))        # rise 1200mm

    input("stop here")
    s.sendall(temp_pose.encode('ascii'))        # go to temp pose (move back)
    input()
    s.sendall(woman_pose.encode('ascii'))       # go to woman pose (L shape)
    s.sendall(close_grip.encode('ascii'))        # close gripper

    input()
    SN = scan_rotate(s)
    SN = int(SN)
    face, grabbing = match2database(SN, actual_length)
    face = (max(face), grabbing)
    face = (max(face), min(face))

    print("SN is: {}".format(SN))
    input()
    s.sendall(scan_pos.encode('ascii')) # go to scan pos
    return face, grabbing, SN
    
