package entity

type Room struct {
	Id          int    `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
	AdminId     int    `json:"admin_id"`
}
