from aiogram.fsm.state import State, StatesGroup


class AddPurchase(StatesGroup):
    asset = State()
    price = State()
    amount = State()
    confirm = State()
