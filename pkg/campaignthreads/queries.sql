-- name: UpdateStatus :exec
UPDATE campaign_threads
SET status = @status
WHERE id = @id;
