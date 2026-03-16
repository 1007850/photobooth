import booth_config as config
import booth_imgproc as imgproc
import booth_fs as ffs
import booth_printer as printer
import booth_camera as camera
from booth_upload import upload
from booth_settings import SettingWindow
from booth_messaging import logger, loglevels, signals, changedSettings

from booth_gui_components import imagePreview, imageBox, QRWindow, textWindow, postWarning
from pathlib import Path

from PyQt6.QtWidgets import QComboBox, QMessageBox
from PyQt6.QtCore import QThread, QTimer, QUrl, QCoreApplication, pyqtSignal
from PyQt6.QtMultimedia import QSoundEffect

from time import sleep
import importlib



class ctrl:
    
    def __init__(self):
        # stop init if workingPath is not valid. do not set default directory as luts and overlays are required
        if not config.workingPath.exists():
            self.warning = postWarning(None, 'ALERT', "workingPath in config is not set or does not exist\n\nplease set the working directory then restart app", QMessageBox.StandardButton.Ok)

        # imitialise directories
        config.generatePaths()

        # initialise thread pool
        self.pool = []
        
        # initialise printer module
        self.prn = printer.prn()

        # initialise camera
        self.cam: camera.cam = None
        self.init_camera()

        # path for last exported collage
        self.lastExport: Path = None
        
        # initialise beep sound
        self.sfx = QSoundEffect()
        self.sfx.setSource(QUrl.fromLocalFile(str(Path("beep.wav"))))
        
        # delay between shots
        self.delay = config.captureDelay
        
        # initialise overlays and luts
        self.overlays: dict[str, imgproc.overlayItem] = None
        self.luts: dict[str, imgproc.lutItem] = None
        self.selectedOverlay: imgproc.overlayItem = None
        self.selectedLut: imgproc.lutItem = None
        self.init_luts_overlays()
        
        # initialise shot count
        self.shotCount = 0
        
        # saving settings triggers signal
        signals.settingSignal.connect(self.handleSettingsSaved)
    

    def init_camera(self):
        # initialise camera module
        try:
            self.cam = camera.cam()
        except:
            logger.post("ERROR: could not initialise camera", loglevels.ERROR)


    def init_luts_overlays(self):
        # initialise overlays
        self.overlays = {}
        for p in ffs.get_children(config.overlaysPath):
            self.overlays[p.stem] = imgproc.overlayItem(p)
        for p in self.overlays.values():
            logger.post(f"INFO: loaded overlay {p.name} with {p.nbounds} bounds", loglevels.INFO)
            
        # initialise filters
        self.luts = {}
        for p in ffs.get_children(config.lutsPath):
            self.luts[p.stem] = imgproc.lutItem(p)
        lutNames = [x.name for x in(self.luts.values())]
        logger.post(f'INFO: loaded luts {", ".join(lutNames)}', loglevels.INFO)
        
        # initialise selected overlay
        if self.overlays == {}:
            # allow init to finish so that the gui layout can fail silently
            logger.post("no overlays detected, populate overlaysPath and restart", loglevels.ERROR)
            if config.workingPath.exists():
                self.warning = postWarning(None, 'ALERT', f'ERROR: no overlays detected in {config.overlaysPath}\npopulate overlays folder or change path in settings\n', QMessageBox.StandardButton.Ok)
        else:
            self.selectedOverlay = min(self.overlays.values(), key=lambda x: x.name)

        # initialise selected lut
        if self.luts == {}:
            # allow init to finish so that the gui layout can fail silently
            logger.post("no LUTs detected, populate overlaysPath and restart", loglevels.ERROR)
            if config.workingPath.exists():
                self.warning = postWarning(None, 'ALERT', f"ERROR: no LUTs detected in {config.lutsPath}\npopulate LUTs folder or change path in settings", QMessageBox.StandardButton.Ok)
        else:
            self.selectedLut = min(self.luts.values(), key=lambda x: x.name)


    #--------------------------------------------------

    
    def reload_cam(self):
        self.cam.close()
        importlib.reload(camera)
        # initialise camera module
        try:
            self.cam = camera.cam()
        except:
            logger.post("ERROR: could not initialise camera", loglevels.ERROR)
    
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
            
    
    #--------------------------------------------------

    def export_poster(self):
        if (self.selectedOverlay.nbounds>len(self.cam.lastCapture)):
            logger.post(f"ERROR: {len(self.cam.lastCapture)} images captured for collage that needs {self.selectedOverlay.nbounds}", loglevels.WARNING)
            return
        targetPath = config.collagePath / (ffs.get_time(False)+".jpg")
        imgproc.create_collage(self.cam.lastCapture[-self.selectedOverlay.nbounds:], targetPath, self.selectedOverlay, self.selectedLut)
        self.lastExport = targetPath
    
    def preview_last(self):
        if self.lastExport is None or not self.lastExport.exists():
            logger.post('ERROR: no file to preview', loglevels.ERROR)
            return
        self.preview = imagePreview(self.lastExport)
        
    def upload_last(self):
        if not config.upload:
            logger.post('INFO: file upload disabled', loglevels.WARNING)
            return
        elif self.lastExport is None or not self.lastExport.exists():
            logger.post('ERROR: no file to upload', loglevels.ERROR)
            return
        url = upload(self.lastExport)
        self.preview = QRWindow(url)
        
        
    #--------------------------------------------------

    def print_last(self):
        if not config.print:
            logger.post('INFO: printing disabled', loglevels.WARNING)
            return
        elif not self.prn.initialised:
            logger.post('ERROR: printer is not initialised', loglevels.ERROR)
            return
        self.prn.setImage(self.lastExport)
        t = runnerThread(self.prn.print)
        self.pool.append(t)
        t.start()
    
    def selectFilePrint(self):
        if not config.print:
            logger.post('INFO: printing disabled', loglevels.WARNING)
            return
        elif not self.prn.initialised:
            logger.post('ERROR: printer is not initialised', loglevels.ERROR)
            return
        self.prn.interactiveSetImage()
        t = runnerThread(self.prn.print)
        self.pool.append(t)
        t.start()
        
    def setPrinteSettings(self):
        self.prn.setPrintSettings()
    
    
    #--------------------------------------------------
    
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
        
    #--------------------------------------------------

    def capturePreviewImage(self, imageBoxes: list[imageBox]):
        # get reference pic by camera or configured preview image
        if config.previewImagePath.exists():
            # use configured preview image if available to preview luts
            logger.post("INFO: using configured image to generate lut previews", loglevels.INFO)
            resizedImage = imgproc.resizeForPreview(config.previewImagePath, True)
        elif not self.cam.loaded:
            # check that camera is loaded
            logger.post('ERROR: camera not loaded', loglevels.ERROR)
            return
        else:
            self.cam.clear()
            self.cam.shoot()
            resizedImage = imgproc.resizeForPreview(self.cam.lastCapture[0], False)
        
        # generate previews, replacing old ones
        for lut in sorted(self.luts.values(), key=lambda x: x.name):
            previewPath = config.previewsPath / f"lut_{lut.name}.jpeg"
            previewPath.resolve()
            previewPath.unlink(True)
            imgproc.genLUTPreview(resizedImage, lut).save(str(previewPath), format='JPEG')

        # load previews
        self.loadPreviewImages(imageBoxes, True)
    
    def loadPreviewImages(self, imageBoxes: list[imageBox], wait: bool=False):
        for idx,lut in enumerate(sorted(self.luts.values(), key=lambda x: x.name)):
            pb = imageBoxes[idx]
            previewPath = config.previewsPath / f"lut_{lut.name}.jpeg"
            previewPath.resolve()
            if not previewPath.is_file():
                if wait:
                    # wait for fs to catch up
                    while not previewPath.is_file():
                        sleep(0.1)
                    sleep(0.5)
                    pb.loadQIM(previewPath)
                else:
                    # don't wait and skip over lut preview
                    logger.post(f'INFO: lut preview for lut [{lut.name}] {previewPath} not available', loglevels.WARNING)
            else:
                # file was already available
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
    
    
    #--------------------------------------------------
    
    def open_settings(self):
        self.settings = SettingWindow()


    def handleSettingsSaved(self, settings: changedSettings):
        if settings.restart:
            raise Exception("restart triggered")
        if settings.printer:
            self.prn = printer.prn()
        if settings.lutoverlay:
            self.init_luts_overlays()
        if settings.camera:
            self.cam.close()
            importlib.reload(camera)
            self.init_camera()
        if settings.gui:
            signals.guiSignal.emit('')

    def handleQuit(self):
        config.restart = False
        exit()



    

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



        