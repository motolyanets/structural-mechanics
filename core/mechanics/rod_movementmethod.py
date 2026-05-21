from typing import List

from core.mechanics.node import Node


class RodForMovementMethod:
    """
    Стержень для метода перемещений
    """
    def __init__(self,
                 start_node: Node,
                 end_node: Node,
                 start_support_type: str,
                 end_support_type: str,
                 stiffness: float = 1,
                 loads: List | None = None,
                 diagram_M: List | None = None,
                 diagram_Q: List | None = None,
    ):
        self.start_node = start_node
        self.end_node = end_node
        self.start_support_type = start_support_type
        self.end_support_type = end_support_type
        self.stiffness = stiffness
        self.loads = loads
        self.diagram_M = diagram_M
        self.diagram_Q = diagram_Q
        self.name = f'{start_node.name}{end_node.name}'

        if start_support_type and end_support_type not in ['Жесткий', 'Шарнирный', 'Скользящий', 'Нет']:
            raise Exception(f'Задан невевный тип зпкрепления стержня {self.name}')



    def __repr__(self) -> str:
        return f"RodForMovementMethod----{self.start_node.name}→{self.end_node.name}"