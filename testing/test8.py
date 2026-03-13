import booth_gui_components as bg
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication





if __name__=="__main__":
    app = QApplication([])
    # QApplication.setFont(QFont("Times", 12))
    window = bg.textWindow("2")
    app.exec()