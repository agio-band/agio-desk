import logging
from agio.tools import qt
from agio_desk.apps.tray_icon import TrayIconApp


logger = logging.getLogger(__name__)


def start_desktop_app(*args, **kwargs):
    headless: bool = kwargs.pop('headless', False)
    if headless:
        logger.debug("Starting in headless mode")
    # qt.start_app('agio Desk')
    # qapp = GlobalSignalingApp(sys.argv)
    # qapp.setQuitOnLastWindowClosed(False)
    # qapp.setApplicationName('agio Desk')
    #
    # # break qt event loop every N time to catch python core events
    # timer = QTimer()
    # timer.start(100)
    # timer.timeout.connect(lambda: None)
    # qapp.timer = timer
    #
    # try:
    #     app = TrayIconApp()
    #     on_exit(app.shutdown)
    #     on_exit(lambda *args: qapp.quit())
    #     if not headless:
    #         app.show_ui()
    #     qapp.exec()
    #     # sys.exit(qapp.exec())
    # except Exception as e:
    #     logging.exception("Application startup error")
    #     if not headless:
    #         QMessageBox.critical(None, "Error", f"{type(e).__name__}: {e}")

    with qt.main_app('agio Desk', dialog_mode=False) as qapp:
        tray_icon = TrayIconApp()

        if not headless:
            tray_icon.show_ui()