# Skeleton Tracking using RealSense Depth Camera D435

![image](https://user-images.githubusercontent.com/50642442/134936895-477be5c3-db1f-4577-990d-33807c6cbb6b.png)

Pose estimation refers to computer vision techniques that detect human figures in images and videos.
The pose estimation models take a processed camera image as the input and output information about keypoints.
Using these deteceting points in the RGB image and depth image from RealSense camera, I was able to calculate the distance in centimeters to 33 keypoints in the human body.

# Pose Landmark Model:
The landmark model in MediaPipe Pose predicts the location of 33 pose landmarks.
The landmarks detected are indexed by a part ID, with a confidence score between 0.0 and 1.0. 

![image](https://user-images.githubusercontent.com/50642442/134937772-571f00d8-bfb6-455c-89c5-7fe8246e8f69.png)
























