"""
Слой доступа к SQLite для TaskFlow Team.

Класс Database инкапсулирует соединение с БД на время работы приложения,
выполняет запросы с параметрами и фиксирует изменения через commit().
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

# Тип значений, передаваемых в SQL как плейсхолдеры «?» (идентификаторы и строки).
SqlParam = int | str


class Database:
    """
    Работа с локальной базой SQLite.

    Одно соединение открывается при первом запросе и переиспользуется
    до вызова close(). Включены внешние ключи (PRAGMA foreign_keys).
    """

    def __init__(
        self,
        db_path: Path,
        schema_path: Path,
        seed_path: Path | None = None,
    ) -> None:
        """Сохраняет пути к БД, схеме и опционально к сид-файлу; соединение ещё не создано."""
        self.db_path = db_path
        self.schema_path = schema_path
        self.seed_path = seed_path
        self._connection: sqlite3.Connection | None = None

    def _conn(self) -> sqlite3.Connection:
        """Возвращает активное соединение, при необходимости создаёт его один раз."""
        if self._connection is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            self._connection = conn
        return self._connection

    def close(self) -> None:
        """Закрывает соединение с БД, если оно было открыто."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def initialize(self) -> None:
        """Читает schema.sql и применяет его к БД (создание таблиц при отсутствии)."""
        schema_sql = self.schema_path.read_text(encoding="utf-8")
        conn = self._conn()
        conn.executescript(schema_sql)
        conn.commit()

    def load_seed(self) -> None:
        """
        Выполняет sql/seed.sql: очистка и вставка демо-данных.

        Raises:
            ValueError: если путь к сиду не задан (None).
        """
        if self.seed_path is None:
            raise ValueError("Seed path is not configured.")
        seed_sql = self.seed_path.read_text(encoding="utf-8")
        conn = self._conn()
        conn.executescript(seed_sql)
        conn.commit()

    def add_employee(
        self,
        full_name: str,
        position: str,
        email: str,
        team: str | None,
    ) -> None:
        """Вставляет новую строку в таблицу employees."""
        query = """
        INSERT INTO employees (full_name, position, email, team)
        VALUES (?, ?, ?, ?);
        """
        conn = self._conn()
        conn.execute(query, (full_name, position, email, team or None))
        conn.commit()

    def list_employees(self) -> list[tuple]:
        """Возвращает всех сотрудников; пустое team показывается как «-»."""
        query = """
        SELECT id, full_name, position, email, COALESCE(team, '-')
        FROM employees
        ORDER BY id;
        """
        conn = self._conn()
        rows = conn.execute(query).fetchall()
        return [tuple(row) for row in rows]

    def update_employee(
        self,
        employee_id: int,
        full_name: str,
        position: str,
        email: str,
        team: str | None,
    ) -> bool:
        """Обновляет поля сотрудника по id; True если строка была найдена и изменена."""
        query = """
        UPDATE employees
        SET full_name = ?, position = ?, email = ?, team = ?
        WHERE id = ?;
        """
        conn = self._conn()
        cursor = conn.execute(
            query,
            (full_name, position, email, team or None, employee_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete_employee(self, employee_id: int) -> bool:
        """Удаляет сотрудника по id (задачи каскадно удаляются согласно схеме)."""
        query = "DELETE FROM employees WHERE id = ?;"
        conn = self._conn()
        cursor = conn.execute(query, (employee_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count_tasks_by_employee(self, employee_id: int) -> int:
        """Считает задачи, назначенные на указанного сотрудника."""
        conn = self._conn()
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM tasks WHERE employee_id = ?",
            (employee_id,),
        ).fetchone()
        return int(row["c"] or 0)

    def task_exists(self, task_id: int) -> bool:
        """Проверяет, существует ли задача с данным id."""
        conn = self._conn()
        row = conn.execute(
            "SELECT 1 FROM tasks WHERE id = ? LIMIT 1",
            (task_id,),
        ).fetchone()
        return row is not None

    def add_task(
        self,
        title: str,
        description: str,
        deadline: str,
        priority: str,
        status: str,
        employee_id: int,
    ) -> bool:
        """
        Добавляет задачу.

        Returns:
            False, если сотрудник с employee_id не существует; иначе True после вставки.
        """
        if not self.employee_exists(employee_id):
            return False
        query = """
        INSERT INTO tasks (title, description, deadline, priority, status, employee_id)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        conn = self._conn()
        conn.execute(
            query,
            (title, description, deadline, priority, status, employee_id),
        )
        conn.commit()
        return True

    def list_tasks(self) -> list[tuple]:
        """Список задач с именем исполнителя, сортировка по сроку и id."""
        query = """
        SELECT
            t.id,
            t.title,
            t.deadline,
            t.priority,
            t.status,
            e.full_name
        FROM tasks t
        JOIN employees e ON e.id = t.employee_id
        ORDER BY t.deadline, t.id;
        """
        conn = self._conn()
        rows = conn.execute(query).fetchall()
        return [tuple(row) for row in rows]

    def update_task(
        self,
        task_id: int,
        title: str,
        description: str,
        deadline: str,
        priority: str,
        status: str,
        employee_id: int,
    ) -> bool:
        """
        Полное обновление задачи.

        Returns:
            False, если исполнитель не существует или задача с task_id не найдена.
        """
        if not self.employee_exists(employee_id):
            return False
        query = """
        UPDATE tasks
        SET title = ?, description = ?, deadline = ?, priority = ?, status = ?,
            employee_id = ?
        WHERE id = ?;
        """
        conn = self._conn()
        cursor = conn.execute(
            query,
            (
                title,
                description,
                deadline,
                priority,
                status,
                employee_id,
                task_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0

    def update_task_status(self, task_id: int, status: str) -> bool:
        """Меняет только статус задачи; True если строка найдена."""
        query = "UPDATE tasks SET status = ? WHERE id = ?;"
        conn = self._conn()
        cursor = conn.execute(query, (status, task_id))
        conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по id; True если удалена хотя бы одна строка."""
        query = "DELETE FROM tasks WHERE id = ?;"
        conn = self._conn()
        cursor = conn.execute(query, (task_id,))
        conn.commit()
        return cursor.rowcount > 0

    def filter_tasks(
        self,
        employee_id: int | None = None,
        status: str | None = None,
        priority: str | None = None,
        overdue: bool = False,
    ) -> list[tuple]:
        """
        Выборка задач с JOIN на сотрудников и опциональными условиями.

        overdue=True добавляет условие «дедлайн раньше сегодня и статус не done».
        """
        query = """
        SELECT
            t.id,
            t.title,
            t.deadline,
            t.priority,
            t.status,
            e.full_name
        FROM tasks t
        JOIN employees e ON e.id = t.employee_id
        WHERE 1 = 1
        """
        params: list[SqlParam] = []
        if employee_id is not None:
            query += " AND t.employee_id = ?"
            params.append(employee_id)
        if status is not None:
            query += " AND t.status = ?"
            params.append(status)
        if priority is not None:
            query += " AND t.priority = ?"
            params.append(priority)
        if overdue:
            query += " AND date(t.deadline) < date('now') AND t.status != 'done'"
        query += " ORDER BY t.deadline, t.id;"
        conn = self._conn()
        rows = conn.execute(query, tuple(params)).fetchall()
        return [tuple(row) for row in rows]

    def team_summary(self) -> tuple[int, int, int, int, int]:
        """Агрегаты по всем задачам: всего, по статусам и число просроченных."""
        query = """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS done_count,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_count,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) AS new_count,
            SUM(
                CASE
                    WHEN date(deadline) < date('now') AND status != 'done' THEN 1
                    ELSE 0
                END
            ) AS overdue_count
        FROM tasks;
        """
        conn = self._conn()
        row = conn.execute(query).fetchone()
        return (
            row["total"] or 0,
            row["done_count"] or 0,
            row["in_progress_count"] or 0,
            row["new_count"] or 0,
            row["overdue_count"] or 0,
        )

    def employee_summary(self) -> list[tuple]:
        """По каждому сотруднику: всего задач, выполнено, просрочено (LEFT JOIN на задачи)."""
        query = """
        SELECT
            e.id,
            e.full_name,
            COUNT(t.id) AS total_tasks,
            SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS done_tasks,
            SUM(
                CASE
                    WHEN date(t.deadline) < date('now') AND t.status != 'done' THEN 1
                    ELSE 0
                END
            ) AS overdue_tasks
        FROM employees e
        LEFT JOIN tasks t ON t.employee_id = e.id
        GROUP BY e.id, e.full_name
        ORDER BY e.id;
        """
        conn = self._conn()
        rows = conn.execute(query).fetchall()
        return [
            (
                row["id"],
                row["full_name"],
                row["total_tasks"] or 0,
                row["done_tasks"] or 0,
                row["overdue_tasks"] or 0,
            )
            for row in rows
        ]

    def employee_exists(self, employee_id: int) -> bool:
        """Проверяет наличие строки в employees с заданным id."""
        query = "SELECT 1 FROM employees WHERE id = ? LIMIT 1;"
        conn = self._conn()
        row = conn.execute(query, (employee_id,)).fetchone()
        return row is not None
