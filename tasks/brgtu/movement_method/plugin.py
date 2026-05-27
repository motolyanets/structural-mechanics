from typing import Dict, Any

import ezdxf
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.load import Twist, Displacement, Force
from core.mechanics.solver import FrameForMovementMethod, SolvableFrame, multiply_M_frames_by_Simpson
from services.authocad import draw_main_frame, draw_mm_diagram
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
            # {"scheme_id": 19, "name": "Схема 19"},
            {"scheme_id": 22, "name": "Схема 22"},
            # {"scheme_id": 24, "name": "Схема 24"},
            # {"scheme_id": 27, "name": "Схема 27"},
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
                        report += f'r{load_name}{frame.name} = {round_up(r, 3)}'
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
                        report += f'r{load_name}{frame.name} = {round_up(r, 3)}'
                        coefficients[f'r{load_name}{frame.name}'] = r
                        reports[f'r{load_name}{frame.name}'] = report
            return coefficients, reports

        def replace_m_diagram_from_mmframe_to_fmframe(mm_frame: FrameForMovementMethod, fm_frame: SolvableFrame):
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
                                elif i == len(sorted_rods) - 1:
                                    m1 = m2
                                    m2 = m_end
                                else:
                                    m1 = m2
                                    l1 += fm_rod.length()
                                    m2 = m_start + (m_end - m_start) * l1 / mm_length
                                fm_rod.diagram_M = [m1, m2]

        if circuit_number == 17:
            from schemes.brgtu.movement_method.frame_17 import create_frame_17, create_primary_system_17
            fr_nodes, fr_rods, fr_supports, fr_loads = create_frame_17(params)
            # ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_17(params)
        elif circuit_number == 22:
            from schemes.brgtu.movement_method.frame_22 import create_frame_22, create_mm_primary_system_22, create_fm_primary_system_22
            fr_nodes, fr_rods, fr_supports, fr_loads = create_frame_22(params)
            mm_nodes, mm_rods, mm_supports, mm_loads = create_mm_primary_system_22(params)
            new_mm_frame = create_mm_primary_system_22
            new_fm_frame = create_fm_primary_system_22
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        # Создаем главную раму и рисуем ее
        main_frame = Frame(fr_nodes, fr_rods, fr_supports, fr_loads)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.geometrical_center()[0], main_frame.geometrical_center()[1], 0.0)
        frame, msp, base_point = draw_main_frame(frame=main_frame, base_point=base_point, msp=msp)

        # Создаем единичные рамы МП, расчитываем их
        diagrams = ['1', '2', '3', 'p']
        mm_frames = []
        calculating_diagram_reports = dict()

        for diagram in diagrams:
            print(diagram)
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
            print(reports)

            # Проверяем r12=r21 и т.д.
            for c in coefficients:
                coefficient = f'{c[0]}{c[2]}{c[1]}'
                if coefficient not in finded_coefficients:
                    finded_coefficients[c] = coefficients[c]
                else:
                    if finded_coefficients[coefficient] != coefficients[c]:
                        raise Exception(f'{coefficient} = {finded_coefficients[coefficient]} ....{c} = {coefficients[c]}')

        print(finded_coefficients)

        # Преобразовываем рамы МП в МС, отрисовываем их в автокаде
        fm_frames = []
        for i in ['1', '2', '3', 'p']:
            fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
            print(i)

            for mm_frame in mm_frames:
                if mm_frame.name == i:
                    m_fr = mm_frame

            fm_frame = SolvableFrame(name=i, nodes=fm_nodes, rods=fm_rods, supports=m_fr.supports, loads=m_fr.loads)
            for mm_frame in mm_frames:
                if mm_frame.name == i:
                    replace_m_diagram_from_mmframe_to_fmframe(mm_frame=mm_frame, fm_frame=fm_frame)

            for rod in fm_frame.rods:
                print(f'{rod}.....{rod.diagram_M}')

            fm_frame, msp, base_point = draw_main_frame(frame=fm_frame, base_point=base_point, diagram_name='M', msp=msp, accuracy=3)
            fm_frames.append(fm_frame)

        # Расчитываем эпюру Ms и отрисовываем ее
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        s_mm_frame = SolvableFrame(name='s', nodes=fm_nodes, rods=fm_rods, supports=m_fr.supports, loads=None)
        for rod in s_mm_frame.rods:
            rod.diagram_M = [0, 0]
            for i in ['1', '2', '3']:
                for fr in fm_frames:
                    if fr.name == i:
                        for rod1 in fr.rods:
                            if rod1.name == rod.name:
                                print(rod1.diagram_M)
                                rod.diagram_M[0] += rod1.diagram_M[0]
                                rod.diagram_M[1] += rod1.diagram_M[1]
            print(f'{rod}....{rod.diagram_M}')
        s_mm_frame, msp, base_point = draw_main_frame(frame=s_mm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                    accuracy=3)
        for entity in layout:
            if entity.dxf.layer == 'мп_эпюра Мs' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (s_mm_frame.base_point[0], s_mm_frame.base_point[1], 0.0)



        print('-------Универсальная проверка-------')
        universal_check = '\n\n'
        delta_ss_text, delta_ss = multiply_M_frames_by_Simpson(frame1=s_mm_frame, frame2=s_mm_frame)
        delta_ss_text = delta_ss_text.replace('/EI', '·i')
        universal_check += f'δ\\H0.5x;ss\\H2.0x; = {delta_ss_text}\n'
        print(f'δss = {delta_ss_text}\n')
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

        for entity in layout:
            if entity.dxf.layer == 'Универсальная проверка':
                entity.text += universal_check



        print('-------Столбцовая проверка-------')
        column_check = '\n\n'
        fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)
        p_fm_frame = SolvableFrame(name='fm_s', nodes=fm_nodes, rods=fm_rods, supports=fm_supports, loads=fm_loads).classify_part()
        report = p_fm_frame.solve_frame()
        p_fm_frame.base_point = base_point
        p_fm_frame.create_sections_for_diagrams()
        finding_moments_report = ''
        for rod in p_fm_frame.rods:
            section_equation = rod.calculate_diagram_m('m')
            finding_moments_report += section_equation + '\n'
        finding_moments_report = finding_moments_report.replace('\n\n', '\n')
        finding_moments_report = finding_moments_report.replace('= =', '=')

        p_fm_frame, msp, base_point = draw_main_frame(frame=p_fm_frame, base_point=base_point, msp=msp, diagram_name='M',
                                                      accuracy=3)

        for entity in layout:
            if entity.dxf.layer == 'sf_Mp' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (p_fm_frame.base_point[0], p_fm_frame.base_point[1], 0.0)
            elif entity.dxf.layer == 'sf_Mp нахождение опорных реакций':
                entity.text = report
            elif entity.dxf.layer == 'sf_Mp расчет эпюры моментов':
                entity.text = finding_moments_report

        delta_sp_text, delta_sp = multiply_M_frames_by_Simpson(frame1=s_mm_frame, frame2=p_fm_frame)
        delta_sp_text = delta_sp_text.replace('/EI', '')
        column_check += f'δ\\H0.5x;sp\\H2.0x; = {delta_sp_text}\n'
        print(f'δsp = {delta_sp_text}\n')
        r1p = finded_coefficients['r1p']
        r2p = finded_coefficients['r2p']
        r3p = finded_coefficients['r3p']

        sum_delta = round_up(r1p + r2p + r3p, 3)
        col_check_text = (f'R\\H0.5x;1p\\H2.0x; + R\\H0.5x;2p\\H2.0x; + R\\H0.5x;3p\\H2.0x; = {round_up(r1p, 3)} + '
                          f'{round_up(r2p, 3)} + {round_up(r3p, 3)} = {sum_delta}\n')
        print(f'R1p + R2p + R3p = {r1p} + {r2p} + {r3p} = {sum_delta}\n')
        E_col_check, e_text_col_check = relative_error_percent(delta_sp, sum_delta, tolerance_percent=3)
        column_check += '\n' + col_check_text + '\n' + e_text_col_check + '\n' + 'Проверка выполняется'

        for entity in layout:
            if entity.dxf.layer == 'Столбцовая проверка':
                entity.text += column_check











        zoom.extents(msp)
        doc.saveas(f'report.dxf')
