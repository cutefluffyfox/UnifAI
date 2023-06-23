package service

import (
	"unifai/config"
	"unifai/entity"
	"github.com/jackc/pgx/v5"
)

type UserService interface {
	Save(user entity.User) (entity.User, error)
	FindUserById(id int) (entity.User, error)

	SaveAudioFile(userId int, content []byte) (bool, error)
	GetAudioFile(userId int) ([]byte, error)
}
type userService struct{}

func NewUserService(c *pgx.Conn) UserService {
	config.CreateUserTable(c)
	return &userService{}
}

// FindUserById implements UserService.
func (*userService) FindUserById(id int) (entity.User, error) {
	panic("unimplemented")
}

// GetAudioFile implements UserService.
func (*userService) GetAudioFile(userId int) ([]byte, error) {
	panic("unimplemented")
}

// Save implements UserService.
func (*userService) Save(user entity.User) (entity.User, error) {
	panic("unimplemented")
}

// SaveAudioFile implements UserService.
func (*userService) SaveAudioFile(userId int, content []byte) (bool, error) {
	panic("unimplemented")
}

