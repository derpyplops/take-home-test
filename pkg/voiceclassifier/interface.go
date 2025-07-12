package voiceclassifier

import (
	"context"
	"time"

	"github.com/tryhavana/take-home-test/pkg/common"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

type ClassifyParams struct {
	Transcript string
	Timezone   string
	CalledAt   time.Time
}

type ClassifyResponse struct {
	Intent         common.Intent `json:"intent"`
	InterestedTime *time.Time    `json:"interestedTime"`
	CallBackTime   *time.Time    `json:"callBackTime"`
}

type ClassifierInterface interface {
	Classify(ctx context.Context, senv *svc.Env, params ClassifyParams) (*ClassifyResponse, error)
}
