package db

import (
	"database/sql"
	"time"
)

func FromNullTime(s sql.NullTime) *time.Time {
	if s.Valid {
		return &s.Time
	}
	return nil
}

func ToNullTime(t *time.Time) sql.NullTime {
	if t == nil {
		return sql.NullTime{}
	}
	return sql.NullTime{Time: *t, Valid: true}
}
