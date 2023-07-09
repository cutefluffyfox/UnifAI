package ws

import "golang.org/x/text/language"

type Hub struct {
	unregister chan *Client
	register   chan *Client
	send       chan ChatMessage

	clients map[*Client]bool
	rooms   map[int][]*Client
}

func NewHub() *Hub {
	return &Hub{
		unregister: make(chan *Client),
		register:   make(chan *Client),
		send:       make(chan ChatMessage),

		clients: make(map[*Client]bool),
		rooms:   make(map[int][]*Client),
	}
}

type usersUpdateMessage struct {
	MessageType string `json:"type"`
	UserId int `json:"user_id"`
}

func (h *Hub) run() {
	for {
		select {
		case cl := <- h.register:
			rid := cl.RoomId
			h.clients[cl] = true
			h.rooms[rid] = append(h.rooms[rid], cl)

			msg := usersUpdateMessage{MessageType: "new_user", UserId: cl.UserId}
			for _, c := range h.rooms[rid] {
				c.Out <- msg
			}

		case cl := <- h.unregister:
			if _, ok := h.clients[cl]; ok {
				delete(h.clients, cl)
				close(cl.Out)
			}

			rid := cl.RoomId
			msg := usersUpdateMessage{MessageType: "user_left", UserId: cl.UserId}
			for _, c := range h.rooms[rid] {
				c.Out <- msg
			}

		case msg := <- h.send:
			rid := msg.RoomId
			for _, cl := range h.rooms[rid] {
				if _, ok := h.clients[cl]; cl.UserId != msg.UserId && ok {
					msgOut := &msg
					if msg.Lang != cl.PreferredLang { // need to translate stuff
						msgOut.Body = translate(msg.Body, msg.Lang, cl.PreferredLang)
						msgOut.Lang = cl.PreferredLang
					}

					select {
					case cl.Out <- msgOut:
					default:
						delete(h.clients, cl)
						close(cl.Out)
					}
				}
			}
		}
	}
}

func translate(src string, from language.Tag, to language.Tag) string {
	return src
}
