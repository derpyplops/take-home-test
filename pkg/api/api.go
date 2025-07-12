package api

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/tryhavana/take-home-test/pkg/svc"
)

func Router(senv *svc.Env) http.Handler {
	r := mux.NewRouter()

	HandleWithResponse(senv, r, "/classifications/{thread_id}", ListClassificationsForThreadHandler).Methods("GET")
	return r
}

func Handle(senv *svc.Env, router *mux.Router, route string, f func(context.Context, *svc.Env, http.ResponseWriter, *http.Request) error) *mux.Route {
	return router.HandleFunc(route, func(w http.ResponseWriter, r *http.Request) {
		if err := f(r.Context(), senv, w, r); err != nil {
			http.Error(w, err.Error(), 500)
		}
	})
}

func HandleWithResponse[ResponseType any](senv *svc.Env, r *mux.Router, route string, f func(context.Context, *svc.Env, *http.Request) (ResponseType, error)) *mux.Route {
	return Handle(senv, r, route, func(ctx context.Context, senv *svc.Env, w http.ResponseWriter, r *http.Request) error {
		res, err := f(ctx, senv, r)
		if err != nil {
			return err
		}
		return json.NewEncoder(w).Encode(res)
	})
}
