from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.show()
    
    def initWindow(self):
        self.setWindowTitle("test sound")
        
        button = QPushButton()
        button.clicked.connect(self.beeper)
        self.setCentralWidget(button)
    
    def beeper(self):
        QApplication.beep()


if __name__=="__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec()
