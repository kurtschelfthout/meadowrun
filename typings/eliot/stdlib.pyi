from logging import Handler

class EliotHandler(Handler):
    def emit(self, record) -> None: ...
