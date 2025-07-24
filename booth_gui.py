from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtMultimedia import QSoundEffect
from booth_ctrl import ctrl
from pathlib import Path
from threading import Thread, Timer
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl = ctrl()
        self.initWindow()
        self.show()
        
    
    def initWindow(self):
        self.setWindowTitle("Photobooth by Roger")
        
        # create and set gridlayout
        self.layout: QGridLayout = QGridLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        # reload cam button
        reloadButton = QPushButton("Reload Camera")
        reloadButton.clicked.connect(self.ctrl.reload_cam)
        self.layout.addWidget(reloadButton, 0, 0)
        
        # run auto expose button
        exposeButton = QPushButton("Expose")
        exposeButton.clicked.connect(self.ctrl.expose)
        self.layout.addWidget(exposeButton, 1, 0)
        
        # exit app button
        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.ctrl.exit)
        self.layout.addWidget(exitButton, 2, 0)
        
        # single shot button
        singleShotButton = QPushButton("Single Shot")
        singleShotButton.clicked.connect(self.ctrl.single_shot)
        self.layout.addWidget(singleShotButton, 0, 1)
        
        # series capture button
        captureButton = QPushButton("Capture")
        captureButton.clicked.connect(self.ctrl.capture_handler)
        self.layout.addWidget(captureButton, 1, 1)
        
        # auto exposure toggle
        autoCheckbox = QCheckBox("auto exposure")
        autoCheckbox.setChecked(True)
        autoCheckbox.setMinimumSize(20,20)
        autoCheckbox.toggled.connect(lambda x: self.ctrl.toggle_autosw(x))
        self.layout.addWidget(autoCheckbox, 2, 1)
        
        # export poster button
        exportButton = QPushButton("Export")
        exportButton.clicked.connect(self.ctrl.export_poster)
        self.layout.addWidget(exportButton, 0, 2)
        
        # preview last button
        previewLastButton = QPushButton("Preview Last")
        previewLastButton.clicked.connect(self.ctrl.preview_last)
        self.layout.addWidget(previewLastButton, 1, 2)

        # default print button
        printLastButton = QPushButton("Print Last")
        printLastButton.clicked.connect(self.ctrl.print_last)
        self.layout.addWidget(printLastButton, 0, 3)
        
        # number of prints combobox
        self.nPrintsCombobox = QComboBox()
        for n in range(10):
            self.nPrintsCombobox.addItem(str(n+1))
        self.nPrintsCombobox.currentIndexChanged.connect(lambda: self.ctrl.prn.setNumPrints(self.nPrintsCombobox.currentIndex()+1))
        self.layout.addWidget(self.nPrintsCombobox, 1, 3)

        # manual print button
        manualPrintButton = QPushButton("Manual Print")
        manualPrintButton.clicked.connect(self.ctrl.selectFilePrint)
        self.layout.addWidget(manualPrintButton, 2, 3)
        


            


if __name__=="__main__":
    app = QApplication([])
    QApplication.setFont(QFont("Times", 20))
    window = MainWindow()
    app.exec()