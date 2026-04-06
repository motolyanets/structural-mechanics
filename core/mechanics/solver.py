from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import math
import sympy as sp

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.support import Support
from services.services import round_up


class SolvableFrame:
    def __init__(self, nodes: List[Node], rods: List[Rod], supports: List[Support], loads: list,
                 finded_reactions=None):
        self.nodes = nodes
        self.rods = rods
        self.supports = supports
        self.loads = loads
        self.finded_reactions = finded_reactions if finded_reactions is not None else []

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

    def find_node_with_single_unknown(self):
        reactions = self.reactions()
        for node in self.nodes:
            point = (node.x, node.y)
            unknown_count = []
            for reaction in reactions:
                lever_arm = reaction.get_lever_arm(point=point)
                if lever_arm and not reaction.value:
                    unknown_count.append(reaction)
            if len(unknown_count) == 1:
                return node, unknown_count[0]
        raise Exception('В раме нет такого узла, в котором будет только одна неизвестная')

    def solve_single_unknown_at_node(self, node: Node):
        point = (node.x, node.y)
        moment = 0
        for load in self.loads:
            if isinstance(load, Force):
                moment += load.get_moment_about(point=point)
            elif isinstance(load, Momentum):
                if load.rotation:
                    moment += load.value
                else:
                    moment -= load.value
            if isinstance(load, DistributedForce):
                moment += load.get_moment_about(point=point)

        reaction = self.find_node_with_single_unknown()[1]
        reaction_lever_arm = reaction.get_lever_arm(point=point)
        reaction_value = -moment / reaction_lever_arm
        return [reaction.name, round_up(reaction_value, 2)]

    def sum_force_projections(self, axis: str):
        sum_of_projections = 0
        all_loads = self.loads + self.finded_reactions
        for load in all_loads:
            if isinstance(load, Force):
                projection = load.get_projection_on_axis(axis_name=axis)
                sum_of_projections += projection
            elif isinstance(load, DistributedForce):
                projection = load.get_projection_on_axis(axis_name=axis)
                sum_of_projections += projection
        return sum_of_projections

    def find_reaction_from_force_projection(self, axis: str):
        sum_of_loads = self.sum_force_projections(axis=axis)
        finded_reactions_names = [i.name for i in self.finded_reactions]
        unknown_count = []

        for reaction in self.reactions():
            if reaction.name not in finded_reactions_names and reaction.rotation in [0, 180] and axis == 'x':
                unknown_count.append(reaction)
            elif reaction.name not in finded_reactions_names and reaction.rotation in [90, 270] and axis == 'y':
                unknown_count.append(reaction)

        if len(unknown_count) > 1:
            raise Exception('В сумме проекций больше одной переменной')
        elif len(unknown_count) == 0:
            raise Exception('В сумме проекций нет неизвестных')
        else:
            reaction = unknown_count[0]
            rotation_radians = math.radians(reaction.rotation)
            if axis == 'x':
                reaction.value = round_up(- sum_of_loads * math.cos(rotation_radians))
            elif axis == 'y':
                reaction.value = round_up(- sum_of_loads * math.sin(rotation_radians))
            self.finded_reactions.append(reaction)

    def get_unknown_reactions_from_part(self) -> List[Force]:
        all_reactions = self.reactions()
        known_names = [r.name for r in self.finded_reactions]
        unknown_reactions = []
        for reaction in all_reactions:
            if reaction.name not in known_names and isinstance(reaction, Force):
                unknown_reactions.append(reaction)
        return unknown_reactions

    def create_moment_equation_about_support(self, support_node: Node, unknown_reactions: List[Force]) -> str:
        point = (support_node.x, support_node.y)
        return self.create_moment_equation_with_two_unknowns(point, unknown_reactions)

    def create_moment_equation_with_two_unknowns(self, point: Tuple[float, float], unknown_reactions: List[Force]) -> str:
        coefficients = {}
        constant_term = 0

        for reaction in unknown_reactions:
            reaction.value = None
            coefficients[reaction.name] = 0

        all_known_loads = self.loads.copy()
        for reaction in self.finded_reactions:
            if isinstance(reaction, Force):
                all_known_loads.append(reaction)

        for load in all_known_loads:
            if isinstance(load, Force):
                moment = load.get_moment_about(point=point)
                if abs(moment) > 1e-10:
                    constant_term += moment
            elif isinstance(load, Momentum):
                if load.rotation:
                    moment = load.value
                else:
                    moment = -load.value
                if abs(moment) > 1e-10:
                    constant_term += moment
            elif isinstance(load, DistributedForce):
                moment = load.get_moment_about(point=point)
                if abs(moment) > 1e-10:
                    constant_term += moment

        for reaction in unknown_reactions:
            lever_arm = reaction.get_lever_arm(point=point)
            coefficients[reaction.name] = lever_arm

        equation_parts = []
        sorted_coeffs = sorted(coefficients.items(), key=lambda x: x[0])
        is_first_term = True

        for name, coeff in sorted_coeffs:
            if abs(coeff) > 1e-10:
                if coeff == 1:
                    coeff_str = ""
                elif coeff == -1:
                    coeff_str = "-"
                else:
                    coeff_str = self._format_number(abs(coeff)) + "·"

                if is_first_term:
                    if coeff < 0:
                        equation_parts.append(f"-{coeff_str}{name}")
                    else:
                        equation_parts.append(f"{coeff_str}{name}")
                    is_first_term = False
                else:
                    if coeff < 0:
                        equation_parts.append(f"- {coeff_str}{name}")
                    else:
                        equation_parts.append(f"+ {coeff_str}{name}")

        if abs(constant_term) > 1e-10:
            if is_first_term:
                if constant_term < 0:
                    equation_parts.append(f"-{self._format_number(abs(constant_term))}")
                else:
                    equation_parts.append(f"{self._format_number(constant_term)}")
            else:
                if constant_term < 0:
                    equation_parts.append(f"- {self._format_number(abs(constant_term))}")
                else:
                    equation_parts.append(f"+ {self._format_number(constant_term)}")

        if equation_parts:
            equation = " ".join(equation_parts)
            equation = equation.replace("  ", " ")
            equation += " = 0"
        else:
            equation = "0 = 0"

        point_label = self._get_point_label(point)
        return f"∑M{point_label}: {equation}"

    def _format_number(self, num: float) -> str:
        rounded = round(num, 2)
        if rounded.is_integer():
            return str(int(rounded))
        else:
            return f"{rounded:.2f}".rstrip('0').rstrip('.')

    def _get_point_label(self, point: Tuple[float, float]) -> str:
        for support in self.supports:
            if support.node.x == point[0] and support.node.y == point[1]:
                return f"({support.node.name})"
        for node in self.nodes:
            if node.x == point[0] and node.y == point[1]:
                return f"({node.name})"
        return f"[{point[0]};{point[1]}]"

    def classify_part(self):
        amount_of_reactions = len(self.reactions())
        amount_of_hinges = sum(1 for node in self.nodes if node.is_hinge)

        if amount_of_reactions == 3 and amount_of_hinges == 0:
            print('   - Простая рама')
            return SimpleFrame(
                nodes=self.nodes, rods=self.rods, supports=self.supports,
                loads=self.loads, finded_reactions=self.finded_reactions
            )
        elif amount_of_reactions == 4 and amount_of_hinges == 0:
            print('   - Затяжка')
            return Tightening(
                nodes=self.nodes, rods=self.rods, supports=self.supports,
                loads=self.loads, finded_reactions=self.finded_reactions
            )
        elif amount_of_reactions == 4 and amount_of_hinges == 1:
            print('   - Трехшарнирная рама')
            return ThreeHingedFrame(
                nodes=self.nodes, rods=self.rods, supports=self.supports,
                loads=self.loads, finded_reactions=self.finded_reactions
            )
        else:
            raise Exception(f"Вид рамы не определен: reactions={amount_of_reactions}, hinges={amount_of_hinges}")



