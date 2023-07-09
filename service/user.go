package service

import (
	"context"
	"time"
	"unifai/entity"
)

func (store *Datastore) CreateUser(u entity.User) (*entity.User, error) {
	req := `INSERT INTO users(username, passhash)
					VALUES($1, $2) RETURNING id, username, passhash`

	var res entity.User
	row := store.pool.QueryRow(context.Background(), req, u.Username, u.PasswordHashed)
	if err := row.Scan(&res.Id, &res.Username, &res.PasswordHashed); err != nil {
		return nil, err
	}

	return &res, nil
}

func (store *Datastore) GetUserById(id int) (*entity.User, error) {
	req := `SELECT id, username, last_update 
					FROM users WHERE id = $1`
	
	var u entity.User
	row := store.pool.QueryRow(context.Background(), req, id)
	if err := row.Scan(&u.Id, &u.Username, &u.AudioLastUpdated); err != nil{
		return nil, err
	}

	return &u, nil
}

func (store *Datastore) GetUserByName(username string) (*entity.User, error) {
	req := `SELECT id, username, last_update
					FROM users WHERE username = $1`
	
	var u entity.User
	row := store.pool.QueryRow(context.Background(), req, username)
	if err := row.Scan(&u.Id, &u.Username, &u.AudioLastUpdated); err != nil{
		return nil, err
	}

	return &u, nil
}

func (store *Datastore) SetUserAudio(id int, content []byte) (*entity.User, error) {
	req := `UPDATE users SET 
					audio = $2 last_update = $3 
					WHERE id = $1
					RETURNING id, username, last_update`
	row := store.pool.QueryRow(context.Background(), req, id, content, time.Now())

	var u entity.User
	if err := row.Scan(&u.Id, &u.Username, &u.AudioLastUpdated); err != nil {
		return nil, err
	}

	return &u, nil
}

func (store *Datastore) DeleteUser(id int) (*entity.User, error) {
	req := `DELETE FROM users WHERE id = $1
					RETURNING id, username, passhash, last_update`
	
	row := store.pool.QueryRow(context.Background(), req, id)

	var u entity.User
	if err := row.Scan(&u.Id, &u.Username, &u.PasswordHashed, &u.AudioLastUpdated); err != nil {
		return nil, err
	}
	return &u, nil
}
