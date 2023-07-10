package main

import (
	"log"
	"unifai/config"
	"unifai/controller"
	"unifai/service"
	"unifai/ws"
	_ "unifai/docs"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/swaggo/files"
	"github.com/swaggo/gin-swagger"
)

//	@title			UnifAI API
//	@version		0.1.0
//	@description	WIP UnifAI API

//	@host		localhost:8080
//	@BasePath	/api/v1

//	@securityDefinitions.apikey	BearerAccess
//	@in							header
//	@name						Authorization
//	@description				Type "Bearer" followed by a space and JWT Acess token.

//	@securityDefinitions.apikey	BearerRefresh
//	@in							header
//	@name						Authorization
//	@description				Type "Bearer" followed by a space and JWT Refresh token.
func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatalf("Could not read .env: %v\n", err)
	}
	config.Migrate(config.Connect()) // TODO: replace with sql file and Docker migrate job probably

	// Initiating DB
	pool, err := service.NewDBPool()
	if err != nil {
		log.Fatalf("Could not connect to database: %v\n", err)
	}
	ds := service.NewDatastore(pool)
	defer pool.Close()

	// Initiating gRPC translation service
	trans, err := service.NewTranslator()
	if err != nil {
		log.Fatalf("Could not connect to translator service: %v\n", err)
	}
	defer trans.Conn.Close()

	// Initiating websocket wsHub
	wsHub := ws.NewHub(trans)
	c := controller.NewController(&ds, wsHub)
	go wsHub.Run()


	r := gin.Default()
	r.MaxMultipartMemory = config.MAX_AUDIO_SIZE

	v1 := r.Group("/api/v1")
	{
		auth := v1.Group("/auth")
		{
			auth.POST("/register", c.Register)
			auth.POST("/login", c.Login)
			auth.POST("/refresh", service.TokenAuthMiddleware("refresh"), c.Refresh)
		}

		user := v1.Group("/user")
		{
			user.Use(service.TokenAuthMiddleware("access"))
			audio := user.Group("/audio")
			{
				audio.POST("", c.UploadAudio)
				audio.GET(":id", c.GetAudio)
			}
			user.GET("/me", c.Whoami)
		}

		room := v1.Group("/room")
		{
			room.Use(service.TokenAuthMiddleware("access"))
			actions := room.Group(":id")
			{
				actions.GET("/join", c.JoinRoom)
				actions.GET("/leave", c.LeaveRoom)
				actions.GET("/connect")
			}
			room.POST("/create", c.CreateRoom)
			room.GET("/list", c.ListRooms)
		}
	}
	r.StaticFile("/docs/swagger.json", "./docs/swagger.json")
	url := ginSwagger.URL("/docs/swagger.json")
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler, url))

	err = r.Run("0.0.0.0:8080")
	if err != nil {
		panic(err)
	}
}
