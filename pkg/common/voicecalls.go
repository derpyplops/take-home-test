package common

import "time"

type VoiceCall struct {
	ID               string     `json:"id"`
	CampaignThreadID string     `json:"campaignThreadID"`
	CreatedAt        time.Time  `json:"createdAt"`
	CalledAt         *time.Time `json:"calledAt"`
	Transcript       string     `json:"transcript"`
	TimeZone         string     `json:"timeZone"`
}

type VoiceCallStatus string

const (
	VoiceCallStatusQueued     VoiceCallStatus = "queued"
	VoiceCallStatusInProgress VoiceCallStatus = "in_progress"
	VoiceCallStatusCompleted  VoiceCallStatus = "completed"
	VoiceCallStatusFailed     VoiceCallStatus = "failed"
)
