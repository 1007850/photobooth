from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Photobooth by Roger")

        # create and set gridlayout
        self.layout: QGridLayout = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        # Create QPushButton
        button = QPushButton("Click Me")
        button.clicked.connect(self.onButtonClick)
        buttonpolicy = button.sizePolicy()
        self.layout.addWidget(button, 0, 0, 1, 1)

        # Create QPushButton
        button = QPushButton("Click Me")
        button.clicked.connect(self.onButtonClick)
        buttonpolicy = button.sizePolicy()
        self.layout.addWidget(button, 1, 0, 2, 2)

        # Create QLabeol
        label = QLabel("Urmum")
        labelpolicy = label.sizePolicy()
        labelpolicy.setVerticalStretch(0)
        labelpolicy.setHorizontalStretch(0)
        labelpolicy.setHeightForWidth(True)
        self.layout.addWidget(label, 10, 10, 1, 1)
        # layout.setColumnStretch(11, 1)
        self.layout.setRowStretch(11, 0)
        
        # create slider
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0,1)
        slider.valueChanged.connect(lambda x: self.toggleStretch(x))
        self.layout.addWidget(slider, 3, 0, 2, 2)
        
        # create checkbox
        checkbox = QCheckBox("Toggle")
        checkbox.setChecked(True)
        checkbox.toggled.connect(lambda x: self.toggleStretch(x))
        self.layout.addWidget(checkbox, 4, 1, 2, 2)
        

        self.setStyleSheet("""
            QWidget:hover {
                border: 2px solid #007ACC;
                border-radius: 4px;
            }
        """)

    def onButtonClick(self):
        print("Button clicked!")

    def toggleStretch(self, tog: bool):
        if tog:
            for i in range(11):
                self.layout.setColumnStretch(i,1)
                self.layout.setRowStretch(i,1)
        else:
            for i in range(11):
                self.layout.setColumnStretch(i,0)
                self.layout.setRowStretch(i,0)
            

if __name__ == "__main__":
   app = QApplication([])
   window = MainWindow()
   window.show()
   app.exec()
