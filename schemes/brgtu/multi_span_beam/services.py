import importlib


def get_beam_load_schema(load_number):
    # Импортируем модуль динамически
    module = importlib.import_module(f'schemes.brgtu.multi_span_beam.load_{load_number}')

    try:
        # Получаем функции из модуля
        create_beam_load = getattr(module, f'create_beam_load_{load_number}')

        return create_beam_load

    except (ImportError, AttributeError) as e:
        raise ValueError(f"Схема нагрузок {load_number} не реализована") from e
