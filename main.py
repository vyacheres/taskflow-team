"""
Точка входа и меню консольного приложения TaskFlow Team.

Логика: цикл главного меню, вызов подменю сотрудников/задач/фильтров/отчётов,
очистка экрана и короткое сообщение «flash» о результате последнего действия.
"""

from __future__ import annotations

import sqlite3

from config import DB_PATH, SCHEMA_PATH, SEED_PATH
from database import Database
from utils import (
    MAX_FULL_NAME,
    MAX_POSITION,
    MAX_TASK_DESCRIPTION,
    MAX_TASK_TITLE,
    MAX_TEAM,
    clear_screen,
    print_table,
    read_date,
    read_email,
    read_int,
    read_optional_limited,
    read_priority,
    read_required_limited,
    read_status,
    read_yes_no,
    wait_for_enter,
)

# Тексты ошибок/сообщений длиннее 88 символов вынесены в константы (PEP 8).
_MSG_TASK_ADD_CHECK = (
    "Could not add task: data does not satisfy database rules "
    "(priority or status)."
)
_MSG_TASK_UPDATE_CHECK = (
    "Could not update task: data does not satisfy database rules "
    "(priority or status)."
)
_MSG_STATUS_CHECK = (
    "Could not update status: invalid value for database rules."
)


def employee_menu(db: Database) -> None:
    """
    Подменю «Сотрудники»: добавление, список, изменение, удаление.

    Использует переменную flash — строка, показываемая один раз после
    очистки экрана перед следующим отображением меню.
    """
    flash = ""
    while True:
        clear_screen()
        if flash:
            print(flash + "\n")
            flash = ""
        print(
            "--- Employees ---\n"
            "1. Add employee\n"
            "2. Show employees\n"
            "3. Update employee\n"
            "4. Delete employee\n"
            "0. Back",
        )
        choice = input("Select an action: ").strip()

        if choice == "1":
            clear_screen()
            full_name = read_required_limited("Full name: ", MAX_FULL_NAME)
            position = read_required_limited("Position: ", MAX_POSITION)
            email = read_email("Email: ")
            team = read_optional_limited("Team (optional): ", MAX_TEAM)
            try:
                db.add_employee(full_name, position, email, team or None)
                flash = "Employee added."
            except sqlite3.IntegrityError:
                flash = "Error: email must be unique."
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"

        elif choice == "2":
            clear_screen()
            try:
                rows = db.list_employees()
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            print_table(
                "Employees",
                rows,
                ["ID", "Full Name", "Position", "Email", "Team"],
            )
            wait_for_enter()

        elif choice == "3":
            clear_screen()
            employee_id = read_int("Employee ID: ")
            full_name = read_required_limited("New full name: ", MAX_FULL_NAME)
            position = read_required_limited("New position: ", MAX_POSITION)
            email = read_email("New email: ")
            team = read_optional_limited("New team (optional): ", MAX_TEAM)
            try:
                updated = db.update_employee(
                    employee_id,
                    full_name,
                    position,
                    email,
                    team or None,
                )
            except sqlite3.IntegrityError:
                flash = "Error: email must be unique."
                continue
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            flash = "Employee updated." if updated else "Employee not found."

        elif choice == "4":
            clear_screen()
            employee_id = read_int("Employee ID: ")
            if not db.employee_exists(employee_id):
                flash = "Employee not found."
                continue
            task_count = db.count_tasks_by_employee(employee_id)
            if task_count > 0:
                warn = (
                    f"Warning: {task_count} task(s) are assigned to this employee. "
                    "Deleting the employee will permanently remove those tasks "
                    "(ON DELETE CASCADE)."
                )
                print(warn)
                if not read_yes_no("Continue? (y/n): "):
                    flash = "Cancelled."
                    continue
            try:
                deleted = db.delete_employee(employee_id)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            flash = "Employee deleted." if deleted else "Employee not found."

        elif choice == "0":
            return
        else:
            flash = "Unknown command."


