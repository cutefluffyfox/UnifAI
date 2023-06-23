package service

import (
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gofrs/uuid"
	"github.com/golang-jwt/jwt/v5"
)

func CreateTokenPair(uid int) (*TokenDetails, error) {
	td := &TokenDetails{}

	td.AtExpires = time.Now().Add(time.Hour * 2).Unix()
	id, err := uuid.NewV4()
	if err != nil {
		return nil, err
	}
	td.AccessUuid = id.String()

	td.RtExpires = time.Now().Add(time.Hour * 24 * 7).Unix()
	id, err = uuid.NewV4()
	if err != nil {
		return nil, err
	}
	td.RefreshUuid = id.String()

	atClaims := jwt.MapClaims{}
	atClaims["type"] = "access"
	atClaims["uuid"] = td.AccessUuid
	atClaims["user_id"] = uid
	atClaims["exp"] = td.AtExpires

	at := jwt.NewWithClaims(jwt.SigningMethodHS256, atClaims)
	td.AccessToken, err = at.SignedString([]byte(os.Getenv("JWT_SECRET")))
	if err != nil {
		return nil, err
	}

	rtClaims := jwt.MapClaims{}
	rtClaims["type"] = "refresh"
	rtClaims["uuid"] = td.RefreshUuid
	rtClaims["user_id"] = uid
	rtClaims["exp"] = td.RtExpires

	rt := jwt.NewWithClaims(jwt.SigningMethodHS256, rtClaims)
	td.RefreshToken, err = rt.SignedString([]byte(os.Getenv("JWT_SECRET")))
	if err != nil {
		return nil, err
	}

	return td, nil
}

func ParseToken(tokenStr string) (*jwt.Token, error) {
	t, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
		// if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
		// 	return nil, fmt.Errorf("Unexpected signing method: %v\n", token.Header["alg"])
		// } // seemingly addressed with WithValidMethods (?)
		return []byte(os.Getenv("JWT_SECRET")), nil
	}, jwt.WithValidMethods([]string{"HMAC"}) )
	return t, err
}

// Check that token is still valid
func ValidateToken(token *jwt.Token) (bool, error) {
	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		if et, err := claims.GetExpirationTime(); err == nil {
			if et.After(time.Now()) {
				return true, nil
			} else {
				return false, jwt.ErrTokenExpired
			}
		} else {
			return false, err
		}
	} else {
		return false, jwt.ErrTokenInvalidClaims
	}
}

func ExtractToken(r *http.Request) (string, error) {
	raw := r.Header.Get("Authorization")
	str := strings.Split(raw, " ")
	if len(str) == 2 {
		return str[1], nil
	}
	return "", InvalidHeaderError{}
}

func TokenAuthMiddleware() gin.HandlerFunc {
	return func(ctx *gin.Context) {
		tstr, err := ExtractToken(ctx.Request)
		if err != nil {
			ctx.JSON(http.StatusUnauthorized, err.Error())
			ctx.Abort()
			return
		}

		tok, err := ParseToken(tstr)
		if err != nil {
			ctx.JSON(http.StatusUnauthorized, err.Error())
			ctx.Abort()
			return
		}
		// if tok == nil {
		// 	ctx.JSON(http.StatusUnauthorized, jwt.ErrTokenMalformed.Error())
		// 	ctx.Abort()
		// 	return
		// }
		
		if res, err := ValidateToken(tok); !res || err != nil {
			ctx.JSON(http.StatusUnauthorized, err.Error())
			ctx.Abort()
			return
		}

		ctx.Next()
	}
}

type InvalidHeaderError struct {}

func (err InvalidHeaderError) Error() string {
	return "Invalid Authorization header"
}

type TokenDetails struct {
	AccessToken  string
	RefreshToken string
	AccessUuid   string
	RefreshUuid  string
	AtExpires    int64
	RtExpires    int64
}

type AccessDetails struct {
	AccessUuid string
	UserId     int
	Expires    int64
}

type RefreshDetails struct {
	RefreshUuid string
	UserId      int
	Expires     int64
}
