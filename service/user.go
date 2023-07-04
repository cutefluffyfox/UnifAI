package service

import (
	"context"
	"fmt"
	"unifai/config"
	"unifai/entity"
)

// type UserService interface {
// 	Register(user entity.User) (int, error)
// 	FindUserById(id int) (entity.User, error)
// 	FindUserByUsername(username string) (entity.User, error)
//
// 	SaveAudioFile(userId int, content []byte, n int) error
// 	GetAudioFile(userId int) ([]byte, error)
// }
// type userService struct{}
//
//
// func NewUserService() UserService {
// 	return &userService{}
// }

// FindUserById implements UserService.
func FindUserById(id int) (entity.User, error) {
	req := "select id, username, passhash from users where \"id\" = $1"
	conn := config.Connect() 

	var u entity.User
	if err := conn.QueryRow(context.Background(), req, id).Scan(&u.Id, &u.Username, &u.PasswordHashed); err != nil {
		return entity.User{}, err
	}
	return u, nil
}

// FindUserByUsername implements UserService.
func FindUserByUsername(username string) (entity.User, error) {
	req := "select is, username, passhash from users where \"username\" = $1"
	conn := config.Connect() 

	var u entity.User
	if err := conn.QueryRow(context.Background(), req, username).Scan(&u.Id, &u.Username, &u.PasswordHashed); err != nil {
		return entity.User{}, err
	}
	return u, nil
}

// SaveAudioFile implements UserService.
func SaveAudioFile(userId int, content []byte, n int) error {
	req := "update users set audio = $1 where id = $2"
	conn := config.Connect()

	tag, err := conn.Exec(context.Background(), req, content, userId)
	fmt.Printf("Setting audio for user %d: %s\n", userId, tag.String())
	return err
}

// GetAudioFile implements UserService.
func GetAudioFile(userId int) ([]byte, error) {
	req := "select audio from users where \"id\" = $1"
	conn := config.Connect() 

	content := make([]byte, config.MAX_AUDIO_SIZE)
	if err := conn.QueryRow(context.Background(), req, userId).Scan(&content); err != nil {
		return nil, err
	}
	return content, nil
}

func RegisterUser(user entity.User) (int, error) {
	req := "insert into users(username, passhash) values($1, $2) returning \"id\""
	conn := config.Connect()
	var id int
	if err := conn.QueryRow(context.Background(), req, user.Username, user.PasswordHashed).Scan(&id); err != nil {
		return -1, err
	}

	return id, nil
}



type UsernameTaken struct {}

func (err *UsernameTaken) Error() string {
	return "Username taken"
}
