from typing import List, Tuple

from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.rod_movementmethod import RodForMovementMethod
from core.mechanics.support import Support
from services.services import round_up, normalize_equation, are_collinear_nodes


class Frame:
    def __init__(self, nodes: List[Node], rods: List[Rod] | List[RodForMovementMethod], supports: List[Support],
                 loads: list, symmetry: Tuple[str, Node] | None = None, finded_reactions=None, base_point=None, calkulate_diagram_rods_order: List[List[Rod]]=None,
                 name: str | None = None):
        self.name = name
        self.nodes = nodes
        self.rods = rods
        self.supports = supports
        self.loads = loads
        self.symmetry = symmetry
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

    def get_symmetric_pare_of_rods(self):
        symmetric_pare_of_rods = []
        if not self.symmetry:
            raise Exception('Рама не симметрична')
        axis_of_symmetry, node_of_symmetry = self.symmetry
        other_axis = 'y' if axis_of_symmetry == 'x' else 'x'
        if axis_of_symmetry == 'x':
            for rod1 in self.rods:
                for rod2 in self.rods:
                    if rod1 != rod2:
                        if rod1.dx() == rod2.dx() == 0:
                            condition1 = rod1.start_node.y == rod2.start_node.y
                            condition2 = abs(node_of_symmetry.x - rod1.start_node.x) == abs(node_of_symmetry.x - rod2.start_node.x)
                            condition3 = abs(node_of_symmetry.x - rod1.end_node.x) == abs(node_of_symmetry.x - rod2.end_node.x)
                            condition4 = True
                        else:
                            condition1 = rod1.start_node.y == rod2.end_node.y
                            condition2 = rod1.end_node.y == rod2.start_node.y
                            condition3 = abs(node_of_symmetry.x - rod1.start_node.x) == abs(node_of_symmetry.x - rod2.end_node.x)
                            condition4 = abs(node_of_symmetry.x - rod1.end_node.x) == abs(node_of_symmetry.x - rod2.start_node.x)
                        if condition1 and condition2 and condition3 and condition4:
                            pare_of_rods = [rod1, rod2]
                            pare_of_rods.sort(key=lambda i: i.start_node.x)
                            pare_of_rods = tuple(pare_of_rods)
                            if pare_of_rods not in symmetric_pare_of_rods:
                                symmetric_pare_of_rods.append(tuple(pare_of_rods))

        if len(self.rods) != len(symmetric_pare_of_rods) * 2:
            raise Exception(f'Количество пар стержней не равно общему количеству стержней \n{symmetric_pare_of_rods}')
        return symmetric_pare_of_rods

    def geometrical_center(self) -> Tuple[float, float]:
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0
        for node in self.nodes:
            x_min = min(node.x, x_min)
            x_max = max(node.x, x_max)
            y_min = min(node.y, y_min)
            y_max = max(node.y, y_max)
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        return center_x, center_y

    def length(self) -> float:
        x_min = 0
        x_max = 0
        for node in self.nodes:
            x_min = min(node.x, x_min)
            x_max = max(node.x, x_max)
        length = x_max - x_min
        return length

    def sum_momentum_about_node(self, node: Node):
        all_loads = self.loads + self.finded_reactions

        point = (node.x, node.y)
        moment = 0
        equation = ''
        for load in all_loads:
            if isinstance(load, Force):
                text, moment_of_load = load.get_moment_about(point=point)
                moment += moment_of_load
                equation += text
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
                equation += text

        moment = round_up(moment, 3)
        print(equation)
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
                sum_force_expression_values += f'+ {round_up(projection)}'
            else:
                sum_force_expression_values += f' {round_up(projection)} '
        # sum_of_projections = round_up(sum_of_projections, 4)
        return sum_of_projections, sum_force_expression_names, sum_force_expression_values

    def find_max_value_on_diagram(self, diagram_name: str) -> float:
        max_value = 0
        for rod in self.rods:
            diagram = rod.__getattribute__(f'diagram_{diagram_name}')
            if diagram:
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
            if node.name == rod.start_node.name or node.name == rod.end_node.name:
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

    def is_all_rods_with_sections(self):
        for rod in self.rods:
            if not rod.sections:
                return False
        return True

    def create_sections_for_diagrams(self):
        self.is_that_frame_solved()

        for rod in self.rods:
            rod.sections = None

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

        # Проходим по всем цепочкам стержней, ведущих от свободного конца, до узла с множеством стержней
        for node in nodes_with_1_rod:
            using_loads = []
            load_on_current_rod = None

            # Находим первый стержень в цепочке и идем по цепочке пока не встретим узел с 3 и более стержнями
            for rod in self.rods:
                if node is rod.start_node or node is rod.end_node:
                    current_rod = rod
                    break
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

            if current_rod:
                while True:
                    if not current_rod or current_rod.start_node in nodes_with_3_or_more_rodes or current_rod.end_node in nodes_with_3_or_more_rodes:
                        break
                    current_rod = self.next_rod(previous_rod=current_rod, node=next_node)

                    load_on_current_rod = None
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






        # Проходим по узлам, где встречаются 3 и более стержней, находим есть ли такой узел в котором есть только один
        # стержень где еще нет сечений
        if not self.is_all_rods_with_sections():
            for node in nodes_with_3_or_more_rodes:
                rods_with_node = []
                for rod in self.rods:
                    if rod.start_node.name == node.name or rod.end_node.name == node.name:
                        rods_with_node.append(rod)
                rods_without_sections = []
                rods_with_sections = []
                for rod in rods_with_node:
                    if not rod.sections:
                        rods_without_sections.append(rod)
                    else:
                        rods_with_sections.append(rod)
                if len(rods_without_sections) == 1:
                    current_rod = rods_without_sections[0]
                    next_node = node
                    current_loads = []
                    for rod in rods_with_sections:
                        sections_on_rod = rod.sections
                        section_on_rod_with_node = None
                        for section in sections_on_rod:
                            dx = section.x - node.x
                            dy = section.y - node.y
                            if abs(dx) <= 0.1 and abs(dy) <= 0.1:
                                section_on_rod_with_node = section
                                for load in section_on_rod_with_node.loads:
                                    if load not in current_loads:
                                        current_loads.append(load)

                    if current_rod:
                        i = 0
                        while True:
                            load_on_current_rod = None
                            for load in all_loads:
                                # Добавляем нагрузки, действующие в текущем узле
                                if isinstance(load, (Force, Momentum)):
                                    if load.node.name == next_node.name and load not in current_loads:
                                        current_loads.append(load)
                                # Добавляем распределенную нагрузку, действующую на текущий стержень
                                elif isinstance(load, DistributedForce):
                                    if load.rod == current_rod:
                                        load_on_current_rod = load

                            sections_on_rod, number_of_section, next_node = current_rod.make_sections_on_rod(
                                first_node=next_node,
                                number_of_section=number_of_section,
                                loads=current_loads,
                                load_on_current_rod=load_on_current_rod,
                            )
                            sections += sections_on_rod
                            if load_on_current_rod:
                                current_loads.append(load_on_current_rod)

                            if i != 0 and current_rod.start_node in nodes_with_3_or_more_rodes or current_rod.end_node in nodes_with_3_or_more_rodes:
                                break
                            current_rod = self.next_rod(previous_rod=current_rod, node=next_node)
                            i += 1

        if not self.is_all_rods_with_sections():
            raise Exception(f'Созданы сечения не на всех стержнях')

    def calculate_N_in_node(self, node: Node, rods_with_node:List[Rod]) -> bool:
        unsoleved_rods = []
        for rod in rods_with_node:
            if not rod.diagram_N:
                unsoleved_rods.append(rod)
            elif len(rod.diagram_N) == 1:
                unsoleved_rods.append(rod)
        if len(unsoleved_rods) > 2 or len(unsoleved_rods) == 0:
            return False
        elif len(unsoleved_rods) == 2:
            if unsoleved_rods[0].get_angle_deg() == unsoleved_rods[1].get_angle_deg():
                return False

        known_intentions = []
        for rod in rods_with_node:
            if rod.dx() != 0 and rod.dy() != 0:
                raise Exception('Расчет эпюры N для наклонных стержней не реализован')
            if rod.diagram_N:
                if rod.dx() == 0:
                    if node == rod.start_node:
                        n_value = abs(rod.diagram_N[0])
                        if rod.diagram_N[0] >= 0:
                            n_direction = 90
                        else:
                            n_direction = 270
                    elif node == rod.end_node:
                        n_value = abs(rod.diagram_N[-1])
                        if rod.diagram_N[-1] >= 0:
                            n_direction = 270
                        else:
                            n_direction = 90
                elif rod.dy() == 0:
                    if node == rod.start_node:
                        n_value = abs(rod.diagram_N[0])
                        if rod.diagram_N[0] >= 0:
                            n_direction = 0
                        else:
                            n_direction = 180
                    elif node == rod.end_node:
                        n_value = abs(rod.diagram_N[-1])
                        if rod.diagram_N[-1] >= 0:
                            n_direction = 180
                        else:
                            n_direction = 0
                intention = Force(name=f'N{rod.name}', node=node, rotation=n_direction, value=n_value)
                known_intentions.append(intention)
            if rod.diagram_Q:
                if rod.dx() == 0:
                    if node == rod.start_node:
                        q_value = abs(rod.diagram_Q[0])
                        if rod.diagram_Q[0] >= 0:
                            q_direction = 0
                        else:
                            q_direction = 180
                    elif node == rod.end_node:
                        q_value = abs(rod.diagram_Q[-1])
                        if rod.diagram_Q[-1] >= 0:
                            q_direction = 180
                        else:
                            q_direction = 0
                elif rod.dy() == 0:
                    if node == rod.start_node:
                        q_value = abs(rod.diagram_Q[0])
                        if rod.diagram_Q[0] >= 0:
                            q_direction = 270
                        else:
                            q_direction = 90
                    elif node == rod.end_node:
                        q_value = abs(rod.diagram_Q[-1])
                        if rod.diagram_Q[-1] >= 0:
                            q_direction = 90
                        else:
                            q_direction = 270
                intention = Force(name=f'Q{rod.name}', node=node, rotation=q_direction, value=q_value)
                known_intentions.append(intention)
        for load in self.loads:
            if isinstance(load, Force):
                if load.node == node:
                    known_intentions.append(load)

        if len(known_intentions) == 0:
            return False

        for unsoleved_rod in unsoleved_rods:
            n = 0
            if unsoleved_rod.dx() == 0:
                for known_intention in known_intentions:
                    if known_intention.rotation in [90, 270]:
                        if known_intention.rotation == 90:
                            n += known_intention.value
                        elif known_intention.rotation == 270:
                            n -= known_intention.value

                if unsoleved_rod.start_node == node:
                    if not unsoleved_rod.diagram_N:
                        unsoleved_rod.diagram_N = [-n]
                    elif len(unsoleved_rod.diagram_N) == 1:
                        diagram_N = [-n, unsoleved_rod.diagram_N[0]]
                        unsoleved_rod.diagram_N = diagram_N
                elif unsoleved_rod.end_node == node:
                    if not unsoleved_rod.diagram_N:
                        unsoleved_rod.diagram_N = [n]
                    elif len(unsoleved_rod.diagram_N) == 1:
                        diagram_N = [unsoleved_rod.diagram_N[0], -n]
                        unsoleved_rod.diagram_N = diagram_N

            elif unsoleved_rod.dy() == 0:
                for known_intention in known_intentions:
                    if known_intention.rotation in [0, 180]:
                        if known_intention.rotation == 0:
                            n += known_intention.value
                        elif known_intention.rotation == 180:
                            n -= known_intention.value
                if unsoleved_rod.start_node == node:
                    if not unsoleved_rod.diagram_N:
                        unsoleved_rod.diagram_N = [-n]
                    elif len(unsoleved_rod.diagram_N) == 1:
                        diagram_N = [-n, unsoleved_rod.diagram_N[0]]
                        unsoleved_rod.diagram_N = diagram_N
                elif unsoleved_rod.end_node == node:
                    if not unsoleved_rod.diagram_N:
                        unsoleved_rod.diagram_N = [n]
                    elif len(unsoleved_rod.diagram_N) == 1:
                        diagram_N = [unsoleved_rod.diagram_N[0], -n]
                        unsoleved_rod.diagram_N = diagram_N
            else:
                raise Exception('Расчет эпюры N для наклонных стержней не реализован')

            is_there_q_on_rod = False
            for load in self.loads:
                if isinstance(load, DistributedForce):
                    if load.rod == unsoleved_rod:
                        is_there_q_on_rod = True

            inclined_rod = unsoleved_rod.dx() != 0 and unsoleved_rod.dy() != 0

            if len(unsoleved_rod.diagram_N) == 1:
                if not inclined_rod:
                    unsoleved_rod.diagram_N = [unsoleved_rod.diagram_N[0], unsoleved_rod.diagram_N[0]]
                elif inclined_rod and not is_there_q_on_rod:
                    unsoleved_rod.diagram_N = [unsoleved_rod.diagram_N[0], unsoleved_rod.diagram_N[0]]
        return True

    def replace_N_from_collinear_rode(self, node: Node, rods_with_node:List[Rod]) -> bool:
        if len(rods_with_node) != 2:
            raise Exception('Для коллинеальности нужны 2 стержня')
        rod1, rod2 = rods_with_node
        if rod1.diagram_N and not rod2.diagram_N:
            rod2.diagram_N = rod1.diagram_N
            return True
        elif rod2.diagram_N and not rod1.diagram_N:
            rod1.diagram_N = rod2.diagram_N
            return True
        return False

    def calculate_diagram_N(self):
        rods = self.rods
        for rod in rods:
            if not rod.diagram_Q:
                raise Exception(f'В сержне {rod} не расчитана эпюра Q')

        nodes_for_calculating = []
        nodes_with_collinear_rodes = []

        for node in self.nodes:
            rods_with_node = []
            for rod in self.rods:
                if node is rod.start_node or node is rod.end_node:
                    rods_with_node.append(rod)
            if len(rods_with_node) > 1:
                other_nodes = [node]
                for rod_with_node in rods_with_node:
                    other_node = rod_with_node.end_node if rod_with_node.end_node is not node else rod_with_node.start_node
                    other_nodes.append(other_node)
                if len(other_nodes) > 2:
                    coordinates_of_nodes = []
                    for other_node in other_nodes:
                        coordinates_of_nodes.append((other_node.x, other_node.y))
                    condition = are_collinear_nodes(points=coordinates_of_nodes)
                    if not condition:
                        nodes_for_calculating.append(node)
                    if len(other_nodes) == 3 and condition:
                        nodes_with_collinear_rodes.append(node)

        while True:
            changed = False
            for node in nodes_for_calculating:
                rods_with_node = []
                for rod in self.rods:
                    if node is rod.start_node or node is rod.end_node:
                        rods_with_node.append(rod)
                changing_in_node = self.calculate_N_in_node(node=node, rods_with_node=rods_with_node)
                if changing_in_node:
                    changed = True
            for node in nodes_with_collinear_rodes:
                rods_with_node = []
                for rod in self.rods:
                    if node is rod.start_node or node is rod.end_node:
                        rods_with_node.append(rod)
                changing_in_node = self.replace_N_from_collinear_rode(node=node, rods_with_node=rods_with_node)
                if changing_in_node:
                    changed = True
            if not changed:
                break

        for rod in rods:
            if not rod.diagram_N:
                print(f'Эпюра N на стержне {rod} не расчитана')

    def set_reactions_from_diagrams(self):
        for rod in self.rods:
            if not rod.diagram_M or not rod.diagram_Q or not rod.diagram_N:
                raise Exception('Рама не решена')
        finded_reactions = []
        for reaction in self.reactions():
            if reaction not in finded_reactions:
                r_node = reaction.node
                r_rod = None
                for rod in self.rods:
                    if rod.start_node == r_node or rod.end_node == r_node:
                        if not r_rod:
                            r_rod = rod
                        else:
                            raise Exception('К опоре может подходить только 1 стержень')
                if not r_rod:
                    raise Exception('К опоре не подходит ни один стержень')

                if isinstance(reaction, Momentum):
                    if r_node == r_rod.start_node:
                        value = abs(r_rod.diagram_M[0])
                        if r_rod.diagram_M[0] >= 0:
                            rotation = False
                        else:
                            rotation = True
                    elif r_node == r_rod.end_node:
                        value = abs(r_rod.diagram_M[-1])
                        if r_rod.diagram_M[0] >= 0:
                            rotation = True
                        else:
                            rotation = False
                    reaction.value = value
                    reaction.rotation = rotation
                    finded_reactions.append(reaction)
                elif isinstance(reaction, Force):
                    if r_node == r_rod.start_node:
                        if r_rod.dy() == 0:
                            n = r_rod.diagram_N[0]
                            if n >= 0:
                                n_rotation = 180
                            else:
                                n_rotation = 0
                            q = r_rod.diagram_Q[0]
                            if q >= 0:
                                q_rotation = 90
                            else:
                                q_rotation = 270

                            if reaction.rotation in [0, 180]:
                                reaction.rotation = n_rotation
                                reaction.value = abs(n)
                            elif reaction.rotation in [90, 270]:
                                reaction.rotation = q_rotation
                                reaction.value = abs(q)
                            finded_reactions.append(reaction)
                        elif r_rod.dx() == 0:
                            n = r_rod.diagram_N[0]
                            if n >= 0:
                                n_rotation = 270
                            else:
                                n_rotation = 90
                            q = r_rod.diagram_Q[0]
                            if q >= 0:
                                q_rotation = 180
                            else:
                                q_rotation = 0

                            if reaction.rotation in [90, 270]:
                                reaction.rotation = n_rotation
                                reaction.value = abs(n)
                            elif reaction.rotation in [0, 180]:
                                reaction.rotation = q_rotation
                                reaction.value = abs(q)
                            finded_reactions.append(reaction)
                    if r_node == r_rod.end_node:
                        if r_rod.dy() == 0:
                            n = r_rod.diagram_N[-1]
                            if n >= 0:
                                n_rotation = 0
                            else:
                                n_rotation = 180
                            q = r_rod.diagram_Q[-1]
                            if q >= 0:
                                q_rotation = 270
                            else:
                                q_rotation = 90

                            if reaction.rotation in [0, 180]:
                                reaction.rotation = n_rotation
                                reaction.value = abs(n)
                            elif reaction.rotation in [90, 270]:
                                reaction.rotation = q_rotation
                                reaction.value = abs(q)
                            finded_reactions.append(reaction)
                        elif r_rod.dx() == 0:
                            n = r_rod.diagram_N[-1]
                            if n >= 0:
                                n_rotation = 90
                            else:
                                n_rotation = 270
                            q = r_rod.diagram_Q[-1]
                            if q >= 0:
                                q_rotation = 0
                            else:
                                q_rotation = 180

                            if reaction.rotation in [90, 270]:
                                reaction.rotation = n_rotation
                                reaction.value = abs(n)
                            elif reaction.rotation in [0, 180]:
                                reaction.rotation = q_rotation
                                reaction.value = abs(q)
                            finded_reactions.append(reaction)
        self.finded_reactions = finded_reactions


