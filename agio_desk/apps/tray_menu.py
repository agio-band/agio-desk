import logging
from collections import defaultdict

from PySide6.QtGui import QCursor, QAction
from PySide6.QtWidgets import QMenu


class MainMenu(QMenu):
    menu_names = (
        'tray.main_menu',
        'tray.tools_menu'
    )
    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.items = self.collect_items()

    def collect_items(self):
        from agio.core import plugin_hub

        menu_actions = defaultdict(list)
        for menu_name in self.menu_names:
            for plugin in plugin_hub.iter_plugins('service'):
                items = plugin.get_action_items(menu_name)
                for action in items:
                    action['name'] = f"{plugin.package.name}.{action['name']}"
                menu_actions[menu_name].extend(items)
                # if action.get('divider_before'):
                #     all_actions.append({'type': 'divider'})
                # if action.get('divider_after'):
                #     all_actions.append({'type': 'divider'})
        return menu_actions

    def open(self):
        object_names = {}

        submenu = QMenu('Tools', self)
        for item in self.items[self.menu_names[1]]:
            if item['type'] == "action":
                if item['name'] in object_names:
                    logging.warning('Duplicate action name "%s" found"', item['name'])
                qaction = QAction(
                    item['label'], submenu,
                    # triggered=item['command'],
                    objectName=item['name']
                )
                submenu.addAction(qaction)
        self.addMenu(submenu)

        for item in self.items[self.menu_names[0]]:
            if item['type'] == "action":
                # if item.get('is_visible') and not item['is_visible']():
                #     continue
                if item['name'] in object_names:
                    logging.warning('Duplicate action name "%s" found"', item['name'])
                qaction = QAction(
                    item['label'], self,
                    # triggered=item['command'],
                    objectName=item['name']
                )
                self.addAction(qaction)

        self.exec(QCursor.pos())
        self.clear()

    def _open(self):
        """Open menu callback"""
        object_names = {}
        for item in sorted(self.items, key=lambda i: i['order']):
            if item['type'] == "action":
                if item.get('is_visible') and not item['is_visible']():
                    continue
                if item['name'] in object_names:
                    logging.warning('Duplicate action name "%s" found"', item['name'])
                qaction = QAction(item['label'], self, triggered=item['command'], objectName=item['name'])
                self.addAction(qaction)
            elif item['type'] == 'divider':
                self.addSeparator()
        self.exec(QCursor.pos())
        self.clear()