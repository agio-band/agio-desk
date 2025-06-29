from agio_desktop.widgets import tray_icon
from agio.core.plugins.base.command_base import ACommandPlugin


class DesktopCommand(ACommandPlugin):
    name = 'desktop_cmd'
    command_name = 'desktop'

    def execute(self):
        tray_icon.main()
