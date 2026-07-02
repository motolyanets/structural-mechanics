import math
from typing import List, Tuple

from ezdxf import zoom, bbox
from ezdxf.lldxf.const import HATCH_PATTERN_TYPE, HATCH_TYPE_PREDEFINED, HATCH_TYPE_CUSTOM
from ezdxf.math import Vec2
from openpyxl import drawing

from core.mechanics.frame import Frame
from core.mechanics.load import Force, Momentum, DistributedForce, Twist, Displacement
from core.mechanics.node import Node
from core.mechanics.rod import Rod
from core.mechanics.solver import FrameForMovementMethod
from services.services import round_up

h_r = 0.1


def keep_only_layout(doc, layout_name_to_keep):
    """
    Сохраняет только указанный layout, удаляя все остальные.

    Args:
        input_path: исходный DXF файлу
        layout_name_to_keep: имя layout, который нужно оставить (например, "Layout1")
    """

    # Получаем все layouts (кроме модели)
    all_layouts = list(doc.layouts)

    layout_to_keep = doc.layouts.get(layout_name_to_keep)

    # Удаляем все layouts, кроме нужного
    for layout in all_layouts:
        if layout.name != layout_name_to_keep and not layout.is_modelspace:
            doc.layouts.delete(layout.name)
    return layout_to_keep


def draw_hinge(hinge_point: Node, direction_point, msp, hinge_radius=h_r):
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


