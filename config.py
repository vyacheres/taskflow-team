"""
Конфигурация путей приложения TaskFlow Team.

Здесь задаются каталог проекта и абсолютные пути к файлу SQLite,
схеме БД и сид-скрипту. Остальной код импортирует готовые константы,
чтобы не дублировать строки путей.
"""

from pathlib import Path

# Каталог, в котором лежит этот файл (корень пакета приложения).
BASE_DIR = Path(__file__).resolve().parent
# Путь к файлу базы данных рядом с кодом.
DB_PATH = BASE_DIR / "taskflow_team.db"
# SQL-файл со структурой таблиц (CREATE …).
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
# SQL-файл с демонстрационными данными (очистка и INSERT).
SEED_PATH = BASE_DIR / "sql" / "seed.sql"
