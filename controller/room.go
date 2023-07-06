package controller

import (
	"net/http"
	"unifai/entity"
	"unifai/httputil"
	"unifai/service"
	"strconv"

	"github.com/gin-gonic/gin"
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

	rid, err := service.NewRoom(entity.Room{})
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Created room with ID: " + strconv.Itoa(rid)})
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
//	@Param			roomId	path		int	true	"Room id"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/{id}/join [get]
func (c *Controller) JoinRoom(ctx *gin.Context) {
	roomId, err := strconv.Atoi(ctx.Param("roomId"))

	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	userId := ctx.GetInt("user_id")
	err = service.JoinRoom(roomId, userId)
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
//	@Param			roomId	path		int	true	"Room id"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/room/{id}/leave [get]
func (c *Controller) LeaveRoom(ctx *gin.Context) {
	roomId, err := strconv.Atoi(ctx.Param("roomId"))

	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	userId := ctx.GetInt("user_id")
	err = service.LeaveRoom(roomId, userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Left room successfully"})
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
	rooms, err := service.ListRooms(userId)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
	}

	ctx.JSON(http.StatusOK, rooms)
}

func (c *Controller) ConnectRoom(ctx *gin.Context) {
}
