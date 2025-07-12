package classifications

import (
	"context"

	"github.com/pkg/errors"
	"github.com/tryhavana/take-home-test/pkg/classifications/generated"
	"github.com/tryhavana/take-home-test/pkg/common"
	"github.com/tryhavana/take-home-test/pkg/db"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

func ListClassificationsForThread(ctx context.Context, senv *svc.Env, tx db.DBTX, threadID string) ([]*common.Classification, error) {
	q := generated.New(tx)
	rows, err := q.ListClassificationsForThread(ctx, threadID)
	if err != nil {
		return nil, errors.Wrap(err, "list classifications for thread")
	}
	ret := make([]*common.Classification, 0, len(rows))
	for _, row := range rows {
		ret = append(ret, &common.Classification{
			ID:               row.ID,
			CampaignThreadID: row.CampaignThreadID,
			CreatedAt:        row.CreatedAt,
			UpdatedAt:        row.UpdatedAt,
			InterestedTime:   db.FromNullTime(row.InterestedTime),
			CallBackTime:     db.FromNullTime(row.CallBackTime),
			Intent:           common.Intent(row.Intent),
		})
	}
	return ret, nil
}
