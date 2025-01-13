import os
import json
import pickle

from dataclasses import dataclass
import asyncio

import telebot.types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime, timedelta
import hashlib

from TextManager import *
from DataBase import *

script_path = os.path.dirname(os.path.realpath(__file__))

load_dotenv()

if os.path.exists('text_manager.pkl'):  # load TextManager if saved
    with open('text_manager.pkl', 'rb') as f:
        text_manager = pickle.load(f)
else:
    text_manager = TextManager(5, 0.7, timedelta(minutes=5))

bot = AsyncTeleBot(os.environ['BOT_TOKEN'], parse_mode='HTML')
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
ADMIN_ID = int(os.environ['ADMIN_ID'])

with open(f'{script_path}/config.json', 'r') as f:
    config = json.load(f)

REMOVE_DICE = config['REMOVE_DICE']
REMOVE_JACKPOT = config['REMOVE_JACKPOT']

MODERATING_TYPES = config['MODERATING_TYPES']
SAVE_PERIOD = config['SAVE_PERIOD']

last_save = datetime.now()


def get_user(from_user: telebot.types.User, session: Session) -> TelegramUser:
    user = session.query(TelegramUser).filter_by(id=from_user.id).first()

    if not user:
        user = TelegramUser(id=from_user.id,
                            username=from_user.username,
                            first_name=from_user.first_name,
                            last_name=from_user.last_name)
        session.add(user)
        session.commit()

    return user


def save_state():  # TODO: implement save to database instead of save to pickle file
    global last_save

    if (datetime.now() - last_save).total_seconds() < SAVE_PERIOD:
        return

    last_save = datetime.now()

    with open('text_manager.pkl', 'wb') as f:
        pickle.dump(text_manager, f)


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


async def process_link_preview(message: telebot.types.Message):
    if message.link_preview_options is not None and not message.link_preview_options.is_disabled:
        await bot.edit_message_text(message.text or message.caption or "", message.chat.id, message.message_id, disable_web_page_preview=True)


@bot.channel_post_handler(content_types=['dice'])
async def remove_dice(message: telebot.types.Message):  # Remove all dices, except casino jackpot
    if message.chat.id != CHANNEL_ID:
        return

    is_jackpot = message.dice.emoji == '🎰' and message.dice.value in [1, 22, 43, 64]

    if REMOVE_DICE and (not is_jackpot or REMOVE_JACKPOT):
        await bot.delete_message(message.chat.id, message.message_id)


@bot.channel_post_handler(content_types=MODERATING_TYPES)
async def handle_post(message: telebot.types.Message):  # Handle all media messages
    if message.chat.id != CHANNEL_ID:
        return

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

        if not attachment and (
                not message.from_user or message.from_user.is_bot or message.from_user.id < 0):  # Сначала нужно кинуть медиа в бота или постить не анонимно
            await bot.delete_message(CHANNEL_ID, message.message_id)
            return

        if not attachment:  # Если выложили новое медиа не анонимно
            user = get_user(message.from_user, session)
            attachment = Attachment(type_id=attachment_type.id, hash=file_hash, from_user_id=user.id)
            session.add(attachment)
            session.commit()

        # Write message to db
        item = AttachmentItem(
            attachment_id=attachment.id,
            media_group_id=media_group_id,
            message_id=message.message_id,
            created_at=datetime.now()
        )
        session.add(item)

        if not attachment.is_banned:
            session.commit()
        else:
            await bot.delete_message(CHANNEL_ID, message.message_id)
            session.rollback()

    await process_link_preview(message)


@bot.channel_post_handler(commands=['ban'])
async def ban_content(message: telebot.types.Message):
    if (message.chat.id != CHANNEL_ID
            or not message.reply_to_message
            or not message.from_user
            or message.from_user.id != ADMIN_ID):
        await bot.delete_message(message.chat.id, message.message_id)
        return

    target_message = message.reply_to_message
    media_group_id = get_media_group_id(target_message)

    with Session() as session:
        attachment_items = session.query(AttachmentItem).filter_by(media_group_id=media_group_id).all()

        args = list(map(int, message.text.split()[1:])) or list(
            range(1, len(attachment_items) + 1))  # args from the command

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


