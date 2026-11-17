import logging

import requests

from valutes.dicts import V_MOEX, V_MOEX_R
from valutes.exceptions import InvalidJsonExc, InvalidResponseExc

logger = logging.getLogger(__name__)
MOEX_URL = 'https://iss.moex.com/iss/engines/currency/markets/selt/securities.json'


def get_moex_answer(mark_sec):
    try:
        response = requests.get(
            MOEX_URL,
            params={'iss.only': 'securities,marketdata',
                    'securities': ','.join(V_MOEX_R.values()),
                    'iss.meta': 'off'},
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        raise InvalidResponseExc(f'MOEX недоступна: {error}') from error
    try:
        table = response.json()[mark_sec]
        return [dict(zip(table['columns'], row)) for row in table['data']]
    except (ValueError, KeyError, TypeError) as error:
        raise InvalidJsonExc('Некорректный ответ MOEX') from error


def moex_currency_dict(moment, mark_sec):
    return {
        V_MOEX[row['SECID']][0]: str(row[moment])
        for row in get_moex_answer(mark_sec)
        if row.get('SECID') in V_MOEX and row.get(moment) is not None
    }


def get_moex_currency_rate(valute, moment):
    nominal = 100 if valute in ('JPY', 'KZT') else 1
    values = moex_currency_dict(moment, 'marketdata')
    # Отсутствующую текущую котировку нельзя выдавать за курс реального времени.
    if valute not in values:
        raise InvalidResponseExc(f'Нет текущей котировки {valute}')
    return f'{float(values[valute]) / nominal:.3f}'


def get_moex_previous_rate(valute):
    nominal = 100 if valute in ('JPY', 'KZT') else 1
    values = moex_currency_dict('PREVPRICE', 'securities')
    if valute not in values:
        raise InvalidResponseExc(f'Нет предыдущей котировки {valute}')
    return f'{float(values[valute]) / nominal:.3f}'
