from typing import Dict, Any

from tasks.base import TaskPlugin
from tasks.brgtu.composite_frame.loader import CompositeFrameLoader
from core.mechanics.load import Force


class BRGTUCompositeFrame(TaskPlugin):
    task_id = "composite_frame"
    task_name = "Составная рама"
    university = "brgtu"

    def _init_loader(self):
        self.loader = CompositeFrameLoader(self.excel_path)

    def get_available_schemes(self) -> list:
        return [
            {"scheme_id": 24, "name": "Схема 24"},
            {"scheme_id": 29, "name": "Схема 29"}
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
        print(f"  F = {params['F']} кН")
        print(f"  P = {params['P']} кН")
        print(f"  q = {params['q']} кН/м")
        print(f"  m = {params['m']} кН·м")
        print(f"  load_index = {params['load_index']}")
        print(f"{'=' * 60}")

        if circuit_number == 24:
            from schemes.brgtu.composite_frame.frame_24 import create_frame_24
            nodes, rods, supports, loads, splitted_order = create_frame_24(params)
        elif circuit_number == 29:
            from schemes.brgtu.composite_frame.frame_29 import create_frame_29
            nodes, rods, supports, loads, splitted_order = create_frame_29(params)
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        from schemes.brgtu.composite_frame.base_composit_frame import CompositeFrame
        frame = CompositeFrame(nodes, rods, supports, loads, splitted_order)

        parts_of_frame = frame.split_frame()

        inner_reactions = []
        for i, part in enumerate(parts_of_frame):
            if i > 1:
                break

            if inner_reactions:
                for reaction in inner_reactions:
                    if reaction.node in part.nodes:
                        new_reaction = Force(
                            name=reaction.name,
                            node=reaction.node,
                            rotation=reaction.rotation + 180,
                            value=reaction.value
                        )
                        part.loads.append(new_reaction)

            part.solve_frame()

            for reaction in part.finded_reactions:
                if reaction not in inner_reactions:
                    inner_reactions.append(reaction)

        result = {
            "cipher": cipher,
            "scheme": circuit_number,
            "params": params,
            "reactions": {}
        }

        for reaction in inner_reactions:
            result["reactions"][reaction.name] = {
                "value": reaction.value,
                "rotation": reaction.rotation
            }

        return result
