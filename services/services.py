import math
import re


def round_up(number: float, decimals: int = 2):
    multiplier = 10 ** decimals
    if number > 0:
        return int(number * multiplier + 0.5) / multiplier
    return int(number * multiplier - 0.5) / multiplier

def normalize_equation(expr: str) -> str:
    # Убираем пробелы в начале и конце
    expr = expr.strip()

    # Убираем ведущий плюс, если есть
    if expr.startswith('+'):
        expr = expr[1:].strip()

    # Разбиваем на члены по пробелам
    terms = expr.split()

    normalized_terms = []

    for term in terms:
        if not term:
            continue

        # Определяем внешний знак члена
        sign = 1
        if term.startswith('-'):
            sign = -1
            term = term[1:]
        elif term.startswith('+'):
            sign = 1
            term = term[1:]

        # Разбиваем на компоненты по '·'
        if '·' in term:
            components = term.split('·')
        else:
            components = [term]

        # Разделяем числа и переменные
        numbers = []
        variables = []
        for comp in components:
            try:
                # Пробуем преобразовать в число
                num = float(comp)
                numbers.append(num)
            except ValueError:
                variables.append(comp)

        # Определяем знак произведения чисел (без учёта внешнего знака)
        product_sign = 1
        for num in numbers:
            if num < 0:
                product_sign *= -1

        # Итоговый знак члена
        final_sign = sign * product_sign

        # Собираем компоненты с положительными числами
        new_components = []
        for comp in components:
            try:
                num = float(comp)
                # Берём модуль числа
                abs_num = abs(num)
                # Убираем .0 у целых чисел
                if abs_num.is_integer():
                    abs_num = int(abs_num)
                new_components.append(str(abs_num))
            except ValueError:
                new_components.append(comp)

        # Собираем член без знака
        term_body = '·'.join(new_components)

        # Если после всех преобразований term_body пуст (не бывает), пропускаем
        if not term_body:
            continue

        # Сохраняем знак и тело
        normalized_terms.append((final_sign, term_body))

    # Формируем итоговую строку
    result_parts = []
    for i, (sign, body) in enumerate(normalized_terms):
        if i == 0:
            # Первый член: если знак минус, ставим '-', иначе ничего
            if sign == -1:
                result_parts.append(f"-{body}")
            else:
                result_parts.append(body)
        else:
            # Последующие члены
            if sign == 1:
                result_parts.append(f"+ {body}")
            else:
                result_parts.append(f"- {body}")

    # Собираем строку
    result = ' '.join(result_parts)

    # Убираем лишние пробелы (двойные)
    result = re.sub(r'\s+', ' ', result)

    # Убираем пробел перед знаком, если он есть (не должно быть, но на всякий случай)
    result = result.replace(' +', '+').replace(' -', '-')
    # Но нам нужны пробелы вокруг знаков, поэтому после замены вернём пробелы
    result = re.sub(r'([+-])', r' \1 ', result)
    result = re.sub(r'\s+', ' ', result).strip()

    # Если начинается с '+ ', убираем
    if result.startswith('+ '):
        result = result[2:]

    return result

def making_report_of_multiply(lst):
    text_1 = ''
    text_2 = ''
    result = 0
    for i in lst:
        if i:
            text_1 += i[0] + ' + '
            text_2 += f'{str(round_up(i[1]))}/EI' + ' + '
            result += i[1]

    text_2 = text_2.replace("+ -", "- ")
    result = round_up(result)
    text = f'{text_1[:-3]} = {text_2[:-3]} = {result}/EI'

    return text, result

def relative_error_percent(number1: float, number2: float, tolerance_percent: float):
    number1 = abs(number1)
    number2 = abs(number2)
    E = round_up((max(number1, number2) - min(number1, number2)) / min(number1, number2) * 100, 4)
    text = f'ε = ({round_up(max(number1, number2), 3)} - {round_up(min(number1, number2), 3)}) / {round_up(min(number1, number2), 3)} · 100% = {E}%'

    if E <= tolerance_percent:
        e_text = f'{text} ≤ {tolerance_percent}'
        print(f'{e_text}')
        print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}\n")
    else:
        e_text = f'{text} > {tolerance_percent}'
        print(f'{e_text}')
        print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}\n")

    return E, e_text

