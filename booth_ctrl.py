import booth_camera as camera, booth_fs as ffs, booth_imgproc as imgproc, booth_printer as printer
import numpy as np
import cv2 as cv
from pathlib import Path

from multiprocessing import Process
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QThread, QTimer, QUrl, Qt
from PyQt6.QtMultimedia import QSoundEffect

from sys import platform


class ctrl:
    
    def __init__(self):
        # initialise thread pool
        self.pool = []
        
        # initialise printer module
        self.prn = printer.prn()

        # initialise camera module
        if (platform=="win32"):
            self.cam = camera.WinCam()
        else:
            self.cam = camera.UnixCam()

        # auto exposure switch
        self.autosw = False

        # imitialise save directory
        self.savePath = Path(r"./dump")
        ffs.create_directory(self.savePath)

        # path for last exported collage
        self.lastExport: Path = None
        
        # initialise beep sound
        self.sfx = QSoundEffect()
        self.sfx.setSource(QUrl.fromLocalFile(str(Path("beep.wav"))))
        
        # delay between shots
        self.delay = 6
        
    
    def reload_cam(self):
        self.cam.close()
        if (platform=="win32"):
            self.cam = camera.WinCam()
        else:
            self.cam = camera.UnixCam()
    
    def expose(self):
        self.cam.autoexpose()
    
    def exit(self):
        self.cam.close()

    def single_shot(self):
        self.cam.shoot()
    
    def capture_handler(self):
        self.cam.clear()
        if self.autosw:
            self.expose()
            self.capture()
        else:
            self.capture()

    
    def capture(self):
        for i in range(imgproc.nbounds):
            countdown = (i+1)*self.delay*1000
            QTimer.singleShot(countdown, self.cam.shoot)
            QTimer.singleShot(countdown-1000, self.sfx.play)
            QTimer.singleShot(countdown-1160, self.sfx.play)
            QTimer.singleShot(countdown-1320, self.sfx.play)
            QTimer.singleShot(countdown-1480, self.sfx.play)
            QTimer.singleShot(countdown-2000, self.sfx.play)
            QTimer.singleShot(countdown-2160, self.sfx.play)
            QTimer.singleShot(countdown-2320, self.sfx.play)
            QTimer.singleShot(countdown-3000, self.sfx.play)
            QTimer.singleShot(countdown-3160, self.sfx.play)
            QTimer.singleShot(countdown-4000, self.sfx.play)


    def toggle_autosw(self, sw: bool):
        self.autosw = sw
    
    def export_poster(self):
        targetPath = self.savePath / (ffs.get_time(False)+".jpg")
        # subprocess for image processing and export
        exportP = Process(target = imgproc.create_collage, args=(self.cam.lastCapture[-imgproc.nbounds:], targetPath))
        exportP.start()
        self.lastExport = targetPath
    
    def preview_last(self):
        self.preview = imagePreview(self.lastExport)
    
    def print_last(self):
        self.prn.setImage(self.lastExport)
        t = runnerThread(self.prn.print)
        self.pool.append(t)
        t.start()
    
    def selectFilePrint(self):
        self.prn.interactiveSetImage()
        t = runnerThread(self.prn.print)
        self.pool.append(t)
        t.start()


class runnerThread(QThread):
    def __init__(self, target):
        super().__init__()
        self.target = target
    def run(self):
        self.target()


class imagePreview(QMainWindow):
    def __init__(self, imagePath: Path):
        super().__init__()
        self.imagePath = imagePath
        self.initWindow()
        self.show()
    
    def initWindow(self):
        self.setWindowTitle("Image Preview")
        
        self.label = QLabel("urmum")
        self.label.setMinimumHeight(200)
        self.label.setMinimumWidth(200)
        self.setCentralWidget(self.label)

        self.pixmap = QPixmap(str(self.imagePath))
        self.label.setPixmap(self.pixmap)
        self.ratio = self.pixmap.width() / self.pixmap.height()
        
    def resizeEvent(self, a0):
        self.blockSignals(True)
        scaled_pixmap = self.pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)
        
        new_width = self.width()
        new_height = int(new_width // self.ratio)
        self.resize(new_width, new_height)
        self.blockSignals(False)