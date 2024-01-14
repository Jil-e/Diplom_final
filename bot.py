import telebot

def sending_m(i, txt,  bot_data, bot_data_chat):
    bot = telebot.TeleBot(bot_data)
    try:
        bot.send_message(bot_data_chat, f"Алерт № {i} = {txt} сработал. Рекомендуем проверить данные")
    except Exception as ex:
        print(ex)

def send_error(bot_data, bot_data_chat):
    bot = telebot.TeleBot(bot_data)
    try:
        bot.send_message(bot_data_chat,f"Каких-либо данных пока нет")

    except Exception as ex:
        print(ex)