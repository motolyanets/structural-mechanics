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
    text = f'ε = ({max(number1, number2)} - {min(number1, number2)}) / {min(number1, number2)} · 100% = {E}%'

    if E <= tolerance_percent:
        e_text = f'{text} ≤ {tolerance_percent}'
        print(f'{e_text}')
        print(f"{"\033[92m"}Проверка выполняется{"\033[0m"}\n")
    else:
        e_text = f'{text} > {tolerance_percent}'
        print(f'{e_text}')
        print(f"{"\033[91m"}Проверка НЕ выполняется{"\033[0m"}\n")

    return E, e_text
