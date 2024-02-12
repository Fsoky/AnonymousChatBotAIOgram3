from aiogram import Router

def setup_message_routers() -> Router:
    from . import start, chat_commands, bot_messages

    router = Router()
    router.include_router(start.router)
    router.include_router(chat_commands.router)
    router.include_router(bot_messages.router)
    return router