import logging
import logging.handlers
import os
import time


class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, dt)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", dt)
        return f"{s}.{int(record.msecs):03d}"


class Logger(logging.Logger):
    def __init__(self, name: str, level: int | str = 40):
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
        self.setLevel(logging.INFO)
