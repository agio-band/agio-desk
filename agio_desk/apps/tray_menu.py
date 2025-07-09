from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import QMenu

from agio.core.utils import get_actions
from agio.core.utils.action_items import make_callback, ActionGroupItem, ActionItem


class MainMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.items_group = get_actions('tray.main_menu', 'desk')

    def generate_menu(self, level: ActionGroupItem, parent_menu=None):
        parent_menu = parent_menu or self
        for item in level.sorted_items():
            if isinstance(item, ActionItem):
                action = QAction(item.label,
                                 parent=parent_menu,
                                 triggered=make_callback(item),
                                 objectName=item.name
                                 )
                self.addAction(action)
            elif isinstance(item, ActionGroupItem):
                submenu = QMenu(item.label, parent=parent_menu)
                self.generate_menu(item, parent_menu)
                self.addMenu(submenu)

    def open(self):
        self.generate_menu(self.items_group)
        self.exec(QCursor.pos())
        self.clear()
