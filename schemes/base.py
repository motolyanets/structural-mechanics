from typing import List, Tuple
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum
from core.mechanics.support import Support
from core.mechanics.solver import SolvableFrame, SimpleFrame, Tightening, ThreeHingedFrame


class Frame:
    def __init__(self, nodes: List[Node], rods: List[Rod], supports: List[Support],
                 loads: list, splitted_frames_order: Tuple[Tuple[str, ...], ...] | None = None):
        self.nodes = nodes
        self.rods = rods
        self.supports = supports
        self.loads = loads
        self.splitted_frames_order = splitted_frames_order

    def reactions(self):
        reactions = []
        for support in self.supports:
            if support.number_of_reactions == 1:
                reactions.append(Force(name=f'R{support.node.name}', node=support.node, rotation=support.rotation))
            elif support.number_of_reactions == 2:
                reactions.append(Force(name=f'X{support.node.name}', node=support.node, rotation=0))
                reactions.append(Force(name=f'Y{support.node.name}', node=support.node, rotation=90))
            else:
                reactions.append(Force(name=f'X{support.node.name}', node=support.node, rotation=0))
                reactions.append(Force(name=f'Y{support.node.name}', node=support.node, rotation=90))
                reactions.append(Momentum(name=f'M{support.node.name}', node=support.node, rotation=True))
        return reactions

    def split_frame(self):
        print(50 * '-')
        print('Разделяем раму на составляющие')
        parts_of_frame = []
        finded_reactions = []

        for small_frame in self.splitted_frames_order:
            new_nodes = []
            for node in self.nodes:
                if node.name in small_frame:
                    new_nodes.append(node)

            new_supports = []
            for support in self.supports:
                if support.node in new_nodes:
                    new_supports.append(support)

            new_rods = []
            for rod in self.rods:
                if rod.start_node in new_nodes and rod.end_node in new_nodes:
                    new_rods.append(rod)
                    if rod.is_start_hinge:
                        sup = Support(node=rod.start_node, number_of_reactions=2, rotation=90)
                        rod.is_start_hinge = False
                        new_supports.append(sup)
                    elif rod.is_end_hinge:
                        sup = Support(node=rod.end_node, number_of_reactions=2, rotation=90)
                        rod.is_end_hinge = False
                        new_supports.append(sup)

            new_loads = []
            for load in self.loads:
                if isinstance(load, (Force, Momentum)):
                    if load.node in new_nodes:
                        new_loads.append(load)
                else:
                    if load.rod in new_rods:
                        new_loads.append(load)

            finded_reactions = finded_reactions.copy()

            part_of_frame = SolvableFrame(
                nodes=new_nodes, rods=new_rods,
                supports=new_supports, loads=new_loads
            )

            part_of_frame = part_of_frame.classify_part()
            parts_of_frame.append(part_of_frame)

        print('Рама разделена на составляющие')
        print(50 * '-')
        return parts_of_frame

