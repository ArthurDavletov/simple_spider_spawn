from blocks import Blocks
from logger import Logger


class Territory:
    """Класс представляет собой ферму опыта. Красная шерсть означает, что там могут появиться пауки
    Публичные методы:
        select(x: int, y: int) -> None
        get(x: int, y: int) -> None
    """
    __slots__ = ("__blocks", "__logger")

    def __init__(self):
        self.__blocks: list[list[Blocks | None]] = [[None] * 18 for _ in range(18)]
        self.__logger = Logger(__name__)
        self.__logger.info("Первичное заполнение блоков")
        self.__fill_blocks()
        self.__logger.info("Заполнение закончено")

    def __fill_blocks(self) -> None:
        """Первичное заполнение"""
        for x in range(18):
            for y in range(18):
                block = None
                if x in (0, len(self.__blocks) - 1) or y in (0, len(self.__blocks) - 1):
                    block = Blocks.STONE
                if x in (8, 9) or y in (8, 9):
                    block = Blocks.WATER
                if block is None:
                    block = Blocks.RED_WOOL
                self.__blocks[x][y] = block

    def __check_cell(self, x: int, y: int) -> bool:
        """Проверяет, можно ли создать паука на этом блоке"""
        counter = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                if 0 <= x + dx < len(self.__blocks) and 0 <= y + dy < len(self.__blocks):
                    counter += self.__blocks[x + dx][y + dy] is not Blocks.TRAPDOOR
        return counter == 8

    def __update_cell(self, x: int, y: int) -> None:
        """Обновляет информацию по спауну в клетке c координатами (x, y). Нумерация с 0"""
        if self.__blocks[x][y] in (None, Blocks.WATER, Blocks.TRAPDOOR):
            return
        if self.__check_cell(x, y):
            self.__blocks[x][y] = Blocks.RED_WOOL
        else:
            self.__blocks[x][y] = Blocks.STONE

    def select(self, x: int, y: int) -> None:
        """Происходит выбор клетки. Нумерация с 0
        Если там вода или пустота, ничего не происходит. Иначе ставится / убирается люк"""
        if self.__blocks[x][y] in (None, Blocks.WATER):
            self.__logger.info(f"Выбран пустой блок или вода на ({x}, {y})")
            return
        if self.__blocks[x][y] is not Blocks.TRAPDOOR:
            self.__logger.info(f"Выбран камень или шерсть на ({x}, {y})")
            self.__blocks[x][y] = Blocks.TRAPDOOR
        else:
            self.__logger.info(f"Выбран люк на ({x}, {y})")
            self.__blocks[x][y] = Blocks.STONE
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if x + dx < 0 or x + dx >= len(self.__blocks) or y + dy < 0 or y + dy >= len(self.__blocks):
                    continue
                self.__update_cell(x + dx, y + dy)

    def get(self, x: int, y: int) -> Blocks | None:
        """Можно узнать, какой блок расположен по указанным координатам (нумерация с 0)"""
        return self.__blocks[x][y]
