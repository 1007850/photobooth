from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel, QApplication, QHBoxLayout, QVBoxLayout, QSpinBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from booth_ctrl import ctrl
from booth_messaging import logger, signals
import booth_styling as styling



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl = ctrl()
        self.initWindow()
        self.show()
        self.setFocus()
        
        signals.guiSignal.connect(self.initWindow)
    
    def initWindow(self):
        self.setWindowTitle("Photobooth by Roger")
        self.setStyleSheet(styling.MAIN)
        # self.setMinimumSize(900, 600)
        
        self.layout: QHBoxLayout = QHBoxLayout()
        # self.layout.setContentsMargins(12, 12, 12, 12)
        # self.layout.setSpacing(12)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        #--------------------------------------------------

        self.leftPanel = QWidget()
        # self.leftPanel.setObjectName("panel")
        self.leftLayout = QVBoxLayout(self.leftPanel)
        # self.leftLayout.setContentsMargins(18, 18, 18, 18)
        # self.leftLayout.setSpacing(10)
        self.layout.addWidget(self.leftPanel)
        
        
        #--------------------------------------------------
        
        # instruction label
        if self.ctrl.luts != {}:
            nbounds = next(iter(self.ctrl.overlays.values())).nbounds
            instructionLabel = QLabel(f'''There will be {nbounds} shots.
    {self.ctrl.delay}-second countdown before every shot.

    After processing, a QR code will appear with the link to your photo.
    Please have your camera ready to scan it.

    Once ready, press start and the countdown will begin.''')
            instructionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.leftLayout.addWidget(instructionLabel)

        
        # number of prints label
        nPrintsLabel = QLabel("Print Count: ")
        nPrintsLabel.setMaximumWidth(150)
        nPrintsLabel.setMaximumHeight(20)
        self.leftLayout.addWidget(nPrintsLabel, alignment=Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignCenter)

        # number of prints SpinBox
        nPrintsCombobox = QSpinBox()
        nPrintsCombobox.setMaximumWidth(150)
        nPrintsCombobox.setRange(1,1000)
        nPrintsCombobox.valueChanged.connect(lambda: self.ctrl.prn.setNumPrints(nPrintsCombobox.value()))
        self.leftLayout.addWidget(nPrintsCombobox, alignment=Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignCenter)

        # start button
        startButton = QPushButton("Start")
        startButton.setMaximumWidth(150)
        startButton.clicked.connect(self.ctrl.startFlow)
        self.leftLayout.addWidget(startButton, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # last QR button
        lastQRButton =QPushButton('View Last QR')
        lastQRButton.setMaximumWidth(200)
        lastQRButton.clicked.connect(self.ctrl.handleLastUploadQR)
        self.leftLayout.addWidget(lastQRButton, alignment=Qt.AlignmentFlag.AlignCenter)
        
        #--------------------------------------------------
        
        # admin row
        self.adminLayout = QHBoxLayout()
        self.adminWidget = QWidget()
        self.adminWidget.setLayout(self.adminLayout)
        self.leftLayout.addWidget(self.adminWidget)
        
        # settings button
        settingsButton = QPushButton("Settings")
        settingsButton.setMaximumWidth(150)
        settingsButton.clicked.connect(self.ctrl.handleOpenSettings)
        self.adminLayout.addWidget(settingsButton)
        
        # quit button
        quitButton = QPushButton("Quit")
        quitButton.setMaximumWidth(150)
        quitButton.clicked.connect(self.ctrl.handleQuit)
        self.adminLayout.addWidget(quitButton)

        #--------------------------------------------------
        
        # for i in range(self.leftLayout.count()):
        #     self.leftLayout.setStretch(i, 0)
        self.leftLayout.setStretch(0, 4)
        self.leftLayout.setStretch(4, 1)
        self.leftLayout.setStretch(5, 1)
        
        #--------------------------------------------------

        # logging
        self.logPanel = QWidget()
        # self.logPanel.setObjectName("panel")
        self.logLayout = QVBoxLayout(self.logPanel)
        # self.logLayout.setContentsMargins(14, 14, 14, 14)
        # self.logLayout.setSpacing(8)
        self.layout.addWidget(self.logPanel)
        for logline in logger.loglines:
            self.logLayout.addWidget(logline, alignment=Qt.AlignmentFlag.AlignLeft)
        logger.update_log_stream()

        self.layout.setStretch(0, 3)
        self.layout.setStretch(1, 2)
        

def run(app: QApplication):
    QApplication.setFont(QFont("Segoe UI", 11))
    window = MainWindow()
    app.exec()


if __name__=="__main__":
    thisapp = QApplication([])
    run(thisapp)
