-- name: ListClassificationsForThread :many
SELECT *
FROM classifications
WHERE campaign_thread_id = $1;

-- name: ListVoiceCallsForThread :many
SELECT * FROM voice_calls
WHERE campaign_thread_id = $1;

-- name: InsertClassification :exec
INSERT INTO classifications (id, campaign_thread_id, intent, interested_time, call_back_time)
VALUES ($1, $2, $3, $4, $5);
