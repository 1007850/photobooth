import json
import booth_config as config
import importlib
from booth_messaging import signals, changedSettings, logger, loglevels
from booth_upload import envPath
from dotenv import load_dotenv, set_key
import os
import booth_upload as upload

from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea
import booth_styling as styling
from booth_gui_components import BlockLayout


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
        self.setStyleSheet(styling.SETTINGS)
        self.setMinimumWidth(700)

        # layouts
        # outer widget and layout
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)

        # scroll area and widget
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.mainLayout.addWidget(self.scrollArea)  # test layout or widget
        self.inputWidget = QWidget()
        self.inputWidget.setMaximumWidth(600)
        self.scrollArea.setWidget(self.inputWidget)

        # input layout
        self.inputLayout = QVBoxLayout()
        self.inputWidget.setLayout(self.inputLayout)

        titleLabel = QLabel('Settings')
        titleLabel.setObjectName('heading')
        self.inputLayout.addWidget(titleLabel)

        subtitleLabel = QLabel('Update paths, print settings, and upload options.')
        # subtitleLabel.setObjectName('subtle')
        self.inputLayout.addWidget(subtitleLabel)
        
        # DB_HOST
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('domain/url'))
        self.dbhostEdit = QLineEdit()
        blockLayout.addWidget(self.dbhostEdit)
        
        # DB_KEY
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('api key'))
        self.dbkeyEdit = QLineEdit()
        blockLayout.addWidget(self.dbkeyEdit)

        # printer name
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Printer Name'))
        self.printerNameEdit = QLineEdit()
        blockLayout.addWidget(self.printerNameEdit)
        
        # working path (root dir)
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Working Path (root directory for other paths)'))
        self.workingPathEdit = QLineEdit()
        blockLayout.addWidget(self.workingPathEdit)

        # collage path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Collage Path (relative to working path)'))
        self.collagePathEdit = QLineEdit()
        blockLayout.addWidget(self.collagePathEdit)

        # LUTs path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('LUTs Path (relative to working path)'))
        self.lutsPathEdit = QLineEdit()
        blockLayout.addWidget(self.lutsPathEdit)

        # overlays path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Overlays Path (relative to working path)'))
        self.overlaysPathEdit = QLineEdit()
        blockLayout.addWidget(self.overlaysPathEdit)

        # temp path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Temporary Path (relative to working path)'))
        self.tmpPathEdit = QLineEdit()
        blockLayout.addWidget(self.tmpPathEdit)

        # preview image path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Preview Image Path (relative to working path)'))
        self.previewImagePathEdit = QLineEdit()
        blockLayout.addWidget(self.previewImagePathEdit)

        # previews output path
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Previews Output Path (relative to working path)'))
        self.previewsPathEdit = QLineEdit()
        blockLayout.addWidget(self.previewsPathEdit)

        # paper size
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Paper Size'))
        self.paperSizeCombobox = QComboBox()
        self.paperSizeCombobox.setEditable(True)
        for page in ['A4', 'A5', 'Letter', 'Legal', 'Executive', 'B5', 'JisB5', 'Postcard', 'AnsiA', 'AnsiB']:
            self.paperSizeCombobox.addItem(page)
        blockLayout.addWidget(self.paperSizeCombobox)

        # custom page width
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel("Custom Page Width (mm, used when configured Paper Size isn't available)"))
        self.customPageWidthBox = QSpinBox()
        self.customPageWidthBox.setRange(1, 2000)
        blockLayout.addWidget(self.customPageWidthBox)

        # custom page height
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel("Custom Page Height (mm, used when configured Paper Size isn't available)"))
        self.customPageHeightBox = QSpinBox()
        self.customPageHeightBox.setRange(1, 2000)
        blockLayout.addWidget(self.customPageHeightBox)

        # custom page name
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Custom Page Name'))
        self.customPageNameEdit = QLineEdit()
        blockLayout.addWidget(self.customPageNameEdit)

        # capture delay
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Capture Delay (seconds)'))
        self.captureDelayBox = QSpinBox()
        self.captureDelayBox.setRange(0, 3600)
        blockLayout.addWidget(self.captureDelayBox)

        # zone tolerance (for alignment and zone detection)
        blockLayout = BlockLayout(self.inputLayout)
        blockLayout.addWidget(QLabel('Zone Tolerance (0.0 to 1.0)'))
        self.zoneToleranceBox = QDoubleSpinBox()
        self.zoneToleranceBox.setRange(0.0, 1.0)
        self.zoneToleranceBox.setDecimals(3)
        self.zoneToleranceBox.setSingleStep(0.005)
        blockLayout.addWidget(self.zoneToleranceBox)

        # mock camera
        self.mockCameraCheckbox = QCheckBox('Use Mock Camera')
        self.mockCameraCheckbox.setObjectName('settingblock')
        self.inputLayout.addWidget(self.mockCameraCheckbox)

        # toggle standalone mode
        self.standaloneModeCheckbox = QCheckBox('Standalone Mode')
        self.standaloneModeCheckbox.setObjectName('settingblock')
        self.inputLayout.addWidget(self.standaloneModeCheckbox)

        # toggle printing
        self.printCheckbox = QCheckBox('Enable Printing')
        self.printCheckbox.setObjectName('settingblock')
        self.inputLayout.addWidget(self.printCheckbox)

        # toggle upload
        self.uploadCheckbox = QCheckBox('Enable Upload')
        self.uploadCheckbox.setObjectName('settingblock')
        self.inputLayout.addWidget(self.uploadCheckbox)

        #---------------------------------------------------------
        
        self.savelayout = QHBoxLayout()
        self.mainLayout.addLayout(self.savelayout)

        # cancel button
        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.setMaximumWidth(150)
        self.cancelButton.clicked.connect(self.close)
        self.savelayout.addWidget(self.cancelButton)

        # save button
        self.saveButton = QPushButton('Save')
        self.saveButton.setMaximumWidth(150)
        self.saveButton.clicked.connect(self.saveConfig)
        self.savelayout.addWidget(self.saveButton)
        

        
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
        
        
