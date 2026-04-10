import math
from typing import Tuple

from core.mechanics.node import Node
from core.mechanics.rod import Rod
from services.services import round_up


class Force:
    """Создаем класс для сосредоточенного усилия"""

    def __init__(self, name: str, node: Node, rotation: int, value: float | None = None):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = int(rotation)

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

        return moment_arm

    def get_moment_about(self, point: Tuple[float, float]) -> float:
        lever_arm = self.get_lever_arm(point=point)
        moment = round_up(lever_arm * self.value)
        text = f'{self.name} * {lever_arm}'
        return text, moment

    def get_projection_on_axis(self, axis_name: str) -> float:
        rotation_radians = math.radians(self.rotation)
        if axis_name == 'x':
            projection = self.value * math.cos(rotation_radians)
        elif axis_name == 'y':
            projection = self.value * math.sin(rotation_radians)
        else:
            raise Exception('Название оси должно быть \'x\' или \'y\'')
        projection = round(projection, 2)
        if projection >= 0:
            expression = f'+{self.name}'
        else:
            expression = f'-{self.name}'
        return projection, expression

    def __repr__(self) -> str:
        return f"Force({self.name}={self.value} ---- {self.rotation}, node - {self.node.name})"


class Momentum:
    """Создаем класс для момента"""

    def __init__(self, name: str, node: Node, rotation: bool, value: float | None = None):
        self.name = name
        self.node = node
        self.value = value
        self.rotation = rotation


class DistributedForce:
    """Создаем класс для распределенной нагрузки"""

    def __init__(self, name: str, rod: Rod, value: float, rotation: int):
        self.name = name
        self.rod = rod
        self.value = float(value)
        self.rotation = int(rotation)

        if self.rotation in [90, 270]:
            self.length = round_up(self.rod.dx())
        elif self.rotation in [0, 180]:
            self.length = round_up(self.rod.dy())
        else:
            raise Exception("Направление распределенной нагрузки должно быть 0, 90, 180 или 270")

    def Q(self):
        return self.value * self.length

    def center(self) -> Tuple[float, float]:
        start_point = (self.rod.start_node.x, self.rod.start_node.y)
        end_point = (self.rod.end_node.x, self.rod.end_node.y)
        center_x = (start_point[0] + end_point[0]) / 2
        center_y = (start_point[1] + end_point[1]) / 2
        return center_x, center_y


    def get_projection_on_axis(self, axis_name: str) -> float:
        rotation_radians = math.radians(self.rotation)
        if axis_name == 'x':
            projection = self.Q() * math.cos(rotation_radians)
        elif axis_name == 'y':
            projection = self.Q() * math.sin(rotation_radians)
        else:
            raise Exception('Название оси должно быть \'x\' или \'y\'')
        projection = round(projection, 2)
        if projection >= 0:
            expression = f'+{self.name}*{self.length}'
        else:
            expression = f'-{self.name}*{self.length}'
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

        return moment_arm

    def get_moment_about(self, point: Tuple[float, float]) -> float:
        lever_arm = self.get_lever_arm(point=point)
        moment = lever_arm * self.Q()
        return round_up(number=moment)
