package common

import "time"

type CampaignThread struct {
	ID        string    `json:"id"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
	Status    string    `json:"status"`
}

type CampaignThreadStatus string

const (
	CampaignThreadStatusNotStarted            CampaignThreadStatus = "not_started"
	CampaignThreadStatusVoiceCallUnclassified CampaignThreadStatus = "voice_call_unclassified"
	CampaignThreadStatusVoiceCallClassified   CampaignThreadStatus = "voice_call_classified"
)