class BaseFrame(ABC):
    @abstractmethod
    def solve_frame(self):
        pass


class SimpleFrame(SolvableFrame, BaseFrame):
    def solve_frame(self):
        print(50 * '-')
        print('Решаем простую раму')
        reactions = self.reactions()
        node1 = self.find_node_with_single_unknown()[0]
        r = self.solve_single_unknown_at_node(node=node1)
        for reaction in reactions:
            if r[0] == reaction.name:
                reaction.value = r[1]
                self.finded_reactions.append(reaction)

        self.find_reaction_from_force_projection('x')
        self.find_reaction_from_force_projection('y')

        for reaction in self.finded_reactions:
            print(f'{reaction.name}={reaction.value} ------ {reaction.rotation}')
        print(50 * '-')
        return self


class Tightening(SolvableFrame, BaseFrame):
    def solve_frame(self):
        print(50 * '-')
        print('Решаем затяжку')
        reactions = self.reactions()
        node1 = self.find_node_with_single_unknown()[0]
        r = self.solve_single_unknown_at_node(node=node1)
        for reaction in reactions:
            if r[0] == reaction.name:
                reaction.value = r[1]
                self.finded_reactions.append(reaction)

        try:
            self.find_reaction_from_force_projection('x')
        except Exception:
            self.find_reaction_from_force_projection('y')

        for reaction in self.finded_reactions:
            print(f'{reaction.name}={reaction.value} ------ {reaction.rotation}')
        print(50 * '-')
        return self


