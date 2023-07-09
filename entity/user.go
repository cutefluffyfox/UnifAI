package entity

import "time"

type User struct {
	Id int `json:"id"`
	Username       string `json:"username"`
	PasswordHashed string `json:"password_hash,omitempty"`
	AudioLastUpdated time.Time `json:"audio_last_updated"`
}

type UserDetails struct {
	Username    string `json:"username" binding:"required"`
	PasswordRaw string `json:"password" binding:"required"`
}
