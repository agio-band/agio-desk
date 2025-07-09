import logging
import os

from agio.core.plugins.service_hub import AServiceHub
from agio.core.plugins.base.command_base import ACommandPlugin
import click

from agio.core.utils import context
from agio.core.utils.process_utils import restart_with_env
from agio_desk.apps.main import start_desktop_app

logger = logging.getLogger(__name__)


class DeskCommand(ACommandPlugin):
    name = 'desk_cmd'
    command_name = 'desk'
    arguments = [
        click.option("-d", "--headless", is_flag=True, help='Start in headless mode'),
    ]
    services = {
        # 'queue',
        'broker'
    }

    def execute(self, **kwargs):
        if context.app_name != 'desk':
            logger.info('Restart as application "desk"')
            restart_with_env({'AGIO_APP_NAME': 'desk'})
        with AServiceHub(self.services) as sh:
            start_desktop_app(headless=kwargs.get('headless', False))

