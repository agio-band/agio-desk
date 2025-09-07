from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from agio.core.pkg import resources


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