def draw_hinge(node_point: Tuple[float, float], hinge_radius: float, msp):
    circle_radius = hinge_radius

    msp.add_circle(
        center=node_point,
        radius=circle_radius,
        dxfattribs={
            'layer': 'HINGE',
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
        draw_hinge(node_point=node_point, hinge_radius=hinge_radius, msp=msp)


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
            draw_hinge(hinge_point, direction_point, msp)
        if rod.is_end_hinge:
            hinge_point = line.dxf.end
            direction_point = line.dxf.start
            draw_hinge(hinge_point, direction_point, msp)
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

    for node in frame.nodes:
        if node.is_hinge:
            node_point = (node.x + base_point[0], node.y + base_point[1])
            draw_hinge(node_point=node_point, hinge_radius=h_r, msp=msp)

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
            if max_value != 0:
                scale = 2 / max_value
            else:
                scale = 1
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
                    msp = load.draw(insert_point, msp)
                elif isinstance(load, DistributedForce):
                    insert_point = (load.center()[0] + base_point[0], load.center()[1] + base_point[1])
                    msp = load.draw(insert_point, msp)

        for reaction in frame.finded_reactions:
            insert_point = (reaction.node.x + base_point[0], reaction.node.y + base_point[1])
            msp = reaction.draw(insert_point, msp)


    base_point = [base_point[0] + frame.length() + 10, base_point[1]]
    return frame, msp, base_point


def draw_dimension_chains(frame: Frame, base_point: List[float], msp, offset=1):
    """
    Создает цепочки линейных размеров снизу и справа от рамы.

    Args:
        frame: Рама
        msp: пространство листа
        offset: расстояние от крайних точек рамы до размерной линии
        text_height: высота текста размеров
    """
    nodes = frame.nodes

    # Извлекаем координаты узлов
    points = [(node.x + base_point[0], node.y + base_point[1]) for node in nodes]

    # Находим границы рамы
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    points_x = []
    points_y = []
    for point in points:
        if point not in points_x:
            points_x.append((point[0], min_y))
        if point not in points_y:
            points_y.append((max_x, point[1]))


    # ============================================
    # 1. Нижняя размерная цепь (горизонтальные размеры)
    # ============================================
    # Сортируем точки по X для нижней цепи
    bottom_points = sorted(points_x, key=lambda p: p[0])

    # Y-координата для нижней размерной линии
    dim_y = min_y - offset

    # Проходим по всем точкам снизу (по X)
    for i in range(len(bottom_points) - 1):
        x1 = bottom_points[i][0]
        x2 = bottom_points[i + 1][0]
        y = bottom_points[i][1]  # используем Y точки для выноски

        # Создаем размер между соседними точками по X
        create_linear_dimension(
            msp=msp,
            x1=x1, y1=y,
            x2=x2, y2=y,
            dim_line_y=dim_y,
            text=str(round(abs(x2 - x1), 2))
        )

    # ============================================
    # 2. Правая размерная цепь (вертикальные размеры)
    # ============================================
    # Сортируем точки по Y для правой цепи
    right_points = sorted(points_y, key=lambda p: p[1])

    # X-координата для правой размерной линии
    dim_x = max_x + offset

    # Проходим по всем точкам справа (по Y)
    for i in range(len(right_points) - 1):
        x = right_points[i][0]  # используем X точки для выноски
        y1 = right_points[i][1]
        y2 = right_points[i + 1][1]

        # Создаем размер между соседними точками по Y
        create_linear_dimension(
            msp=msp,
            x1=x, y1=y1,
            x2=x, y2=y2,
            dim_line_x=dim_x,
            text=str(round(abs(y2 - y1), 2))
        )


def create_linear_dimension(msp, x1, y1, x2, y2, dim_line_y=None, dim_line_x=None, text=None, dimstyle='ISO-25'):
    """
    Создает один линейный размер.
    """
    # Проверяем, что точки не совпадают
    if abs(x1 - x2) < 0.001 and abs(y1 - y2) < 0.001:
        return None

    # Создаем размер
    if dim_line_y is not None:
        # Горизонтальный размер
        dim = msp.add_linear_dim(
            p1=(x1, y1),
            p2=(x2, y2),
            base=(x1, dim_line_y),  # ← здесь base вместо location
            dimstyle=dimstyle
        )
    elif dim_line_x is not None:
        # Вертикальный размер
        dim = msp.add_linear_dim(
            p1=(x1, y1),
            p2=(x2, y2),
            base=(dim_line_x, y1),  # ← здесь base вместо location
            angle=90,
            dimstyle=dimstyle
        )
    else:
        # Автоматическое определение
        dim_y = min(y1, y2) - 10
        dim = msp.add_linear_dim(
            p1=(x1, y1),
            p2=(x2, y2),
            base=(x1, dim_y),  # ← здесь base вместо location
            dimstyle=dimstyle
        )

    return dim


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
                msp = load.draw(insert_point, msp)
            elif isinstance(load, DistributedForce):
                insert_point = (load.center()[0] + base_point[0], load.center()[1] + base_point[1])
                msp = load.draw(insert_point, msp)

    base_point = [base_point[0] + frame.length() + 10, base_point[1]]
    return frame, msp, base_point


def get_direction_of_rod(base_node: Node, rod: Rod) -> Vec2:
    node_point = Vec2(base_node.x, base_node.y)
    if rod.start_node == base_node:
        other_node = rod.end_node
    elif rod.end_node == base_node:
        other_node = rod.start_node
    else:
        raise Exception(f'Узел {base_node} не связан со стержнем {rod}')

    other_point = Vec2(other_node.x, other_node.y)
    direction = other_point - node_point
    return direction


def draw_node_with_inner_loads(frame: Frame, node_name:str, msp, n_base_point: Vec2 | None, is_drawing_m: bool = True, is_drawing_q: bool = True,
                               is_drawing_n: bool = True, truncate_length: float = 1):
    if not n_base_point:
        n_base_point = Vec2(frame.base_point[0], frame.base_point[1]) + Vec2(0, -20)
    else:
        n_base_point = n_base_point + Vec2(0, -10)

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
        direction = get_direction_of_rod(base_node=node, rod=rod_with_node)
        direction_normalized = direction.normalize()
        end_point = node_point + direction_normalized * truncate_length

        line = msp.add_line(
            start=node_point + n_base_point,
            end=end_point + n_base_point,
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


                msp.add_blockref(block_name, insert=end_point + n_base_point,
                                 dxfattribs={
                                     "layer": "Loads",
                                     'rotation': angle_deg,
                                 })
                text = f'{round_up(abs(m), 3)}'
                if direction_normalized == Vec2(1, 0):
                    offset = Vec2(0, 0.4)
                elif direction_normalized == Vec2(0, 1):
                    offset = Vec2(0.4, 0.2)
                elif direction_normalized == Vec2(-1, 0):
                    offset = Vec2(-0.6, -0.6)
                elif direction_normalized == Vec2(0, -1):
                    offset = Vec2(0.4, -0.4)
                else:
                    offset = Vec2(0.1, -0.1)
                placement = end_point + n_base_point + offset
                msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads", "color": 1}).set_placement(placement)
        if is_drawing_q:
            if rod_with_node.diagram_Q:
                if node == rod_with_node.start_node:
                    q = rod_with_node.diagram_Q[0]
                elif node == rod_with_node.end_node:
                    q = rod_with_node.diagram_Q[-1]

                text = f'{round_up(abs(q), 3)}'

                if direction_normalized == Vec2(1, 0):
                    offset = Vec2(0.5, -0.6)
                elif direction_normalized == Vec2(0, 1):
                    offset = Vec2(0.4, 0.6)
                elif direction_normalized == Vec2(-1, 0):
                    offset = Vec2(-0.9, 0.5)
                elif direction_normalized == Vec2(0, -1):
                    offset = Vec2(0.4, -0.8)
                else:
                    offset = direction_normalized * 0.7

                if q >= 0:
                    q_angle = angle_deg - 90
                else:
                    q_angle = angle_deg + 90

                msp.add_blockref('сила Q', insert=end_point + n_base_point + direction_normalized * 0.7,
                                 dxfattribs={
                                     "layer": "Loads",
                                     'rotation': q_angle,
                                 })

                placement = end_point + n_base_point + offset
                msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads", "color": 5}).set_placement(placement)
        if is_drawing_n:
            if rod_with_node.diagram_N:
                if node == rod_with_node.start_node:
                    n = rod_with_node.diagram_N[0]
                elif node == rod_with_node.end_node:
                    n = rod_with_node.diagram_N[-1]

                text = f'{round_up(abs(n), 3)}'

                if direction_normalized == Vec2(1, 0):
                    offset = Vec2(1, 0.15)
                elif direction_normalized == Vec2(0, 1):
                    offset = Vec2(0.15, 1.2)
                elif direction_normalized == Vec2(-1, 0):
                    offset = Vec2(-1.55, -0.35)
                elif direction_normalized == Vec2(0, -1):
                    offset = Vec2(0.15, -1.3)
                else:
                    offset = direction_normalized * 1.2
                if n >= 0:
                    n_angle = angle_deg
                else:
                    if angle_deg in [0, 180]:
                        n_angle = angle_deg - 180
                    else:
                        n_angle = -angle_deg
                msp.add_blockref('сила N', insert=end_point + n_base_point + direction_normalized * 1.2,
                                 dxfattribs={
                                     "layer": "Loads",
                                     'rotation': n_angle,
                                 })

                placement = end_point + n_base_point + offset
                msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads", "color": 3}).set_placement(placement)
    return msp, n_base_point


def draw_displacement_finding(frame: Frame, displacement: Displacement, msp, n_base_point: Vec2 | None, truncate_length: float = 1):
    if not n_base_point:
        n_base_point = Vec2(frame.base_point[0], frame.base_point[1]) + Vec2(0, -20)
    else:
        n_base_point = n_base_point + Vec2(0, -15)

    relatives_nodes = displacement.find_relatives_nodes(frame)
    relatives_nodes.append(displacement.node)
    rods_with_impact_of_displacement = displacement.find_rods_with_impact_of_displacement(frame=frame)

    for rod in frame.rods:
        if rod.start_node in relatives_nodes and rod.end_node in relatives_nodes:
            draw_rod(rod=rod, base_point=[n_base_point[0], n_base_point[1]], msp=msp)

    for node in relatives_nodes:
        if node.is_hinge:
            msp.add_circle(
                center=(node.x + n_base_point[0], node.y + n_base_point[1]),
                radius=h_r,
                dxfattribs={
                    'layer': 'CIRCLES',
                    'lineweight': 30
                }
            )

    for load in frame.loads:
        if isinstance(load, Force):
            if load.rotation in [0, 180] and displacement.rotation in [0, 180]:
                if load.node in relatives_nodes:
                    insert_point = (load.node.x + n_base_point[0], load.node.y + n_base_point[1])
                    load.draw(insert_point=insert_point, msp=msp)

    for rod in rods_with_impact_of_displacement:
        base_node = None
        if displacement.rotation in [0, 180]:
            if rod.start_node.y == displacement.node.y:
                base_node = rod.start_node
            elif rod.end_node.y == displacement.node.y:
                base_node = rod.end_node
        elif displacement.rotation in [90, 270]:
            if rod.start_node.x == displacement.node.x:
                base_node = rod.start_node
            elif rod.end_node.x == displacement.node.x:
                base_node = rod.end_node
        if not base_node:
            raise Exception(f'Узел {base_node} не связан со стержнем {rod}')
        node_point = Vec2(base_node.x, base_node.y)
        direction = get_direction_of_rod(base_node=base_node, rod=rod)
        direction_normalized = direction.normalize()
        end_point = node_point + direction_normalized * truncate_length

        line = msp.add_line(
            start=node_point + n_base_point,
            end=end_point + n_base_point,
            dxfattribs={
                'layer': 'Rod',
                'lineweight': 30
            }
        )

        dx = end_point[0] - node_point[0]
        dy = end_point[1] - node_point[1]
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        if rod.diagram_Q:
            if direction_normalized in [Vec2(1, 0), Vec2(0, 1)]:
                q = rod.diagram_Q[0]
                offset = direction_normalized * 0.5
            elif direction_normalized in [Vec2(-1, 0), Vec2(0, -1)]:
                q = rod.diagram_Q[-1]
                offset = direction_normalized * 0.5
            else:
                offset = direction_normalized * 0.2

            if q >= 0:
                q_angle = angle_deg - 90
            else:
                q_angle = angle_deg + 90

            msp.add_blockref('сила Q', insert=end_point + n_base_point + direction_normalized * 0.2,
                             dxfattribs={
                                 "layer": "Loads",
                                 'rotation': q_angle,
                             })
            text = f'{round_up(abs(q), 3)}'
            placement = end_point + n_base_point + offset
            msp.add_text(text=text, height=0.2, dxfattribs={"layer": "Loads", "color": 5}).set_placement(placement)

    return msp, n_base_point


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


def sample_spline(spline_points: List, num_points=100, direction_x0: bool = False):
    """
    Дискретизирует сплайн (поддерживает и fit_points, и control_points).
    """
    p0 = spline_points[0]
    p1 = spline_points[1]
    p2 = spline_points[2]

    if not direction_x0:
        (x1, y1), (x2, y2), (x3, y3) = (p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1])
    else:
        (x1, y1), (x2, y2), (x3, y3) = (p0[1], p0[0]), (p1[1], p1[0]), (p2[1], p2[0])

    # 1. Находим коэффициенты a, b, c через определители (правило Крамера)
    # Системы уравнений:
    # a*x1^2 + b*x1 + c = y1
    # a*x2^2 + b*x2 + c = y2
    # a*x3^2 + b*x3 + c = y3

    denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
    if denom == 0:
        raise ValueError("Точки не должны лежать на одной вертикальной линии (X должны отличаться).")

    a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
    b = (x3 ** 2 * (y1 - y2) + x2 ** 2 * (y3 - y1) + x1 ** 2 * (y2 - y3)) / denom
    c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom

    # 2. Генерируем точки с равным шагом по X от x1 до x3
    points = []
    start_x = x1
    end_x = x3

    for i in range(num_points + 1):
        # Равномерный шаг от start_x до end_x
        x = start_x + (end_x - start_x) * (i / num_points)
        # Считаем y по точной формуле параболы
        y = a * x ** 2 + b * x + c
        if not direction_x0:
            points.append((round(x, 4), round(y, 4)))

        else:
            points.append((round(y, 4), round(x, 4)))
    return points


def draw_diagram_between_two_lines(rod_line_points: List, diagram_line_points: List, angle: float, msp):
    p1 = [rod_line_points[0][0], rod_line_points[0][1]]
    p2 = [rod_line_points[-1][0], rod_line_points[-1][1]]
    rod_points = [p1, p2]
    hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 1'})
    hatch.set_pattern_fill("ANSI31", scale=0.05, color=3, angle=angle)

    if len(diagram_line_points) == 3:
        direction_x0 = False
        if rod_points[0][0] == rod_points[1][0]:
            direction_x0 = True
        diagram_line_points = sample_spline(spline_points=diagram_line_points, direction_x0=direction_x0)

    path_points = []

    # Добавляем точки полилинии (в прямом порядке)
    path_points.extend(rod_points)

    # Добавляем точки сплайна (в обратном порядке)
    path_points.extend(reversed(diagram_line_points))

    # Замыкаем контур (добавляем первую точку в конец)
    if path_points:
        path_points.append(path_points[0])

    path_polyline = msp.add_lwpolyline(path_points,
                                       dxfattribs={'layer': 'diagram M', 'color': 6, 'linetype': 'CONTINUOUS'})
    path_polyline.closed = True

    hatch.paths.add_polyline_path(path_points, is_closed=True)


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

    diagram_points = []
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
        diagram_points.append(diagram_point)

    perpendicular_angle = find_perpendicular_angle(start_point=start_point, end_point=end_point)

    draw_diagram_between_two_lines(rod_line_points=points_on_rod, diagram_line_points=diagram_points, angle=perpendicular_angle-45, msp=msp)

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
    points_on_rod = [start_point, end_point]

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
    diagram_points = []

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
        diagram_points.append(diagram_point)

    perpendicular_angle = find_perpendicular_angle(start_point=start_point, end_point=end_point)

    draw_diagram_between_two_lines(rod_line_points=points_on_rod, diagram_line_points=diagram_points, angle=perpendicular_angle-45, msp=msp)

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


def safe_zoom_for_work(doc):
    """
    Безопасный zoom для чертежей с проблемными размерами.
    """
    msp = doc.modelspace()

    # Получаем все объекты, исключая размеры
    all_entities = list(msp)
    filtered = []

    for e in all_entities:
        # Пропускаем все типы размеров
        if e.dxftype() in ('DIMENSION', 'DIMLINEAR', 'DIMALIGNED',
                           'DIMRADIUS', 'DIMDIAMETER', 'DIMANGULAR'):
            continue
        filtered.append(e)

    if not filtered:
        print("Нет объектов для zoom")
        return

    try:
        # Вычисляем габариты
        ext = bbox.extents(filtered, fast=True)
        if ext:
            # Получаем минимальные и максимальные координаты
            min_x, min_y, min_z = ext.extmin
            max_x, max_y, max_z = ext.extmax

            # Вычисляем центр и размеры
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            width = max_x - min_x
            height = max_y - min_y

            # Добавляем отступ (10%)
            margin = 0.1
            width *= (1 + margin)
            height *= (1 + margin)

            # Используем zoom.center для установки вида
            zoom.center(msp, (center_x, center_y), (width, height))
        else:
            print("⚠️ Не удалось вычислить габариты")
            # Пробуем стандартный zoom
            try:
                zoom.extents(msp)
            except:
                pass
    except Exception as e:
        print(f"❌ Ошибка zoom: {e}")
        # Пробуем стандартный zoom как запасной вариант
        try:
            zoom.extents(msp)
        except:
            print("❌ Не удалось выполнить zoom")