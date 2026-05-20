from typing import Dict, Any

import ezdxf
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.solver import SolvableFrame
from services.authocad import draw_frame
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
            # {"scheme_id": 22, "name": "Схема 22"},
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

        if circuit_number == 17:
            from schemes.brgtu.movement_method.frame_17 import create_frame_17, create_primary_system_17
            fr_nodes, fr_rods, fr_supports, fr_loads = create_frame_17(params)
            # ps_nodes, ps_rods, ps_supports, ps_loads = create_primary_system_17(params)
        else:
            raise ValueError(f"Схема {circuit_number} не реализована")

        frame = Frame(fr_nodes, fr_rods, fr_supports, fr_loads)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (frame.geometrical_center()[0], frame.geometrical_center()[1], 0.0)
        frame, msp, base_point = draw_frame(frame=frame, base_point=base_point, msp=msp)

        frame = SolvableFrame(fr_nodes, fr_rods, fr_supports, fr_loads)

        ms = [[-0.476, 0.925], [0, 0], [-2.536, -0.845], [-0.845, 0.845], [0.845, 2.536], [-0.546, 0], [-0.919, 0], [0, 0.714], [0, -0.211 / 2], [-0.211 / 2, -0.211]]
        i = 0
        for rod in frame.rods:
            rod.diagram_Ms = ms[i]

        delta_ss_text, delta_ss = frame.multiply_M_diagrams_by_Simpson('Ms', 'Ms')
        print(f'δss = {delta_ss_text}\n')





        zoom.extents(msp)
        doc.saveas(f'report.dxf')
