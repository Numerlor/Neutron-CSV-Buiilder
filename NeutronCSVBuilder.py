import ctypes
import sys
import traceback
from pathlib import Path

from PySide2 import QtWidgets, QtGui

from appinfo import APP, ORG, APPID
import gui


# https://stackoverflow.com/a/44352931
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', Path(__file__).absolute().parent)
    return str(base_path / relative_path)


class ExceptionHandler:
    def __init__(self):
        self.w = gui.CrashPop()

    def handler(self, exctype, value, tb):
        exc = traceback.format_exception(exctype, value, tb)
        sys.__excepthook__(exctype, value, tb)
        self.w.add_traceback(exc)
        self.w.show()


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path(Path("icons/icon_lib.ico"))))
    app.setApplicationName(APP)
    app.setOrganizationName(ORG)
    # save traceback to logfile if Exception is raised
    sys.excepthook = ExceptionHandler().handler
    # create org and app folders if not found
    ui = gui.MainWindow()
    ui.setup_ui()
    ui.show()
    sys.exit(app.exec_())
