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

    def __repr__(self) -> str:
        return f"Rod({self.start_node.name}→{self.end_node.name}, L={self.length():.3f})"
