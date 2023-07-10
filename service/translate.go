package service

import (
	"context"
	"errors"
	"log"
	"os"
	"strconv"
	pb "unifai/translate"

	"golang.org/x/text/language"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Translator struct {
	client pb.TranslatorClient
	Conn *grpc.ClientConn
}

func NewTranslator() (*Translator, error) {
	addr := os.Getenv("GRPC_ADDR")
	log.Printf("Connecting to gRPC server at %s\n", addr)
	conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}
	client := pb.NewTranslatorClient(conn)
	t := Translator{client: client, Conn: conn}

	return &t, nil
}

func (t *Translator) Translate(text string, from language.Tag, to language.Tag) (string, error) {
	req := pb.TranslationRequest{Text: text, FromLang: from.String(), ToLang: to.String()}

	resp, err := t.client.Translate(context.Background(), &req)
	if err != nil {
		return "", err
	}

	if resp.Status == 0 {
	}
	switch resp.Status {
	case 0:
		return resp.Text, nil
	case 1:
		return "", errors.New("Unsupported language pair: " + req.FromLang + " and " + req.ToLang)
	default:
		return "", errors.New("Translation server returned undefined status " + strconv.Itoa(int(resp.Status)))
	}
}

