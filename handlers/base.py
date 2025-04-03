from aiogram import Bot, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from core import messages
from data.manager import DataManager
from states.purchases import AddPurchase

router = Router()


def setup_handlers(data_manager: DataManager) -> Router:
    """Настройка хендлеров с передачей DataManager."""

    @router.message(Command("start"))
    async def cmd_start(msg: Message, bot: Bot) -> None:
        first_name: str = msg.from_user.first_name
        last_name: str = msg.from_user.last_name
        await msg.answer(
            messages.WELCOME.format(
                name=first_name or last_name or 'Пришелец'
            )
        )

    @router.message(Command("help"))
    async def cmd_help(msg: Message, bot: Bot) -> None:
        await msg.answer(messages.HELP)

    @router.message(StateFilter(None), Command("add"))
    async def cmd_add(msg: Message, state: FSMContext) -> None:
        await msg.reply("💲 Введите название актива (например, BTC)")
        await state.set_state(AddPurchase.asset)

    @router.message(AddPurchase.asset)
    async def process_asset(msg: Message, state: FSMContext) -> None:
        await state.update_data(asset=msg.text.strip().lower())
        await msg.answer("Введите цену покупки")

        await state.set_state(AddPurchase.price)

    @router.message(AddPurchase.price)
    async def process_price(msg: Message, state: FSMContext) -> None:
        try:
            price = float(msg.text.strip())
            if price <= 0:
                raise ValueError("Цена должна быть положительной")
        except ValueError:
            await msg.reply(
                "Цена должна быть числом больше 0. Попробуйте снова"
            )
        else:
            await state.update_data(price=price)
            await msg.reply("Введите количество монет (например, 2.5)")
            await state.set_state(AddPurchase.amount)

    @router.message(AddPurchase.amount)
    async def process_amount(msg: Message, state: FSMContext) -> None:
        try:
            amount = float(msg.text.strip())
            if amount <= 0:
                raise ValueError("Количество должно быть положительным")
            await state.update_data(amount=amount)
            data = await state.get_data()
            output = messages.PURCHASE_INPUT_DATA.format(
                asset=data['asset'],
                price=data['price'],
                amount=data['amount'],
            )

            await msg.answer(
                f"🏁 Все верно?\n{output}\n\nВведите 'да' для подтверждения"
            )
            await state.set_state(AddPurchase.confirm)
        except ValueError:
            await msg.reply(
                "Количество должно быть числом больше 0. Попробуйте снова"
            )

    @router.message(AddPurchase.confirm)
    async def process_confirm(msg: Message, state: FSMContext) -> None:
        if msg.text.strip().lower() != "да":
            await msg.answer("Добавление отменено")
            await state.clear()
            return

        data = await state.get_data()
        user_id = msg.from_user.id
        asset = data["asset"]
        price = data["price"]
        amount = data["amount"]

        data_manager.add_purchase(user_id, asset, price, amount)
        avg_price, total_amount, total_cost = data_manager.get_stats(
            user_id, asset
        )

        await msg.answer(
            messages.ADDED_PURCHASE_INFO.format(
                asset=asset,
                price=price,
                amount=amount,
                avg_price=avg_price,
                total_amount=total_amount,
                total_cost=total_cost,
            )
        )
        await state.clear()

    @router.message(Command("view"))
    async def cmd_view(msg: Message) -> None:
        user_id = msg.from_user.id
        assets = data_manager.get_user_assets(user_id)
        if not assets:
            await msg.reply("У вас нет покупок")
            return

        for asset in assets:
            avg_price, total_amount, total_cost = data_manager.get_stats(
                user_id, asset
            )
            await msg.reply(
                messages.AVG_PRICE_INFO.format(
                    asset=asset,
                    avg_price=avg_price,
                    total_amount=total_amount,
                    total_cost=total_cost,
                )
            )

    @router.message(Command("clear"))
    async def cmd_clear(msg: Message) -> None:
        user_id = msg.from_user.id
        assets = data_manager.get_user_assets(user_id)

        if not assets:
            await msg.reply("У вас нет покупок для очистки")
            return

        data_manager.clear(user_id)
        await msg.reply("Все данные о покупках очищены")

    return router
