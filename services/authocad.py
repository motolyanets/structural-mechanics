import math
from typing import List

from ezdxf.lldxf.const import HATCH_PATTERN_TYPE, HATCH_TYPE_PREDEFINED, HATCH_TYPE_CUSTOM
from ezdxf.math import Vec2

from core.mechanics.frame import Frame
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.solver import FrameForMovementMethod
from services.services import round_up

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


def draw_node(node: Node, base_point: List[float], msp, task_method: str, hinge_radius=h_r):
    if task_method not in ['fm', 'mm']:
        raise Exception('Неизвестный метод задачи')
    node_point = (node.x + base_point[0], node.y + base_point[1])

    if task_method == 'fm':
        try:
            int(node.name)
        except:
            placement = (node_point[0] + 0.2, node_point[1] + 0.2)
            msp.add_text(text=node.name, height=0.2, dxfattribs={"layer": "Node", }).set_placement(placement)
    elif task_method == 'mm':
        if node.name != '0':
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


def draw_rod(rod: Rod, base_point: List[float], msp, hinge_radius=h_r, drowing_stiffnes: bool | str = False):
    line = msp.add_line(
        start=(rod.start_node.x + base_point[0], rod.start_node.y + base_point[1]),
        end=(rod.end_node.x + base_point[0], rod.end_node.y + base_point[1]),
        dxfattribs={
            'layer': 'Rod',
            'lineweight': 30
        }
    )
    if drowing_stiffnes:
        rod_center = rod.middle()
        placement = (rod_center[0] + base_point[0] + 0.2, rod_center[1] + base_point[1] + 0.2)
        msp.add_text(text=f'{drowing_stiffnes}', height=0.2, dxfattribs={"layer": "Rod", "color": 2}).set_placement(placement)

    try:
        if rod.is_start_hinge:
            hinge_point = line.dxf.start
            direction_point = line.dxf.end
            drow_hinge(hinge_point, direction_point, msp)
        if rod.is_end_hinge:
            hinge_point = line.dxf.end
            direction_point = line.dxf.start
            drow_hinge(hinge_point, direction_point, msp)
    except:
        pass


def draw_section(rod: Rod, base_point: List[float], msp):
    if rod.sections:
        for section in rod.sections:
            section_point = (section.x_drawing + base_point[0], section.y_drawing + base_point[1])
            perpendicular_angle = find_perpendicular_angle(
                start_point=Vec2(rod.start_node.x, rod.start_node.y),
                end_point=Vec2(rod.end_node.x, rod.end_node.y)
            )

            msp.add_blockref('Сечение', insert=section_point,
                             dxfattribs={
                                 'layer': 'SECTIONS',
                                 'rotation': perpendicular_angle,
                             })

            msp.add_text(text=section.name, height=0.1, dxfattribs={'layer': 'SECTIONS', 'color': 1}).set_placement(section_point)
    return msp


def draw_frame(frame: Frame, base_point: List[float], msp, diagram_name: str = None, drawing_sections: bool = True,
               drawing_nodes: bool = True, drowing_stiffnes: bool = False, drowing_loads: bool = True, accuracy: int = 2):
    frame.base_point = base_point

    if drawing_nodes:
        for node in frame.nodes:
            if isinstance(frame, FrameForMovementMethod):
                task_method = 'mm'
            else:
                task_method = 'fm'
            draw_node(node, base_point, msp, task_method=task_method)

    for rod in frame.rods:
        if drowing_stiffnes:
            if isinstance(frame, FrameForMovementMethod):
                drowing_stiffnes_text = f'{round_up(rod.linear_stiffness,3)}·i'
            else:
                drowing_stiffnes_text = f'{rod.stiffness}·EI'

        draw_rod(rod=rod, base_point=base_point, msp=msp, drowing_stiffnes=drowing_stiffnes if not drowing_stiffnes else drowing_stiffnes_text)
        if drawing_sections:
            draw_section(rod=rod, base_point=base_point, msp=msp)
        if diagram_name:
            max_value = frame.find_max_value_on_diagram(diagram_name=diagram_name)
            scale = 2 / max_value
            diagram = rod.__getattribute__(f'diagram_{diagram_name}')
            if diagram_name.startswith('M'):
                draw_diagram_m(rod=rod, base_point=base_point, diagram=diagram, msp=msp, scale=scale, accuracy=accuracy)
            elif diagram_name.startswith('Q') or diagram_name.startswith('N'):
                if diagram:
                    draw_diagram_q(rod=rod, base_point=base_point, diagram=diagram, msp=msp, scale=scale, accuracy=accuracy)


    for support in frame.supports:
        insert_point = (support.node.x + base_point[0], support.node.y + base_point[1])
        msp = support.drow(insert_point, msp)

    if drowing_loads:
        if frame.loads:
            for load in frame.loads:
                if isinstance(load, (Force, Momentum, Twist, Displacement)):
                    insert_point = (load.node.x + base_point[0], load.node.y + base_point[1])
                    msp = load.drow(insert_point, msp)
                elif isinstance(load, DistributedForce):
                    insert_point = (load.center()[0] + base_point[0], load.center()[1] + base_point[1])
                    msp = load.drow(insert_point, msp)

        for reaction in frame.finded_reactions:
            insert_point = (reaction.node.x + base_point[0], reaction.node.y + base_point[1])
            msp = reaction.drow(insert_point, msp)


    base_point = [base_point[0] + frame.length() + 10, base_point[1]]
    return frame, msp, base_point


