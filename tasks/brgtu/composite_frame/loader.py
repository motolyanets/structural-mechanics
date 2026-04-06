from logging import raiseExceptions
from pathlib import Path
from typing import Dict, Any

from core.base_excel_loader import BaseExcelLoader


class CompositeFrameLoader(BaseExcelLoader):
    """
    Загрузчик для составной рамы.
    Знает структуру: cipher_1, cipher_2, cipher_3, cipher_4
    """

    def load_cipher(self, cipher: str) -> Dict[str, Any]:
        """
        Загружает параметры по 4-значному шифру.

        Returns:
            dict: {
                "circuit_number": int,  # номер схемы (24 или 29)
                "l1": float,
                "l2": float,
                "h1": float,
                "h2": float,
                "load_index": int,
                "F": float,
                "P": float,
                "q": float,
                "m": float
            }
        """
        if not cipher.isdigit() or len(cipher) != 4:
            raise ValueError(f"Шифр должен быть 4 цифры: {cipher}")

        digits = [int(d) for d in cipher]

        # Загружаем данные с каждого листа
        first_data = self._get_sheet_data("cipher_1").get(digits[0])
        second_data = self._get_sheet_data("cipher_2").get(digits[1])
        third_data = self._get_sheet_data("cipher_3").get(digits[2])
        fourth_data = self._get_sheet_data("cipher_4").get(digits[3])

        if first_data is None:
            raise ValueError(f"Цифра {digits[0]} не найдена на листе 'cipher_1'")
        if second_data is None:
            raise ValueError(f"Цифра {digits[1]} не найдена на листе 'cipher_2'")
        if third_data is None:
            raise ValueError(f"Цифра {digits[2]} не найдена на листе 'cipher_3'")
        if fourth_data is None:
            raise ValueError(f"Цифра {digits[3]} не найдена на листе 'cipher_4'")

        # Формируем номер схемы
        circuit_part1 = first_data.get("circuit_part")
        circuit_part2 = second_data.get("circuit_part")

        if circuit_part1 is None or circuit_part2 is None:
            raise ValueError("Не найдены поля 'circuit_part' в данных")

        circuit_number = int(f"{int(circuit_part1)}{int(circuit_part2)}")

        return {
            "circuit_number": circuit_number,
            "l1": float(first_data.get("l1", 0)),
            "l2": float(second_data.get("l2", 0)),
            "h1": float(third_data.get("h1", 0)),
            "h2": float(fourth_data.get("h2", 0)),
            "load_index": int(third_data.get("load_index", 3)),
            "F": float(first_data.get("f", 0)),
            "P": float(second_data.get("p", 0)),
            "q": float(third_data.get("q", 0)),
            "m": float(fourth_data.get("m", 0))
        }

    def get_scheme_from_cipher(self, cipher: str) -> int:
        """Возвращает номер схемы по шифру"""
        digits = [int(d) for d in cipher]
        first_data = self._get_sheet_data("cipher_1").get(digits[0])
        second_data = self._get_sheet_data("cipher_2").get(digits[1])

        circuit_part1 = first_data.get("circuit_part")
        circuit_part2 = second_data.get("circuit_part")

        return int(f"{int(circuit_part1)}{int(circuit_part2)}")
