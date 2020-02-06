from pyzbar.pyzbar import decode
import cv2
import numpy as np

camera_index = 2

def qrcodeReader(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    qrcodes = decode(image)
    for decodedObject in qrcodes:
        print(decodedObject)
        points = decodedObject.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)
    data = map(lambda bc: bc.data.decode("utf-8"), qrcodes)
    return list(data)


cap = cv2.VideoCapture(camera_index)

while True:
    ret, frame = cap.read()
    qrcode = qrcodeReader(frame)
    print(qrcode)
    cv2.imshow('qrcode reader', frame)
    code = cv2.waitKey(1)
    if code == ord('q'):
        break
