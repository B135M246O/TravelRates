import logging
from datetime import datetime as dt, timedelta

from send_message import send_message
from valutes.dicts import V_MOEX_R
from valutes.exceptions import InvalidDate
from valutes.valutes_cb_xml import corr_date, date_args, get_api_answer, parse_valute
from valutes.valutes_moex import get_moex_currency_rate, get_moex_previous_rate

logger = logging.getLogger(__name__)


def currency_rate(update, context):
    chat = update.effective_chat
    if not context.args:
        send_message(chat, context, 'Укажите валюты поездки: /currency USD EUR CNY')
        return
    today = dt.now()
    try:
        current = get_api_answer(today)
        previous = get_api_answer(today - timedelta(days=1))
    except Exception as error:
        logger.warning('Не удалось получить курсы ЦБ: %s', error)
        send_message(chat, context, f'Курсы ЦБ временно недоступны: {error}')
        return
    for code in context.args:
        code = code.upper()
        try:
            value = parse_valute(current, code)
            old_value = parse_valute(previous, code)
            message = (f'TravelRates · {code}\n'
                       f'ЦБ РФ (на {corr_date(current)}): {value:.3f} RUB '
                       f'({value - old_value:+.3f}) за 1 {code}')
        except Exception as error:
            send_message(chat, context, str(error))
            continue
        if code in V_MOEX_R:
            try:
                quote = get_moex_currency_rate(code, 'LAST')
                opened = get_moex_currency_rate(code, 'OPEN')
                message += (f'\nMOEX (запрос в {today:%H:%M}): {quote} RUB '
                            f'({float(quote) - float(opened):+.3f})')
            except Exception:
                try:
                    quote = get_moex_previous_rate(code)
                    message += f'\nMOEX: предыдущая цена {quote} RUB (не текущий курс)'
                except Exception:
                    message += '\nMOEX: котировка недоступна'
        send_message(chat, context, message)


def all_valutes(update, context):
    chat = update.effective_chat
    try:
        date = date_args(context.args[0]) if context.args else dt.now()
        response = get_api_answer(date)
        lines = []
        for code, currency in response['Valute'].items():
            value = parse_valute(response, code)
            lines.append(f'{code} — {currency["Name"]} — {value:.3f} RUB')
        message = (f'TravelRates · курсы для поездки на {response["@Date"]}\n'
                   'Рублей за 1 единицу валюты:\n' + '\n'.join(lines))
        send_message(chat, context, message)
    except InvalidDate as error:
        send_message(chat, context, str(error))
    except Exception as error:
        logger.warning('Не удалось получить список валют: %s', error)
        send_message(chat, context, f'Курсы ЦБ временно недоступны: {error}')
