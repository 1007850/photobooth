from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QLabel, QComboBox, QApplication
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
        self.ctrl.setPrinteSettings()
        
    
    def initWindow(self):
        self.setWindowTitle("Photobooth by Roger")
        
        # create and set gridlayout
        self.layout: QGridLayout = QGridLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        #--------------------------------------------------

        # reload cam button
        reloadButton = QPushButton("Reload Cam")
        reloadButton.clicked.connect(self.ctrl.reload_cam)
        self.layout.addWidget(reloadButton, 0, 0)
        
        # capture preview button
        capturePreviewButton = QPushButton("Get Previews")
        capturePreviewButton.clicked.connect(lambda: self.ctrl.capturePreviewImage(self.lutboxes))
        self.layout.addWidget(capturePreviewButton, 1, 0)
        
        # exit app button
        exitButton = QPushButton("Unload Cam")
        exitButton.clicked.connect(self.ctrl.exit)
        self.layout.addWidget(exitButton, 2, 0)
        
        #--------------------------------------------------
        
        # lut combobox label
        lutselLabel = QLabel("Colour: ")
        lutselLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(lutselLabel, 0, 1)

        # overlay combobox label
        overlayselLabel = QLabel("Frame: ")
        overlayselLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(overlayselLabel, 1, 1)
        
        # number of prints label
        nPrintsLabel = QLabel("Print Count: ")
        nPrintsLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(nPrintsLabel, 2, 1)

        #--------------------------------------------------
        
        # lut selector combobox
        self.lutCombobox = QComboBox()
        for lut in sorted(self.ctrl.luts.values(), key=lambda x: x.name):
            self.lutCombobox.addItem(lut.name)
        self.lutCombobox.setCurrentText(self.ctrl.selectedLut.name)
        self.lutCombobox.currentIndexChanged.connect(lambda: self.ctrl.handleLUTComboboxChange(self.lutCombobox.currentText(), self.lutboxes))
        self.layout.addWidget(self.lutCombobox, 0, 2)
        
        # overlay selector combobox
        self.overlayCombobox = QComboBox()
        for overlay in sorted(self.ctrl.overlays.values(), key=lambda x: x.name):
            self.overlayCombobox.addItem(overlay.name)
        self.overlayCombobox.setCurrentText(self.ctrl.selectedOverlay.name)
        self.overlayCombobox.currentIndexChanged.connect(lambda: self.ctrl.handleOverlayComboboxChange(self.overlayCombobox.currentText(), self.overlayboxes))
        self.layout.addWidget(self.overlayCombobox, 1, 2)
        
        # number of prints combobox
        nPrintsCombobox = QComboBox()
        for n in range(10):
            nPrintsCombobox.addItem(str(n+1))
        nPrintsCombobox.currentIndexChanged.connect(lambda: self.ctrl.prn.setNumPrints(nPrintsCombobox.currentIndex()+1))
        self.layout.addWidget(nPrintsCombobox, 2, 2)

        #--------------------------------------------------

        # single shot button
        singleShotButton = QPushButton("Single Shot")
        singleShotButton.clicked.connect(self.ctrl.single_shot)
        self.layout.addWidget(singleShotButton, 0, 3)
        
        # series capture button
        captureButton = QPushButton("Capture")
        captureButton.clicked.connect(self.ctrl.capture_handler)
        self.layout.addWidget(captureButton, 1, 3)
        
        #--------------------------------------------------

        # export poster button
        exportButton = QPushButton("Export")
        exportButton.clicked.connect(self.ctrl.export_poster)
        self.layout.addWidget(exportButton, 0, 4)
        
        # preview last button
        previewLastButton = QPushButton("Preview Last")
        previewLastButton.clicked.connect(self.ctrl.preview_last)
        self.layout.addWidget(previewLastButton, 1, 4)
        
        # upload last button
        uploadLastButton = QPushButton("Upload Last")
        uploadLastButton.clicked.connect(self.ctrl.upload_last)
        self.layout.addWidget(uploadLastButton, 2, 4)

        #--------------------------------------------------

        # default print button
        printLastButton = QPushButton("Print Last")
        printLastButton.clicked.connect(self.ctrl.print_last)
        self.layout.addWidget(printLastButton, 0, 5)
        
        # manual print button
        manualPrintButton = QPushButton("Manual Print")
        manualPrintButton.clicked.connect(self.ctrl.selectFilePrint)
        self.layout.addWidget(manualPrintButton, 1, 5)
        
        # print settings button
        printSettingsButton = QPushButton("Print Settings")
        printSettingsButton.clicked.connect(self.ctrl.setPrinteSettings)
        self.layout.addWidget(printSettingsButton, 2, 5)
        
        #--------------------------------------------------
        
        # preview luts
        for lut in sorted(self.ctrl.luts.values(), key=lambda x: x.name):
            pb = imageBox(lut.name, lambda x: self.ctrl.handlePreviewClick(x, self.lutboxes, self.lutCombobox, self.ctrl.setLut))
            pb.toggleBorder(False)
            self.lutboxes.append(pb)
        for idx,pb in enumerate(self.lutboxes):
            self.layout.addWidget(pb, idx//3+3, idx%3*2, 1, 2)
        self.lutboxes[0].toggleBorder(True)
        
        # preview overlays
        for overlay in sorted(self.ctrl.overlays.values(), key=lambda x: x.name):
            pb = imageBox(overlay.name, lambda x: self.ctrl.handlePreviewClick(x, self.overlayboxes, self.overlayCombobox, self.ctrl.setOverlay))
            pb.loadQIM(self.ctrl.exportOverlayPreview(overlay))
            pb.toggleBorder(False)
            self.overlayboxes.append(pb)
        for idx,pb in enumerate(self.overlayboxes):
            self.layout.addWidget(pb, 3, idx*2+6, 3, 2)
        self.overlayboxes[0].toggleBorder(True)
        
        # set column sizing
        for i in range(6+len(self.overlayboxes)*2):
            self.layout.setColumnStretch(i,1)


if __name__=="__main__":
    app = QApplication([])
    QApplication.setFont(QFont("Times", 12))
    window = MainWindow()
    app.exec()