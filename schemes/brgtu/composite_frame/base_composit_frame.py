from copy import deepcopy
from typing import List, Tuple

from core.mechanics.frame import Frame
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum
from core.mechanics.support import Support
from core.mechanics.solver import SolvableFrame, SimpleFrame, Tightening, ThreeHingedFrame


class CompositeFrame(Frame):
    def __init__(self, nodes: List[Node], rods: List[Rod], supports: List[Support],
                 loads: list, splitted_frames_order: Tuple[Tuple[str, ...], ...] | None = None, name: str | None = None):
        super().__init__(nodes=nodes, rods=rods, supports=supports, loads=loads, name=name)
        self.splitted_frames_order = splitted_frames_order

    def split_frame(self):
        print(50 * '-')
        print('Разделяем раму на составляющие')
        parts_of_frame = []
        finded_reactions = []

        for small_frame in self.splitted_frames_order:
            is_adding_new_support_in_hinge = False
            for node_name in small_frame:
                if len(node_name) > 1:
                    new_name_of_hinge = node_name
                    is_adding_new_support_in_hinge = True

            new_nodes = []
            for node in self.nodes:
                for n_name in small_frame:
                    if node.name == n_name[0]:
                        new_node = deepcopy(node)
                        new_node.name = n_name
                        new_nodes.append(new_node)

            new_supports = []
            for support in self.supports:
                if support.node.name in small_frame:
                    new_supports.append(deepcopy(support))

            new_rods = []
            for rod in self.rods:
                if rod.start_node.name[0] in [x[0] for x in small_frame] and rod.end_node.name in [x[0] for x in small_frame]:
                    new_rod = deepcopy(rod)
                    if is_adding_new_support_in_hinge:
                        if new_rod.start_node.name == new_name_of_hinge[0]:
                            new_rod.start_node.name = new_name_of_hinge
                        elif new_rod.end_node.name == new_name_of_hinge[0]:
                            new_rod.end_node.name = new_name_of_hinge
                        new_rod.name = f'{new_rod.start_node.name}{new_rod.end_node.name}'
                    new_rods.append(new_rod)
                    if new_rod.is_start_hinge:
                        sup = Support(node=new_rod.start_node, number_of_reactions=2, rotation=90)
                        new_rod.is_start_hinge = False
                        new_supports.append(sup)
                    elif new_rod.is_end_hinge:
                        sup = Support(node=new_rod.end_node, number_of_reactions=2, rotation=90)
                        new_rod.is_end_hinge = False
                        new_supports.append(sup)

            for new_node in new_nodes:
                if new_node.is_hinge:
                    amount_of_rods_with_node = 0
                    for new_rod in new_rods:
                        if new_node.name in [new_rod.start_node.name, new_rod.end_node.name]:
                            amount_of_rods_with_node += 1
                    if amount_of_rods_with_node == 1:
                        if is_adding_new_support_in_hinge:
                            sup = Support(node=new_node, number_of_reactions=2, rotation=90)
                            new_supports.append(sup)
                    new_node.is_hinge = False

            new_loads = []
            for load in self.loads:
                new_load = deepcopy(load)
                if isinstance(new_load, (Force, Momentum)):
                    if new_load.node.name == new_name_of_hinge[0]:
                        new_load.node.name = new_name_of_hinge
                    if new_load.node.name in small_frame:
                        new_loads.append(new_load)
                else:
                    if new_load.rod.name.count(new_name_of_hinge[0]) == 1:
                        if new_load.rod.start_node.name == new_name_of_hinge[0]:
                            new_load.rod.start_node.name = new_name_of_hinge
                        elif new_load.rod.end_node.name == new_name_of_hinge[0]:
                            new_load.rod.end_node.name = new_name_of_hinge
                        new_load.rod.name = f'{new_load.rod.start_node.name}{new_load.rod.end_node.name}'
                    if new_load.rod.name in [x.name for x in new_rods]:
                        new_loads.append(new_load)

            finded_reactions = finded_reactions.copy()

            part_of_frame = SolvableFrame(
                nodes=new_nodes, rods=new_rods,
                supports=new_supports, loads=new_loads
            )
            part_of_frame.finded_reactions = finded_reactions
            part_of_frame = part_of_frame.classify_part()
            parts_of_frame.append(part_of_frame)

        print('Рама разделена на составляющие')
        print(50 * '-')
        return parts_of_frame

