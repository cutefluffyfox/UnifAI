package controller

import (
	"errors"
	"net/http"
	"unifai/entity"
	"unifai/httputil"
	"unifai/service"

	"github.com/gin-gonic/gin"
)

// Register godoc
//	@Summary		Register new user
//	@Description	Register new user with username and plaintext password
//	@Tags			auth
//	@Accept			json
//	@Produce		json
//	@Param			userDetails	body		entity.UserDetails	true	"Username"
//	@Success		200			{object}	service.TokenDetails
//	@Failure		400			{object}	httputil.HTTPError
//	@Failure		500			{object}	httputil.HTTPError
//	@Router			/auth/register [post]
func (c *Controller) Register(ctx *gin.Context) {
	var ud entity.UserDetails
	err := ctx.ShouldBindJSON(&ud)
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	hash, err := service.HashPassword(ud.PasswordRaw)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	var u entity.User = entity.User{Username: ud.Username, PasswordHashed: hash}
	id, err := service.RegisterUser(u)

	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}

	td, err := service.CreateTokenPair(id)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}
	ctx.JSON(http.StatusOK, td)
}

// Login godoc
//	@Summary		Log into existing user account
//	@Description	Obtain token pairs with username and plaintext password
//	@Tags			auth
//	@Accept			json
//	@Produce		json
//	@Param			userDetails	body		entity.UserDetails	true	"Username"
//	@Success		200			{object}	service.TokenDetails
//	@Failure		400			{object}	httputil.HTTPError
//	@Failure		401			{object}	httputil.HTTPError
//	@Failure		500			{object}	httputil.HTTPError
//	@Router			/auth/login [post]
func (c *Controller) Login(ctx *gin.Context) {
	var ud entity.UserDetails
	err := ctx.ShouldBindJSON(&ud)
	if err != nil {
		httputil.NewError(ctx, http.StatusBadRequest, err)
		return
	}

	user, err := service.FindUserByUsername(ud.Username)
	if err != nil {
		httputil.NewError(ctx, http.StatusUnauthorized, err)
		return
	}

	good := service.CheckPasswordHash(ud.PasswordRaw, user.PasswordHashed)
	if !good {
		httputil.NewError(ctx, http.StatusUnauthorized, errors.New("Wrong username/password"))
		return
	}

	td, err := service.CreateTokenPair(user.Id)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}
	ctx.JSON(http.StatusOK, td)
}

// Refresh godoc
//	@Summary		Refresh token pair
//	@Description	Obtain token pair with valid refresh token
//	@Tags			auth
//	@Produce		json
//	@Success		200	{object}	service.TokenDetails
//	@Failure		401	{object}	httputil.HTTPError
//	@Failure		500	{object}	httputil.HTTPError
//	@Security		BearerRefresh
//	@Router			/auth/refresh [post]
func (c *Controller) Refresh(ctx *gin.Context) {
	uid := ctx.GetInt("user_id")
	td, err := service.CreateTokenPair(uid)
	if err != nil {
		httputil.NewError(ctx, http.StatusInternalServerError, err)
		return
	}
	ctx.JSON(http.StatusOK, td)
}
