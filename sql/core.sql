CREATE SCHEMA IF NOT EXISTS core;

-- Пользователи
CREATE TABLE IF NOT EXISTS core.dim_user (
    user_id int PRIMARY KEY,
    name    text,
    city    text
);

TRUNCATE core.dim_user;

INSERT INTO core.dim_user
SELECT DISTINCT ON (raw->>'id')
    (raw->>'id')::int,
    raw->>'name',
    raw->'address'->>'city'
FROM staging.users
ORDER BY raw->>'id', _loaded_at DESC;

-- Посты
CREATE TABLE IF NOT EXISTS core.fct_post (
    post_id int PRIMARY KEY,
    user_id int,
    title   text
);

TRUNCATE core.fct_post;

INSERT INTO core.fct_post
SELECT DISTINCT ON (raw->>'id')
    (raw->>'id')::int,
    (raw->>'userId')::int,
    raw->>'title'
FROM staging.posts
ORDER BY raw->>'id', _loaded_at DESC;

-- Комментарии
CREATE TABLE IF NOT EXISTS core.fct_comment (
    comment_id int PRIMARY KEY,
    post_id    int,
    email      text
);

TRUNCATE core.fct_comment;

INSERT INTO core.fct_comment
SELECT DISTINCT ON (raw->>'id')
    (raw->>'id')::int,
    (raw->>'postId')::int,
    lower(raw->>'email')
FROM staging.comments
ORDER BY raw->>'id', _loaded_at DESC;