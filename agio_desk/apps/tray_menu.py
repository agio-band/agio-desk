from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import QMenu

from agio.core.utils import get_actions
from agio.core.utils.action_items import ActionGroupItem, ActionItem


class MainMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.items_group = get_actions('tray.main_menu', 'desk')

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

    def open(self):
        self.generate_menu(self.items_group)
        self.exec(QCursor.pos())
        self.clear()
