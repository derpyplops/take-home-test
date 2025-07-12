package svc

import (
	"github.com/sashabaranov/go-openai"
	"github.com/tryhavana/take-home-test/pkg/db"
)

type Env struct {
	OpenAIClient *openai.Client
	DB           db.DBTX
}
