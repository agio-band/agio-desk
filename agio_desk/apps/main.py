import logging
from agio.tools import qt
from agio_desk.apps.tray_icon import TrayIconApp


logger = logging.getLogger(__name__)


def start_desk_app(*args, **kwargs):
    headless: bool = kwargs.pop('headless', False)
    if headless:
        logger.debug("Starting in headless mode")

    with qt.main_app('agio.desk', dialog_mode=False) as qapp:
        tray_icon = TrayIconApp()

        if not headless:
            tray_icon.show_ui()