from typing import List

from services.services import round_up, normalize_equation


class Section:
    """Сечение для расчета и построения эпюр"""
    def __init__(
            self,
            x: float,
            y: float,
            x_drawing: float,
            y_drawing: float,
            name: str,
            loads: List,
            is_hinge: bool = False,
    ):
        self.x = float(x)
        self.y = float(y)
        self.x_drawing = float(x_drawing)
        self.y_drawing = float(y_drawing)
        self.name = name
        self.loads = loads
        self.is_hinge = is_hinge

    def sum_momentum_in_section(self):
        from core.mechanics.load import Force, Momentum, DistributedForce

        all_loads = self.loads
        point = (self.x, self.y)
        moment = 0
        equation = ''
        for load in all_loads:
            if isinstance(load, Force):
                text, moment_of_load = load.get_moment_about(point=point)
                moment += moment_of_load
                equation += f'+ {text} '
            elif isinstance(load, Momentum):
                if load.rotation:
                    moment += load.value
                    equation += f'+{load.name} '
                else:
                    moment -= load.value
                    equation += f'-{load.name} '
            if isinstance(load, DistributedForce):
                text, moment_of_load = load.get_moment_about(point=point)
                moment += moment_of_load
                equation += f'+ {text} '

        moment = round_up(moment, 3)
        equation = f'∑M({self.name}): ' + normalize_equation(equation) + ' = 0'
        return moment, equation

    def sum_momentum_about_section(self):
        from core.mechanics.load import Force, Momentum, DistributedForce

        if self.is_hinge:
            moment = 0
            equation = f'M({self.name}) = 0'
        else:
            all_loads = self.loads

            point = (self.x, self.y)
            moment = 0
            equation = ''
            for load in all_loads:
                if isinstance(load, Force):
                    text, moment_of_load = load.get_moment_about(point=point)
                    moment += moment_of_load
                    equation += f'+ {text} '
                elif isinstance(load, Momentum):
                    if load.rotation:
                        moment += load.value
                        equation += f'+{load.name} '
                    else:
                        moment -= load.value
                        equation += f'-{load.name} '
                if isinstance(load, DistributedForce):
                    text, moment_of_load = load.get_moment_about(point=point)
                    moment += moment_of_load
                    equation += f'+ {text} '

            moment = round_up(moment, 3)
            equation = f'M({self.name}) =' + normalize_equation(equation) + ' = ' + str(moment)
        return moment, equation


    def __repr__(self) -> str:
        return f"Section --- {self.name} ({self.x};{self.y})-----{self.loads}"
