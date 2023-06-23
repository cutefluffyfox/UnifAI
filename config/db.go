package config 

import (
  "fmt"
  "context"
  "os"
  "github.com/jackc/pgx/v5"
)

func Connect() *pgx.Conn {
  conn, err := pgx.Connect(context.Background(), os.Getenv("DB_URL"))
  if err != nil {
    fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
    os.Exit(1)
  }
  fmt.Println("Connected to DB")
  return conn
}

func CreateUserTable(c *pgx.Conn) {
  req := `CREATE TABLE IF NOT EXISTS "users" (
  "id" serial PRIMARY KEY, 
  "email" varchar,
  "username" varchar,
  "passhash" bytea )`

  if _, err := c.Exec(context.Background(), req); err != nil {
    fmt.Fprintf(os.Stderr, "Could not create users table: %v\n", err)
    os.Exit(1)
  }

  fmt.Println("Created users table")
}
