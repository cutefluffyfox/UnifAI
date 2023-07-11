package service

import (
	"errors"
	"fmt"
	"net/http"
	"os"
	"time"
	"unifai/httputil"

	"github.com/gin-gonic/gin"
	"github.com/gofrs/uuid"
	"github.com/golang-jwt/jwt/v5"
)

func CreateTokenPair(uid int) (*TokenDetails, error) {
	td := &TokenDetails{}

	// Contructing access token
	exp := time.Now().Add(time.Hour * 2)
	id, err := uuid.NewV4()
	if err != nil {
		return nil, err
	}

	atClaims := TokenClaims{
		TokenType: "access",
		UserId: uid,
		RegisteredClaims: jwt.RegisteredClaims{
			ID: id.String(),
			ExpiresAt: jwt.NewNumericDate(exp),
		},
	}
	at := jwt.NewWithClaims(jwt.SigningMethodHS256, atClaims)
	td.AccessToken, err = at.SignedString([]byte(os.Getenv("JWT_SECRET")))
	if err != nil {
		return nil, err
	}

	// Constructing refresh token
	exp = time.Now().Add(time.Hour * 24 * 7)
	id, err = uuid.NewV4()
	if err != nil {
		return nil, err
	}

	rtClaims := TokenClaims{
		TokenType: "refresh",
		UserId: uid,
		RegisteredClaims: jwt.RegisteredClaims{
			ID: id.String(),
			ExpiresAt: jwt.NewNumericDate(exp),
		},
	}

	rt := jwt.NewWithClaims(jwt.SigningMethodHS256, rtClaims)
	td.RefreshToken, err = rt.SignedString([]byte(os.Getenv("JWT_SECRET")))
	if err != nil {
		return nil, err
	}

	return td, nil
}

func ParseToken(tokenStr string) (*jwt.Token, error) {
	getSecret := func(token *jwt.Token) (interface{}, error) {
		return []byte(os.Getenv("JWT_SECRET")), nil
	}

	t, err := jwt.ParseWithClaims(tokenStr, &TokenClaims{}, getSecret, jwt.WithValidMethods([]string{"HS256"}) )
	return t, err
}


func ExtractToken(r *http.Request) (string, error) {
	raw := r.Header.Get("Authorization")
	var str string
	n, err := fmt.Sscanf(raw, "Bearer %s", &str)

	if n == 1 && err == nil {
		return str, nil
	}
	return "", errors.New("Incorrect token format: " + err.Error())
}

// Validates jwt token, compares its type(refresh/access) and sets user_id header to id stored in the token
func TokenAuthMiddleware(tokenType string) gin.HandlerFunc {
	return func(ctx *gin.Context) {
		tstr, err := ExtractToken(ctx.Request)
		if err != nil {
			httputil.NewError(ctx, http.StatusUnauthorized, err)
			ctx.Abort()
			return
		}

		tok, err := ParseToken(tstr)
		if err != nil {
			httputil.NewError(ctx, http.StatusUnauthorized, err)
			ctx.Abort()
			return
		}
		
		claims, ok := tok.Claims.(*TokenClaims)
		if !ok {
			httputil.NewError(ctx, http.StatusUnauthorized, jwt.ErrTokenInvalidClaims)
			ctx.Abort()
			return
		}

		ctx.Set("user_id", claims.UserId)
		ctx.Next()
	}
}

type InvalidHeaderError struct {}

func (err InvalidHeaderError) Error() string {
	return "Invalid Authorization header"
}

type TokenClaims struct {
	UserId int	`json:"user_id"`
	TokenType string `json:"type"`
	jwt.RegisteredClaims
}

type TokenDetails struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
}

