import math
from typing import List

from core.mechanics.load import Twist, Displacement
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
        self.linear_stiffness = stiffness / self.length()

        if start_support_type and end_support_type not in ['Жесткий', 'Шарнирный', 'Скользящий', 'Нет']:
            raise Exception(f'Задан невевный тип зпкрепления стержня {self.name}')

    def dx(self) -> float:
        dx = self.end_node.x - self.start_node.x
        return math.fabs(dx)

    def dy(self) -> float:
        dy = self.end_node.y - self.start_node.y
        return math.fabs(dy)

    def length(self) -> float:
        dx = self.dx()
        dy = self.dy()
        length = math.sqrt(dx ** 2 + dy ** 2)
        return length

    def calculate_diagram_m(self):
        length = self.length()
        linear_stiffness = self.linear_stiffness
        if self.loads:
            if self.start_support_type == 'Жесткий' and self.end_support_type == 'Шарнирный':
                if len(self.loads) == 1 and isinstance(self.loads[0], Twist):
                    load = self.loads[0]
                    if load.rotation:
                        sign = 1
                    else:
                        sign = -1
                    if load.node == self.start_node:
                        m_start = -3 * linear_stiffness * sign
                        m_end = 0
                    else:
                        raise Exception(f'Поворот не может быть приложен к шарниру ({self}.....{load})')
                    self.diagram_M = [m_start, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Displacement):
                    load = self.loads[0]
                    if load.rotation in [0, 90] and load.node == self.start_node:
                        sign = 1
                    elif load.rotation in [0, 90] and load.node == self.end_node:
                        sign = -1
                    elif load.rotation in [180, 270] and load.node == self.end_node:
                        sign = 1
                    elif load.rotation in [180, 270] and load.node == self.start_node:
                        sign = -1
                    m_start = sign * 3 * linear_stiffness / length
                    m_end = 0
                    self.diagram_M = [m_start, m_end]

            elif self.start_support_type == 'Шарнирный' and self.end_support_type == 'Жесткий':
                if len(self.loads) == 1 and isinstance(self.loads[0], Twist):
                    load = self.loads[0]
                    if load.rotation:
                        sign = 1
                    else:
                        sign = -1
                    if load.node == self.end_node:
                        m_start = 0
                        m_end = 3 * linear_stiffness * sign
                    else:
                        raise Exception(f'Поворот не может быть приложен к шарниру ({self}.....{load})')
                    self.diagram_M = [m_start, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Displacement):
                    load = self.loads[0]
                    if load.rotation in [0, 90] and load.node == self.start_node:
                        sign = -1
                    elif load.rotation in [0, 90] and load.node == self.end_node:
                        sign = 1
                    elif load.rotation in [180, 270] and load.node == self.end_node:
                        sign = -1
                    elif load.rotation in [180, 270] and load.node == self.start_node:
                        sign = 1
                    m_start = 0
                    m_end = sign * 3 * linear_stiffness / length
                    self.diagram_M = [m_start, m_end]
        else:
            self.diagram_M = [0, 0]
        if self.diagram_M:
            print(f'{self}....{self.diagram_M}')

    def __repr__(self) -> str:
        return f"RodForMovementMethod----{self.start_node.name}→{self.end_node.name}"