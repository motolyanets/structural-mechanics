import unittest
import warnings
from unittest.mock import patch
from io import StringIO
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath('../../..'))
t = 0.6

def check_absolute_difference(actual, expected, tolerance):
    """
    Проверяет, что абсолютная разница между actual и expected меньше tolerance.

    Args:
        actual: фактическое значение
        expected: ожидаемое значение
        tolerance: допустимая разница

    Returns:
        bool: True если разница в допуске
        float: абсолютная разница
    """
    diff = abs(actual - expected)
    return diff < tolerance, diff


def compare_moment_lists(actual_list, expected_list, tolerance):
    """
    Сравнивает два списка эпюр моментов с заданным допуском.

    Args:
        actual_list: фактический список m_ok_output
        expected_list: ожидаемый список
        tolerance: допустимая абсолютная разница (по умолчанию 0.5)

    Returns:
        list: список ошибок (пустой если всё хорошо)
    """
    errors = []

    # Проверяем количество стержней
    if len(actual_list) != len(expected_list):
        errors.append(f"Разное количество стержней: {len(actual_list)} != {len(expected_list)}")
        return errors

    # Проверяем каждый стержень
    for i, (actual_rod, expected_rod) in enumerate(zip(actual_list, expected_list)):
        if len(actual_rod) != len(expected_rod):
            errors.append(f"Стержень {i + 1}: разная длина {len(actual_rod)} != {len(expected_rod)}")
            continue

        # Проверяем каждую точку
        for j, (actual_val, expected_val) in enumerate(zip(actual_rod, expected_rod)):
            is_ok, diff = check_absolute_difference(actual_val, expected_val, tolerance)
            if not is_ok:
                errors.append(
                    f"Стержень {i + 1}, точка {j + 1}: "
                    f"значение {actual_val}, ожидалось {expected_val}, "
                    f"разница {diff:.6f} > допуск {tolerance}"
                )

    return errors


