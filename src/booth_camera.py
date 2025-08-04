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
            self.hwnd = FindWindow(None, 'Remote') or FindWindow(None, 'Capture One')
            self.clear()
            if (self.hwnd == 0):
                print('ERROR: cannot find Imaging Edge window')
                self.loaded = False
            else:
                self.loaded = True
                print("log: successfully loaded camera")

        def shoot(self):
            if not self.loaded:
                print("ERROR: camera not loaded")
                return
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
            ffs.create_directory(config.tmpPath)


else:

    class cam:
        def __init__(self):
            self.lastCapture: list[img.Image] = []
            self.lastCapturePath: list[Path] = []
            try:
                self.camera = gp.Camera()
                self.camera.init()
            except:
                print("ERROR: failed to load camera")

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