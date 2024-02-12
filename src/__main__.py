import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from bot.handlers import setup_message_routers
from bot.middlewares import DBSessionMiddleware, CheckUser

from db import Base
from config_reader import config


async def on_startup(_engine: AsyncEngine) -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(session: AsyncSession) -> None:
    await session.close()


async def main() -> None:
    _engine = create_async_engine(config.DATABASE_URL.get_secret_value())
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)

    bot = Bot(config.BOT_TOKEN.get_secret_value(), parse_mode=ParseMode.HTML)
    dp = Dispatcher(_engine=_engine, storage=RedisStorage.from_url(config.REDIS_URL))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(DBSessionMiddleware(_sessionmaker))
    dp.message.middleware(CheckUser())

    message_routers = setup_message_routers()
    dp.include_router(message_routers)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())