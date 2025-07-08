from PySide6.QtWidgets import QApplication


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
