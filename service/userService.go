package service

import (
	"context"
	"unifai/config"
	"unifai/entity"

	"github.com/jackc/pgx/v5"
)

type UserService interface {
	Register(user entity.User) (int, error)
	FindUserById(id int) (entity.User, error)
	FindUserByUsername(username string) (entity.User, error)

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
	req := "select * from users where \"id\" = $1"
	conn := config.Connect() 

	var u entity.User
	if err := conn.QueryRow(context.Background(), req, id).Scan(&u.Id, &u.Username, &u.PasswordHashed); err != nil {
		return entity.User{}, err
	}
	return u, nil
}

// FindUserByUsername implements UserService.
func (*userService) FindUserByUsername(username string) (entity.User, error) {
	req := "select * from users where \"username\" = $1"
	conn := config.Connect() 

	var u entity.User
	if err := conn.QueryRow(context.Background(), req, username).Scan(&u.Id, &u.Username, &u.PasswordHashed); err != nil {
		return entity.User{}, err
	}
	return u, nil
}

// GetAudioFile implements UserService.
func (service *userService) GetAudioFile(userId int) ([]byte, error) {
	panic("unimplemented")
}

func (service *userService) Register(user entity.User) (int, error) {
	req := "insert into users(username, passhash) values($1, $2) returning \"id\""
	conn := config.Connect()
	var id int
	if err := conn.QueryRow(context.Background(), req, user.Username, user.PasswordHashed).Scan(&id); err != nil {
		return -1, err
	}

	return id, nil
}


// SaveAudioFile implements UserService.
func (service *userService) SaveAudioFile(userId int, content []byte) (bool, error) {
	panic("unimplemented")
}

type UsernameTaken struct {}

func (err *UsernameTaken) Error() string {
	return "Username taken"
}
