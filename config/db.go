package config 

import (
  "fmt"
  "context"
  "os"
  "github.com/jackc/pgx/v5"
)

const MAX_AUDIO_SIZE = 2 << 20 // 2 MiB


func Connect() *pgx.Conn {
  conn, err := pgx.Connect(context.Background(), os.Getenv("DB_URL"))
  if err != nil {
    fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
    os.Exit(1)
  }
  fmt.Println("Connected to DB")
  return conn
}

func Migrate(c *pgx.Conn) {
	CreateUserTable(c)
	CreateRoomsTable(c)
	CreateRoomsUsersRelation(c)
}

func CreateUserTable(c *pgx.Conn) {
  req := `drop table if exists "users" cascade;
	CREATE TABLE IF NOT EXISTS "users" (
		"id" serial PRIMARY KEY, 
		"username" varchar UNIQUE,
		"passhash" varchar,
		"audio" bytea,
		"last_update" timestamp)`

  if _, err := c.Exec(context.Background(), req); err != nil {
    fmt.Fprintf(os.Stderr, "Could not create users table: %v\n", err)
    os.Exit(1)
  }

  fmt.Println("Created users table")
}

func CreateRoomsTable(c *pgx.Conn) {
	req := `drop table if exists "rooms" cascade; 
		CREATE TABLE IF NOT EXISTS "rooms" (
			"id" serial PRIMARY KEY,
			"admin_id" integer references users(id),
			"name" varchar,
			"description" varchar)`

  if _, err := c.Exec(context.Background(), req); err != nil {
    fmt.Fprintf(os.Stderr, "Could not create rooms table: %v\n", err)
    os.Exit(1)
  }

  fmt.Println("Created rooms table")
}

func CreateRoomsUsersRelation(c *pgx.Conn) {
	req := `drop table if exists "rooms_users";
		CREATE TABLE IF NOT EXISTS "rooms_users" (
		"user_id" integer references users(id),
		"room_id" integer references rooms(id))`

  if _, err := c.Exec(context.Background(), req); err != nil {
    fmt.Fprintf(os.Stderr, "Could not create rooms-users table: %v\n", err)
    os.Exit(1)
  }

  fmt.Println("Created rooms-users table")
}
