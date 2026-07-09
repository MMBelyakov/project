
CREATE SCHEMA IF NOT EXISTS marts;
DROP TABLE IF EXISTS marts.user_activity;

CREATE TABLE marts.user_activity AS
SELECT
    u.user_id                    AS user_id,
    u.name                  AS user_name,
    u.city                  AS city,
    COUNT(DISTINCT p.post_id)    AS posts_count,
    COUNT(DISTINCT c.comment_id)    AS comments_count
FROM core.dim_user u
LEFT JOIN core.fct_post p
    ON p.user_id = u.user_id
LEFT JOIN core.fct_comment c
    ON c.post_id = p.post_id 
GROUP BY
    u.user_id ,
    u.name,
    u.city
ORDER BY
    posts_count DESC;
