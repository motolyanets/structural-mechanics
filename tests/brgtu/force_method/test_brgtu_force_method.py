import unittest
import warnings
from unittest.mock import patch
from io import StringIO
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.abspath('../../..'))
t = 0.5

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

    @patch('sys.stdin', StringIO('2\n1111\n'))
    @patch('sys.stdout', new_callable=StringIO)
    def test_brgtu_force_method_1111(self, mock_stdout):
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
    def test_brgtu_force_method_1112(self, mock_stdout):
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
    def test_brgtu_force_method_1211(self, mock_stdout):
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
    def test_brgtu_force_method_1212(self, mock_stdout):
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
    def test_brgtu_force_method_1311(self, mock_stdout):
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
    def test_brgtu_force_method_1312(self, mock_stdout):
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
    def test_brgtu_force_method_7495(self, mock_stdout):
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
    def test_brgtu_force_method_7496(self, mock_stdout):
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
    def test_brgtu_force_method_1511(self, mock_stdout):
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
    def test_brgtu_force_method_1512(self, mock_stdout):
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
    def test_brgtu_force_method_1611(self, mock_stdout):
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
    def test_brgtu_force_method_1612(self, mock_stdout):
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
    def test_brgtu_force_method_3716(self, mock_stdout):
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
    def test_brgtu_force_method_3717(self, mock_stdout):
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
    def test_brgtu_force_method_1811(self, mock_stdout):
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
    def test_brgtu_force_method_1812(self, mock_stdout):
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
    def test_brgtu_force_method_5938(self, mock_stdout):
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
    def test_brgtu_force_method_5939(self, mock_stdout):
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


    # @patch('sys.stdin', StringIO('2\n2011\n'))
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_brgtu_force_method_2011(self, mock_stdout):
    #     from main import main
    #     m_ok_output, q_ok_output, n_ok_output = main()
    #
    #     # Ожидаемые значения эпюр моментов для каждого стержня
    #     expected_m_ok_output = [[-0.0006614811951609679, -10.91377823896081], [-10.91443972015597, -10.914439720155968], [-10.913589720155967, 6.084710279844028], [4.896833997829038, 0.0], [14.405266664094487, 0.0], [-7.202993427696171, 14.404906460397953], [1.1896601014716568, 6.1180254696269465], [6.117689570278774, -0.6475948297212271, -2.902844829721227], [-2.902844829721227, -0.6475948297212271, 6.117689570278774], [0, 0], [0, 0], [-1.1896601014716568, -6.1180254696269465], [0.0, 4.896833997829038], [-14.405266664094487, -0.0], [7.202993427696171, -14.404906460397953], [10.913589720155967, -6.084710279844028], [10.91443972015597, 10.914439720155968], [-10.91377823896081, -0.0006614811951609679]]
    #     expected_q_ok_output = [[6.614010156221605, 6.614010156221605], [-8.881784197001252e-16, -8.881784197001252e-16], [-8.499149999999997, -8.499149999999997], [1.9587335991316153, 1.9587335991316153], [7.2026333320472435, 7.2026333320472435], [-10.803949944047062, -10.803949944047062], [-1.296938254777708, -1.296938254777708], [4.652879845161291, 0.002879845161290806], [-0.002879845161290806, -4.652879845161291], [0, 0], [0, 0], [1.296938254777708, 1.296938254777708], [-1.9587335991316153, -1.9587335991316153], [-7.2026333320472435, -7.2026333320472435], [10.803949944047062, 10.803949944047062], [8.499149999999997, 8.499149999999997], [8.881784197001252e-16, 8.881784197001252e-16], [-6.614010156221605, -6.614010156221605]]
    #     expected_n_ok_output = [[0, 0], [-6.614010156221605, -6.614010156221605], [-6.614010156221605, -6.614010156221605], [-7.2022117452222885, -7.2022117452222885], [1.9587335991316162, 1.9587335991316162], [1.9587335991316162, 1.9587335991316162], [-4.65527655708999, -4.65527655708999], [-1.2969382547777073, -1.2969382547777073], [-1.2969382547777073, -1.2969382547777073], [-18.006583276094304, -18.006583276094304], [-18.006583276094304, -18.006583276094304], [-4.65527655708999, -4.65527655708999], [-7.2022117452222885, -7.2022117452222885], [1.9587335991316162, 1.9587335991316162], [1.9587335991316162, 1.9587335991316162], [-6.614010156221605, -6.614010156221605], [-6.614010156221605, -6.614010156221605], [0, 0]]
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
    #
    #
    # @patch('sys.stdin', StringIO('2\n2012\n'))
    # @patch('sys.stdout', new_callable=StringIO)
    # def test_brgtu_force_method_2012(self, mock_stdout):
    #     from main import main
    #     m_ok_output, q_ok_output, n_ok_output = main()
    #
    #     # Ожидаемые значения эпюр моментов для каждого стержня
    #     expected_m_ok_output = [[-0.0004305743539924031, -7.104046266520658], [-7.104476840874651, -7.104476840874652], [-7.104476840874652, -7.104476840874652], [-10.48522172454392, 0.0], [1.416772614191867, 0.0], [-0.7084217228689091, 1.4167371877922967], [3.381093467142449, 4.364320852950584, 10.147068238758722], [10.146627396585899, -11.101672603414103], [-11.102522603414101, -11.102522603414101], [-11.102522603414101, -11.102522603414101], [-11.101672603414103, 10.146627396585899], [0, 0], [0, 0], [-3.381093467142449, -4.364320852950584, -10.147068238758722], [0.0, -10.48522172454392], [-1.416772614191867, -0.0], [0.7084217228689091, -1.4167371877922967], [7.104476840874652, 7.104476840874652], [7.104476840874651, 7.104476840874652], [-7.104046266520658, -0.0004305743539924031]]
    #     expected_q_ok_output = [[4.305221631616162, 4.305221631616162], [4.440892098500626e-16, 4.440892098500626e-16], [0.0, 0.0], [-4.194088689817567, -4.194088689817567], [0.7083863070959335, 0.7083863070959335], [-1.062579455330603, -1.062579455330603], [0.7085063070959317, -4.091493692904068], [8.49932, 8.49932], [0.0, 0.0], [-0.0, -0.0], [-8.49932, -8.49932], [0, 0], [0, 0], [-0.7085063070959317, 4.091493692904068], [4.194088689817567, 4.194088689817567], [-0.7083863070959335, -0.7083863070959335], [1.062579455330603, 1.062579455330603], [-0.0, -0.0], [-4.440892098500626e-16, -4.440892098500626e-16], [-4.305221631616162, -4.305221631616162]]
    #     expected_n_ok_output = [[0, 0], [-4.305221631616162, -4.305221631616162], [-4.305221631616162, -4.305221631616162], [-0.7085063070959317, -0.7085063070959317], [-4.194088689817567, -4.194088689817567], [-4.194088689817567, -4.194088689817567], [-8.499310321433729, -8.499310321433729], [-4.091493692904067, -4.091493692904067], [-4.091493692904067, -4.091493692904067], [-4.091493692904067, -4.091493692904067], [-4.091493692904067, -4.091493692904067], [-1.770965762426536, -1.770965762426536], [-1.770965762426536, -1.770965762426536], [-8.499310321433729, -8.499310321433729], [-0.7085063070959317, -0.7085063070959317], [-4.194088689817567, -4.194088689817567], [-4.194088689817567, -4.194088689817567], [-4.305221631616162, -4.305221631616162], [-4.305221631616162, -4.305221631616162], [0, 0]]
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

if __name__ == '__main__':
    unittest.main()
