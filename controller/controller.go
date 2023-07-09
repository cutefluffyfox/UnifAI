package controller

import (
	"unifai/service"
	"unifai/ws"
)

type Controller struct {
	Store *service.Datastore
	Hub *ws.Hub
}

func NewController(ds *service.Datastore, hub *ws.Hub) *Controller {
	return &Controller{Store: ds, Hub: hub}
}
type Message struct {
	Message string `json:"message"`
}
