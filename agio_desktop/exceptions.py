from agio.core.exceptions import AException


class StartupError(AException):
    detail = 'Startup failed'