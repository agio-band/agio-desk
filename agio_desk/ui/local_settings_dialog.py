import logging
import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from agio.core.entities.profile import AProfile
from agio.tools import qt, app_dirs
from agio_desk.ui import local_settings_tools
from agio.core.settings import save_local_settings

logger = logging.getLogger(__name__)

class LocalSettingsDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Local Settings')
        self.main_ly = QVBoxLayout(self)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setHandleWidth(2)

        left_widget = QWidget(self)
        left_ly = QVBoxLayout(left_widget)
        left_ly.setContentsMargins(0, 0, 0, 0)
        company_grp = QGroupBox('Company')
        company_ly = QVBoxLayout(company_grp)
        self.company_cbb = CompanyList(self)
        self.company_cbb.currentIndexChanged.connect(self.on_company_changed)
        self.show_home_button = QCheckBox('Show All Home')
        self.show_home_button.clicked.connect(self.update_company_list)
        company_ly.addWidget(self.company_cbb)
        company_ly.addWidget(self.show_home_button)
        left_ly.addWidget(company_grp)

        projects_grp = QGroupBox('Projects')
        projects_ly = QVBoxLayout(projects_grp)
        self.projects_lst = QListWidget(projects_grp)
        self.projects_lst.currentItemChanged.connect(self.on_project_selected)
        projects_ly.addWidget(self.projects_lst)
        left_ly.addWidget(projects_grp)

        self.splitter.addWidget(left_widget)

        self.settings_grp = QGroupBox('Local Roots')
        self.settings_ly = QVBoxLayout(self.settings_grp)
        self.mount_point_lb = QLabel('Projects Mount Point*')
        self.settings_ly.addWidget(self.mount_point_lb)

        self.mount_point_ly = QHBoxLayout()
        self.projects_root_le = QLineEdit(self.settings_grp)
        self.projects_root_le.textChanged.connect(self.on_path_value_changed)
        self.mount_point_ly.addWidget(self.projects_root_le)

        self.projects_root_browse_btn = QPushButton('...', clicked=lambda: self.browse_path(self.projects_root_le))
        self.projects_root_browse_btn.setMaximumSize(QSize(30, 30))
        self.mount_point_ly.addWidget(self.projects_root_browse_btn)
        self.settings_ly.addLayout(self.mount_point_ly)

        self.temp_dir_lb = QLabel('Temp Dir')
        self.settings_ly.addWidget(self.temp_dir_lb)

        self.temp_dir_ly = QHBoxLayout()
        self.temp_root_le = QLineEdit(self.settings_grp)
        self.temp_root_le.textChanged.connect(self.on_path_value_changed)
        self.temp_dir_ly.addWidget(self.temp_root_le)

        self.temp_root_browse_btn = QPushButton('...', clicked=lambda: self.browse_path(self.temp_root_le))
        self.temp_root_browse_btn.setMaximumSize(QSize(30, 30))
        self.temp_dir_ly.addWidget(self.temp_root_browse_btn)

        self.settings_ly.addLayout(self.temp_dir_ly)
        self.settings_ly.addItem( QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.splitter.addWidget(self.settings_grp)
        self.main_ly.addWidget(self.splitter)

        self.bottom_buttons_ly = QHBoxLayout()
        self.help_btn = QPushButton('Help')
        self.bottom_buttons_ly.addWidget(self.help_btn)
        self.help_btn.hide() # TODO add help link
        self.bottom_buttons_ly.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.loading_lb = QLabel('Loading...')
        self.bottom_buttons_ly.addWidget(self.loading_lb)

        self.not_saved = QLabel('[Not saved]')
        self.bottom_buttons_ly.addWidget(self.not_saved)
        self.not_saved.hide()

        self.bottom_buttons_ly.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.reload_btn = QPushButton('Reload', clicked=self.reload_ui)
        self.save_btn = QPushButton('Save Company Roots', clicked=self.on_save_clicked)
        self.bottom_buttons_ly.addWidget(self.reload_btn)
        self.bottom_buttons_ly.addWidget(self.save_btn)
        self.main_ly.addLayout(self.bottom_buttons_ly)
        self.main_ly.setStretch(0, 1)

        self.splitter.setSizes([300, 600])

        self.resize(900, 500)

        self._data = {}
        self._current_user = None
        self._companies = []
        self._current_project = None
        self._has_unsaved_changed = False
        self.thread = None
        self.reload_ui()

    def reload_ui(self):
        if self.thread and self.thread.isRunning():
            return
        self.clear_ui()
        self.setEnabled(False)
        self.projects_root_le.setEnabled(False)
        self.temp_root_le.setEnabled(False)
        try:
            user = AProfile.current()
            self._current_user = user
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
            return
        self.loading_lb.show()
        self.thread = QThread()
        self.worker = Worker(local_settings_tools.load_companies)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.on_loaded)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.on_load_error)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._on_thread_stopped)
        self.thread.start()

    def clear_ui(self):
        self.company_cbb.clear()
        self.projects_lst.clear()
        self.projects_root_le.clear()
        self.temp_root_le.clear()

    def _on_thread_stopped(self):
        self.thread = None

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
        self._companies = data
        self.company_cbb.blockSignals(True)
        try:
            self.update_company_list()
        except Exception as e:
            logger.exception('Company list update failed')
            QMessageBox.critical(self, 'Error', str(e))
        finally:
            # set prev index
            self.company_cbb.blockSignals(False)
        self.on_company_changed()

    def update_company_list(self):
        current_text = self.company_cbb.currentText()
        self.company_cbb.clear()
        show_other_users = self.show_home_button.isChecked()

        def sort_companies(comp):
            return bool(comp.get('hostUser')), (comp.get('hostUser') or {}).get('name'),  comp['name']

        for i, cmp in enumerate(sorted(self._companies, key=sort_companies)):
            if cmp.get('hostUser'):
                if not show_other_users and cmp['hostUser']['id'] != self._current_user.id:
                    continue
                label = f'Home ({cmp["hostUser"]["name"]})'
            else:
                label = cmp['name']
            self.company_cbb.addItem(label, cmp)

        self.company_cbb.setCurrentText(current_text)
        self.setEnabled(True)
        self.loading_lb.hide()

    def on_company_changed(self):

        self.projects_root_le.blockSignals(False)
        self.temp_root_le.blockSignals(False)
        self.projects_root_le.clear()
        self.temp_root_le.clear()
        self.projects_lst.clear()
        self.projects_root_le.blockSignals(False)
        self.temp_root_le.blockSignals(False)
        self.unsaved = False

        company = self.company_cbb.currentData(Qt.UserRole)
        if not company:
            return
        self._data = {item['project'].id: item for item in local_settings_tools.load_projects(company['id'])}
        if not self._data:
            logger.warning(f'No projects for selected company')
            return
        for item in self._data.values():
            list_item = QListWidgetItem(item['project'].name)
            list_item.setData(Qt.UserRole, item['project'].id)
            self.projects_lst.addItem(list_item)

    def get_default_mount_point(self):
        return ''

    def get_default_temp_dir(self):
        return ''   # app_dirs.temp_dir().as_posix()

    @property
    def unsaved(self):
        return self._has_unsaved_changed

    @unsaved.setter
    def unsaved(self, value):
        self._has_unsaved_changed = value
        self.not_saved.setVisible(value)

    def on_project_selected(self, item):

        if not item:
            self.projects_root_le.blockSignals(True)
            self.temp_root_le.blockSignals(True)
            self.projects_root_le.setEnabled(False)
            self.temp_root_le.setEnabled(False)
            self.projects_root_le.clear()
            self.temp_root_le.clear()
            self.projects_root_le.blockSignals(False)
            self.temp_root_le.blockSignals(False)
            self._current_project = None
            return
        project_id = item.data(Qt.UserRole)
        self._current_project = project_id
        root_settings = self._data.get(project_id)['settings'].get('agio_pipe.local_roots', {}).get('value') or []
        roots = {r['name']: r['path'] for r in root_settings}

        self.projects_root_le.blockSignals(True)
        self.temp_root_le.blockSignals(True)
        try:
            if roots:
                self.projects_root_le.setText(roots.get('projects', self.get_default_mount_point()))
                self.temp_root_le.setText(roots.get('temp', self.get_default_temp_dir()))
            else:
                self.projects_root_le.setText(self.get_default_mount_point())
                self.temp_root_le.setText(self.get_default_temp_dir())
        finally:
            self.projects_root_le.blockSignals(False)
            self.temp_root_le.blockSignals(False)
        self.projects_root_le.setEnabled(True)
        self.temp_root_le.setEnabled(True)

    def on_path_value_changed(self):
        if self._current_project:
            prj_raw = self.projects_root_le.text().strip()
            if prj_raw:
                mount_point_path = Path(prj_raw).expanduser().as_posix()
            else:
                mount_point_path = ''

            tmp_raw = self.temp_root_le.text().strip()
            if tmp_raw:
                temp_path = Path(tmp_raw.strip()).expanduser().as_posix()
            else:
                temp_path = ''

            parameter = [
                    {'name': 'projects', 'path': mount_point_path},
                    {'name': 'temp', 'path': temp_path},
                ]
            self._data[self._current_project]['settings']['agio_pipe.local_roots']['value'] = parameter
            self.unsaved = True

    def on_save_clicked(self):
        try:
            self.check_paths()
        except Exception as e:
            logger.exception('Failed to check settings')
            QMessageBox.critical(self, 'Error', str(e))
            return
        try:
            count = self.save_not_empty()
            self.unsaved = False
            if count:
                QMessageBox.information(self, 'Success', 'Settings saved.')
            else:
                QMessageBox.information(self, 'Oops', 'Nothing to save.')
        except Exception as e:
            logger.exception('Failed to save settings')
            QMessageBox.critical(self, 'Error', str(e))

    def save_not_empty(self):
        saved = 0
        for project_id, item in self._data.items():
            roots = [r['path'] for r in item['settings'].get('agio_pipe.local_roots', {}).get('value')]
            if any(roots):
                save_local_settings(item['settings'], item['project'])
                saved += 1
        return saved

    def check_paths(self):
        for item in self._data.values():
            roots = item['settings'].get('agio_pipe.local_roots', {}).get('value')
            if not roots:
                continue
                # raise ValueError('Roots for project "{}" not defined'.format(item["project"].name))
            for root in roots:
                if not root['path'] and root['name'] == 'projects':
                    raise ValueError(f'Path "{root["name"]}" must be defined , project: {item["project"].name}')
                path = Path(root['path'])
                if not path.exists():
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except PermissionError as e:
                        raise PermissionError(f'{e}, project: {item["project"].name}')
                    if not os.access(path.as_posix(), os.W_OK | os.X_OK):
                        raise OSError(f'Permission denied for {path}, project: {item["project"].name}')

    def browse_path(self, widget):
        path  = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if path:
            widget.setText(path)


class CompanyList(QComboBox):
    def __init__(self, parent: LocalSettingsDialog = None):
        super().__init__(parent=parent)
        self.p = parent

    def has_unsaved_changed(self):
        return self.p.unsaved

    def mousePressEvent(self, e, /):
        if self.has_unsaved_changed():
            if QMessageBox.question(self, 'Unsaved changes', 'Current company settings not saved. Continue?') != QMessageBox.Yes:
                return
        super().mousePressEvent(e)


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
            logger.exception('Failed to execute bg task')
            self.error.emit(str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LocalSettingsDialog()
    window.show()
    qt.center_on_screen(window, app)
    sys.exit(app.exec())