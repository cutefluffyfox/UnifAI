package ws

import (
	"time"

	"golang.org/x/text/language"
)

type ChatMessage struct {
	UserId int `json:"user_id"`
	RoomId int `json:"room_id"`
	Lang language.Tag `json:"lang"`
	Body string `json:"text"`
}

type MessageIn struct {
	MessageType string `json:"type"`
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
	MessageType string `json:"type"`
	Users []WsClientDigest `json:"users"`
}

type MessageRoomUpdate struct {
	MessageType string `json:"type"`
	UserId int `json:"user_id"`
}