def draw_mm_diagram(frame: Frame, base_point: List[float], msp, diagram_name: str = None, drawing_sections: bool = True):
    frame.base_point = base_point

    for node in frame.nodes:
        draw_node(node, base_point, msp)

    for rod in frame.rods:
        draw_rod(rod=rod, base_point=base_point, msp=msp)
        if diagram_name:
            max_value = frame.find_max_value_on_diagram(diagram_name=diagram_name)
            scale = 2 / max_value
            diagram = rod.__getattribute__(f'diagram_{diagram_name}')
            if diagram_name.startswith('M'):
                draw_diagram_m(rod=rod, base_point=base_point, diagram=diagram, msp=msp, scale=scale)
            elif diagram_name.startswith('Q') or diagram_name.startswith('N'):
                if diagram:
                    draw_diagram_q(rod=rod, base_point=base_point, diagram=diagram, msp=msp, scale=scale)

    for support in frame.supports:
        insert_point = (support.node.x + base_point[0], support.node.y + base_point[1])
        msp = support.drow(insert_point, msp)

    if frame.loads:
        for load in frame.loads:
            if isinstance(load, (Force, Momentum, Twist, Displacement)):
                insert_point = (load.node.x + base_point[0], load.node.y + base_point[1])
                msp = load.drow(insert_point, msp)
            elif isinstance(load, DistributedForce):
                insert_point = (load.center()[0] + base_point[0], load.center()[1] + base_point[1])
                msp = load.drow(insert_point, msp)

    base_point = [base_point[0] + frame.length() + 10, base_point[1]]
    return frame, msp, base_point


def draw_node_with_inner_loads(frame: Frame, node_name:str, msp, is_drawing_m: bool = True, is_drawing_q: bool = True,
                               is_drawing_n: bool = True, truncate_length: float = 1):
    base_point = Vec2(frame.base_point[0], frame.base_point[1]) + Vec2(0, -15)
    node = None
    for frame_node in frame.nodes:
        if frame_node.name == node_name:
            node = frame_node
            break
    if not node:
        raise Exception(f'В раме {frame.name} нет узла {node_name}')

    rods_with_node = []
    for rod in frame.rods:
        if node in [rod.start_node, rod.end_node]:
            rods_with_node.append(rod)

    node_point = Vec2(node.x, node.y)
    for rod_with_node in rods_with_node:
        if rod_with_node.start_node == node:
            other_node = rod_with_node.end_node
        elif rod_with_node.end_node == node:
            other_node = rod_with_node.start_node
        else:
            raise Exception(f'Узел {node} не связан со стержнем {rod_with_node}')

        other_point = Vec2(other_node.x, other_node.y)
        direction = other_point - node_point
        direction_normalized = direction.normalize()
        end_point = node_point + direction_normalized * truncate_length

        line = msp.add_line(
            start=node_point + base_point,
            end=end_point + base_point,
            dxfattribs={
                'layer': 'Rod',
                'lineweight': 30
            }
        )

        dx = end_point[0] - node_point[0]
        dy = end_point[1] - node_point[1]
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        if is_drawing_m:
            if rod_with_node.diagram_M:
                if node == rod_with_node.start_node:
                    m = rod_with_node.diagram_M[0]
                    if m >= 0:
                        block_name = 'Момент по часовой (для вырезания узла)'
                    else:
                        block_name = 'Момент против часовой (для вырезания узла)'

                elif node == rod_with_node.end_node:
                    m = rod_with_node.diagram_M[-1]
                    if m >= 0:
                        block_name = 'Момент против часовой (для вырезания узла)'
                    else:
                        block_name = 'Момент по часовой (для вырезания узла)'


                msp.add_blockref(block_name, insert=end_point + base_point,
                                 dxfattribs={
                                     "layer": "Loads",
                                     'rotation': angle_deg,
                                 })
                text = f'{round_up(abs(m), 3)}'
                placement = end_point + base_point + direction_normalized * Vec2(0, -1)
                msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads", "color": 1}).set_placement(placement)
    return msp


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


