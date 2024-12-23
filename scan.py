#!/usr/bin/python3

import cv2
import requests
from time import sleep
import sys
import json


pibaseurl = f"http://raspberrypi.local:5000/"

cam = cv2.VideoCapture(0)
width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

def turnon(n, color="white"):
    requests.get(f"{pibaseurl}{color}/{n}")

def turnoff():
    requests.get(f"{pibaseurl}off")

angle = int(sys.argv[1])

try:
    f = open("data.json", "r")
    data = json.load(f)
    f.close()
except (FileNotFoundError, json.decoder.JSONDecodeError):
    data = {}
data[angle] = {}

turnoff()
sleep(0.1)
for i in range(50):
    turnon(i)
    sleep(0.1)
    r, frame = cam.read()
    # filtered = frame.copy()
    # filtered[:, :, 0] = 0
    # filtered[:, :, 1] = 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    #print(i, ">", maxVal, maxLoc)
    # if i % 5 == 0:
    #     cv2.circle(frame, maxLoc, 5, (255, 0, 0), 2)
    #     cv2.imwrite(f"frame{i}.png", frame)
    if maxVal > 200:
        data[angle][i] = str(maxLoc)
    sleep(0.5)
turnoff()

f = open("data.json", "w")
json.dump(data, f, indent=2)
f.close()
