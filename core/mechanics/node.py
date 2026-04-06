from dataclasses import dataclass


class Node:
    """Узел расчётной схемы"""
    def __init__(
            self,
            x: float,
            y: float,
            name: str | None = None,
            is_hinge: bool = False,
    ):
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.is_hinge = is_hinge


    def __repr__(self) -> str:
        return f"Node({self.name}, [{self.x}, {self.y}])"
