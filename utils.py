"""
Вспомогательные функции ввода-вывода для консольного приложения TaskFlow Team.

Содержит: проверку email, ограничение длины полей, чтение дат и перечислений,
очистку экрана, табличный вывод и подтверждения yes/no.
"""

from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime

# Допустимые значения приоритета (совпадают с CHECK в таблице tasks).
VALID_PRIORITIES = {"low", "medium", "high"}
# Допустимые статусы задачи.
VALID_STATUSES = {"new", "in_progress", "done"}
# Максимальная ширина ячейки при печати таблицы (обрезка длинного текста).
MAX_COLUMN_WIDTH = 36

# --- Ограничения длины текстовых полей (согласованы с интерфейсом, не с SQL) ---
MAX_FULL_NAME = 200
MAX_POSITION = 120
MAX_EMAIL_LEN = 254
MAX_TEAM = 120
MAX_TASK_TITLE = 200
MAX_TASK_DESCRIPTION = 4000

# Шаблон «простого» ASCII-email для локальных корпоративных адресов.
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
)


def is_valid_email(value: str) -> bool:
    """True, если строка непустая, не длиннее лимита и совпадает с _EMAIL_RE."""
    return bool(value) and len(value) <= MAX_EMAIL_LEN and bool(_EMAIL_RE.match(value))


def clear_screen() -> None:
    """
    Очищает консоль: Windows — через cmd /c cls, Unix — команда clear.

    При ошибке запуска внешней команды печатает ANSI-последовательность
    очистки экрана и курсор в начало.
    """
    try:
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "cls"], check=False)
        else:
            subprocess.run(["clear"], check=False)
    except (FileNotFoundError, OSError):
        print("\033[2J\033[H", end="", flush=True)


def wait_for_enter(prompt: str = "\nPress Enter to continue... ") -> None:
    """Ожидает нажатия Enter (пауза после вывода таблицы)."""
    input(prompt)


def read_required(prompt: str) -> str:
    """Запрашивает непустую строку; пустой ввод отвергается и запрос повторяется."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Field cannot be empty.")


def read_required_limited(prompt: str, max_len: int) -> str:
    """Как read_required, но с ограничением длины max_len символов."""
    while True:
        value = read_required(prompt)
        if len(value) > max_len:
            print(f"Too long: maximum {max_len} characters.")
            continue
        return value


def read_optional(prompt: str) -> str:
    """Читает строку с консоли; пустая строка допустима (возврат '')."""
    return input(prompt).strip()


def read_optional_limited(prompt: str, max_len: int) -> str:
    """Необязательное поле: пусто разрешено, иначе длина не больше max_len."""
    while True:
        value = read_optional(prompt)
        if not value:
            return ""
        if len(value) > max_len:
            print(f"Too long: maximum {max_len} characters.")
            continue
        return value


def read_email(prompt: str) -> str:
    """Запрашивает email до тех пор, пока is_valid_email не вернёт True."""
    while True:
        value = read_required(prompt)
        if not is_valid_email(value):
            print("Invalid email format. Use a valid address like name@company.com")
            continue
        return value


def read_int(prompt: str) -> int:
    """Читает целое число; при ошибке парсинга сообщение и повтор."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Enter a valid integer.")


def read_date(prompt: str) -> str:
    """Принимает дату в формате YYYY-MM-DD (строгая проверка через datetime)."""
    while True:
        raw = input(prompt).strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")


def read_priority(prompt: str = "Priority (low/medium/high): ") -> str:
    """Возвращает один из VALID_PRIORITIES (регистр ввода не важен)."""
    while True:
        priority = input(prompt).strip().lower()
        if priority in VALID_PRIORITIES:
            return priority
        print("Invalid priority. Enter low, medium, or high.")


def read_status(prompt: str = "Status (new/in_progress/done): ") -> str:
    """Возвращает один из VALID_STATUSES (регистр ввода не важен)."""
    while True:
        status = input(prompt).strip().lower()
        if status in VALID_STATUSES:
            return status
        print("Invalid status. Enter new, in_progress, or done.")


def read_yes_no(prompt: str) -> bool:
    """True для y/yes, False для n/no; иные ответы отвергаются."""
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Enter y or n.")


def print_table(title: str, rows: list[tuple], columns: list[str]) -> None:
    """
    Печатает таблицу: заголовок, разделитель, строки с выравниванием по ширине.

    Длина колонок ограничена MAX_COLUMN_WIDTH; длинные значения обрезаются с «...».
    """
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("No data.")
        return

    string_rows = [
        tuple("" if item is None else str(item) for item in row) for row in rows
    ]

    widths: list[int] = []
    for idx, column in enumerate(columns):
        max_cell_width = max((len(row[idx]) for row in string_rows), default=0)
        widths.append(
            min(MAX_COLUMN_WIDTH, max(len(column), max_cell_width)),
        )

    def format_cell(value: str, width: int) -> str:
        """Форматирует одну ячейку: обрезка или дополнение пробелами слева."""
        if len(value) > width:
            if width <= 3:
                return value[:width]
            return f"{value[: width - 3]}..."
        return value.ljust(width)

    header = " | ".join(
        format_cell(col, widths[idx]) for idx, col in enumerate(columns)
    )
    separator = "-+-".join("-" * width for width in widths)
    print(header)
    print(separator)
    for row in string_rows:
        line = " | ".join(
            format_cell(row[idx], widths[idx]) for idx in range(len(columns))
        )
        print(line)