def draw_diagram_m(rod: Rod, base_point: List[float], diagram: List[float], msp, scale: float = 1.0, accuracy: int = 2):
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
    points_on_rod = [start_point, end_point]
    if not diagram:
        return msp
    if len(diagram) == 3:
        mdl = rod.middle()
        middle_point = Vec2(mdl[0] + base_point[0], mdl[1] + base_point[1])
        points_on_rod = [start_point, middle_point, end_point]

    # Определяем вектор стержня и его длину
    rod_vector = end_point - start_point
    length = rod.length()

    if length < 1e-6:
        return  # Стержень нулевой длины

    # Определяем ориентацию стержня
    is_horizontal = abs(rod_vector.y) < 1e-6  # Горизонтальный
    is_vertical = abs(rod_vector.x) < 1e-6  # Вертикальный

    # Получаем значения моментов
    M_start = round_up(diagram[0], accuracy)
    M_end = round_up(diagram[-1], accuracy)



    # Определяем знаки и нормализуем значения
    # Для горизонтального стержня: + вверх, - вниз
    # Для вертикального стержня: + влево, - вправо

    # Рассчитываем локальные координаты для эпюры
    num_segments = 2  # Количество сегментов для интерполяции
    points = [start_point]

    for i, M in enumerate(diagram):
        # Определяем направление отступа
        if is_horizontal:
            # Для горизонтального стержня: положительный момент - вверх (увеличиваем y)
            offset_direction = Vec2(0, 1) if M >= 0 else Vec2(0, -1)
            offset_value = abs(M) * scale
            diagram_point = points_on_rod[i] + offset_direction * offset_value
        elif is_vertical:
            # Для вертикального стержня: положительный момент - влево (уменьшаем x)
            offset_direction = Vec2(-1, 0) if M >= 0 else Vec2(1, 0)
            offset_value = abs(M) * scale
            diagram_point = points_on_rod[i] + offset_direction * offset_value
        else:
            # Наклонный стержень: перпендикулярное направление
            # Нормализуем вектор стержня и находим перпендикуляр
            rod_dir = rod_vector.normalize()
            # Перпендикуляр (поворот на 90 градусов)
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            # Положительный момент в одну сторону, отрицательный - в другую
            offset_direction = perpendicular if M >= 0 else -perpendicular
            offset_value = abs(M) * scale
            diagram_point = points_on_rod[i] + offset_direction * offset_value

        points.append(diagram_point)
    points.append(end_point)

    # Рисуем эпюру как полилинию
    if len(points) > 1:
        polyline = msp.add_lwpolyline(points, dxfattribs={'layer': 'diagram M', 'color': 6, 'linetype': 'CONTINUOUS'})
        polyline.closed = True

    perpendicular_angle = find_perpendicular_angle(start_point=start_point, end_point=end_point)

    if rod.dx() == 0:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 1'})
    elif rod.dy() == 0:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 2'})
    else:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 3'})

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
        msp.add_text(f"{abs(M_start)}", dxfattribs={'layer': 'diagram M', 'height': 0.2, 'color': 6}).set_placement(text_point)

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
        msp.add_text(f"{abs(M_end)}", dxfattribs={'layer': 'diagram M', 'height': 0.2, 'color': 6}).set_placement(text_point)

    # Подпись в середине стержня
    if len(diagram) == 3:
        M_mdl = round_up(diagram[1], accuracy)
        if abs(M_mdl) > 0.01:
            if is_horizontal:
                offset_dir = Vec2(0, 1) if M_mdl >= 0 else Vec2(0, -1)
            elif is_vertical:
                offset_dir = Vec2(-1, 0) if M_mdl >= 0 else Vec2(1, 0)
            else:
                rod_dir = rod_vector.normalize()
                perpendicular = Vec2(-rod_dir.y, rod_dir.x)
                offset_dir = perpendicular if M_mdl >= 0 else -perpendicular

            text_point = middle_point + offset_dir * abs(M_mdl) * scale
            msp.add_text(f"{abs(M_mdl)}", dxfattribs={'layer': 'diagram M', 'height': 0.2, 'color': 6}).set_placement(text_point)

    return msp


