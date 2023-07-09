package controller

import (
	"net/http"
	"strconv"
	"strings"
	"unifai/entity"
	"unifai/httputil"
	"unifai/ws"

	"github.com/gin-gonic/gin"
	"golang.org/x/text/language"
)

// CreateRoom godoc
//
//	@Summary		Create a new room
//	@Description	Create a new room with given name, description and owner
//	@Tags			rooms
//	@Accept			json
//	@Produce		json
//	@Param			details	body		RoomCreation	true	"Room details"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/create [post]
func (c *Controller) CreateRoom(ctx *gin.Context) {
	var rd RoomCreation
	if err := ctx.ShouldBindJSON(&rd); err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}
	if rd.AdminId == 0 { // ID starts from 1 in postgres
		rd.AdminId = ctx.GetInt("user_id")
	}

	room, err := c.Store.CreateRoom(entity.Room{Name: rd.Name, Description: rd.Description, AdminId: rd.AdminId})
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}
	uid := ctx.GetInt("user_id")
	err = c.Store.UpdateRoomJoin(room.Id, uid)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Created room with ID: " + strconv.Itoa(room.Id)})
}

type RoomCreation struct {
	Name        string `json:"name" binding:"required" validate:"required"`
	Description string `json:"description"`
	AdminId     int    `json:"admin_id"`
}

// JoinRoom godoc
//
//	@Summary		Join a room
//	@Description	Join the room with given id
//	@Tags			rooms
//	@Produce		json
//	@Param			id	path		int	true	"Room id"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/{id}/join [get]
func (c *Controller) JoinRoom(ctx *gin.Context) {
	par := ctx.Param("id") // has slashes on beginning and end
	roomId, err := strconv.Atoi(strings.ReplaceAll(par, "//", ""))

	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	userId := ctx.GetInt("user_id")
	err = c.Store.UpdateRoomJoin(roomId, userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Joined room successfully"})
}

// LeaveRoom godoc
//
//	@Summary		Leave a room 
//	@Description	Leave the room with given ID
//	@Tags			rooms
//	@Produce		json
//	@Param			id	path		int	true	"Room id"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/{id}/leave [get]
func (c *Controller) LeaveRoom(ctx *gin.Context) {
	par := ctx.Param("id") // has slashes on beginning and end
	roomId, err := strconv.Atoi(strings.ReplaceAll(par, "//", ""))

	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	userId := ctx.GetInt("user_id")
	err = c.Store.UpdateRoomLeave(roomId, userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Left room successfully"})
}

// RoomConnect godoc
//
//	@Summary		Connect to a room
//	@Description	Initiate websocket connection with given room id and preferred language
//	@Tags			rooms
//	@Produce		json
//	@Param			id	path		int	true	"Room id"
//	@Param			lang	query		string	true	"Preferred language"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/{id}/connect [get]
func (c *Controller) RoomConnect(ctx *gin.Context) {
	par := ctx.Param("roomId") // has slashes on beginning and end
	roomId, err := strconv.Atoi(strings.ReplaceAll(par, "//", ""))

	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	langStr := ctx.Request.URL.Query().Get("lang")
	lang, err := language.Parse(langStr)
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	clients, err := c.Store.GetRoomParticipants(roomId)
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err) // Room probably does not exist or DB is down
		return
	}
	
	userId := ctx.GetInt("user_id")
	currentUser, err := c.Store.GetUserById(userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err) // Room probably does not exist or DB is down
		return
	}

	var userData []ws.WsClientData
	for _, u := range clients {
		userData = append(userData, ws.WsClientData{Id: u.Id, LastUpdate: u.AudioLastUpdated})
	}


	clientInfo := ws.Client{
		UserId: userId,
		RoomId: roomId,
		Name: currentUser.Username,
		PreferredLang: lang,
	}

	ws.ServeWs(c.Hub, clientInfo, ctx.Writer, ctx.Request, userData...)
}

// ListRooms godoc
//
//	@Summary		List current user's rooms
//	@Description	Get all rooms that current user is a member of
//	@Tags			rooms
//	@Produce		json
//	@Success		200	{array}		entity.Room
//	@Failure		401	{object}	httputil.HTTPError
//	@Failure		500	{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/list [get]
func (c *Controller) ListRooms(ctx *gin.Context) {
	userId := ctx.GetInt("user_id")
	rooms, err := c.Store.GetUserRooms(userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
	}

	ctx.JSON(http.StatusOK, rooms)
}

