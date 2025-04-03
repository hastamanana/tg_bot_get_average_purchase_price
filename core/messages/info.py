WELCOME: str = (
    "Привет, {name}! 👋\n\n"
    "📝 Доступные операции:\n\n"
    "/add - Добавить покупку\n"
    "/view - Посмотреть среднюю цену\n"
    "/clear - Очистить данные"
)

HELP: str = (
    "Необходимо указать: \n\t"
    "- название актива\n\t"
    "- количество монет\n\t"
    "- цену покупки\n\n"
    "ℹ Используйте /add для добавления покупки"
)


PURCHASE_INPUT_DATA: str = (
    "\n🪙 Название актива: {asset}"
    "\n💱 Цена: {price}"
    "\n⚖️ Количество: {amount}"
)

ADDED_PURCHASE_INFO: str = (
    "🛒 Покупка добавлена:\n"
    "Актив: {asset}\n"
    "Цена: {price}\n"
    "Количество: {amount}\n"
    "Новая средняя цена: {avg_price:.2f}\n"
    "Общее количество: {total_amount:.2f}\n"
    "Общая стоимость: {total_cost:.2f}"
)

AVG_PRICE_INFO: str = (
    "Актив: {asset}\n"
    "Средняя цена: {avg_price:.2f}\n"
    "Общее количество: {total_amount:.2f}\n"
    "Общая стоимость: {total_cost:.2f}"
)

