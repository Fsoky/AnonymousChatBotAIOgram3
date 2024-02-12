from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import main_kb
from db import Users

router = Router()


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    if not user:
        session.add(Users(id=message.from_user.id))
        await session.commit()

    searchers = await session.scalars(select(Users).where(Users.status == 1))
    await message.reply(
        "<b>☕ Начинай поиск собеседника!</b>\n"
        f"<i>👀 Участников в поиске:</i> <code>{len(searchers.fetchall())}</code>",
        reply_markup=main_kb
    )