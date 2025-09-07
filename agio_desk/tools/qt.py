import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import *
from PySide6.QtCore import *
from agio.core.pkg import resources


logger = logging.getLogger(__name__)

def get_main_parent():
    qapp = QApplication.instance()
    if qapp is None:
        raise RuntimeError('QApplication not created')
    return QApplication.topLevelWidgets()[0]


def center_on_screen(widget):
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    widget_geometry = widget.frameGeometry()
    widget_geometry.moveCenter(screen_geometry.center())
    widget.move(widget_geometry.topLeft())


def message_dialog(title, message, level='info'):
    levels = {
        'info': QMessageBox.Icon.Information,
        'warning': QMessageBox.Icon.Warning,
        'error': QMessageBox.Icon.Critical
    }
    icon = resources.get_res('core/agio-icon.png')
    app = QApplication.instance() or QApplication([])
    msg = QMessageBox()
    msg.setWindowIcon(QIcon(icon))
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setIcon(levels.get(level))
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec_()


def open_simple_dialog(widget_class, *args, **kwargs):
    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(True)
    qapp.setApplicationName(kwargs.pop('app_name', 'agio'))

    # break qt event loop every N time to catch python core events
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    try:
        w = widget_class(*args, **kwargs)
        w.show()
        sys.exit(qapp.exec())
    except Exception as e:
        logging.exception("Application startup error")

