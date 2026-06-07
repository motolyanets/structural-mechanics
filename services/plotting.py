import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, pymupdf, layout as draw_layout
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy
from ezdxf.math import Vec2, Matrix44
import pathlib
from PyPDF2 import PdfMerger


def export_rectangles_to_single_pdf(doc, layout_name, output_pdf="output.pdf"):
    """
    Экспортирует все прямоугольники из layout в один PDF файл.
    Каждый прямоугольник = отдельная страница.
    """
    source_layout = doc.layouts.get(layout_name)

    # 1. Находим все прямоугольники
    rectangles = []
    for entity in source_layout:
        if entity.dxftype() == 'LWPOLYLINE' and entity.dxf.layer == "Листы":
            vertices = list(entity.vertices())
            if len(vertices) == 4:
                verts = []
                for v in vertices:
                    if hasattr(v, 'location'):
                        verts.append(Vec2(v.location.x, v.location.y))
                    elif isinstance(v, (tuple, list)):
                        verts.append(Vec2(v[0], v[1]))
                    else:
                        verts.append(Vec2(v.x, v.y))

                min_pt = Vec2(min(v.x for v in verts), min(v.y for v in verts))
                max_pt = Vec2(max(v.x for v in verts), max(v.y for v in verts))
                rectangles.append({
                    'entity': entity,
                    'min': min_pt,
                    'max': max_pt,
                    'width': max_pt.x - min_pt.x,
                    'height': max_pt.y - min_pt.y
                })

    print(f"Найдено прямоугольников: {len(rectangles)}")

    if not rectangles:
        print("Прямоугольники не найдены!")
        return

    # Сортируем прямоугольники
    rectangles.sort(key=lambda r: (-r['min'].y, r['min'].x))

    temp_pdfs = []

    for idx, rect in enumerate(rectangles):
        print(f"\nОбработка прямоугольника {idx + 1} из {len(rectangles)}")
        print(f"  Размер: {rect['width']:.2f} x {rect['height']:.2f} мм")

        # Создаём временный layout
        temp_name = f"__temp_{idx}"
        if temp_name in doc.layout_names():
            doc.delete_layout(temp_name)
        temp_layout = doc.layouts.new(temp_name)

        # Настраиваем размер листа
        temp_layout.page_setup(
            size=(rect['width'], rect['height']),
            margins=(0, 0, 0, 0),
            units='mm'
        )

        # Собираем все текстовые объекты внутри прямоугольника
        texts_to_copy = []
        viewports_data = []

        for entity in source_layout:
            if entity is rect['entity']:
                continue

            pos = get_entity_center(entity)
            if pos is None:
                continue

            if (rect['min'].x <= pos.x <= rect['max'].x and
                    rect['min'].y <= pos.y <= rect['max'].y):

                if entity.dxftype() == 'VIEWPORT':
                    # Сохраняем данные видового экрана для обработки
                    viewports_data.append(entity)
                else:
                    # Обычные сущности копируем со смещением
                    texts_to_copy.append(entity)

        print(f"  Найдено текстовых объектов: {len(texts_to_copy)}")
        print(f"  Найдено видовых экранов: {len(viewports_data)}")

        # Копируем текстовые объекты со смещением
        for entity in texts_to_copy:
            try:
                new_entity = temp_layout.add_entity(entity.copy())
                offset_entity(new_entity, rect['min'].x, rect['min'].y)
            except Exception as e:
                print(f"    Ошибка копирования {entity.dxftype()}: {e}")

        # Обрабатываем каждый видовой экран
        for vp in viewports_data:
            try:
                render_viewport_to_layout(doc, temp_layout, vp, rect['min'])
            except Exception as e:
                print(f"    Ошибка обработки видового экрана: {e}")

        # Экспортируем в PDF
        temp_pdf = pathlib.Path(f"temp_{idx}.pdf")
        try:
            export_layout_to_pdf(doc, temp_layout, temp_pdf, rect['width'], rect['height'])
            temp_pdfs.append(temp_pdf)
            print(f"  PDF создан")
        except Exception as e:
            print(f"  Ошибка экспорта PDF: {e}")
        finally:
            if temp_name in doc.layout_names():
                doc.delete_layout(temp_name)

    # Объединяем PDF
    if temp_pdfs:
        merge_pdfs(temp_pdfs, output_pdf)
        print(f"\n✅ Готово! Результат: {output_pdf}")
        for temp_pdf in temp_pdfs:
            try:
                if temp_pdf.exists():
                    temp_pdf.unlink()
            except:
                pass
    else:
        print("❌ Не создано ни одного PDF!")