def is_point_on_rod(start_point: tuple[float, float], end_point: tuple[float, float], load_point: tuple[float, float], epsilon=1e-9):
    """
    Проверяет, лежит ли точка на отрезке (а не на всей прямой)
    """
    # Сначала проверяем коллинеарность
    cross_product = ((end_point[0] - start_point[0]) * (load_point[1] - start_point[1]) -
                     (end_point[1] - start_point[1]) * (load_point[0] - start_point[0]))
    if abs(cross_product) > epsilon:
        return False

    # Проверяем, находится ли точка в bounding box отрезка
    min_x = min(start_point[0], end_point[0]) - epsilon
    max_x = max(start_point[0], end_point[0]) + epsilon
    min_y = min(start_point[1], end_point[1]) - epsilon
    max_y = max(start_point[1], end_point[1]) + epsilon

    return min_x <= load_point[0] <= max_x and min_y <= load_point[1] <= max_y

def is_distr_force_on_rod(rod_start: tuple[float, float], rod_end: tuple[float, float], load_start: tuple[float, float],
                          load_end: tuple[float, float], epsilon=1e-9):
    """
    Проверяет, является ли стержень подотрезком распределенной нагрузки. Функция работает только корректно только в том
    случае, если нагрузка распределена по ВСЕЙ длине стержня.

    Returns:
        bool: True если стержень является подотрезком распределенной нагрузки
    """

    # Проверяем, что обе точки второго отрезка лежат на первом
    return (is_point_on_rod(load_start, load_end, rod_start, epsilon) and
            is_point_on_rod(load_start, load_end, rod_end, epsilon))

def distance_between_two_points(point_1: tuple[float, float], point_2: tuple[float, float]) -> float:
    dx = point_2[0] - point_1[0]
    dy = point_2[1] - point_1[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    return distance


def is_subsegment_2d(small_segment, big_segment, tolerance=1e-9):
    """
    Проверяет, является ли отрезок segment1 подотрезком отрезка segment2 в 2D.

    Параметры:
    segment1, segment2 -- кортежи/списки вида ((x1, y1), (x2, y2))
    tolerance -- допустимая погрешность для сравнения чисел с плавающей точкой

    Возвращает:
    True, если segment1 лежит на segment2 и полностью внутри него, иначе False
    """
    p1, p2 = small_segment
    q1, q2 = big_segment

    # Проверяем, что все точки segment1 лежат на прямой segment2
    if not are_collinear(p1, p2, q1, q2, tolerance):
        return False

    # Проверяем, что p1 и p2 находятся между q1 и q2
    if not is_point_between(p1, q1, q2, tolerance):
        return False

    if not is_point_between(p2, q1, q2, tolerance):
        return False

    return True


def are_collinear(p1, p2, q1, q2, tolerance=1e-9):
    """
    Проверяет, лежат ли точки p1 и p2 на одной прямой с отрезком q1-q2.
    """
    # Векторное произведение (q2 - q1) и (p1 - q1) должно быть равно 0
    cross1 = cross_product(subtract(q2, q1), subtract(p1, q1))
    cross2 = cross_product(subtract(q2, q1), subtract(p2, q1))

    return abs(cross1) < tolerance and abs(cross2) < tolerance


def is_point_between(point, a, b, tolerance=1e-9):
    """
    Проверяет, лежит ли точка на отрезке между a и b (включая концы).
    """
    # Проверяем, что точка находится в bounding box
    min_x = min(a[0], b[0]) - tolerance
    max_x = max(a[0], b[0]) + tolerance
    min_y = min(a[1], b[1]) - tolerance
    max_y = max(a[1], b[1]) + tolerance

    if not (min_x <= point[0] <= max_x and min_y <= point[1] <= max_y):
        return False

    # Проверяем, что точка лежит на прямой
    cross = cross_product(subtract(b, a), subtract(point, a))
    if abs(cross) > tolerance:
        return False

    # Проверяем, что точка между a и b (скалярное произведение >= 0)
    dot = dot_product(subtract(point, a), subtract(b, point))
    return dot >= -tolerance  # tolerance для учета погрешности


def cross_product(v1, v2):
    """Векторное произведение для 2D векторов."""
    return v1[0] * v2[1] - v1[1] * v2[0]


def dot_product(v1, v2):
    """Скалярное произведение."""
    return v1[0] * v2[0] + v1[1] * v2[1]


def subtract(v1, v2):
    """Разность векторов."""
    return (v1[0] - v2[0], v1[1] - v2[1])
