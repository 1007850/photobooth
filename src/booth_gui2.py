from PyQt6.QtWidgets import QMainWindow, QGridLayout, QPushButton, QWidget, QLabel, QComboBox, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from booth_ctrl import ctrl
from booth_gui_components import imageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ctrl = ctrl()
        self.initWindow()
        self.show()
        self.ctrl.setPrinteSettings()
    
    def initWindow(self):
        self.setWindowTitle("Photobooth by Roger")
        
        self.layout: QGridLayout = QGridLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        #--------------------------------------------------
        
        # instruction label
        nbounds = next(iter(self.ctrl.overlays.values())).nbounds
        instructionLabel = QLabel(f'''There will be {nbounds} shots.
{self.ctrl.delay}-second countdown before every shot.

After processing, a QR code will appear with the link to your photo.
Please have your camera ready to scan it.

Once ready, press start and the countdown will begin.''')
        instructionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(instructionLabel, 0, 0)
        

        # start button
        startButton = QPushButton("Start")
        startButton.clicked.connect(self.ctrl.startFlow)
        self.layout.addWidget(startButton)


if __name__=="__main__":
    app = QApplication([])
    QApplication.setFont(QFont("Times", 12))
    window = MainWindow()
    app.exec()