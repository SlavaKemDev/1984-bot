from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class AttachmentType(Base):
    __tablename__ = 'attachment_types'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String)

    attachments = relationship('Attachment', back_populates='type')


class Attachment(Base):
    __tablename__ = 'attachments'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    type_id = mapped_column(Integer, ForeignKey('attachment_types.id'))
    type = relationship('AttachmentType', back_populates='attachments')

    from_user_id = mapped_column(Integer, ForeignKey('telegram_users.id'))
    from_user = relationship('TelegramUser', back_populates='attachments')

    hash = mapped_column(String)
    is_banned = mapped_column(Boolean, default=False)

    items = relationship('AttachmentItem', back_populates='attachment')


class AttachmentItem(Base):
    __tablename__ = 'attachment_items'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    attachment_id = mapped_column(Integer, ForeignKey('attachments.id'))
    attachment = relationship('Attachment', back_populates='items')

    media_group_id = mapped_column(String)
    message_id = mapped_column(Integer)

    created_at = mapped_column(DateTime)


class TelegramUser(Base):
    __tablename__ = 'telegram_users'

    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String, nullable=True)
    first_name = mapped_column(String)
    last_name = mapped_column(String, nullable=True)

    is_agreement_accepted = mapped_column(Boolean, default=False)

    attachments = relationship('Attachment', back_populates='from_user')
