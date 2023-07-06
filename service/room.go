package service

import (
	"context"
	"errors"
	"unifai/config"
	"unifai/entity"
)

// type RoomService interface {
// 	NewRoom(entity.Room) error
// 	DeleteRoom(int) error
// 	FindRoomById(int) (entity.Room, error)
//
// 	JoinRoom(int, int) error
// 	LeaveRoom(int, int) error
// }
//
// type roomService struct{}
//
// func NewRoomService(c *pgx.Conn) RoomService {
// 	config.CreateRoomsTable(c)
// 	config.CreateRoomsUsersRelation(c)
// 	return roomService{}
// }

func DeleteRoom(roomId int, userId int) error {
	room, err := FindRoomById(roomId)
	if err != nil {
		return err
	}

	if userId != room.AdminId {
		return errors.New("Only admin can delete a rooms")
	}

	req := "delete from rooms_users where room_id = $1; delete from rooms where id = $1"
	conn := config.Connect()
	_, err = conn.Exec(context.Background(), req, roomId)
	return err
}

func FindRoomById(roomId int) (entity.Room, error) {
	req := "select * from rooms where id = $1"
	conn := config.Connect()

	var r entity.Room
	if err := conn.QueryRow(context.Background(), req, roomId).Scan(&r); err != nil {
		return entity.Room{}, err
	}
	return r, nil
}

func GetParticipants(roomId int) ([]int, error) {
	req := "select user_id from rooms_users where room_id = $1"
	conn := config.Connect()

	rows, err := conn.Query(context.Background(), req, roomId)
	if err != nil {
		return nil, err
	}

	var ids []int
	for rows.Next() {
		var id int
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}

	return ids, nil
}

func JoinRoom(roomId int, userId int) error {
	req := "insert into rooms_users(user_id, room_id) values($1, $2)"
	conn := config.Connect()

	_, err := conn.Exec(context.Background(), req, userId, roomId)
	return err
}

func ListRooms(userId int) ([]entity.Room, error) {
	req := "select distinct room_id, admin_id, name, description from rooms_users ru join rooms r on ru.room_id = r.id where ru.user_id = $1"
	conn := config.Connect()

	rows, err := conn.Query(context.Background(), req, userId)
	if err != nil {
		return nil, err
	}
	var rooms []entity.Room
	for rows.Next() {
		var r entity.Room
		err := rows.Scan(&r)
		if err != nil {
			return nil, err
		}
		rooms = append(rooms, r)
	}

	return rooms, nil
}

func LeaveRoom(roomId int, userId int) error {
	room, err := FindRoomById(roomId)
	if err != nil {
		return err
	}

	if userId == room.AdminId {
		return errors.New("Admin cannot leave a room without deleting it")
	}

	req := "delete from rooms_users where room_id = $1, user_id = $2"
	conn := config.Connect()

	_, err = conn.Exec(context.Background(), req, userId, roomId)
	return err
}

func NewRoom(room entity.Room) (int, error) {
	req := "insert into rooms(name, description, admin_id) values($1, $2, $3) returning id"
	conn := config.Connect()

	var id int
	if err := conn.QueryRow(context.Background(), req, room.Name, room.Description, room.AdminId).Scan(&id); err != nil {
		return -1, err
	}

	return id, nil
}

