package entity

type User struct {
	Id int `json:"id"`
	Username       string `json:"username" binding:"required"`
	PasswordHashed string `json:"passhash" binding:"required"`
}

type UserDetails struct {
	Username    string `json:"username" binding:"required"`
	PasswordRaw string `json:"password" binding:"required"`
}
