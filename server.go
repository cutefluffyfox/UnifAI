package main

import (
	"github.com/gin-gonic/gin"
	"unifai/service"
)

var ()

func main() {
	server := gin.Default()

	// User login - provide token pair in response to login/password
	server.POST("/auth/login", func(ctx *gin.Context) {
	})

	// Refresh - generate new token pair with old refresh token
	server.POST("/auth/refresh", func(ctx *gin.Context) {
	})

	// Protected endpoint - upload voice sample
	server.GET("/user/uploadAudio", service.TokenAuthMiddleware(), func(ctx *gin.Context) {
	})

	server.GET("/user/register", func(ctx *gin.Context) {
	})

	server.GET("/joinRoom", service.TokenAuthMiddleware(), func(ctx *gin.Context) {
	})

	err := server.Run()
	if err != nil {
		panic(err)
	}
}
