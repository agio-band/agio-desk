import logging

from agio.core.events import emit
from agio.core.plugins.base_service import ServicePlugin, make_action
# from agio.tools import app_context

logger = logging.getLogger(__name__)


class DeskService(ServicePlugin):
    name = 'desk'

    @make_action()
    def show_message(self, text: str, title: str = None, *args, **kwargs):
        logger.info(f'Show message: {text}')
        # TODO send to desk by localhost
        emit('desk.tray.show_message', {'text': text, 'title': title})
