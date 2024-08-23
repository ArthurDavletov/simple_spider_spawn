import logging
import logging.handlers
import os
import time


class CustomFormatter(logging.Formatter):
    """Кастомный форматер для даты и времени. С поддержкой миллисекунд"""
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, dt)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", dt)
        return f"{s}.{int(record.msecs):03d}"


class Logger(logging.Logger):
    """Класс, отвечающий за логирование. Отличается от обычного логгера за счёт ротирования файлов,
    а также кастомной даты формата ДД.ММ.ГГГГ ЧЧ:ММ:СС.ммм"""
    def __init__(self, name: str, level: int | str = 0):
        """Создаёт экземпляр логгера

        Параметры:
            * name: str
                Имя логгера (от него зависят название файлов логов)
            * level:
                Уровень логирования. По умолчанию логируются все действия (в частности 'INFO').
                Для уменьшения логов следует использовать 'ERROR' или 40"""
        super().__init__(name, level)
        if not os.path.exists("logs"):
            os.makedirs("logs")
        self.__handler = logging.handlers.RotatingFileHandler(f"logs/{name}.log",
                                                              encoding = "utf-8",
                                                              maxBytes = 2 * 10 ** 6,
                                                              backupCount = 5)
        self.__formatter = CustomFormatter("%(name)s | %(asctime)s | %(levelname)s | %(message)s",
                                           "%d.%m.%Y %H:%M:%S")
        self.__handler.setFormatter(self.__formatter)
        self.addHandler(self.__handler)
