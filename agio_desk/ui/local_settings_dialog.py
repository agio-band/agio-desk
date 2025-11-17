import os
import sys
from pathlib import Path

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from agio.tools import qt, app_dirs
from agio_desk.ui.local_settings_tools import load_dialog_data, save_settings


class LocalSettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Local Settings')
        self.main_ly = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        self.projects_grp = QGroupBox('Projects')
        projects_ly = QVBoxLayout(self.projects_grp)
        self.projects_lst = QListWidget(self.projects_grp)
        self.projects_lst.currentItemChanged.connect(self.on_project_selected)
        projects_ly.addWidget(self.projects_lst)
        self.splitter.addWidget(self.projects_grp)

        self.settings_grp = QGroupBox('Local Roots')
        self.settings_ly = QVBoxLayout(self.settings_grp)
        self.mount_point_lb = QLabel('Projects Mount Point')
        self.settings_ly.addWidget(self.mount_point_lb)

        self.mount_point_ly = QHBoxLayout()
        self.projects_root_le = QLineEdit(self.settings_grp)
        self.projects_root_le.textChanged.connect(self.on_path_value_changed)
        self.mount_point_ly.addWidget(self.projects_root_le)

        self.projects_root_browse_btn = QPushButton('...')
        self.projects_root_browse_btn.setMaximumSize(QSize(30, 30))
        self.mount_point_ly.addWidget(self.projects_root_browse_btn)
        self.settings_ly.addLayout(self.mount_point_ly)

        self.temp_dir_lb = QLabel(self.settings_grp)
        self.settings_ly.addWidget(self.temp_dir_lb)

        self.temp_dir_ly = QHBoxLayout()
        self.temp_root_le = QLineEdit(self.settings_grp)
        self.temp_root_le.textChanged.connect(self.on_path_value_changed)
        self.temp_dir_ly.addWidget(self.temp_root_le)

        self.temp_root_browse_btn = QPushButton('...')
        self.temp_root_browse_btn.setMaximumSize(QSize(30, 30))
        self.temp_dir_ly.addWidget(self.temp_root_browse_btn)
        self.settings_ly.addLayout(self.temp_dir_ly)
        self.settings_ly.addItem( QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.splitter.addWidget(self.settings_grp)
        self.main_ly.addWidget(self.splitter)

        self.bottom_buttons_ly = QHBoxLayout()
        self.help_btn = QPushButton('Help')
        self.bottom_buttons_ly.addWidget(self.help_btn)
        self.bottom_buttons_ly.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.loading_lb = QLabel('Loading...')
        self.bottom_buttons_ly.addWidget(self.loading_lb)
        self.bottom_buttons_ly.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.save_btn = QPushButton('Save', clicked=self.on_save_clicked)
        self.bottom_buttons_ly.addWidget(self.save_btn)
        self.main_ly.addLayout(self.bottom_buttons_ly)
        self.main_ly.setStretch(0, 1)

        self.splitter.setSizes([300, 600])

        self.resize(900, 300)

        self.data = {}
        self._current_project = None
        self.reload_ui()

    def reload_ui(self):
        self.setEnabled(False)
        self.loading_lb.show()
        self.thread = QThread()
        self.worker = Worker(load_dialog_data,)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.on_loaded)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.on_load_error)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_load_error(self, text):
        msg = QMessageBox(self)
        btn_retry = msg.addButton('Retry', QMessageBox.AcceptRole)
        btn_exit = msg.addButton('Exit', QMessageBox.RejectRole)
        msg.setText(text)
        index = msg.exec()
        pressed_button = msg.buttons()[index-2]
        if pressed_button == btn_retry:
            self.reload_ui()
        elif pressed_button == btn_exit:
            app.quit()

    def on_loaded(self, data):
        self.data = {item['project'].id: item for item in data}
        self.projects_lst.clear()
        for item in data:
            list_item = QListWidgetItem(item['project'].name)
            list_item.setData(Qt.UserRole, item['project'].id)
            self.projects_lst.addItem(list_item)
        self.setEnabled(True)
        self.loading_lb.hide()

    def get_default_mount_point(self):
        return ''

    def get_default_temp_dir(self):
        return app_dirs.temp_dir().as_posix()

    def on_path_value_changed(self):
        if self._current_project:
            mount_point_path = Path(self.projects_root_le.text()).expanduser().as_posix()
            tamp_path = Path(self.temp_root_le.text()).expanduser().as_posix()
            parameter = [
                    {'name': 'projects', 'path': mount_point_path},
                    {'name': 'temp', 'path': tamp_path},
                ]
            self.data[self._current_project]['settings'].set('agio_pipe.local_roots', parameter)

    def on_project_selected(self, item):
        project_id = item.data(Qt.UserRole)
        self._current_project = project_id
        settings = self.data.get(project_id)['settings']
        roots_list = settings.get('agio_pipe.local_roots')
        roots = {r.name: r.path for r in roots_list}
        self.projects_root_le.setText(roots.get('projects', self.get_default_mount_point()))
        self.temp_root_le.setText(roots.get('temp', self.get_default_temp_dir()))

    def on_save_clicked(self):
        try:
            self.check_paths()
        except Exception as e:
            print(repr(e))
            QMessageBox.critical(self, 'Error', str(e))
            return
        try:
            save_settings(self.data)
            QMessageBox.information(self, 'Success', 'Settings saved.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def check_paths(self):
        for item in self.data.values():
            roots = item['settings'].get('agio_pipe.local_roots')
            for root in roots:
                path = Path(root.path)
                if not path.exists():
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except PermissionError as e:
                        raise PermissionError(f'{e}, project: {item["project"].name}')
                    if not os.access(path.as_posix(), os.W_OK | os.X_OK):
                        raise OSError(f'Permission denied for {path}, project: {item["project"].name}')


class Worker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, target_function, *args, **kwargs):
        super().__init__()
        self._target_function = target_function
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._target_function(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LocalSettingsDialog()
    window.show()
    qt.center_on_screen(window, app)
    sys.exit(app.exec())