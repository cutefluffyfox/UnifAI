package controller

import (
	"net/http"
	"unifai/config"
	"unifai/httputil"

	"github.com/gin-gonic/gin"
)

// UploadAudio godoc
//	@Summary		Upload voice recording for current user
//	@Description	Register new user with username and plaintext password
//	@Tags			user
//	@Accept			mpfd
//	@Produce		json
//	@Param			audio	formData	file	true	"Audio recording"
//	@Success		200		{object}	controller.Message
//	@Failure		400		{object}	httputil.HTTPError
//	@Failure		401		{object}	httputil.HTTPError
//	@Failure		500		{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/user/audio [post]
func (c *Controller) UploadAudio(ctx *gin.Context) {
	formFile, err := ctx.FormFile("audio")
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	file, err := formFile.Open()
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	content := make([]byte, config.MAX_AUDIO_SIZE)
	_, err = file.Read(content)
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	uid := ctx.GetInt("user_id")
	_, err = c.Store.SetUserAudio(uid, content)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	ctx.JSON(http.StatusOK, Message{Message: "Audio set."})
}

// GetAudio godoc
//
//	@Summary		Get voice recording for user
//	@Description	Register new user with username and plaintext password
//	@Tags			user
//	@Produce		mpfd
//	@Produce		json
//	@Param			id	path		int	true	"User id"
//	@Success		200	{file}		file
//	@Failure		400	{object}	httputil.HTTPError
//	@Failure		401	{object}	httputil.HTTPError
//	@Failure		500	{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/user/audio/{id} [get]
func (c *Controller) GetAudio(ctx *gin.Context) {
	_ = ctx.Param("id")
}

// Whoami godoc
//
//	@Summary		DEBUG ONLY: Get user info
//	@Description	Get id, username and password hash for logged in user
//	@Tags			user
//	@Produce		json
//	@Success		200	{object}	entity.User
//	@Failure		401	{object}	httputil.HTTPError
//	@Failure		500	{object}	httputil.HTTPError
//	@Security		BearerAccess
//	@Router			/user/me [get]
func (c *Controller) Whoami(ctx *gin.Context) {
	uid := ctx.GetInt("user_id")
	user, err := c.Store.GetUserById(uid)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}
	ctx.JSON(http.StatusOK, user)
}
