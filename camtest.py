#!/usr/bin/python3

import cv2
from time import sleep


pibaseurl = f"http://raspberrypi.local:5000/"

#camurl = "rtsp://192.168.1.182:8080/video/h264"
#camurl = "http://192.168.1.182:4747/video"
#camurl = "rtsp://admin:admin@192.168.1.182:1935"


cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(width, "x", height)


r, frame = cam.read()
rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
if r:
    cv2.imwrite(f'testsnap.png', frame)
    cv2.imwrite(f'rtestsnap.png', rotated)
else:
    print("Something went wrong")

