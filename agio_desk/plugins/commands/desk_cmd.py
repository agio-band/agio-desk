from agio.core.plugins.service_hub import AServiceHub
from agio.core.plugins.base.command_base import ACommandPlugin
import click

from agio_desk.apps.main_app import start_desktop_app


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
        with AServiceHub(self.services) as sh:
            start_desktop_app(headless=kwargs.get('headless', False))

