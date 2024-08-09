import telebot
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '6943008733:AAGXq619kbAiFcLiZcHD0pBHtv7miQnA6y0')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.type in ['group', 'supergroup']:
        print(f"Chat ID: {message.chat.id}")

if __name__ == '__main__':
    bot.polling(none_stop=True)
