package service

import (
	"unifai/config"
	"unifai/entity"

	"github.com/jackc/pgx/v5"
)

type RoomService interface {
	NewRoom(entity.Room) error
	DeleteRoom(int) error
	FindRoomById(int) (entity.Room, error)

	JoinRoom(int, int) error
	LeaveRoom(int, int) error
}

type roomService struct{}

func NewRoomService(c *pgx.Conn) RoomService {
	config.CreateRoomsTable(c)
	config.CreateRoomsUsersRelation(c)
	return roomService{}
}

// DeleteRoom implements RoomService.
func (roomService) DeleteRoom(roomId int) error {
	panic("unimplemented")
}

// FindRoomById implements RoomService.
func (roomService) FindRoomById(roomId int) (entity.Room, error) {
	panic("unimplemented")
}

// JoinRoom implements RoomService.
func (roomService) JoinRoom(roomId int, userId int) error {
	panic("unimplemented")
}

// LeaveRoom implements RoomService.
func (roomService) LeaveRoom(roomId int, userId int) error {
	panic("unimplemented")
}

// NewRoom implements RoomService.
func (roomService) NewRoom(room entity.Room) error {
	panic("unimplemented")
}

