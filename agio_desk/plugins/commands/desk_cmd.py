import logging

import click

from agio.core.plugins.base.command_base import AStartAppCommand
from agio.core.plugins.service_hub import AServiceHub
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
        with AServiceHub(self.services) as sh:
            start_desktop_app(headless=kwargs.get('headless', False))

