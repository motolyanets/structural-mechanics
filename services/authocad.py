import math
from typing import List

import ezdxf as ezdxf

from data_base.frames import Node, Rod
from problem_condition import circuit_number

# Создаем новый DXF документ
doc = ezdxf.new('R2010')

# Получаем модель пространства
msp = doc.modelspace()


def drow_hinge(base_point, direction_point, hinge_radius, msp):
    # Вычисляем вектор направления линии
    dx = direction_point.x - base_point.x
    dy = direction_point.y - base_point.y
    dz = direction_point.z - base_point.z

    # Длина линии
    line_length = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    if line_length > 0:
        # Нормализуем вектор
        dx /= line_length
        dy /= line_length
        dz /= line_length

        # Вычисляем точку на заданном расстоянии ОТ конца ВДОЛЬ линии
        circle_center = (
            base_point.x + dx * hinge_radius,
            base_point.y + dy * hinge_radius,
            base_point.z + dz * hinge_radius
        )

        # Рисуем круг
        msp.add_circle(
            center=(circle_center[0], circle_center[1]),
            radius=hinge_radius,
            dxfattribs={
                'layer': 'CIRCLES',
                'lineweight': 30
            }
        )


def drow_frame(nodes: List[Node], rods: List[Rod], msp=msp):
    hinge_radius = 0.1

    for node in nodes:
        if node.is_hinge:
            circle_radius = hinge_radius

            center = (node.x, node.y)
            msp.add_circle(
                center=center,
                radius=circle_radius,
                dxfattribs={
                    'layer': 'CIRCLES',
                    'lineweight': 30
                }
            )

    for rod in rods:
        line = msp.add_line(
            start=(rod.start_node.x, rod.start_node.y),
            end=(rod.end_node.x, rod.end_node.y),
            dxfattribs={
                'layer': 'LINES',
                'lineweight': 30
            }
        )

        if rod.is_start_hinge:
            base_point = line.dxf.start
            direction_point = line.dxf.end
            drow_hinge(base_point, direction_point, hinge_radius, msp)
        if rod.is_end_hinge:
            base_point = line.dxf.end
            direction_point = line.dxf.start
            drow_hinge(base_point, direction_point, hinge_radius, msp)

    doc.saveas(f'{circuit_number}.dxf')
    print(f'Чертеж создан: {circuit_number}.dxf')
