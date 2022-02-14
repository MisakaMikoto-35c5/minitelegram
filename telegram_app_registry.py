import json
import traceback
import re
from . import minitg_exceptions
from . import telegram_httpapi

class TelegramAppRegistry:

    ALL_MESSAGE_HOOKS = []
    COMMAND_HOOKS = {}
    COMMAND_REGEX = re.compile('^\\/[a-zA-Z\\_]+$')

    def __init__(self, config) -> None:
        self.LOGGER = self.default_logger
        self.config = config
        self.tg_httpapi = telegram_httpapi.TelegramHttpApi(self.config)

    def default_logger(self, type, message):
        if type != 'debug':
            print(message)

    def all(self, **args):
        def inner_func(func):
            self.add_all_command_hook(func, args)
            return func
        return inner_func

    def command(self, command, **args):
        def inner_func(func):
            self.add_command_hook(command, func, args)
            return func
        return inner_func

    def add_command_hook(self, command, func, options):
        try:
            self.COMMAND_HOOKS[command]
            raise RuntimeError("Command {} is already registered".format(command))
        except KeyError:
            self.COMMAND_HOOKS[command] = {
                'registry': self,
                'func': func,
                'options': options
            }

    def add_all_command_hook(self, func, options):
        self.ALL_MESSAGE_HOOKS.append({
            'registry': self,
            'func': func,
            'options': options
        })
    
    def process_telegram_message(self, message):
        if type(message) == str:
            message = json.loads(message)
        for hook in self.ALL_MESSAGE_HOOKS:
            try:
                hook['func']({
                    'registry': self,
                    'message': message
                })
            except minitg_exceptions.StopMessageProcessing:
                self.LOGGER(
                    'debug',
                    'A hook canceled the message processing'
                )
            except:
                self.LOGGER(
                    'error',
                    'FATAL ERROR on all message hook. Message: {}, Exception: {}' \
                        .format(message, traceback.format_exc())
                )
        msg = message.get('message')
        if msg is None:
            return
        text = msg.get('text')
        if text == None or len(text) < 2 or text[0] != '/':
            return

        space_pos = text.find(' ')
        if space_pos == -1:
            command = text
            args = None
        else:
            command = text[:space_pos]
            args = text[space_pos + 1:]

        if self.COMMAND_REGEX.match(command) == None:
            return

        try:
            hook = self.COMMAND_HOOKS[command]
            hook['func']({
                'registry': self,
                'message': message,
                'args': args
            })
        except minitg_exceptions.StopMessageProcessing:
            pass
        except KeyError:
            pass
        except:
            self.LOGGER(
                'error',
                'FATAL ERROR on command hook. Message: {}, Exception: {}' \
                    .format(message, traceback.format_exc())
            )
