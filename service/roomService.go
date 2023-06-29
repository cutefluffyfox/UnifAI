package service

import (
	"unifai/config"
	"unifai/entity"

	"github.com/jackc/pgx/v5"
)

type RoomService interface {
	NewRoom(entity.Room) (bool, error)
	DeleteRoom(int) (bool, error)
	FindRoomById(int) (entity.Room, error)

	JoinRoom(int, int) (bool, error)
	LeaveRoom(int, int) (bool, error)
}

type roomService struct{}

func NewRoomService(c *pgx.Conn) RoomService {
	config.CreateRoomsTable(c)
	config.CreateRoomsUsersRelation(c)
	return roomService{}
}

// DeleteRoom implements RoomService.
func (roomService) DeleteRoom(int) (bool, error) {
	panic("unimplemented")
}

// FindRoomById implements RoomService.
func (roomService) FindRoomById(int) (entity.Room, error) {
	panic("unimplemented")
}

// JoinRoom implements RoomService.
func (roomService) JoinRoom(int, int) (bool, error) {
	panic("unimplemented")
}

// LeaveRoom implements RoomService.
func (roomService) LeaveRoom(int, int) (bool, error) {
	panic("unimplemented")
}

// NewRoom implements RoomService.
func (roomService) NewRoom(entity.Room) (bool, error) {
	panic("unimplemented")
}