@bot.channel_post_handler(commands=['mute'])
async def mute(message: telebot.types.Message):
    if (message.chat.id != CHANNEL_ID
            or not message.reply_to_message
            or not message.from_user
            or message.from_user.id != ADMIN_ID):
        await bot.delete_message(message.chat.id, message.message_id)
        return

    text_manager.mark_explicit(message.reply_to_message.text.lower())


@bot.channel_post_handler(content_types=['text'])
async def text_handler(message: telebot.types.Message):
    text = message.text.lower()

    if not text_manager.check_is_available(text, datetime.now()):
        await bot.delete_message(CHANNEL_ID, message.message_id)
        return

    text_manager.add_text(message.text.lower(), datetime.now())

    await process_link_preview(message)


# Accept posts from direct messages

@bot.message_handler(content_types=MODERATING_TYPES, func=lambda message: message.chat.id == message.from_user.id)
async def handle_direct_media(message: telebot.types.Message):
    await handle_direct_message(message)


@bot.message_handler(func=lambda message: message.chat.id == message.from_user.id)
async def handle_direct_message(message: telebot.types.Message):
    admins_list = await bot.get_chat_administrators(CHANNEL_ID)
    admin_ids = [admin.user.id for admin in admins_list]

    if message.from_user.id not in admin_ids:  # Чтобы не писали с фейк аккаунтов
        await bot.reply_to(message, "Бот может использоваться только администраторами канала.")

    with Session() as session:
        user = get_user(message.from_user, session)

        if not user.is_agreement_accepted:  # Сначала нужно принять соглашение
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("Принимаю соглашение", callback_data="cb_accept_agreement"))

            await bot.reply_to(
                message,
                f"Для публикации медиа вы должны принять текст соглашения:\n\nЯ, {user.first_name} {user.last_name}, обязуюсь не публиковать контент, нарушающий законы Российской Федерации, а также не публиковать контент, нарушающий правила канала (правила канала, при их наличии, публикуются в канале и закрепляются).",
                reply_markup=markup
            )

            return

        attachment_data = await parse_attachment(message)

        content_type = attachment_data.content_type
        file_hash = attachment_data.hash

        attachment_type = session.query(AttachmentType).filter_by(name=content_type).first()

        if not attachment_type:
            attachment_type = AttachmentType(name=content_type)
            session.add(attachment_type)
            session.commit()

        attachment = session.query(Attachment).filter_by(type_id=attachment_type.id, hash=file_hash).first()

        if attachment:
            await bot.reply_to(message, "Медиа уже было опубликовано")
            return

        attachment = Attachment(type_id=attachment_type.id, hash=file_hash, from_user_id=user.id)
        session.add(attachment)
        session.commit()

        await bot.reply_to(message, "Медиа доступно для публикации")


@bot.callback_query_handler(func=lambda call: call.data == "cb_accept_agreement")
async def accept_agreement(call: telebot.types.CallbackQuery):
    with Session() as session:
        user = get_user(call.from_user, session)

        if not user:
            await bot.answer_callback_query(call.id, "Произошла ошибка. Попробуйте еще раз.")

        if user.is_agreement_accepted:
            await bot.answer_callback_query(call.id, "Соглашение уже принято.")
            return

        user.is_agreement_accepted = True
        session.commit()

        await bot.answer_callback_query(call.id, "Соглашение принято.")
        await bot.send_message(call.from_user.id,
                               "Согласие принято. Теперь вы можете отправлять сюда медиа, которые хотите опубликовать, они будут допущены к публикации без ограничения по числу постов. Но тем не менее, данные о том, кто допустил медиа к публикации, у нас остаются")


async def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    await bot.polling(non_stop=True, request_timeout=60)


asyncio.run(main())
