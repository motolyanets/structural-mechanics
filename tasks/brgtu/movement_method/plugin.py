from typing import Dict, Any

import ezdxf
from ezdxf import zoom

from core.mechanics.frame import Frame
from core.mechanics.load import Twist, Displacement, Force
from core.mechanics.solver import FrameForMovementMethod, SolvableFrame
from services.authocad import draw_frame
from services.services import round_up
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

        frame = Frame(fr_nodes, fr_rods, fr_supports, fr_loads)

        for entity in layout:
            if entity.dxf.layer == "1.Главная рама" and entity.dxftype() == 'VIEWPORT':
                if entity:
                    entity.dxf.view_center_point = (frame.geometrical_center()[0], frame.geometrical_center()[1], 0.0)
        frame, msp, base_point = draw_frame(frame=frame, base_point=base_point, msp=msp)

        diagrams = ['1', '2', '3', 'p']
        mm_frames = []

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
            print(calculating_diagram_report)


        load_z1 = mm_loads['1']
        load_z2 = mm_loads['2']
        load_z3 = mm_loads['3']

        print(load_z1)
        print(load_z2)
        print(load_z3)

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


        finded_coefficients = dict()

        for frame in mm_frames:
            coefficients, reports = calculation_r(frame, mm_loads)
            print(reports)

            for c in coefficients:
                coefficient = f'{c[0]}{c[2]}{c[1]}'
                if coefficient not in finded_coefficients:
                    finded_coefficients[c] = coefficients[c]
                else:
                    if finded_coefficients[coefficient] != coefficients[c]:
                        raise Exception(f'{coefficient} = {finded_coefficients[coefficient]} ....{c} = {coefficients[c]}')

        print(finded_coefficients)

        for i in ['s']:
            fm_nodes, fm_rods, fm_supports, fm_loads = new_fm_frame(params)

            fm_frame = SolvableFrame(nodes=fm_nodes, rods=fm_rods, supports=fm_supports, loads=fm_loads).classify_part()
            fm_frame.solve_frame()









        # frame = SolvableFrame(fr_nodes, fr_rods, fr_supports, fr_loads)
        #
        # ms = [[-0.476, 0.925], [0, 0], [-2.536, -0.845], [-0.845, 0.845], [0.845, 2.536], [-0.546, 0], [-0.919, 0], [0, 0.714], [0, -0.211 / 2], [-0.211 / 2, -0.211]]
        # i = 0
        # for rod in frame.rods:
        #     rod.diagram_Ms = ms[i]
        #
        # delta_ss_text, delta_ss = frame.multiply_M_diagrams_by_Simpson('Ms', 'Ms')
        # print(f'δss = {delta_ss_text}\n')





        zoom.extents(msp)
        doc.saveas(f'report.dxf')
