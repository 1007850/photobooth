import booth_config as config
import booth_imgproc as imgproc
import booth_fs as ffs
import booth_printer as printer
import booth_camera as camera
from booth_upload import upload

from booth_gui_components import imagePreview, imageBox, QRWindow
from pathlib import Path

from multiprocessing import Process
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import QThread, QTimer, QUrl
from PyQt6.QtMultimedia import QSoundEffect

from time import sleep



class ctrl:
    
    def __init__(self):
        # imitialise directories
        config.generatePaths()

        # initialise thread pool
        self.pool = []
        
        # initialise printer module
        self.prn = printer.prn()

        # initialise camera module
        try:
            self.cam = camera.cam()
        except:
            print("ERROR: could not initialise camera")

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
        QTimer.singleShot(0, self.capture)

    
    def capture(self):
        self.shotCount = self.selectedOverlay.nbounds
        for i in range(self.selectedOverlay.nbounds):
            sleep(self.delay-4)
            self.beep(1)
            sleep(1)
            self.beep(2)
            sleep(1)
            self.beep(3)
            sleep(1)
            self.beep(4)
            self.single_shot_with_count()
    
    def beep(self, count: int):
        self.sfx.play()
        for i in range(count-1):
            sleep(0.16)
            self.sfx.play()
            


    def export_poster(self):
        if (self.selectedOverlay.nbounds>len(self.cam.lastCapture)):
            print(f"ERROR: {len(self.cam.lastCapture)} images captured for collage that needs {self.selectedOverlay.nbounds}")
            return
        targetPath = config.collagePath / (ffs.get_time(False)+".jpg")
        # subprocess for image processing and export
        # exportP = Process(target = imgproc.create_collage, args=(
        #     self.cam.lastCapture[-self.selectedOverlay.nbounds:],
        #     targetPath,
        #     self.selectedOverlay,
        #     self.selectedLut))
        # exportP.start()
        imgproc.create_collage(self.cam.lastCapture[-self.selectedOverlay.nbounds:], targetPath, self.selectedOverlay, self.selectedLut)
        self.lastExport = targetPath
    
    def preview_last(self):
        self.preview = imagePreview(self.lastExport)
        
    def upload_last(self):
        url = upload(self.lastExport)
        self.preview = QRWindow(url)

    
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
        
    def handlePreviewClick(self, selection: str, previewBoxes: list[imageBox], combobox: QComboBox, updateParam):
        for pb in previewBoxes:
            pb.toggleBorder(pb.label.text()==selection)
        combobox.blockSignals(True)
        combobox.setCurrentText(selection)
        combobox.blockSignals(False)
        updateParam(selection)
    
    def handleLUTComboboxChange(self, selection: str, previewBoxes: list[imageBox]):
        for pb in previewBoxes:
            pb.toggleBorder(pb.label.text()==selection)
        self.setLut(selection)
        
    def handleOverlayComboboxChange(self, selection: str, previewBoxes: list[imageBox]):
        for pb in previewBoxes:
            pb.toggleBorder(pb.label.text()==selection)
        self.setOverlay(selection)
        
    def capturePreviewImage(self, imageBoxes: list[imageBox]):
        if config.previewImagePath.exists():
            print("log: using configured image to generate lut previews")
            resizedImage = imgproc.resizeForPreview(config.previewImagePath, True)
        else:
            self.cam.clear()
            self.cam.shoot()
            resizedImage = imgproc.resizeForPreview(self.cam.lastCapture[0], False)
        for idx,lut in enumerate(sorted(self.luts.values(), key=lambda x: x.name)):
            pb = imageBoxes[idx]
            previewPath = config.previewsPath / f"lut_{lut.name}.jpeg"
            previewPath.resolve()
            previewPath.unlink(True)
            imgproc.genLUTPreview(resizedImage, lut).save(str(previewPath), format='JPEG')
            while not previewPath.is_file():
                sleep(0.1)
            sleep(0.5)
            pb.loadQIM(previewPath)
    
    def exportOverlayPreview(self, overlay: imgproc.overlayItem):
        previewPath = config.previewsPath / f"overlay_{overlay.name}.jpeg"
        previewPath.resolve()
        if not previewPath.is_file():
            resized = imgproc.resizeForPreview(overlay.overlay, False)
            imgproc.setBGGrey(resized).save(str(previewPath), format='JPEG')
            while not previewPath.is_file():
                sleep(0.1)
            sleep(0.5)
        return previewPath
    




class runnerThread(QThread):
    def __init__(self, target):
        super().__init__()
        self.target = target
    def run(self):
        self.target()



        