import config
import telebot
import adm
import usr

bot = telebot.TeleBot(config.token)










@bot.message_handler(content_types=["text"])
def logic(message):
    if message.text == '/admin ' + str(config.adm_password):
        bot.send_message(message.chat.id, adm.logic(message.text))







if __name__ == '__main__':
    bot.polling(none_stop=True)
