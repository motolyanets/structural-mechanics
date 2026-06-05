import math
from typing import Tuple

from ezdxf.math import Vec2

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from services.services import round_up


class Load:
    pass


class Force(Load):
    """Создаем класс для сосредоточенного усилия"""

    def __init__(self, name: str, node: Node, rotation: int | float, value: float | None = None):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = int(rotation)
        self.x = node.x
        self.y = node.y

    def get_lever_arm(self, point: Tuple[float, float]) -> float:
        """
        Определяет плечо силы относительно точки с учетом знака ("+" - по часовой, "-" - против часовой).

        Args:
            point: координата точки (x, y), относительно которой вычисляется момент

        Returns:
            float: moment_arm: плечо силы со знаком
        """

        # Вычисляем вектор от точки до точки приложения силы
        dx = point[0] - self.node.x
        dy = point[1] - self.node.y

        # Преобразуем угол силы в радианы
        angle_rad = math.radians(self.rotation)

        # Вычисляем компоненты вектора силы
        force_x = math.cos(angle_rad)
        force_y = math.sin(angle_rad)

        # Вычисляем плечо силы (векторное произведение радиус-вектора на вектор силы)
        # M = r × F = |r| * |F| * sin(θ)
        # В 2D: M = (dx * Fy - dy * Fx)
        moment_arm = dx * force_y - dy * force_x
        moment_arm = round_up(moment_arm, 3)

        return moment_arm

    def get_moment_about(self, point: Tuple[float, float]) -> tuple:
        lever_arm = self.get_lever_arm(point=point)
        moment = lever_arm * self.value
        if lever_arm >= 0:
            text = f' +{self.name}·{round_up(abs(lever_arm))}'
        else:
            text = f' -{self.name}·{round_up(abs(lever_arm))}'
        return text, moment

    def get_projection_on_axis(self, axis_name: str) -> tuple:
        rotation_radians = math.radians(self.rotation)
        if axis_name == 'x':
            projection = self.value * math.cos(rotation_radians)
        elif axis_name == 'y':
            projection = self.value * math.sin(rotation_radians)
        else:
            raise Exception('Название оси должно быть \'x\' или \'y\'')
        # projection = round(projection, 2)
        if projection >= 0:
            expression = f' + {self.name}'
        else:
            expression = f' - {self.name}'
        return projection, expression

    def draw(self, insert_point: Tuple[float, float], msp):
        msp.add_blockref('Сосредоточенная сила', insert=insert_point,
                         dxfattribs={
                             "layer": "Loads",
                             "rotation": self.rotation,
                         })
        text = f'{self.name} = {round_up(self.value)}'

        # Рассчитываем вектор направления
        angle_rad = math.radians(self.rotation)
        direction = Vec2(math.cos(angle_rad), math.sin(angle_rad))

        # Вычисляем точку на конце стрелки
        tip_point = Vec2(insert_point) + direction * 0.6 + Vec2(0.1, -0.1)

        msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads",}).set_placement(tip_point)
        return msp

    def __repr__(self) -> str:
        return f"Force({self.name}={self.value} ---- {self.rotation}, node - {self.node.name})"


class Momentum(Load):
    """Создаем класс для момента"""

    def __init__(self, name: str, node: Node, rotation: bool, value: float | None = None, rod: Rod | None = None):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = rotation
        self.x = node.x
        self.y = node.y
        self.rod = rod
        if self.node.is_hinge:
            if self.rod:
                self.rod.momentum_at_hinge = True
            else:
                raise Exception('Если момент приложен к шарниру, нужно указать на какой стержень он действует')


    def draw(self, insert_point: Tuple[float, float], msp):
        if self.rotation:
            block_name = 'Момент (по часовой)'
        else:
            block_name = 'Момент (против часовой)'

        if not self.rod:
            insert = insert_point
        else:
            t = 0.1 / self.rod.length()
            if self.node == self.rod.start_node:
                x1, y1 = self.rod.start_node.x, self.rod.start_node.y
                x2, y2 = self.rod.end_node.x, self.rod.end_node.y
            else:
                x2, y2 = self.rod.start_node.x, self.rod.start_node.y
                x1, y1 = self.rod.end_node.x, self.rod.end_node.y
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            insert = (px, py)


        msp.add_blockref(block_name, insert=insert,
                         dxfattribs={
                             "layer": "Loads",
                         })
        text = f'{self.name} = {round_up(self.value)}'
        placement = (insert_point[0] + 0.1, insert_point[1] - 0.1)
        msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads",}).set_placement(placement)
        return msp

    def __repr__(self) -> str:
        return f"Momentum({self.name}={self.value} ---- {self.rotation}, node - {self.node.name})"


