import json
import sys
from pathlib import Path
import booth_config as config
import importlib
from booth_messaging import signals, changedSettings, logger, loglevels
from booth_upload import envPath
from dotenv import load_dotenv, set_key
import os
import booth_upload as upload

from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget, QHBoxLayout


class SettingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.configPath = config.configPath
        self.envPath = envPath
        self.initWindow()
        self.loadConfig()
        self.show()

    def initWindow(self):
        self.setWindowTitle('Photobooth Settings')

        # layouts
        self.vlayout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vlayout)
        self.setCentralWidget(self.central_widget)
        
        # DB_HOST
        self.vlayout.addWidget(QLabel('domain/url'))
        self.dbhostEdit = QLineEdit()
        self.vlayout.addWidget(self.dbhostEdit)
        
        # DB_KEY
        self.vlayout.addWidget(QLabel('api key'))
        self.dbkeyEdit = QLineEdit()
        self.vlayout.addWidget(self.dbkeyEdit)

        # printer name
        self.vlayout.addWidget(QLabel('Printer Name'))
        self.printerNameEdit = QLineEdit()
        self.vlayout.addWidget(self.printerNameEdit)
        
        # working path (root dir)
        self.vlayout.addWidget(QLabel('Working Path (root directory for other paths)'))
        self.workingPathEdit = QLineEdit()
        self.vlayout.addWidget(self.workingPathEdit)

        # collage path
        self.vlayout.addWidget(QLabel('Collage Path (relative to working path)'))
        self.collagePathEdit = QLineEdit()
        self.vlayout.addWidget(self.collagePathEdit)

        # LUTs path
        self.vlayout.addWidget(QLabel('LUTs Path (relative to working path)'))
        self.lutsPathEdit = QLineEdit()
        self.vlayout.addWidget(self.lutsPathEdit)

        # overlays path
        self.vlayout.addWidget(QLabel('Overlays Path (relative to working path)'))
        self.overlaysPathEdit = QLineEdit()
        self.vlayout.addWidget(self.overlaysPathEdit)

        # temp path
        self.vlayout.addWidget(QLabel('Temporary Path (relative to working path)'))
        self.tmpPathEdit = QLineEdit()
        self.vlayout.addWidget(self.tmpPathEdit)

        # preview image path
        self.vlayout.addWidget(QLabel('Preview Image Path (relative to working path)'))
        self.previewImagePathEdit = QLineEdit()
        self.vlayout.addWidget(self.previewImagePathEdit)

        # previews output path
        self.vlayout.addWidget(QLabel('Previews Output Path (relative to working path)'))
        self.previewsPathEdit = QLineEdit()
        self.vlayout.addWidget(self.previewsPathEdit)

        # paper size
        self.vlayout.addWidget(QLabel('Paper Size'))
        self.paperSizeCombobox = QComboBox()
        self.paperSizeCombobox.setEditable(True)
        for page in ['A4', 'A5', 'Letter', 'Legal', 'Executive', 'B5', 'JisB5', 'Postcard', 'AnsiA', 'AnsiB']:
            self.paperSizeCombobox.addItem(page)
        self.vlayout.addWidget(self.paperSizeCombobox)

        # custom page width
        self.vlayout.addWidget(QLabel("Custom Page Width (mm, used when configured Paper Size isn't available)"))
        self.customPageWidthBox = QSpinBox()
        self.customPageWidthBox.setRange(1, 2000)
        self.vlayout.addWidget(self.customPageWidthBox)

        # custom page height
        self.vlayout.addWidget(QLabel("Custom Page Height (mm, used when configured Paper Size isn't available)"))
        self.customPageHeightBox = QSpinBox()
        self.customPageHeightBox.setRange(1, 2000)
        self.vlayout.addWidget(self.customPageHeightBox)

        # custom page name
        self.vlayout.addWidget(QLabel('Custom Page Name'))
        self.customPageNameEdit = QLineEdit()
        self.vlayout.addWidget(self.customPageNameEdit)

        # capture delay
        self.vlayout.addWidget(QLabel('Capture Delay (seconds)'))
        self.captureDelayBox = QSpinBox()
        self.captureDelayBox.setRange(0, 3600)
        self.vlayout.addWidget(self.captureDelayBox)

        # zone tolerance (for alignment and zone detection)
        self.vlayout.addWidget(QLabel('Zone Tolerance (0.0 to 1.0)'))
        self.zoneToleranceBox = QDoubleSpinBox()
        self.zoneToleranceBox.setRange(0.0, 1.0)
        self.zoneToleranceBox.setDecimals(3)
        self.zoneToleranceBox.setSingleStep(0.005)
        self.vlayout.addWidget(self.zoneToleranceBox)

        # mock camera
        self.mockCameraCheckbox = QCheckBox('Use Mock Camera')
        self.vlayout.addWidget(self.mockCameraCheckbox)

        # toggle standalone mode
        self.standaloneModeCheckbox = QCheckBox('Standalone Mode')
        self.vlayout.addWidget(self.standaloneModeCheckbox)

        # toggle printing
        self.printCheckbox = QCheckBox('Enable Printing')
        self.vlayout.addWidget(self.printCheckbox)

        # toggle upload
        self.uploadCheckbox = QCheckBox('Enable Upload')
        self.vlayout.addWidget(self.uploadCheckbox)

        #---------------------------------------------------------
        
        self.hlayout = QHBoxLayout()
        self.vlayout.addLayout(self.hlayout)

        # cancel button
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.setMaximumWidth(150)
        self.cancelButton.clicked.connect(self.close)
        self.hlayout.addWidget(self.cancelButton)

        # save button
        self.saveButton = QPushButton('Save')
        self.saveButton.setMaximumWidth(150)
        self.saveButton.clicked.connect(self.saveConfig)
        self.hlayout.addWidget(self.saveButton)

        
    def loadConfig(self):
        # load .env
        if load_dotenv(envPath):
            DB_HOST = os.getenv("DB_HOST")
            DB_KEY = os.getenv("DB_KEY")
        else:
            DB_HOST = ''
            DB_KEY = ''
        self.dbhostEdit.setText(DB_HOST)
        self.dbkeyEdit.setText(DB_KEY)

        
        # load config
        with open(self.configPath, 'r') as file:
            data = json.load(file)

        self.printerNameEdit.setText(str(data.get('printerName', '')))
        self.workingPathEdit.setText(str(data.get('workingPath', '')))
        self.collagePathEdit.setText(str(data.get('collagePath', '')))
        self.lutsPathEdit.setText(str(data.get('lutsPath', '')))
        self.overlaysPathEdit.setText(str(data.get('overlaysPath', '')))
        self.tmpPathEdit.setText(str(data.get('tmpPath', '')))
        self.previewImagePathEdit.setText(str(data.get('previewImagePath', '')))
        self.previewsPathEdit.setText(str(data.get('previewsPath', '')))

        paperSize = str(data.get('paperSize', ''))
        if paperSize and self.paperSizeCombobox.findText(paperSize) < 0:
            self.paperSizeCombobox.addItem(paperSize)
        self.paperSizeCombobox.setCurrentText(paperSize)

        self.customPageWidthBox.setValue(int(data.get('customPageWidth', 100)))
        self.customPageHeightBox.setValue(int(data.get('customPageHeight', 148)))
        self.customPageNameEdit.setText(str(data.get('customPageName', 'Custom')))
        self.captureDelayBox.setValue(int(data.get('captureDelay', 3)))
        self.zoneToleranceBox.setValue(float(data.get('zoneTolerance', 0.02)))

        self.mockCameraCheckbox.setChecked(bool(data.get('mockCamera', False)))
        self.standaloneModeCheckbox.setChecked(bool(data.get('standaloneMode', False)))
        self.printCheckbox.setChecked(bool(data.get('print', True)))
        self.uploadCheckbox.setChecked(bool(data.get('upload', True)))

    def saveConfig(self):
        paperSize = self.paperSizeCombobox.currentText().strip()
        if paperSize == '':
            QMessageBox.warning(self, 'Invalid value', 'Paper Size cannot be empty.')
            return

        data = {
            'printerName': self.printerNameEdit.text().strip(),
            'workingPath': self.workingPathEdit.text().strip(),
            'collagePath': self.collagePathEdit.text().strip(),
            'lutsPath': self.lutsPathEdit.text().strip(),
            'overlaysPath': self.overlaysPathEdit.text().strip(),
            'tmpPath': self.tmpPathEdit.text().strip(),
            'previewImagePath': self.previewImagePathEdit.text().strip(),
            'previewsPath': self.previewsPathEdit.text().strip(),
            'paperSize': paperSize,
            'customPageWidth': self.customPageWidthBox.value(),
            'customPageHeight': self.customPageHeightBox.value(),
            'customPageName': self.customPageNameEdit.text().strip(),
            'captureDelay': self.captureDelayBox.value(),
            'zoneTolerance': self.zoneToleranceBox.value(),
            'mockCamera': self.mockCameraCheckbox.isChecked(),
            'standaloneMode': self.standaloneModeCheckbox.isChecked(),
            'print': self.printCheckbox.isChecked(),
            'upload': self.uploadCheckbox.isChecked(),
        }
        
        chgSettings = changedSettings()
        chgSettings.printer = (
            data['printerName'] != config.data['printerName'] or
            data['paperSize'] != config.data['paperSize'] or
            data['customPageWidth'] != config.data['customPageWidth'] or
            data['customPageWidth'] != config.data['customPageWidth'] or
            data['customPageName'] != config.data['customPageName'] or
            data['print'] != config.data['print']
        )
        chgSettings.lutoverlay = (
            data['zoneTolerance'] != config.data['zoneTolerance'] or
            data['previewsPath'] != config.data['previewsPath'] or
            data['lutsPath'] != config.data['lutsPath'] or
            data['overlaysPath'] != config.data['overlaysPath'] or
            data['workingPath'] != config.data['workingPath']
        )
        
        chgSettings.camera = data['mockCamera'] != config.data['mockCamera']
        
        chgSettings.gui = chgSettings.lutoverlay
        
        chgSettings.restart = data['standaloneMode']!=config.data['standaloneMode']
        
        # warn user that saving will cause a restart
        if chgSettings.restart:
            res = QMessageBox.question(self, 'WARNING', 'Toggling Standalone Mode will trigger a restart', QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Cancel)
            if res!=QMessageBox.StandardButton.Save:
                return
        
        # block save if upload is toggled and cannot connect to supabase
        if self.uploadCheckbox.isChecked() and not upload.testconnection(self.dbhostEdit.text().strip(), self.dbkeyEdit.text().strip()):
            res = QMessageBox.question(self, 'WARNING', 'ERROR: supabase configuration is invalid, enter correct host and api key or disable uploads', QMessageBox.StandardButton.Ok)
            return
        
            
        # update .env
        set_key(self.envPath, 'DB_HOST', self.dbhostEdit.text().strip())
        set_key(self.envPath, 'DB_KEY', self.dbkeyEdit.text().strip())

        # update config
        with open(self.configPath, 'w') as file:
            json.dump(data, file, indent=4)

        # log settings change
        logger.post(f'INFO: settings updated', loglevels.WARNING)
    
        # trigger cascading updates
        importlib.reload(config)    # reload config first as upload checks upload toggle in config
        importlib.reload(upload)
        print('\nUpdate Settings')
        print(f'camera: {chgSettings.camera}\ngui: {chgSettings.gui}\nprinter: {chgSettings.printer}\nlutoverlay: {chgSettings.lutoverlay}\nrestart: {chgSettings.restart}')
        signals.settingSignal.emit(chgSettings)
        
        