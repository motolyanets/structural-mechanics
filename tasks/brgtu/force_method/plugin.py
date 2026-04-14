from pathlib import Path
from typing import Dict, Any

from core.mechanics.solver import SolvableFrame
from services.services import round_up, making_report_of_multiply
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

        multiply_M1_M1 = []
        for rod in rods:
            multiply_M1_M1.append(rod.multiply_diagrams_Simpson('M1', 'M1'))
        delta_11_text, delta_11 = making_report_of_multiply(multiply_M1_M1)
        print("11 ----", delta_11_text)
        "Сделать из этого метод в SolvableFrame, чтобы тут просто вызывать его"


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
