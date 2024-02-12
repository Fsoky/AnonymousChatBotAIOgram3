from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import select

from db import Users


class CheckUser(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        session = data["session"]
        user = await session.scalar(select(Users).where(Users.id == event.from_user.id))

        if not user:
            if event.text != "/start":
                return await event.answer("/start")
        return await handler(event, data)