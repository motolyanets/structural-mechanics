from pathlib import Path
from typing import Dict, Any

from core.mechanics.solver import SolvableFrame
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

        print("Создаем исходную раму")
        print("Создаем объект ОС")
        print("\nРешаем М1")
        print(" - Реакции опор")
        print(" - Проверка")
        print(" - Построение эпюры")
        print("\nРешаем М2")
        print(" - Реакции опор")
        print(" - Проверка")
        print(" - Построение эпюры")
        print("\nРешаем М3")
        print(" - Реакции опор")
        print(" - Проверка")
        print(" - Построение эпюры")
        print("\nРешаем Мs")
        print("\nРешаем Мp")
        print(" - Реакции опор")
        print(" - Проверка")
        print(" - Построение эпюры")
        print("\nОпределяем коэффициенты с помощью перемножения эпюр")
        print("\nУниверсальная проверка Ms^2")
        print("\nСтолбцовая проверка Ms*Mp")
        print("\nРешение системы уравнений")
        print("\nРешаем Мok")
        print("\nДеформационная проверка Ms*Mok")
        print("\nПостроение Qok")
        print("\nПостроение Nok")
        print("\nПостроение Nok")
        print("\nСтатическая проверка исходной рамы")
        print("\nОпределение перемещения в точке К")
        print(" - Реакции опор")
        print(" - Проверка")
        print(" - Построение эпюры Mk")
        print(" - Перемножение  Mk*Mok")

        if circuit_number == 27:
            from schemes.brgtu.force_method.frame_27 import create_frame_27, create_primary_system_27
            nodes, rods, supports, loads = create_frame_27(params)
            ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_27(params)
        # # elif circuit_number == 29:
        # #     from schemes.brgtu.composite_frame.frame_29 import create_frame_29
        # #     nodes, rods, supports, loads, splitted_order = create_frame_29(params)
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        from schemes.base import Frame
        frame = Frame(nodes, rods, supports, loads)

        sf = {}
        for load in ps_loads:
            fr = SolvableFrame(nodes=ps_nodes, rods=ps_rods, supports=ps_supports, loads=ps_loads[load])
            sf[f'sf_{load}'] = fr.classify_part()

        for f in sf:
            print(f)
            frame_1 = sf[f]
            frame_1.solve_frame()
            print(frame_1.finded_reactions)

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
