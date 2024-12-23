import cv2
import threading

from time import sleep

camurl = "rtsp://192.168.1.182:1935"
class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.cap = None
        self.frame = None
        self.stopped = False
        self.thread = None

    def start(self):
        self.cap = cv2.VideoCapture(self.url)
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            else:
                print("Error reading frame")

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.thread is not None:
            self.thread.join()
        self.cap.release()

if __name__ == "__main__":
    stream = RTSPStream(camurl).start()
    print("Connected")
    sleep(3)

    for i in range(10):
        frame = stream.read()
        if frame is not None:
            cv2.imwrite(f'netcam{i}.png', frame)
        else:
            print("Problem on iteration", i)
        sleep(3)

    stream.stop()
    cv2.destroyAllWindows()