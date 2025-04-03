import logging
from logging.handlers import RotatingFileHandler

LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_MAX_COUNT: int = 5


class LoggerConfig:
    """Класс для настройки логирования."""

    def __init__(
            self,
            logger_name: str = "default_logger",
            log_file: str = "default.log",
            log_level: int = logging.INFO,
            max_bytes: int = LOG_FILE_MAX_BYTES,
            backup_count: int = LOG_FILE_BACKUP_MAX_COUNT,
            console_output: bool = True
    ) -> None:
        """
        Инициализация конфигурации логирования.

        :param logger_name: Имя логгера.
        :param log_file: Путь к файлу логов.
        :param log_level: Уровень логирования (по умолчанию INFO).
        :param max_bytes: Максимальный размер файла логов в байтах.
        :param backup_count: Количество резервных копий логов.
        :param console_output: Выводить ли логи в консоль.
        """
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(log_level)

        log_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="UTF-8"
        )
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
