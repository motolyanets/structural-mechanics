from services.services import round_up


class Node:
    """Узел расчётной схемы"""
    def __init__(
            self,
            x: float,
            y: float,
            name: str | None = None,
            is_hinge: bool = False,
    ):
        self.x = round_up(float(x), 6)
        self.y = round_up(float(y), 6)
        self.y = float(y)
        self.name = name
        self.is_hinge = is_hinge


    def __repr__(self) -> str:
        return f"Node({self.name}, [{self.x}, {self.y}])"
