-- =============================================================================
-- Схема БД TaskFlow Team (SQLite).
-- Выполняется при старте приложения (executescript из database.initialize).
-- Стиль комментариев: короткие строки (~79 символов), пояснение назначения.
-- =============================================================================

-- Сотрудники: идентификатор, ФИО, должность, уникальный email, опциональная
-- команда. Связь 1:N с tasks (у одного сотрудника много задач).
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    team TEXT
);

-- Задачи: срок deadline хранится как TEXT в формате YYYY-MM-DD (проверка в UI).
-- priority и status ограничены CHECK; employee_id — FK с каскадным удалением.
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    deadline TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL CHECK (status IN ('new', 'in_progress', 'done')),
    employee_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
