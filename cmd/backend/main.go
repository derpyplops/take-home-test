package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"

	"github.com/spf13/viper"
	"github.com/tryhavana/take-home-test/pkg/api"
	"github.com/tryhavana/take-home-test/pkg/db"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

func main() {
	log.Println("Starting backend server...")
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	ctx, cancel := context.WithCancel(ctx)

	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.SetDefault("db", "")
	if err := viper.ReadInConfig(); err != nil {
		log.Fatal(err)
	}
	viper.SetEnvPrefix("havana")
	viper.AutomaticEnv()

	pgdb, err := db.New(ctx)
	if err != nil {
		log.Fatal(err)
	}
	senv := &svc.Env{
		DB: pgdb,
	}
	s := http.Server{
		Addr:    "localhost:8080",
		Handler: api.Router(senv),
	}
	srvErr := make(chan error, 1)
	go func() {
		srvErr <- s.ListenAndServe()
	}()
	select {
	case err := <-srvErr:
		log.Fatal(err)
	case <-ctx.Done():
		stop()
	}
	if err := s.Shutdown(ctx); err != nil {
		log.Fatal(err)
	}
	log.Println("Shutting down...")
	cancel()
}
