# minitelegram

A lightweight Telegram Bot framework on Python 3.

Sample code:

```
import minitelegram
import time

telegram_bot_api_configuration = {
    "telegram_host": "api.telegram.org",
    "is_https": True,
    "bot_token": ""
}

minitg_registry = minitelegram.telegram_app_registry.TelegramAppRegistry(telegram_bot_api_configuration)

@minitg_registry.all()
def all_handler(message):
    print(message)

@minitg_registry.command('/testcommand')
def test_command_handler(message):
    print(message)
    message['registry'].tg_httpapi.send_telegram_message(message['chat']['id'], 'command received!')

updates_processer = minitelegram.telegram_updates.TelegramUpdates(minitg_registry)

while True:
    try:
        update_result = updates_processer.do_update()
        time.sleep(1)
    except KeyboardInterrupt:
        break
```