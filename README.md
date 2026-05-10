# TaskFlow Team / Команда TaskFlow

---

## 1. Название проекта / Project name

**RU:** **TaskFlow Team** — консольное приложение на Python для учёта внутренних задач IT-компании: сотрудники, задачи, фильтры и отчёты в одной локальной базе SQLite.

**EN:** **TaskFlow Team** is a Python console app for internal task tracking in an IT company: employees, tasks, filters, and reports in a single local SQLite database.

---

## 2. Описание задачи / Task description

**RU:** **Контекст:** компания **NovaSoft**. **Заказчик** — тимлид команды Core Platform; **проблема** — задачи разбросаны по чатам и таблицам, сложно контролировать сроки и загрузку команды; **решение** — единый CLI с одной БД для сотрудников, задач, статусов и отчётов.

**EN:** **Context:** **NovaSoft** company. **Customer** — Core Platform team lead; **problem** — tasks scattered across chats and spreadsheets, making deadlines and team workload hard to control; **solution** — one CLI tool with a single database for employees, tasks, statuses, and reports.

---

## 3. Технологии / Technologies

| | RU | EN |
|---|----|----|
| **Язык** | Python 3.10+ | Python 3.10+ |
| **СУБД** | SQLite (файл `taskflow_team.db`, скрипты `sql/schema.sql`, `sql/seed.sql`) | SQLite (file `taskflow_team.db`, scripts `sql/schema.sql`, `sql/seed.sql`) |
| **Стандартная библиотека** | `sqlite3`, `pathlib`, `unittest`, консольный ввод-вывод | `sqlite3`, `pathlib`, `unittest`, console I/O |

Метаданные версии Python: `pyproject.toml` → `requires-python`.

---

## 4. Установка и запуск / Installation and launch

### RU (для проверяющего)

1. Установите **Python 3.10 или новее** и убедитесь, что команда `python` доступна в терминале.
2. Клонируйте или распакуйте проект и перейдите в каталог `taskflow_team` (корень, где лежит `main.py`).
3. Запуск приложения:
   ```bash
   python main.py
   ```
4. При первом запуске таблицы создаются из `sql/schema.sql`. Файл БД появится рядом с кодом (`taskflow_team.db`).
5. (Опционально) Демо-данные: в главном меню пункт **5. Load demo data (seed)** или выполните команду из раздела «Примеры» ниже.
6. (Опционально) Тесты:
   ```bash
   python -m unittest discover -s tests -v
   ```

### EN (for the reviewer)

1. Install **Python 3.10+** and ensure `python` works in your terminal.
2. Open the project root folder `taskflow_team` (where `main.py` lives).
3. Run:
   ```bash
   python main.py
   ```
4. On first launch, tables are created from `sql/schema.sql`. The DB file `taskflow_team.db` appears next to the code.
5. (Optional) Demo data: main menu → **5. Load demo data (seed)**, or use the shell one-liner in **Usage examples**.
6. (Optional) Tests:
   ```bash
   python -m unittest discover -s tests -v
   ```

**RU:** Экран очищается перед каждым меню; после больших таблиц нажмите **Enter**, чтобы вернуться к меню. Если нет `sql/schema.sql` или нет доступа к файлу БД — программа выведет сообщение об ошибке и завершится.

**EN:** The screen is cleared before each menu; after large tables, press **Enter** to return. If `sql/schema.sql` is missing or the DB file cannot be opened, the app prints an error and exits.

---

## 5. Примеры использования / Usage examples

**RU:** Ниже — текстовый сценарий работы с приложением.

**EN:** Below is a text-only usage scenario.

### RU

```
=== Main Menu ===
…
Выберите 5 → подтвердите загрузку сида → в меню Employees (1) появятся 8 сотрудников.
Tasks (2) — список задач спринта.
Filters (3) → 4 — просроченные задачи.
Reports (4) → 1 — сводка по команде.
```

Загрузка сида из shell (альтернатива меню):

```bash
python -c "from pathlib import Path; import sqlite3; conn=sqlite3.connect('taskflow_team.db'); conn.executescript(Path('sql/seed.sql').read_text(encoding='utf-8')); conn.commit(); conn.close()"
```

### EN

