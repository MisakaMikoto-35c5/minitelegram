import json
import requests
from . import minitg_exceptions

class TelegramHttpApi:
    def __init__(self, config):
        self.config = config
        self.LOGGER = self.default_logger
        self.init_base_url()
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        self.__UPDATE_ID = 0
        self.TIMEOUT = 10

    def default_logger(self, type, message):
        if type != 'debug':
            print(message)
    
    def init_base_url(self):
        is_https = self.config.get('is_https', True)
        if is_https:
            schema = 'https'
        else:
            schema = 'http'
        telegram_api_host = self.config.get('telegram_host', 'api.telegram.org')
        self.base_url = '{}://{}/bot{}/'.format(
            schema,
            telegram_api_host,
            self.config['bot_token']
        )
    
    def send_get_request(self, command):
        resp = self.session.get(
            self.base_url + command,
            timeout=self.TIMEOUT
        )
        try:
            tg_resp = json.loads(resp.text)
            if not tg_resp['ok']:
                error = minitg_exceptions.TelegramServerError('Unknown error from Telegram api server: ' + resp.text)
                error.text = resp.text
                error.json = tg_resp
                raise error
            return tg_resp['result']
        except ValueError:
            error = minitg_exceptions.MalformedMessageDetectedError('Unknown error from Telegram api server: ' + resp.text)
            error.text = resp.text
            raise error
    
    def send_post_request(self, command, data):
        resp = self.session.post(
            self.base_url + command,
            data=json.dumps(data),
            timeout=self.TIMEOUT
        )
        try:
            tg_resp = json.loads(resp.text)
            if not tg_resp['ok']:
                error = minitg_exceptions.TelegramServerError('Unknown error from Telegram api server: ' + resp.text)
                error.text = resp.text
                error.json = tg_resp
                raise error
            return tg_resp['result']
        except ValueError:
            error = minitg_exceptions.MalformedMessageDetectedError('Unknown error from Telegram api server: ' + resp.text)
            error.text = resp.text
            raise error

    def get_telegram_updates(self):
        commands = self.send_get_request('getUpdates')
        messages = []
        max_update_id = self.__UPDATE_ID
        for i in commands:
            if i['update_id'] > self.__UPDATE_ID:
                if i['update_id'] > max_update_id:
                    max_update_id = i['update_id']
                messages.append(i)
        self.__UPDATE_ID = max_update_id
        return messages
    
    def send_telegram_message(self, chat_id, content):
        result = self.send_get_request(
            'sendMessage',
            {
                'chat_id': chat_id,
                'text': content
            }
        )
        return result