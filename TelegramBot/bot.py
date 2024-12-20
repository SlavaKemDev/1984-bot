import os

import telebot.types
from dotenv import load_dotenv
from telebot import TeleBot
from datetime import datetime, timedelta

from TextManager import TextManager

load_dotenv()

text_manager = TextManager(5, 0.7, timedelta(minutes=5))
bot = TeleBot(os.environ['BOT_TOKEN'])

CHANNEL_ID = os.environ['CHANNEL_ID']
REMOVE_DICE = os.environ['REMOVE_DICE']


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Big Brother is watching you!")


@bot.message_handler(content_types=['dice'])
def remove_dice(message: telebot.types.Message):
    if REMOVE_DICE:
        bot.delete_message(CHANNEL_ID, message.forward_from_message_id)


@bot.message_handler(commands=['mute'])
def mute(message: telebot.types.Message):
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Эту команду нужно отправить в ответ на сообщение!")
        return

    text_manager.mark_explicit(message.reply_to_message.text.lower())


@bot.message_handler(content_types=['text'])
def text_handler(message: telebot.types.Message):
    text = message.text.lower()

    if text_manager.check_is_available(text, datetime.now()):
        bot.send_message(message.chat.id, "Сообщение прошло модерацию.")
    else:
        bot.send_message(message.chat.id, "Сообщение не прошло модерацию.")
        bot.delete_message(message.chat.id, message.message_id)

    text_manager.add_text(message.text.lower(), datetime.now())


bot.polling(timeout=30)