class ThreeHingedFrame(SolvableFrame, BaseFrame):
    def split_three_hinged_frame(self):
        for node in self.nodes:
            if node.is_hinge:
                hinge_node = node

        rods_connected_to_hinge = []
        for rod in self.rods:
            if rod.start_node == hinge_node or rod.end_node == hinge_node:
                rods_connected_to_hinge.append(rod)

        if len(rods_connected_to_hinge) != 2:
            raise Exception(f"К шарниру в узле {hinge_node.name} должно быть подключено 2 стержня")

        left_nodes = {hinge_node}
        right_nodes = {hinge_node}
        left_rods = set()
        right_rods = set()

        def traverse_from_hinge(start_rod, collected_nodes, collected_rods):
            collected_rods.add(start_rod)
            if start_rod.start_node == hinge_node:
                current_node = start_rod.end_node
            else:
                current_node = start_rod.start_node
            collected_nodes.add(current_node)
            stack = [(current_node, start_rod)]

            while stack:
                node, came_from_rod = stack.pop()
                for rod in self.rods:
                    if rod in collected_rods:
                        continue
                    if rod.start_node == node or rod.end_node == node:
                        if rod.start_node == node:
                            neighbor = rod.end_node
                        else:
                            neighbor = rod.start_node
                        collected_rods.add(rod)
                        if neighbor not in collected_nodes:
                            collected_nodes.add(neighbor)
                            stack.append((neighbor, rod))

        traverse_from_hinge(rods_connected_to_hinge[0], left_nodes, left_rods)
        traverse_from_hinge(rods_connected_to_hinge[1], right_nodes, right_rods)

        left_nodes_list = [node for node in self.nodes if node in left_nodes]
        left_rods_list = [rod for rod in self.rods if rod in left_rods]
        left_supports = [sup for sup in self.supports if sup.node in left_nodes]

        right_nodes_list = [node for node in self.nodes if node in right_nodes]
        right_rods_list = [rod for rod in self.rods if rod in right_rods]
        right_supports = [sup for sup in self.supports if sup.node in right_nodes]

        left_loads, right_loads = self._distribute_loads_with_hinge(
            hinge_node, left_nodes, right_nodes, left_rods, right_rods
        )

        left_part = SolvableFrame(
            nodes=left_nodes_list, rods=left_rods_list, supports=left_supports,
            loads=left_loads, finded_reactions=self.finded_reactions.copy()
        )
        right_part = SolvableFrame(
            nodes=right_nodes_list, rods=right_rods_list, supports=right_supports,
            loads=right_loads, finded_reactions=self.finded_reactions.copy()
        )

        return left_part, right_part, hinge_node

    def _distribute_loads_with_hinge(self, hinge_node, left_nodes, right_nodes, left_rods, right_rods):
        left_loads = []
        right_loads = []
        distributed_loads = set()

        for load in self.loads:
            load_id = id(load)
            if load_id in distributed_loads:
                continue

            if isinstance(load, (Force, Momentum)):
                if load.node == hinge_node:
                    left_loads.append(load)
                    distributed_loads.add(load_id)
                elif load.node in left_nodes:
                    left_loads.append(load)
                    distributed_loads.add(load_id)
                elif load.node in right_nodes:
                    right_loads.append(load)
                    distributed_loads.add(load_id)

            elif isinstance(load, DistributedForce):
                if load.rod in left_rods:
                    left_loads.append(load)
                    distributed_loads.add(load_id)
                elif load.rod in right_rods:
                    right_loads.append(load)
                    distributed_loads.add(load_id)

        return left_loads, right_loads

    def find_intersection_point_of_reactions(self, part: SolvableFrame) -> Tuple[float, float]:
        unknown_reactions = []
        for reaction in part.reactions():
            if reaction.name not in [r.name for r in part.finded_reactions]:
                if isinstance(reaction, Force):
                    unknown_reactions.append(reaction)

        if len(unknown_reactions) != 2:
            raise Exception(f"В части рамы должно быть 2 неизвестные реакции")

        for support in part.supports:
            if support.number_of_reactions == 2:
                return (support.node.x, support.node.y)

        lines = []
        for reaction in unknown_reactions:
            x0, y0 = reaction.node.x, reaction.node.y
            angle_rad = math.radians(reaction.rotation)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)
            lines.append({'point': (x0, y0), 'direction': (dx, dy), 'reaction': reaction})

        x1, y1 = lines[0]['point']
        dx1, dy1 = lines[0]['direction']
        x2, y2 = lines[1]['point']
        dx2, dy2 = lines[1]['direction']

        t1, t2 = sp.symbols('t1 t2')
        eq1 = sp.Eq(x1 + t1 * dx1, x2 + t2 * dx2)
        eq2 = sp.Eq(y1 + t1 * dy1, y2 + t2 * dy2)
        solution = sp.solve([eq1, eq2], [t1, t2])

        if not solution:
            for support in part.supports:
                return (support.node.x, support.node.y)

        t1_val = float(solution[t1])
        intersection_x = x1 + t1_val * dx1
        intersection_y = y1 + t1_val * dy1
        return intersection_x, intersection_y

    def create_equation_for_half_about_hinge(self, part: SolvableFrame, hinge_node: Node) -> str:
        point = (hinge_node.x, hinge_node.y)
        unknown_reactions = []
        for reaction in part.reactions():
            if reaction.name not in [r.name for r in part.finded_reactions]:
                if isinstance(reaction, Force):
                    unknown_reactions.append(reaction)
        return part.create_moment_equation_with_two_unknowns(point, unknown_reactions)

    def create_equation_for_whole_frame_about_point(self, point: Tuple[float, float]) -> str:
        unknown_reactions = []
        for reaction in self.reactions():
            if reaction.name not in [r.name for r in self.finded_reactions]:
                if isinstance(reaction, Force):
                    unknown_reactions.append(reaction)
        return self.create_moment_equation_with_two_unknowns(point, unknown_reactions[:2])

    def solve_system_of_equations(self, equation1: str, equation2: str) -> dict:
        import re

        def parse_equation(equation: str):
            """Парсит уравнение вида: ∑M(X): a·XA + b·YA + c = 0"""

            # Убираем префикс ∑M(...):
            if ':' in equation:
                equation_part = equation.split(':', 1)[1].strip()
            else:
                equation_part = equation.strip()

            # Переносим правую часть влево
            if '=' in equation_part:
                left, right = equation_part.split('=')
                left = left.strip()
                right = right.strip()
                if right and right != '0':
                    if right.startswith('-'):
                        left += f" + {right[1:]}"
                    else:
                        left += f" - {right}"
            else:
                left = equation_part

            # Находим все переменные (только XA, YA, XB, YB и т.д.)
            # Ищем заглавные буквы с возможной цифрой
            var_pattern = r'\b([A-Z][A-Z0-9]*)\b'
            variables = re.findall(var_pattern, left)
            # Убираем дубликаты, сохраняем порядок
            variables = list(dict.fromkeys(variables))

            # Если переменных больше 2, берём первые две
            # Если меньше 2, остальные считаем нулевыми

            coeffs = {var: 0.0 for var in variables[:2]}
            constant = 0.0

            # Разбиваем на термы (с учётом знаков)
            # Заменяем · на * для единообразия
            left = left.replace('·', '*')

            # Добавляем + в начало для удобства парсинга
            if not left.startswith('-') and not left.startswith('+'):
                left = '+' + left

            # Ищем термы вида: + 15*YA, - 7.6*XA, + 4, - 0.01
            term_pattern = r'([+-])\s*([0-9.]*)\s*\*?\s*([A-Z][A-Z0-9]*)?'

            for match in re.finditer(term_pattern, left):
                sign = 1 if match.group(1) == '+' else -1

                # Число
                num_str = match.group(2)
                if num_str and num_str.strip():
                    num = float(num_str) * sign
                else:
                    num = 1.0 * sign

                # Переменная
                var = match.group(3)

                if var:
                    # Это член с переменной
                    if var in coeffs:
                        coeffs[var] += num
                    else:
                        # Неожиданная переменная, игнорируем или добавляем
                        coeffs[var] = num
                else:
                    # Это свободный член
                    constant += num

            # Приводим к стандартному виду: a·XA + b·YA + c = 0
            var_names = list(coeffs.keys())

            # Определяем XA и YA (или другие имена)
            x_name = None
            y_name = None

            for var in var_names:
                if 'X' in var or var.startswith('X'):
                    x_name = var
                elif 'Y' in var or var.startswith('Y'):
                    y_name = var

            # Если не нашли по X/Y, берём первую и вторую
            if x_name is None and len(var_names) > 0:
                x_name = var_names[0]
            if y_name is None and len(var_names) > 1:
                y_name = var_names[1]

            a = coeffs.get(x_name, 0.0) if x_name else 0.0
            b = coeffs.get(y_name, 0.0) if y_name else 0.0

            return a, b, constant, x_name, y_name

        # Парсим уравнения
        a1, b1, c1, x_name1, y_name1 = parse_equation(equation1)
        a2, b2, c2, x_name2, y_name2 = parse_equation(equation2)

        # print(f"\n📐 Распознанные уравнения:")
        # print(f"   1: {a1:.4f}·{x_name1} + {b1:.4f}·{y_name1} + {c1:.4f} = 0")
        # print(f"   2: {a2:.4f}·{x_name2} + {b2:.4f}·{y_name2} + {c2:.4f} = 0")

        # Приводим к общим именам переменных
        # Определяем, как названы переменные в обоих уравнениях
        all_vars = set()
        if x_name1:
            all_vars.add(x_name1)
        if y_name1:
            all_vars.add(y_name1)
        if x_name2:
            all_vars.add(x_name2)
        if y_name2:
            all_vars.add(y_name2)

        all_vars = sorted(list(all_vars))

        if len(all_vars) == 1:
            # Только одна переменная
            var = all_vars[0]

            # Собираем коэффициенты из обоих уравнений
            coeff_sum = 0
            const_sum = 0

            if var in [x_name1, y_name1]:
                coeff_sum += a1 if var == x_name1 else b1
                const_sum += c1
            if var in [x_name2, y_name2]:
                coeff_sum += a2 if var == x_name2 else b2
                const_sum += c2

            if abs(coeff_sum) < 1e-10:
                raise Exception(f"Нет уравнения для определения {var}")

            value = -const_sum / coeff_sum
            value = round(value, 2)

            # print(f"\n✅ Решение:")
            # print(f"   {var} = {value}")

            return {var: value}

        elif len(all_vars) == 2:
            # Две переменные
            var1, var2 = all_vars[0], all_vars[1]

            # Приводим оба уравнения к одним переменным
            def get_coeffs(a, b, x_name, y_name):
                coeff_var1 = a if x_name == var1 else (b if y_name == var1 else 0)
                coeff_var2 = a if x_name == var2 else (b if y_name == var2 else 0)
                return coeff_var1, coeff_var2

            a1_new, b1_new = get_coeffs(a1, b1, x_name1, y_name1)
            a2_new, b2_new = get_coeffs(a2, b2, x_name2, y_name2)

            # Решаем систему
            determinant = a1_new * b2_new - a2_new * b1_new

            # print(f"\n   Определитель: Δ = {determinant:.6f}")

            if abs(determinant) < 1e-8:
                raise Exception(f"Система вырождена (Δ = {determinant:.2e})")

            det_var1 = (-c1) * b2_new - (-c2) * b1_new
            det_var2 = a1_new * (-c2) - a2_new * (-c1)

            value1 = det_var1 / determinant
            value2 = det_var2 / determinant

            value1 = round(value1, 2)
            value2 = round(value2, 2)

            # print(f"\n✅ Решение:")
            # print(f"   {var1} = {value1}")
            # print(f"   {var2} = {value2}")

            return {var1: value1, var2: value2}

        else:
            raise Exception(f"Не удалось распознать переменные в уравнениях")

    def solve_frame(self):
        print(50 * '-')
        print('Решаем трехшарнирную раму')

        left_part, right_part, hinge_node = self.split_three_hinged_frame()

        equation1 = self.create_equation_for_half_about_hinge(left_part, hinge_node)
        intersection_point = self.find_intersection_point_of_reactions(right_part)
        equation2 = self.create_equation_for_whole_frame_about_point(intersection_point)

        solution = self.solve_system_of_equations(equation1, equation2)

        for var, value in solution.items():
            for reaction in self.reactions():
                if reaction.name == var:
                    reaction.value = value
                    self.finded_reactions.append(reaction)
                    # print(f"Реакция {var} = {value:.2f} сохранена")

        self.find_reaction_from_force_projection('x')
        self.find_reaction_from_force_projection('y')

        for reaction in self.finded_reactions:
            print(f'{reaction.name}={reaction.value} ------ {reaction.rotation}')
        print(50 * '-')

        return self
