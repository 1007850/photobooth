import os
import sys
import time
import booth_config as config
import subprocess
from PyQt6.QtWidgets import QApplication
from booth_messaging import signals


def main(app: QApplication):
    print("Running app")
    if config.standaloneMode:
        import booth_gui2 as gui
    else:
        import booth_gui as gui
    gui.run(app)
    print('window closed')

def restart():
    if getattr(sys, 'frozen', False):
        print("Restarting app...")
        for i in range(500):
            time.sleep(0.01)
        env = os.environ.copy()
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        subprocess.Popen([sys.executable] + sys.argv[1:], env=env)
        sys.exit(0)
    else:
        print("Restarting script...")
        for i in range(500):
            time.sleep(0.01)
        script = os.path.abspath(__file__)
        subprocess.Popen([sys.executable, script], cwd=os.path.dirname(script))
        sys.exit(0)

def closeapp():
    app.closeAllWindows()

signals.stopSignal.connect(closeapp)
    

if __name__=="__main__":
    app = QApplication([])
    try:
        main(app)
    except BaseException as e:
        print(e)

    if config.restart:
        restart()
    else:
        print('not restarting...')
        sys.exit(0)
