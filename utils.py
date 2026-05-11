"""
Вспомогательные функции ввода-вывода для консольного приложения TaskFlow Team.

Содержит: проверку email, ограничение длины полей, чтение дат и перечислений,
очистку экрана, табличный вывод и подтверждения yes/no.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime

from config import ENABLE_COLORS, MAX_DISPLAY_COLUMN_WIDTH, TASKS_VIEW_MODE

# Допустимые значения приоритета (совпадают с CHECK в таблице tasks).
VALID_PRIORITIES = {"low", "medium", "high"}
# Допустимые статусы задачи.
VALID_STATUSES = {"new", "in_progress", "done"}
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

_ANSI_RESET = "\033[0m"
_ANSI_BOLD = "\033[1m"
_PRIORITY_COLORS = {
    "high": "\033[31m",  # red
    "medium": "\033[33m",  # yellow
    "low": "\033[32m",  # green
}
_STATUS_COLORS = {
    "new": "\033[37m",  # white
    "in_progress": "\033[36m",  # cyan
    "done": "\033[32m",  # green
}


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
    Длина колонок подстраивается под максимальную длину значения в колонке.
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
        widths.append(min(MAX_DISPLAY_COLUMN_WIDTH, max(len(column), max_cell_width)))

    def wrap_cell(value: str, width: int) -> list[str]:
        """Переносит значение по словам; ничего не отбрасывает."""
        if value == "":
            return [""]
        return textwrap.wrap(
            value,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        )

    header = " | ".join(col.ljust(widths[idx]) for idx, col in enumerate(columns))
    separator = "-+-".join("-" * width for width in widths)
    print(header)
    print(separator)
    for row in string_rows:
        wrapped_cells = [wrap_cell(row[idx], widths[idx]) for idx in range(len(columns))]
        line_count = max(len(lines) for lines in wrapped_cells)
        for line_idx in range(line_count):
            line_parts = []
            for col_idx, lines in enumerate(wrapped_cells):
                cell_line = lines[line_idx] if line_idx < len(lines) else ""
                # На строках-продолжениях явно показываем, что это тот же ряд.
                if line_idx > 0 and col_idx == 0 and cell_line == "":
                    cell_line = "↳"
                line_parts.append(cell_line.ljust(widths[col_idx]))
            print(" | ".join(line_parts))
        print(separator)


def _supports_color() -> bool:
    """Возвращает True, если терминал, вероятно, поддерживает ANSI-цвета."""
    if not ENABLE_COLORS:
        return False
    if not sys.stdout.isatty():
        return False
    if os.name != "nt":
        return True
    return bool(
        os.environ.get("WT_SESSION")
        or os.environ.get("ANSICON")
        or os.environ.get("TERM")
        or os.environ.get("ConEmuANSI") == "ON"
    )


def _paint(text: str, color_code: str, bold: bool = False) -> str:
    """Оборачивает текст в ANSI-цвета при поддержке терминала."""
    if not _supports_color():
        return text
    prefix = _ANSI_BOLD + color_code if bold else color_code
    return f"{prefix}{text}{_ANSI_RESET}"


def _format_priority(priority: str) -> str:
    color = _PRIORITY_COLORS.get(priority.lower(), "")
    return _paint(priority, color, bold=True) if color else priority


def _format_status(status: str) -> str:
    color = _STATUS_COLORS.get(status.lower(), "")
    return _paint(status, color, bold=True) if color else status


def print_tasks_cards(title: str, rows: list[tuple]) -> None:
    """
    Печатает задачи в режиме карточек (по одной записи блоком).
    Ожидаемый формат row: (id, title, deadline, priority, status, assignee).
    """
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("No data.")
        return

    card_width = 96
    border = "+" + "-" * (card_width - 2) + "+"
    for row in rows:
        task_id, task_title, deadline, priority, status, assignee = row
        title_lines = textwrap.wrap(
            str(task_title),
            width=card_width - 14,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]
        print(border)
        print(f"| ID: {str(task_id).ljust(card_width - 8)}|")
        print(f"| Title: {title_lines[0].ljust(card_width - 10)}|")
        for extra in title_lines[1:]:
            print(f"|        {extra.ljust(card_width - 10)}|")
        print(f"| Deadline: {str(deadline).ljust(card_width - 13)}|")
        plain_meta = f"Priority: {str(priority)}    Status: {str(status)}"
        print(f"| {plain_meta.ljust(card_width - 3)}|")
        print(f"| Assignee: {str(assignee).ljust(card_width - 13)}|")
        print(border)
        print(
            f"  {_format_priority(str(priority))} priority"
            f" | status: {_format_status(str(status))}",
        )


def print_tasks(title: str, rows: list[tuple]) -> None:
    """Печатает задачи в режиме из config (cards/table)."""
    mode = TASKS_VIEW_MODE.strip().lower()
    if mode == "table":
        colored_rows: list[tuple] = []
        for task_id, task_title, deadline, priority, status, assignee in rows:
            colored_rows.append(
                (
                    task_id,
                    task_title,
                    deadline,
                    _format_priority(str(priority)),
                    _format_status(str(status)),
                    assignee,
                ),
            )
        print_table(
            title,
            colored_rows,
            ["ID", "Title", "Deadline", "Priority", "Status", "Assignee"],
        )
        return
    print_tasks_cards(title, rows)
