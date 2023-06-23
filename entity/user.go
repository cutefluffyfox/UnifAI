package entity

type User struct {
	Id             int    `json:"id"`
	email          string `json:"email"`
	Username       string `json:"username"`
	PasswordHashed string `json:"passhash"`
}
