from typing import List, Tuple

from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.support import Support
from services.services import round_up, normalize_equation


class Frame:
    def __init__(self, nodes: List[Node], rods: List[Rod], supports: List[Support],
                 loads: list, finded_reactions=None, base_point=None, calkulate_diagram_rods_order: List[List[Rod]]=None):
        self.nodes = nodes
        self.rods = rods
        self.supports = supports
        self.loads = loads
        self.finded_reactions = finded_reactions if finded_reactions is not None else []
        self.base_point = base_point
        self.calkulate_diagram_rods_order = calkulate_diagram_rods_order

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

    def sum_momentum_about_node(self, node: Node):
        all_loads = self.loads + self.finded_reactions

        point = (node.x, node.y)
        moment = 0
        equation = ''
        for load in all_loads:
            if isinstance(load, Force):
                text, moment_of_load = load.get_moment_about(point=point)
                moment += moment_of_load
                equation += f'+ {text} '
            elif isinstance(load, Momentum):
                if load.rotation:
                    moment += load.value
                    equation += f'+{load.name} '
                else:
                    moment -= load.value
                    equation += f'-{load.name} '
            if isinstance(load, DistributedForce):
                text, moment_of_load = load.get_moment_about(point=point)
                moment += moment_of_load
                equation += f'+ {text} '

        moment = round_up(moment, 3)
        equation = f'∑M({node.name}): ' + normalize_equation(equation) + ' = 0'
        return moment, equation

    def sum_force_projections(self, axis: str):
        sum_force_expression_names = ''
        sum_force_expression_values = ''
        sum_of_projections = 0

        all_loads = self.loads + self.finded_reactions
        loads_taken_into_account = []
        for load in all_loads:
            if isinstance(load, (Force, DistributedForce)):
                if load.rotation in [0, 180] and axis in ['x', 'X']:
                    loads_taken_into_account.append(load)
                elif load.rotation in [90, 270] and axis in ['y', 'Y']:
                    loads_taken_into_account.append(load)

        for load in loads_taken_into_account:
            projection, expression = load.get_projection_on_axis(axis_name=axis)
            sum_of_projections += projection
            sum_force_expression_names += expression
            if projection >= 0:
                sum_force_expression_values += f'+ {projection}'
            else:
                sum_force_expression_values += f' {projection} '
        sum_of_projections = round_up(sum_of_projections, 4)
        return sum_of_projections, sum_force_expression_names, sum_force_expression_values

    def find_max_value_diagram_m(self, diagram_name: str) -> float:
        max_value = 0
        for rod in self.rods:
            diagram = rod.__getattribute__(f'diagram_M{diagram_name}')
            m1, m2 = diagram[0], diagram[1]
            if abs(m1) > max_value:
                max_value = abs(m1)
            if abs(m2) > max_value:
                max_value = abs(m2)
        return max_value

    def is_that_frame_solved(self):
        if not len(self.reactions()) == len(self.finded_reactions):
            raise Exception('Найдены не все опорные реакции')

    def next_rod(self, previous_rod:Rod, node: Node) -> Rod:
        rods_with_node = []
        for rod in self.rods:
            if node is rod.start_node or node is rod.end_node:
                rods_with_node.append(rod)

        if len(rods_with_node) == 1:
            return None
        elif len(rods_with_node) == 2:
            for rod in rods_with_node:
                if rod is not previous_rod:
                    return rod
            return None
        else:
            return None

    def create_sections_for_diagrams(self):
        self.is_that_frame_solved()

        nodes_with_1_rod = []
        nodes_with_3_or_more_rodes = []
        sections = []

        for node in self.nodes:
            i = 0
            for rod in self.rods:
                if node is rod.start_node or node is rod.end_node:
                    i += 1
            if i == 1:
                nodes_with_1_rod.append(node)
            if i > 2:
                nodes_with_3_or_more_rodes.append(node)

        all_loads = self.loads + self.finded_reactions
        number_of_section = 1

        print(all_loads)

        # Находим узел с одним стержнем
        for node in nodes_with_1_rod:
            using_loads = []
            load_on_current_rod = None

            # Находим первый стержень в цепочке и идем по цепочке пока не встретим узел с 3 и более стержнями
            for rod in self.rods:
                if node is rod.start_node or node is rod.end_node:
                    current_rod = rod
                    break
            amount_of_sections = 2
            for load in all_loads:
                # Добавляем нагрузки, действующие в текущем узле
                if isinstance(load, (Force, Momentum)):
                    if load.node.name == node.name and load not in using_loads:
                        using_loads.append(load)
                # Добавляем распределенную нагрузку, действующую на текущий стержень
                elif isinstance(load, DistributedForce):
                    if load.rod == current_rod:
                        load_on_current_rod = load

            sections_on_rod, number_of_section, next_node = current_rod.make_sections_on_rod(
                first_node=node,
                number_of_section=number_of_section,
                loads=using_loads,
                load_on_current_rod=load_on_current_rod,
            )
            sections += sections_on_rod
            if load_on_current_rod:
                using_loads.append(load_on_current_rod)
                load_on_current_rod = None

            while True:
                load_on_current_rod = None
                current_rod = self.next_rod(previous_rod=current_rod, node=next_node)
                for load in all_loads:
                    # Добавляем нагрузки, действующие в текущем узле
                    if isinstance(load, (Force, Momentum)):
                        if load.node.name == next_node.name and load not in using_loads:
                            using_loads.append(load)
                    # Добавляем распределенную нагрузку, действующую на текущий стержень
                    elif isinstance(load, DistributedForce):
                        if load.rod == current_rod:
                            load_on_current_rod = load


                sections_on_rod, number_of_section, next_node = current_rod.make_sections_on_rod(
                    first_node=next_node,
                    number_of_section=number_of_section,
                    loads=using_loads,
                    load_on_current_rod=load_on_current_rod,
                )
                sections += sections_on_rod
                if load_on_current_rod:
                    using_loads.append(load_on_current_rod)

                if current_rod.start_node in nodes_with_3_or_more_rodes or current_rod.end_node in nodes_with_3_or_more_rodes:
                    break
