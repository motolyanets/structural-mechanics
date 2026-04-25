import math
from typing import List

from core.mechanics.frame import Frame
from core.mechanics.load import Force, Momentum, DistributedForce
from core.mechanics.node import Node
from core.mechanics.rod import Rod

h_r = 0.1

def drow_hinge(hinge_point, direction_point, msp, hinge_radius=h_r):
    # Вычисляем вектор направления линии
    dx = direction_point.x - hinge_point.x
    dy = direction_point.y - hinge_point.y
    dz = direction_point.z - hinge_point.z

    # Длина линии
    line_length = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

    if line_length > 0:
        # Нормализуем вектор
        dx /= line_length
        dy /= line_length
        dz /= line_length

        # Вычисляем точку на заданном расстоянии ОТ конца ВДОЛЬ линии
        circle_center = (
            hinge_point.x + dx * hinge_radius,
            hinge_point.y + dy * hinge_radius,
            hinge_point.z + dz * hinge_radius
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


def draw_node(node: Node, base_point: List[float], msp, hinge_radius=h_r):
    node_point = (node.x + base_point[0], node.y + base_point[1])
    try:
        int(node.name)
    except:
        placement = (node_point[0] + 0.2, node_point[1] + 0.2)
        msp.add_text(text=node.name, height=0.2, dxfattribs={"layer": "Node", }).set_placement(placement)

    if node.is_hinge:
        circle_radius = hinge_radius

        msp.add_circle(
            center=node_point,
            radius=circle_radius,
            dxfattribs={
                'layer': 'HINGE',
                'lineweight': 30
            }
        )


def draw_rod(rod: Rod, base_point: List[float], msp, hinge_radius=h_r):
    line = msp.add_line(
        start=(rod.start_node.x + base_point[0], rod.start_node.y + base_point[1]),
        end=(rod.end_node.x + base_point[0], rod.end_node.y + base_point[1]),
        dxfattribs={
            'layer': 'Rod',
            'lineweight': 30
        }
    )

    if rod.is_start_hinge:
        hinge_point = line.dxf.start
        direction_point = line.dxf.end
        drow_hinge(hinge_point, direction_point, msp)
    if rod.is_end_hinge:
        hinge_point = line.dxf.end
        direction_point = line.dxf.start
        drow_hinge(hinge_point, direction_point, msp)


def draw_frame(frame: Frame, base_point: List[float], msp):
    for node in frame.nodes:
        draw_node(node, base_point, msp)

    for rod in frame.rods:
        draw_rod(rod, base_point, msp)

    for support in frame.supports:
        insert_point = (support.node.x + base_point[0], support.node.y + base_point[1])
        msp = support.drow(insert_point, msp)

    for load in frame.loads:
        if isinstance(load, (Force, Momentum)):
            insert_point = (load.node.x + base_point[0], load.node.y + base_point[1])
            msp = load.drow(insert_point, msp)
        elif isinstance(load, DistributedForce):
            insert_point = (load.center()[0] + base_point[0], load.center()[1] + base_point[1])
            msp = load.drow(insert_point, msp)

    for reaction in frame.finded_reactions:
        insert_point = (reaction.node.x + base_point[0], reaction.node.y + base_point[1])
        msp = reaction.drow(insert_point, msp)


    print(f'Рама нарисована')
    base_point = [base_point[0] + 30, base_point[1]]
    return msp, base_point
