import os
from dataclasses import dataclass

import telebot.types
from dotenv import load_dotenv
from telebot import TeleBot
from datetime import datetime, timedelta
import hashlib

from TextManager import TextManager
from DataBase import *

from collections import OrderedDict

load_dotenv()

text_manager = TextManager(5, 0.7, timedelta(minutes=5))
bot = TeleBot(os.environ['BOT_TOKEN'])

CHANNEL_ID = os.environ['CHANNEL_ID']
REMOVE_DICE = os.environ['REMOVE_DICE']

MODERATING_TYPES = ['audio', 'video', 'photo', 'document', 'animation', 'voice', 'video_note']


@dataclass
class MessageAttachment:
    content_type: str
    hash: str


def parse_attachments(message: telebot.types.Message) -> list[MessageAttachment]:
    answer: list[MessageAttachment] = []

    for content_type in MODERATING_TYPES:
        attachment = getattr(message, content_type)

        if not attachment:
            continue

        if isinstance(attachment, list):
            attachment = attachment[-1]

        file_info = bot.get_file(attachment.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_hash = hashlib.sha512(downloaded_file).hexdigest()

        answer.append(MessageAttachment(content_type, file_hash))

    return answer


@bot.message_handler(content_types=['dice'])
def remove_dice(message: telebot.types.Message):
    if REMOVE_DICE:
        bot.delete_message(CHANNEL_ID, message.forward_from_message_id)


@bot.message_handler(content_types=MODERATING_TYPES)
def handle_post(message: telebot.types.Message):
    print(message)

    with Session() as session:
        content_approved = True

        attachments = parse_attachments(message)

        for attachment in attachments:
            print(attachment)

            content_type = attachment.content_type
            file_hash = attachment.hash

            attachment_type = session.query(AttachmentType).filter_by(name=content_type).first()

            if not attachment_type:
                attachment_type = AttachmentType(name=content_type)
                session.add(attachment_type)
                session.commit()

            attachment = session.query(Attachment).filter_by(hash=file_hash).first()

            if not attachment:
                attachment = Attachment(type_id=attachment_type.id, hash=file_hash)
                session.add(attachment)
                session.commit()

            content_approved &= not attachment.is_banned

        if content_approved:
            session.commit()
        else:
            bot.delete_message(CHANNEL_ID, message.forward_from_message_id)
            session.rollback()

        session.close()


@bot.message_handler(commands=['ban'])
def ban_content(message: telebot.types.Message):
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        is_admin = True  # if sent by anonymous admin
    else:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Retrieve the user's status in the chat
        chat_member = bot.get_chat_member(chat_id, user_id)

        # Check if the user is an administrator or the chat creator
        is_admin = chat_member.status in ['administrator', 'creator']

    if not is_admin:  # You got it
        bot.reply_to(message, "Ты кто такой? Пошёл нахуй!")
        return

    target_message = message.reply_to_message

    attachments = parse_attachments(target_message)

    args = list(map(int, message.text.split()[1:])) or list(range(1, len(attachments) + 1))  # args from the command

    with Session() as session:
        banned_ids = []

        for i in args:
            i -= 1

            if i < 0 or i >= len(attachments):
                continue

            banned_ids.append(i + 1)

            # Retrieve the attachment and its type
            telegram_attachment = attachments[i]
            attachment_type = session.query(AttachmentType).filter_by(name=telegram_attachment.content_type).first()

            if not attachment_type:
                attachment_type = AttachmentType(name=telegram_attachment.content_type)
                session.add(attachment_type)
                session.commit()

            attachment = session.query(Attachment).filter_by(hash=telegram_attachment.hash).first()

            if not attachment:
                attachment = Attachment(type_id=attachment_type.id, hash=telegram_attachment.hash)
                session.add(attachment)
                session.commit()

            # Ban this attachment
            attachment.is_banned = True

        bot.delete_message(CHANNEL_ID, target_message.forward_from_message_id)
        session.commit()

        session.close()


@bot.message_handler(commands=['mute'])
def mute(message: telebot.types.Message):
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Эту команду нужно отправить в ответ на сообщение!")
        return

    text_manager.mark_explicit(message.reply_to_message.text.lower())


@bot.message_handler(content_types=['text'])
def text_handler(message: telebot.types.Message):
    text = message.text.lower()

    target_message = message.reply_to_message

    if not text_manager.check_is_available(text, datetime.now()):
        bot.delete_message(CHANNEL_ID, target_message.forward_from_message_id)

    text_manager.add_text(message.text.lower(), datetime.now())


bot.polling(timeout=30, none_stop=True)
