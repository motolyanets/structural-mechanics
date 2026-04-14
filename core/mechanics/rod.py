import math
from typing import List, Optional
from core.mechanics.node import Node
from services.services import round_up


class Rod:
    def __init__(
            self,
            start_node: Node,
            end_node: Node,
            qx: int | None = None,
            qy: int | None = None,
            is_start_hinge: bool = False,
            is_end_hinge: bool = False,
            diagram_M1: List | None = None,
            diagram_M2: List | None = None,
            diagram_M3: List | None = None,
            diagram_Ms: List | None = None,
            diagram_Mp: List | None = None,
            diagram_Mok: List | None = None,
            diagram_Mk: List | None = None,
            diagram_Q: List | None = None,
            stiffness: float = 1,
    ):
        self.start_node = start_node
        self.end_node = end_node
        self.qx = qx
        self.qy = qy
        self.is_start_hinge = is_start_hinge
        self.is_end_hinge = is_end_hinge
        self.diagram_M1 = diagram_M1
        self.diagram_M2 = diagram_M2
        self.diagram_M3 = diagram_M3
        self.diagram_Ms = diagram_Ms
        self.diagram_Mp = diagram_Mp
        self.diagram_Mok = diagram_Mok
        self.diagram_Mk = diagram_Mk
        self.diagram_Q = diagram_Q
        self.stiffness = stiffness

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
        return round_up(length)

    def multiply_diagrams_Simpson(self, diagram_1_name, diagram_2_name):
        diagram_1 = self.__getattribute__(f'diagram_{diagram_1_name}')
        diagram_2 = self.__getattribute__(f'diagram_{diagram_2_name}')

        length = self.length()
        stiffness = self.stiffness

        multiplied_diagram = []

        d1_start = diagram_1[0]
        d1_center = round_up((diagram_1[0] + diagram_1[1]) / 2, 3)
        d1_end = diagram_1[1]
        d2_start = diagram_2[0]
        d2_center = round_up((diagram_2[0] + diagram_2[1]) / 2, 3)
        d2_end = diagram_2[1]

        if len(diagram_1) == len(diagram_2) == 2:
            result = (length / (6 * stiffness)) * (d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end)
            if result:
                text = (
                    f'({length} / (6 * {stiffness}EI)) * ({d1_start} * {d2_start} + 4 * {round_up(d1_center)} * {round_up(d2_center)} + '
                    f'{d1_end} * {d2_end})')
                multiplied_diagram.append(text)
                multiplied_diagram.append(round_up(result))
        else:
            result = (length / (6 * stiffness)) * (
                        d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end + 4 * d1_center * diagram_2[
                    2] * length ** 2 / 8)
            if result:
                text = (
                    f'({length} / (6 * {stiffness}EI)) * ({d1_start} * {d2_start} + 4 * {round_up(d1_center)} * {round_up(d2_center)} + '
                    f'{d1_end} * {d2_end} + 4 * {d1_center} * {diagram_2[2]} * {length}^2 / 8)')
                multiplied_diagram.append(text)
                multiplied_diagram.append(round_up(result))

        return multiplied_diagram

    def __repr__(self) -> str:
        return f"Rod({self.start_node.name}→{self.end_node.name}, L={self.length():.3f})"