def task_menu(db: Database) -> None:
    """Подменю «Задачи»: CRUD и смена статуса; логика flash такая же, как у сотрудников."""
    flash = ""
    while True:
        clear_screen()
        if flash:
            print(flash + "\n")
            flash = ""
        print(
            "--- Tasks ---\n"
            "1. Add task\n"
            "2. Show tasks\n"
            "3. Update task\n"
            "4. Update task status\n"
            "5. Delete task\n"
            "0. Back",
        )
        choice = input("Select an action: ").strip()

        if choice == "1":
            clear_screen()
            title = read_required_limited("Title: ", MAX_TASK_TITLE)
            description = read_required_limited(
                "Description: ",
                MAX_TASK_DESCRIPTION,
            )
            deadline = read_date("Deadline (YYYY-MM-DD): ")
            priority = read_priority()
            status = read_status()
            employee_id = read_int("Employee ID: ")
            try:
                created = db.add_task(
                    title,
                    description,
                    deadline,
                    priority,
                    status,
                    employee_id,
                )
            except sqlite3.IntegrityError:
                flash = _MSG_TASK_ADD_CHECK
                continue
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            if created:
                flash = "Task added."
            else:
                flash = "Error: employee with this ID was not found."

        elif choice == "2":
            clear_screen()
            try:
                rows = db.list_tasks()
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            print_table(
                "Tasks",
                rows,
                ["ID", "Title", "Deadline", "Priority", "Status", "Assignee"],
            )
            wait_for_enter()

        elif choice == "3":
            clear_screen()
            task_id = read_int("Task ID: ")
            if not db.task_exists(task_id):
                flash = "Task not found."
                continue
            title = read_required_limited("New title: ", MAX_TASK_TITLE)
            description = read_required_limited(
                "New description: ",
                MAX_TASK_DESCRIPTION,
            )
            deadline = read_date("New deadline (YYYY-MM-DD): ")
            priority = read_priority("New priority (low/medium/high): ")
            status = read_status("New status (new/in_progress/done): ")
            employee_id = read_int("New employee ID: ")
            if not db.employee_exists(employee_id):
                flash = "Employee not found."
                continue
            try:
                updated = db.update_task(
                    task_id,
                    title,
                    description,
                    deadline,
                    priority,
                    status,
                    employee_id,
                )
            except sqlite3.IntegrityError:
                flash = _MSG_TASK_UPDATE_CHECK
                continue
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            flash = "Task updated." if updated else "Task not found."

        elif choice == "4":
            clear_screen()
            task_id = read_int("Task ID: ")
            if not db.task_exists(task_id):
                flash = "Task not found."
                continue
            status = read_status()
            try:
                updated = db.update_task_status(task_id, status)
            except sqlite3.IntegrityError:
                flash = _MSG_STATUS_CHECK
                continue
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            flash = "Status updated." if updated else "Task not found."

        elif choice == "5":
            clear_screen()
            task_id = read_int("Task ID: ")
            if not db.task_exists(task_id):
                flash = "Task not found."
                continue
            if not read_yes_no("Delete this task permanently? (y/n): "):
                flash = "Cancelled."
                continue
            try:
                deleted = db.delete_task(task_id)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            flash = "Task deleted." if deleted else "Task not found."

        elif choice == "0":
            return
        else:
            flash = "Unknown command."


