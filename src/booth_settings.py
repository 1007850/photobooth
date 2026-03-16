import json
import sys
from pathlib import Path
import booth_config as config
import importlib
from booth_messaging import signals, changedSettings

from PyQt6.QtWidgets import QLabel, QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget


class SettingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.configPath = self.getConfigPath()
        self.initWindow()
        self.loadConfig()
        self.show()

    def getConfigPath(self):
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / 'config.json'
        return Path(__file__).parent.resolve() / 'config.json'

    def initWindow(self):
        self.setWindowTitle('Photobooth Settings')

        # layouts
        self.vlayout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.vlayout)
        self.setCentralWidget(self.central_widget)

        # printer name
        self.vlayout.addWidget(QLabel('Printer Name'))
        self.printerNameEdit = QLineEdit()
        self.vlayout.addWidget(self.printerNameEdit)
        
        # working path (root dir)
        self.vlayout.addWidget(QLabel('Working Path (root directory for other paths)'))
        self.workingPathEdit = QLineEdit()
        self.vlayout.addWidget(self.workingPathEdit)

        # collage path
        self.vlayout.addWidget(QLabel('Collage Path'))
        self.collagePathEdit = QLineEdit()
        self.vlayout.addWidget(self.collagePathEdit)

        # LUTs path
        self.vlayout.addWidget(QLabel('LUTs Path'))
        self.lutsPathEdit = QLineEdit()
        self.vlayout.addWidget(self.lutsPathEdit)

        # overlays path
        self.vlayout.addWidget(QLabel('Overlays Path'))
        self.overlaysPathEdit = QLineEdit()
        self.vlayout.addWidget(self.overlaysPathEdit)

        # temp path
        self.vlayout.addWidget(QLabel('Temporary Path'))
        self.tmpPathEdit = QLineEdit()
        self.vlayout.addWidget(self.tmpPathEdit)

        # preview image path
        self.vlayout.addWidget(QLabel('Preview Image Path'))
        self.previewImagePathEdit = QLineEdit()
        self.vlayout.addWidget(self.previewImagePathEdit)

        # previews output path
        self.vlayout.addWidget(QLabel('Previews Output Path'))
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
        self.vlayout.addWidget(QLabel('Custom Page Width (mm)'))
        self.customPageWidthBox = QSpinBox()
        self.customPageWidthBox.setRange(1, 2000)
        self.vlayout.addWidget(self.customPageWidthBox)

        # custom page height
        self.vlayout.addWidget(QLabel('Custom Page Height (mm)'))
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

        # save button
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.saveConfig)
        self.vlayout.addWidget(self.saveButton)

        # save status
        self.statusLabel = QLabel('')
        self.vlayout.addWidget(self.statusLabel)

    def loadConfig(self):
        if not self.configPath.exists():
            self.statusLabel.setText(f'Config not found: {self.configPath}')
            return

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
            data['customPageName'] != config.data['customPageName']
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

        with open(self.configPath, 'w') as file:
            json.dump(data, file, indent=4)

        self.statusLabel.setText(f'Saved: {self.configPath}')
    
        importlib.reload(config)
        
        print('\nUpdate Settings')
        print(f'camera: {chgSettings.camera}\ngui: {chgSettings.gui}\nprinter: {chgSettings.printer}\nlutoverlay: {chgSettings.lutoverlay}\nrestart: {chgSettings.restart}')
        signals.settingSignal.emit(chgSettings)

