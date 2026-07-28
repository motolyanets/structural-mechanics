from logging import raiseExceptions
from pathlib import Path
from typing import Dict, Any

from core.base_excel_loader import BaseExcelLoader


class MultiSpanBeamLoader(BaseExcelLoader):
    """
    Загрузчик для составной рамы.
    Знает структуру: cipher_1, cipher_2, cipher_3, cipher_4
    """

    def load_cipher(self, cipher: str) -> Dict[str, Any]:
        """
        Загружает параметры по 4-значному шифру.

        Returns:
            dict: {
                "circuit_number": int,
                "load_number": int,
                "a": float,
                "b": float,
                "c": float,
                "d": float,
                "P1": float,
                "P2": float,
                "P3": float,
                "q1": float,
                "q2": float,
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
        load_part1 = third_data.get("load_part")
        load_part2 = fourth_data.get("load_part")

        if circuit_part1 is None or circuit_part2 is None:
            raise ValueError("Не найдены поля 'circuit_part' в данных")
        if load_part1 is None or load_part2 is None:
            raise ValueError("Не найдены поля 'load_part' в данных")

        circuit_number = int(f"{int(circuit_part1)}{int(circuit_part2)}")
        load_number = int(f"{int(load_part1)}{int(load_part2)}")

        return {
            "circuit_number": circuit_number,
            "load_number": load_number,
            "a": float(first_data.get("a", 0)),
            "b": float(second_data.get("b", 0)),
            "c": float(third_data.get("c", 0)),
            "d": float(fourth_data.get("d", 0)),
            "P1": float(first_data.get("p1", 0)),
            "P2": float(second_data.get("p2", 0)),
            "P3": float(third_data.get("p3", 0)),
            "q1": float(third_data.get("q1", 0)),
            "q2": float(fourth_data.get("q2", 0)),
        }

    # def get_scheme_from_cipher(self, cipher: str) -> int:
    #     """Возвращает номер схемы по шифру"""
    #     digits = [int(d) for d in cipher]
    #     first_data = self._get_sheet_data("cipher_1").get(digits[0])
    #     second_data = self._get_sheet_data("cipher_2").get(digits[1])
    #
    #     circuit_part1 = first_data.get("circuit_part")
    #     circuit_part2 = second_data.get("circuit_part")
    #
    #     return int(f"{int(circuit_part1)}{int(circuit_part2)}")