class DistributedForce(Load):
    """Создаем класс для распределенной нагрузки"""

    def __init__(self, name: str, value: float, rotation: int, rod: Rod | None = None,
                 start_coordinates: Tuple[float, float] | None = None, end_coordinates: Tuple[float, float] | None = None):
        self.name = name
        self.rod = rod
        self.value = float(value)
        self.rotation = int(rotation)

        if rod:
            self.start_coordinates = (self.rod.start_node.x, self.rod.start_node.y)
            self.end_coordinates = (self.rod.end_node.x, self.rod.end_node.y)
        else:
            self.start_coordinates = start_coordinates
            self.end_coordinates = end_coordinates

        if self.rotation in [90, 270]:
            dx = math.fabs(self.end_coordinates[0] - self.start_coordinates[0])
            self.length = round_up(dx)
        elif self.rotation in [0, 180]:
            dy = math.fabs(self.end_coordinates[1] - self.start_coordinates[1])
            self.length = round_up(dy)
        else:
            raise Exception("Направление распределенной нагрузки должно быть 0, 90, 180 или 270")

    def Q(self):
        return self.value * self.length

    def center(self) -> Tuple[float, float]:
        start_point = (self.start_coordinates[0], self.start_coordinates[1])
        end_point = (self.end_coordinates[0], self.end_coordinates[1])
        center_x = (start_point[0] + end_point[0]) / 2
        center_y = (start_point[1] + end_point[1]) / 2
        return center_x, center_y


    def get_projection_on_axis(self, axis_name: str) -> tuple:
        rotation_radians = math.radians(self.rotation)
        if axis_name == 'x':
            projection = self.Q() * math.cos(rotation_radians)
        elif axis_name == 'y':
            projection = self.Q() * math.sin(rotation_radians)
        else:
            raise Exception('Название оси должно быть \'x\' или \'y\'')
        projection = round(projection, 2)
        if projection >= 0:
            expression = f' + {self.name}·{self.length}'
        else:
            expression = f' - {self.name}·{self.length}'
        return projection, expression


    def get_lever_arm(self, point: Tuple[float, float]) -> float:
        """
        Определяет плечо силы относительно точки с учетом знака ("+" - по часовой, "-" - против часовой).

        Args:
            point: координата точки (x, y), относительно которой вычисляется момент

        Returns:
            float: moment_arm: плечо силы со знаком
        """

        # Вычисляем вектор от точки до точки приложения силы
        dx = point[0] - self.center()[0]
        dy = point[1] - self.center()[1]

        # Преобразуем угол силы в радианы
        angle_rad = math.radians(self.rotation)

        # Вычисляем компоненты вектора силы
        force_x = math.cos(angle_rad)
        force_y = math.sin(angle_rad)

        # Вычисляем плечо силы (векторное произведение радиус-вектора на вектор силы)
        # M = r × F = |r| * |F| * sin(θ)
        # В 2D: M = (dx * Fy - dy * Fx)
        moment_arm = dx * force_y - dy * force_x
        moment_arm = round_up(moment_arm, 3)
        return moment_arm

    def get_moment_about(self, point: Tuple[float, float]) -> tuple:
        lever_arm = self.get_lever_arm(point=point)
        moment = round_up(lever_arm * self.Q())
        if lever_arm >= 0:
            text = f' +{self.name}·{self.length}·{round_up(abs(lever_arm))}'
        else:
            text = f' -{self.name}·{self.length}·{round_up(abs(lever_arm))}'
        return text, moment

    def split_load_for_calculation_section(self):
        center_point = self.center()
        load1 = DistributedForce(name=self.name, rod=None, value=self.value, start_coordinates=self.start_coordinates,
                                 end_coordinates=center_point, rotation=self.rotation, )
        load2 = DistributedForce(name=self.name, rod=None, value=self.value, start_coordinates=center_point,
                                 end_coordinates=self.end_coordinates, rotation=self.rotation, )
        return [load1, load2]

    def draw(self, insert_point: Tuple[float, float], msp):
        msp.add_blockref('Распределенная нагрузка', insert=insert_point,
                         dxfattribs={
                             "layer": "Loads",
                             "rotation": self.rotation,
                             "yscale": self.length,
                         #     !!!!!!!!!!!!!!!!!!!!!!!!!! Тут нужно сделать взависимости от направления
                         })
        text = f'{self.name} = {self.value}'
        placement = (insert_point[0] + 0.5, insert_point[1])
        msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads",}).set_placement(placement)
        return msp

    def __repr__(self) -> str:
        return f"DistributedForce({self.name}={self.value} ---- {self.rotation}, rod - ({self.start_coordinates}:{self.end_coordinates}))"


