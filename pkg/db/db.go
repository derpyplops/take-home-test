package db

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
	pgxstdlib "github.com/jackc/pgx/v5/stdlib"
	"github.com/jmoiron/sqlx"
	"github.com/pkg/errors"
	"github.com/spf13/viper"
)

type DBTX interface {
	ExecContext(context.Context, string, ...interface{}) (sql.Result, error)
	PrepareContext(context.Context, string) (*sql.Stmt, error)
	QueryContext(context.Context, string, ...interface{}) (*sql.Rows, error)
	QueryRowContext(context.Context, string, ...interface{}) *sql.Row
	PrepareNamedContext(context.Context, string) (*sqlx.NamedStmt, error)

	QueryxContext(context.Context, string, ...interface{}) (*sqlx.Rows, error)
	QueryRowxContext(context.Context, string, ...interface{}) *sqlx.Row
}

var _ DBTX = (*sqlx.DB)(nil)
var _ DBTX = (*sqlx.Tx)(nil)

func New(ctx context.Context) (*sqlx.DB, error) {
	dbStr := viper.GetString("db")

	if dbStr == "" {
		return nil, errors.New("no valid db string")
	}

	poolConfig, err := pgxpool.ParseConfig(dbStr)
	if err != nil {
		return nil, err
	}

	connPool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		return nil, errors.Wrap(err, "connect")
	}

	nativeDB := pgxstdlib.OpenDBFromPool(connPool)
	return sqlx.NewDb(nativeDB, "pgx"), nil
}

func WithTx(ctx context.Context, db DBTX, f func(tx *sqlx.Tx) error) error {
	if txx, ok := db.(*sqlx.Tx); ok {
		return f(txx)
	}
	dbb, ok := db.(*sqlx.DB)
	if !ok {
		return errors.New("db is not a *sqlx.DB")
	}
	tx, err := dbb.Beginx()
	if err != nil {
		return err
	}
	defer func() {
		if err := tx.Rollback(); err != nil {
			if errors.Is(err, sql.ErrTxDone) {
				return
			}
			fmt.Printf("rollback error: %v\n", err)
		}
	}()
	if err := f(tx); err != nil {
		return err
	}
	return tx.Commit()
}