def filter_menu(db: Database) -> None:
    """Подменю фильтров задач; после таблицы — пауза Enter."""
    flash = ""
    while True:
        clear_screen()
        if flash:
            print(flash + "\n")
            flash = ""
        print(
            "--- Task Filters ---\n"
            "1. By employee\n"
            "2. By status\n"
            "3. By priority\n"
            "4. Overdue tasks\n"
            "0. Back",
        )
        choice = input("Select an action: ").strip()
        rows: list[tuple] = []

        if choice == "1":
            clear_screen()
            employee_id = read_int("Employee ID: ")
            if not db.employee_exists(employee_id):
                flash = "Employee not found."
                continue
            try:
                rows = db.filter_tasks(employee_id=employee_id)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue

        elif choice == "2":
            clear_screen()
            status = read_status()
            try:
                rows = db.filter_tasks(status=status)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue

        elif choice == "3":
            clear_screen()
            priority = read_priority()
            try:
                rows = db.filter_tasks(priority=priority)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue

        elif choice == "4":
            clear_screen()
            try:
                rows = db.filter_tasks(overdue=True)
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue

        elif choice == "0":
            return
        else:
            flash = "Unknown command."
            continue

        print_table(
            "Filter Results",
            rows,
            ["ID", "Title", "Deadline", "Priority", "Status", "Assignee"],
        )
        wait_for_enter()


def reports_menu(db: Database) -> None:
    """Подменю отчётов: сводка по команде и по сотрудникам."""
    flash = ""
    while True:
        clear_screen()
        if flash:
            print(flash + "\n")
            flash = ""
        print(
            "--- Reports ---\n"
            "1. Team summary\n"
            "2. Employee summary\n"
            "0. Back",
        )
        choice = input("Select an action: ").strip()

        if choice == "1":
            clear_screen()
            try:
                summary = db.team_summary()
                total, done, prog, new, overdue = summary
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            rows = [(total, done, prog, new, overdue)]
            print_table(
                "Team Summary",
                rows,
                ["Total", "Done", "In Progress", "New", "Overdue"],
            )
            wait_for_enter()

        elif choice == "2":
            clear_screen()
            try:
                rows = db.employee_summary()
            except sqlite3.Error as exc:
                flash = f"Database error: {exc}"
                continue
            print_table(
                "Employee Summary",
                rows,
                ["ID", "Full Name", "Total Tasks", "Done", "Overdue"],
            )
            wait_for_enter()

        elif choice == "0":
            return
        else:
            flash = "Unknown command."


def main() -> None:
    """
    Создаёт Database, инициализирует схему, запускает главный цикл меню.

    При ошибке инициализации печатает сообщение и завершает работу.
    Соединение с БД закрывается в finally.
    """
    db = Database(DB_PATH, SCHEMA_PATH, SEED_PATH)
    try:
        try:
            db.initialize()
        except FileNotFoundError as exc:
            print(f"Startup error: required file is missing ({exc}).")
            return
        except OSError as exc:
            print(
                "Startup error: cannot read schema or open database "
                f"({exc}).",
            )
            return
        except sqlite3.Error as exc:
            print(f"Startup error: database initialization failed ({exc}).")
            return

        flash = "TaskFlow Team started. Database is ready."
        while True:
            clear_screen()
            if flash:
                print(flash + "\n")
                flash = ""
            print(
                "=== Main Menu ===\n"
                "1. Employees\n"
                "2. Tasks\n"
                "3. Filters\n"
                "4. Reports\n"
                "5. Load demo data (seed)\n"
                "0. Exit",
            )
            choice = input("Select an action: ").strip()

            if choice == "1":
                employee_menu(db)
            elif choice == "2":
                task_menu(db)
            elif choice == "3":
                filter_menu(db)
            elif choice == "4":
                reports_menu(db)
            elif choice == "5":
                clear_screen()
                seed_warn = (
                    "This will erase all employees and tasks, then load data "
                    "from sql/seed.sql."
                )
                print(seed_warn)
                if read_yes_no("Continue? (y/n): "):
                    try:
                        db.load_seed()
                        flash = "Demo data loaded."
                    except OSError as exc:
                        flash = f"Error reading seed file: {exc}"
                    except sqlite3.Error as exc:
                        flash = f"Database error: {exc}"
                else:
                    flash = "Cancelled."
            elif choice == "0":
                clear_screen()
                print("Exiting program.")
                break
            else:
                flash = "Unknown command."
    finally:
        db.close()


if __name__ == "__main__":
    main()
