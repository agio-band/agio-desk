import logging

from agio.core.plugins.base_command import AStartAppCommand
from agio.tools.qt import main_app, center_on_screen
from agio_desk.ui.local_settings_dialog import LocalSettingsDialog

logger = logging.getLogger(__name__)


class LocalSettingsCommand(AStartAppCommand):
    name = 'local_settings_cmd'
    command_name = 'settings-ui'
    app_name = 'local_settings'

    def execute(self, **kwargs):
        with main_app() as app:
            dialog = LocalSettingsDialog()
            center_on_screen(dialog, app)
            dialog.show()


