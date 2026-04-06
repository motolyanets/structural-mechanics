from core.mechanics.node import Node


class Support:
    """Создаем класс для опоры"""

    def __init__(self, node: Node, number_of_reactions: int, rotation: int):
        self.node = node

        if number_of_reactions in [1, 2, 3]:
            self.number_of_reactions = number_of_reactions
        else:
            raise Exception("Количество реакций в опоре должно быть 1, 2 или 3")

        if rotation in [0, 90, 180, 270]:
            self.rotation = int(rotation)
        else:
            raise Exception("Направление главной реакции должно быть 0, 90, 180 или 270")
