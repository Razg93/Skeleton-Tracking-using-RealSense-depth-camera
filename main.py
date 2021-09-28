import time
import logging
import os, sys, subprocess, pkg_resources
import datetime

# set log file
import cv2

log_file_name = "RealSenseTool.log"
logging.basicConfig(filename=log_file_name, filemode='a', level=logging.DEBUG,
                    format='[%(asctime)s.%(msecs)d] [%(name)s] [%(levelname)s]: %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S')


def is_on_intel_network():
    # importing socket module
    import socket
    # getting the hostname by socket.gethostname() method
    hostname = socket.gethostname()
    # getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    # printing the hostname and ip_address
    print("Current hostname: {}".format(hostname))
    print("Current IP Address: {}".format(ip_address))

    # if this script run on Intel network
    return ip_address.startswith("10")


def install_python_libraries(package):
    args_list = [sys.executable, "-m", "pip", "install", package]
    # if this script run on Intel network
    if is_on_intel_network():
        args_list += ["--proxy", "http://proxy.jer.intel.com:911"]
    subprocess.call(args_list)


def check_and_install_libraries():
    # install external libraries for text detection and image processing
    for package in ['pyrealsense2', 'matplotlib', 'tensorflow', 'opencv-python', 'numpy', 'mediapipe']:
        try:
            dist = pkg_resources.get_distribution(package)
            print('{} ({}) is installed'.format(dist.key, dist.version))
        except pkg_resources.DistributionNotFound:
            print('{} is NOT installed. Installing it'.format(package))
            install_python_libraries(package)


check_and_install_libraries()


def info_print(*args, **kwargs):
    """
    Print to info screen
    :param args:
    :param kwargs:
    :return:
    """
    print(*args, file=sys.stdout, **kwargs)
    logging.info(*args)


def _run_cmd(cmd):
    """
    running input cmd command and return its output
    :param cmd:
    :return:
    """
    import subprocess
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = process.communicate()
    return out.decode("utf-8")


import cv2
import mediapipe as mp
from realsense_camera import *


class PoseDetector:

    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.8, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        # print(results.pose_landmarks)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def getPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                # print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList


def main():
    object_to_track = [0,1,3,4,6,9,10]
    rs = RealsenseCamera()
    detector = PoseDetector()

    cTime = 0
    pTime = 0

    while True:

        # ----------------Capture Camera Frame-----------------
        ret, color_image, depth_image, depth_colormap = rs.get_frame_stream()

        # Acquire frame and resize to expected shape [1xHxWx3]
        frame = color_image.copy()
        frame = detector.findPose(frame)
        lmList = detector.getPosition(frame)

        if len(lmList) != 0:
            for objet in object_to_track:
                _, x, y = lmList[objet]
                print(lmList[objet])
                depth_to_object = depth_image[y, x]
            text = "Depth: {} cm".format(depth_to_object / 10)
            print(text)
            cv2.putText(frame, text, (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2, cv2.LINE_AA)

        else:
            print("object did not detected")



        # calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Draw framerate in corner of frame
        cv2.putText(frame, 'FPS: {0:.2f}'.format(fps), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)
        # # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Frame RGB', frame)
        cv2.imshow('depth image colormap', depth_colormap)
        # cv2.imshow("depth_image", depth_image)

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break


    rs.release()

# Clean up
cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
