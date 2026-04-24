from typing import Tuple

from core.mechanics.node import Node


class Support:
    """Создаем класс для опоры"""

    def __init__(self, node: Node, number_of_reactions: int, rotation: int):
        self.node = node

        if number_of_reactions in [1, 2, 3]:
            self.number_of_reactions = number_of_reactions
        else:
            raise Exception("Количество реакций в опоре должно быть 1, 2 или 3")

        if number_of_reactions == 1:
            self.block_name = 'Подвижная опора'
        elif number_of_reactions == 2:
            self.block_name = 'Неподвижная опора'
        elif number_of_reactions == 3:
            self.block_name = 'Жесткая заделка'

        if rotation in [0, 90, 180, 270]:
            self.rotation = int(rotation)
        else:
            raise Exception("Направление главной реакции должно быть 0, 90, 180 или 270")

    def drow(self, insert_point: Tuple[float, float], msp):
        msp.add_blockref(self.block_name, insert=insert_point,
                         dxfattribs={
                             "layer": "Supports",
                             "rotation": self.rotation,
                         })
        return msp

