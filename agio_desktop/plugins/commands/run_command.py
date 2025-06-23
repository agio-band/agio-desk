from agio_desktop.exceptions import StartupError
import sys
from pathlib import Path
from agio.core.utils.process_utils import start_process
from agio.core.plugins.base.base_plugin_command import ACommandPlugin, ASubCommand


class DesktopRunCommand(ASubCommand):
    command_name = "run"
    arguments = [
        # click.option(
        #     "-p", "--path", help='Package root path, Default: $PWD',
        #              type=click.Path(exists=True, dir_okay=True, resolve_path=True),
        #              default=Path.cwd().absolute().as_posix()
        # ),
    ]

    def execute(self):
        main_process_file_path = Path(__file__).joinpath('../../../main.py').resolve()
        if not main_process_file_path.exists():
            raise StartupError('Main startup file not found')
        cmd = [
            sys.executable,
            # '--workspace', 'id',
            '-m', 'agio',
            'run', sys.executable, main_process_file_path.as_posix(),

        ]
        start_process(cmd, replace=True)


class DesktopCommand(ACommandPlugin):
    name = 'desktop'
    command_name = 'desktop'
    arguments = [
        # click.option("-a", "--arg-a", is_flag=True, help='Bool flag'),
        # click.option("-b", "--arg-b", help='String argument'),
        # click.option('-c', '--arg-c', help='Path Argument',
        #              type=click.Path(exists=True, dir_okay=True, resolve_path=True),
        #              default=Path.cwd().absolute().as_posix()
        #              ),
    ]
    subcommands = [DesktopRunCommand]

    def execute(self):
        pass
