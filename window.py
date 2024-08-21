import tkinter as tk
from PIL import ImageTk, Image
from blocks import Blocks
from territory import Territory
from logger import Logger


def get_resized_image(file: str, width: int, height: int) -> ImageTk.PhotoImage:
    image = Image.open(file).resize((width, height))
    return ImageTk.PhotoImage(image)


class Window(tk.Tk):
    """Окно 540x540. Расположен canvas, где размещены кнопки"""
    def __init__(self, *args, **kwargs):
        self.__logger = Logger(__name__)

        self.__width, self.__height = 540, 540
        super().__init__(*args, **kwargs)
        self.geometry(f"{self.__width}x{self.__height}")
        self.resizable(False, False)
        self.title("Проверка появления пауков")

        self.__logger.info("Начало загрузки элементов")

        self.__red_wool_image = get_resized_image("assets/BlockSprite_red-wool.png",
                                                  int(self.__width / 18), int(self.__height / 18))
        self.__stone_image = get_resized_image("assets/BlockSprite_stone.png",
                                               int(self.__width / 18), int(self.__height / 18))
        self.__trapdoor_image = get_resized_image("assets/BlockSprite_spruce-trapdoor.png",
                                                  int(self.__width / 18), int(self.__height / 18))
        self.__water_image = get_resized_image("assets/BlockSprite_water.png",
                                               int(self.__width / 18), int(self.__height / 18))

        self.__logger.info("Изображения загружены")

        self.__canvas = tk.Canvas(bg= "white", width=self.__width, height=self.__height)
        self.__canvas.pack(anchor=tk.CENTER, expand=1)
        self.__territory = Territory()
        self.__logger.info("Создание и размещение кнопок")
        self.__buttons: list[list[tk.Button]] = [[tk.Button(width=int(self.__width / 18),
                                                            height=int(self.__height / 18),
                                                            command=lambda x=x, y=y: self.__select_cell(x, y))
                                                  for y in range(18)] for x in range(18)]
        self.__place_buttons()
        self.__logger.info("Кнопки размещены")

    def __update_button(self, x: int, y: int) -> None:
        """Обновляет состояние кнопки по указанным координатам (нумерация с 0)"""
        block = self.__territory.get(x, y)
        btn = self.__buttons[x][y]
        image = None
        match block:
            case None:
                btn.configure(state="disabled")
                return
            case Blocks.TRAPDOOR:
                image = self.__trapdoor_image
            case Blocks.STONE:
                image = self.__stone_image
            case Blocks.WATER:
                image = self.__water_image
            case Blocks.RED_WOOL:
                image = self.__red_wool_image
            case _:
                self.__logger.error(f"Попытка добавить несуществующий блок: {block}")
                raise NotImplementedError(f"Данный блок ({block}) пока не поддерживается")
        btn.configure(image=image)
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
                if 0 <= x + dx < len(self.__buttons) and 0 <= y + dy < len(self.__buttons):
                    self.__update_button(x + dx, y + dy)
