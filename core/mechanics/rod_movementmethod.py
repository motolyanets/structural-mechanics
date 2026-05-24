import math
from typing import List

from core.mechanics.load import Twist, Displacement, DistributedForce, Force, Momentum
from core.mechanics.node import Node
from services.services import distance_between_two_points, round_up


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

    def calculate_diagram_m_movement(self):
        length = self.length()
        linear_stiffness = self.linear_stiffness
        report = ''
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
                        Q = -sign * 3 * linear_stiffness / length
                    else:
                        raise Exception(f'Поворот не может быть приложен к шарниру ({self}.....{load})')
                    text = f'M{self.name} = 3 · i  = {abs(round_up(m_start, 3))}\n'
                    report += text
                    self.diagram_M = [m_start, m_end]
                    self.diagram_Q = [Q, Q]
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
                    Q = sign * 3 * linear_stiffness / length ** 2
                    self.diagram_M = [m_start, m_end]
                    self.diagram_Q = [Q, Q]
                    text = f'M{self.name} = 3 · i / l = {abs(round_up(m_start, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1
                    m_start = sign * load.value * length ** 2 / 8
                    m_midl = -sign * load.value * length ** 2 / 16
                    m_end = 0
                    Q_start = sign * 5 * load.value * length / 8
                    Q_end = -sign * 3 * load.value * length / 8
                    self.diagram_M = [m_start, m_midl, m_end]
                    self.diagram_Q = [Q_start, Q_end]
                    text = f'M{self.name} = q · l² / 8 = {abs(round_up(m_start,3))}\n'
                    text += f'M{self.name} = q · l² / 16 = {abs(round_up(m_midl, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y), point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = sign * load.value * b * (length ** 2 - b ** 2) / (2 * length ** 2)
                    m_p = (-sign * load.value * b / 2) * ((2 * a / length) - (b / length ** 3) * (length ** 2 - b ** 2))
                    m_end = 0
                    Q_start = sign * load.value * b * (3 * length ** 2 - b ** 2) / (2 * length ** 3)
                    Q_end = -sign * load.value * a * (3 * length - a) / (2 * length ** 3)
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_p, m_end]
                    text = f'M{self.name} = P · b · (l² - b²) / (2 · l²) = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = P · b / 2 · ((2 · a / l) - (b / l³) · (l² - b²)) = {abs(round_up(m_p, 3))}\n'
                    report += text
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

                    if rotation in [0, 270]:
                        sign = 1
                    elif rotation in [90, 180]:
                        sign = -1

                    m_start = sign * 1.5 * force_1.value * a * (1 - a / length)
                    m_1 = -sign * force_1.value * a * (1.5 * (a / length) * (2 - a / length) - 0.5)
                    m_2 = -sign * force_1.value * a * (1 - 1.5 * (a / length) * (1 - a / length))
                    m_end = 0
                    Q_start = sign * force_1.value * (1 + 1.5 * (a / length) * (1 - a / length))
                    Q_end = -sign * force_1.value * (1 - 1.5 * (a / length) * (1 - a / length))
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = 1.5 · P · a · (1 - a / l) = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = P · a · (1.5 · a / l · (2 - a / l) - 0.5) = {abs(round_up(m_1, 3))}\n'
                    text += f'M{self.name} = P · a · (1 - 1.5 · (a / l) · (1 - a / l)) = {abs(round_up(m_2, 3))}\n'
                    report += text
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
                    Q = -sign * load.value * (length ** 2 - b ** 2) / (2 * length ** 3)
                    self.diagram_Q = [Q, Q]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = m · (l² - 3 · b²) / (2 · l²) = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = (m · a / l) - (b / l) · m_start = {abs(round_up(m_1, 3))}\n'
                    text += f'M{self.name} = (m · b / l) + (b / l) · m_start = {abs(round_up(m_2, 3))}\n'
                    report += text

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
                        Q = -sign * 3 * linear_stiffness / length

                    else:
                        raise Exception(f'Поворот не может быть приложен к шарниру ({self}.....{load})')
                    self.diagram_M = [m_start, m_end]
                    self.diagram_Q = [Q, Q]
                    text = f'M{self.name} = 3 · i = {abs(round_up(m_end, 3))}\n'
                    report += text
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
                    Q = -sign * 3 * linear_stiffness / length ** 2
                    self.diagram_M = [m_start, m_end]
                    self.diagram_Q = [Q, Q]
                    text = f'M{self.name} = 3 · i / l = {abs(round_up(m_end, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1
                    m_start = 0
                    m_midl = -sign * load.value * length ** 2 / 16
                    m_end = sign * load.value * length ** 2 / 8
                    Q_start = -sign * 3 * load.value * length / 8
                    Q_end = sign * 5 * load.value * length / 8
                    self.diagram_M = [m_start, m_midl, m_end]
                    self.diagram_Q = [Q_start, Q_end]
                    text = f'M{self.name} = q · l² / 8 = {abs(round_up(m_end,3))}\n'
                    text += f'M{self.name} = q · l² / 16 = {abs(round_up(m_midl, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
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
                    Q_start = sign * load.value * a * (3 * length - a) / (2 * length ** 3)
                    Q_end = -sign * load.value * b * (3 * length ** 2 - b ** 2) / (2 * length ** 3)
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_p, m_end]
                    text = f'M{self.name} = P · b · (l² - b²) / (2 · l²) = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = P · b / 2 · ((2 · a / l) - (b / l³) · (l² - b²)) = {abs(round_up(m_p, 3))}\n'
                    report += text
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

                    if rotation in [0, 270]:
                        sign = 1
                    elif rotation in [90, 180]:
                        sign = -1

                    m_start = 0
                    m_1 = -sign * force_1.value * a * (1 - 1.5 * (a / length) * (1 - a / length))
                    m_2 = -sign * force_1.value * a * (1.5 * (a / length) * (2 - a / length) - 0.5)
                    m_end = sign * 1.5 * force_1.value * a * (1 - a / length)
                    Q_start = sign * force_1.value * (1 - 1.5 * (a / length) * (1 - a / length))
                    Q_end = -sign * force_1.value * (1 + 1.5 * (a / length) * (1 - a / length))
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = 1.5 · P · a · (1 - a / l) = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = P · a · (1.5 · a / l · (2 - a / l) - 0.5) = {abs(round_up(m_2, 3))}\n'
                    text += f'M{self.name} = P · a · (1 - 1.5 · (a / l) · (1 - a / l)) = {abs(round_up(m_1, 3))}\n'
                    report += text
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
                    Q = -sign * load.value * (length ** 2 - b ** 2) / (2 * length ** 3)
                    self.diagram_Q = [Q, Q]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = m · (l² - 3 · b²) / (2 · l²) = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = (m · a / l) - (b / l) · m_start = {abs(round_up(m_2, 3))}\n'
                    text += f'M{self.name} = (m · b / l) + (b / l) · m_start = {abs(round_up(m_1, 3))}\n'
                    report += text

            elif self.start_support_type == 'Жесткий' and self.end_support_type == 'Жесткий':
                if len(self.loads) == 1 and isinstance(self.loads[0], Twist):
                    load = self.loads[0]
                    if load.rotation and load.node == self.start_node:
                        sign = 1
                    elif load.rotation and load.node == self.end_node:
                        sign = -1
                    elif not load.rotation and load.node == self.end_node:
                        sign = 1
                    elif not load.rotation and load.node == self.start_node:
                        sign = -1

                    if load.node == self.start_node:
                        m_start = -sign * 4 * linear_stiffness
                        m_end = sign * 2 * linear_stiffness
                        Q = -sign * 6 * linear_stiffness / length
                    elif load.node == self.end_node:
                        m_start = sign * 2 * linear_stiffness
                        m_end = -sign * 4 * linear_stiffness
                        Q = sign * 6 * linear_stiffness / length
                    else:
                        raise Exception(f'Поворот может быть приложен только в заделке')
                    self.diagram_M = [m_start, m_end]
                    self.diagram_Q = [Q, Q]
                    text = f'M{self.name} = 2 · i = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = 4 · i = {abs(round_up(m_end, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Displacement):
                    load = self.loads[0]
                    if load.rotation in [90, 180] and load.node == self.start_node:
                        sign = 1
                    elif load.rotation in [90, 180] and load.node == self.end_node:
                        sign = -1
                    elif load.rotation in [0, 270] and load.node == self.end_node:
                        sign = 1
                    elif load.rotation in [0, 270] and load.node == self.start_node:
                        sign = -1

                    m_start = sign * 6 * linear_stiffness / length
                    m_end = -sign * 6 * linear_stiffness / length
                    Q = sign * 12 * linear_stiffness / length ** 2
                    self.diagram_Q = [Q, -Q]
                    self.diagram_M = [m_start, m_end]
                    text = f'M{self.name} = 6 · i / l = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = 6 · i / l = {abs(round_up(m_end, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1
                    m_start = sign * load.value * length ** 2 / 12
                    m_midl = -sign * load.value * length ** 2 / 24
                    m_end = sign * load.value * length ** 2 / 12
                    Q = -sign * load.value * length / 2
                    self.diagram_Q = [Q, -Q]
                    self.diagram_M = [m_start, m_midl, m_end]
                    text = f'M{self.name} = q · l² / 12 = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = q · l² / 24 = {abs(round_up(m_midl, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = sign * load.value * a * b ** 2 / (length ** 2)
                    m_p = -sign * (load.value * a * b / length) * (1 - (a / length) - (b - a) * b / (length ** 2))
                    m_end = sign * load.value * b * a ** 2 / (length ** 2)
                    Q_start = sign * load.value * (b ** 2) * (1 + 2 * a / length) / length ** 2
                    Q_end = -sign * load.value * (a ** 2) * (1 + 2 * b / length) / length ** 2
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_p, m_end]
                    text = f'M{self.name} = P · a · b² / l² = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = P · a · (b / l) · (1 - (a / l) - (b - a) · b / l² = {abs(round_up(m_p, 3))}\n'
                    text += f'M{self.name} = P · b · a² / l² = {abs(round_up(m_end, 3))}\n'
                    report += text
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

                    if rotation in [0, 270]:
                        sign = 1
                    elif rotation in [90, 180]:
                        sign = -1

                    m_start = sign * force_1.value * a *(1 - a / length)
                    m_1 = -sign * force_1.value * a ** 2 / length
                    m_2 = m_1
                    m_end = m_start
                    Q = -sign * force_1.value
                    self.diagram_Q = [Q, -Q]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = P · a · (1 - (a / l)) = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = P · a² / l = {abs(round_up(m_1, 3))}\n'
                    report += text
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

                    m_start = -sign * load.value * b * (3 * a - length) / (length ** 2)
                    m_1 = sign * ((load.value * b / (length ** 3)) + (length ** 2 - 3 * a * length + 6 * (a ** 2)))
                    m_2 = -sign * ((load.value * a / (length ** 3)) + (length ** 2 - 3 * b * length + 6 * (b ** 2)))
                    m_end = sign * load.value * a * (3 * b - length) / (length ** 2)
                    Q = -sign * 6 * a * b * load.value / length ** 3
                    self.diagram_Q = [Q, Q]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = m · b · (3 · a - l) / l² = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = m · a · (3 · b - l) / l² = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = m · b · (l² - 3 · a · l + 6 · a²) / l³ = {abs(round_up(m_1, 3))}\n'
                    text += f'M{self.name} = m · a · (l² - 3 · b · l + 6 · b²) / l³ = {abs(round_up(m_2, 3))}\n'
                    report += text

            elif self.start_support_type == 'Жесткий' and self.end_support_type == 'Нет':
                if len(self.loads) == 1 and isinstance(self.loads[0], Twist):
                    load = self.loads[0]
                    if load.node == self.start_node:
                        m_start = 0
                        m_end = 0
                    else:
                        raise Exception(f'Поворот может быть приложен только в заделке')
                    self.diagram_Q = [0, 0]
                    self.diagram_M = [m_start, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Displacement):
                    self.diagram_M = [0, 0]
                    self.diagram_Q = [0, 0]
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1
                    m_start = sign * load.value * length ** 2 / 2
                    m_midl = sign * load.value * length ** 2 / 8
                    m_end = 0
                    Q_start = sign * load.value * length
                    Q_end = 0
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_midl, m_end]
                    text = f'M{self.name} = q · l² / 2 = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = q · l² / 8 = {abs(round_up(m_midl, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = sign * load.value * a
                    m_p = 0
                    m_end = 0
                    Q_start = sign * load.value
                    Q_end = 0
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_p, m_end]
                    text = f'M{self.name} = P · a = {abs(round_up(m_start, 3))}\n'
                    report += text
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

                    if rotation in [0, 270]:
                        sign = 1
                    elif rotation in [90, 180]:
                        sign = -1

                    m_start = sign * force_1.value * a + force_1.value * (length - a)
                    m_1 = sign * force_1.value * (length - 2 * a)
                    m_2 = 0
                    m_end = 0
                    Q_start = sign * 2 * force_1.value
                    Q_end = 0
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = P · a + P · (l - a) = {abs(round_up(m_start, 3))}\n'
                    text += f'M{self.name} = P · (l - 2 · a) = {abs(round_up(m_1, 3))}\n'
                    report += text
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

                    m_start = sign * load.value
                    m_1 = sign * load.value
                    m_2 = 0
                    m_end = 0
                    self.diagram_Q = [0, 0]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = m = {abs(round_up(m_start, 3))}\n'
                    report += text

            elif self.start_support_type == 'Нет' and self.end_support_type == 'Жесткий':
                if len(self.loads) == 1 and isinstance(self.loads[0], Twist):
                    load = self.loads[0]
                    if load.node == self.end_node:
                        m_start = 0
                        m_end = 0
                    else:
                        raise Exception(f'Поворот может быть приложен только в заделке')
                    self.diagram_Q = [0, 0]
                    self.diagram_M = [m_start, m_end]
                elif len(self.loads) == 1 and isinstance(self.loads[0], Displacement):
                    self.diagram_M = [0, 0]
                    self.diagram_Q = [0, 0]
                elif len(self.loads) == 1 and isinstance(self.loads[0], DistributedForce):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1
                    m_start = 0
                    m_midl = sign * load.value * length ** 2 / 8
                    m_end = sign * load.value * length ** 2 / 2
                    Q_start = 0
                    Q_end = -sign * load.value * length
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_midl, m_end]
                    text = f'M{self.name} = q · l² / 2 = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = q · l² / 8 = {abs(round_up(m_start, 3))}\n'
                    report += text
                elif len(self.loads) == 1 and isinstance(self.loads[0], Force):
                    load = self.loads[0]
                    if load.rotation in [0, 270]:
                        sign = 1
                    elif load.rotation in [90, 180]:
                        sign = -1

                    a = distance_between_two_points(point_1=(self.start_node.x, self.start_node.y),
                                                    point_2=(load.node.x, load.node.y))
                    if a < length:
                        b = length - a
                    else:
                        raise Exception('Расстояние от начала стержня не может быть больше длины стержня')

                    m_start = 0
                    m_p = 0
                    m_end = sign * load.value * a
                    Q_start = 0
                    Q_end = -sign * load.value
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_p, m_end]
                    text = f'M{self.name} = P · a = {abs(round_up(m_end, 3))}\n'
                    report += text
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

                    if rotation in [0, 270]:
                        sign = 1
                    elif rotation in [90, 180]:
                        sign = -1

                    m_start = 0
                    m_1 = 0
                    m_2 = sign * force_1.value * (length - 2 * a)
                    m_end = sign * force_1.value * a + force_1.value * (length - a)
                    Q_start = 0
                    Q_end = -sign * 2 * force_1.value
                    self.diagram_Q = [Q_start, Q_end]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = P · a + P · (l - a) = {abs(round_up(m_end, 3))}\n'
                    text += f'M{self.name} = P · (l - 2 · a) = {abs(round_up(m_2, 3))}\n'
                    report += text
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

                    m_start = 0
                    m_1 = 0
                    m_2 = -sign * load.value
                    m_end = -sign * load.value
                    self.diagram_Q = [0, 0]
                    self.diagram_M = [m_start, m_1, m_2, m_end]
                    text = f'M{self.name} = m = {abs(round_up(m_start, 3))}\n'
                    report += text
        #     Дописать случаи для скользящей опоры


        else:
            self.diagram_M = [0, 0]
        if self.diagram_M:
            print(f'{self}....{self.diagram_M}')
            return report

    def __repr__(self) -> str:
        return f"RodForMovementMethod----{self.start_node.name}→{self.end_node.name}"