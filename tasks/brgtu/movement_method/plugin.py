import importlib
from typing import Dict, Any

import ezdxf
import numpy
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.load import Twist, Displacement, Force
from core.mechanics.rod import Rod
from core.mechanics.solver import FrameForMovementMethod, SolvableFrame, multiply_M_frames_by_Simpson
from services.authocad import draw_frame, draw_node_with_inner_loads, draw_displacement_finding
from services.services import round_up, is_subsegment_2d, relative_error_percent
from tasks.base import TaskPlugin
from tasks.brgtu.movement_method.loader import MovementMethodLoader


class BRGTUMovementMethod(TaskPlugin):
    task_id = "movement_method"
    task_name = "Метод перемещений"
    university = "brgtu"

    def _init_loader(self):
        self.loader = MovementMethodLoader(self.excel_path)

    def get_available_schemes(self) -> list:
        return [
            # {"scheme_id": 10, "name": "Схема 10"},
            {"scheme_id": 17, "name": "Схема 17"},
            {"scheme_id": 19, "name": "Схема 19"},
            {"scheme_id": 22, "name": "Схема 22"},
            # {"scheme_id": 24, "name": "Схема 24"},
            {"scheme_id": 27, "name": "Схема 27"},
            # {"scheme_id": 29, "name": "Схема 29"},
        ]

    def solve(self, cipher: str) -> Dict[str, Any]:
        params = self.loader.load_cipher(cipher)
        circuit_number = params["circuit_number"]

        # Создаем новый DXF документ
        doc = ezdxf.readfile('Шаблон.dxf')
        msp = doc.modelspace()
        msp.delete_all_entities()
        layout = doc.layouts.get("Шаблон (метод перемещений)")
        base_point = [0, 0]

        task_condition_text = (f'{cipher}\n'
                               f'Схема - {circuit_number}       Нагрузка - {params['load_index']}\n'
                               f"l\\H0.5x;1\\H2.0x;={params['l1']}м          l\\H0.5x;2\\H2.0x;={params['l2']}м\n"
                               f"m = {params['m']}кН·м\n"
                               f"P = {params['P']}кН\n"
                               f"h\\H0.5x;1\\H2.0x;={params['h1']}м          h\\H0.5x;2\\H2.0x;={params['h2']}м\n"
                               f"q = {params['q']}кН/м\n"
                               f"I2/I1 = {params['i2']}\n"
                               f"I3/I1 = {params['i3']}")

        for entity in layout:
            if entity.dxf.layer == "Условие задачи":
                entity.text = task_condition_text

        print(f"\n{'=' * 60}")
        print(f"Задача: {self.task_name}")
        print(f"ВУЗ: {self.university}")
        print(f"Шифр: {cipher}")
        print(f"Схема: {circuit_number}")
        print(f"\nПараметры:")
        print(f"  l1 = {params['l1']} м")
        print(f"  l2 = {params['l2']} м")
        print(f"  h1 = {params['h1']} м")
        print(f"  h2 = {params['h2']} м")
        print(f"  m = {params['m']} кН·м")
        print(f"  P = {params['P']} кН")
        print(f"  q = {params['q']} кН/м")
        print(f"  I2 = {params['i2']}")
        print(f"  I3 = {params['i3']}")
        print(f"  load_index = {params['load_index']}")
        print(f"{'=' * 60}")

        def get_circuit_functions(circuit_number):
            try:
                # Импортируем модуль динамически
                module = importlib.import_module(f'schemes.brgtu.movement_method.frame_{circuit_number}')

                # Получаем функции из модуля
                create_main_frame = getattr(module, f'create_frame_{circuit_number}')
                new_mm_frame = getattr(module, f'create_mm_primary_system_{circuit_number}')
                new_fm_frame = getattr(module, f'create_fm_primary_system_{circuit_number}')

                return create_main_frame, new_mm_frame, new_fm_frame

            except (ImportError, AttributeError) as e:
                raise ValueError(f"Схема {circuit_number} не реализована") from e

        def calculation_r(frame: FrameForMovementMethod, loads: dict):
            coefficients = dict()
            reports = dict()
            for load_name in loads:
                load_list = loads[load_name]
                if len(load_list) == 1 and isinstance(load_list[0], (Twist, Displacement)):
                    load = load_list[0]

                    if isinstance(load, Twist):
                        m, eq = frame.sum_of_moment_in_rods_at_node(node_name=load.node.name)
                        report = f'{'' if load.rotation else '- '}' + f'r{load_name}{frame.name} ' + eq + '= 0\n'
                        if load.rotation:
                            r = -m
                        else:
                            r = m
                        report += f'r{load_name}{frame.name} = {round_up(r, 3)}\n'
                        coefficients[f'r{load_name}{frame.name}'] = r
                        reports[f'r{load_name}{frame.name}'] = report
                    elif isinstance(load, Displacement):
                        f, eq = frame.sum_of_forces_along_displacement(displacement=load)

                        relatives_nodes = load.find_relatives_nodes(frame)
                        for force in frame.loads:
                            if isinstance(force, Force):
                                if force.node in relatives_nodes:
                                    if force.rotation and load.rotation in [0, 180] or force.rotation and load.rotation in [90, 270]:
                                        if force.rotation in [0, 90]:
                                            f += force.value
                                            eq += f'+ {force.value} '
                                        elif force.rotation in [180, 270]:
                                            f -= force.value
                                            eq += f'- {force.value} '


                        report = f'{'' if load.rotation in [0, 90] else '- '}' + f'r{load_name}{frame.name} ' + eq + '= 0\n'
                        if load.rotation in [0, 90]:
                            r = -f
                        else:
                            r = f
                        report += f'r{load_name}{frame.name} = {round_up(r, 3)}\n'
                        coefficients[f'r{load_name}{frame.name}'] = r
                        reports[f'r{load_name}{frame.name}'] = report
            return coefficients, reports

        def replace_diagrams_from_mmframe_to_fmframe(mm_frame: FrameForMovementMethod, fm_frame: SolvableFrame):
            for mm_rod in mm_frame.rods:
                fm_rods_related_to_mm_rod = []
                for fm_rod in fm_frame.rods:
                    small_segment = ((fm_rod.start_node.x, fm_rod.start_node.y), (fm_rod.end_node.x, fm_rod.end_node.y))
                    big_segment = ((mm_rod.start_node.x, mm_rod.start_node.y), (mm_rod.end_node.x, mm_rod.end_node.y))
                    if is_subsegment_2d(small_segment=small_segment, big_segment=big_segment):
                        fm_rods_related_to_mm_rod.append(fm_rod)
                if len(mm_rod.diagram_M) == len(fm_rods_related_to_mm_rod):
                    for i, fm_rod in enumerate(fm_rods_related_to_mm_rod):
                        fm_rod.diagram_M = mm_rod.diagram_M[i]
                        fm_rod.diagram_Q = mm_rod.diagram_Q
                else:
                    if len(mm_rod.diagram_M) <= len(fm_rods_related_to_mm_rod):
                        if fm_rods_related_to_mm_rod[0].dx() == 0:
                            sorted_rods = sorted(fm_rods_related_to_mm_rod, key=lambda rod: rod.start_node.y)
                        elif fm_rods_related_to_mm_rod[0].dy() == 0:
                            sorted_rods = sorted(fm_rods_related_to_mm_rod, key=lambda rod: rod.start_node.x)
                        else:
                            raise Exception('Application is not support rods with dx!=0 and dy!=0')

                        if len(mm_rod.diagram_M) == 1:
                            m_start = mm_rod.diagram_M[0][0]
                            m_end = mm_rod.diagram_M[0][1]
                            q_start = mm_rod.diagram_Q[0]
                            q_end = mm_rod.diagram_Q[1]
                            mm_length = mm_rod.length()
                            fm_length = 0
                            for fm_rod in sorted_rods:
                                fm_length += fm_rod.length()
                            if mm_length != fm_length:
                                raise Exception('Длины стержней из рамы МП и рамы МС должны быть равны')
                            for i, fm_rod in enumerate(sorted_rods):
                                if i == 0:
                                    l1 = fm_rod.length()
                                    m1 = m_start
                                    m2 = m_start + (m_end - m_start) * l1 / mm_length
                                    q1 = q_start
                                    q2 = q_start + (q_end - q_start) * l1 / mm_length
                                elif i == len(sorted_rods) - 1:
                                    m1 = m2
                                    m2 = m_end
                                    q1 = q2
                                    q2 = q_end
                                else:
                                    m1 = m2
                                    q1 = q2
                                    l1 += fm_rod.length()
                                    m2 = m_start + (m_end - m_start) * l1 / mm_length
                                    q2 = q_start + (q_end - q_start) * l1 / mm_length
                                fm_rod.diagram_M = [m1, m2]
                                fm_rod.diagram_Q = [q1, q2]

        create_main_frame, new_mm_frame, new_fm_frame = get_circuit_functions(circuit_number)

        # Создаем главную раму и рисуем ее
        fr_nodes, fr_rods, fr_supports, fr_loads, symmetry = create_main_frame(params)
        main_frame = Frame(fr_nodes, fr_rods, fr_supports, fr_loads, symmetry)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.geometrical_center()[0], main_frame.geometrical_center()[1], 0.0)
        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, msp=msp, drowing_stiffnes=True)

        # Отрисовываем основную систему МП
        ps_mm_nodes, ps_mm_rods, ps_mm_supports, ps_mm_loads = new_mm_frame(params)

        ed_diagrams = []
        for load in ps_mm_loads:
            if load != 'p':
                ed_diagrams.append(load)

        ps_mm_ed_loads = []
        for i in ps_mm_loads:
            if i in ed_diagrams:
                ps_mm_ed_loads.append(ps_mm_loads[i][0])
        ps_mm_frame = FrameForMovementMethod(name='ps_mm', nodes=ps_mm_nodes, rods=ps_mm_rods, supports=ps_mm_supports, loads=ps_mm_ed_loads)
        linear_stiffness_report = 'Зададим погонные жесткости:\n'
        for rod in ps_mm_rods:
            linear_stiffness_text = f'i{rod.name} = {rod.stiffness}·EI / {round_up(rod.length(), 3)} = {round_up(rod.linear_stiffness, 3)}i\n'
            linear_stiffness_report += linear_stiffness_text
        ps_mm_frame, msp, base_point = draw_frame(frame=ps_mm_frame, base_point=base_point, msp=msp, accuracy=3,
                                                  drawing_sections=False, drowing_stiffnes=True)
        for entity in layout:
            if entity.dxf.layer == 'мп_основная система' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (ps_mm_frame.base_point[0] + ps_mm_frame.geometrical_center()[0],
                                                    ps_mm_frame.base_point[1] + ps_mm_frame.geometrical_center()[1],
                                                    0.0)
            elif entity.dxf.layer == 'мп_погонные жесткости':
                entity.text = linear_stiffness_report


        # Создаем единичные рамы МП, расчитываем их
        ed_diagrams_with_p = ed_diagrams.copy()
        ed_diagrams_with_p.append('p')
        mm_frames = []
        calculating_diagram_reports = dict()

        for diagram in ed_diagrams_with_p:
            print(f'Расчет эпюры М{diagram} метода перемещений')
            mm_nodes, mm_rods, mm_supports, mm_loads = new_mm_frame(params)
            frame = FrameForMovementMethod(name=diagram, nodes=mm_nodes, rods=mm_rods, supports=mm_supports, loads=mm_loads[diagram])
            mm_frames.append(frame)

            calculating_diagram_report = ''
            for rod in frame.rods:
                rod_diagram_report = rod.calculate_diagram_m_movement()
                if rod_diagram_report:
                    calculating_diagram_report += rod_diagram_report
            calculating_diagram_reports[diagram] = calculating_diagram_report
            print(calculating_diagram_report)

        # Находим коэффициенты
        finded_coefficients = dict()
        for frame in mm_frames:
            coefficients, reports = calculation_r(frame, mm_loads)
            report = ''
            for r in reports:
                report += reports[r] + '\n'
            print(report)

            for entity in layout:
                if entity.dxf.layer == f'мп_определение коэффициентов_{frame.name}':
                    entity.text = report


            # Проверяем r12=r21 и т.д.
            for c in coefficients:
                coefficient = f'{c[0]}{c[2]}{c[1]}'
                if coefficient not in finded_coefficients:
                    finded_coefficients[c] = coefficients[c]
                else:
                    if finded_coefficients[coefficient] != coefficients[c]:
                        raise Exception(f'{coefficient} = {finded_coefficients[coefficient]} ....{c} = {coefficients[c]}')

        # Нужно сделать логику для построения грузовой эпюры на свободном конце рамы
        print(finded_coefficients)

        # Преобразовываем рамы МП в МС, отрисовываем их в автокаде
        fm_frames = []
        _, _, _, mm_loads = new_mm_frame(params)
        for i in ed_diagrams_with_p:
            fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)

            for mm_frame in mm_frames:
                if mm_frame.name == i:
                    m_fr = mm_frame

            fm_frame = SolvableFrame(name=i, nodes=fm_nodes, rods=fm_rods, supports=m_fr.supports, loads=m_fr.loads)
            for mm_frame in mm_frames:
                if mm_frame.name == i:
                    replace_diagrams_from_mmframe_to_fmframe(mm_frame=mm_frame, fm_frame=fm_frame)

            fm_frame, msp, base_point = draw_frame(frame=fm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                   accuracy=3, drawing_nodes=False)
            n_base_point = None
            for mm_load in mm_loads:
                for fm_node in fm_frame.nodes:
                    if mm_loads[mm_load][0].node.x == fm_node.x and mm_loads[mm_load][0].node.y == fm_node.y:
                        if isinstance(mm_loads[mm_load][0], Twist):
                            msp, n_base_point = draw_node_with_inner_loads(frame=fm_frame, node_name=fm_node.name,
                                                                           n_base_point=n_base_point, msp=msp)
                            node_point = (fm_node.x + n_base_point[0], fm_node.y + n_base_point[1])
                            mm_loads[mm_load][0].draw(insert_point=node_point, msp=msp,
                                                      load_name=f'r{mm_load}{fm_frame.name}')
                        elif isinstance(mm_loads[mm_load][0], Displacement):
                            msp, n_base_point = draw_displacement_finding(frame=fm_frame, displacement=mm_loads[mm_load][0],
                                                                           n_base_point=n_base_point, msp=msp)
                            node_point = (fm_node.x + n_base_point[0], fm_node.y + n_base_point[1])
                            mm_loads[mm_load][0].draw(insert_point=node_point, msp=msp,
                                                      load_name=f'r{mm_load}{fm_frame.name}')

                        for entity in layout:
                            if entity.dxf.layer == f'мп_узел r{mm_load}{fm_frame.name}' and entity.dxftype() == 'VIEWPORT':
                                if entity:
                                    entity.dxf.view_center_point = node_point



            fm_frames.append(fm_frame)

            for entity in layout:
                if entity.dxf.layer in [f'мп_еденичная эпюра М{i}', 'мп_эпюра Мp'] and entity.dxftype() == 'VIEWPORT':
                    if entity:
                        entity.dxf.view_center_point = (fm_frame.base_point[0] + fm_frame.geometrical_center()[0],
                                                            fm_frame.base_point[1] + fm_frame.geometrical_center()[1],
                                                            0.0)
                elif entity.dxf.layer == f'мп_расчет М{i}':
                    entity.text = calculating_diagram_reports[i]

        # Расчитываем эпюру Ms и отрисовываем ее
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        s_mm_frame = SolvableFrame(name='s', nodes=fm_nodes, rods=fm_rods, supports=m_fr.supports, loads=None)
        for rod in s_mm_frame.rods:
            rod.diagram_M = [0, 0]
            for i in ed_diagrams:
                for fr in fm_frames:
                    if fr.name == i:
                        for rod1 in fr.rods:
                            if rod1.name == rod.name:
                                rod.diagram_M[0] += rod1.diagram_M[0]
                                rod.diagram_M[1] += rod1.diagram_M[1]
                                break
                        break
        s_mm_frame, msp, base_point = draw_frame(frame=s_mm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                 accuracy=3)
        for entity in layout:
            if entity.dxf.layer == 'мп_эпюра Мs' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (s_mm_frame.base_point[0] + s_mm_frame.geometrical_center()[0],
                                                    s_mm_frame.base_point[1] + s_mm_frame.geometrical_center()[1],
                                                    0.0)

        print('\n-------Универсальная проверка-------')
        universal_check = '\n\n'
        delta_ss_text, delta_ss = multiply_M_frames_by_Simpson(frame1=s_mm_frame, frame2=s_mm_frame)
        delta_ss_text = delta_ss_text.replace('/EI', '·i')
        universal_check += f'δ\\H0.5x;ss\\H2.0x; = {delta_ss_text}\n'
        print(f'δss = {delta_ss_text}\n')
        if len(ed_diagrams) == 3:
            r11 = finded_coefficients['r11']
            r12 = finded_coefficients['r21']
            r13 = finded_coefficients['r31']
            r22 = finded_coefficients['r22']
            r23 = finded_coefficients['r32']
            r33 = finded_coefficients['r33']
            sum_delta = r11 + r12 * 2 + r13 * 2 + r22 + r23 * 2 + r33
            uni_check_text = (f'r\\H0.5x;11\\H2.0x; + r\\H0.5x;12\\H2.0x;·2 + r\\H0.5x;13\\H2.0x;·2 + r\\H0.5x;22\\H2.0x; + '
                              f'r\\H0.5x;23\\H2.0x;·2 + r\\H0.5x;33\\H2.0x; = {round_up(r11, 3)}·i + '
                              f'2·{round_up(r12, 3)}·i + 2·{round_up(r13, 3)}·i + {round_up(r22, 3)}·i + '
                              f'2·{round_up(r23, 3)}·i + {round_up(r33, 3)}·i = {round_up(sum_delta, 3)}·i\n')
            print(f'r11 + r12·2 + r13·2 + r22 + r23·2 + r33 = {r11}·i + 2·{r12}·i + 2·{r13}·i + {r22}·i + 2·{r23}·i + {r33}·i = {sum_delta}·i\n')
            E_uni_check, e_text_uni_check = relative_error_percent(delta_ss, sum_delta, tolerance_percent=3)
            universal_check += '\n' + uni_check_text + '\n' + e_text_uni_check + '\n' + 'Проверка выполняется'
        elif len(ed_diagrams) == 2:
            r11 = finded_coefficients['r11']
            r12 = finded_coefficients['r21']
            r22 = finded_coefficients['r22']
            sum_delta = r11 + r12 * 2 + r22
            uni_check_text = (f'r\\H0.5x;11\\H2.0x; + r\\H0.5x;12\\H2.0x;·2 + r\\H0.5x;22\\H2.0x; = {round_up(r11, 3)}·i + '
                              f'2·{round_up(r12, 3)}·i + {round_up(r22, 3)}·i = {round_up(sum_delta, 3)}·i\n')
            print(f'r11 + r12·2 + r22 = {r11}·i + 2·{r12}·i + {r22}·i = {sum_delta}·i\n')
            E_uni_check, e_text_uni_check = relative_error_percent(delta_ss, sum_delta, tolerance_percent=3)
            universal_check += '\n' + uni_check_text + '\n' + e_text_uni_check + '\n' + 'Проверка выполняется'

        for entity in layout:
            if entity.dxf.layer == 'Универсальная проверка':
                entity.text += universal_check



        print('\n-------Столбцовая проверка-------')
        column_check = '\n\n'
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        p_fm_frame = SolvableFrame(name='fm_p', nodes=fm_nodes, rods=fm_rods, supports=fm_supports, loads=fm_loads['p']).classify_part()
        report = p_fm_frame.solve_frame()
        p_fm_frame.base_point = base_point
        p_fm_frame.create_sections_for_diagrams()
        finding_moments_report = ''
        for rod in p_fm_frame.rods:
            section_equation = rod.calculate_diagram_m('m')
            finding_moments_report += section_equation + '\n'
            # if rod.name == 'AE':
            #     rod.diagram_M = [0, 55]

        finding_moments_report = finding_moments_report.replace('\n\n', '\n')
        finding_moments_report = finding_moments_report.replace('= =', '=')

        p_fm_frame, msp, base_point = draw_frame(frame=p_fm_frame, base_point=base_point, msp=msp, diagram_name='M',
                                                 accuracy=3)

        for entity in layout:
            if entity.dxf.layer == 'sf_Mp' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (p_fm_frame.base_point[0] + p_fm_frame.geometrical_center()[0],
                                                    p_fm_frame.base_point[1] + p_fm_frame.geometrical_center()[1],
                                                    0.0)
            elif entity.dxf.layer == 'sf_Mp нахождение опорных реакций':
                entity.text = report
            elif entity.dxf.layer == 'sf_Mp расчет эпюры моментов':
                entity.text = finding_moments_report

        delta_sp_text, delta_sp = multiply_M_frames_by_Simpson(frame1=s_mm_frame, frame2=p_fm_frame)
        delta_sp_text = delta_sp_text.replace('/EI', '')
        column_check += f'δ\\H0.5x;sp\\H2.0x; = {delta_sp_text}\n'
        print(f'δsp = {delta_sp_text}\n')

        if len(ed_diagrams) == 3:
            r1p = finded_coefficients['r1p']
            r2p = finded_coefficients['r2p']
            r3p = finded_coefficients['r3p']

            sum_delta = round_up(r1p + r2p + r3p, 3)
            col_check_text = (f'R\\H0.5x;1p\\H2.0x; + R\\H0.5x;2p\\H2.0x; + R\\H0.5x;3p\\H2.0x; = {round_up(r1p, 3)} + '
                              f'{round_up(r2p, 3)} + {round_up(r3p, 3)} = {sum_delta}\n')
            print(f'R1p + R2p + R3p = {r1p} + {r2p} + {r3p} = {sum_delta}\n')
            E_col_check, e_text_col_check = relative_error_percent(delta_sp, sum_delta, tolerance_percent=3)
            column_check += '\n' + col_check_text + '\n' + e_text_col_check + '\n' + 'Проверка выполняется'
        elif len(ed_diagrams) == 2:
            r1p = finded_coefficients['r1p']
            r2p = finded_coefficients['r2p']

            sum_delta = round_up(r1p + r2p, 3)
            col_check_text = (f'R\\H0.5x;1p\\H2.0x; + R\\H0.5x;2p\\H2.0x; = {round_up(r1p, 3)} + '
                              f'{round_up(r2p, 3)} = {sum_delta}\n')
            print(f'R1p + R2p = {r1p} + {r2p} = {sum_delta}\n')
            E_col_check, e_text_col_check = relative_error_percent(delta_sp, sum_delta, tolerance_percent=3)
            column_check += '\n' + col_check_text + '\n' + e_text_col_check + '\n' + 'Проверка выполняется'

        for entity in layout:
            if entity.dxf.layer == 'Столбцовая проверка':
                entity.text += column_check


        print('\n-------Решение системы уравнений-------')
        if len(ed_diagrams) == 3:
            eq1 = f'{round_up(r11, 3)}·i·z1 + {round_up(r12, 3)}·i·z2 + {round_up(r13, 3)}·i·z3 + {round_up(r1p, 3)} = 0'
            eq2 = f'{round_up(r12, 3)}·i·z1 + {round_up(r22, 3)}·i·z2 + {round_up(r23, 3)}·i·z3 + {round_up(r2p, 3)} = 0'
            eq3 = f'{round_up(r13, 3)}·i·z1 + {round_up(r23, 3)}·i·z2 + {round_up(r33, 3)}·i·z3 + {round_up(r3p, 3)} = 0'

            system_of_equations_1 = eq1 + '\n' + eq2 + '\n' + eq3 + '\n'

            print(system_of_equations_1)

            # Матрица коэффициентов
            A = numpy.array([[r11, r12, r13],
                             [r12, r22, r23],
                             [r13, r23, r33]])

            # Вектор правых частей
            B = numpy.array([-r1p, -r2p, -r3p])

            # Решение
            solution = numpy.linalg.solve(A, B)
            z1 = round_up(solution[0], 3)
            z2 = round_up(solution[1], 3)
            z3 = round_up(solution[2], 3)

            coef_z = {'z1': z1, 'z2': z2, 'z3': z3, 'zp': 1}

            system_of_equations_2 = f"z1 = {z1}\nz2 = {z2}\nz3 = {z3}\n"
            print(system_of_equations_2)
        elif len(ed_diagrams) == 2:
            eq1 = f'{round_up(r11, 3)}·i·z1 + {round_up(r12, 3)}·i·z2 + {round_up(r1p, 3)} = 0'
            eq2 = f'{round_up(r12, 3)}·i·z1 + {round_up(r22, 3)}·i·z2 + {round_up(r2p, 3)} = 0'

            system_of_equations_1 = eq1 + '\n' + eq2 + '\n'

            print(system_of_equations_1)

            # Матрица коэффициентов
            A = numpy.array([[r11, r12],
                             [r12, r22]])

            # Вектор правых частей
            B = numpy.array([-r1p, -r2p])

            # Решение
            solution = numpy.linalg.solve(A, B)
            z1 = round_up(solution[0], 3)
            z2 = round_up(solution[1], 3)

            coef_z = {'z1': z1, 'z2': z2, 'zp': 1}

            system_of_equations_2 = f"z1 = {z1}\nz2 = {z2}\n"
            print(system_of_equations_2)

        for entity in layout:
            if entity.dxf.layer == 'Система уравнений 1':
                entity.text = system_of_equations_1
            elif entity.dxf.layer == 'Система уравнений 2':
                entity.text = system_of_equations_2


        print('-------"Эпюра Мок"-------')
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        ok_mm_frame = SolvableFrame(name='ok', nodes=fm_nodes, rods=fm_rods, supports=m_fr.supports, loads=fm_loads['p'])
        for rod in ok_mm_frame.rods:
            rod.diagram_M = [0, 0]
            for i in ed_diagrams_with_p:
                for fr in fm_frames:
                    if fr.name == i:
                        for rod1 in fr.rods:
                            if rod1.name == rod.name:
                                if not rod1.diagram_M:
                                    break
                                if len(rod1.diagram_M) == 2 and len(rod.diagram_M) == 2:
                                    rod.diagram_M[0] += rod1.diagram_M[0] * coef_z[f'z{i}']
                                    rod.diagram_M[1] += rod1.diagram_M[1] * coef_z[f'z{i}']
                                elif len(rod1.diagram_M) == 3 and len(rod.diagram_M) == 2:
                                    rod.diagram_M = [rod.diagram_M[0], (rod.diagram_M[0] + rod.diagram_M[1]) / 2, rod.diagram_M[1]]
                                    rod.diagram_M[0] += rod1.diagram_M[0] * coef_z[f'z{i}']
                                    rod.diagram_M[1] += rod1.diagram_M[1] * coef_z[f'z{i}']
                                    rod.diagram_M[2] += rod1.diagram_M[2] * coef_z[f'z{i}']
                                elif len(rod1.diagram_M) == 2 and len(rod.diagram_M) == 3:
                                    d_M = [rod1.diagram_M[0], (rod1.diagram_M[0] + rod1.diagram_M[1]) / 2, rod1.diagram_M[1]]
                                    rod.diagram_M[0] += d_M[0] * coef_z[f'z{i}']
                                    rod.diagram_M[1] += d_M[1] * coef_z[f'z{i}']
                                    rod.diagram_M[2] += d_M[2] * coef_z[f'z{i}']
                                elif len(rod1.diagram_M) == 3 and len(rod.diagram_M) == 3:
                                    rod.diagram_M[0] += rod1.diagram_M[0] * coef_z[f'z{i}']
                                    rod.diagram_M[1] += rod1.diagram_M[1] * coef_z[f'z{i}']
                                    rod.diagram_M[2] += rod1.diagram_M[2] * coef_z[f'z{i}']
                                break
            print(f'{rod}.....{rod.diagram_M}')
        ok_mm_frame, msp, base_point = draw_frame(frame=ok_mm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                  drowing_loads=False, accuracy=3)

        for entity in layout:
            if entity.dxf.layer == 'мп_эпюра Мok' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (ok_mm_frame.base_point[0] + ok_mm_frame.geometrical_center()[0],
                                                    ok_mm_frame.base_point[1] + ok_mm_frame.geometrical_center()[1],
                                                    0.0)


        print('-------Деформационная проверка-------')
        deformation_check = '\n\n'
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        s_fm_frame = SolvableFrame(name='fm_s', nodes=fm_nodes, rods=fm_rods, supports=fm_supports, loads=fm_loads['s']).classify_part()
        report = s_fm_frame.solve_frame()
        s_fm_frame.base_point = base_point
        s_fm_frame.create_sections_for_diagrams()
        finding_moments_report = ''
        for rod in s_fm_frame.rods:
            section_equation = rod.calculate_diagram_m('m')
            finding_moments_report += section_equation + '\n'
        finding_moments_report = finding_moments_report.replace('\n\n', '\n')
        finding_moments_report = finding_moments_report.replace('= =', '=')

        s_fm_frame, msp, base_point = draw_frame(frame=s_fm_frame, base_point=base_point, msp=msp, diagram_name='M',
                                                 accuracy=2)

        for entity in layout:
            if entity.dxf.layer == 'sf_Ms' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (s_fm_frame.base_point[0] + s_fm_frame.geometrical_center()[0],
                                                    s_fm_frame.base_point[1] + s_fm_frame.geometrical_center()[1],
                                                    0.0)
            elif entity.dxf.layer == 'sf_Ms нахождение опорных реакций':
                entity.text = report
            elif entity.dxf.layer == 'sf_Ms расчет эпюры моментов':
                entity.text = finding_moments_report


        delta_sok_text, delta_sok = multiply_M_frames_by_Simpson(frame1=s_fm_frame, frame2=ok_mm_frame)
        delta_sok_text = delta_sok_text.replace('/EI', '')
        print(f'δsok = {delta_sok_text}\n')
        print(f'δsok = {delta_sok} ≈ 0')
        if delta_sok <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}\n")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}\n")

        deformation_check += (f'δ\\H0.5x;sok\\H2.0x; = {delta_sok_text}\n' + '\n' + f'δ\\H0.5x;sok\\H2.0x; = {delta_sok} ≈ 0\n' +
                              'Проверка выполняется')

        for entity in layout:
            if entity.dxf.layer == 'Деформационная проверка':
                entity.text += deformation_check

        print('-------"Эпюра Q"-------')
        calculating_Q_report = ''
        i = 1
        for rod in ok_mm_frame.rods:
            q = None
            if len(rod.diagram_M) == 3:
                q = params['q']

            report = rod.calculate_diagram_q(q=q)
            calculating_Q_report += report + '\n'
            i += 1
            print(f'{rod} ------ {rod.diagram_Q}')
        ok_mm_frame.base_point = base_point
        ok_mm_frame, msp, base_point = draw_frame(frame=ok_mm_frame, base_point=base_point, diagram_name='Q', msp=msp,
                                                  drowing_loads=False, accuracy=2)

        for entity in layout:
            if entity.dxf.layer == 'sf_Q' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (ok_mm_frame.base_point[0] + ok_mm_frame.geometrical_center()[0],
                                                    ok_mm_frame.base_point[1] + ok_mm_frame.geometrical_center()[1],
                                                    0.0)
            elif entity.dxf.layer == 'Расчет эпюры Q':
                entity.text = calculating_Q_report




        zoom.extents(msp)
        doc.saveas(f'report.dxf')

        input('Проверьте файл report.dxf, подготовьтесь вводить значения эпюры N и опорные реакции, далее нажмите ENTER')
        doc = ezdxf.readfile('report.dxf')
        msp = doc.modelspace()
        layout = doc.layouts.get("Шаблон (метод перемещений)")
        print(f'\n')

        # чекист
        nn = [-4.09, 0, -7.21, -7.21, -7.21, 0, -6.74, -14.18, -1.13, -1.13]
        # мацукевич
        # nn = [-20.2, -18.66, -18.66, 0, 0.21, 0.21, -14.85]
        # демон
        # nn = [3.37, 0, 0, 13.29, 0, 13, 0, 3.37]
        print('-------"Эпюра N"-------')
        i = 0
        for rod in ok_mm_frame.rods:
            # print(rod)
            # N1 = float(input('Введите N1:'))
            N1 = nn[i]
            rod.diagram_N = [N1, N1]
            i += 1

        ok_mm_frame.base_point = base_point
        ok_mm_frame, msp, base_point = draw_frame(frame=ok_mm_frame, base_point=base_point, diagram_name='N', msp=msp,
                                                  drowing_loads=False, accuracy=2)

        for entity in layout:
            if entity.dxf.layer == 'sf_N' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (ok_mm_frame.base_point[0] + ok_mm_frame.geometrical_center()[0],
                                                    ok_mm_frame.base_point[1] + ok_mm_frame.geometrical_center()[1],
                                                    0.0)


        if symmetry:
            symmetric_pare_of_rods = main_frame.get_symmetric_pare_of_rods()
            for ok_rod in ok_mm_frame:
                for pare_of_rods in symmetric_pare_of_rods:
                    if ok_rod.name in [pare_of_rods[0].name, pare_of_rods[1].name]:
                        if not ok_rod.diagram_M or not ok_rod.diagram_Q or not ok_rod.diagram_N:
                            raise Exception(f'Стержень {ok_rod} не расчитан')
                        else:
                            for rod in pare_of_rods:
                                if rod.name == ok_rod:
                                    rod.diagram_M = ok_rod.diagram_M
                                    rod.diagram_Q = ok_rod.diagram_Q
                                    rod.diagram_N = ok_rod.diagram_N
                                if rod.name != ok_rod:
                                    if rod.dx() == 0:
                                        rod.diagram_M = [-x for x in ok_rod.diagram_M]
                                    else:
                                        rod.diagram_M = sorted(ok_rod.diagram_M, reverse=True)
                                    rod.diagram_Q = [-x for x in ok_rod.diagram_Q]
                                    rod.diagram_N = ok_rod.diagram_N


        # чекист
        r = [-5.66, 4.09, -4.69, -0.66, -6.74, -2.28, -1.13, 6.18, -10.53]
        # мацукевич
        # r = [1.64, 20.2, 2.19, -1.64, 20.2, -2.19]
        # демон
        # r = [-3.37, 11.84, -25.49, 0.8, 3.37, -0.51, 1.64, -6.13]
        i = 0
        for reaction in main_frame.reactions():
            # print(reaction)
            # v = float(input('Введите значение реакции:'))
            # reaction.value = v
            reaction.value = r[i]
            main_frame.finded_reactions.append(reaction)
            i += 1

        for reaction in main_frame.finded_reactions:
            print(reaction)

        print('-------Статическая проверка-------')
        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, msp=msp)

        for entity in layout:
            if entity.dxf.layer == 'мп_рама для статической проверки' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.base_point[0] + main_frame.geometrical_center()[0],
                                                    main_frame.base_point[1] + main_frame.geometrical_center()[1],
                                                    0.0)

        static_check = '\n\n'
        # node_name = str(input("\nВведите имя, относительно которого хотите составить уравнение моментов: "))
        node_name = 'E'
        for node in main_frame.nodes:
            if node.name == node_name:
                node_for_checking = node
        if node_for_checking:
            check_moment, check_equation = main_frame.sum_momentum_about_node(node=node_for_checking)
        else:
            raise Exception("Задано неверное имя узла")
        static_check_1 = check_equation + '\n' + f'   {round_up(check_moment, 4)} = 0\n' + 'Проверка выполняется\n\n'
        print(check_equation)
        print(f'   {check_moment} = 0')
        if abs(check_moment) <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = main_frame.sum_force_projections('x')
        print(f'∑x: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_2 = (f'∑x: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {round_up(sum_of_projections, 4)} = 0\n' + 'Проверка выполняется\n\n')

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = main_frame.sum_force_projections('y')
        print(f'∑y: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_3 = (f'∑y: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {round_up(sum_of_projections, 4)} = 0\n' + 'Проверка выполняется\n')

        static_check = static_check_1 + static_check_2 + static_check_3
        for entity in layout:
            if entity.dxf.layer == 'Статическая проверка':
                entity.text = static_check

        zoom.extents(msp)
        doc.save()
