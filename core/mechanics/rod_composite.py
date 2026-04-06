from typing import List

from core.mechanics.node import Node
from core.mechanics.rod import Rod


class RodForCompositeFrame(Rod):
    """
    Стержень для составной рамы
    """
    def __init__(self,
                 start_node: Node,
                 end_node: Node,
                 is_start_hinge: bool = False,
                 is_end_hinge: bool = False,
                 stiffness: float = 1,
                 diagram_M: List | None = None,
                 diagram_Q: List | None = None,
                 diagram_N: List | None = None,
    ):
        super().__init__(start_node, end_node, is_start_hinge, is_end_hinge, stiffness)
        self.diagram_M = diagram_M
        self.diagram_Q = diagram_Q
        self.diagram_N = diagram_N


    def __repr__(self) -> str:
        return f"RodForCompositeFrame----{self.start_node.name}→{self.end_node.name}"