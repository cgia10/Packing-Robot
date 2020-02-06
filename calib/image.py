import numpy as np
import cv2
import math

ratio = np.load('./calibration_data/pixel2mm.npy')

camera_index = 2


def distance (x, y, a, b):
    return np.sqrt((x - a) ** 2 + (y-b)**2)


def take_pictures():
    cap = cv2.VideoCapture(camera_index)

    while 1:
        # Capture frame-by-frame
        ret, image = cap.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        cv2.imshow('raw', gray)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY, gray)
        done = cv2.morphologyEx(gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)))
        edges = cv2.Canny(gray, 100, 200)

        # Display the resulting frame
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_filtered = []

        # Filter out large contours
        for i in contours:
            if len(i) > 20:
                contours_filtered.append(i)

        mu = [None]*len(contours_filtered)
        mc = [None]*len(contours_filtered)

        # Moments
        for i in range(len(contours_filtered)):
            mu[i] = cv2.moments(contours_filtered[i])

        # Get the mass centers
        for i in range(len(contours_filtered)):
            if cv2.arcLength(contours_filtered[i], True) < 20:
                continue
            # add 1e-5 to avoid division by zero
            mc[i] = (mu[i]['m10'] / (mu[i]['m00'] + 1e-5), mu[i]['m01'] / (mu[i]['m00'] + 1e-5))


        # Check duplicates
        # Filter moments and centroids
        mu_filtered = []
        mc_filtered = []
        contours_filterered = []

        for i in range(len(contours_filtered)):
            pushable = True
            for j in range(len(contours_filterered)):
                if distance(mc[i][0], mc[i][1], mc_filtered[j][0], mc_filtered[j][1]) < 30:
                    pushable = False
                    break
            if pushable:
                contours_filterered.append(contours_filtered[i])
                mu_filtered.append(mu[i])
                mc_filtered.append(mc[i])


        drawing = np.zeros((edges.shape[0],edges.shape[1], 3), dtype=np.uint8)
        principal_angle = []
        bounding_boxes = []
        actual_legnth_of_boxes = []
        for i in range(len(contours_filterered)):
            # Draw contours
            color = (np.random.randint(0,256), np.random.randint(0,256), np.random.randint(0,256))
            cv2.drawContours(drawing, contours_filterered, i, color, 2)
            bound_rect = cv2.minAreaRect(contours_filterered[i])
            
            bound_4 = cv2.boxPoints(bound_rect)
            bound_4_len = np.linalg.norm(bound_4[0] - bound_4[1]), np.linalg.norm(bound_4[1] - bound_4[2])
            bounding_boxes.append(bound_4)
            print(bound_4)
            actual_bound = bound_4_len * ratio
            actual_legnth_of_boxes.append(actual_bound)
            print("length of bounding box: ", bound_4_len)
            print("actual length: ", actual_bound)

            cv2.circle(drawing, (int(mc_filtered[i][0]), int(mc_filtered[i][1])), 4, color, -1)
            # Principal angle
            num = 2 * (mu_filtered[i]['m00'] * mu_filtered[i]['m11'] -mu_filtered[i]['m10'] *mu_filtered[i]['m01'])
            denom = ((mu_filtered[i]['m00'] *mu_filtered[i]['m20'] -mu_filtered[i]['m10'] *mu_filtered[i]['m10']) - (mu_filtered[i]['m00'] *mu_filtered[i]['m02'] -mu_filtered[i]['m01'] *mu_filtered[i]['m01']))
            P_angle = 0.5 * math.atan2( num, denom)

            if P_angle > math.pi/ 2:
                P_angle -= math.pi
            m = math.tan(P_angle)

            x1 = mc_filtered[i][0] + 100
            x2 = mc_filtered[i][0] - 100
            y1 = m * (x1 - mc_filtered[i][0]) +  mc_filtered[i][1]
            y2 = m * (x2 - mc_filtered[i][0]) +  mc_filtered[i][1]
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)
            principal_angle.append(P_angle * 180 / math.pi )
            cv2.line(drawing, (x1, y1), (x2, y2), color)
            print(i, P_angle * 180 / math.pi , mc_filtered[i])
            
            
        cv2.imshow('Contours', drawing)
        if cv2.waitKey() == ord('q'):
            cv2.destroyWindow('raw')
            return mc_filtered, principal_angle
        
    return


def mapping(act, image):
    act = np.matrix(act)
    ones = np.matrix(np.ones([1, 3]))
    act = np.concatenate((act, ones.T), axis=1)
    image = np.concatenate((image, ones.T), axis=1)
    act = act.T
    image = image.T
    A = np.matmul(act, image.I)
    return A
        
# Yellow (469.51339957488125, 131.64767848311172) top-left 
# 187.51265
# 367.98181
# -182.7314
# Green (551.8404734749532, 335.5730447400397) bottom-right
# -185.7127
# 576.04547
# -184.7553
# (481.7600934857015, 97.13918453055045) top-right
# -140.7747
# 382.30029
# -177.4168

def find_grabbing(p, e1, e2):
    v1 = [e1[0][0] - e1[1][0], e1[0][1] - e1[1][1]]
    v2 = [e2[0][0] - e2[1][0], e2[0][1] - e2[1][1]]
    x1, y1 = (0, 0)
    x2, y2 = (1, math.tan(p))
    p_vec = [x2 - x1, y2 - y1]
    if abs(np.dot(p_vec, v1)) > abs(np.dot(p_vec, v2)):
        return np.linalg.norm(v1)
    else:
        return np.linalg.norm(v2)
    # [(x1, y1) , (x2, y2)]
    # [(x2, y2) , (x3, y3)]