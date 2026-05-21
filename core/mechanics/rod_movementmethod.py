import math
from typing import List

from core.mechanics.load import Twist, Displacement, DistributedForce, Force, Momentum
from core.mechanics.node import Node
from services.services import distance_between_two_points


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
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 90]:
                        sign = 1
                    elif load.rotation in [180, 270]:
                        sign = -1
                    m_start = sign * load.value * length ** 2 / 8
                    m_midl = -sign * load.value * length ** 2 / 16
                    m_end = 0
                    self.diagram_M = [m_start, m_midl, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 90]:
                        sign = 1
                    elif load.rotation in [180, 270]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y), point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = sign * load.value * b * (length ** 2 - b ** 2) / (2 * length ** 2)
                    m_p = (-sign * load.value * b / 2) * ((2 * a / length) - (b / length ** 3) * (length ** 2 - b ** 2))
                    m_end = 0
                    self.diagram_M = [m_start, m_p, m_end]
                elif len(self.loads) == 2 and isinstance(self.loads[0], Force) and isinstance(self.loads[1], Force):
                    force_1 = self.loads[0]
                    force_2 = self.loads[1]
                    if force_1.rotation == force_2.rotation and force_1.value == force_2.value:
                        rotation = force_1.rotation
                    else:
                        raise Exception('Случай для нагружения стержня двумя разнонаправленными сосредоточенными усилиями не определен')
                    distance_to_start = 0
                    distance_to_end = 0
                    for force in self.loads:
                        ds = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y), point_2=(force.node.x, force.node.y))
                        de = distance_between_two_points(point_1=(self.end_node.x, self.end_node.y), point_2=(force.node.x, force.node.y))
                        if ds < de:
                            distance_to_start = ds
                        else:
                            distance_to_end = de

                    if distance_to_start == distance_to_end:
                        a = distance_to_start
                    else:
                        raise Exception('Если на стержень действуют две сосредоточенные силы, они должны быть равноудалены от краев стержня')

                    if rotation in [0, 90]:
                        sign = 1
                    elif rotation in [180, 270]:
                        sign = -1

                    m_start = sign * 1.5 * force_1.value * a * (1 - a / length)
                    m_1 = -sign * force_1.value * a * (1.5 * (a / length) * (2 - a / length) - 0.5)
                    m_2 = -sign * force_1.value * a * (1 - 1.5 * (a / length) * (1 - a / length))
                    m_end = 0
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Momentum):
                    load = self.loads[0]
                    if load.rotation:
                        sign = 1
                    else:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = -sign * load.value * (length ** 2 - 3 * b ** 2) / (2 * length ** 2)
                    m_1 = sign * ((load.value * a / length) - (b / length) * abs(m_start))
                    m_2 = -sign * ((load.value * b / length) + (b / length) * abs(m_start))
                    m_end = 0
                    self.diagram_M = [m_start, m_1, m_2, m_end]

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
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 90]:
                        sign = 1
                    elif load.rotation in [180, 270]:
                        sign = -1
                    m_start = 0
                    m_midl = -sign * load.value * length ** 2 / 16
                    m_end = sign * load.value * length ** 2 / 8
                    self.diagram_M = [m_start, m_midl, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 90]:
                        sign = 1
                    elif load.rotation in [180, 270]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.end_node.x, self.end_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = 0
                    m_p = (-sign * load.value * b / 2) * ((2 * a / length) - (b / length ** 3) * (length ** 2 - b ** 2))
                    m_end = sign * load.value * b * (length ** 2 - b ** 2) / (2 * length ** 2)
                    self.diagram_M = [m_start, m_p, m_end]
                elif len(self.loads) == 2 and isinstance(self.loads[0], Force) and isinstance(self.loads[1], Force):
                    force_1 = self.loads[0]
                    force_2 = self.loads[1]
                    if force_1.rotation == force_2.rotation and force_1.value == force_2.value:
                        rotation = force_1.rotation
                    else:
                        raise Exception(
                            'Случай для нагружения стержня двумя разнонаправленными сосредоточенными усилиями не определен')
                    distance_to_start = 0
                    distance_to_end = 0
                    for force in self.loads:
                        ds = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y),
                                                         point_2=(force.node.x, force.node.y))
                        de = distance_between_two_points(point_1=(self.end_node.x, self.end_node.y),
                                                         point_2=(force.node.x, force.node.y))
                        if ds < de:
                            distance_to_start = ds
                        else:
                            distance_to_end = de

                    if distance_to_start == distance_to_end:
                        a = distance_to_start
                    else:
                        raise Exception(
                            'Если на стержень действуют две сосредоточенные силы, они должны быть равноудалены от краев стержня')

                    if rotation in [0, 90]:
                        sign = 1
                    elif rotation in [180, 270]:
                        sign = -1

                    m_start = 0
                    m_1 = -sign * force_1.value * a * (1 - 1.5 * (a / length) * (1 - a / length))
                    m_2 = -sign * force_1.value * a * (1.5 * (a / length) * (2 - a / length) - 0.5)
                    m_end = sign * 1.5 * force_1.value * a * (1 - a / length)
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Momentum):
                    load = self.loads[0]
                    if load.rotation:
                        sign = -1
                    else:
                        sign = 1

                    a = distance_between_two_points(point_1=(self.end_node.x, self.end_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = 0
                    m_end = -sign * load.value * (length ** 2 - 3 * b ** 2) / (2 * length ** 2)
                    m_1 = -sign * ((load.value * b / length) + ((b / length) * abs(m_end)))
                    m_2 = sign * ((load.value * a / length) - ((b / length) * abs(m_end)))
                    self.diagram_M = [m_start, m_1, m_2, m_end]

        else:
            self.diagram_M = [0, 0]
        if self.diagram_M:
            print(f'{self}....{self.diagram_M}')

    def __repr__(self) -> str:
        return f"RodForMovementMethod----{self.start_node.name}→{self.end_node.name}"