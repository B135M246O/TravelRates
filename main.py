import os
import argparse
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from kitty import cat_image
from random_answer import first_answer, help_command
from valutes.valutes import all_valutes, currency_rate

load_dotenv(Path(__file__).with_name('.env'))


def build_updater(token):
    updater = Updater(token=token)
    updater.dispatcher.add_handler(CommandHandler('start', help_command))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CommandHandler('valutes', all_valutes))
    updater.dispatcher.add_handler(
        MessageHandler(Filters.regex(r'\b[мякМЯК]{3}\b'), cat_image))
    updater.dispatcher.add_handler(
        CommandHandler('currency', currency_rate))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, first_answer))
    return updater


def main():
    parser = argparse.ArgumentParser(description='TravelRates — валюты для поездки')
    parser.add_argument('--check', action='store_true',
                        help='Проверить импорты и конфигурацию без Telegram')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    if args.check:
        print('TravelRates: импорты OK; /start /help /valutes /currency; '
              'источники ЦБ РФ, MOEX, TheCatAPI/TheDogAPI')
        return
    token = os.getenv('API_TOKEN')
    if not token or token == 'replace-with-your-telegram-bot-token':
        raise SystemExit('Заполните API_TOKEN в .env токеном своего бота.')
    updater = build_updater(token)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
