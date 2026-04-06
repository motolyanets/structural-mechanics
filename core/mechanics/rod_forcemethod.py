from typing import List

from core.mechanics.node import Node
from core.mechanics.rod import Rod


class RodForForceMethod(Rod):
    """
    Стержень для составной рамы
    """
    def __init__(self,
                 start_node: Node,
                 end_node: Node,
                 is_start_hinge: bool = False,
                 is_end_hinge: bool = False,
                 stiffness: float = 1,
                 diagram_M1: List | None = None,
                 diagram_M2: List | None = None,
                 diagram_M3: List | None = None,
                 diagram_Ms: List | None = None,
                 diagram_Mp: List | None = None,
                 diagram_Mok: List | None = None,
                 diagram_Mk: List | None = None,
                 diagram_Q: List | None = None,
    ):
        super().__init__(start_node, end_node, is_start_hinge, is_end_hinge, stiffness)
        self.diagram_M1 = diagram_M1
        self.diagram_M2 = diagram_M2
        self.diagram_M3 = diagram_M3
        self.diagram_Ms = diagram_Ms
        self.diagram_Mp = diagram_Mp
        self.diagram_Mok = diagram_Mok
        self.diagram_Mk = diagram_Mk
        self.diagram_Q = diagram_Q


    def __repr__(self) -> str:
        return f"RodForForceMethod----{self.start_node.name}→{self.end_node.name}"