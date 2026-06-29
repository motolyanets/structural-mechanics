#!/usr/bin/env python3
from pathlib import Path

from tasks.brgtu.composite_frame.plugin import BRGTUCompositeFrame
from tasks.brgtu.force_method.plugin import BRGTUForceMethod
from tasks.brgtu.movement_method.plugin import BRGTUMovementMethod


# from tasks.brgtu.force_method.plugin import BRGTUForceMethod


def main():
    print("=" * 60)
    print("СТРОИТЕЛЬНАЯ МЕХАНИКА")
    print("=" * 60)

    tasks = {
        "1": {
            "name": "Составная рама",
            "class": BRGTUCompositeFrame,
            "excel_path": Path("data/brgtu/composite_frame.xlsx")
        },
        "2": {
            "name": "Метод сил",
            "class": BRGTUForceMethod,
            "excel_path": Path("data/brgtu/force_method.xlsx")
        },
        "3": {
            "name": "Метод перемещений (Задание 4)",
            "class": BRGTUMovementMethod,
            "excel_path": Path("data/brgtu/movement_method_4.xlsx")
        },
        "4": {
            "name": "Метод перемещений (Задача 8)",
            "class": BRGTUMovementMethod,
            "excel_path": Path("data/brgtu/movement_method_8.xlsx")
        },
    }

    print("\nДоступные задачи:")
    for key, task in tasks.items():
        print(f"  {key}. {task['name']}")

    # choice = input("\nВыберите задачу: ").strip()
    choice = "2"

    if choice not in tasks:
        print("❌ Неверный выбор")
        return

    task_info = tasks[choice]

    if not task_info["excel_path"].exists():
        print(f"❌ Файл не найден: {task_info['excel_path']}")
        return

    # cipher = input("\nВведите 4-значный шифр: ").strip()
    cipher = "3025".strip()

    try:
        plugin = task_info["class"](task_info["excel_path"])
        plugin.loader.print_summary()
        result = plugin.solve(cipher)

        # print("\n" + "=" * 60)
        # print("РЕЗУЛЬТАТ:")
        # print("=" * 60)
        #
        # if "reactions" in result and result["reactions"]:
        #     print("\nНайденные реакции:")
        #     for name, data in result["reactions"].items():
        #         print(f"  {name} = {data['value']} (угол: {data['rotation']}°)")
        #
        # if "message" in result:
        #     print(f"\n{result['message']}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()