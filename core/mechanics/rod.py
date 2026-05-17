import math
from typing import List, Optional, Tuple

from core.mechanics.node import Node
from core.mechanics.section import Section
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
            diagram_N: List | None = None,
            stiffness: float = 1,
    ):
        self.sections = None
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
        self.diagram_N = diagram_N
        self.stiffness = stiffness
        self.nodes = [self.start_node, self.end_node]

    def dx(self) -> float:
        dx = self.end_node.x - self.start_node.x
        return math.fabs(dx)

    def dy(self) -> float:
        dy = self.end_node.y - self.start_node.y
        return math.fabs(dy)

    def middle(self) -> Tuple[float, float]:
        x = (self.start_node.x + self.end_node.x) / 2
        y = (self.start_node.y + self.end_node.y) / 2
        return x, y

    def length(self) -> float:
        dx = self.dx()
        dy = self.dy()
        length = math.sqrt(dx ** 2 + dy ** 2)
        return round_up(length)

    def is_node_on_rod(self, node: Node):
        if node.name != self.start_node.name and node.name != self.end_node.name:
            raise ValueError(f"Узел {node} не принадлежит этому стержню ({self})")

    def get_coordinates_of_section(self, node: Node, distance: float = 0.0001, center: bool = False) -> tuple[float, float, float, float]:
        """
        node : объект узла (self.start_node или self.end_node)
        distance : float, расстояние от указанного узла вдоль стержня
        возвращает (x, y)
        """
        drawing_distance = 0.1
        if center:
            distance = self.length() / 2

        if distance > self.length():
            raise ValueError(f"Расстояние {distance} больше длины стержня {self.length}")
        self.is_node_on_rod(node=node)

        t = distance / self.length()
        t_drawing = drawing_distance / self.length()
        if node is self.start_node:
            x = self.start_node.x + t * (self.end_node.x - self.start_node.x)
            y = self.start_node.y + t * (self.end_node.y - self.start_node.y)
            x_drawing = self.start_node.x + t_drawing * (self.end_node.x - self.start_node.x)
            y_drawing = self.start_node.y + t_drawing * (self.end_node.y - self.start_node.y)
        elif node is self.end_node:
            x = self.end_node.x + t * (self.start_node.x - self.end_node.x)
            y = self.end_node.y + t * (self.start_node.y - self.end_node.y)
            x_drawing = self.end_node.x + t_drawing * (self.start_node.x - self.end_node.x)
            y_drawing = self.end_node.y + t_drawing * (self.start_node.y - self.end_node.y)
        else:
            raise ValueError("Узел не принадлежит этому стержню")

        return x, y, x_drawing, y_drawing

    def make_section(self, number_of_section: int, node: Node, loads: List) -> Section:
        self.is_node_on_rod(node=node)

        is_hinge = False

        x, y, x_drawing, y_drawing = self.get_coordinates_of_section(node=node)
        if node.is_hinge:
            is_hinge = True
        if node == self.start_node and self.is_start_hinge:
            is_hinge = True
        elif node == self.end_node and self.is_end_hinge:
            is_hinge = True

        section = Section(name=str(number_of_section), x=x, y=y, x_drawing=x_drawing, y_drawing=y_drawing, loads=loads,
                          is_hinge=is_hinge)
        return section

    def make_section_in_center_of_rod(self, number_of_section: int, node: Node, loads: List) -> Section:
        self.is_node_on_rod(node=node)

        x, y, _, _ = self.get_coordinates_of_section(node=node, center=True)

        section = Section(name=str(number_of_section), x=x, y=y, x_drawing=x, y_drawing=y, loads=loads)
        return section

    def make_sections_on_rod(self, first_node: Node, number_of_section: int, loads: List, load_on_current_rod):
        loads = loads.copy()

        self.is_node_on_rod(node=first_node)
        if not load_on_current_rod:
            if first_node is self.start_node:
                section1 = self.make_section(number_of_section=number_of_section, node=self.start_node, loads=loads)
                number_of_section += 1
                section2 = self.make_section(number_of_section=number_of_section, node=self.end_node, loads=loads)
                next_node = self.end_node
            elif first_node is self.end_node:
                section1 = self.make_section(number_of_section=number_of_section, node=self.end_node, loads=loads)
                number_of_section += 1
                section2 = self.make_section(number_of_section=number_of_section, node=self.start_node, loads=loads)
                next_node = self.start_node
            sections = [section1, section2]

        else:
            distr_load = load_on_current_rod.split_load_for_calculation_section()
            if first_node is self.start_node:
                section1 = self.make_section(number_of_section=number_of_section, node=self.start_node, loads=loads.copy())

                number_of_section += 1
                loads_for_center = loads.copy()
                loads_for_center.append(distr_load[0])
                section2 = self.make_section_in_center_of_rod(number_of_section=number_of_section, node=self.start_node,
                                                              loads=loads_for_center)

                number_of_section += 1
                loads_for_end = loads.copy()
                loads_for_end.append(load_on_current_rod)
                section3 = self.make_section(number_of_section=number_of_section, node=self.end_node, loads=loads_for_end)
                next_node = self.end_node
            elif first_node is self.end_node:
                section1 = self.make_section(number_of_section=number_of_section, node=self.end_node, loads=loads.copy())

                number_of_section += 1
                loads_for_center = loads.copy()
                loads_for_center.append(distr_load[1])
                section2 = self.make_section_in_center_of_rod(number_of_section=number_of_section, node=self.start_node,
                                                              loads=loads_for_center)

                number_of_section += 1
                loads_for_end = loads.copy()
                loads_for_end.append(load_on_current_rod)
                section3 = self.make_section(number_of_section=number_of_section, node=self.start_node, loads=loads_for_end)
                next_node = self.start_node
            sections = [section1, section2, section3]
        number_of_section += 1
        self.sections = sections
        return sections, number_of_section, next_node

    def determine_sign_of_section_m(self):
        if self.dy() == 0:
            # Стержень горизонтальный
            if self.sections[-1].x > self.sections[0].x:
                # Если сечения идут с лева на право
                sign = -1
            else:
                # Если сечения идут с права на лево
                sign = 1
        elif self.dx() == 0:
            # Стержень вертикальный
            if self.sections[-1].y > self.sections[0].y:
                # Если сечения идут с низа в верх
                sign = -1
            else:
                # Если сечения идут с верха в низ
                sign = 1
        elif self.dx() != 0 and self.dy() != 0:
            # Стержень наклонный
            if self.sections[-1].x > self.sections[0].x:
                # Если сечения идут с лева на право
                sign = -1
            else:
                # Если сечения идут с права на лево
                sign = 1
        else:
            raise Exception('Сдучай определения знака эпюры моментов не определен!')
        return sign

    def sort_sections(self):
        if self.dx() == 0:
            # Стержень вертикальный
            sorted_sections = sorted(self.sections, key=lambda x: x.y)
        else:
            # Стержень наклонный или горизонтальный
            sorted_sections = sorted(self.sections, key=lambda x: x.x)
        return sorted_sections

    def calculate_diagram_m(self, diagram_name: str):
        diagram = []

        finding_moments = []
        for section in self.sort_sections():
            section_moment, section_equation = section.sum_momentum_about_section()
            sign = self.determine_sign_of_section_m()
            if section_moment == 0:
                diagram.append(section_moment)
            else:
                diagram.append(section_moment * sign)
            finding_moments.append(section_equation)




        if diagram_name == '1':
            # if self.start_node.name in ['4', 'K']:
            #     diagram = [0, 0]
            # elif self.start_node.name == '2' and self.end_node.name == '4':
            #     diagram[-1] = 0
            self.diagram_M1 = diagram
        elif diagram_name == '2':
            self.diagram_M2 = diagram
        elif diagram_name == '3':
            # if self.start_node.name == '8' and self.end_node.name == 'C':
            #     diagram = [0, 0]
            self.diagram_M3 = diagram
        elif diagram_name == 'p':
            self.diagram_Mp = diagram
        elif diagram_name == 'k':
            # if self.start_node.name == '8' and self.end_node.name == 'C':
            #     diagram = [0, 0]
            self.diagram_Mk = diagram
        else:
            raise Exception(f'Такое название нагрузок ({diagram_name}) не определено')


        report = ''
        for i in finding_moments:
            report += f'{i}\n'
        report.strip('\n')
        print(f'{self}-------{diagram}')

        return report


    def multiply_diagrams_Simpson(self, diagram_1_name, diagram_2_name, q: float | None = None):
        diagram_1 = self.__getattribute__(f'diagram_{diagram_1_name}')
        diagram_2 = self.__getattribute__(f'diagram_{diagram_2_name}')

        length = self.length()
        stiffness = self.stiffness

        multiplied_diagram = []

        d1_start = diagram_1[0]
        d1_center = round_up((diagram_1[0] + diagram_1[-1]) / 2, 3)
        d1_end = diagram_1[-1]
        d2_start = diagram_2[0]
        d2_center = round_up((diagram_2[0] + diagram_2[-1]) / 2, 3)
        d2_end = diagram_2[-1]

        d1_start_t = round_up(d1_start)
        d1_center_t = round_up(d1_center)
        d1_end_t = round_up(d1_end)
        d2_start_t = round_up(d2_start)
        d2_center_t = round_up(d2_center)
        d2_end_t = round_up(d2_end)

        if len(diagram_1) == len(diagram_2) == 2:
            result = (length / (6 * stiffness)) * (d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end)
            if result:
                text = (
                    f'({length} / (6·{stiffness}·EI)) · ({d1_start_t}·{d2_start_t} + 4·{d1_center_t}·{d2_center_t} + '
                    f'{d1_end_t}·{d2_end_t})')
                multiplied_diagram.append(text)
                multiplied_diagram.append(result)
        else:
            result = (length / (6 * stiffness)) * (
                        d1_start * d2_start + 4 * d1_center * d2_center + d1_end * d2_end + 4 * d1_center * q * length ** 2 / 8)
            if result:
                text = (
                    f'({length} / (6·{stiffness}·EI)) * ({d1_start_t}·{d2_start_t} + 4·{d1_center_t}·{d2_center_t} + '
                    f'{d1_end_t}·{d2_end_t} + 4·{d1_center_t}·{q}·{length}² / 8)')
                multiplied_diagram.append(text)
                multiplied_diagram.append(result)

        return multiplied_diagram

    def __repr__(self) -> str:
        return f"Rod({self.start_node.name}→{self.end_node.name}, L={self.length():.3f})"
