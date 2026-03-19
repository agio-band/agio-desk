import logging

from agio.core.plugins.base_command import AStartAppCommand
from agio.tools.qt import main_app, center_on_screen, open_widget
from agio_desk.ui import local_settings_dialog

logger = logging.getLogger(__name__)


class LocalSettingsCommand(AStartAppCommand):
    name = 'local_settings_cmd'
    command_name = 'settings-ui'
    app_name = 'local_settings'

    def execute(self, **kwargs):
        with main_app() as app:
            dialog = local_settings_dialog.LocalSettingsDialog()
            open_widget(dialog, qapp=app)
            # center_on_screen(dialog, app)
            # dialog.show()


