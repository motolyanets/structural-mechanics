from typing import List, Tuple

from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.support import Support
from services.services import round_up, normalize_equation


class Frame:
    def __init__(self, nodes: List[Node], rods: List[Rod], supports: List[Support],
                 loads: list, finded_reactions=None, base_point=None):
        self.nodes = nodes
        self.rods = rods
        self.supports = supports
        self.loads = loads
        self.finded_reactions = finded_reactions if finded_reactions is not None else []
        self.base_point = base_point

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
            print(diagram)
            m1, m2 = diagram[0], diagram[1]
            if abs(m1) > max_value:
                max_value = abs(m1)
            if abs(m2) > max_value:
                max_value = abs(m2)
        print(max_value)
        return max_value
