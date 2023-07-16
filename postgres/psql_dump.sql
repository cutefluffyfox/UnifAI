CREATE TABLE IF NOT EXISTS "users" (
	"id" serial PRIMARY KEY, 
	"username" varchar UNIQUE,
	"passhash" varchar,
	"audio" bytea,
	"last_update" timestamp)

CREATE TABLE IF NOT EXISTS "rooms" (
	"id" serial PRIMARY KEY,
	"admin_id" integer references users(id),
	"name" varchar,
	"description" varchar)

CREATE TABLE IF NOT EXISTS "rooms_users" (
	"user_id" integer references users(id),
	"room_id" integer references rooms(id))
