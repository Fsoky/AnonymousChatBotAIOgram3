from aiogram.fsm.state import StatesGroup, State


class ChatForm(StatesGroup):
    searching = State()
    chatting = State()