"""Тесты слоя Database на временной файловой БД."""

import tempfile
import unittest
from pathlib import Path

from database import Database

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


class TestDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.db = Database(self.db_path, SCHEMA_PATH, None)
        self.db.initialize()

    def tearDown(self) -> None:
        self.db.close()
        self._tmpdir.cleanup()

    def test_employee_and_task_roundtrip(self) -> None:
        self.db.add_employee("Test User", "Dev", "test.user@example.com", None)
        rows = self.db.list_employees()
        self.assertEqual(len(rows), 1)
        emp_id = rows[0][0]
        self.assertTrue(self.db.add_task("T1", "D1", "2026-06-01", "low", "new", emp_id))
        self.assertTrue(self.db.task_exists(1))
        self.assertFalse(self.db.task_exists(999))
        tasks = self.db.list_tasks()
        self.assertEqual(len(tasks), 1)

    def test_team_summary_empty_tasks(self) -> None:
        total, done, prog, new, overdue = self.db.team_summary()
        self.assertEqual((total, done, prog, new, overdue), (0, 0, 0, 0, 0))

    def test_filter_unknown_employee_returns_empty_via_exists(self) -> None:
        self.assertFalse(self.db.employee_exists(42))
        rows = self.db.filter_tasks(employee_id=42)
        self.assertEqual(rows, [])

    def test_count_tasks_by_employee(self) -> None:
        self.db.add_employee("A", "R", "a@example.com", None)
        self.db.add_employee("B", "R", "b@example.com", None)
        r = self.db.list_employees()
        id_a, id_b = r[0][0], r[1][0]
        self.db.add_task("t", "d", "2026-01-01", "medium", "new", id_a)
        self.db.add_task("t2", "d", "2026-01-02", "medium", "new", id_a)
        self.assertEqual(self.db.count_tasks_by_employee(id_a), 2)
        self.assertEqual(self.db.count_tasks_by_employee(id_b), 0)
