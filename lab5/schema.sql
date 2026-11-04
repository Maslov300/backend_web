-- Запускать в БД matvey_mavrin_knowledge_base под её владельцем.
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(30) UNIQUE NOT NULL,
    password VARCHAR(162) NOT NULL,
    name VARCHAR(100) NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    login_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(50),
    article_text TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    likes INTEGER DEFAULT 0
);
-- Для совместимости с ранней версией таблицы пользователей:
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(100) NOT NULL DEFAULT '';
