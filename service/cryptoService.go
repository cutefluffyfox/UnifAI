package service

import "golang.org/x/crypto/bcrypt"

type CryptoService interface {
	HashPassword(string) (string, error)
	CheckPasswordHash(string, string) bool
}

type cryptoService struct{}

func NewCryptoService() CryptoService {
	return cryptoService{}
}
// CheckPasswordHash implements CryptoService.
func (cryptoService) CheckPasswordHash(password string, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err != nil
}

// HashPassword implements CryptoService.
func (cryptoService) HashPassword(pass string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(pass), 14)
	return string(bytes), err
}

