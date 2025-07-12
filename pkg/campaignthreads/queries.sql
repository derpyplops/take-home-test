-- name: UpdateStatus :exec
UPDATE campaign_threads
SET status = @status
WHERE id = @id;

-- name: ListThreadsByStatus :many
SELECT * FROM campaign_threads
WHERE status = @status;
