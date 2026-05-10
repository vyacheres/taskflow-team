-- =============================================================================
-- Демонстрационные данные TaskFlow Team (SQLite).
-- Сначала очистка таблиц и сброс AUTOINCREMENT, затем INSERT с фиксированными
-- связями employee_id (1..8). Повторный запуск безопасен после правок схемы.
-- =============================================================================

-- Порядок важен при включённых FK: сначала задачи, затем сотрудники.
DELETE FROM tasks;
DELETE FROM employees;

-- Сброс счётчика id, иначе повторная загрузка даст id 9+ при старых ссылках в
-- INSERT задач и нарушится внешний ключ.
DELETE FROM sqlite_sequence WHERE name IN ('employees', 'tasks');

-- Восемь сотрудников: тимлид, бэкенд, фронтенд, QA, DevOps, продакт.
-- id присваиваются по порядку вставки: 1..8.
INSERT INTO employees (full_name, position, email, team) VALUES
('Ivan Petrov', 'Team Lead', 'ivan.petrov@novasoft.local', 'Core Platform'),
('Alina Sokolova', 'Backend Developer', 'alina.sokolova@novasoft.local', 'Core Platform'),
('Dmitry Orlov', 'Backend Developer', 'dmitry.orlov@novasoft.local', 'Core Platform'),
('Nikita Frolov', 'Frontend Developer', 'nikita.frolov@novasoft.local', 'Web Apps'),
('Elena Volkova', 'QA Engineer', 'elena.volkova@novasoft.local', 'Quality Assurance'),
('Maria Smirnova', 'QA Engineer', 'maria.smirnova@novasoft.local', 'Quality Assurance'),
('Sergey Kozlov', 'DevOps Engineer', 'sergey.kozlov@novasoft.local', 'Infrastructure'),
('Anna Belova', 'Product Manager', 'anna.belova@novasoft.local', 'Product');

-- Шестнадцать задач спринта; employee_id ссылается на строки employees выше.
INSERT INTO tasks (title, description, deadline, priority, status, employee_id) VALUES
('Release 1.8 sprint planning', 'Prepare sprint backlog, validate estimates with tech lead, and align release goals with product priorities.', '2026-04-24', 'high', 'done', 8),
('Implement role-based permissions', 'Add RBAC checks for admin and manager roles in API endpoints and service layer.', '2026-04-30', 'high', 'in_progress', 2),
('Refactor notification module', 'Split notification service into channels and add retry policy for failed deliveries.', '2026-05-04', 'medium', 'in_progress', 3),
('Fix duplicate invoice webhook processing', 'Prevent duplicate transaction handling in payment callback consumer.', '2026-04-22', 'high', 'new', 2),
('Add API health endpoint', 'Implement /health and /ready endpoints for infrastructure monitoring.', '2026-04-25', 'medium', 'done', 3),
('Update user profile page UI', 'Redesign profile layout according to approved design system components.', '2026-05-06', 'medium', 'in_progress', 4),
('Add frontend error boundary', 'Handle unexpected UI crashes and show fallback screen with error reference ID.', '2026-04-27', 'high', 'new', 4),
('Regression test for release candidate', 'Run full regression checklist for auth, billing, and notifications.', '2026-04-29', 'high', 'in_progress', 5),
('Prepare smoke tests for staging', 'Create quick smoke set for critical business flows before deployment.', '2026-04-23', 'medium', 'done', 6),
('Automate nightly DB backup', 'Configure scheduled backup with retention policy and restore verification.', '2026-04-26', 'high', 'in_progress', 7),
('Add deployment rollback script', 'Implement one-command rollback for previous stable build in production.', '2026-04-24', 'high', 'new', 7),
('Customer onboarding analytics report', 'Build weekly report on activation funnel and retention for new clients.', '2026-05-02', 'low', 'new', 8),
('Optimize slow SQL query in dashboard', 'Investigate and optimize endpoint query causing latency over 2 seconds.', '2026-04-21', 'high', 'in_progress', 3),
('Create test data factory', 'Implement reusable test fixtures for API integration tests.', '2026-05-01', 'medium', 'new', 5),
('Security checklist before release', 'Review OWASP basics, secret handling, and audit log completeness.', '2026-04-28', 'high', 'done', 1),
('Run team retrospective notes', 'Collect sprint blockers and improvements, then document agreed actions.', '2026-04-25', 'low', 'done', 1);
