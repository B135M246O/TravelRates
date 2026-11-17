import logging

import requests

from send_message import send_cat

logger = logging.getLogger(__name__)


URL = 'https://api.thecatapi.com/v1/images/search'


def cat_image(update, context):
    chat = update.effective_chat
    try:
        response = requests.get(URL, timeout=15)
        response.raise_for_status()
        image = response.json()[0]['url']
    except (requests.RequestException, ValueError, KeyError, IndexError) as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        try:
            response = requests.get(new_url, timeout=15)
            response.raise_for_status()
            image = response.json()[0]['url']
        except (requests.RequestException, ValueError, KeyError, IndexError):
            context.bot.send_message(
                chat_id=chat.id, text='Фото временно недоступны. Попробуйте позже.'
            )
            return
    send_cat(chat, context, image)
