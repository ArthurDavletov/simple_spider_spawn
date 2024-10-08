import os
import sys
import tkinter as tk
from PIL import ImageTk, Image
from blocks import Blocks
from territory import Territory
from logger import Logger


def get_resized_image(file, width: int) -> Image:
    """Функция возвращает квадратное изображение произвольного размера width"""
    return Image.open(file).resize((width, width))


def resource_path(relative_path):
    """Получает абсолютный путь к файлу.
    Функция необходима из-за Pyinstaller, так как без него файлы не находятся."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Window(tk.Tk):
    """Окно 540x540. Расположен canvas, где размещены кнопки"""
    def __init__(self, logging_level: int | str = 0, *args, **kwargs):
        """Инициализатор класса Window

        Параметры:

        * logging_level
            Отвечает за уровень логирования. По умолчанию отлавливаются все события (считая 'INFO').
            Для ведения менее подробного журнала следует использовать 'ERROR', logging.ERROR или 40
        * Позиционные и именованные аргументы родительского класса tk.TK"""
        self.__logger = Logger(__name__, logging_level)

        self.__width, self.__height = 540, 540
        self.__png_size = int(self.__width / 18)  # размер картинки на кнопке
        self.__png_cache_path = os.path.join(".cache", __name__, str(self.__png_size))
        super().__init__(*args, **kwargs)
        self.geometry(f"{self.__width}x{self.__height}")
        self.resizable(False, False)
        self.title("Проверка появления пауков")

        self.__logger.info("Начало загрузки элементов")
        self.__images: dict[Blocks, ImageTk.PhotoImage] = dict()
        self.__load_images()

        self.__logger.info("Изображения загружены")

        self.__canvas = tk.Canvas(bg= "white", width=self.__width, height=self.__height)
        self.__canvas.pack(anchor=tk.CENTER, expand=1)
        self.__territory = Territory(logging_level)
        self.__logger.info("Создание и размещение кнопок")
        self.__buttons: list[list[tk.Button]] = [[tk.Button(width=int(self.__width / 18),
                                                            height=int(self.__height / 18),
                                                            command=lambda x=x, y=y: self.__select_cell(x, y))
                                                  for y in range(18)] for x in range(18)]
        self.__place_buttons()
        self.__logger.info("Кнопки размещены")
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __on_closing(self):
        """Событие происходит при закрытии приложении.
        Важно сохранить данные поля, так как предполагается, что изображения уже сохранены"""
        self.__territory.save()
        self.destroy()

    def __save_images(self):
        """Сохранение изображений в кеш"""
        filenames = ["red_wool.png", "stone.png", "trapdoor.png", "water.png"]
        if not os.path.exists(self.__png_cache_path):
            os.makedirs(self.__png_cache_path)
        not_existing_files = []
        for filename in filenames:
            abspath = resource_path(os.path.join("assets", filename))
            if not os.path.exists(abspath):
                not_existing_files.append(abspath)
        if len(not_existing_files) != 0:
            self.__logger.error(f"Следующие файлы не были обнаружены: {', '.join(map(str, not_existing_files))}")
            raise FileNotFoundError(f"Файлы изображений не найдены: {', '.join(map(str, not_existing_files))}")
        for filename in filenames:
            abspath = resource_path(os.path.join("assets", filename))
            get_resized_image(abspath, self.__png_size).save(os.path.join(self.__png_cache_path, filename))

    def __load_images(self):
        """Загрузка изображений из кеша. Если такого нет, то происходит их создание"""
        filenames = ["red_wool.png", "stone.png", "trapdoor.png", "water.png"]
        blocks = [Blocks.RED_WOOL, Blocks.STONE, Blocks.TRAPDOOR, Blocks.WATER]
        if not all(os.path.exists(os.path.join(self.__png_cache_path, filename)) for filename in filenames):
            self.__save_images()
            self.__logger.info("Кеш изображений создан")
        self.__logger.info("Обращение к заранее созданным изображениям")
        for block, filename in zip(blocks, filenames):
            self.__images[block] = ImageTk.PhotoImage(
                Image.open(
                    os.path.join(self.__png_cache_path, filename)
                )
            )

    def __update_button(self, x: int, y: int) -> None:
        """Обновляет состояние кнопки по указанным координатам (нумерация с 0)"""
        block = self.__territory.get(x, y)
        btn = self.__buttons[x][y]
        if block is None:
            btn.configure(state="disabled")
            return
        if block not in self.__images:
            self.__logger.error(f"Попытка добавить несуществующий блок: {block}")
            raise NotImplementedError(f"Данный блок ({block}) пока не поддерживается")
        btn.configure(image=self.__images[block])
        self.__canvas.create_window(self.__width / 18 * x, self.__height / 18 * y,
                                    window=btn, anchor = "nw",
                                    width=self.__width / 18, height=self.__height / 18)

    def __place_buttons(self) -> None:
        """Первичное заполнение кнопками"""
        for x in range(18):
            for y in range(18):
                self.__update_button(x, y)

    def __select_cell(self, x: int, y: int) -> None:
        """Выбор клетки по указанным координатам (нумерация с 0)"""
        self.__territory.select(x, y)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if 0 <= x + dx < len(self.__buttons) and 0 <= y + dy < len(self.__buttons[x + dx]):
                    self.__update_button(x + dx, y + dy)
