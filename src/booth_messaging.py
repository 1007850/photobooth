from PyQt6.QtCore import QObject, pyqtSignal, pyqtBoundSignal
from PyQt6.QtWidgets import QLabel, QSizePolicy, QApplication
from booth_fs import get_time
from enum import Enum


class loglevels(Enum):
    ERROR = "red"
    WARNING = "yellow"
    INFO = "white"

class Logger(QObject):
    message = pyqtSignal(str, loglevels)
    logs: list[tuple[str,loglevels]] = []  # (message,colour)
    log_history = 25

    def __init__(self):
        super().__init__()
        self.loglines: list[QLabel] = []
        for i in range(Logger.log_history):
            logline = QLabel("")
            logline.setMinimumHeight(10)
            logline.setMinimumWidth(10)
            logline.setMaximumHeight(15)
            logline.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
            # logline.setWordWrap(False)
            self.loglines.append(logline)
        
        self.message.connect(self.log_message)


    @staticmethod
    def update_log(message: str, loglevel: loglevels):
        if len(Logger.logs)>Logger.log_history-1:
            Logger.logs.pop(0)
        Logger.logs.append((f'{get_time(readable=True)[-8:]} - {message}', loglevel))
    
    def post(self, message: str, loglevel: loglevels):
        print(message)
        self.message.emit(message, loglevel)
        
    
    def log_message(self, message: str, loglevel: loglevels):
        self.update_log(message, loglevel)
        self.update_log_stream()
    

    # iterate over stream of logs and update qlabels
    def update_log_stream(self):
        for idx,line in enumerate(self.loglines):
            try:
                log = self.logs[idx]  # (message,colour)
            except:
                continue
            line.setStyleSheet(f'color: {log[1].value}; font-size: 12px')
            line.setText(log[0])
    

class changedSettings:
    def __init__(self):
        self.restart: bool = False
        self.printer: bool = False
        self.gui: bool = False
        self.lutoverlay: bool = False
        self.camera: bool = False




logapp = QApplication([])
logger = Logger()
    
class Signals(QObject):
    # used to signal new settings being applied
    settingSignal: pyqtBoundSignal = pyqtSignal(changedSettings)

    logSignal: pyqtBoundSignal = logger.message

    # used to signal render of gui
    guiSignal: pyqtBoundSignal = pyqtSignal(str)
    
    # used to close app
    stopSignal: pyqtBoundSignal = pyqtSignal()

signals = Signals()


