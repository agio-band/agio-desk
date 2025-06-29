import os
import signal
import sys

from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QMessageBox
from PySide6.QtCore import Qt, QObject, QTimer
from PySide6.QtGui import QIcon


class LauncherTrayIcon(QObject):
    """
    Launcher Tray Icon Class

    """
    tray_message_title = 'agio Launcher'
    on_startup_message = 'agio Launcher started'
    icon_path = '/home/paul/pw-storage/dev/work/agio/packages/agio-core/agio/resources/agio.png'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(self.icon_path))
        # on mouse clicked
        self.tray_icon.activated.connect(self.tray_icon_activated)
        # set default icon
        # self.set_normal()

    # Methods for launcher control

    def show_ui(self):
        self.tray_icon.show()

    def close_ui(self):
        self.tray_icon.hide()

    # messages

    def show_message(self, msg, title=None, **kwargs):
        """
        Show tray message
        :param msg: str
        """
        icon = kwargs.get('icon')
        # ico = self._icons.get(icon) or self._icons.get(self.ICON_NO)
        self.tray_icon.showMessage(title or self.tray_message_title, msg)  #, icon=ico)
        # super(LauncherTrayIcon, self).show_message(msg, title)

    # def set_waiting(self, text):
    #     self.tray_icon.setIcon(QIcon(get_icon('tray_wait')))
    #     self.waiting_menu(text)

    # def set_normal(self):
    #     self.tray_icon.setIcon(QIcon(get_icon('tray')))

    def tray_icon_activated(self, reason):
        """
        Execute click on tray icon if is WINDOWS
        """
        # QSystemTrayIcon.Trigger       LMB
        # QSystemTrayIcon.Context       RMB
        # QSystemTrayIcon.MiddleClick   MMB
        # QSystemTrayIcon.DoubleClick   DBC
        if reason == QSystemTrayIcon.Context:
            self.on_mouse_right_click()
        elif reason == QSystemTrayIcon.Trigger:
            self.on_mouse_left_click()
        elif reason == QSystemTrayIcon.MiddleClick:
            self.on_mouse_middle_click()
        elif reason == QSystemTrayIcon.DoubleClick:
            self.on_mouse_double_click()
        else:
            pass

    # mouse events
    # todo: add modifiers for mouse events

    def on_mouse_left_click(self):
        print('TRAY ICON CLICK')

    def on_mouse_double_click(self):
        print('TRAY ICON DOUBLE CLICK')

    def on_mouse_right_click(self):
        print('TRAY ICON RIGHT CLICK')

    def on_mouse_middle_click(self):
        print('TRAY ICON MIDDLE CLICK')

    def shutdown(self, *args):
        print('TRAY ICON SHUTDOWN')


def main():
    from agio.core.events import on_exit

    qapp = QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    qapp.setApplicationName('agio Launcher')

    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    try:
        app = LauncherTrayIcon()
        on_exit(app.shutdown)
        on_exit(lambda *args: qapp.quit())
        app.show_ui()
        sys.exit(qapp.exec())
    except Exception as e:
        print("Application startup error")
        QMessageBox.critical(None, "Error", f"{type(e).__name__}: {e}")
