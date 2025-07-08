import sys

from PySide6.QtWidgets import QSystemTrayIcon, QApplication, QMessageBox
from PySide6.QtCore import Qt, QObject, QTimer
from PySide6.QtGui import QIcon

from agio.core.packages.resources import get_res
from .tray_menu import MainMenu


class TrayIconApp(QObject): # TODO Rename this
    """
    Launcher Tray Icon Class
    """
    tray_message_title = 'agio Launcher'
    on_startup_message = 'agio Launcher started'
    icon_path = get_res('agio.png')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tray_icon = None
        self.manu = None

    # Methods for launcher control

    def show_ui(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon(self.icon_path))
        # on mouse clicked
        self.tray_icon.activated.connect(self.tray_icon_activated)
        # set default icon
        self.menu = MainMenu()
        self.tray_icon.show()

    def close_ui(self):
        if self.tray_icon:
            self.tray_icon.hide()

    # messages

    def show_message(self, msg, title=None, **kwargs):
        """
        Show tray message
        :param msg: str
        """
        if self.tray_icon:
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
        self.menu.open()

    def on_mouse_middle_click(self):
        print('TRAY ICON MIDDLE CLICK')

    def shutdown(self, *args):
        if self.tray_icon:
            print('TRAY ICON SHUTDOWN')

