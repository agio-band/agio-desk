from agio.core import emit
from agio.core.plugins.base.service_base import ServicePlugin, make_action


class DeskService(ServicePlugin):
    name = 'desk'

    @make_action()
    def show_message(self, text: str, title: str = None, *args, **kwargs):
        emit('desk.tray.show_message', {'text': text, 'title': title})
