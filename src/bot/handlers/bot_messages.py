from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states import ChatForm
from db import Users

router = Router()


# ! NOT WORKING!!!
# @router.edited_message(ChatForm.chatting)
# async def editing_messages(message: Message, **data) -> None:
#     user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
#     if user.status == 2:
#         if message.text:
#             await message.bot.edit_message_text(
#                 message.text, user.interlocutor, message.message_id + 1
#             )
#         elif message.caption:
#             await message.bot.edit_message_caption(
#                 message.caption,
#                 user.interlocutor,
#                 message.message_id + 1,
#                 caption_entities=message.caption_entities,
#                 parse_mode=None
#             )


@router.message(
    ChatForm.chatting,
    F.content_type.in_(
        [
            "text", "audio", "voice",
            "sticker", "document", "photo",
            "video"
        ]
    )
)
async def echo(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    
    if user.status == 2:
        if message.content_type == "text":
            reply = None
            if message.reply_to_message:
                if message.reply_to_message.from_user.id == message.from_user.id:
                    reply = message.reply_to_message.message_id + 1
                else:
                    reply = message.reply_to_message.message_id - 1

            await message.bot.send_message(
                user.interlocutor,
                message.text,
                entities=message.entities,
                reply_to_message_id=reply,
                parse_mode=None
            )
        if message.content_type == "photo":
            await message.bot.send_photo(
                user.interlocutor,
                message.photo[-1].file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                parse_mode=None,
                has_spoiler=True
            )
        if message.content_type == "audio":
            await message.bot.send_audio(
                user.interlocutor,
                message.audio.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                parse_mode=None
            )
        if message.content_type == "voice":
            await message.bot.send_voice(
                user.interlocutor,
                message.voice.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                parse_mode=None
            )
        if message.content_type == "document":
            await message.bot.send_document(
                user.interlocutor,
                message.document.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                parse_mode=None
            )
        if message.content_type == "sticker":
            await message.bot.send_sticker(
                user.interlocutor,
                message.sticker.file_id
            )
        if message.content_type == "video":
            await message.bot.send_video(
                user.interlocutor,
                message.video.file_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                parse_mode=None,
                has_spoiler=True
            )
