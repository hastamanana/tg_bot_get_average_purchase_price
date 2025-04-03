import logging

from core.logging import LoggerConfig
from .abstract import Storage
from .storage import JSONStorage, MemoryStorage, SQLiteStorage

logger = LoggerConfig(
    logger_name="factory",
    log_file="cca_bot.log",
    log_level=logging.INFO
).get_logger()


class StorageFactory:
    """Фабрика для создания хранилищ данных."""

    @staticmethod
    def create_storage(storage_type: str, **kwargs) -> Storage:
        if storage_type == "memory":
            return MemoryStorage()
        elif storage_type == "sqlite":
            return SQLiteStorage(
                db_path=kwargs.get("db_path", "purchases.db")
            )
        elif storage_type == "json":
            return JSONStorage(
                file_path=kwargs.get("file_path", "purchases.json")
            )

        logger.error(f"Неизвестный тип хранилища: {storage_type}")
        raise TypeError(f"Неизвестный тип хранилища: {storage_type}")