class TestBrgtuForceMethod(unittest.TestCase):
    """Тесты для проверки эпюр моментов m_ok_output"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='ezdxf')
        self.tolerance = t  # можно менять для разных тестов

    @patch('sys.stdin', StringIO('2\n3025\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_10_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 0.15], [-10.55, -1.97], [0, -10.55], [-1.82, 0.82, 12.2], [0.0, -12.2], [0, 0], [0, 0],
                                [0, 0], [0, 0], [0, 12.2], [12.2, 0.82, -1.82], [10.55, 1.97], [0, 10.55], [0.15, 0]]
        expected_q_ok_output = [[-0.05, -0.05], [-3.81, -3.81], [4.69, 4.69], [0.63, -5.73], [3.81, 3.81], [0, 0], [0, 0],
                                [0, 0], [0, 0], [-3.81, -3.81], [5.73, -0.63], [3.81, 3.81], [-4.69, -4.69], [0.05, 0.05]]
        expected_n_ok_output = [[0, 0], [-2.5, -2.5], [-2.5, -2.5], [-4.49, -1.56], [-4.55, -4.55], [-4.55, -4.55],
                                [-3.81, -3.81], [-3.81, -3.81], [-4.55, -4.55], [-4.55, -4.55], [-1.56, -4.49],
                                [-2.5, -2.5], [-2.5, -2.5], [0, 0]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n3024\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_10_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -7.08], [-7.08, -1.41], [1.1, 4.31, 9.29], [0, -0.34, 1.1], [7.87, -10.19], [0, 10.19],
                                [0, 0], [0, 0], [0, 0], [0, 0], [0, -10.19], [-10.19, 7.87], [-1.1, -4.31, -9.29],
                                [0, 0.34, -1.1], [-1.41, -7.08], [-7.08, 0]]
        expected_q_ok_output = [[4.72, 4.72], [-3.78, -3.78], [-2.06, -5.21], [1.09, -2.06], [3.31, 3.31], [-3.29, -3.29],
                                [0, 0], [0, 0], [0, 0], [0, 0], [3.29, 3.29], [-3.31, -3.31], [2.06, 5.21], [-1.09, 2.06],
                                [3.78, 3.78], [-4.72, -4.72]]
        expected_n_ok_output = [[0, 0], [0, 0], [-9.68, -9.68], [-9.68, -9.68], [-7.15, -7.15], [5.91, 5.91], [5.91, 5.91],
                                [3.28, 3.28], [3.28, 3.28], [5.91, 5.91], [5.91, 5.91], [-7.15, -7.15], [-9.68, -9.68],
                                [-9.68, -9.68], [0, 0], [0, 0]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1111\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_11_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 6.62], [6.62, -9.91], [0, -0.9, 2.86], [-0.56, 0], [-6.48, -11.99], [-11.99, 0.0],
                                [0, 0], [0, 0], [0, 0], [0.0, -11.99], [-11.99, -6.48], [0.56, 0], [0, 0.9, -2.86],
                                [-9.91, 6.62], [0, -6.62]]
        expected_q_ok_output = [[-1.65, -1.65], [2.2, 2.2], [1.68, -3.12], [-0.15, -0.15], [2.2, 2.2], [-4.8, -4.8],
                                [0, 0], [0, 0], [0, 0], [4.8, 4.8], [-2.2, -2.2], [0.15, 0.15], [-1.68, 3.12], [-2.2, -2.2],
                                [1.65, 1.65]]
        expected_n_ok_output = [[-2.2, -2.2], [-1.65, -1.65], [0, 0], [0, 0], [-4.62, -4.62], [-4.62, -4.62],
                                [-9.59, -9.59], [-0.15, -0.15], [-0.15, -0.15], [-4.62, -4.62], [-4.62, -4.62], [0, 0],
                                [0, 0], [-1.65, -1.65], [-2.2, -2.2]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1112\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_11_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -0.96], [-0.96, 12.08], [12.08, -5.3, -5.8], [0, -2.44], [2.33, 0], [-10.57, -5.29],
                                [-5.29, 0.0], [0, 0], [0, 0], [0, 0], [0.0, -5.29], [-5.29, -10.57], [-2.33, 0],
                                [0, 2.44], [-5.8, -5.3, 12.08], [0, 0.96], [0.96, -12.08]]
        expected_q_ok_output = [[0.48, 0.48], [-6.52, -6.52], [6.89, -2.11], [0.61, 0.61], [0.61, 0.61], [-2.11, -2.11],
                                [-2.11, -2.11], [0, 0], [0, 0], [0, 0], [2.11, 2.11], [2.11, 2.11], [-0.61, -0.61],
                                [-0.61, -0.61], [2.11, -6.89], [-0.48, -0.48], [6.52, 6.52]]
        expected_n_ok_output = [[-6.89, -6.89], [-6.89, -6.89], [-6.52, -6.5], [0, 0], [0, 0], [-6.52, -6.52],
                                [-6.52, -6.52], [-4.23, -4.23], [0.58, 0.58], [0.58, 0.58], [-6.52, -6.52],
                                [-6.52, -6.52], [0, 0], [0, 0], [-6.52, -6.52], [-6.89, -6.89], [-6.89, -6.89]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1211\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_12_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[9.81, -3.1], [-3.1, 0.0], [0.0, 3.22, 8.32], [0, -0.3], [-0.3, -0.6],
                                [7.72, -5.74, 0.0], [3.77, 0.0], [0, 3.77], [0, 0], [0, 0], [0, -3.77], [-3.77, -0.0],
                                [0.0, -5.74, 7.72], [0.3, 0.6], [0, 0.3], [8.32, 3.22, 0.0], [-9.81, 3.1], [3.1, -0.0]]
        expected_q_ok_output = [[6.45, 6.45], [-1.55, -1.55], [-1.83, -4.83], [0.15, 0.15], [0.15, 0.15], [5.61, -3.73],
                                [1.4, 1.4], [-1.18, -1.18], [0, 0], [0, 0], [1.18, 1.18], [-1.4, -1.4], [3.73, -5.61],
                                [-0.15, -0.15], [-0.15, -0.15], [4.83, 1.83], [-6.45, -6.45], [1.55, 1.55]]
        expected_n_ok_output = [[1.83, 1.83], [1.83, 1.83], [-1.55, -1.55], [-10.92, -10.92], [-10.92, -10.92],
                                [-2.77, -0.55], [-3.5, -3.5], [-3.5, -3.5], [-2.58, -2.58], [-2.58, -2.58], [-3.5, -3.5],
                                [-3.5, -3.5], [-0.55, -2.77], [-10.92, -10.92], [-10.92, -10.92], [-1.55, -1.55],
                                [1.83, 1.83], [1.83, 1.83]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1212\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_12_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[1.08, -1.86, 0.0], [0.0, -4.31], [0, -5.24], [-5.24, 5.52], [1.21, 0.0], [-1.37, 0.0],
                                [0, -1.37], [0, 0], [0, 0], [0, 1.37], [1.37, -0.0], [0.0, 1.21], [5.24, -5.50],
                                [0, 5.24], [-4.31, 0.0], [-1.08, 1.86, -0.0]]
        expected_q_ok_output = [[2.67, -2.13], [1.72, 1.72], [2.62, 2.62], [-5.38, -5.38], [0.15, 0.15], [-0.49, -0.49],
                                [0.43, 0.43], [0, 0], [0, 0], [-0.43, -0.43], [0.49, 0.49], [-0.15, -0.15], [5.38, 5.38],
                                [-2.62, -2.62], [-1.72, -1.72], [-2.67, 2.13]]
        expected_n_ok_output = [[-1.72, -1.72], [-2.13, -2.13], [-0.31, -0.31], [-0.31, -0.31], [-7.78, -7.78],
                                [2.03, 2.03], [2.03, 2.03], [0.92, 0.92], [0.92, 0.92], [2.03, 2.03], [2.03, 2.03],
                                [-7.78, -7.78], [-0.31, -0.31], [-0.31, -0.31], [-2.13, -2.13], [-1.72, -1.72]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1311\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_13_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -4.41, -6.95], [0, -6.16], [-13.11, 0.0], [0.0, -16.97], [-16.97, 4.32],
                                [-2.21, -4.32], [0, -2.21], [0, 0], [-13.91, 2.35, 0]]
        expected_q_ok_output = [[2.27, 0.68], [1.54, 1.54], [-3.45, -3.45], [3.99, 3.99], [-5.01, -5.01], [0.55, 0.55],
                                [0.55, 0.55], [0, 0], [-6.45, 2.9]]
        expected_n_ok_output = [[-13.05, -10.5], [5.27, 5.27], [-3.99, -3.99], [-3.45, -3.45], [-3.45, -3.45],
                                [-5.01, -5.01], [-5.01, -5.01], [-2.9, -2.9], [0, 0]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1312\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_13_2(self, mock_stdout):
        """Тест эпюр моментов для choice=2, cipher='1312'"""
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 9.2], [0, 6.99], [15.98, 5.59, 0.0], [0.0, -4.61], [-15.69, 4.61], [0, -15.69],
                                [0, 0], [-8.15, 13.93], [13.93, 0]]
        expected_q_ok_output = [[-1.9, -1.9], [-1.75, -1.75], [6.39, 1.59], [0.54, 0.54], [-5.08, -5.08], [3.92, 3.92],
                                [0, 0], [-5.52, -5.52], [3.48, 3.48]]
        expected_n_ok_output = [[18.41, 18.41], [-17.16, -17.16], [-0.54, -0.54], [1.59, 1.59], [0.54, 0.54], [0.54, 0.54],
                                [-3.48, -3.48], [0, 0], [0, 0]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n7495\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_14_1(self, mock_stdout):
        """Тест эпюр моментов для choice=2, cipher='1312'"""
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[15.32, 0.0], [0.0, -10.23, -0.05], [0, -17.19], [-17.24, 0.0], [0.0, -31.36, -8.04],
                                [-26.82, 8.04], [0, -26.82], [0, 0], [0, 0], [26.82, -8.04], [0, 26.82],
                                [-8.04, -31.36, 0.0], [17.24, -0.0], [-0.05, -10.23, 0.0], [0, 17.19], [-15.32, -0.0]]
        expected_q_ok_output = [[2.95, 2.95], [7.43, -7.42], [3.31, 3.31], [-3.75, -3.75], [12.53, -10.81],
                                [-4.84, -4.84], [5.16, 5.16], [0, 0], [0, 0], [4.84, 4.84], [-5.16, -5.16],
                                [10.81, -12.53], [3.75, 3.75], [7.42, -7.43], [-3.31, -3.31], [-2.95, -2.95]]
        expected_n_ok_output = [[-7.43, -7.43], [-7.05, -7.05], [-21.54, -21.54], [-14.13, -14.13], [-7.52, -0.78],
                                [-10.17, -10.17], [-10.17, -10.17], [-8.59, -8.59], [-8.59, -8.59], [-10.17, -10.17],
                                [-10.17, -10.17], [-0.78, -7.52], [-14.13, -14.13], [-7.05, -7.05], [-21.54, -21.54],
                                [-7.43, -7.43]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n7496\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_14_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[27.6, 0.8], [0.8, 0.0], [0.0, 3.42], [0, -17.18], [-13.77, -14.66, 0.0], [0.0, 16.13],
                                [23.88, -16.13], [0, 23.88], [0, 0], [0, 0], [-23.88, 16.13], [0, -23.88], [16.13, 0.0],
                                [13.77, 14.66, -0.0], [3.42, 0.0], [0, 17.18], [-27.6, -0.8], [-0.8, -0.0]]
        expected_q_ok_output = [[10.31, 10.31], [0.31, 0.31], [-0.62, -0.62], [3.3, 3.3], [3.61, -9.35], [-1.72, -1.72],
                                [5.41, 5.41], [-4.59, -4.59], [0, 0], [0, 0], [-5.41, -5.41], [4.59, 4.59], [1.72, 1.72],
                                [-3.61, 9.35], [0.62, 0.62], [-3.3, -3.3], [-10.31, -10.31], [-0.31, -0.31]]
        expected_n_ok_output = [[0.62, 0.62], [0.62, 0.62], [0.31, 0.31], [-1.53, -1.53], [-0.91, -0.91], [-9.23, -9.23],
                                [0.91, 0.91], [0.91, 0.91], [-3.94, -3.94], [-3.94, -3.94], [0.91, 0.91], [0.91, 0.91],
                                [-9.23, -9.2], [-0.91, -0.91], [0.31, 0.31], [-1.53, -1.53], [0.62, 0.62], [0.62, 0.62]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1511\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_15_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 4.9], [0.0, 0.0], [0.0, 0.0], [2.22, -2.64, 0.0], [2.68, 0], [0, 0], [0, 0.0],
                                [0.0, 4.28], [0, 11.25], [11.25, 0.51], [2.17, 0.54, 0.0], [2.63, -3.91], [-3.91, 0]]
        expected_q_ok_output = [[-1.23, -1.23], [0.0, 0.0], [0.0, 0.0], [3.44, -2.56], [0.71, 0.71], [0, 0], [0, 0],
                                [-0.75, -0.75], [-5.63, -5.63], [5.37, 5.37], [2.28, 0], [3.44, 3.44], [-2.06, -2.06]]
        expected_n_ok_output = [[-3.44, -3.44], [-0.0, -0.0], [0, 0], [-1.93, -1.93], [0, 0], [0.71, 0.71], [-1.8, -1.8],
                                [-1.93, -1.93], [-3.03, -3.03], [-3.03, -3.03], [0, 0], [0, 0], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1512\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_15_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 11.9], [-22.0, -22.0], [0, -22], [-9.15, 0.0], [-0.95, -2.87, 0], [0, 0], [0, 0.0],
                                [0.0, -1.22], [0, -2.09], [-2.09, 6.83], [0.0, 0.0], [5.61, 0]]
        expected_q_ok_output = [[-2.98, -2.98], [0, 0], [11, 11], [-1.83, -1.83], [2.1, -2.64], [0, 0], [0, 0],
                                [0.21, 0.21], [1.04, 1.04], [-4.46, -4.46], [0.0, 0.0], [1.4, 1.4]]
        expected_n_ok_output = [[1.83, 1.83], [11, 11], [0, 0], [5.86, 5.86], [0, 0], [-2.64, -2.64], [-2.04, -2.04],
                                [5.86, 5.86], [0.21, 0.21], [0.21, 0.21], [0, 0], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1611\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_16_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[-4.9, 9.85], [9.85, -10.08, 0.0], [-0.49, 0.0], [0, 0.51], [1, -4], [-4, 0.0], [0, 0],
                                [0, 0], [0, 0], [0, 0], [0, -4], [-4, 1], [0, -0.51], [0.49, 0], [0.0, -10.08, 9.85],
                                [4.9, -9.85]]
        expected_q_ok_output = [[-2.5, -2.5], [6.86, -4.93], [-0.13, -0.13], [-0.13, -0.13], [6.67, 6.67], [-5.33, -5.33],
                                [0, 0], [0, 0], [0, 0], [0, 0], [5.33, 5.33], [-6.67, -6.67], [0.13, 0.13], [0.13, 0.13],
                                [4.93, -6.86], [2.5, 2.5]]
        expected_n_ok_output = [[-7.46, -7.46], [-3.85, -1.61], [-4.54, -4.54], [-11.21, -11.21], [0, 0], [0, 0],
                                [-5.33, -5.33], [-2.63, -2.63], [-2.63, -2.63], [-5.33, -5.33], [0, 0], [0, 0],
                                [-11.21, -11.21], [-4.54, -4.54], [-1.61, -3.85], [-7.46, -7.46]]


        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1612\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_16_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[12.34, -7.1], [-7.1, 2.02], [2.02, 0.0], [4.01, 4.41, 0.0], [0, 5.59], [1.57, 0.79],
                                [0.79, 0.0], [0, 0.0], [0, 0], [0, 0], [0, -0.0], [0.0, 0.79], [0.79, 1.57], [0, -5.59],
                                [-4.01, -4.41, -0.0], [0.0, 2.02], [-12.34, 7.1], [7.1, -2.02]]
        expected_q_ok_output = [[9.72, 9.72], [-2.28, -2.28], [0.2, 0.2], [-1.4, 3.4], [-1.4, -1.4], [1.05, 1.05],
                                [1.05, 1.05], [0, 0], [0, 0], [0, 0], [0, 0], [-1.05, -1.05], [-1.05, -1.05], [1.4, 1.4],
                                [1.4, -3.4], [-0.2, -0.2], [-9.72, -9.72], [2.28, 2.28]]
        expected_n_ok_output = [[-0.66, -0.66], [-0.66, -0.66], [-2.37, -2.37], [0.66, 0.66], [-0.39, -0.39], [0, 0],
                                [0, 0], [1.05, 1.05], [1.12, 1.12], [1.12, 1.12], [1.05, 1.05], [0, 0], [0, 0],
                                [-0.39, -0.39], [0.66, 0.66], [-2.37, -2.37], [-0.66, -0.66], [-0.66, -0.66]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n3716\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_17_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -2.33, -1.96], [-1.96, 1.11, 6.88], [5.27, -6.88], [0.0, -9.26], [-9.26, 7.47],
                                [-24.76, 0.0], [2.2, 2.2], [2.2, 2.2], [0, 0], [0, 0], [0.0, -24.76], [-0.0, 9.26],
                                [9.26, -7.47], [-5.27, 6.88], [6.88, 1.11, -1.96], [-1.96, -2.33, 0]]
        expected_q_ok_output = [[2.45, -1.15], [-1.15, -4.75], [2.53, 2.53], [4.63, 4.63], [-8.37, -8.37], [-8.25, -8.25],
                                [0.0, 0.0], [-0.0, -0.0], [0, 0], [0, 0], [8.25, 8.25], [-4.63, -4.63], [8.37, 8.37],
                                [-2.53, -2.53], [4.75, 1.15], [1.15, -2.45]]
        expected_n_ok_output = [[0, 0], [0, 0], [-4.75, -4.75], [-4.75, -4.75], [-4.75, -4.75], [4.63, 4.63], [-10.9, -10.9],
                                [-10.9, -10.9], [2.53, 2.53], [2.53, 2.53], [4.63, 4.63], [-4.75, -4.75], [-4.75, -4.75],
                                [-4.75, -4.75], [0, 0], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n3717\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_17_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -19.16], [-19.16, 0.67], [2.94, -2.62, -0.67], [0.0, 1.41], [19.84, 0.0],
                                [-1.53, -1.53], [-1.53, -1.53], [0, 0], [0, 0], [0.0, 19.84], [-0.0, -1.41],
                                [-2.94, 2.62, 0.67], [0.67, -19.16], [-19.16, 0]]
        expected_q_ok_output = [[6.39, 6.39], [-6.61, -6.61], [3.72, -2.28], [-0.35, -0.35], [6.61, 6.61], [0.0, 0.0],
                                [-0.0, -0.0], [0, 0], [0, 0], [-6.61, -6.61], [0.35, 0.35], [-3.72, 2.28], [6.61, 6.61],
                                [-6.39, -6.39]]
        expected_n_ok_output = [[0, 0], [0, 0], [-6.61, -6.61], [-6.61, -6.61], [-0.35, -0.35], [-4.07, -4.07],
                                [-4.07, -4.07], [-2.28, -2.28], [-2.28, -2.28], [-0.35, -0.35], [-6.61, -6.61],
                                [-6.61, -6.61], [0, 0], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1811\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_18_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[15.94, -6.03], [-6.03, -0.0], [0.0, -3.56, 7.58], [3.88, -7.58], [36.07, 3.88],
                                [0, 29.4], [-6.67, 37.44], [37.44, -6.67], [0, 0], [0, 0], [29.4, 0], [-36.07, -3.88],
                                [-3.88, 7.58], [7.58, -3.56, 0.0], [6.03, 0.0], [-15.94, 6.03]]
        expected_q_ok_output = [[10.99, 10.99], [-3.01, -3.01], [2.74, -4.64], [3.01, 3.01], [16.1, 16.1], [-14, -14],
                                [-17.65, -17.65], [17.65, 17.65], [0, 0], [0, 0], [14, 14], [-16.1, -16.1],
                                [-3.01, -3.01], [4.64, -2.74], [3.01, 3.01], [-10.99, -10.99]]
        expected_n_ok_output = [[-4.75, -4.75], [-4.75, -4.75], [-4.92, -0.91], [-3.65, -3.65], [-3.65, -3.65], [0, 0],
                                [-16.1, -16.1], [-16.1, -16.1], [13.08, 13.08], [13.08, 13.08], [0, 0], [-3.65, -3.65],
                                [-3.65, -3.65], [-0.91, -4.92], [-4.75, -4.75], [-4.75, -4.75]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n1812\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_18_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[-17.24, -14.73, -11.02], [-11.02, -6.11, 0], [0.0, -11.65], [-17.51, 11.65],
                                [-2.51, -17.51], [0.0, 0.0], [2.51, -11.24], [-11.24, 2.51], [0, 0], [0, 0], [0.0, 0.0],
                                [2.51, 17.51], [17.51, -11.65], [-11.65, 0.0], [11.02, 6.11, 0.0], [17.24, 14.73, 11.02]]
        expected_q_ok_output = [[-1.91, -4.31], [-4.31, -6.71], [1.45, 1.45], [-7.29, -7.29], [7.5, 7.5], [-0.0, -0.0],
                                [5.5, 5.5], [-5.5, -5.5], [0, 0], [0, 0], [0.0, 0.0], [-7.5, -7.5], [7.29, 7.29],
                                [-1.45, -1.45], [4.31, 6.71], [1.91, 4.31]]
        expected_n_ok_output = [[-5.5, -5.5], [-5.5, -5.5], [-8.55, -8.55], [5.5, 5.5], [5.5, 5.5], [0, 0],
                                [-7.5, -7.5], [-7.5, -7.5], [14.79, 14.79], [14.79, 14.79], [0, 0], [5.5, 5.5],
                                [5.5, 5.5], [-8.55, -8.55], [-5.55, -5.5], [-5.5, -5.5]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n5938\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_19_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -10.66], [-10.66, -10.33, 0.0], [0.0, -14.86], [-14.86, 19.02], [5.7, 0], [0, -5.97],
                                [7.37, 7.37], [0, 0], [0, 0], [7.37, 7.37], [-5.7, 0], [0, 5.97], [19.02, -14.86],
                                [-14.86, 0.0], [10.66, 10.33, -0.0], [-10.66, 0]]
        expected_q_ok_output = [[4.57, 4.57], [1.87, -6.13], [4.57, 4.57], [-10.43, -10.43], [1.1, 1.1], [1.19, 1.19],
                                [0.0, 0.0], [0, 0], [0, 0], [-0.0, -0.0], [-1.1, -1.1], [-1.19, -1.19], [10.43, 10.43],
                                [-4.57, -4.57], [-1.87, 6.13], [-4.57, -4.57]]
        expected_n_ok_output = [[1.87, 1.87], [-4.57, -4.57], [-6.13, -6.13], [-6.13, -6.13], [0, 0], [-10.42, -10.42],
                                [-6.04, -6.04], [1.1, 1.1], [1.1, 1.1], [-6.04, -6.04], [0, 0], [-10.42, -10.42],
                                [-6.13, -6.13], [-6.13, -6.13], [-4.56, -4.56], [1.87, 1.87]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n5939\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_19_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -5.08], [-5.08, -21.3], [-21.3, 0.0], [0.0, -1.43, 1.36], [1.36, 8.38, 19.63],
                                [1.82, 0], [0, -2.02], [15.78, -10.46], [0, 0], [0, 0], [-10.46, 15.78], [-1.82, 0],
                                [0, 2.02], [19.63, 8.38, 1.36], [1.36, -1.43, 0.0], [5.08, 21.3], [21.3, 0], [-5.08, 0]]
        expected_q_ok_output = [[2.18, 2.18], [6.49, 6.49], [-8.52, -8.52], [2.18, -3.02], [-3.02, -8.22], [0.34, 0.34],
                                [0.4, 0.4], [7.5, 7.5], [0, 0], [0, 0], [-7.5, -7.5], [-0.34, -0.34], [-0.4, -0.4],
                                [8.22, 3.02], [3.02, -2.18], [-6.49, -6.49], [8.52, 8.52], [-2.18, -2.18]]
        expected_n_ok_output = [[6.48, 6.48], [-2.17, -2.17], [-2.17, -2.17], [-8.52, -8.52], [-8.52, -8.52], [0, 0],
                                [-15.72, -15.72], [-8.45, -8.45], [0.34, 0.34], [0.34, 0.34], [-8.45, -8.45], [0, 0],
                                [-15.72, -15.72], [-8.52, -8.52], [-8.52, -8.52], [-2.17, -2.17], [-2.17, -2.17],
                                [6.48, 6.48]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2011\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_20_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -10.93], [-10.93, -10.93], [-10.93, 6.07], [4.93, 0.0], [14.36, 0.0], [-7.03, 14.36],
                                [1.14, 6.15], [6.15, -0.65, -2.86], [-2.86, -0.65, 6.15], [0, 0], [0, 0], [-1.14, -6.15],
                                [0.0, 4.93], [-14.36, 0], [7.03, -14.36], [10.93, -6.07], [10.93, 10.93], [-10.93, 0]]
        expected_q_ok_output = [[6.62, 6.62], [0, 0], [-8.5, -8.5], [1.97, 1.97], [7.18, 7.18], [-10.7, -10.7],
                                [-1.32, -1.32], [4.65, 0], [0, -4.65], [0, 0], [0, 0], [1.32, 1.32], [-1.97, -1.97],
                                [-7.18, -7.18], [10.7, 10.7], [8.5, 8.5], [0, 0], [-6.62, -6.62]]
        expected_n_ok_output = [[0, 0], [-6.62, -6.62], [-6.62, -6.62], [-7.18, -7.18], [1.97, 1.97], [1.97, 1.97],
                                [-4.65, -4.65], [-1.32, -1.32], [-1.32, -1.32], [-17.88, -17.88], [-17.88, -17.88],
                                [-4.65, -4.65], [-7.18, -7.18], [1.97, 1.97], [1.97, 1.97], [-6.62, -6.62],
                                [-6.62, -6.62], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2012\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_20_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -7.1], [-7.1, -7.1], [-7.1, -7.1], [-10.49, 0.0], [1.42, 0.0], [-0.7, 1.42],
                                [3.39, 4.37, 10.14], [10.14, -11.11], [-11.11, -11.11], [-11.11, -11.11], [-11.11, 10.14],
                                [0, 0], [0, 0], [-3.39, -4.37, -10.14], [0.0, -10.49], [-1.42, -0.0], [0.7, -1.42],
                                [7.1, 7.1], [7.1, 7.1], [-7.1, 0]]
        expected_q_ok_output = [[4.3, 4.3], [0, 0], [0.0, 0.0], [-4.2, -4.2], [0.71, 0.71], [-1.06, -1.06], [0.71, -4.09],
                                [8.5, 8.5], [0.0, 0.0], [-0.0, -0.0], [-8.5, -8.5], [0, 0], [0, 0], [-0.71, 4.09],
                                [4.2, 4.2], [-0.71, -0.71], [1.06, 1.06], [-0.0, -0.0], [0, 0], [-4.3, -4.3]]
        expected_n_ok_output = [[0, 0], [-4.3, -4.3], [-4.3, -4.3], [-0.71, -0.71], [-4.2, -4.2], [-4.2, -4.2],
                                [-8.5, -8.5], [-4.09, -4.09], [-4.09, -4.09], [-4.09, -4.09], [-4.09, -4.09],
                                [-1.77, -1.77], [-1.77, -1.77], [-8.5, -8.5], [-0.71, -0.71], [-4.2, -4.2], [-4.2, -4.2],
                                [-4.3, -4.3], [-4.3, -4.3], [0, 0]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    # @patch('sys.stdin', StringIO('2\n4113\n'))
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_brgtu_force_method_schema_21_1(self, mock_stdout):
    #     from main import main
    #     m_ok_output, q_ok_output, n_ok_output = main()
    #
    #     # Ожидаемые значения эпюр моментов для каждого стержня
    #     expected_m_ok_output = [[0, 1.78], [1.78, 3.55], [3.55, -4.33, 4.67], [0, 0.0], [0.0, -1.88], [2.79, 4.02],
    #                             [4.02, -7.36], [0, 0], [0, 0], [-7.36, 4.02], [-2.79, -4.02], [-0.0, 1.88], [0, -0.0],
    #                             [4.67, -4.33, 3.55], [0, -1.78], [-1.78, -3.55]]
    #     expected_q_ok_output = [[-0.89, -0.89], [-0.89, -0.89], [3.8, -4.06], [0, 0], [0.3, 0.3], [-0.58, -0.58],
    #                             [3.5, 3.5], [0, 0], [0, 0], [-3.5, -3.5], [0.58, 0.58], [-0.3, -0.3], [0, 0], [4.06, -3.8],
    #                             [0.89, 0.89], [0.89, 0.89]]
    #     expected_n_ok_output = [[-4.85, -4.85], [-4.85, -4.85], [-3.14, 1.25], [-7.65, -7.65], [-7.65, -7.65], [-3.5, -3.5],
    #                             [-0.58, -0.58], [-0.3, -0.3], [-0.3, -0.3], [-0.58, -0.58], [-3.5, -3.5], [-7.65, -7.65],
    #                             [-7.65, -7.65], [1.25, -3.14], [-4.85, -4.85], [-4.85, -4.85]]
    #
    #     errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
    #     errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
    #     errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)
    #
    #     # Собираем все ошибки вместе
    #     all_errors = []
    #     if errors_m:
    #         all_errors.extend(errors_m)
    #     if errors_q:
    #         all_errors.extend(errors_q)
    #     if errors_n:
    #         all_errors.extend(errors_n)
    #
    #     # Если есть ошибки, выводим их
    #     if all_errors:
    #         error_message = "\n".join(all_errors)
    #         self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n4114\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_21_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -5.85], [-5.85, 2.3], [2.3, -2.12], [0, 0.0], [0.0, -1.36], [-3.48, 4.61],
                                [4.61, -0.14, -1.73], [0, 0], [0, 0], [-1.73, -0.14, 4.61], [3.48, -4.61], [-0.0, 1.36],
                                [0, -0.0], [-2.12, 2.3], [0, 5.85], [5.85, -2.3]]
        expected_q_ok_output = [[2.93, 2.93], [-4.07, -4.07], [0.51, 0.51], [0, 0], [0.22, 0.22], [-3.85, -3.85], [3.9, 0],
                                [0, 0], [0, 0], [0, -3.9], [3.85, 3.85], [-0.22, -0.22], [0, 0], [-0.51, -0.51],
                                [-2.93, -2.93], [4.07, 4.07]]
        expected_n_ok_output = [[-2.87, -2.87], [-2.87, -2.87], [-4.95, -4.95], [-1.03, -1.03], [-1.03, -1.03],
                                [-3.9, -3.9], [-3.85, -3.85], [-0.22, -0.22], [-0.22, -0.22], [-3.85, -3.85], [-3.9, -3.9],
                                [-1.03, -1.03], [-1.03, -1.03], [-4.96, -4.96], [-2.87, -2.87], [-2.87, -2.87]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n6279\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_22_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[-14.72, 12.64], [16.67, -11.26], [-11.26, -21.63], [-21.63, 0.0], [-4.03, 0], [0, 3.07],
                                [-0.71, 0.0], [10.91, 2.73, 0.0], [0, 12.19, 7.14]]
        expected_q_ok_output = [[-4.89, -4.89], [2.11, 2.11], [2.59, 2.59], [-5.41, -5.41], [-0.38, -0.38], [-0.38, -0.38],
                                [-0.09, -0.09], [6.93, 0], [-7.43, 4.89]]
        expected_n_ok_output = [[-2.21, -2.21], [-1.51, -1.51], [0.09, 0.09], [0.09, 0.09], [-4.97, -4.97], [-4.97, -4.97],
                                [-5.41, -5.41], [0, 0], [-12.72, -12.72]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n6278\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_22_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[26.08, -13.67], [35.24, -15.57], [-15.57, -35.18], [-35.18, -39.59, -35.19],
                                [-35.19, -22, 0.0], [-48.9, 0], [0, 37.26], [7.01, 0.0], [25.2, 0], [0, -5.05]]
        expected_q_ok_output = [[7.1, 7.1], [7.77, 7.77], [3, 3], [4.4, -4.4], [-4.4, -13.2], [-4.66, -4.66],
                                [-4.66, -4.66], [0.9, 0.9], [8, 8], [0.9, 0.9]]
        expected_n_ok_output = [[0.25, 0.25], [3.08, 3.08], [-3.35, -3.35], [-0.9, -0.9], [-0.9, -0.9], [0, 0], [0, 0],
                                [-13.2, -13.2], [0, 0], [-25.85, -25.85]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2311\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_23_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -7.73], [-7.73, 2.53], [2.53, 0.0], [0.0, -2.53], [1.88, -2.06], [-4.59, 3.29],
                                [3.29, -0.43, 0.96], [0.96, -0.43, 3.29], [4.59, -3.29], [-1.88, 2.06], [-2.53, 0.0],
                                [0.0, 2.53], [7.73, -2.53], [0, 7.73]]
        expected_q_ok_output = [[3.87, 3.87], [-5.13, -5.13], [0.6, 0.6], [0.6, 0.6], [0.98, 0.98], [-4.15, -4.15],
                                [2.76, -1.74], [1.74, -2.76], [4.15, 4.15], [-0.98, -0.98], [-0.6, -0.6], [-0.6, -0.6],
                                [5.13, 5.13], [-3.87, -3.87]]
        expected_n_ok_output = [[-0.6, -0.6], [-0.6, -0.6], [-5.13, -5.13], [-5.13, -5.13], [-4.35, -4.35], [-4.95, -4.95],
                                [-5.84, -3.77], [-3.77, -5.84], [-4.95, -4.95], [-4.35, -4.35], [-5.13, -5.13],
                                [-5.13, -5.13], [-0.6, -0.6], [-0.6, -0.6]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2312\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_23_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -1.29, -1.39], [-1.39, -0.28, 2.02], [2.02, 0.0], [0.0, -2.02], [-1.42, 0.52],
                                [-1.5, 5.28], [5.28, -6.5], [-6.5, 5.28], [1.5, -5.28], [1.42, -0.52], [-2.02, 0.0],
                                [0.0, 2.02], [1.3, 0.28, -2.02], [0, 1.29, 1.39]]
        expected_q_ok_output = [[1.89, -0.51], [-0.51, -2.91], [0.48, 0.48], [0.48, 0.48], [-0.49, -0.49], [-3.39, -3.39],
                                [2.57, 2.57], [-2.57, -2.57], [3.39, 3.39], [0.49, 0.49], [-0.48, -0.48], [-0.48, -0.48],
                                [0.51, 2.91], [-1.89, 0.51]]
        expected_n_ok_output = [[-0.48, -0.48], [-0.48, -0.48], [-2.91, -2.91], [-2.91, -2.91], [-4.02, -4.02], [-4.5, -4.5],
                                [-5.01, -5.01], [-5.01, -5.01], [-4.5, -4.5], [-4.02, -4.02], [-2.91, -2.91], [-2.91, -2.91],
                                [-0.48, -0.48], [-0.48, -0.48]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n0483\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_24_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -9.1], [-9.1, 5.79], [5.79, 0.0], [0.0, -5.79], [0, 1.47], [1.47, -1.81],
                                [-7.6, 12.75], [12.75, -6.24, -12.57], [-12.57, -6.24, 12.75], [7.6, -12.75],
                                [-1.47, 1.81], [0, -1.47], [-5.79, 0.0], [0.0, 5.79], [9.1, -5.79], [0, 9.1], [0, 0],
                                [0, 0]]
        expected_q_ok_output = [[3.79, 3.79], [-6.21, -6.21], [1.29, 1.29], [1.29, 1.29], [-0.61, -0.61], [1.36, 1.36],
                                [-4.84, -4.84], [11.25, 0], [0, -11.25], [4.84, 4.84], [-1.36, -1.36], [0.61, 0.61],
                                [-1.29, -1.29], [-1.29, -1.29], [6.21, 6.21], [-3.79, -3.79], [0, 0], [0, 0]]
        expected_n_ok_output = [[-1.29, -1.29], [-1.29, -1.29], [-6.21, -6.21], [-6.21, -6.21], [-9.96, -9.96],
                                [-9.96, -9.96], [-11.25, -11.25], [-4.84, -4.84], [-4.84, -4.84], [-11.25, -11.25],
                                [-9.96, -9.96], [-9.96, -9.96], [-6.21, -6.21], [-6.21, -6.21], [-1.29, -1.29],
                                [-1.29, -1.29], [-1.97, -1.97], [-1.97, -1.97]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n0484\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_24_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -4.32, -5.05], [-5.05, -2.17, 4.3], [4.3, 0.0], [0.0, -4.3], [0, 2.34], [2.34, -3.31],
                                [-7.61, 12.38], [12.38, -10.12], [-10.12, -10.12], [-10.12, -10.12], [-10.12, 12.38],
                                [7.61, -12.38], [-2.34, 3.31], [0, -2.34], [-4.3, 0.0], [0.0, 4.3], [5.05, 2.17, -4.3],
                                [0, 4.32, 5.05], [0, 0], [0, 0]]
        expected_q_ok_output = [[5.1, -0.9], [-0.9, -6.9], [0.96, 0.96], [0.96, 0.96], [-0.97, -0.97], [2.35, 2.35],
                                [-4.54, -4.54], [10, 10], [0.0, 0.0], [-0.0, -0.0], [-10, -10], [4.54, 4.54],
                                [-2.35, -2.35], [0.97, 0.97], [-0.96, -0.96], [-0.96, -0.96], [0.9, 6.9], [-5.1, 0.9],
                                [0, 0], [0, 0]]
        expected_n_ok_output = [[-0.96, -0.96], [-0.96, -0.96], [-6.9, -6.9], [-6.9, -6.9], [-9.04, -9.04], [-9.04, -9.04],
                                [-10, -10], [-4.54, -4.54], [-4.54, -4.54], [-4.54, -4.54], [-4.54, -4.54], [-10, -10],
                                [-9.04, -9.04], [-9.04, -9.04], [-6.9, -6.9], [-6.9, -6.9], [-0.96, -0.96], [-0.96, -0.96],
                                [-3.33, -3.33], [-3.33, -3.33]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2511\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_25_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 0.93], [-21.38, 17.03], [17.03, -10.96], [-10.96, 3.19], [22.31, 4.32, -6.9],
                                [-6.9, -10.3, -11.44], [-11.44, -10.3, -6.9], [-6.9, 4.32, 22.31], [3.19, -10.96],
                                [-10.96, 17.03], [21.38, -17.03], [0, -0.93]]
        expected_q_ok_output = [[-0.23, -0.23], [-20.22, -20.22], [5.71, 5.71], [-4.99, -4.99], [9, 3.3], [3.3, 0],
                                [0, -3.3], [-3.3, -9], [4.99, 4.99], [-5.71, -5.71], [20.22, 20.22], [0.23, 0.23]]
        expected_n_ok_output = [[-20, -20], [-11, -11], [-22.29, -22.29], [-19.59, -19.59], [19.98, 19.98], [19.98, 19.98],
                                [19.98, 19.98], [19.98, 19.98], [-19.59, -19.59], [-22.29, -22.29], [-11, -11], [-20, -20]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2512\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_25_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 10.09], [-22.96, 7.6], [7.6, -2.25, 4.41], [33.05, -19.2], [-19.2, -19.2],
                                [-19.2, -19.2], [-19.2, 33.05], [4.41, -2.25, 7.6], [22.96, -7.6], [0, -10.09]]
        expected_q_ok_output = [[-2.52, -2.52], [-15.28, -15.28], [4.76, -3.94], [11, 11], [0, 0], [0, 0], [-11, -11],
                                [3.94, -4.76], [15.28, 15.28], [2.52, 2.52]]
        expected_n_ok_output = [[-20, -20], [-9, -9], [-17.08, -14.76], [12.76, 12.76], [12.76, 12.76], [12.76, 12.76],
                                [12.76, 12.76], [-14.76, -17.08], [-9, -9], [-20, -20]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2611\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_26_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -2], [-7.94, 7.31], [0.0, -7.94], [7.94, 0.0], [5.31, 1.97], [1.97, -1.44, -2.57],
                                [-2.57, -1.44, 1.97], [-5.31, -1.97], [7.94, -7.31], [0, 7.94], [-7.94, 0], [-2, 0]]
        expected_q_ok_output = [[0.2, 0.2], [-8.03, -8.03], [3.97, 3.97], [3.97, 3.97], [1.76, 1.76], [3.3, 0], [0, -3.3],
                                [-1.76, -1.76], [8.03, 8.03], [-3.97, -3.97], [-3.97, -3.97], [-0.2, -0.2]]
        expected_n_ok_output = [[9.93, 9.93], [-4.96, -4.96], [-4.96, -4.96], [-4.96, -4.96], [-3.3, -3.3], [1.76, 1.76],
                                [1.76, 1.76], [-3.3, -3.3], [-4.96, -4.96], [-4.96, -4.96], [-4.96, -4.96], [9.93, 9.93]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2612\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_26_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -9.01, 11.98], [-2.27, -4.55], [0.0, -2.27], [2.27, 0.0], [7.43, 5.25], [5.25, -11.25],
                                [-11.25, 5.25], [-7.43, -5.25], [2.27, 4.55], [0, 2.27], [-2.27, 0], [11.98, -9.01, 0]]
        expected_q_ok_output = [[4.71, -7.06], [1.14, 1.14], [1.14, 1.14], [1.14, 1.14], [1.09, 1.09], [6, 6], [-6, -6],
                                [-1.09, -1.09], [-1.14, -1.14], [-1.14, -1.14], [-1.14, -1.14], [7.06, -4.71]]
        expected_n_ok_output = [[-0.99, 1.36], [-13.19, -13.19], [-13.19, -13.19], [-13.19, -13.19], [-6, -6],
                                [1.09, 1.09], [1.09, 1.09], [-6, -6], [-13.19, -13.19], [-13.19, -13.19], [-13.19, -13.19],
                                [1.36, -0.99]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n0762\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_27_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[-4.54, 10.86], [-27.65, 0.0], [0.0, -33.2], [-33.2, 22.67], [4.98, -22.67], [0, -15.4],
                                [38.51, 0], [0, -17.37, 20.38]]
        expected_q_ok_output = [[-4.28, -4.28], [-6.91, -6.91], [3.69, 3.69], [-9.31, -9.31], [6.91, 6.91], [4.28, 4.28],
                                [8.56, 8.56], [8.56, -12.44]]
        expected_n_ok_output = [[-12.25, -12.25], [-3.69, -3.69], [-6.91, -6.91], [-6.91, -6.91], [-9.31, -9.31],
                                [-21.75, -21.75], [2.64, 2.64], [2.64, 2.64]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n0761\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_27_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[-17.29, 17.92], [-12.28, 0.0], [0.0, -1.1], [-1.1, -1.83], [-0.32, 4.36, 1.83],
                                [0, -7.85], [30.2, 0], [0, -30.2], [-30.2, 7.53]]
        expected_q_ok_output = [[-9.78, -9.78], [-3.23, -3.23], [0.12, 0.12], [0.12, 0.12], [-4.37, 3.23], [2.18, 2.18],
                                [6.71, 6.71], [6.71, 6.71], [-6.29, -6.29]]
        expected_n_ok_output = [[-6.83, -6.83], [-0.12, -0.12], [-3.23, -3.23], [-3.23, -3.23], [0.12, 0.12],
                                [-6.17, -6.17], [-6.55, -6.55], [-6.55, -6.55], [-6.55, -6.55]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2811\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_28_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 3], [3, 6.01], [6.01, -5.16, -1.63], [-7.59, 3.58], [0, -7.59], [1.96, 15.41],
                                [15.41, -6.74], [-6.74, 0], [0, -6.74], [-6.74, 15.41], [-1.96, -15.41], [7.59, -3.58],
                                [0, 7.59], [-1.63, -5.16, 6.01], [-3, -6.01], [0, -3], [0, 0], [0, 0]]
        expected_q_ok_output = [[-1.5, -1.5], [-1.5, -1.5], [5.29, -3.11], [-5.58, -5.58], [3.8, 3.8], [-7.09, -7.09],
                                [9.75, 9.75], [-2.97, -2.97], [2.97, 2.97], [-9.75, -9.75], [7.09, 7.09], [5.58, 5.58],
                                [-3.8, -3.8], [3.11, -5.29], [1.5, 1.5], [1.5, 1.5], [0, 0], [0, 0]]
        expected_n_ok_output = [[-5.29, -5.29], [-5.29, -5.29], [-1.5, -1.5], [-17.11, -17.11], [-17.11, -17.11],
                                [-14, -14], [-12.29, -12.29], [-6.44, -6.44], [-6.44, -6.44], [-12.29, -12.29], [-14, -14],
                                [-17.11, -17.11], [-17.11, -17.11], [-1.5, -1.5], [-5.29, -5.29], [-5.29, -5.29],
                                [9.38, 9.38], [9.38, 9.38]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2812\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_28_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -11.75], [-11.75, 4.5], [4.5, -1.16], [3.71, -4.57], [0, 3.71], [-5.73, 2.24],
                                [2.24, -1.43, 0], [0, -1.43, 2.24], [5.73, -2.24], [-3.71, 4.57], [0, -3.71], [-1.16, 4.5],
                                [11.75, -4.5], [0, 11.75], [0, 0], [0, 0]]
        expected_q_ok_output = [[5.88, 5.88], [-8.12, -8.12], [0.81, 0.81], [4.14, 4.14], [-1.85, -1.85], [-3.98, -3.98],
                                [2.72, -1.74], [1.74, -2.71], [3.98, 3.98], [-4.14, -4.14], [1.85, 1.85], [-0.81, -0.81],
                                [8.12, 8.12], [-5.88, -5.88], [0, 0], [0, 0]]
        expected_n_ok_output = [[-0.81, -0.81], [-0.81, -0.81], [-8.12, -8.12], [-4.14, -4.14], [-4.14, -4.14],
                                [-4.95, -4.95], [-5.75, -3.59], [-3.59, -5.75], [-4.95, -4.95], [-4.14, -4.14],
                                [-4.14, -4.14], [-8.12, -8.12], [-0.81, -0.81], [-0.81, -0.81], [-5.99, -5.99],
                                [-5.99, -5.99]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2935\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_29_1(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, 5.27], [5.27, -14.43], [-14.43, 0.0], [0.0, 12.37], [0.25, -1.71], [0, 0.25],
                                [10.66, 0.05, -3.03], [-3.03, 0.05, 10.66], [0, -0.25], [-0.25, 1.71], [12.37, 0.0],
                                [0.0, -14.43], [-14.43, 5.27], [0, -5.27], [0, 0], [0, 0]]
        expected_q_ok_output = [[-1.14, -1.14], [8.66, 8.66], [-6.34, -6.34], [-6.34, -6.34], [0.43, 0.43], [-0.1, -0.1],
                                [5.77, -0.36], [0.36, -5.77], [0.1, 0.1], [-0.43, -0.43], [6.34, 6.34], [6.34, 6.34],
                                [-8.66, -8.66], [1.14, 1.14], [0, 0], [0, 0]]
        expected_n_ok_output = [[-8.66, -8.66], [-1.14, -1.14], [-1.14, -1.14], [-1.14, -1.14], [-13.38, -13.38],
                                [-13.38, -13.38], [-4.1, -0.63], [-0.63, -4.1], [-13.38, -13.38], [-13.38, -13.38],
                                [-1.14, -1.14], [-1.14, -1.14], [-1.14, -1.14], [-8.66, -8.66], [-0.53, -0.53],
                                [-0.53, -0.53]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")


    @patch('sys.stdin', StringIO('2\n2936\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_schema_29_2(self, mock_stdout):
        from main import main
        m_ok_output, q_ok_output, n_ok_output = main()

        # Ожидаемые значения эпюр моментов для каждого стержня
        expected_m_ok_output = [[0, -3.06, 3.1], [3.1, 1.55], [1.55, 0.0], [0.0, -1.33], [-5.36, 11.56], [0, -5.36],
                                [10.24, -12.75], [-12.75, -2.74], [-2.74, -12.75], [-12.75, 10.24], [0, 5.36],
                                [5.36, -11.56], [-1.33, 0.0], [0.0, 1.55], [1.55, 3.1], [0, 3.06, -3.1], [0, 0], [0, 0]]
        expected_q_ok_output = [[3.19, -4.49], [0.68, 0.68], [0.68, 0.68], [0.68, 0.68], [-3.53, -3.53], [2.14, 2.14],
                                [9.08, 9.08], [-3.96, -3.96], [3.96, 3.96], [-9.08, -9.08], [-2.14, -2.14], [3.53, 3.53],
                                [-0.68, -0.68], [-0.68, -0.68], [-0.68, -0.68], [-3.19, 4.49], [0, 0], [0, 0]]
        expected_n_ok_output = [[-0.68, -0.68], [-4.49, -4.49], [-4.49, -4.49], [-4.49, -4.49], [-14.32, -14.32],
                                [-14.32, -14.32], [-14.37, -14.37], [-6.96, -6.96], [-6.96, -6.96], [-14.37, -14.37],
                                [-14.32, -14.32], [-14.32, -14.32], [-4.49, -4.49], [-4.49, -4.49], [-4.49, -4.49],
                                [-0.68, -0.68], [5.67, 5.67], [5.67, 5.67]]

        errors_m = compare_moment_lists(m_ok_output, expected_m_ok_output, self.tolerance)
        errors_q = compare_moment_lists(q_ok_output, expected_q_ok_output, self.tolerance)
        errors_n = compare_moment_lists(n_ok_output, expected_n_ok_output, self.tolerance)

        # Собираем все ошибки вместе
        all_errors = []
        if errors_m:
            all_errors.extend(errors_m)
        if errors_q:
            all_errors.extend(errors_q)
        if errors_n:
            all_errors.extend(errors_n)

        # Если есть ошибки, выводим их
        if all_errors:
            error_message = "\n".join(all_errors)
            self.fail(f"Найдены расхождения:\n{error_message}")

if __name__ == '__main__':
    unittest.main()
