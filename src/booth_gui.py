from booth_messaging import logger, signals
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QLabel, QComboBox, QApplication, QVBoxLayout, QHBoxLayout, QSpinBox, QSpacerItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from booth_ctrl import ctrl
from booth_gui_components import imageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.lutboxes: list[imageBox] = []
        self.overlayboxes: list[imageBox] = []
        self.ctrl = ctrl()
        self.initWindow()
        self.show()
        # self.ctrl.setPrinteSettings()
        
        # signal to re-initialise gui - used when new settings are applied
        signals.guiSignal.connect(self.reinitWindow)
    
    def reinitWindow(self, s: str):
        self.central_widget.destroy()
        self.lutboxes: list[imageBox] = []
        self.overlayboxes: list[imageBox] = []
        self.initWindow()
    
    def initWindow(self):
        self.setWindowTitle("Photobooth by Roger")
        
        # create and set gridlayout
        self.layout: QHBoxLayout = QHBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        #--------------------------------------------------
        
        self.leftLayout = QVBoxLayout()
        self.layout.addLayout(self.leftLayout)
        self.rightLayout = QVBoxLayout()
        self.layout.addLayout(self.rightLayout)

        self.leftLayout.addLayout(self.init_control_widget())
        self.rightLayout.addLayout(self.init_log_widget())
        if self.ctrl.luts!={} and self.ctrl.overlays!={}:
            self.leftLayout.addLayout(self.init_luts_widget())
            self.rightLayout.addLayout(self.init_overlays_widget())
        
        self.layout.setStretchFactor(self.leftLayout, 3)
        self.layout.setStretchFactor(self.rightLayout, self.rightLayout.count())


    def init_control_widget(self) -> QGridLayout:
        self.controlLayout = QGridLayout()

        # reload cam button
        reloadButton = QPushButton("Reload Cam")
        reloadButton.clicked.connect(self.ctrl.reload_cam)
        self.controlLayout.addWidget(reloadButton, 0, 0)
        
        # capture preview button
        capturePreviewButton = QPushButton("Get Previews")
        capturePreviewButton.clicked.connect(lambda: self.ctrl.capturePreviewImage(self.lutboxes))
        self.controlLayout.addWidget(capturePreviewButton, 1, 0)
        
        # exit app button
        exitButton = QPushButton("Unload Cam")
        exitButton.clicked.connect(self.ctrl.exit)
        self.controlLayout.addWidget(exitButton, 2, 0)
        
        #--------------------------------------------------
        
        # lut combobox label
        lutselLabel = QLabel("Colour: ")
        lutselLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.controlLayout.addWidget(lutselLabel, 0, 1)

        # overlay combobox label
        overlayselLabel = QLabel("Frame: ")
        overlayselLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.controlLayout.addWidget(overlayselLabel, 1, 1)
        
        # number of prints label
        nPrintsLabel = QLabel("Print Count: ")
        nPrintsLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.controlLayout.addWidget(nPrintsLabel, 2, 1)

        #--------------------------------------------------
        
        if self.ctrl.luts!={} and self.ctrl.overlays!={}:

            # lut selector combobox
            self.lutCombobox = QComboBox()
            for lut in sorted(self.ctrl.luts.values(), key=lambda x: x.name):
                self.lutCombobox.addItem(lut.name)
            self.lutCombobox.setCurrentText(self.ctrl.selectedLut.name)
            self.lutCombobox.currentIndexChanged.connect(lambda: self.ctrl.handleLUTComboboxChange(self.lutCombobox.currentText(), self.lutboxes))
            self.controlLayout.addWidget(self.lutCombobox, 0, 2)
            
            # overlay selector combobox
            self.overlayCombobox = QComboBox()
            for overlay in sorted(self.ctrl.overlays.values(), key=lambda x: x.name):
                self.overlayCombobox.addItem(overlay.name)
            self.overlayCombobox.setCurrentText(self.ctrl.selectedOverlay.name)
            self.overlayCombobox.currentIndexChanged.connect(lambda: self.ctrl.handleOverlayComboboxChange(self.overlayCombobox.currentText(), self.overlayboxes))
            self.controlLayout.addWidget(self.overlayCombobox, 1, 2)
        
        # number of prints SpinBox
        nPrintsCombobox = QSpinBox()
        nPrintsCombobox.setRange(1,1000)
        nPrintsCombobox.valueChanged.connect(lambda: self.ctrl.prn.setNumPrints(nPrintsCombobox.value()))
        self.controlLayout.addWidget(nPrintsCombobox, 2, 2)

        #--------------------------------------------------

        # single shot button
        singleShotButton = QPushButton("Single Shot")
        singleShotButton.clicked.connect(self.ctrl.single_shot)
        self.controlLayout.addWidget(singleShotButton, 0, 3)
        
        # series capture button
        captureButton = QPushButton("Capture")
        captureButton.clicked.connect(self.ctrl.capture_handler)
        self.controlLayout.addWidget(captureButton, 1, 3)
        
        #--------------------------------------------------

        # export poster button
        exportButton = QPushButton("Export")
        exportButton.clicked.connect(self.ctrl.export_poster)
        self.controlLayout.addWidget(exportButton, 0, 4)
        
        # preview last button
        previewLastButton = QPushButton("Preview Last")
        previewLastButton.clicked.connect(self.ctrl.preview_last)
        self.controlLayout.addWidget(previewLastButton, 1, 4)
        
        # upload last button
        uploadLastButton = QPushButton("Upload Last")
        uploadLastButton.clicked.connect(self.ctrl.upload_last)
        self.controlLayout.addWidget(uploadLastButton, 2, 4)

        #--------------------------------------------------

        # default print button
        printLastButton = QPushButton("Print Last")
        printLastButton.clicked.connect(self.ctrl.print_last)
        self.controlLayout.addWidget(printLastButton, 0, 5)
        
        # manual print button
        manualPrintButton = QPushButton("Manual Print")
        manualPrintButton.clicked.connect(self.ctrl.selectFilePrint)
        self.controlLayout.addWidget(manualPrintButton, 1, 5)
        
        # print settings button
        printSettingsButton = QPushButton("Print Settings")
        printSettingsButton.clicked.connect(self.ctrl.setPrinteSettings)
        self.controlLayout.addWidget(printSettingsButton, 2, 5)
        
        #--------------------------------------------------

        # settings button
        settingsButton = QPushButton("Settings")
        settingsButton.clicked.connect(self.ctrl.open_settings)
        self.controlLayout.addWidget(settingsButton, 0, 6)
        
        # quit button
        quitButton = QPushButton("Quit")
        quitButton.clicked.connect(self.ctrl.handleQuit)
        self.controlLayout.addWidget(quitButton, 1, 6)
        
        #--------------------------------------------------

        # min column width
        for i in range(self.controlLayout.columnCount()):
            self.controlLayout.setColumnMinimumWidth(i, 130)
        
        # spacer
        self.controlLayout.setColumnStretch(self.controlLayout.columnCount(), 1)
    
        return self.controlLayout
        

    # preview overlays
    def init_overlays_widget(self) -> QHBoxLayout:
        self.overlayLayout = QHBoxLayout()
        for overlay in sorted(self.ctrl.overlays.values(), key=lambda x: x.name):
            pb = imageBox(overlay.name, lambda x: self.ctrl.handlePreviewClick(x, self.overlayboxes, self.overlayCombobox, self.ctrl.setOverlay))
            pb.loadQIM(self.ctrl.exportOverlayPreview(overlay))
            pb.toggleBorder(False)
            self.overlayboxes.append(pb)
        for pb in self.overlayboxes:
            self.overlayLayout.addWidget(pb)
        self.overlayboxes[0].toggleBorder(True)
        return self.overlayLayout
        
    # preview luts
    def init_luts_widget(self) -> QGridLayout:
        self.lutLayout = QGridLayout()
        # create lut preview boxes
        for lut in sorted(self.ctrl.luts.values(), key=lambda x: x.name):
            pb = imageBox(lut.name, lambda x: self.ctrl.handlePreviewClick(x, self.lutboxes, self.lutCombobox, self.ctrl.setLut))
            pb.toggleBorder(False)
            self.lutboxes.append(pb)
        # gridbox just for lut preview scaling
        for idx,pb in enumerate(self.lutboxes):
            self.lutLayout.addWidget(pb, idx//3, idx%3, 1, 1)
        self.lutboxes[0].toggleBorder(True)
        
        # load images into boxes
        self.ctrl.loadPreviewImages(self.lutboxes, False)
        return self.lutLayout

    # logging
    def init_log_widget(self) -> QVBoxLayout:
        self.logLayout = QVBoxLayout()
        for logline in logger.loglines:
            self.logLayout.addWidget(logline, alignment=Qt.AlignmentFlag.AlignLeft)
        logger.update_log_stream()
        return self.logLayout
    


def run(app: QApplication):
    QApplication.setFont(QFont("Times", 12))
    window = MainWindow()
    app.exec()

if __name__=="__main__":
    thisapp = QApplication([])
    run(thisapp)