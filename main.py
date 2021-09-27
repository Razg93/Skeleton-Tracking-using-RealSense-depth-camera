import time
import logging
import os, sys, subprocess, pkg_resources
import datetime
import cv2

def install_python_libraries(package):
    args_list = [sys.executable, "-m", "pip", "install", package]
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
                text = "{} cm".format(depth_to_object / 10)
                print(text)

        else:
            print("object did not detected")



        # calculate FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Draw framerate in corner of frame
        cv2.putText(color_image, 'FPS: {0:.2f}'.format(fps), (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
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
