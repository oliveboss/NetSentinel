# main.py
from ui.main_window import IDSMainWindow
import threading
import time


def main():
    app = IDSMainWindow()
#ts, args=(app.controller,), daemon=True).start()

    app.run()

if __name__ == "__main__":
    main()