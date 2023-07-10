package service_test

import (
	"testing"
	"unifai/service"

	"golang.org/x/text/language"
)

func TestTranslate(t *testing.T) {
	trans, err := service.NewTranslator()
	if err != nil {
		t.Errorf("Error creating translator service: %v\n", err)
		return
	}
	defer trans.Conn.Close()

	res, err := trans.Translate("Я люблю когда голые волосатые мужики обмазываются маслом.", language.Russian, language.English)
	if err != nil {
		t.Errorf("Translate failed with error: %v\n", err)
	}
	t.Logf("EN: %s\n", res)

	res, err = trans.Translate("Я люблю когда голые волосатые мужики обмазываются маслом.", language.Russian, language.French)
	if err != nil {
		t.Errorf("Translate failed with error: %v\n", err)
	}
	t.Logf("FR: %s\n", res)
}
