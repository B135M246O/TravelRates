from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
import xmltodict

import kitty
import main
from random_answer import help_command
from valutes import valutes, valutes_cb_xml as cbr, valutes_moex as moex
from valutes.exceptions import InvalidApiExc, InvalidDate, InvalidValuteExc


@pytest.fixture
def rates():
    fixture = Path(__file__).parent / 'fixtures/cbr.xml'
    return cbr.make_json(xmltodict.parse(fixture.read_bytes()))


@pytest.fixture
def chat():
    return SimpleNamespace(effective_chat=SimpleNamespace(id=7))


def context(*args):
    return SimpleNamespace(args=list(args), bot=Mock())


@pytest.mark.parametrize('value', ['31.02.2024', '15.07.2024garbage', '2024-07-15', ''])
def test_invalid_dates(value):
    with pytest.raises(InvalidDate):
        cbr.date_args(value)


def test_date_and_cbr_nominal(rates):
    assert cbr.date_args('15.07.2024') == datetime(2024, 7, 15)
    assert cbr.parse_valute(rates, 'USD') == 87.743
    assert cbr.parse_valute(rates, 'JPY') == 0.55
    assert cbr.corr_date(rates) == '15.07'


def test_one_currency_response():
    response = cbr.make_json({'ValCurs': {
        '@Date': '15.07.2024', 'Valute': {
            'CharCode': 'AED', 'Nominal': '1', 'Value': '23,89', 'Name': 'Дирхам'
        }
    }})
    assert cbr.parse_valute(response, 'AED') == 23.89


def test_bad_responses_and_unknown_code(rates):
    with pytest.raises(InvalidApiExc):
        cbr.check_data({'@Date': '15.07.2024'}, 'USD')
    with pytest.raises(InvalidValuteExc):
        cbr.parse_valute(rates, 'ZZZ')


def test_get_cbr_uses_requested_date_and_timeout(monkeypatch):
    response = Mock(status_code=200, content=(Path(__file__).parent / 'fixtures/cbr.xml').read_bytes())
    get = Mock(return_value=response)
    monkeypatch.setattr(cbr.requests, 'get', get)
    assert cbr.get_api_answer(datetime(2024, 7, 15))['@Date'] == '15.07.2024'
    assert get.call_args.kwargs['timeout'] == 15
    assert 'date_req=15/07/2024' in get.call_args.args[0]
    with pytest.raises(InvalidDate):
        cbr.get_api_answer(datetime(1992, 6, 30))


def test_currency_keeps_cbr_when_moex_fails(monkeypatch, rates, chat):
    monkeypatch.setattr(valutes, 'get_api_answer', lambda date: rates)
    monkeypatch.setattr(valutes, 'get_moex_currency_rate', Mock(side_effect=RuntimeError('offline')))
    monkeypatch.setattr(valutes, 'get_moex_previous_rate', Mock(side_effect=RuntimeError('offline')))
    ctx = context('usd', 'jpy')
    valutes.currency_rate(chat, ctx)
    messages = [call.kwargs['text'] for call in ctx.bot.send_message.call_args_list]
    assert len(messages) == 2
    assert '87.743 RUB' in messages[0]
    assert '0.550 RUB' in messages[1]
    assert all('котировка недоступна' in message for message in messages)
    assert all('\n' in message for message in messages)


def test_previous_quote_is_labeled(monkeypatch, rates, chat):
    monkeypatch.setattr(valutes, 'get_api_answer', lambda date: rates)
    monkeypatch.setattr(valutes, 'get_moex_currency_rate', Mock(side_effect=RuntimeError('closed')))
    monkeypatch.setattr(valutes, 'get_moex_previous_rate', lambda code: '87.000')
    ctx = context('USD')
    valutes.currency_rate(chat, ctx)
    assert 'предыдущая цена 87.000 RUB (не текущий курс)' in ctx.bot.send_message.call_args.kwargs['text']


def test_currency_without_arguments(chat):
    ctx = context()
    valutes.currency_rate(chat, ctx)
    assert '/currency USD EUR CNY' in ctx.bot.send_message.call_args.kwargs['text']


def test_all_rates_and_calendar_error(monkeypatch, rates, chat):
    monkeypatch.setattr(valutes, 'get_api_answer', lambda date: rates)
    ctx = context('15.07.2024')
    valutes.all_valutes(chat, ctx)
    text = ctx.bot.send_message.call_args.kwargs['text']
    assert '15.07.2024' in text and 'JPY' in text and '0.550 RUB' in text
    ctx.args = ['31.02.2024']
    valutes.all_valutes(chat, ctx)
    assert 'календарной даты нет' in ctx.bot.send_message.call_args.kwargs['text']


def test_moex_json_and_nominal(monkeypatch):
    response = Mock()
    response.json.return_value = {'marketdata': {
        'columns': ['SECID', 'LAST', 'OPEN'],
        'data': [['JPYRUB_TOM', 55, 54], ['UNKNOWN', 9, 8]],
    }}
    monkeypatch.setattr(moex.requests, 'get', Mock(return_value=response))
    assert moex.get_moex_currency_rate('JPY', 'LAST') == '0.550'


def test_cat_falls_back_to_dog(monkeypatch, chat):
    dog = Mock()
    dog.json.return_value = [{'url': 'https://images.example.com/dog.jpg'}]
    get = Mock(side_effect=[requests.ConnectionError('offline'), dog])
    monkeypatch.setattr(kitty.requests, 'get', get)
    ctx = context()
    kitty.cat_image(chat, ctx)
    assert 'thedogapi' in get.call_args.args[0]
    ctx.bot.send_photo.assert_called_once_with(chat_id=7, photo='https://images.example.com/dog.jpg')


def test_help_and_handler_registration(chat):
    ctx = context()
    help_command(chat, ctx)
    assert 'TravelRates' in ctx.bot.send_message.call_args.kwargs['text']
    updater = main.build_updater('123456789:dummy-token-for-local-check')
    handlers = updater.dispatcher.handlers[0]
    commands = set().union(*(getattr(handler, 'command', set()) for handler in handlers))
    assert {'start', 'help', 'valutes', 'currency'} <= commands
