from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

from core.mechanics.frame import Frame
from core.mechanics.solver import SolvableFrame


class TaskPlugin(ABC):
    task_id: str
    task_name: str
    university: str

    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self._init_loader()

    @abstractmethod
    def _init_loader(self):
        pass

    @abstractmethod
    def solve(self, cipher: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_available_schemes(self) -> list:
        pass
