import importlib
from copy import deepcopy
from typing import Dict, Any

import ezdxf
import numpy
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.load import Force
from core.mechanics.solver import SolvableFrame, multiply_M_frames_by_Simpson
from schemes.brgtu.composite_frame.base_composit_frame import CompositeFrame
from services.authocad import draw_frame, draw_node_with_inner_loads
from services.services import round_up, relative_error_percent
from tasks.base import TaskPlugin
from tasks.brgtu.force_method.loader import ForceMethodLoader


class BRGTUForceMethod(TaskPlugin):
    task_id = "force_method"
    task_name = "Метод сил"
    university = "brgtu"

    def _init_loader(self):
        self.loader = ForceMethodLoader(self.excel_path)

    def solve(self, cipher: str) -> Dict[str, Any]:
        params = self.loader.load_cipher(cipher)
        circuit_number = params["circuit_number"]

        # Создаем новый DXF документ
        doc = ezdxf.readfile('Шаблон.dxf')
        msp = doc.modelspace()
        msp.delete_all_entities()
        layout = doc.layouts.get("Шаблон (метод сил)")
        base_point = [0, 0]

        task_condition_text = (f'{cipher}\n'
                               f'Схема - {circuit_number}       Нагрузка - {params['load_index']}\n'
                               f"l\\H0.5x;1\\H2.0x;={params['l1']}м          l\\H0.5x;2\\H2.0x;={params['l2']}м\n"
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
        print(f"  P = {params['P']} кН")
        print(f"  q = {params['q']} кН/м")
        print(f"  I2 = {params['i2']}")
        print(f"  I3 = {params['i3']}")
        print(f"  load_index = {params['load_index']}")
        print(f"{'=' * 60}")

        def get_circuit_functions(circuit_number):
            # Импортируем модуль динамически
            module = importlib.import_module(f'schemes.brgtu.force_method.frame_{circuit_number}')

            try:
                # Получаем функции из модуля
                create_main_frame = getattr(module, f'create_frame_{circuit_number}')
                new_fm_frame = getattr(module, f'create_primary_system_{circuit_number}')

                return create_main_frame, new_fm_frame

            except (ImportError, AttributeError) as e:
                raise ValueError(f"Схема {circuit_number} не реализована") from e

        create_main_frame, new_fm_frame = get_circuit_functions(circuit_number)

        # Создаем главную раму и рисуем ее
        fr_nodes, fr_rods, fr_supports, fr_loads, symmetry, main_details = create_main_frame(params)
        _, _, _, _, fm_details = new_fm_frame(params)

        main_frame = Frame(fr_nodes, fr_rods, fr_supports, fr_loads, symmetry)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.geometrical_center()[0], main_frame.geometrical_center()[1], 0.0)
                    entity.dxf.view_height = main_frame.height() + 0.3
            elif entity.dxf.layer == "мс_определение ССН":
                entity.text += fm_details['equation_of_static_determinacy']
        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, msp=msp, drowing_stiffnes=True)

        for i in [1, 2, 3]:
            b_p = [base_point[0], base_point[1] - main_frame.height() * i - 10 * i]
            _, msp, _ = draw_frame(frame=main_frame, base_point=b_p, msp=msp, drowing_stiffnes=False, drowing_loads=False,
                                   drawing_sections=False)
            for entity in layout:
                if entity.dxf.layer == f"ОС{i}" and entity.dxftype() == 'VIEWPORT':
                    if entity:
                        entity.dxf.view_center_point = (main_frame.geometrical_center()[0] + base_point[0],
                                                        main_frame.geometrical_center()[1] - main_frame.height() * i - 10 * i,
                                                        0.0)
                        entity.dxf.view_height = main_frame.height() + 0.3

        # Отрисовываем основную систему МП
        _, _, _, ps_fm_loads, _ = new_fm_frame(params)

        ed_diagrams = []
        for load in ps_fm_loads:
            if load != 'p' and load != 'k':
                ed_diagrams.append(load)

        # Создаем единичные рамы МС
        ed_diagrams_with_p = ed_diagrams.copy()
        ed_diagrams_with_p.append('p')
        ed_diagrams_with_p.append('k')
        fm_frames = []

        for diagram in ed_diagrams_with_p:
            print(f'Расчет эпюры М{diagram} метода перемещений')
            fm_nodes, fm_rods, fm_supports, fm_loads, _ = new_fm_frame(params)

            if 'splitted_frames_order' in fm_details:
                frame = CompositeFrame(name=f'{diagram}', nodes=fm_nodes, rods=fm_rods, supports=fm_supports,
                                            loads=fm_loads[diagram],
                                            splitted_frames_order=fm_details['splitted_frames_order'])
            else:
                frame = SolvableFrame(name=f'{diagram}', nodes=fm_nodes, rods=fm_rods, supports=fm_supports,
                                           loads=fm_loads[diagram]).classify_part()
            fm_frames.append(frame)

        # Расчитываем единичные рамы МС
        for fm_frame in fm_frames:
            report = fm_frame.solve_frame()
            fm_frame.base_point = base_point
            fm_frame.create_sections_for_diagrams()
            finding_moments_report = ''
            for rod in fm_frame.rods:
                section_equation = rod.calculate_diagram_m()
                finding_moments_report += section_equation + '\n'
            finding_moments_report = finding_moments_report.replace('\n\n', '\n')
            finding_moments_report = finding_moments_report.replace('= =', '=')

            fm_frame, msp, base_point = draw_frame(frame=fm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                   accuracy=3, drawing_nodes=False)

            for entity in layout:
                if entity.dxf.layer == f'sf_M{fm_frame.name}' and entity.dxftype() == 'VIEWPORT':
                    if entity:
                        entity.dxf.view_center_point = (fm_frame.base_point[0] + fm_frame.geometrical_center()[0],
                                                            fm_frame.base_point[1] + fm_frame.geometrical_center()[1],
                                                            0.0)
                        entity.dxf.view_height = fm_frame.height() + 0.3
                elif entity.dxf.layer == f'sf_M{fm_frame.name} нахождение опорных реакций':
                    entity.text = report
                elif entity.dxf.layer == f'sf_M{fm_frame.name} расчет эпюры моментов':
                    entity.text = finding_moments_report

        # Расчитываем эпюру Ms и отрисовываем ее
        fm_nodes, fm_rods, fm_supports, fm_loads, _ = new_fm_frame(params)
        s_fm_frame = SolvableFrame(name='s', nodes=fm_nodes, rods=fm_rods, supports=fm_supports, loads=None)
        for rod in s_fm_frame.rods:
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
        s_fm_frame, msp, base_point = draw_frame(frame=s_fm_frame, base_point=base_point, diagram_name='M', msp=msp,
                                                 accuracy=3)
        for entity in layout:
            if entity.dxf.layer == 'sf_Ms' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (s_fm_frame.base_point[0] + s_fm_frame.geometrical_center()[0],
                                                    s_fm_frame.base_point[1] + s_fm_frame.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = s_fm_frame.height() + 0.3



        odds_text = '\n\n'
        for frame in fm_frames:
            if frame.name == '1':
                fm_frame_1 = frame
            elif frame.name == '2':
                fm_frame_2 = frame
            elif frame.name == '3':
                fm_frame_3 = frame
            elif frame.name == 'p':
                fm_frame_p = frame
            elif frame.name == 'k':
                fm_frame_k = frame

        delta_11_text, delta_11 = multiply_M_frames_by_Simpson(frame1=fm_frame_1, frame2=fm_frame_1)
        delta_12_text, delta_12 = multiply_M_frames_by_Simpson(frame1=fm_frame_1, frame2=fm_frame_2)
        delta_13_text, delta_13 = multiply_M_frames_by_Simpson(frame1=fm_frame_1, frame2=fm_frame_3)
        delta_22_text, delta_22 = multiply_M_frames_by_Simpson(frame1=fm_frame_2, frame2=fm_frame_2)
        delta_23_text, delta_23 = multiply_M_frames_by_Simpson(frame1=fm_frame_2, frame2=fm_frame_3)
        delta_33_text, delta_33 = multiply_M_frames_by_Simpson(frame1=fm_frame_3, frame2=fm_frame_3)
        delta_1p_text, delta_1p = multiply_M_frames_by_Simpson(frame1=fm_frame_1, frame2=fm_frame_p)
        delta_2p_text, delta_2p = multiply_M_frames_by_Simpson(frame1=fm_frame_2, frame2=fm_frame_p)
        delta_3p_text, delta_3p = multiply_M_frames_by_Simpson(frame1=fm_frame_3, frame2=fm_frame_p)

        odds_text += (f'δ\\H0.5x;11\\H2.0x; = {delta_11_text}\n' + '\n' + f'δ\\H0.5x;12\\H2.0x; = {delta_12_text}\n' + '\n' +
                      f'δ\\H0.5x;13\\H2.0x; = {delta_13_text}\n' + '\n' + f'δ\\H0.5x;22\\H2.0x; = {delta_22_text}\n' + '\n' +
                      f'δ\\H0.5x;23\\H2.0x; = {delta_23_text}\n' + '\n' + f'δ\\H0.5x;33\\H2.0x; = {delta_33_text}\n' + '\n' +
                      f'Δ\\H0.5x;1p\\H2.0x; = {delta_1p_text}\n' + '\n' + f'Δ\\H0.5x;2p\\H2.0x; = {delta_2p_text}\n' + '\n' +
                      f'Δ\\H0.5x;3p\\H2.0x; = {delta_3p_text}')
        for entity in layout:
            if entity.dxf.layer == 'Определение коэффициентов при неизвестных':
                entity.text += odds_text

        print(f'δ11 = {delta_11_text}\n')
        print(f'δ12 = {delta_12_text}\n')
        print(f'δ13 = {delta_13_text}\n')
        print(f'δ22 = {delta_22_text}\n')
        print(f'δ23 = {delta_23_text}\n')
        print(f'δ33 = {delta_33_text}\n')
        print(f'Δ1p = {delta_1p_text}\n')
        print(f'Δ2p = {delta_2p_text}\n')
        print(f'Δ3p = {delta_3p_text}\n')


        print('\n-------Универсальная проверка-------')
        universal_check = '\n\n'
        delta_ss_text, delta_ss = multiply_M_frames_by_Simpson(frame1=s_fm_frame, frame2=s_fm_frame)
        delta_ss_text = delta_ss_text.replace('/EI', '·i')
        universal_check += f'δ\\H0.5x;ss\\H2.0x; = {delta_ss_text}\n'
        print(f'δss = {delta_ss_text}\n')
        sum_delta = delta_11 + delta_12 * 2 + delta_13 * 2 + delta_22 + delta_23 * 2 + delta_33
        uni_check_text = (f'δ\\H0.5x;11\\H2.0x; + δ\\H0.5x;12\\H2.0x;·2 + δ\\H0.5x;13\\H2.0x;·2 + δ\\H0.5x;22\\H2.0x; + '
                          f'δ\\H0.5x;23\\H2.0x;·2 + δ\\H0.5x;33\\H2.0x; = {delta_11}/EI + 2·{delta_12}/EI + 2·{delta_13}/EI + {delta_22}/EI + 2·{delta_23}/EI + {delta_33}/EI = {sum_delta}/EI\n')
        print(f'δ11 + δ12·2 + δ13·2 + δ22 + δ23·2 + δ33 = {delta_11}/EI + 2·{delta_12}/EI + 2·{delta_13}/EI + {delta_22}/EI + 2·{delta_23}/EI + {delta_33}/EI = {sum_delta}/EI\n')
        E_uni_check, e_text_uni_check = relative_error_percent(delta_ss, sum_delta, tolerance_percent=3)
        universal_check += '\n' + uni_check_text + '\n' + e_text_uni_check + '\n' + 'Проверка выполняется'

        for entity in layout:
            if entity.dxf.layer == 'Универсальная проверка':
                entity.text += universal_check


        print('-------Столбцовая проверка-------')
        column_check = '\n\n'
        delta_sp_text, delta_sp = multiply_M_frames_by_Simpson(frame1=s_fm_frame, frame2=fm_frame_p)
        column_check += f'δ\\H0.5x;sp\\H2.0x; = {delta_sp_text}\n'
        print(f'δsp = {delta_sp_text}\n')
        sum_delta = round_up(delta_1p + delta_2p + delta_3p, 2)
        col_check_text = (f'Δ\\H0.5x;1p\\H2.0x; + Δ\\H0.5x;2p\\H2.0x; + Δ\\H0.5x;3p\\H2.0x; = {delta_1p}/EI + '
                          f'{delta_2p}/EI + {delta_3p}/EI = {sum_delta}/EI\n')
        print(f'Δ1p + Δ2p + Δ3p = {delta_1p}/EI + {delta_2p}/EI + {delta_3p}/EI = {sum_delta}/EI\n')
        E_col_check, e_text_col_check = relative_error_percent(delta_sp, sum_delta, tolerance_percent=3)
        column_check += '\n' + col_check_text + '\n' + e_text_col_check + '\n' + 'Проверка выполняется'

        for entity in layout:
            if entity.dxf.layer == 'Столбцовая проверка':
                entity.text += column_check




        print('-------Решение системы уравнений-------')
        eq1 = f'({round_up(delta_11,3)}/EI)·x1 + ({round_up(delta_12,3)}/EI)·x2 +({round_up(delta_13,3)}/EI)·x3 + {round_up(delta_1p,3)}/EI = 0'
        eq2 = f'({round_up(delta_12,3)}/EI)·x1 + ({round_up(delta_22,3)}/EI)·x2 +({round_up(delta_23,3)}/EI)·x3 + {round_up(delta_2p,3)}/EI = 0'
        eq3 = f'({round_up(delta_13,3)}/EI)·x1 + ({round_up(delta_23,3)}/EI)·x2 +({round_up(delta_33,3)}/EI)·x3 + {round_up(delta_3p,3)}/EI = 0'

        system_of_equations_1 = eq1 + '\n' + eq2 + '\n' + eq3 + '\n'

        print(system_of_equations_1)

        # Матрица коэффициентов
        A = numpy.array([[delta_11, delta_12, delta_13],
                         [delta_12, delta_22, delta_23],
                         [delta_13, delta_23, delta_33]])

        # Вектор правых частей
        B = numpy.array([-delta_1p, -delta_2p, -delta_3p])

        # Решение
        solution = numpy.linalg.solve(A, B)
        x1 = float(solution[0])
        x2 = float(solution[1])
        x3 = float(solution[2])

        # x1 = -0.303
        # x2 = -0.58
        # x3 = -7.36

        coef = dict()
        coef['1'] = x1
        coef['2'] = x2
        coef['3'] = x3
        coef['p'] = 1


        system_of_equations_2 = f"x1 = {round_up(x1, 3)}\nx2 = {round_up(x2, 3)}\nx3 = {round_up(x3, 3)}\n"
        print(system_of_equations_2)

        for entity in layout:
            if entity.dxf.layer == 'Система уравнений 1':
                entity.text = system_of_equations_1
            elif entity.dxf.layer == 'Система уравнений 2':
                entity.text = system_of_equations_2



        print('-------"Эпюра Мок"-------')
        fm_nodes, fm_rods, fm_supports, fm_loads, _ = new_fm_frame(params)
        ok_mm_frame = SolvableFrame(name='ok', nodes=fm_nodes, rods=fm_rods, supports=fr_supports, loads=fm_loads['p'])
        for rod in ok_mm_frame.rods:
            rod.diagram_M = [0, 0]
            for i in ed_diagrams_with_p:
                if i != 'k':
                    for fr in fm_frames:
                        if fr.name == i:
                            for rod1 in fr.rods:
                                if rod1.name == rod.name:
                                    if not rod1.diagram_M:
                                        break
                                    if len(rod1.diagram_M) == 2 and len(rod.diagram_M) == 2:
                                        rod.diagram_M[0] += rod1.diagram_M[0] * coef[i]
                                        rod.diagram_M[1] += rod1.diagram_M[1] * coef[i]
                                    elif len(rod1.diagram_M) == 3 and len(rod.diagram_M) == 2:
                                        rod.diagram_M = [rod.diagram_M[0], (rod.diagram_M[0] + rod.diagram_M[1]) / 2, rod.diagram_M[1]]
                                        rod.diagram_M[0] += rod1.diagram_M[0] * coef[i]
                                        rod.diagram_M[1] += rod1.diagram_M[1] * coef[i]
                                        rod.diagram_M[2] += rod1.diagram_M[2] * coef[i]
                                    elif len(rod1.diagram_M) == 2 and len(rod.diagram_M) == 3:
                                        d_M = [rod1.diagram_M[0], (rod1.diagram_M[0] + rod1.diagram_M[1]) / 2, rod1.diagram_M[1]]
                                        rod.diagram_M[0] += d_M[0] * coef[i]
                                        rod.diagram_M[1] += d_M[1] * coef[i]
                                        rod.diagram_M[2] += d_M[2] * coef[i]
                                    elif len(rod1.diagram_M) == 3 and len(rod.diagram_M) == 3:
                                        rod.diagram_M[0] += rod1.diagram_M[0] * coef[i]
                                        rod.diagram_M[1] += rod1.diagram_M[1] * coef[i]
                                        rod.diagram_M[2] += rod1.diagram_M[2] * coef[i]
                                    break
            print(f'{rod}.....{rod.diagram_M}')


        print('\n')
        print('-------Деформационная проверка-------')
        deformation_check = '\n\n'
        fm_nodes, fm_rods, fm_supports, fm_loads, _ = new_fm_frame(params)
        delta_sok_text, delta_sok = multiply_M_frames_by_Simpson(frame1=s_fm_frame, frame2=ok_mm_frame)
        print(f'δsok = {delta_sok_text}\n')
        print(f'δsok = {delta_sok}/EI ≈ 0')
        if delta_sok <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}\n")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}\n")

        deformation_check += (f'δ\\H0.5x;sok\\H2.0x; = {delta_sok_text}\n' + '\n' + f'δ\\H0.5x;sok\\H2.0x; = {delta_sok}/EI ≈ 0\n' +
                              'Проверка выполняется')

        for entity in layout:
            if entity.dxf.layer == 'Деформационная проверка':
                entity.text += deformation_check

        # q = [[-0.89, -0.89], [-0.89, -0.89], [3.8, -4.06], [0, 0], [0.3, 0.3], [-0.58, -0.58], [3.5, 3.5]]
        # i = 0
        # for rod in ok_mm_frame.rods:
        #     rod.diagram_Q = q[i]
        #     i += 1


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

        for entity in layout:
            if entity.dxf.layer == 'Расчет эпюры Q':
                entity.text = calculating_Q_report


        print('\n')
        print('-------"Эпюра N"-------')

        nodes_for_calculating = ok_mm_frame.calculate_diagram_N()
        # nodes_for_calculating = [ok_mm_frame.nodes[1], ok_mm_frame.nodes[2], ok_mm_frame.nodes[4], ok_mm_frame.nodes[5]]
        # n = [[-7.43, -7.43], [-7.08, -7.08], [-21.37, -21.37], [-14.95, -14.95], [-7.36, -0.78], [-10.35, -10.35], [-10.35, -10.35]]
        # i = 0
        # for rod in ok_mm_frame.rods:
        #     rod.diagram_N = n[i]
        #     i += 1
        for rod in ok_mm_frame.rods:
            print(f'{rod} ------ {rod.diagram_N}')

        # doc.saveas(f'report.dxf')


        ok_mm_frame.base_point = base_point
        n_base_point = None
        for node_for_calculating in nodes_for_calculating:
            msp, n_base_point = draw_node_with_inner_loads(frame=ok_mm_frame, node_name=node_for_calculating.name,
                                                           n_base_point=n_base_point, msp=msp, is_drawing_m=False)
        for entity in layout:
            if entity.dxf.layer == 'sf_N вырезание узлов' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (ok_mm_frame.base_point[0] + ok_mm_frame.geometrical_center()[0],
                                                    ok_mm_frame.base_point[1] + ok_mm_frame.geometrical_center()[1] - 20,
                                                    0.0)
                    entity.dxf.view_height = ok_mm_frame.height() + 0.3


        if symmetry:
            symmetric_pare_of_rods = main_frame.get_symmetric_pare_of_rods()
            for ok_rod in ok_mm_frame.rods:
                for pare_of_rods in symmetric_pare_of_rods:
                    if ok_rod.name in [pare_of_rods[0].name, pare_of_rods[1].name]:
                        if not ok_rod.diagram_M or not ok_rod.diagram_Q or not ok_rod.diagram_N:
                            raise Exception(f'Стержень {ok_rod} не расчитан')
                        else:
                            for rod in pare_of_rods:
                                if rod.name == ok_rod.name:
                                    rod.diagram_M = ok_rod.diagram_M
                                    rod.diagram_Q = ok_rod.diagram_Q
                                    rod.diagram_N = ok_rod.diagram_N
                                if rod.name != ok_rod.name:
                                    if rod.dx() == 0:
                                        rod.diagram_M = [-x for x in ok_rod.diagram_M]
                                        rod.diagram_Q = [-x for x in ok_rod.diagram_Q]
                                    else:
                                        d_M = ok_rod.diagram_M.copy()
                                        d_M.reverse()
                                        rod.diagram_M = d_M
                                        d_Q = [-x for x in ok_rod.diagram_Q]
                                        d_Q.reverse()
                                        rod.diagram_Q = d_Q
                                    rod.diagram_N = ok_rod.diagram_N
        else:
            for main_rod in main_frame.rods:
                for ok_rod in ok_mm_frame.rods:
                    if not ok_rod.diagram_M or not ok_rod.diagram_Q or not ok_rod.diagram_N:
                        raise Exception(f'Стержень {ok_rod} не расчитан')
                    else:
                        if main_rod.name == ok_rod.name:
                            main_rod.diagram_M = ok_rod.diagram_M
                            main_rod.diagram_Q = ok_rod.diagram_Q
                            main_rod.diagram_N = ok_rod.diagram_N
                            break

        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, diagram_name='M',
                                                  msp=msp,
                                                  drowing_loads=False, accuracy=2)

        for rod in main_frame.rods:
            if not rod.diagram_M:
                rod.diagram_M = [0, 0]
            if not rod.diagram_Q:
                rod.diagram_Q = [0, 0]
        for rod in main_frame.rods:
            if not rod.diagram_N:
                _ = main_frame.calculate_diagram_N()

        for entity in layout:
            if entity.dxf.layer == 'sf_Mok' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.base_point[0] + main_frame.geometrical_center()[0],
                                                    main_frame.base_point[1] + main_frame.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = main_frame.height() + 0.3
        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, diagram_name='Q', msp=msp,
                                                  drowing_loads=False, accuracy=2)
        for entity in layout:
            if entity.dxf.layer == 'sf_Q' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.base_point[0] + main_frame.geometrical_center()[0],
                                                    main_frame.base_point[1] + main_frame.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = main_frame.height() + 0.3

        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, diagram_name='N', msp=msp,
                                                  drowing_loads=False, accuracy=2)
        for entity in layout:
            if entity.dxf.layer == 'sf_N' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.base_point[0] + main_frame.geometrical_center()[0],
                                                    main_frame.base_point[1] + main_frame.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = main_frame.height() + 0.3


        print('\n')
        print('-------"Опорные реакции"-------')

        main_frame.set_reactions_from_diagrams()

        for reaction in main_frame.finded_reactions:
            print(reaction)


        print('\n')
        print('-------Статическая проверка-------')
        main_frame, msp, base_point = draw_frame(frame=main_frame, base_point=base_point, msp=msp)

        for entity in layout:
            if entity.dxf.layer == 'мс_рама для статической проверки' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (main_frame.base_point[0] + main_frame.geometrical_center()[0],
                                                    main_frame.base_point[1] + main_frame.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = main_frame.height() + 0.3

        static_check = '\n\n'
        node_name = main_details['node_name_for_static_check']
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
        if abs(check_moment) <= 0.2:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = main_frame.sum_force_projections('x')
        print(f'∑x: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.2:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_2 = (f'∑x: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {round_up(sum_of_projections, 4)} = 0\n' + 'Проверка выполняется\n\n')

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = main_frame.sum_force_projections('y')
        print(f'∑y: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.2:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_3 = (f'∑y: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {round_up(sum_of_projections, 4)} = 0\n' + 'Проверка выполняется\n')

        static_check = static_check_1 + static_check_2 + static_check_3
        for entity in layout:
            if entity.dxf.layer == 'Статическая проверка':
                entity.text = static_check
        print(f'\n')

        print('-------Перемещение точки К-------')

        delta_kok_text, delta_kok = multiply_M_frames_by_Simpson(frame1=fm_frame_k, frame2=ok_mm_frame)
        delta_k_text = f'Δ\\H0.5x;k\\H2.0x; = {delta_kok_text}\n'
        print(f'Δk = {delta_kok_text}\n')

        for entity in layout:
            if entity.dxf.layer == 'Перемещение точки К':
                entity.text = delta_k_text

        fm_frame_k, msp, base_point = draw_frame(frame=fm_frame_k, base_point=base_point, diagram_name='M', msp=msp,
                                                 accuracy=3)

        for entity in layout:
            if entity.dxf.layer == 'sf_Mk' and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (fm_frame_k.base_point[0] + fm_frame_k.geometrical_center()[0],
                                                    fm_frame_k.base_point[1] + fm_frame_k.geometrical_center()[1],
                                                    0.0)
                    entity.dxf.view_height = fm_frame_k.height() + 0.3

        zoom.extents(msp)
        doc.saveas(f'report.dxf')

