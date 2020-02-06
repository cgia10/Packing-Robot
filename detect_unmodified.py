# returns true if QR code is detected
# o.w. false
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import queue
from param import *

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
        for decodedObject in qrcodes:
            points = decodedObject.polygon
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(image, [pts], True, (0, 255, 0), 3)
        data = map(lambda bc: bc.data.decode("utf-8"), qrcodes)
        data = list(data)
        print("i = %d" % i)
        if len(data) != 0:
            SN = data[0]
            print("serial number = {}".format(data[0]))
            return True
    
    return False

# 2 scans
def scan_rotate(s):
    s.sendall(scan_pos.encode('ascii'))
    input("press anything when object is in place")
    detected = qrcodeReader()

    # Register "SN"
    if detected:
        return True

    s.sendall(scan_pos_inv.encode('ascii'))
    input("press anything when object is in place")
    detected = qrcodeReader()
    return detected

# Exit : back to bar code scanning position
# Detecting barcode for 1 object
def detect(i, s):
    global SN
    SN = ""
    face = (0, 0)
    grabbing = 0
    # First 2 scans
    if scan_rotate(s):

        return face, grabbing
        pass
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
    if scan_rotate(s):
        return face, grabbing
        pass

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
    scan_rotate(s)
    
    return face, grabbing