```
=== Main Menu ===
…
Choose 5 → confirm seed load → Employees (1) shows 8 demo employees.
Tasks (2) — sprint task list.
Filters (3) → option 4 — overdue tasks.
Reports (4) → option 1 — team summary.
```

Shell seed (alternative to the menu):

```bash
python -c "from pathlib import Path; import sqlite3; conn=sqlite3.connect('taskflow_team.db'); conn.executescript(Path('sql/seed.sql').read_text(encoding='utf-8')); conn.commit(); conn.close()"
```

---

## 6. Структура проекта / Project structure

```text
taskflow_team/
├── main.py              # RU: меню CLI, вызов Database, очистка экрана. EN: CLI menus, Database calls, screen clear.
├── database.py          # RU: SQL-запросы, одно соединение на сессию. EN: SQL layer, one connection per session.
├── utils.py             # RU: ввод, валидация, таблицы в консоли. EN: input helpers, validation, table printing.
├── config.py            # RU: пути к БД и SQL. EN: paths to DB and SQL files.
├── sql/
│   ├── schema.sql       # RU: CREATE TABLE. EN: schema DDL.
│   └── seed.sql         # RU: демо-данные. EN: demo seed data.
├── docs/
│   └── er_diagram.txt   # RU: ER-модель (текст). EN: ER model (text).
├── tests/               # RU: unittest. EN: unit tests.
├── pyproject.toml       # RU: requires-python и метаданные. EN: Python version metadata.
└── README.md            # RU/EN: этот файл. EN: this file.
```

---

## 7. Схема базы данных / Database schema

**RU:** Текстовая ER-диаграмма в нотации Мартина и пояснения связей — в **`docs/er_diagram.txt`**. Кратко:

- Таблица **`employees`**: `id`, ФИО, должность, уникальный `email`, опциональная `team`.
- Таблица **`tasks`**: `id`, `title`, `description`, `deadline` (TEXT `YYYY-MM-DD`), `priority`, `status`, `employee_id` → FK на `employees(id)` **ON DELETE CASCADE**, `created_at`.
- Связь **1 : N** (один сотрудник — много задач; у задачи один исполнитель).

**EN:** Textual ER diagram (Martin notation) — **`docs/er_diagram.txt`**. Summary:

- **`employees`**: `id`, name, role, unique `email`, optional `team`.
- **`tasks`**: `id`, `title`, `description`, `deadline` (TEXT `YYYY-MM-DD`), `priority`, `status`, `employee_id` → FK to `employees(id)` **ON DELETE CASCADE**, `created_at`.
- Relationship **1 : N** (one employee, many tasks; each task has one assignee).

---

## 8. Известные проблемы / Known issues

**RU:**

- Интерфейс только CLI, без GUI.
- Проверка email ориентирована на «простой» ASCII-шаблон; адреса с нестандартными символами могут быть отклонены.
- Лимиты длины полей заданы в коде (`utils.py`), в SQLite отдельных `CHECK(length…)` нет.
- Поле `created_at` в таблице есть, в текущих списках задач в консоли не выводится.
- Сравнение «сегодня» для просрочки завязано на SQLite `date('now')` (UTC-поведение SQLite).

**EN:**

- CLI only; no GUI.
- Email validation uses a simple ASCII-oriented pattern; some valid real-world addresses may be rejected.
- Field length limits are enforced in code (`utils.py`), not as SQLite `CHECK` constraints.
- Column `created_at` exists but is not shown in current task listings.
- “Overdue” logic relies on SQLite `date('now')` (SQLite’s date semantics).

---

## 9. Автор / Author

| | |
|---|--|
| **ФИО / Name** | Vyacheslav Panyuhin (Вячеслав Панюхин) |
| **Курс / Course** | 2 |
| **Группа / Group** | 11ФС |

---

## Дополнительно: сценарий демо / Extra: demo scenario

**RU:** 1) Employees — команда после сида. 2) Tasks — задачи спринта. 3) Filters — просроченные и приоритет. 4) Reports — сводки. 5) Смена статуса задачи и повтор отчёта.

**EN:** 1) Employees — team after seed. 2) Tasks — sprint items. 3) Filters — overdue / priority. 4) Reports — summaries. 5) Change a task status and refresh reports.
