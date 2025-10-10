import logging
import os

import click

from agio.core.events import emit
from agio.core.plugins.base_command import AStartAppCommand
from agio.core.utils.service_hub import AServiceHub
from agio_desk.apps.main import start_desktop_app

logger = logging.getLogger(__name__)


class DeskCommand(AStartAppCommand):
    name = 'desk_cmd'
    command_name = 'desk'
    app_name = 'desk'
    arguments = [
        click.option("-d", "--headless", is_flag=True, help='Start in headless mode'),
    ]
    services = {
        # 'queue',
        'broker'
    }

    def execute(self, **kwargs):
        # TODO start a new process with correct app context
        emit('agio_desk.app.before_launched')
        with AServiceHub(self.services) as sh:
            start_desktop_app(headless=kwargs.get('headless', False))

