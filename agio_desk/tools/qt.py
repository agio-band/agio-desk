import inspect
import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import *
from PySide6.QtCore import *

from agio.core.events import subscribe, on_exit
from agio.core.pkg import resources


logger = logging.getLogger(__name__)


def get_main_parent():
    qapp = QApplication.instance()
    if qapp is None:
        raise RuntimeError('QApplication not created')
    return QApplication.topLevelWidgets()[0]


def center_on_screen(widget, app = None):
    app = app or QApplication.instance()
    cursor_pos: QPoint = QCursor.pos()
    current_screen: QScreen = app.screenAt(cursor_pos)
    if current_screen is None:
        current_screen = app.primaryScreen()
        if current_screen is None:
            print("Ошибка: Не удалось найти ни один экран.")
            return
    screen_geometry = current_screen.availableGeometry()
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


def open_dialog(widget, on_center: bool = True, *args, **kwargs):
    """
    Use this function to open a any dialogs.
    - apply style
    - fix core events
    - apply app name
    - apply app icon
    """
    qapp = kwargs.pop('qapp') or  QApplication.instance() or QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(True)
    qapp.setApplicationName(kwargs.pop('app_name', 'agio'))

    # break qt event loop every N time to catch python core events
    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    try:
        if inspect.isclass(widget):
            w = widget(*args, **kwargs)
        else:
            w = widget
        if on_center:
            center_on_screen(w, qapp)
        w.show()
        sys.exit(qapp.exec())
    except Exception as e:
        logging.exception(f"Application startup error: {e}")

