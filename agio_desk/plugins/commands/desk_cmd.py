import logging
import os

import click

from agio.core.events import emit, subscribe, AEvent
from agio.core.plugins.base_command import AStartAppCommand
from agio.core.plugins.service_hub import AServiceHub
from agio.tools import qt, env_names
from agio_desk.apps.main import start_desk_app

logger = logging.getLogger(__name__)


class DeskCommand(AStartAppCommand):
    name = 'desk_cmd'
    command_name = 'desk'
    app_name = 'desk'
    help = 'Start agio.desk app'
    arguments = [
        click.option("-d", "--headless", is_flag=True, help='Start in headless mode'),
    ]
    services = {
        # 'queue',
        'broker'
    }

    def before_start(self, **kwargs):
        super().before_start(**kwargs)
        # os.environ[env_names.APP_NAME] = self.app_name

        @subscribe('core.message.error')
        def on_error(event: AEvent):
            qt.show_message_dialog(event.payload['message'], 'Error', 'error')

    def start(self, **kwargs):
        emit('agio_desk.app.before_launched', {'app': self})
        with AServiceHub(self.services) as sh:
            start_desk_app(headless=kwargs.get('headless', False))

