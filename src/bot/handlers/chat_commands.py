from aiogram import Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import reply_builder, main_kb
from bot.states import ChatForm
from db import Users

router = Router()


@router.message(or_f(Command("search"), F.text == "☕ Искать собеседника"))
async def search_interlocutor(
    message: Message, state: FSMContext, dispatcher: Dispatcher, session: AsyncSession
) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    pattern = {
        "text": (
            "<b>☕ У тебя уже есть активный чат</b>\n"
            "<i>Используй команду /leave, чтобы покинуть чат</i>"
        ),
        "reply_markup": reply_builder("🚫 Прекратить диалог")
    }

    if user.status == 0:
        interlocutor = await session.scalar(select(Users).where(Users.status == 1))
        user.status = 1

        if not interlocutor:
            pattern["text"] = (
                "<b>👀 Ищу тебе собеседника...</b>\n"
                "<i>/cancel - Отменить поиск собеседника</i>"
            )
            pattern["reply_markup"] = reply_builder("❌ Отменить поиск")

            await state.set_state(ChatForm.searching)
        else:
            pattern["text"] = (
                "<b>🎁 Я нашел тебе собеседника, приятного общения!</b>\n"
                "<i>/next - Следующий собеседник</i>\n"
                "<i>/leave - Прекратить диалог</i>"
            )
            pattern["reply_markup"] = reply_builder("🚫 Прекратить диалог")
            
            user.interlocutor = interlocutor.id
            user.status = 2
            interlocutor.interlocutor = user.id
            interlocutor.status = 2

            await state.set_state(ChatForm.chatting)
            await dispatcher.fsm.get_context(
                message.bot, interlocutor.id, interlocutor.id
            ).set_state(ChatForm.chatting)

            await message.bot.send_message(interlocutor.id, **pattern)
    elif user.status == 1:
        pattern["text"] = (
            "<b>👀 УЖЕ ИЩУ тебе собеседника...</b>\n"
            "<i>/cancel - Отменить поиск собеседника</i>"
        )
        pattern["reply_markup"] = reply_builder("❌ Отменить поиск")

    await session.commit()
    await message.reply(**pattern)


@router.message(ChatForm.searching, or_f(Command("cancel"), F.text == "❌ Отменить поиск"))
async def cancel_search(message: Message, session: AsyncSession) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    user.status = 0

    await session.commit()
    await message.reply(
        "<b>😔 Все.. больше никого искать не буду!</b>", reply_markup=main_kb
    )


@router.message(
    ChatForm.chatting,
    or_f(Command(commands=["leave", "stop"]), F.text == "🚫 Прекратить диалог")
)
async def leave(
    message: Message, state: FSMContext, dispatcher: Dispatcher, session: AsyncSession
) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    interlocutor = await session.scalar(
        select(Users).where(Users.interlocutor == message.from_user.id)
    )

    await message.reply("<b>💬 Ты покинул чат!</b>", reply_markup=main_kb)
    await message.bot.send_message(
        user.interlocutor, "<b>💬 Собеседник покинул чат!</b>", reply_markup=main_kb
    )

    user.status = 0
    user.interlocutor = None
    interlocutor.status = 0
    interlocutor.interlocutor = None

    await session.commit()
    await state.clear()
    await dispatcher.fsm.get_context(message.bot, interlocutor.id, interlocutor.id).clear()


@router.message(ChatForm.chatting, Command("next"))
async def next_interlocutor(
    message: Message, state: FSMContext, dispatcher: Dispatcher, session: AsyncSession
) -> None:
    user = await session.scalar(select(Users).where(Users.id == message.from_user.id))
    interlocutor = await session.scalar(
        select(Users).where(Users.interlocutor == message.from_user.id)
    )

    await message.reply("<b>💬 Ты покинул чат!</b>", reply_markup=main_kb)
    await message.bot.send_message(
        user.interlocutor, "<b>💬 Собеседник покинул чат!</b>", reply_markup=main_kb
    )

    user.status = 0
    user.interlocutor = None
    interlocutor.status = 0
    interlocutor.interlocutor = None

    await session.commit()
    await state.clear()
    await dispatcher.fsm.get_context(message.bot, interlocutor.id, interlocutor.id).clear()

    await search_interlocutor(message, state, dispatcher, session)