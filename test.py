from booth_camera import cam
import booth_imgproc as imp
import cv2 as cv

thiscam = cam()
thiscam.newCapture(2)
thiscam.close()

cv.namedWindow('test', cv.WINDOW_NORMAL)
cv.imshow('test', imp.applylut(thiscam.lastCapture[0]))
cv.waitKey(0)
cv.destroyAllWindows()