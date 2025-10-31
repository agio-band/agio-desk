import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from agio.core.events import subscribe, on_exit
from agio.core.events.event import AEvent
from agio.core.workspaces.resources import get_res
from .tray_menu import MainMenu

logger = logging.getLogger(__name__)


class TrayIconApp(QObject): # TODO Rename this
    """
    Launcher Tray Icon Class
    """
    tray_message_title = 'agio Launcher'
    on_startup_message = 'agio Launcher started'
    icon_path = get_res('core/agio-icon.png')
    showMessageSignal = Signal(str, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tray_icon = None
        self.manu = None
        self.showMessageSignal.connect(self.show_message)
        on_exit(self.shutdown)

        @subscribe('desk.tray.show_message')
        def _show_message_action(event: AEvent):
            self.showMessageSignal.emit(event.payload['text'], event.payload['title'])

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
    def show_message(self, text: str, title: str = None, **kwargs):
        # todo: add rate limit
        if self.tray_icon:
            # icon = kwargs.get('icon')
            self.tray_icon.showMessage(title or self.tray_message_title, text)  #, icon=ico)

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
        # print('TRAY ICON CLICK')
        pass

    def on_mouse_double_click(self):
        # print('TRAY ICON DOUBLE CLICK')
        pass

    def on_mouse_right_click(self):
        # print('TRAY ICON RIGHT CLICK')
        self.menu.open()

    def on_mouse_middle_click(self):
        # print('TRAY ICON MIDDLE CLICK')
        pass

    def shutdown(self, *args):
        if self.tray_icon:
            logger.debug('Shutting down tray icon')

