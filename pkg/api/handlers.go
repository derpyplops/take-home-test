package api

import (
	"context"
	"net/http"

	"github.com/jmoiron/sqlx"
	"github.com/tryhavana/take-home-test/pkg/classifications"
	"github.com/tryhavana/take-home-test/pkg/common"
	"github.com/tryhavana/take-home-test/pkg/db"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

type ListClassificationsForThreadResponse struct {
	Classifications []*common.Classification `json:"classifications"`
}

func ListClassificationsForThreadHandler(ctx context.Context, senv *svc.Env, r *http.Request) (*ListClassificationsForThreadResponse, error) {
	var ret []*common.Classification
	if err := db.WithTx(ctx, senv.DB, func(tx *sqlx.Tx) error {
		var err error
		ret, err = classifications.ListClassificationsForThread(ctx, senv, tx, r.URL.Query().Get("thread_id"))
		if err != nil {
			return err
		}
		return nil
	}); err != nil {
		return nil, err
	}
	return &ListClassificationsForThreadResponse{Classifications: ret}, nil
}
