#!/usr/bin/python3

import cv2
import requests
from requests.adapters import HTTPAdapter, Retry
from time import sleep
import sys
import json
import threading
from argparse import ArgumentParser
import numpy as np

MASK = [[820, 50], [70, 1988], [1530, 1988]]

parser = ArgumentParser()
parser.add_argument("cmd")
parser.add_argument("-n", "--num",  type=int, default=500)
parser.add_argument("-t", "--threshold", type=int, default=250)
parser.add_argument("-b", "--blur", type=int, default=11)
parser.add_argument("--blur-steps", type=int, default=3)
parser.add_argument("-c", "--color", default="white")
parser.add_argument("-d", "--dest", default="led-raw.json")
parser.add_argument("-m", "--mask", type=(lambda x: np.array(eval(x))), default=np.array(MASK))
parser.add_argument("--snap-freq", type=int, default=0)
parser.add_argument("--prog-freq", type=int, default=50)

pibaseurl = f"http://raspberrypi.local:5000/"

def do_command(args):
    if args.cmd == "debug":
        print(args)
    elif args.cmd == "masktest":
        cam = CamStream(2, cv2.CAP_V4L2)
        cam.start()
        sleep(5)
        frame = cam.read()
        cam.stop()
        rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite("mt-raw.png", rotated)
        mask = make_mask(args.mask, cam.rwidth, cam.rheight)
        rotated[mask == 0] = 0
        cv2.imwrite("mt-masked.png", rotated)
    else:
        print("Unrecognized command")

def do_scan(args):
    try:
        f = open(args.dest, "r")
        data = json.load(f)
        f.close()
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = []

    cam = CamStream(2, cv2.CAP_V4L2)
    cam.start()
    mask = make_mask(args.mask, cam.rwidth, cam.rheight)
    sleep(5)

    sess = requests.Session()
    retries = Retry(total=5,
                    connect=5,
                    read=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    sess.mount('http://', HTTPAdapter(max_retries=retries))

    turnoff(sess)
    for i in range(args.num):
        turnon(sess, i, args.color)
        sleep(3)
        frame = cam.read()
        rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        gray = grayify(rotated, args.color)
        for j in range(args.blur_steps):
            blurred = cv2.GaussianBlur(gray, (args.blur - 2 * j, args.blur - 2 * j), 0)
            blurred[mask == 0] = 0
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blurred)
            if maxVal >= args.threshold:
                break
        if maxVal >= args.threshold:
            xy, z = maxLoc
            if args.snap_freq > 0 and i % args.snap_freq == 0:
                cv2.circle(rotated, maxLoc, 25, (0, 255, 255), 6)
                cv2.imwrite(f"images/detect-{angle:03}-{i:03}.png", rotated)
            if angle >= 180:
                xy = cam.rwidth - xy - 1
            p = {"pos": i, "z": cam.rheight - z - 1}
            if angle % 180 == 0:
                p["x"] = xy
            else:
                p["y"] = xy
            data.append(p)
        else:
            print("Skipping", i)
        if args.prog_freq > 0 and i % args.prog_freq == 0:
            print("L", i)
    turnoff(sess)
    cam.stop()

    f = open(args.dest, "w")
    json.dump(data, f, indent=2)
    f.close()

def make_mask(points, width=1536, height=2304):
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, pts=[points], color=255)
    return mask

def turnon(sess, n, color="white"):
    sess.get(f"{pibaseurl}{color}/{n}")

def turnoff(sess):
    sess.get(f"{pibaseurl}off")

def grayify(frame, color):
    if color == "red":
        return cv2.split(frame)[2]
    elif color == "green":
        return cv2.split(frame)[1]
    elif color == "blue":
        return cv2.split(frame)[0]
    else:
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

class CamStream:
    def __init__(self, num, backend):
        self.num = num
        self.backend = backend
        self.cap = None
        self.frame = None
        self.stopped = False
        self.thread = None

    def start(self):
        self.cam = cv2.VideoCapture(self.num, self.backend)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.cam.set(cv2.CAP_PROP_FPS, 15)
        self.width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.rwidth, self.rheight = self.height, self.width
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cam.read()
            while not ret:
                ret, frame = self.cam.read()
            self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.thread is not None:
            self.thread.join()
        self.cam.release()

if __name__ == "__main__":
    args = parser.parse_args()
    try:
        angle = int(args.cmd)
        do_scan(args)
    except ValueError:
        do_command(args)

