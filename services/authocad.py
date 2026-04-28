import math
from typing import List

from ezdxf.lldxf.const import HATCH_PATTERN_TYPE, HATCH_TYPE_PREDEFINED, HATCH_TYPE_CUSTOM
from ezdxf.math import Vec2

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


def draw_frame(frame: Frame, base_point: List[float], msp, diagram_name: str = None):
    frame.base_point = base_point

    for node in frame.nodes:
        draw_node(node, base_point, msp)

    for rod in frame.rods:
        draw_rod(rod, base_point, msp)
        if diagram_name:
            max_value = frame.find_max_value_diagram_m(diagram_name=diagram_name)
            scale = 2 / max_value
            diagram = rod.__getattribute__(f'diagram_M{diagram_name}')
            draw_diagram_m(rod=rod, base_point=base_point, diagram=diagram, msp=msp, scale=scale)

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
    return frame, msp, base_point


def find_perpendicular_angle(start_point: Vec2, end_point: Vec2) -> float:

    # Вычисляем угол перпендикуляра
    dx = end_point.x - start_point.x
    dy = end_point.y - start_point.y
    angle_deg = math.degrees(math.atan2(dy, dx))
    perpendicular_angle = (angle_deg + 90) % 180

    if perpendicular_angle < 0:
        perpendicular_angle += 180
    elif perpendicular_angle >= 180:
        perpendicular_angle -= 180

    return perpendicular_angle


def draw_diagram_m(rod: Rod, base_point: List[float], diagram: List[float], msp, scale: float = 1.0):
    """
    Отрисовка эпюры моментов.

    Args:
        rod: стержень с узлами (должен иметь start_node и end_node с атрибутами x, y)
        base_point: базовая точка рамы [x, y]
        diagram: список из двух значений [M_start, M_end] (начало и конец стержня)
        msp: пространство листа ezdxf (Model Space)
        scale: масштаб эпюры (коэффициент)
    """
    # Вычисляем глобальные координаты стержня
    start_point = Vec2(rod.start_node.x + base_point[0], rod.start_node.y + base_point[1])
    end_point = Vec2(rod.end_node.x + base_point[0], rod.end_node.y + base_point[1])

    # Определяем вектор стержня и его длину
    rod_vector = end_point - start_point
    length = rod.length()

    if length < 1e-6:
        return  # Стержень нулевой длины

    # Определяем ориентацию стержня
    is_horizontal = abs(rod_vector.y) < 1e-6  # Горизонтальный
    is_vertical = abs(rod_vector.x) < 1e-6  # Вертикальный

    # Получаем значения моментов
    M_start = diagram[0]
    M_end = diagram[1]

    # Определяем знаки и нормализуем значения
    # Для горизонтального стержня: + вверх, - вниз
    # Для вертикального стержня: + влево, - вправо

    # Рассчитываем локальные координаты для эпюры
    num_segments = 2  # Количество сегментов для интерполяции
    points = [start_point]

    for i in range(num_segments + 1):
        t = i / num_segments  # параметр от 0 до 1

        # Точка на стержне
        point_on_rod = start_point.lerp(end_point, t)

        # Интерполяция момента (линейная)
        M = M_start * (1 - t) + M_end * t

        # Определяем направление отступа
        if is_horizontal:
            # Для горизонтального стержня: положительный момент - вверх (увеличиваем y)
            offset_direction = Vec2(0, 1) if M >= 0 else Vec2(0, -1)
            offset_value = abs(M) * scale
            diagram_point = point_on_rod + offset_direction * offset_value
        elif is_vertical:
            # Для вертикального стержня: положительный момент - влево (уменьшаем x)
            offset_direction = Vec2(-1, 0) if M >= 0 else Vec2(1, 0)
            offset_value = abs(M) * scale
            diagram_point = point_on_rod + offset_direction * offset_value
        else:
            # Наклонный стержень: перпендикулярное направление
            # Нормализуем вектор стержня и находим перпендикуляр
            rod_dir = rod_vector.normalize()
            # Перпендикуляр (поворот на 90 градусов)
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            # Положительный момент в одну сторону, отрицательный - в другую
            offset_direction = perpendicular if M >= 0 else -perpendicular
            offset_value = abs(M) * scale
            diagram_point = point_on_rod + offset_direction * offset_value

        points.append(diagram_point)
    points.append(end_point)

    # Рисуем эпюру как полилинию
    if len(points) > 1:
        polyline = msp.add_lwpolyline(points, dxfattribs={'color': 3, 'linetype': 'CONTINUOUS'})
        polyline.closed = True

    perpendicular_angle = find_perpendicular_angle(start_point=start_point, end_point=end_point)

    hatch = msp.add_hatch(color=3)

    hatch.dxf.pattern_name = 'LINE'
    hatch.dxf.pattern_angle = perpendicular_angle
    hatch.dxf.pattern_scale = 0.05

    # Добавляем весь контур целиком
    hatch.paths.add_polyline_path(points, is_closed=True)

    # Рисуем базовую линию (стержень) для справки (опционально)
    # msp.add_line(start_point, end_point, dxfattribs={'color': 7, 'linetype': 'DASHED'})

    # Добавляем подписи значений (опционально)
    # Подпись в начале стержня
    if abs(M_start) > 0.01:
        if is_horizontal:
            offset_dir = Vec2(0, 1) if M_start >= 0 else Vec2(0, -1)
        elif is_vertical:
            offset_dir = Vec2(-1, 0) if M_start >= 0 else Vec2(1, 0)
        else:
            rod_dir = rod_vector.normalize()
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            offset_dir = perpendicular if M_start >= 0 else -perpendicular

        text_point = start_point + offset_dir * abs(M_start) * scale
        msp.add_text(f"{abs(M_start)}", dxfattribs={'height': 0.2, 'color': 3}).set_placement(text_point)

    # Подпись в конце стержня
    if abs(M_end) > 0.01:
        if is_horizontal:
            offset_dir = Vec2(0, 1) if M_end >= 0 else Vec2(0, -1)
        elif is_vertical:
            offset_dir = Vec2(-1, 0) if M_end >= 0 else Vec2(1, 0)
        else:
            rod_dir = rod_vector.normalize()
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            offset_dir = perpendicular if M_end >= 0 else -perpendicular

        text_point = end_point + offset_dir * abs(M_end) * scale
        msp.add_text(f"{abs(M_end)}", dxfattribs={'height': 0.2, 'color': 3}).set_placement(text_point)

    return msp

