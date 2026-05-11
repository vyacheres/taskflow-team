<div align="center">

# TaskFlow Team

**Консольное приложение для учёта задач и сотрудников · SQLite · Python 3.10+**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/database-SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/tests-12%20passed-success?style=flat)](https://github.com/vyacheres/taskflow-team)

</div>

---

## Оглавление · Table of contents

| RU | EN |
|----|-----|
| [1. Название проекта](#s1) | [1. Project name](#s1) |
| [2. Описание задачи](#s2) | [2. Task description](#s2) |
| [3. Технологии](#s3) | [3. Technologies](#s3) |
| [4. Установка и запуск](#s4) | [4. Installation and launch](#s4) |
| [5. Примеры использования](#s5) | [5. Usage examples](#s5) |
| [6. Структура проекта](#s6) | [6. Project structure](#s6) |
| [7. Схема БД](#s7) | [7. Database schema](#s7) |
| [8. Известные ограничения](#s8) | [8. Known issues](#s8) |
| [9. Тестирование](#s9) | [9. Testing](#s9) |
| [10. Автор](#s10) | [10. Author](#s10) |
| [Демо-сценарий](#demo) | [Demo scenario](#demo) |

---

<a id="s1"></a>

## 1. Название проекта / Project name

| RU | EN |
|----|-----|
| **TaskFlow Team** — приложение на Python для учёта внутренних задач IT-компании: сотрудники, задачи, фильтры и отчёты в одной локальной базе **SQLite**. | **TaskFlow Team** is a Python **console** app for internal task tracking: employees, tasks, filters, and reports in a single local **SQLite** database. |

---

<a id="s2"></a>

## 2. Описание задачи / Task description

| RU | EN |
|----|-----|
| **Контекст:** компания **NovaSoft**. **Заказчик** — тимлид команды Core Platform. **Проблема:** задачи разбросаны по чатам и таблицам, сложно контролировать сроки и загрузку. **Решение:** единый CLI и одна БД для сотрудников, задач, статусов и отчётов. | **Context:** **NovaSoft**. **Customer:** Core Platform team lead. **Problem:** tasks scattered across chats and spreadsheets; deadlines and workload are hard to control. **Solution:** one CLI and one database for employees, tasks, statuses, and reports. |

---

<a id="s3"></a>

## 3. Технологии / Technologies

| Компонент · Component | Описание · Details |
|-----------------------|--------------------|
| **Язык · Language** | Python **3.10+** (`pyproject.toml` → `requires-python`) |
| **СУБД · DBMS** | **SQLite** — файл `taskflow_team.db`, скрипты `sql/schema.sql`, `sql/seed.sql` |
| **Библиотеки · Stdlib** | `sqlite3`, `pathlib`, `unittest`, `textwrap`, консольный ввод-вывод · console I/O |
| **Рендеринг CLI · CLI rendering** | Таблицы с переносом длинного текста + режим карточек задач + ANSI-подсветка статуса/приоритета |

---

<a id="s4"></a>

## 4. Установка и запуск / Installation and launch

### RU

1. Установите **Python 3.10+**, в терминале доступна команда `python`.
2. Откройте каталог проекта (корень, где лежит `main.py`).
3. Запуск:

   ```bash
   python main.py
   ```

4. При первом запуске создаются таблицы из `sql/schema.sql`; рядом появится `taskflow_team.db`.
5. **Демо-данные:** в главном меню пункт **5. Load demo data (seed)** или команда из раздела [Примеры](#s5).
6. **Тесты:**

   ```bash
   python -m unittest discover -s tests -v
   ```

   Ожидаемый результат: **12 tests, OK**.

> Экран очищается перед каждым меню; после больших таблиц нажмите **Enter**. Если нет `sql/schema.sql` или нет доступа к файлу БД — программа сообщит об ошибке и завершится.
> Для задач можно менять режим вывода в `config.py`: `TASKS_VIEW_MODE = "cards"` или `"table"`. Цвета включаются флагом `ENABLE_COLORS`, ширина карточки задаётся `TASK_CARD_WIDTH`.

### EN

1. Install **Python 3.10+**; ensure `python` works in your terminal.
2. Open the project root (folder containing `main.py`).
3. Run:

   ```bash
   python main.py
   ```

4. On first launch, tables are created from `sql/schema.sql`; `taskflow_team.db` appears next to the code.
5. **Demo data:** main menu → **5. Load demo data (seed)**, or the shell command in [Usage examples](#s5).
6. **Tests:**

   ```bash
   python -m unittest discover -s tests -v
   ```

   Expected: **12 tests, OK**.

> The screen is cleared before each menu; after large tables, press **Enter**. If `sql/schema.sql` is missing or the DB file cannot be opened, the app prints an error and exits.
> Task output mode is configurable in `config.py`: `TASKS_VIEW_MODE = "cards"` or `"table"`. Colors are controlled by `ENABLE_COLORS`, and card width by `TASK_CARD_WIDTH`.

---

<a id="s5"></a>

## 5. Примеры использования / Usage examples

| RU | EN |
|----|-----|
| Ниже — **текстовый сценарий** работы с приложением (без скриншотов). | Below is a **text-only** walkthrough (no screenshots). |

### RU — сценарий (актуальный формат)

```text
=== Main Menu ===
…
5 → подтвердить seed → Employees (1): 8 сотрудников
Tasks (2) → карточки задач:
----------------------------------------------------------------
Task #13
Title: Optimize slow SQL query in dashboard
Deadline: 2026-04-21
Priority: high | Status: in_progress
Assignee: Dmitry Orlov
----------------------------------------------------------------
Filters (3) → 4 — просроченные задачи
Reports (4) → 1 — сводка по команде
```

Параметры отображения задач в `config.py`:

```python
TASKS_VIEW_MODE = "cards"  # или "table"
TASK_CARD_WIDTH = 64
ENABLE_COLORS = True
```

**Загрузка сида из shell** (альтернатива меню):

```bash
python -c "from pathlib import Path; import sqlite3; conn=sqlite3.connect('taskflow_team.db'); conn.executescript(Path('sql/seed.sql').read_text(encoding='utf-8')); conn.commit(); conn.close()"
```

### EN — scenario (current format)

```text
=== Main Menu ===
…
5 → confirm seed → Employees (1): 8 employees
Tasks (2) → task cards:
----------------------------------------------------------------
Task #13
Title: Optimize slow SQL query in dashboard
Deadline: 2026-04-21
Priority: high | Status: in_progress
Assignee: Dmitry Orlov
----------------------------------------------------------------
Filters (3) → option 4 — overdue tasks
Reports (4) → option 1 — team summary
```

**Shell seed** (alternative to the menu):

```bash
python -c "from pathlib import Path; import sqlite3; conn=sqlite3.connect('taskflow_team.db'); conn.executescript(Path('sql/seed.sql').read_text(encoding='utf-8')); conn.commit(); conn.close()"
```

---

<a id="s6"></a>

## 6. Структура проекта / Project structure

```text
taskflow_team/
├── main.py              # CLI, меню, вызов Database, очистка экрана
├── database.py          # SQL-слой, одно соединение на сессию
├── utils.py             # Ввод, валидация, таблицы + карточки задач + цвета
├── config.py            # Пути к БД/SQL + режим задач + ширина карточки + цвета
├── sql/
│   ├── schema.sql       # DDL (CREATE TABLE)
│   └── seed.sql         # Демо-данные
├── docs/
│   └── er_diagram.txt   # ER-модель (текст, нотация Мартина)
├── tests/               # unittest: database, utils, main
├── pyproject.toml       # requires-python, метаданные проекта
└── README.md            # Документация (этот файл)
```

---

<a id="s7"></a>

## 7. Схема базы данных / Database schema

| RU | EN |
|----|-----|
| Полная текстовая ER-диаграмма и пояснения связей — в файле [`docs/er_diagram.txt`](docs/er_diagram.txt). | Full textual ER diagram (Martin notation) — [`docs/er_diagram.txt`](docs/er_diagram.txt). |

### Кратко · Summary

| Таблица · Table | Поля · Columns | Связи · Relations |
|-----------------|----------------|-------------------|
| **`employees`** | `id`, ФИО, должность, уникальный `email`, опциональная `team` | 1 : N → `tasks` |
| **`tasks`** | `id`, `title`, `description`, `deadline` (TEXT `YYYY-MM-DD`), `priority`, `status`, `employee_id`, `created_at` | `employee_id` → `employees(id)` **ON DELETE CASCADE** |

---

<a id="s8"></a>

## 8. Известные проблемы / Known issues

| RU | EN |
|----|-----|
| Только **CLI**, без GUI. | **CLI** only; no GUI. |
| Email — упрощённый ASCII-шаблон; часть реальных адресов может не пройти. | Email validation is ASCII-oriented; some real addresses may be rejected. |
| Лимиты длины полей в **`utils.py`**, не в `CHECK` в SQLite. | Length limits enforced in **`utils.py`**, not SQLite `CHECK`. |
| `created_at` есть в БД, в текущем отображении задач не выводится (ни в таблицах, ни в карточках). | `created_at` exists in DB but is not currently printed in task table/card views. |
| «Просрочено» через SQLite `date('now')` (семантика дат SQLite). | “Overdue” uses SQLite `date('now')` (SQLite date semantics). |
| ANSI-цвета зависят от терминала; при отсутствии поддержки выводится обычный текст. | ANSI colors depend on terminal support; fallback is plain text output. |

---

<a id="s9"></a>

## 9. Тестирование / Testing

| Показатель · Metric | Значение · Value |
|---------------------|------------------|
| Фреймворк · Framework | `unittest` |
| Количество · Count | **12** тестов |

### Покрытие · Coverage

| Файл · File | Что проверяется · What is tested |
|-------------|----------------------------------|
| `tests/test_utils.py` | Валидация email (валид / невалид) |
| `tests/test_database.py` | CRUD сотрудник/задача; пустой `team_summary()`; фильтр по несуществующему сотруднику; подсчёт задач; **повторный** `load_seed()` без FK-ошибки |
| `tests/test_main.py` | Старт: `FileNotFoundError`, `sqlite3.Error`; `KeyboardInterrupt`; меню **5** при подтверждении и отказе |

### Команда · Command

```bash
python -m unittest discover -s tests -v
```

### Пример вывода · Sample output

```text
...
Ran 12 tests in 0.15s

OK
```

---

<a id="s10"></a>

## 10. Автор / Author

| Поле · Field | Значение · Value |
|--------------|------------------|
| **ФИО · Name** | Vyacheslav Panyuhin (Вячеслав Панюхин) |
| **Курс · Course** | 2 |
| **Группа · Group** | 11ФС |

---

<a id="demo"></a>

## Дополнительно: сценарий демо / Extra: demo scenario

| RU | EN |
|----|-----|
| 1) **Employees** — команда после сида. 2) **Tasks** — задачи спринта. 3) **Filters** — просроченные и приоритет. 4) **Reports** — сводки. 5) Смена статуса задачи и повтор отчёта. | 1) **Employees** — team after seed. 2) **Tasks** — sprint items. 3) **Filters** — overdue / priority. 4) **Reports** — summaries. 5) Change task status and refresh reports. |

