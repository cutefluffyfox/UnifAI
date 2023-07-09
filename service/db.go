package service

import (
	"context"
	"errors"
	"log"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)


type Datastore struct {
	pool *pgxpool.Pool
}

func NewDatastore(pool *pgxpool.Pool) (Datastore) {
	return Datastore{pool}
}

func NewDBPool() (*pgxpool.Pool, error){
	pool, err := pgxpool.New(context.Background(), os.Getenv("DB_URL"))
	if err != nil {
		return nil, err
	}

	err = CheckPool(pool)
	if err != nil {
		return nil, err
	}

	return pool, nil
}

func CheckPool(pool *pgxpool.Pool) error {
	err := pool.Ping(context.Background())
	if err != nil {
		return errors.New("DB connection error")
	}

	var (
		version string 
		user string 
		dbName string
	)

	req := `select current_database(), current_user, version();`
	row := pool.QueryRow(context.Background(), req)
	err = row.Scan(&dbName, &user, &version)
	if err != nil {
		return err
	}

	log.Printf("database version: %s\n", version)
	log.Printf("database user: %s\n", user)
	log.Printf("database name: %s\n", dbName)

	return nil
}
