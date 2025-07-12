package campaignthreads

import (
	"context"

	"github.com/pkg/errors"
	"github.com/tryhavana/take-home-test/pkg/campaignthreads/generated"
	"github.com/tryhavana/take-home-test/pkg/common"
	"github.com/tryhavana/take-home-test/pkg/db"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

func UpdateStatus(ctx context.Context, senv *svc.Env, tx db.DBTX, campaignThreadID string, status common.CampaignThreadStatus) error {
	q := generated.New(tx)
	if err := q.UpdateStatus(ctx, generated.UpdateStatusParams{
		ID:     campaignThreadID,
		Status: string(status),
	}); err != nil {
		return errors.Wrap(err, "update status")
	}
	return nil
}
