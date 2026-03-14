import booth_config as config
import booth_imgproc as imgproc
import booth_fs as ffs
import booth_printer as printer
import booth_camera as camera
from booth_upload import upload
from booth_logging import logger, loglevels

from booth_gui_components import imagePreview, imageBox, QRWindow, textWindow
from pathlib import Path

from multiprocessing import Process
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import QThread, QTimer, QUrl, QCoreApplication
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
            logger.post("ERROR: could not initialise camera", loglevels.ERROR)

        # path for last exported collage
        self.lastExport: Path = None
        
        # initialise overlays
        self.overlays: dict[str, imgproc.overlayItem] = {}
        for p in ffs.get_children(config.overlaysPath):
            self.overlays[p.stem] = imgproc.overlayItem(p)
        for p in self.overlays.values():
            logger.post(f"INFO: loaded overlay {p.name} with {p.nbounds} bounds", loglevels.INFO)

        # initialise filters
        self.luts: dict[str, imgproc.lutItem] = {}
        for p in ffs.get_children(config.lutsPath):
            self.luts[p.stem] = imgproc.lutItem(p)
        for p in self.luts.values():
            logger.post(f"INFO: loaded lut {p.name}", loglevels.INFO)
        
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
        # will fail if camera is not properly initialised
        if not self.cam.loaded:
            logger.post('ERROR: camera not loaded', loglevels.ERROR)
            return
        self.cam.shoot()
    
    def single_shot_with_count(self):
        # will fail if camera is not properly initialised
        if not self.cam.loaded:
            logger.post('ERROR: camera not loaded', loglevels.ERROR)
            return
        logger()
        logger.post(f"shot {self.shotCount}", loglevels.INFO)
        self.shotCount -= 1
        self.cam.shoot()
    
    def capture_handler(self):
        QTimer.singleShot(0, self.capture)

    
    def capture(self):
        if not self.cam.loaded:
            logger.post('ERROR: camera not loaded', loglevels.ERROR)
            return
        self.cam.clear()
        self.shotCount = self.selectedOverlay.nbounds
        if config.mockCamera:
            for i in range(self.selectedOverlay.nbounds):
                self.cam.shoot()
        else:
            for i in range(self.selectedOverlay.nbounds):
                counter = self.delay
                nbeep = 1
                c_disp = textWindow(str(counter))
                c_disp.setFocus()
                QCoreApplication.processEvents()
                sleep(1)
                for j in range(self.delay-1):
                    counter -= 1
                    c_disp.label.setText(str(counter))
                    QCoreApplication.processEvents()
                    if counter < 4:
                        self.beep(nbeep)
                        nbeep += 1
                    sleep(1)
                c_disp.destroy()
                logger.post('INFO: taking shot', loglevels.INFO)
                self.single_shot_with_count()
                logger.post('INFO: took shot', loglevels.INFO)
    
    def beep(self, count: int):
        self.sfx.play()
        for i in range(count-1):
            sleep(0.16)
            self.sfx.play()
            


    def export_poster(self):
        if (self.selectedOverlay.nbounds>len(self.cam.lastCapture)):
            logger.post(f"ERROR: {len(self.cam.lastCapture)} images captured for collage that needs {self.selectedOverlay.nbounds}", loglevels.WARNING)
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
        if self.lastExport is None or not self.lastExport.exists():
            logger.post('ERROR: no file to preview', loglevels.ERROR)
            return
        self.preview = imagePreview(self.lastExport)
        
    def upload_last(self):
        if self.lastExport is None or not self.lastExport.exists():
            logger.post('ERROR: no file to upload', loglevels.ERROR)
            return
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
            logger.post(f"ERROR: selected overlay {name} not available", loglevels.ERROR)
        self.selectedOverlay = self.overlays[name]
        logger.post(f"INFO: overlay set to {name}", loglevels.INFO)
        
    def setLut(self, name: str):
        if (name not in self.luts):
            logger.post(f"ERROR: selected lut {name} not available", loglevels.ERROR)
        self.selectedLut = self.luts[name]
        logger.post(f"INFO: lut set to {name}", loglevels.INFO)
        
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
            logger.post("INFO: using configured image to generate lut previews", loglevels.INFO)
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
    

    def startFlow(self):
        logger.post(f'overlay: {self.selectedOverlay}', loglevels.INFO)
        logger.post(f'lut: {self.selectedLut}')
        logger.post(f'nbounds: {self.selectedOverlay.nbounds}')
        self.capture()
        self.export_poster()
        self.upload_last()
    




class runnerThread(QThread):
    def __init__(self, target):
        super().__init__()
        self.target = target
    def run(self):
        self.target()



        