import os

from dataclasses import dataclass
import asyncio

import telebot.types
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime, timedelta
import hashlib

from TextManager import *
from DataBase import *

load_dotenv()

text_manager = TextManager(5, 0.7, timedelta(minutes=5))
bot = AsyncTeleBot(os.environ['BOT_TOKEN'], parse_mode='HTML')

CHANNEL_ID = os.environ['CHANNEL_ID']
REMOVE_DICE = bool(int(os.environ['REMOVE_DICE']))
REMOVE_JACKPOT = bool(int(os.environ['REMOVE_JACKPOT']))

MODERATING_TYPES = ['sticker', 'audio', 'video', 'photo', 'animation', 'voice', 'video_note', 'document']


@dataclass
class MessageAttachment:
    content_type: str
    hash: str


async def parse_attachment(message: telebot.types.Message) -> Optional[MessageAttachment]:
    for content_type in MODERATING_TYPES:
        attachment = getattr(message, content_type)

        if not attachment:
            continue

        if isinstance(attachment, list):  # get file with max quality
            attachment = attachment[-1]

        file_info = await bot.get_file(attachment.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        file_hash = hashlib.sha512(downloaded_file).hexdigest()

        return MessageAttachment(content_type, file_hash)


def get_media_group_id(message: telebot.types.Message):
    return message.media_group_id or f"single_{message.message_id}"


@bot.message_handler(content_types=['dice'])
async def remove_dice(message: telebot.types.Message):  # Remove all dices, except casino jackpot
    is_jackpot = message.dice.emoji == '🎰' and message.dice.value in [1, 22, 43, 64]

    if REMOVE_DICE and (not is_jackpot or REMOVE_JACKPOT):
        await bot.delete_message(CHANNEL_ID, message.forward_from_message_id)


@bot.message_handler(content_types=MODERATING_TYPES)
async def handle_post(message: telebot.types.Message):  # Handle all media messages
    media_group_id = get_media_group_id(message)
    attachment = await parse_attachment(message)

    with Session() as session:
        content_type = attachment.content_type
        file_hash = attachment.hash

        # Get or create attachment type
        attachment_type = session.query(AttachmentType).filter_by(name=content_type).first()

        if not attachment_type:
            attachment_type = AttachmentType(name=content_type)
            session.add(attachment_type)
            session.commit()

        # Get or create attachment
        attachment = session.query(Attachment).filter_by(type_id=attachment_type.id, hash=file_hash).first()

        if not attachment:
            attachment = Attachment(type_id=attachment_type.id, hash=file_hash)
            session.add(attachment)
            session.commit()

        # Write message to db
        item = AttachmentItem(
            attachment_id=attachment.id,
            media_group_id=media_group_id,
            message_id=message.forward_from_message_id,
            created_at=datetime.now()
        )
        session.add(item)

        if not attachment.is_banned:
            session.commit()
        else:
            await bot.delete_message(CHANNEL_ID, message.forward_from_message_id)
            session.rollback()


@bot.message_handler(commands=['ban'])
async def ban_content(message: telebot.types.Message):
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        is_admin = True  # if sent by anonymous admin
    else:
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Retrieve the user's status in the chat
        chat_member = await bot.get_chat_member(chat_id, user_id)

        # Check if the user is an administrator or the chat creator
        is_admin = chat_member.status in ['administrator', 'creator']

    if not is_admin:  # Command only for admins
        return

    target_message = message.reply_to_message
    media_group_id = get_media_group_id(target_message)

    with Session() as session:
        attachment_items = session.query(AttachmentItem).filter_by(media_group_id=media_group_id).all()

        args = list(map(int, message.text.split()[1:])) or list(range(1, len(attachment_items) + 1))  # args from the command

        for i in map(lambda x: x - 1, args):
            if i < 0 or i >= len(attachment_items):
                continue

            attachment_item = attachment_items[i]
            attachment = attachment_item.attachment

            # Ban this attachment
            attachment.is_banned = True

            for cur_attachment_item in attachment.items:  # Remove all messages with this attachment
                await bot.delete_message(CHANNEL_ID, cur_attachment_item.message_id)

        await bot.delete_message(message.chat.id, message.message_id)  # Delete the command message

        session.commit()


@bot.message_handler(commands=['mute'])
async def mute(message: telebot.types.Message):
    if not message.reply_to_message:
        await bot.send_message(message.chat.id, "Эту команду нужно отправить в ответ на сообщение!")
        return

    text_manager.mark_explicit(message.reply_to_message.text.lower())


@bot.message_handler(content_types=['text'])
async def text_handler(message: telebot.types.Message):
    text = message.text.lower()

    if not text_manager.check_is_available(text, datetime.now()):
        await bot.delete_message(CHANNEL_ID, message.forward_from_message_id)

    text_manager.add_text(message.text.lower(), datetime.now())


async def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    await bot.polling(non_stop=True, request_timeout=60)

asyncio.run(main())
