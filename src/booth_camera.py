import cv2 as cv
import time
import PIL.Image as img
from sys import platform
from pathlib import Path
from io import BytesIO
import booth_fs as ffs
import ctypes
import ctypes.wintypes as wintypes
import time
import booth_config as config

if (platform!="win32"):
    import gphoto2


if (platform=='win32'):
    
    WM_KEYDOWN = 0x100
    WM_KEYUP = 0x101
    VK_1 = 0x31
    DOWN_1 = 0x00020001
    UP_1 = 0xC0020001
    
    DOWN_K = 0x250001
    UP_K = 0xC0250001
    
    user32 = ctypes.windll.user32

    FindWindow = user32.FindWindowW
    FindWindow.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    # FindWindow.restype = wintypes.HWND

    PostMessage = user32.PostMessageW
    PostMessage.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    # PostMessage.restype = wintypes.BOOL
    

    class cam:
        def __init__(self):
            self.lastCapture: list[img.Image] = []
            if (not config.tmpPath.exists()):
                ffs.create_directory(config.tmpPath)
            self.hwnd = FindWindow(None, 'Remote') or FindWindow(None, 'Capture One')
            if (self.hwnd == 0):
                print('ERROR: cannot find window')
            print("log: successfully loaded camera")

        def shoot(self):
            PostMessage(self.hwnd, WM_KEYDOWN, VK_1, DOWN_1)
            time.sleep(0.1)
            PostMessage(self.hwnd, WM_KEYUP, VK_1, UP_1)
            children = ffs.get_children(config.tmpPath)
            while (not children):
                children = ffs.get_children(config.tmpPath)
            capturePath = children[0]
            time.sleep(0.5)
            self.lastCapture.append(img.open(str(capturePath)).copy())
            capturePath.unlink()
            print("capture!")

        def close(self):
            self.clear()

        def clear(self):
            self.lastCapture = []
            children = ffs.get_children(config.tmpPath)
            if children:
                for path in children:
                    path.unlink()

else:

    class cam:
        def __init__(self):
            self.lastCapture: list[img.Image] = []
            self.lastCapturePath: list[Path] = []
            self.camera = gp.Camera()
            self.camera.init()

        def shoot(self):
            capturePath = self.camera.capture(gp.GP_CAPTURE_IMAGE)
            captureFile = self.camera.file_get(capturePath.folder, capturePath.name, gp.GP_FILE_TYPE_NORMAL)
            self.lastCapturePath.append(Path(r"./tmp")/capturePath.name)
            captureData = gp.gp_file_get_data_and_size(captureFile)[1]
            self.lastCapture.append(img.open(BytesIO(captureData)))
            del capturePath, captureFile
            self.camera.exit()
            print("capture!")

        def close(self):
            self.camera.exit()

        def clear(self):
            self.lastCapture = []






class Cam:

    def __init__(self):
        # print("initialising face detect")
        # self.classifier = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # print("initialising webcam")
        # self.cam: cv.VideoCapture = cv.VideoCapture(0)          # instaniate camera handle
        # self.cam.set(cv.CAP_PROP_AUTO_WB, 1)                    # set whitebalance to auto
        # self.cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)              # set auto exposure to disabled
        # self.exposure = 3                                       # current exposure
        # self.targetExposure = 150                               # ENTER DESIRED EXPOSURE /255
        # self.cam.set(cv.CAP_PROP_EXPOSURE, self.exposure)       # set current exposure
        # self.autoexpose()                                       # auto expose
        # self.lastCapture: list[img.Image] = []                  # capture cache
        # self.timeout = time.time() + 2                          # 2s timeout to allow cam to change exposure
        
        self.platform = platform
        print(self.platform)

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
    