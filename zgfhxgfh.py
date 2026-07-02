import ezdxf

from services.authocad import safe_zoom_for_work


def sample_spline(spline, num_points=100):
    """
    Дискретизирует сплайн (поддерживает и fit_points, и control_points).
    """
    points = []

    if spline.dxftype() != 'SPLINE':
        return points

    # Сначала пробуем получить fit_points (если сплайн создан через них)
    fit_points = []
    if hasattr(spline, 'fit_points'):
        fit_points = list(spline.fit_points)

    if fit_points:
        # Строим кривую через fit_points
        if len(fit_points) == 3:
            # Квадратичная кривая через 3 точки
            p0 = fit_points[0]
            p1 = fit_points[1]
            p2 = fit_points[2]

            (x1, y1), (x2, y2), (x3, y3) = (p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1])

            # 1. Находим коэффициенты a, b, c через определители (правило Крамера)
            # Системы уравнений:
            # a*x1^2 + b*x1 + c = y1
            # a*x2^2 + b*x2 + c = y2
            # a*x3^2 + b*x3 + c = y3

            denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
            if denom == 0:
                raise ValueError("Точки не должны лежать на одной вертикальной линии (X должны отличаться).")

            a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
            b = (x3 ** 2 * (y1 - y2) + x2 ** 2 * (y3 - y1) + x1 ** 2 * (y2 - y3)) / denom
            c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom

            # 2. Генерируем точки с равным шагом по X от x1 до x3
            points = []
            start_x = x1
            end_x = x3

            for i in range(num_points + 1):
                # Равномерный шаг от start_x до end_x
                x = start_x + (end_x - start_x) * (i / num_points)
                # Считаем y по точной формуле параболы
                y = a * x ** 2 + b * x + c
                points.append((round(x, 4), round(y, 4)))

            return points


doc = ezdxf.readfile('Шаблон.dxf')
msp = doc.modelspace()

points1 = [[0, 0], [10, 0]]
points2 = [[0, 0], [5, 2], [10, 8]]

spline = msp.add_spline(points2, dxfattribs={'layer': 'diagram M', 'color': 6, 'linetype': 'CONTINUOUS'})

hatch = msp.add_hatch(color=3, dxfattribs={'layer': 'Штриховка 1'})
hatch.set_pattern_fill("ANSI31", scale=0.05, color=3, angle=45)
#
# # Добавляем весь контур целиком
# hatch.paths.add_polyline_path(points, is_closed=True)

num_points = 100
spline_points = sample_spline(spline, num_points)

path_points = []

# Добавляем точки полилинии (в прямом порядке)
path_points.extend(points1)

# Добавляем точки сплайна (в обратном порядке)
path_points.extend(reversed(spline_points))

# Замыкаем контур (добавляем первую точку в конец)
if path_points:
    path_points.append(path_points[0])

path_polyline = msp.add_lwpolyline(path_points, dxfattribs={'layer': 'diagram M', 'color': 6, 'linetype': 'CONTINUOUS'})
path_polyline.closed = True


hatch.paths.add_polyline_path(path_points, is_closed=True)

safe_zoom_for_work(doc)
doc.saveas(f'fhzfzgnxfgn.dxf')