def render_viewport_to_layout(doc, target_layout, viewport, rect_min):
    """
    Рендерит содержимое видового экрана во временный layout.
    """
    msp = doc.modelspace()

    # Получаем параметры видового экрана
    # Центр видового экрана в пространстве листа (в миллиметрах)
    vp_center_x = viewport.dxf.center_x
    vp_center_y = viewport.dxf.center_y

    # Размер видового экрана
    vp_width = viewport.dxf.width
    vp_height = viewport.dxf.height

    # Центр вида в пространстве модели
    view_center_x = viewport.dxf.view_center_x
    view_center_y = viewport.dxf.view_center_y

    # Высота вида в пространстве модели (в единицах модели)
    view_height = viewport.dxf.view_height

    # Коэффициент масштабирования: модель -> лист
    scale = view_height / vp_height

    # Вычисляем границы видового экрана в координатах листа
    vp_min_x = vp_center_x - vp_width / 2
    vp_min_y = vp_center_y - vp_height / 2
    vp_max_x = vp_center_x + vp_width / 2
    vp_max_y = vp_center_y + vp_height / 2

    # Проверяем, что видовой экран попадает в наш прямоугольник
    if not (vp_max_x > rect_min.x and vp_min_x < rect_min.x + 1000):
        return

    # Границы видимой области в пространстве модели
    model_min_x = view_center_x - (vp_width / 2) * scale
    model_min_y = view_center_y - (vp_height / 2) * scale
    model_max_x = view_center_x + (vp_width / 2) * scale
    model_max_y = view_center_y + (vp_height / 2) * scale

    # Собираем все сущности модели в этой области
    entities_to_render = []

    # Используем пространственный поиск (можно доработать)
    for entity in msp:
        try:
            if entity.dxftype() == 'LWPOLYLINE' or entity.dxftype() == 'LINE':
                # Проверяем пересечение с границами
                bbox = entity.bbox()
                if bbox:
                    if (bbox.extmin.x <= model_max_x and bbox.extmax.x >= model_min_x and
                            bbox.extmin.y <= model_max_y and bbox.extmax.y >= model_min_y):
                        entities_to_render.append(entity)
            elif entity.dxftype() in ('TEXT', 'MTEXT'):
                # Для текста проверяем позицию
                x, y = entity.dxf.insert.x, entity.dxf.insert.y
                if model_min_x <= x <= model_max_x and model_min_y <= y <= model_max_y:
                    entities_to_render.append(entity)
            else:
                # Для остальных сущностей используем упрощённую проверку
                try:
                    if hasattr(entity.dxf, 'insert'):
                        x, y = entity.dxf.insert.x, entity.dxf.insert.y
                        if model_min_x <= x <= model_max_x and model_min_y <= y <= model_max_y:
                            entities_to_render.append(entity)
                except:
                    pass
        except:
            pass

    # Теперь нужно добавить эти сущности в target_layout,
    # применив масштабирование и смещение
    for entity in entities_to_render:
        try:
            # Создаём копию сущности
            new_entity = target_layout.add_entity(entity.copy())

            # Применяем трансформацию для каждой вершины/точки
            transform_and_offset_entity(new_entity, model_min_x, model_min_y, scale, vp_min_x, vp_min_y, rect_min)
        except Exception as e:
            pass


