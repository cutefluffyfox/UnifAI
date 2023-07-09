package service

import (
	"context"
	"errors"
	"unifai/entity"
)


func (store *Datastore) CreateRoom(room entity.Room) (*entity.Room, error) {
	req := `INSERT INTO rooms(name, description, admin_id)
					VALUES ($1, $2, $3) RETURNING id, name, description, admin_id`
	
	row := store.pool.QueryRow(context.Background(), req, room.Name, room.Description, room.AdminId)

	var r entity.Room
	if err := row.Scan(&r.Id, &r.Name, &r.Description, &r.AdminId); err != nil {
		return nil, err
	}

	return &r, nil
}

func (store *Datastore) GetRoom(id int) (*entity.Room, error) {
	req := `SELECT id, name, description, admin_id
					FROM rooms WHERE id = $1`
	
	row := store.pool.QueryRow(context.Background(), req, id)

	var r entity.Room
	if err := row.Scan(&r.Id, &r.Name, &r.Description, &r.AdminId); err != nil {
		return nil, err
	}

	return &r, nil
}

func (store *Datastore) GetRoomParticipants(roomId int) ([]entity.User, error) {
	req := `SELECT u.id, u.username, u.last_update
					FROM rooms_users ru JOIN users u ON ru.user_id = u.id
					WHERE ru.room_id = $1`

	rows, err := store.pool.Query(context.Background(), req, roomId)
	if err != nil {
		return nil, err
	}

	var users []entity.User
	for rows.Next() {
		var u entity.User
		if err := rows.Scan(&u.Id, &u.Username, &u.AudioLastUpdated); err != nil {
			return nil, err
		}
		users = append(users, u)
	}

	return users, nil
}

func (store *Datastore) GetUserRooms(userId int) ([]entity.Room, error) {
	req := `SELECT DISTINCT r.id, r.name, r.description, r.admin_id 
					FROM rooms_users ru 
						JOIN rooms r ON ru.room_id = r.id
					WHERE ru.user_id = $1`
	rows, err := store.pool.Query(context.Background(), req, userId)
	if err != nil {
		return nil, err
	}

	var rooms []entity.Room
	for rows.Next() {
		var r entity.Room
		err := rows.Scan(&r.Id, &r.Name, &r.Description, &r.AdminId)
		if err != nil {
			return nil, err
		}
		rooms = append(rooms, r)
	}

	return rooms, nil
}

func (store *Datastore) UpdateRoom(r entity.Room) (*entity.Room, error) {
	req := `UPDATE rooms SET 
						name = $2
						description = $3
						admin_id = $4
					WHERE id = $1 RETURNING id, name, description, admin_id`
	
	row := store.pool.QueryRow(context.Background(), req, r.Id, r.Name, r.Description, r.AdminId)
	var room entity.Room
	if err := row.Scan(&room.Id, &room.Name, &room.Description, &room.AdminId); err != nil {
		return nil, err
	}
	return &room, nil
}

func (store *Datastore) UpdateRoomJoin(roomId int, userId int) error {
	req := `INSERT INTO rooms_users(room_id, user_id) 
					VALUES($1, $2)`
	
	_, err := store.pool.Exec(context.Background(), req, roomId, userId)
	return err
}

func (store *Datastore) UpdateRoomLeave(roomId int, userId int) error {
	room, err := store.GetRoom(roomId)
	if err != nil {
		return err
	}
	if room.AdminId == userId {
		return errors.New("Admin cannot leave a room, only delete it.")
	}

	req := `DELETE FROM rooms_users where room_id = $1, user_id = $2`
	_, err = store.pool.Exec(context.Background(), req, roomId, userId)
	return err
}

func (store *Datastore) DeleteRoom(roomId int) (*entity.Room, error) {
	req := `DELETE FROM rooms_users WHERE room_id = $1;
					DELETE FROM roooms WHERE id = $1
					RETURNING id, name, description, admin_id`

	row := store.pool.QueryRow(context.Background(), req, roomId)
	var r entity.Room
	if err := row.Scan(&r.Id, &r.Name, &r.Description, &r.AdminId); err != nil {
		return nil, err
	}

	return &r, nil
}

