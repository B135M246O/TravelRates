
HELP = (
    'TravelRates — валютный помощник путешественника.\n'
    '/valutes — курсы ЦБ РФ за сегодня, RUB за единицу валюты\n'
    '/valutes 15.07.2024 — курсы на дату\n'
    '/currency USD EUR CNY — выбранные валюты и доступные котировки MOEX\n'
    'Курсы справочные: обменный пункт может установить другую цену.\n'
    'Напишите «мяк», если хочется получить фото кота в дорогу.'
)


def help_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELP)


def first_answer(update, context):
    help_command(update, context)
