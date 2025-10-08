package main

import (
	"context"
	"database/sql"
	"log"
	"os"
	"os/signal"
	"time"

	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
	"github.com/sashabaranov/go-openai"
	"github.com/spf13/viper"
	"github.com/tryhavana/take-home-test/pkg/campaignthreads"
	"github.com/tryhavana/take-home-test/pkg/campaignthreads/generated"
	classificationGenerated "github.com/tryhavana/take-home-test/pkg/classifications/generated"
	"github.com/tryhavana/take-home-test/pkg/common"
	"github.com/tryhavana/take-home-test/pkg/db"
	"github.com/tryhavana/take-home-test/pkg/svc"
	"github.com/tryhavana/take-home-test/pkg/voiceclassifier"
)

func main() {
	log.Println("Starting voice classifier service...")
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	// Load configuration
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.SetDefault("db", "")
	if err := viper.ReadInConfig(); err != nil {
		log.Fatal(err)
	}
	viper.SetEnvPrefix("havana")
	viper.AutomaticEnv()

	// Initialize database
	pgdb, err := db.New(ctx)
	if err != nil {
		log.Fatal(err)
	}

	// Initialize OpenAI client
	openaiAPIKey := viper.GetString("openai_api_key")
	if openaiAPIKey == "" {
		log.Fatal("OpenAI API key not set. Set HAVANA_OPENAI_API_KEY environment variable")
	}
	openaiClient := openai.NewClient(openaiAPIKey)

	// Initialize service environment
	senv := &svc.Env{
		DB:           pgdb,
		OpenAIClient: openaiClient,
	}

	// Initialize voice classifier
	classifier := &voiceclassifier.Classifier{}

	// Start the periodic classification job
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	log.Println("Voice classifier service started. Checking for unclassified voice calls every 5 seconds...")

	for {
		select {
		case <-ctx.Done():
			log.Println("Shutting down voice classifier service...")
			return
		case <-ticker.C:
			if err := processUnclassifiedThreads(ctx, senv, classifier); err != nil {
				log.Printf("Error processing unclassified threads: %v", err)
			}
		}
	}
}

func processUnclassifiedThreads(ctx context.Context, senv *svc.Env, classifier voiceclassifier.ClassifierInterface) error {
	// Get campaign threads with voice_call_unclassified status
	campaignQueries := generated.New(senv.DB)
	unclassifiedThreads, err := campaignQueries.ListThreadsByStatus(ctx, string(common.CampaignThreadStatusVoiceCallUnclassified))
	if err != nil {
		return err
	}

	if len(unclassifiedThreads) == 0 {
		return nil
	}

	log.Printf("Found %d unclassified threads to process", len(unclassifiedThreads))

	classificationQueries := classificationGenerated.New(senv.DB)

	for _, thread := range unclassifiedThreads {
		if err := processThread(ctx, senv, classifier, classificationQueries, thread); err != nil {
			log.Printf("Error processing thread %s: %v", thread.ID, err)
		}
	}

	return nil
}

func processThread(ctx context.Context, senv *svc.Env, classifier voiceclassifier.ClassifierInterface, classificationQueries *classificationGenerated.Queries, thread generated.CampaignThread) error {
	// Get voice calls for this thread
	voiceCalls, err := classificationQueries.ListVoiceCallsForThread(ctx, thread.ID)
	if err != nil {
		return err
	}

	if len(voiceCalls) == 0 {
		log.Printf("No voice calls found for thread %s", thread.ID)
		return nil
	}

	log.Printf("Processing %d voice calls for thread %s", len(voiceCalls), thread.ID)

	// Process each voice call
	for _, voiceCall := range voiceCalls {
		if err := classifyVoiceCall(ctx, senv, classifier, classificationQueries, thread.ID, voiceCall); err != nil {
			log.Printf("Error classifying voice call %s: %v", voiceCall.ID, err)
			return err
		}
	}

	// Update campaign thread status to classified
	if err := db.WithTx(ctx, senv.DB, func(tx *sqlx.Tx) error {
		return campaignthreads.UpdateStatus(ctx, senv, tx, thread.ID, common.CampaignThreadStatusVoiceCallClassified)
	}); err != nil {
		return err
	}

	log.Printf("Successfully classified thread %s", thread.ID)
	return nil
}

func classifyVoiceCall(ctx context.Context, senv *svc.Env, classifier voiceclassifier.ClassifierInterface, classificationQueries *classificationGenerated.Queries, threadID string, voiceCall classificationGenerated.VoiceCall) error {
	// Prepare classification parameters
	params := voiceclassifier.ClassifyParams{
		Transcript: voiceCall.Transcript,
		Timezone:   voiceCall.TimeZone,
		CalledAt:   voiceCall.CalledAt.Time,
	}

	// Classify the voice call
	result, err := classifier.Classify(ctx, senv, params)
	if err != nil {
		return err
	}

	// Convert timestamps to sql.NullTime
	var interestedTime sql.NullTime
	if result.InterestedTime != nil {
		interestedTime = sql.NullTime{Time: *result.InterestedTime, Valid: true}
	}

	var callBackTime sql.NullTime
	if result.CallBackTime != nil {
		callBackTime = sql.NullTime{Time: *result.CallBackTime, Valid: true}
	}

	// Insert classification result
	classificationID := uuid.New().String()
	if err := classificationQueries.InsertClassification(ctx, classificationGenerated.InsertClassificationParams{
		ID:               classificationID,
		CampaignThreadID: threadID,
		Intent:           string(result.Intent),
		InterestedTime:   interestedTime,
		CallBackTime:     callBackTime,
	}); err != nil {
		return err
	}

	log.Printf("Successfully classified voice call %s with intent %s", voiceCall.ID, result.Intent)
	return nil
}
