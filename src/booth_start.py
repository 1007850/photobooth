import os
import sys
import time
import booth_config as config
import subprocess

def main():
    print("Running app")
    if config.standaloneMode:
        import booth_gui2 as gui
    else:
        import booth_gui as gui
    gui.run()
    raise Exception("Crash")


if __name__=="__main__":
    try:
        main()
    except Exception as e:
        if config.restart:
            if getattr(sys, 'frozen', False):
                print("Restarting app due to:", e)
                for i in range(500):
                    time.sleep(0.01)
                env = os.environ.copy()
                env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
                subprocess.Popen([sys.executable] + sys.argv[1:], env=env)
                sys.exit(0)
            else:
                print("Restarting script due to:", e)
                for i in range(500):
                    time.sleep(0.01)
                os.execv(sys.executable, [sys.executable] + sys.argv)
