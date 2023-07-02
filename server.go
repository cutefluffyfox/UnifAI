package main

import (
	"net/http"
	"unifai/config"
	"unifai/entity"
	"unifai/service"

	"github.com/gin-gonic/gin"
)

var (
	db = config.Connect()
	userService = service.NewUserService(db)
	cryptoService = service.NewCryptoService()
)

func main() {
	server := gin.Default()

	// User login - provide token pair in response to login/password
	server.POST("/auth/login", func(ctx *gin.Context) {
		var ud entity.UserDetails
		err := ctx.ShouldBindJSON(&ud)
		if err != nil {
			ctx.JSON(http.StatusUnprocessableEntity, "Body malformed")
			return
		}

		user, err := userService.FindUserByUsername(ud.Username)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}

		good := cryptoService.CheckPasswordHash(ud.PasswordRaw, user.PasswordHashed)
		if !good {
			ctx.JSON(http.StatusUnauthorized, "Wrong username/password")
			return
		}

		td, err := service.CreateTokenPair(user.Id)	
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}
		ctx.JSON(http.StatusOK, td)
	})

	// Refresh - generate new token pair with old refresh token
	server.POST("/auth/refresh", service.TokenAuthMiddleware("refresh"), func(ctx *gin.Context) {
		uid := ctx.GetInt("user_id")
		td, err := service.CreateTokenPair(uid)	
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}
		ctx.JSON(http.StatusOK, td)
	})

	// Protected endpoint - upload voice sample
	server.POST("/user/uploadAudio", service.TokenAuthMiddleware("access"), func(ctx *gin.Context) {
	})

	server.POST("/user/whoami", service.TokenAuthMiddleware("access"), func(ctx *gin.Context) {
		uid := ctx.GetInt("user_id")
		user, err := userService.FindUserById(uid)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}
		ctx.JSON(http.StatusOK, user)
	})

	server.POST("/user/register", func(ctx *gin.Context) {
		var ud entity.UserDetails
		err := ctx.ShouldBindJSON(&ud)
		if err != nil {
			ctx.JSON(http.StatusUnprocessableEntity, "Body malformed")
			return
		}
		
		hash, err := cryptoService.HashPassword(ud.PasswordRaw)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}

		var u entity.User = entity.User{Username: ud.Username, PasswordHashed: hash}
		id, err := userService.Register(u)

		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}
		
		td, err := service.CreateTokenPair(id)	
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, err.Error())
			return
		}
		ctx.JSON(http.StatusOK, td)
	})

	// websocket
	server.GET("/joinRoom", service.TokenAuthMiddleware("access"), func(ctx *gin.Context) {
	})

	err := server.Run()
	if err != nil {
		panic(err)
	}
}
