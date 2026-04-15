from pathlib import Path
from typing import Dict, Any

import numpy

from core.mechanics.solver import SolvableFrame
from services.services import round_up, making_report_of_multiply, relative_error_percent
from tasks.base import TaskPlugin
from core.mechanics.load import Force, Momentum
from tasks.brgtu.force_method.loader import ForceMethodLoader


class BRGTUForceMethod(TaskPlugin):
    task_id = "force_method"
    task_name = "Метод сил"
    university = "brgtu"

    def _init_loader(self):
        self.loader = ForceMethodLoader(self.excel_path)

    def get_available_schemes(self) -> list:
        return [
            {"scheme_id": 27, "name": "Схема 27"},
            {"scheme_id": 29, "name": "Схема 29"},
        ]

    def solve(self, cipher: str) -> Dict[str, Any]:
        params = self.loader.load_cipher(cipher)
        circuit_number = params["circuit_number"]

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

        # print("Создаем исходную раму")
        # print("Создаем объект ОС")
        # print("\nРешаем М1")
        # print(" - Реакции опор")
        # print(" - Проверка")
        # print(" - Построение эпюры")
        # print("\nРешаем М2")
        # print(" - Реакции опор")
        # print(" - Проверка")
        # print(" - Построение эпюры")
        # print("\nРешаем М3")
        # print(" - Реакции опор")
        # print(" - Проверка")
        # print(" - Построение эпюры")
        # print("\nРешаем Мs")
        # print("\nРешаем Мp")
        # print(" - Реакции опор")
        # print(" - Проверка")
        # print(" - Построение эпюры")
        # print("\nОпределяем коэффициенты с помощью перемножения эпюр")
        # print("\nУниверсальная проверка Ms^2")
        # print("\nСтолбцовая проверка Ms*Mp")
        # print("\nРешение системы уравнений")
        # print("\nРешаем Мok")
        # print("\nДеформационная проверка Ms*Mok")
        # print("\nПостроение Qok")
        # print("\nПостроение Nok")
        # print("\nПостроение Nok")
        # print("\nСтатическая проверка исходной рамы")
        # print("\nОпределение перемещения в точке К")
        # print(" - Реакции опор")
        # print(" - Проверка")
        # print(" - Построение эпюры Mk")
        # print(" - Перемножение  Mk*Mok")

        if circuit_number == 27:
            from schemes.brgtu.force_method.frame_27 import create_frame_27, create_primary_system_27
            nodes, rods, supports, loads = create_frame_27(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_27(params)
        elif circuit_number == 29:
            from schemes.brgtu.force_method.frame_29 import create_frame_29, create_primary_system_29
            nodes, rods, supports, loads = create_frame_29(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_29(params)
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        from schemes.base import Frame
        frame = Frame(nodes, rods, supports, loads)

        sf = {}
        calculation_frame = SolvableFrame(nodes=ps_nodes, rods=ps_rods, supports=ps_supports, loads=loads)
        for load in ps_loads:
            fr = SolvableFrame(nodes=ps_nodes, rods=ps_rods, supports=ps_supports, loads=ps_loads[load])
            sf[f'sf_{load}'] = fr.classify_part()

        for f in sf:
            print(f)
            frame_1 = sf[f]
            frame_1.solve_frame()

        rod1_diagram_M1 = [0, 4.88]
        rod2_diagram_M1 = [4.88, 2.44]
        rod3_diagram_M1 = [2.44, 0]
        rod4_diagram_M1 = [0, -2.08]
        rod5_diagram_M1 = [-0.15, -0.43]
        rod6_diagram_M1 = [0, -0.15]
        rod7_diagram_M1 = [-2.5, 0]

        rod1_diagram_M2 = [0, 0.51]
        rod2_diagram_M2 = [0.51, 0.255]
        rod3_diagram_M2 = [0.255, 0]
        rod4_diagram_M2 = [0, -0.21]
        rod5_diagram_M2 = [-0.27, -0.78]
        rod6_diagram_M2 = [0, -0.27]
        rod7_diagram_M2 = [-1, -1]

        rod1_diagram_M3 = [0, 1.29]
        rod2_diagram_M3 = [1.29, 0.645]
        rod3_diagram_M3 = [0.645, 0]
        rod4_diagram_M3 = [0, -0.53]
        rod5_diagram_M3 = [1.8, 0.53]
        rod6_diagram_M3 = [0, 1.8]
        rod7_diagram_M3 = [0, 0]

        rod1_diagram_Mp = [0, -0.46]
        rod2_diagram_Mp = [-0.46, -17.3]
        rod3_diagram_Mp = [-17.3, 0]
        rod4_diagram_Mp = [0, 14.81]
        rod5_diagram_Mp = [0.25, 0.71]
        rod6_diagram_Mp = [0, 0.25]
        rod7_diagram_Mp = [15.49, 0, 1.6]


        m1 = [rod1_diagram_M1, rod2_diagram_M1, rod3_diagram_M1, rod4_diagram_M1, rod5_diagram_M1, rod6_diagram_M1, rod7_diagram_M1]
        m2 = [rod1_diagram_M2, rod2_diagram_M2, rod3_diagram_M2, rod4_diagram_M2, rod5_diagram_M2, rod6_diagram_M2, rod7_diagram_M2]
        m3 = [rod1_diagram_M3, rod2_diagram_M3, rod3_diagram_M3, rod4_diagram_M3, rod5_diagram_M3, rod6_diagram_M3, rod7_diagram_M3]
        mp = [rod1_diagram_Mp, rod2_diagram_Mp, rod3_diagram_Mp, rod4_diagram_Mp, rod5_diagram_Mp, rod6_diagram_Mp, rod7_diagram_Mp]

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

        delta_11_text, delta_11 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M1')
        delta_12_text, delta_12 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M2')
        delta_13_text, delta_13 = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'M3')
        delta_22_text, delta_22 = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'M2')
        delta_23_text, delta_23 = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'M3')
        delta_33_text, delta_33 = calculation_frame.multiply_M_diagrams_by_Simpson('M3', 'M3')
        delta_1p_text, delta_1p = calculation_frame.multiply_M_diagrams_by_Simpson('M1', 'Mp')
        delta_2p_text, delta_2p = calculation_frame.multiply_M_diagrams_by_Simpson('M2', 'Mp')
        delta_3p_text, delta_3p = calculation_frame.multiply_M_diagrams_by_Simpson('M3', 'Mp')
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
        delta_ss_text, delta_ss = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Ms')
        print(f'δss = {delta_ss_text}\n')
        sum_delta = delta_11 + delta_12 * 2 + delta_13 * 2 + delta_22 + delta_23 * 2 + delta_33
        print(f'δ11 + δ12·2 + δ13·2 + δ22 + δ23·2 + δ33 = {delta_11}/EI + 2·{delta_12}/EI + 2·{delta_13}/EI + {delta_22}/EI + 2·{delta_23}/EI + {delta_33}/EI = {sum_delta}/EI\n')
        E_uni_check, e_text_uni_check = relative_error_percent(delta_ss, sum_delta, tolerance_percent=3)

        print('-------Столбцовая проверка-------')
        delta_sp_text, delta_sp = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Mp')
        print(f'δsp = {delta_sp_text}\n')
        sum_delta = delta_1p + delta_2p + delta_3p
        print(f'Δ1p + Δ2p + Δ3p = {delta_1p}/EI + {delta_2p}/EI + {delta_3p}/EI = {sum_delta}/EI\n')
        E_uni_check, e_text_uni_check = relative_error_percent(delta_sp, sum_delta, tolerance_percent=3)

        print('-------Решение системы уравнений-------')
        print(f'({delta_11}/EI)·x1 + ({delta_12}/EI)·x2 +({delta_13}/EI)·x3 + {delta_1p}/EI = 0')
        print(f'({delta_12}/EI)·x1 + ({delta_22}/EI)·x2 +({delta_23}/EI)·x3 + {delta_2p}/EI = 0')
        print(f'({delta_13}/EI)·x1 + ({delta_23}/EI)·x2 +({delta_33}/EI)·x3 + {delta_3p}/EI = 0\n')

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
        print(f"x1 = {x1}\nx2 = {x2}\nx3 = {x3}\n")

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
        delta_sok_text, delta_sok = calculation_frame.multiply_M_diagrams_by_Simpson('Ms', 'Mok')
        print(f'δsok = {delta_sok_text}\n')
        print(f'δsok = {delta_sok}/EI ≈ 0')
        if delta_sok <= 0.1:
            print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}\n")
        else:
            print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}\n")

        # minus_results = 0
        # plus_results = 0

        # for m in multiply_Ms_Mok:
        #     if m[1] > 0:
        #         plus_results += m[1]
        #     else:
        #         minus_results += m[1]

        # delta_sok_text, delta_sok = making_report_of_multiply(multiply_Ms_Mok)
        # print("sok ----", delta_sok_text)
        # E = (minus_results + plus_results) / min(abs(minus_results), plus_results) * 100
        # print(f'({minus_results} + {plus_results}) / {min(abs(minus_results), plus_results)} * 100 = {E}')

        # inner_reactions = []
        # for i, part in enumerate(parts_of_frame):
        #     if i > 1:
        #         break
        #
        #     if inner_reactions:
        #         for reaction in inner_reactions:
        #             if reaction.node in part.nodes:
        #                 new_reaction = Force(
        #                     name=reaction.name,
        #                     node=reaction.node,
        #                     rotation=reaction.rotation + 180,
        #                     value=reaction.value
        #                 )
        #                 part.loads.append(new_reaction)
        #
        #     part.solve_frame()
        #
        #     for reaction in part.finded_reactions:
        #         if reaction not in inner_reactions:
        #             inner_reactions.append(reaction)
        #
        # result = {
        #     "cipher": cipher,
        #     "scheme": circuit_number,
        #     "params": params,
        #     "reactions": {}
        # }
        #
        # for reaction in inner_reactions:
        #     result["reactions"][reaction.name] = {
        #         "value": reaction.value,
        #         "rotation": reaction.rotation
        #     }
        #
        # return result