def draw_diagram_q(rod: Rod, base_point: List[float], diagram: List[float], msp, scale: float = 1.0, accuracy: int = 2):
    """
    Отрисовка эпюры моментов.

    Args:
        rod: стержень с узлами (должен иметь start_node и end_node с атрибутами x, y)
        base_point: базовая точка рамы [x, y]
        diagram: список из двух значений [Q_start, Q_end] (начало и конец стержня)
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
    Q_start = round_up(diagram[0], accuracy)
    Q_end = round_up(diagram[-1], accuracy)

    # Определяем знаки и нормализуем значения
    # Для горизонтального стержня: + вверх, - вниз
    # Для вертикального стержня: + влево, - вправо

    # Рассчитываем локальные координаты для эпюры
    num_segments = 1  # Количество сегментов для интерполяции
    points = [start_point]

    for i in range(num_segments + 1):
        t = i / num_segments  # параметр от 0 до 1

        # Точка на стержне
        point_on_rod = start_point.lerp(end_point, t)

        # Интерполяция момента (линейная)
        Q = Q_start * (1 - t) + Q_end * t

        # Определяем направление отступа
        if is_horizontal:
            # Для горизонтального стержня: положительный момент - вверх (увеличиваем y)
            offset_direction = Vec2(0, 1) if Q >= 0 else Vec2(0, -1)
            offset_value = abs(Q) * scale
            diagram_point = point_on_rod + offset_direction * offset_value
        elif is_vertical:
            # Для вертикального стержня: положительный момент - влево (уменьшаем x)
            offset_direction = Vec2(-1, 0) if Q >= 0 else Vec2(1, 0)
            offset_value = abs(Q) * scale
            diagram_point = point_on_rod + offset_direction * offset_value
        else:
            # Наклонный стержень: перпендикулярное направление
            # Нормализуем вектор стержня и находим перпендикуляр
            rod_dir = rod_vector.normalize()
            # Перпендикуляр (поворот на 90 градусов)
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            # Положительный момент в одну сторону, отрицательный - в другую
            offset_direction = perpendicular if Q >= 0 else -perpendicular
            offset_value = abs(Q) * scale
            diagram_point = point_on_rod + offset_direction * offset_value

        points.append(diagram_point)
    points.append(end_point)

    # Рисуем эпюру как полилинию
    if len(points) > 1:
        polyline = msp.add_lwpolyline(points, dxfattribs={'layer': 'diagram Q', 'color': 6, 'linetype': 'CONTINUOUS'})
        polyline.closed = True

    perpendicular_angle = find_perpendicular_angle(start_point=start_point, end_point=end_point)

    if rod.dx() == 0:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 1'})
    elif rod.dy() == 0:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 2'})
    else:
        hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 3'})

    hatch.dxf.pattern_name = 'LINE'
    hatch.dxf.pattern_angle = perpendicular_angle
    hatch.dxf.pattern_scale = 0.05

    # Добавляем весь контур целиком
    hatch.paths.add_polyline_path(points, is_closed=True)

    # Рисуем базовую линию (стержень) для справки (опционально)
    # msp.add_line(start_point, end_point, dxfattribs={'color': 7, 'linetype': 'DASHED'})

    # Добавляем подписи значений (опционально)
    # Подпись в начале стержня
    if abs(Q_start) > 0.01:
        if is_horizontal:
            offset_dir = Vec2(0, 1) if Q_start >= 0 else Vec2(0, -1)
        elif is_vertical:
            offset_dir = Vec2(-1, 0) if Q_start >= 0 else Vec2(1, 0)
        else:
            rod_dir = rod_vector.normalize()
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            offset_dir = perpendicular if Q_start >= 0 else -perpendicular

        text_point = start_point + offset_dir * abs(Q_start) * scale
        msp.add_text(f"{Q_start}", dxfattribs={'layer': 'diagram Q', 'height': 0.2, 'color': 6}).set_placement(text_point)

    # Подпись в конце стержня
    if abs(Q_end) > 0.01:
        if is_horizontal:
            offset_dir = Vec2(0, 1) if Q_end >= 0 else Vec2(0, -1)
        elif is_vertical:
            offset_dir = Vec2(-1, 0) if Q_end >= 0 else Vec2(1, 0)
        else:
            rod_dir = rod_vector.normalize()
            perpendicular = Vec2(-rod_dir.y, rod_dir.x)
            offset_dir = perpendicular if Q_end >= 0 else -perpendicular

        text_point = end_point + offset_dir * abs(Q_end) * scale
        msp.add_text(f"{Q_end}", dxfattribs={'layer': 'diagram Q', 'height': 0.2, 'color': 6}).set_placement(text_point)

    return msp
