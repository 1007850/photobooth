
import booth_camera as camera, booth_fs as fss, booth_imgproc as imgproc
import numpy as np
import cv2 as cv

thiscam = camera.cam()
print("starting capture")
thiscam.newCapture(2,3)
thiscam.close()

print("starting image processing")
im = imgproc.create_collage(thiscam.lastCapture)
im = np.array(im)[:,:,::-1]

cv.namedWindow('test', cv.WINDOW_NORMAL)
cv.imshow('test', im)
cv.waitKey(0)
cv.destroyAllWindows()