class Twist(Load):
    """Создаем класс для поворота"""

    def __init__(self, name: str, node: Node, rotation: bool = True, value: float = 1):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = rotation
        self.x = node.x
        self.y = node.y

    def draw(self, insert_point: Tuple[float, float], msp, load_name: str | None = None):
        if self.rotation:
            block_name = 'Поворот (по часовой)'
        else:
            block_name = 'Поворот (против часовой)'

        msp.add_blockref(block_name, insert=insert_point,
                         dxfattribs={
                             "layer": "Loads",
                         })
        if not load_name:
            text = f'{self.name} = {self.value}'
        else:
            text = load_name
        placement = (insert_point[0] + 0.5, insert_point[1] - 0.4)
        msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads",}).set_placement(placement)
        return msp


    def __repr__(self) -> str:
        return f"Twist({self.name}={self.value} ---- {self.rotation}, node - {self.node.name})"


class Displacement(Load):
    """Создаем класс для сдвига"""

    def __init__(self, name: str, node: Node, rotation: int, value: float = 1):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = int(rotation)
        self.x = node.x
        self.y = node.y

    def find_relatives_nodes(self, frame):
        rods = frame.rods
        relative_nodes_coordinates = [(self.node.x, self.node.y)]

        if self.rotation in [90, 270]:
            while True:
                changed = False
                for rod in rods:
                    if rod.dx() == 0:
                        if (rod.start_node.x, rod.start_node.y) in relative_nodes_coordinates:
                            if (rod.end_node.x, rod.end_node.y) not in relative_nodes_coordinates:
                                relative_nodes_coordinates.append((rod.end_node.x, rod.end_node.y))
                                changed = True
                        elif (rod.end_node.x, rod.end_node.y) in relative_nodes_coordinates:
                            if (rod.start_node.x, rod.start_node.y) not in relative_nodes_coordinates:
                                relative_nodes_coordinates.append((rod.start_node.x, rod.start_node.y))
                                changed = True
                if not changed:
                    break
        elif self.rotation in [0, 180]:
            while True:
                changed = False
                for rod in rods:
                    if rod.dy() == 0:
                        if (rod.start_node.x, rod.start_node.y) in relative_nodes_coordinates:
                            if (rod.end_node.x, rod.end_node.y) not in relative_nodes_coordinates:
                                relative_nodes_coordinates.append((rod.end_node.x, rod.end_node.y))
                                changed = True
                        elif (rod.end_node.x, rod.end_node.y) in relative_nodes_coordinates:
                            if (rod.start_node.x, rod.start_node.y) not in relative_nodes_coordinates:
                                relative_nodes_coordinates.append((rod.start_node.x, rod.start_node.y))
                                changed = True
                if not changed:
                    break
        relative_nodes = []
        for node in frame.nodes:
            if (node.x, node.y) in relative_nodes_coordinates:
                relative_nodes.append(node)
        return relative_nodes

    def find_rods_with_impact_of_displacement(self, frame):
        rods_with_impact_of_displacement = []
        x = self.node.x
        y = self.node.y
        for rod in frame.rods:
            if self.rotation in [90, 270] and rod.dy() == 0 and rod.dx() != 0:
                if rod.start_node.x == x or rod.end_node.x == x:
                    rods_with_impact_of_displacement.append(rod)
            elif self.rotation in [0, 180] and rod.dx() == 0 and rod.dy() != 0:
                if rod.start_node.y == y or rod.end_node.y == y:
                    rods_with_impact_of_displacement.append(rod)
        return rods_with_impact_of_displacement


    def draw(self, insert_point: Tuple[float, float], msp, load_name: str | None = None):
        msp.add_blockref('Сдвиг', insert=insert_point,
                         dxfattribs={
                             "layer": "Loads",
                             "rotation": self.rotation,
                         })
        if not load_name:
            text = f'{self.name} = {self.value}'
        else:
            text = load_name

        # Рассчитываем вектор направления
        angle_rad = math.radians(self.rotation)
        direction = Vec2(math.cos(angle_rad), math.sin(angle_rad))

        # Вычисляем точку на конце стрелки
        tip_point = Vec2(insert_point) - direction * 1.4 + Vec2(0.1, 0.1)

        msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads",}).set_placement(tip_point)
        return msp


    def __repr__(self) -> str:
        return f"Displacement({self.name}={self.value} ---- {self.rotation}, node - {self.node.name})"

