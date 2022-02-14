class StopMessageProcessing(Exception):
    pass

class TelegramServerError(RuntimeError):
    pass

class MalformedMessageDetectedError(TelegramServerError):
    pass