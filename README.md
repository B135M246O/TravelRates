# TravelRates

Валютный помощник путешественника в Telegram. Показывает справочные курсы ЦБ РФ к рублю на выбранную дату, выбранные валюты и доступные котировки MOEX. Команды и небольшой бонус с фотографиями животных доступны в одном боте.

Автор адаптации и доработок — Рябуха Олег.

Python 3.11, python-telegram-bot 13, requests, XML ЦБ РФ и JSON MOEX ISS. Базы данных и миграций нет.

## Запуск

Из корня проекта в PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Укажите в API_TOKEN токен собственного бота из @BotFather.
.\.venv\Scripts\python main.py --check
.\.venv\Scripts\python main.py
```

Linux/macOS: `python3.11 -m venv .venv`, затем `.venv/bin/python`. `.env` читается рядом с `main.py`. `--check` проверяет импорты без сетевых запросов, не запускает polling и не подтверждает валидность токена. Настоящий запуск требует доступного Telegram API и токена. Остановка — Ctrl+C.

Docker: `docker compose -f infra/docker-compose.yaml up --build`. Образ собирается локально; CI выполняет только тесты и проверку импортов.

## Команды

- `/start`, `/help` — справка.
- `/valutes` — все курсы ЦБ на сегодня, рублей за одну единицу валюты.
- `/valutes 15.07.2024` — курсы на указанную дату; начало архива 01.07.1992. Для будущей даты запрашивается сегодняшний курс. Дата в ответе — фактическая дата данных ЦБ.
- `/currency USD EUR CNY JPY` — выбранные валюты, изменение к данным предыдущего календарного дня и доступные котировки MOEX. Регистр не важен. В выходной обе даты ЦБ могут вернуть одинаковые значения.
- Сообщение `мяк` — фото кота из TheCatAPI; при отказе источника используется TheDogAPI.

Курсы справочные; цену обмена и комиссии определяет ваш банк или обменный пункт. Если текущей котировки MOEX нет, бот показывает предыдущую цену с явной пометкой либо сообщает о недоступности, сохраняя ответ ЦБ. Наличие валюты в ЦБ не означает наличие текущих торгов на MOEX.

## Проверки

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python main.py --check
```

Тесты работают без токенов и сети: проверяют XML с разными номиналами, даты, выбор валют, команды, отказ MOEX и запасной источник фото. Фактические сетевые проверки и ограничения — `REVIEW.md`.

Источники: [ЦБ РФ](https://www.cbr.ru/scripts/XML_daily.asp), [MOEX ISS](https://iss.moex.com/iss/engines/currency/markets/selt/securities.json), [TheCatAPI](https://api.thecatapi.com/v1/images/search), [TheDogAPI](https://api.thedogapi.com/v1/images/search).

Условия использования — в файле `LICENSE`; дополнительные сведения — в `NOTICE.md`.
