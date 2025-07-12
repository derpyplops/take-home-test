-- name: ListClassificationsForThread :many
SELECT *
FROM classifications
WHERE campaign_thread_id = $1;
