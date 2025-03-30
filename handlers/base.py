from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import AddPurchase

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message, bot: Bot):
    await msg.answer("Привет, незнакомец!")


@router.message(Command("help"))
async def cmd_help(msg: Message, bot: Bot):
    await msg.answer(
        "Бот получает название актива (BTC), далее пользователь"
        "\nвводит кол-во монет и цену покупки неограниченное кол-во раз."
    )


@router.message(StateFilter(None), Command("add"))
async def cmd_add(msg: Message, state: FSMContext):
    await msg.reply("Введите название актива")
    await state.set_state(AddPurchase.asset)


@router.message(AddPurchase.asset)
async def process_asset(msg: Message, state: FSMContext):
    await state.update_data(asset=msg.text.strip().lower())
    await msg.answer(f"Введите цену")

    await state.set_state(AddPurchase.price)


@router.message(AddPurchase.price)
async def process_price(msg: Message, state: FSMContext):
    await state.update_data(price=msg.text.strip().lower())
    await msg.reply(f"Введите количество")

    await state.set_state(AddPurchase.amount)


@router.message(AddPurchase.amount)
async def process_price(msg: Message, state: FSMContext):
    await state.update_data(amount=msg.text.strip().lower())
    data = await state.get_data()
    output = (
        f"\nНазвание актива: {data['asset']}"
        f"\nЦена: {data['price']}"
        f"\nКоличество: {data['amount']}"
    )

    await msg.answer(f"Все верно?\n{output}\n\n")

    await state.set_state(AddPurchase.confirm)


@router.message(AddPurchase.confirm)
async def process_confirm(msg: Message, state: FSMContext):
    await msg.answer("Готово!")
    await state.clear()
