package ws

import (
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"
	"golang.org/x/text/language"
)

const (
	writeWait = 10 * time.Second
	pongWait = 60 * time.Second 

	pingPeriod = (pongWait * 9) / 10
	maxMessageSize = 1024
)

var (
	newline = []byte{'\n'}
	space = []byte{' '}
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // TODO: research how to do this if we switch to actual frontend
	},
}

type Client struct {
	UserId int
	RoomId int
	Name string
	PreferredLang language.Tag
	Out chan interface{}

	hub *Hub
	conn *websocket.Conn
}

func (c *Client) readPump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	c.conn.SetReadLimit(maxMessageSize)
	c.conn.SetReadDeadline(time.Now().Add(pongWait))
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		var data MessageIn
		err := c.conn.ReadJSON(&data)
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("ws error: %v", err)
				return
			} else {
				c.conn.WriteJSON(MessageError{MessageType: "error", ErrorType: "format", Err: err})
				continue
			}
		}

		lang, err := language.Parse(data.Language)
		if err != nil {
			c.conn.WriteJSON(MessageError{MessageType: "error", ErrorType: "language", Err: err})
			continue
		}

		c.hub.send <- ChatMessage{UserId: c.UserId, RoomId: c.RoomId, Lang: lang}
	}
}

func (c *Client) writePump() {
	ticker := time.NewTicker(pingPeriod)
	defer func(){
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <- c.Out:
			if !ok {
				c.conn.WriteControl(websocket.CloseMessage, nil, time.Now().Add(writeWait))
			}
			c.conn.SetWriteDeadline(time.Now().Add(writeWait))
			err := c.conn.WriteJSON(message)

			if err != nil {
				log.Printf("Dropping connection with user %d\n", c.UserId)
				return
			}

		case <- ticker.C:
			if err := c.conn.WriteControl(websocket.PingMessage, nil, time.Now().Add(writeWait)); err != nil { 
				return // client did not answer ping
			}
		}
	}
}


func ServeWs(hub *Hub, cl Client, w http.ResponseWriter, r *http.Request, usersData ...WsClientDigest) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}

	cl.Out = make(chan interface{})
	cl.hub = hub
	cl.conn = conn

	cl.hub.register <- &cl
	go cl.readPump()
	go cl.writePump()

	cl.conn.WriteJSON(MessageWelcome{MessageType: "room_users", Users: usersData})
} 
