package ws

import (
	"time"

	"golang.org/x/text/language"
)

type ChatMessage struct {
	UserId int 
	RoomId int
	Lang language.Tag 
	Body string
}

type MessageIn struct {
	MessageType string `json:"action"`
	Body string `json:"text"` 
	Language string `json:"lang"` // ISO 639-1
}

type MessageOut struct {
	MessageType string `json:"type"`
	SenderId int `json:"sender_id"`
	Body string `json:"text"`
}

type MessageError struct {
	MessageType string `json:"type"`
	ErrorType string `json:"error_type"`
	Err error `json:"error_details"`
}

type WsClientDigest struct {
	Id int `json:"user_id"`
	LastUpdate time.Time `json:"last_update"`
}

type MessageWelcome struct {
	MessageType string `json:"action"`
	Users []WsClientDigest `json:"users"`
}

type MessageRoomUpdate struct {
	MessageType string `json:"type"`
	UserId int `json:"user_id"`
}
