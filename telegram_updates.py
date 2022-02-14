from . import telegram_app_registry
from . import minitg_exceptions

class TelegramUpdates:
    def __init__(self, registry: telegram_app_registry.TelegramAppRegistry):
        self.registry = registry
        self.LOGGER = self.default_logger

    def default_logger(self, type, message):
        if type != 'debug':
            print(message)
    
    def do_update(self):
        try:
            messages = self.registry.tg_httpapi.get_telegram_updates()
        except minitg_exceptions.TelegramServerError:
            return False
        for message in messages:
            self.registry.process_telegram_message(message)
        return True
