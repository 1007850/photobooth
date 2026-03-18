import booth_settings
from PyQt6.QtWidgets import QApplication

app = QApplication([])
window = booth_settings.SettingWindow()
app.exec()