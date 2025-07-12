package common

import "time"

type Intent string

const (
	IntentVoiceInterested               Intent = "voice_interested"
	IntentVoiceNotInterested            Intent = "voice_not_interested"
	IntentVoiceImmediateHangup          Intent = "voice_immediate_hangup"
	IntentVoiceWrongNumber              Intent = "voice_wrong_number"
	IntentVoiceNoAction                 Intent = "voice_no_action"
	IntentVoiceWantsCallBack            Intent = "voice_wants_call_back"
	IntentVoiceWantsEmailFollowUp       Intent = "voice_wants_email_follow_up"
	IntentVoiceWantsWhatsappSMSFollowUp Intent = "voice_wants_whatsapp_sms_follow_up"
	IntentVoiceVoiceMail                Intent = "voice_voice_mail"
	IntentVoiceUnknown                  Intent = "voice_unknown"
)

type Classification struct {
	ID               string     `json:"id"`
	CampaignThreadID string     `json:"campaignThreadID"`
	CreatedAt        time.Time  `json:"createdAt"`
	UpdatedAt        time.Time  `json:"updatedAt"`
	InterestedTime   *time.Time `json:"interestedTime"`
	CallBackTime     *time.Time `json:"callBackTime"`
	Intent           Intent     `json:"intent"`
}
