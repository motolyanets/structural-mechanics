from typing import Dict, Any

import ezdxf
import numpy
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.solver import SolvableFrame
from services.authocad import draw_frame, draw_diagram_m
from services.services import round_up, relative_error_percent
from tasks.base import TaskPlugin
from tasks.brgtu.force_method.loader import ForceMethodLoader


class BRGTUForceMethod(TaskPlugin):
    task_id = "force_method"
    task_name = "Метод сил"
    university = "brgtu"

    def _init_loader(self):
        self.loader = ForceMethodLoader(self.excel_path)

    def get_available_schemes(self) -> list:
        return [
            {"scheme_id": 10, "name": "Схема 10"},
            {"scheme_id": 27, "name": "Схема 27"},
            {"scheme_id": 29, "name": "Схема 29"},
        ]

    def solve(self, cipher: str) -> Dict[str, Any]:
        params = self.loader.load_cipher(cipher)
        circuit_number = params["circuit_number"]

        # Создаем новый DXF документ
        doc = ezdxf.readfile('Шаблон.dxf')
        msp = doc.modelspace()
        msp.delete_all_entities()
        layout = doc.layouts.get("Шаблон")
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

        if circuit_number == 10:
            from schemes.brgtu.force_method.frame_10 import create_frame_10, create_primary_system_10
            nodes, rods, supports, loads = create_frame_10(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_10(params)
        elif circuit_number == 27:
            from schemes.brgtu.force_method.frame_27 import create_frame_27, create_primary_system_27
            nodes, rods, supports, loads = create_frame_27(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_27(params)
        elif circuit_number == 29:
            from schemes.brgtu.force_method.frame_29 import create_frame_29, create_primary_system_29
            nodes, rods, supports, loads = create_frame_29(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_29(params)
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        from schemes.brgtu.composite_frame.base_composit_frame import CompositeFrame
        frame = CompositeFrame(nodes, rods, supports, loads)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (base_point[0], base_point[1], 0.0)
        frame, msp, base_point = draw_frame(frame=frame, base_point=base_point, msp=msp)


        sf = {}
        calculation_frame = SolvableFrame(nodes=ps_nodes, rods=ps_rods, supports=ps_supports, loads=loads)
        for load in ps_loads:
            fr = SolvableFrame(nodes=ps_nodes, rods=ps_rods, supports=ps_supports, loads=ps_loads[load])
            sf[f'sf_{load}'] = fr.classify_part()

        for f in sf:
            print(f)
            frame_1 = sf[f]
            report = frame_1.solve_frame()
            frame_1.base_point = base_point
            for entity in layout:
                if entity.dxf.layer == f and entity.dxftype() == 'VIEWPORT':
                    if entity:
                        entity.dxf.view_center_point = (base_point[0], base_point[1], 0.0)
                elif entity.dxf.layer == f'{f} нахождение опорных реакций':
                    entity.text = report




        rod11_diagram_M1 = [0, -1.5]
        rod12_diagram_M1 = [-1.5, -3]
        rod2_diagram_M1 = [0, 0]
        rod3_diagram_M1 = [0, 0]
        rod4_diagram_M1 = [-3, 0]
        rod5_diagram_M1 = [0, 0]
        rod6_diagram_M1 = [0, 0]

        rod11_diagram_M2 = [0, 0]
        rod12_diagram_M2 = [0, 0]
        rod2_diagram_M2 = [2.25, 4.5]
        rod3_diagram_M2 = [0, 2.25]
        rod4_diagram_M2 = [4.5, 3.1]
        rod5_diagram_M2 = [0, -3.1]
        rod6_diagram_M2 = [0, 0]

        rod11_diagram_M3 = [0, 0]
        rod12_diagram_M3 = [0, 0]
        rod2_diagram_M3 = [0.63, 1.26]
        rod3_diagram_M3 = [0, 0.63]
        rod4_diagram_M3 = [1.26, 0.88]
        rod5_diagram_M3 = [0, -0.88]
        rod6_diagram_M3 = [1, 0]

        rod11_diagram_Mp = [0, 0]
        rod12_diagram_Mp = [0, 12.75]
        rod2_diagram_Mp = [8.49, 24.07, 1.4]
        rod3_diagram_Mp = [0, 8.49, 1.4]
        rod4_diagram_Mp = [36.85, 0]
        rod5_diagram_Mp = [0, 0]
        rod6_diagram_Mp = [0, 0]


        m1 = [rod11_diagram_M1, rod12_diagram_M1, rod2_diagram_M1, rod3_diagram_M1, rod4_diagram_M1, rod5_diagram_M1, rod6_diagram_M1]
        m2 = [rod11_diagram_M2, rod12_diagram_M2, rod2_diagram_M2, rod3_diagram_M2, rod4_diagram_M2, rod5_diagram_M2, rod6_diagram_M2]
        m3 = [rod11_diagram_M3, rod12_diagram_M3, rod2_diagram_M3, rod3_diagram_M3, rod4_diagram_M3, rod5_diagram_M3, rod6_diagram_M3]
        mp = [rod11_diagram_Mp, rod12_diagram_Mp, rod2_diagram_Mp, rod3_diagram_Mp, rod4_diagram_Mp, rod5_diagram_Mp, rod6_diagram_Mp]

        rods = calculation_frame.rods
        i = 0
        for rod in rods:
            rod.diagram_M1 = m1[i]
            rod.diagram_M2 = m2[i]
            rod.diagram_M3 = m3[i]
            rod.diagram_Mp = mp[i]
            i += 1




        print('-------"Эпюра Мs"-------')
        for rod in rods:
            Ms_1 = rod.diagram_M1[0] + rod.diagram_M2[0] + rod.diagram_M3[0]
            Ms_2 = rod.diagram_M1[1] + rod.diagram_M2[1] + rod.diagram_M3[1]
            rod.diagram_Ms = [round_up(Ms_1), round_up(Ms_2)]
            print(f'{rod} ------ {rod.diagram_Ms}')

        odds_text = '\n\n'
        delta_11_text, delta_11 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M1')
        delta_12_text, delta_12 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M2')
        delta_13_text, delta_13 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M3')
        delta_22_text, delta_22 = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'M2')
        delta_23_text, delta_23 = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'M3')
        delta_33_text, delta_33 = calculation_frame.multiply_M_diagrams_by_Simpson('M3', 'M3')
        delta_1p_text, delta_1p = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'Mp')
        delta_2p_text, delta_2p = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'Mp')
        delta_3p_text, delta_3p = calculation_frame.multiply_M_diagrams_by_Simpson('M3', 'Mp')

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

        print('-------Универсальная проверка-------')

        universal_check = '\n\n'
        delta_ss_text, delta_ss = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Ms')
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
        delta_sp_text, delta_sp = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Mp')
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
        eq1 = f'({delta_11}/EI)·x1 + ({delta_12}/EI)·x2 +({delta_13}/EI)·x3 + {delta_1p}/EI = 0'
        eq2 = f'({delta_12}/EI)·x1 + ({delta_22}/EI)·x2 +({delta_23}/EI)·x3 + {delta_2p}/EI = 0'
        eq3 = f'({delta_13}/EI)·x1 + ({delta_23}/EI)·x2 +({delta_33}/EI)·x3 + {delta_3p}/EI = 0'

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
        x1 = round_up(solution[0], 3)
        x2 = round_up(solution[1], 3)
        x3 = round_up(solution[2], 3)

        system_of_equations_2 = f"x1 = {x1}\nx2 = {x2}\nx3 = {x3}\n"
        print(system_of_equations_2)

        for entity in layout:
            if entity.dxf.layer == 'Система уравнений 1':
                entity.text = system_of_equations_1
            elif entity.dxf.layer == 'Система уравнений 2':
                entity.text = system_of_equations_2


        print('-------"Эпюра Мок"-------')
        for rod in rods:
            Mok_1 = rod.diagram_M1[0] * x1 + rod.diagram_M2[0] * x2 + rod.diagram_M3[0] * x3 + rod.diagram_Mp[0]
            Mok_2 = rod.diagram_M1[1] * x1 + rod.diagram_M2[1] * x2 + rod.diagram_M3[1] * x3 + rod.diagram_Mp[1]
            rod.diagram_Mok = [round_up(Mok_1), round_up(Mok_2)]
            if len(rod.diagram_Mp) == 3:
                rod.diagram_Mok.append(rod.diagram_Mp[2])
            print(f'{rod} ------ {rod.diagram_Mok}')
        print(f'\n')

        print('-------Деформационная проверка-------')
        deformation_check = '\n\n'
        delta_sok_text, delta_sok = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Mok')
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





        print('-------"Эпюра Q"-------')
        for rod in rods:
            if len(rod.diagram_Mok) == 2:
                Q = (rod.diagram_Mok[0] - rod.diagram_Mok[1]) / rod.length()
                rod.diagram_Q = [round_up(Q), round_up(Q)]
            else:
                rod.diagram_Q = []
            print(f'{rod} ------ {rod.diagram_Q}')

        r = [4.65, -1.09, 9.8, -0.05, -5.95, -0.17, -0.05, -5.95, -0.17, 1.09, 9.8, 4.65]
        i = 0
        for reaction in frame.reactions():
            reaction.value = r[i]
            frame.finded_reactions.append(reaction)
            i += 1

        for reaction in frame.finded_reactions:
            print(reaction)
        print(f'\n')

        print('-------Статическая проверка-------')
        static_check = '\n\n'
        # node_name = str(input("\nВведите имя, относительно которого хотите составить уравнение моментов: "))
        node_name = 'L'
        for node in frame.nodes:
            if node.name == node_name:
                node_for_checking = node
        if node_for_checking:
            check_moment, check_equation = frame.sum_momentum_about_node(node=node_for_checking)
        else:
            raise Exception("Задано неверное имя узла")
        static_check_1 = check_equation + '\n' + f'   {check_moment} = 0\n' + 'Проверка выполняется\n\n'
        print(check_equation)
        print(f'   {check_moment} = 0')
        if abs(check_moment) <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = frame.sum_force_projections('x')
        print(f'∑x: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_2 = (f'∑x: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {sum_of_projections} = 0\n' + 'Проверка выполняется\n\n')

        sum_of_projections, sum_force_expression_names, sum_force_expression_values = frame.sum_force_projections('y')
        print(f'∑y: {sum_force_expression_names} = 0')
        print(f'    {sum_force_expression_values} = 0')
        print(f'    {sum_of_projections} = 0')
        if sum_of_projections <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}")

        static_check_3 = (f'∑y: {sum_force_expression_names} = 0\n' + f'    {sum_force_expression_values} = 0\n' +
                          f'    {sum_of_projections} = 0\n' + 'Проверка выполняется\n')

        static_check = static_check_1 + static_check_2 + static_check_3
        for entity in layout:
            if entity.dxf.layer == 'Статическая проверка':
                entity.text = static_check





        print(f'\n')

        print('-------Перемещение точки К-------')
        rod1_diagram_Mk = [0, 0.51]
        rod2_diagram_Mk = [0.51, -0.88]
        rod3_diagram_Mk = [0.88, 0]
        rod4_diagram_Mk = [0, 0.88]
        rod5_diagram_Mk = [-0.27, -0.78]
        rod6_diagram_Mk = [0, -0.27]
        rod7_diagram_Mk = [0, 0]


        mk = [rod1_diagram_Mk, rod2_diagram_Mk, rod3_diagram_Mk, rod4_diagram_Mk, rod5_diagram_Mk, rod6_diagram_Mk, rod7_diagram_Mk]

        rods = calculation_frame.rods
        i = 0
        for rod in rods:
            rod.diagram_Mk = mk[i]
            i += 1


        delta_kok_text, delta_kok = calculation_frame.multiply_M_diagrams_by_Simpson('Mk', 'Mok')
        delta_k_text = f'Δ\\H0.5x;k\\H2.0x; = {delta_kok_text}\n'
        print(f'Δk = {delta_kok_text}\n')

        for entity in layout:
            if entity.dxf.layer == 'Перемещение точки К':
                entity.text = delta_k_text

        for f in sf:
            frame_1 = sf[f]
            frame_1, msp, base_point = draw_frame(frame=frame_1, base_point=base_point, msp=msp, diagram_name=f[3:])


        zoom.extents(msp)
        doc.saveas(f'report.dxf')
