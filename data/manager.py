import logging

from core.logging import LoggerConfig
from .abstract import Storage

logger = LoggerConfig(
    logger_name="data_manager",
    log_file="cca_bot.log",
    log_level=logging.INFO
).get_logger()


class DataManager:
    """Класс для управления данными о покупках."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        logger.info("Инициализирован DataManager")

    def add_purchase(
            self, user_id: int, asset: str, price: float, amount: float
    ) -> None:
        self.storage.add_purchase(user_id, asset, price, amount)
        logger.info(
            f"Добавлена покупка: user_id={user_id}, "
            f"asset={asset}, price={price}, amount={amount}"
        )

    def __get_total_cost(self, purchases) -> float:
        return sum(
            p["price"] * p["amount"] for p in purchases
        )

    def __get_total_amount(self, purchases) -> float:
        return sum(p["amount"] for p in purchases)

    def __get_avg_price(self, cost: float, amount: float) -> float:
        if amount > 0:
            return cost / amount
        return 0.0

    def get_stats(
            self, user_id: int, asset: str
    ) -> tuple[float, float, float]:
        purchases: list[dict[str, float]] = self.storage.get_purchases(
            user_id, asset
        )
        if not purchases:
            logger.debug(f"Нет покупок для user_id={user_id}, asset={asset}")
            return 0.0, 0.0, 0.0

        total_cost = self.__get_total_cost(purchases)
        total_amount = self.__get_total_amount(purchases)
        avg_price = self.__get_avg_price(total_cost, total_amount)

        logger.debug(
            f"Рассчитаны статистики: user_id={user_id}, "
            f"asset={asset}, avg_price={avg_price}, "
            f"total_amount={total_amount}, total_cost={total_cost}"
        )
        return avg_price, total_amount, total_cost

    def get_user_assets(self, user_id: int) -> list[str]:
        assets = self.storage.get_user_assets(user_id)
        logger.debug(
            f"Получены активы для user_id={user_id}: {assets}"
        )
        return assets

    def clear(self, user_id: int, asset: str = None) -> None:
        self.storage.clear(user_id, asset)
        logger.info(
            f"Очищены данные: user_id={user_id}, "
            f"asset={asset if asset else 'все'}"
        )
