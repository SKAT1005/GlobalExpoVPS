import telebot

bot = telebot.TeleBot('6311655580:AAEAuAfLbzHjWCPnKIrsExE_W6CrsjmElYY')
CHAT_ID = 5063638309



@bot.message_handler(content_types=['text'])
def msg(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text=chat_id)


bot.polling(none_stop=True)