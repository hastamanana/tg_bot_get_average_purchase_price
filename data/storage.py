import json
import logging
import os
import sqlite3
from typing import IO

from core.logging import LoggerConfig
from .abstract import Storage

logger = LoggerConfig(
    logger_name="storage",
    log_file="cca_bot.log",
    log_level=logging.INFO
).get_logger()


class MemoryStorage(Storage):
    """Хранилище данных в памяти."""

    def __init__(self) -> None:
        self.data: dict[int, dict[str, list[dict[str, float]]]] = {}
        logger.info("Инициализировано хранилище в памяти")

    def add_purchase(
            self, user_id: int, asset: str, price: float, amount: float
    ) -> None:
        if user_id not in self.data:
            self.data[user_id] = {}
        if asset not in self.data[user_id]:
            self.data[user_id][asset] = []

        self.data[user_id][asset].append(
            {"price": price, "amount": amount}
        )
        logger.debug(
            f"Добавлена покупка: user_id={user_id}, "
            f"asset={asset}, price={price}, amount={amount}"
        )

    def get_purchases(
            self, user_id: int,
            asset: str,
    ) -> list[dict[str, float]]:
        purchases = self.data.get(user_id, {}).get(asset, [])
        logger.debug(
            f"Получены покупки: user_id={user_id}, "
            f"asset={asset}, count={len(purchases)}"
        )

        return purchases

    def get_user_assets(self, user_id: int) -> list[str]:
        assets = list(self.data.get(user_id, {}).keys())
        logger.debug(f"Получены активы: user_id={user_id}, assets={assets}")

        return assets

    def clear(self, user_id: int, asset: str = None) -> None:
        if user_id not in self.data:
            logger.debug(
                f"Попытка очистки для несуществующего user_id={user_id}"
            )
            return

        if asset is None:
            self.data[user_id] = {}
            logger.info(f"Очищены все данные для user_id={user_id}")
        else:
            self.data[user_id].pop(asset, None)
            logger.info(
                f"Очищены данные для user_id={user_id}, asset={asset}"
            )


class SQLiteStorage(Storage):
    """Хранилище данных в SQLite."""

    def __init__(self, db_path: str = "purchases.db") -> None:
        self.db_path = db_path
        self._init_db()
        logger.info(f"Инициализировано SQLite хранилище: {db_path}")

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchases (
                    user_id INTEGER,
                    asset TEXT,
                    price REAL,
                    amount REAL,
                    PRIMARY KEY (user_id, asset, price, amount)
                )
            """)
            conn.commit()
            logger.debug(
                f"Создана таблица purchases в SQLite -> '{self.db_path}'"
            )

    def add_purchase(
            self, user_id: int, asset: str, price: float, amount: float
    ) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO purchases (user_id, asset, price, amount) 
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, asset, price, amount)
                )
                conn.commit()
                logger.debug(
                    f"Добавлена покупка в SQLite: user_id={user_id}, "
                    f"asset={asset}, price={price}, amount={amount}"
                )
        except sqlite3.Error as err_msg:
            logger.error(f"Ошибка при добавлении покупки в SQLite: {err_msg}")

    def get_purchases(self, user_id: int, asset: str
                      ) -> list[dict[str, float]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT price, amount 
                    FROM purchases 
                    WHERE user_id = ? AND asset = ?
                    """,
                    (user_id, asset)
                )
                purchases: list[dict[str, float]] = [
                    {"price": row[0], "amount": row[1]}
                    for row in cursor.fetchall()
                ]
                logger.debug(
                    f"Получены покупки из SQLite: user_id={user_id}, "
                    f"asset={asset}, count={len(purchases)}"
                )
                return purchases
        except sqlite3.Error as err_msg:
            logger.error(f"Ошибка при получении покупок из SQLite: {err_msg}")
            return []

    def get_user_assets(self, user_id: int) -> list[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT DISTINCT asset 
                    FROM purchases 
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                assets = [row[0] for row in cursor.fetchall()]
                logger.debug(
                    "Получены активы из SQLite: "
                    f"user_id={user_id}, assets={assets}"
                )
                return assets
        except sqlite3.Error as err_msg:
            logger.error(f"Ошибка при получении активов из SQLite: {err_msg}")
            return []

    def clear(self, user_id: int, asset: str = None) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if asset is None:
                    cursor.execute(
                        """
                        DELETE FROM purchases WHERE user_id = ?
                        """, (user_id,)
                    )
                    logger.info(
                        f"Очищены все данные в SQLite для user_id={user_id}"
                    )
                else:
                    cursor.execute(
                        "DELETE FROM purchases "
                        "WHERE user_id = ? AND asset = ?",
                        (user_id, asset)
                    )
                    logger.info(
                        "Очищены данные в SQLite для "
                        f"user_id={user_id}, asset={asset}"
                    )
                conn.commit()
        except sqlite3.Error as err_msg:
            logger.error(f"Ошибка при очистке данных в SQLite: {err_msg}")


class JSONStorage(Storage):
    """Хранилище данных в JSON-файле."""

    def __init__(self, file_path: str = "purchases.json") -> None:
        self.file_path = file_path
        self.data: dict[int, dict[str, list[dict[str, float]]]] = self._load_data()  # noqa: skip
        logger.info(f"Инициализировано JSON хранилище: {file_path}")

    def _load_data(self) -> dict[int, dict[str, list[dict[str, float]]]]:
        if not os.path.exists(self.file_path):
            logger.debug(
                f"JSON файл не существует, создан новый: {self.file_path}"
            )
            return {}

        try:
            with open(self.file_path, "r", encoding="UTF-8") as f:
                return json.load(f)
        except Exception as err_msg:
            logger.error(f"Ошибка при загрузке JSON: {err_msg}")
            return {}

    def _save_data(self) -> None:
        try:
            with open(
                    self.file_path, "w", encoding="UTF-8"
            ) as file:  # type: IO[str]
                json.dump(self.data, file, indent=4)

            logger.debug(f"Данные сохранены в JSON: {self.file_path}")
        except Exception as err_msg:
            logger.error(f"Ошибка при сохранении JSON: {err_msg}")

    def add_purchase(
            self, user_id: int, asset: str, price: float, amount: float
    ) -> None:
        if user_id not in self.data:
            self.data[user_id] = {}
        if asset not in self.data[user_id]:
            self.data[user_id][asset] = []

        self.data[user_id][asset].append({"price": price, "amount": amount})
        self._save_data()
        logger.debug(
            f"Добавлена покупка в JSON: user_id={user_id}, "
            f"asset={asset}, price={price}, amount={amount}"
        )

    def get_purchases(
            self, user_id: int, asset: str
    ) -> list[dict[str, float]]:
        purchases = self.data.get(user_id, {}).get(asset, [])
        logger.debug(
            f"Получены покупки из JSON: user_id={user_id}, "
            f"asset={asset}, count={len(purchases)}"
        )

        return purchases

    def get_user_assets(self, user_id: int) -> list[str]:
        assets = list(self.data.get(user_id, {}).keys())
        logger.debug(
            f"Получены активы из JSON: user_id={user_id}, assets={assets}"
        )

        return assets

    def clear(self, user_id: int, asset: str = None) -> None:
        if user_id not in self.data:
            logger.debug(
                f"Попытка очистки для несуществующего user_id={user_id}"
            )
            return None

        if asset is None:
            self.data[user_id] = {}
            logger.info(f"Очищены все данные в JSON для user_id={user_id}")
        else:
            self.data[user_id].pop(asset, None)
            logger.info(
                f"Очищены данные в JSON для user_id={user_id}, asset={asset}"
            )

        self._save_data()