def transform_and_offset_entity(entity, model_min_x, model_min_y, scale, vp_min_x, vp_min_y, rect_min):
    """
    Трансформирует сущность из координат модели в координаты листа
    с учётом смещения относительно прямоугольника.
    """
    dx = (vp_min_x - rect_min.x) / scale
    dy = (vp_min_y - rect_min.y) / scale

    try:
        if hasattr(entity.dxf, 'insert'):
            # Для текста и вставок
            x = (entity.dxf.insert.x - model_min_x) / scale + (vp_min_x - rect_min.x)
            y = (entity.dxf.insert.y - model_min_y) / scale + (vp_min_y - rect_min.y)
            entity.dxf.insert = (x, y)
        elif entity.dxftype() == 'LWPOLYLINE':
            # Для полилиний (линии, прямоугольники)
            vertices = list(entity.vertices())
            new_vertices = []
            for v in vertices:
                if hasattr(v, 'location'):
                    x = (v.location.x - model_min_x) / scale + (vp_min_x - rect_min.x)
                    y = (v.location.y - model_min_y) / scale + (vp_min_y - rect_min.y)
                    new_vertices.append((x, y, v.start_width, v.end_width, v.bulge))
                elif isinstance(v, (tuple, list)):
                    x = (v[0] - model_min_x) / scale + (vp_min_x - rect_min.x)
                    y = (v[1] - model_min_y) / scale + (vp_min_y - rect_min.y)
                    new_vertices.append((x, y, *v[2:]))
            entity.set_vertices(new_vertices)
        elif entity.dxftype() == 'LINE':
            # Для линий
            start_x = (entity.dxf.start.x - model_min_x) / scale + (vp_min_x - rect_min.x)
            start_y = (entity.dxf.start.y - model_min_y) / scale + (vp_min_y - rect_min.y)
            end_x = (entity.dxf.end.x - model_min_x) / scale + (vp_min_x - rect_min.x)
            end_y = (entity.dxf.end.y - model_min_y) / scale + (vp_min_y - rect_min.y)
            entity.dxf.start = (start_x, start_y)
            entity.dxf.end = (end_x, end_y)
    except Exception as e:
        pass


def get_entity_center(entity):
    """Возвращает позицию сущности"""
    dxftype = entity.dxftype()

    try:
        if dxftype == 'VIEWPORT':
            return Vec2(entity.dxf.center_x, entity.dxf.center_y)
        elif dxftype in ('TEXT', 'MTEXT'):
            return Vec2(entity.dxf.insert.x, entity.dxf.insert.y)
        elif dxftype == 'INSERT':
            return Vec2(entity.dxf.insert.x, entity.dxf.insert.y)
    except Exception:
        pass

    return None


def offset_entity(entity, dx, dy):
    """Смещает сущность"""
    try:
        if hasattr(entity.dxf, 'insert'):
            entity.dxf.insert.x -= dx
            entity.dxf.insert.y -= dy
    except Exception:
        pass


def export_layout_to_pdf(doc, dxf_layout, output_path, width, height):
    """Экспортирует layout в PDF"""
    backend = pymupdf.PyMuPdfBackend()
    config = Configuration(background_policy=BackgroundPolicy.WHITE)

    page = draw_layout.Page(
        width=width,
        height=height,
        units=draw_layout.Units.mm,
        margins=draw_layout.Margins.all(0)
    )

    Frontend(RenderContext(doc), backend, config=config).draw_layout(dxf_layout)
    pdf_bytes = backend.get_pdf_bytes(page)
    output_path.write_bytes(pdf_bytes)


def merge_pdfs(pdf_files, output_path):
    """Объединяет PDF файлы"""
    merger = PdfMerger()
    for pdf_file in pdf_files:
        merger.append(str(pdf_file))
    merger.write(str(output_path))
    merger.close()