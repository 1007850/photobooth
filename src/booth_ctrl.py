import booth_camera as camera, booth_fs as ffs, booth_imgproc as imgproc, booth_printer as printer, booth_config as config
from booth_gui_components import imagePreview
import numpy as np
import cv2 as cv
from pathlib import Path

from multiprocessing import Process
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QThread, QTimer, QUrl, Qt
from PyQt6.QtMultimedia import QSoundEffect



class ctrl:
    
    def __init__(self):
        # initialise thread pool
        self.pool = []
        
        # initialise printer module
        self.prn = printer.prn()

        # initialise camera module
        try:
            self.cam = camera.cam()
        except:
            print("ERROR: could not initialise camera")

        # initialise configured collage dump
        ffs.create_directory(config.collagePath, True)

        # imitialise save directory
        self.savePath = config.collagePath
        ffs.create_directory(self.savePath)
        
        # initialise or clear the tmp directory
        tmpdir = Path(r'./tmp')
        ffs.create_directory(tmpdir)
        for c in ffs.get_children(tmpdir):
            ffs.clear_target(c)

        # path for last exported collage
        self.lastExport: Path = None
        
        # initialise overlays
        self.overlays: dict[str, imgproc.overlayItem] = {}
        for p in ffs.get_children(config.overlaysPath):
            self.overlays[p.stem] = imgproc.overlayItem(p)
        for p in self.overlays.values():
            print(f"log: loaded overlay {p.name} with {p.nbounds} bounds")

        # initialise filters
        self.luts: dict[str, imgproc.lutItem] = {}
        for p in ffs.get_children(config.lutsPath):
            self.luts[p.stem] = imgproc.lutItem(p)
        for p in self.luts.values():
            print(f"log: loaded lut {p.name}")
        
        # initialise beep sound
        self.sfx = QSoundEffect()
        self.sfx.setSource(QUrl.fromLocalFile(str(Path("beep.wav"))))
        
        # delay between shots
        self.delay = config.captureDelay
        
        # initialise selected overlay and lut
        self.selectedOverlay: imgproc.overlayItem = min(self.overlays.values(), key=lambda x: x.name)
        self.selectedLut: imgproc.lutItem = min(self.luts.values(), key=lambda x: x.name)
        
        # initialise shot count
        self.shotCount = 0
        
    
    def reload_cam(self):
        self.cam.close()
        self.cam = camera.cam()
    
    def expose(self):
        self.cam.autoexpose()
    
    def exit(self):
        self.cam.close()

    def single_shot(self):
        self.cam.shoot()
    
    def single_shot_with_count(self):
        print(f"shot {self.shotCount}")
        self.shotCount -= 1
        self.cam.shoot()
    
    def capture_handler(self):
        self.cam.clear()
        if self.autosw:
            self.expose()
            self.capture()
        else:
            self.capture()

    
    def capture(self):
        self.shotCount = self.selectedOverlay.nbounds
        for i in range(self.selectedOverlay.nbounds):
            countdown = (i+1)*self.delay*1000
            QTimer.singleShot(countdown, self.single_shot_with_count)
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
        if (self.selectedOverlay.nbounds!=len(self.cam.lastCapture)):
            print("ERROR: not enough images captured for collage")
            return
        targetPath = self.savePath / (ffs.get_time(False)+".jpg")
        # subprocess for image processing and export
        exportP = Process(target = imgproc.create_collage, args=(
            self.cam.lastCapture[-self.selectedOverlay.nbounds:],
            targetPath,
            self.selectedOverlay,
            self.selectedLut))
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
        
    def setPrinteSettings(self):
        self.prn.setPrintSettings()
    
    def setOverlay(self, name: str):
        if (name not in self.overlays):
            raise Exception(f"ERROR: selected overlay {name} not available")
        self.selectedOverlay = self.overlays[name]
        print(f"log: overlay set to {name}")
        
    def setLut(self, name: str):
        if (name not in self.luts):
            raise Exception(f"ERROR: selected lut {name} not available")
        self.selectedLut = self.luts[name]
        print(f"log: lut set to {name}")
        
    def capturePreviewImage(self):
        self.cam.clear()
        self.cam.shoot()
        



class runnerThread(QThread):
    def __init__(self, target):
        super().__init__()
        self.target = target
    def run(self):
        self.target()



        