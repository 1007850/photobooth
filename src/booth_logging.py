from PyQt6.QtCore import QObject, pyqtSignal
from booth_fs import get_time
from enum import Enum


class loglevels(Enum):
    ERROR = "red"
    WARNING = "yellow"
    INFO = "white"

class Logger(QObject):
    message = pyqtSignal(str, loglevels)
    logs: list[tuple[str,loglevels]] = []  # (message,colour)
    log_history = 15
    
    @staticmethod
    def update_log(message: str, loglevel: loglevels):
        if len(Logger.logs)>Logger.log_history-1:
            Logger.logs.pop(0)
        Logger.logs.append((f'{get_time(readable=True)[-8:]} - {message}', loglevel))
    
    def post(self, message: str, loglevel: loglevels):
        print(message)
        self.message.emit(message, loglevel)





logger = Logger()

    
    

