import cv2
import numpy as np

img = cv2.imread("netcam1.png")
width, height, _ = img.shape
mask = np.zeros((width, height), np.uint8)
points = np.array([[252, 524], [633, 950], [6, 950]])
print(points.dtype)
cv2.fillPoly(mask, pts=[points], color=255)
img[mask == 0] = 0

cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
