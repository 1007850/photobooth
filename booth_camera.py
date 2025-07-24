import cv2 as cv
import time
import PIL.Image as img
from PyQt6 import QtMultimedia



class cam:

    def __init__(self):
        print("initialising face detect")
        self.classifier = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("initialising webcam")
        self.cam: cv.VideoCapture = cv.VideoCapture(0)          # instaniate camera handle
        self.cam.set(cv.CAP_PROP_AUTO_WB, 1)                    # set whitebalance to auto
        self.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)              # set auto exposure to disabled
        self.exposure = 3                                       # current exposure
        self.targetExposure = 150                               # ENTER DESIRED EXPOSURE /255
        self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposure)       # set current exposure
        self.autoexpose()                                       # auto expose
        self.lastCapture: list[img.Image] = []                  # capture cache
        self.timeout = time.time() + 2                          # 2s timeout to allow cam to change exposure

    def shoot(self):
        while self.timeout>time.time():
            time.sleep(0.1)
        print("photo!")
        ret = False
        for i in range(5):
            ret, frame = self.cam.read()
            if ret:
                self.lastCapture.append(img.fromarray(frame[:, :, ::-1]))
                return
            else:
                time.sleep(0.1)
        raise Exception("Unable to capture image")

    def close(self):
        self.cam.release()
    
    def clear(self):
        self.lastCapture = []
    
    def autoexpose(self):
        print("autoexposing...")
        for i in range(100):
            fails = 0
            while True:
                exposure = self.getexpose()
                fails += 1
                if exposure!=0:
                    break                    
                elif fails==10:
                    print("ERROR: face detect failed")
                    exposure = self.targetExposure
                    break
            diff = exposure - self.targetExposure
            # print(f"EXPOSURE: {self.exposure} {exposure}")
            # print(f"DIFF: {diff}")
            if diff > 15:
                self.exposure -= 0.1
                self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposure)
            elif diff < -15:
                self.exposure += 0.1
                self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposure)
            else:
                print(f"autoexpose complete. exposure setting: {self.exposure} exposure: {exposure} target exposure: {self.targetExposure}")
                self.timeout = time.time()
                return
        print(f"ERROR: autoexpose timed out. exposure setting: {self.exposure} exposure: {exposure} target exposure: {self.targetExposure}")
        self.timeout = time.time()

        
    def getexpose(self):
        ret = False
        while not ret:
            ret, frame = self.cam.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = self.classifier.detectMultiScale(image=frame, scaleFactor=1.1)
        means = []
        try:
            for (x,y,w,h) in faces:
                if w==0 or h==0:
                    return 0
                roi = frame[y:y+h, x:x+w]
                mean = cv.mean(roi)[0]
                means.append(mean)
            out = sum(means)/len(means)
            return out
        except:
            return 0
    
    def clear(self):
        self.lastCapture = []