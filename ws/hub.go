package ws

import (
	"log"
	"unifai/service"

	"golang.org/x/text/language"
)

type Hub struct {
	unregister chan *Client
	register   chan *Client
	send       chan ChatMessage

	clients map[*Client]bool
	rooms   map[int][]*Client

	translator *service.Translator
}

func NewHub(t *service.Translator) *Hub {
	return &Hub{
		unregister: make(chan *Client),
		register:   make(chan *Client),
		send:       make(chan ChatMessage),

		clients: make(map[*Client]bool),
		rooms:   make(map[int][]*Client),

		translator: t,
	}
}

func (h *Hub) Run() {
	for {
		select {
		case cl := <- h.register:
			rid := cl.RoomId
			h.clients[cl] = true
			h.rooms[rid] = append(h.rooms[rid], cl)

			log.Printf("User %d joined room %d", cl.UserId, cl.RoomId)
			msg := MessageRoomUpdate{MessageType: "new_user", UserId: cl.UserId}
			for _, c := range h.rooms[rid] {
				c.Out <- msg
			}

		case cl := <- h.unregister:
			if _, ok := h.clients[cl]; ok {
				delete(h.clients, cl)
				close(cl.Out)
			}

			rid := cl.RoomId
			log.Printf("User %d left room %d", cl.UserId, cl.RoomId)
			msg := MessageRoomUpdate{MessageType: "user_left", UserId: cl.UserId}
			for _, c := range h.rooms[rid] {
				c.Out <- msg
			}

		case msg := <- h.send:
			rid := msg.RoomId
			for _, cl := range h.rooms[rid] {
				if _, ok := h.clients[cl]; cl.UserId != msg.UserId && ok {
					msgOut := &msg
					if msg.Lang != cl.PreferredLang { // need to translate stuff
						body, err := h.translator.Translate(msg.Body, msg.Lang, cl.PreferredLang)
						if err != nil {
							log.Printf("Translation error: %v\n", err)
							continue
						} else {
							msgOut.Body = body
							msgOut.Lang = cl.PreferredLang
						}
					}

					select {
					case cl.Out <- msgOut:
					default:
						delete(h.clients, cl)
						close(cl.Out)
						log.Printf("User %d left room %d: failed to recieve message", cl.UserId, cl.RoomId)
					}
				}
			}
		}
	}
}

func translate(src string, from language.Tag, to language.Tag) string {
	return src
}
