from PySide6.QtCore import QRect
from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import QMenu

from agio.core.actions import get_actions
from agio.core.actions.action_item import ActionGroupItem, ActionItem


class MainMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.items_group = get_actions('tray_menu', 'desk')
        # Rebuild actions every time the menu is about to open, no matter
        # who opens it: this app, the OS shell or a DBus StatusNotifier host
        # (KDE Plasma / GNOME render the exported menu by themselves,
        # anchored under the tray icon)
        self.aboutToShow.connect(self.refresh)

    def generate_menu(self, level: ActionGroupItem, parent_menu=None):
        parent_menu = parent_menu or self
        for action in level.sorted_items():
            if isinstance(action, ActionItem):
                if not action.is_visible:
                    continue
                qt_action = QAction(action.label,
                                 parent=parent_menu,
                                 triggered=action,
                                 objectName=action.name
                                 )
                self.addAction(qt_action)
            elif isinstance(action, ActionGroupItem):
                submenu = QMenu(action.label, parent=parent_menu)
                self.generate_menu(action, parent_menu)
                self.addMenu(submenu)

    def refresh(self):
        self.clear()
        self.generate_menu(self.items_group)

    def open_at_icon(self, tray_icon=None):
        """
        Fallback popup for tray hosts that neither render the exported
        menu themselves nor report the icon geometry (plain X11 bars
        without DBusMenu support)
        """
        rect = tray_icon.geometry() if tray_icon is not None else QRect()
        if rect.isValid():
            pos = rect.bottomLeft()
        else:
            pos = QCursor.pos()
        self.popup(pos)
