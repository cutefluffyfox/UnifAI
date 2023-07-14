from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
# from typing import Dict
# import time

AVAILABLE_LANGUAGES = ['en', 'ru', 'fr', 'es']#[, 'de', 'zh', 'sv', 'pl', 'fi', 'nl', 'ca', 'is', 'el', 'no', 'it', 'uk', 'vi', 'da', 'pt']


class SingleWayTTTT:
    def __init__(self, input_language ="en", output_language ="ru"):
        if input_language == output_language:
            self.simple = True
            self.works = True
            return
        else:
            self.simple = False

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{input_language}-{output_language}")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(f"Helsinki-NLP/opus-mt-{input_language}-{output_language}")
            self.translate('')
            self.works = True
            print(f"Model loaded: {input_language} to {output_language}")
        except Exception:
            self.works = False
            print(f"Model not loaded: {input_language} to {output_language}")

    def translate(self, input_text):
        if self.simple:
            return input_text

        s = ''
        if len(input_text) < 1:
            return s

        translated = self.model.generate(**self.tokenizer(input_text, return_tensors="pt", padding=True))

        for t in translated:
            s += self.tokenizer.decode(t, skip_special_tokens=True)

        return s


class TTTT:
    def __init__(self):
        self.languages = AVAILABLE_LANGUAGES
        self.languageMap = {}  # Dict[str, Dict[str, SingleWayTTTT]]
        self.__build_models__()

    def __build_models__(self):
        for input_language in self.languages:
            self.languageMap[input_language] = {}
            for output_language in self.languages:
                model = SingleWayTTTT(input_language, output_language)
                self.languageMap[input_language][output_language] = model

        self.draw_map()

    def translate(self, input_text, input_language, output_language):
        if input_language not in self.languages or output_language not in self.languages:
            print("NOT IMPLEMENTED LANGUAGES")
            print("We have following languages")
            print(self.languages)
            return
        model = self.__find_model__(input_language, output_language)
        if model.works:
            return model.translate(input_text)

        else:
            print(f"There is no connection between {input_language} and {output_language}")

    def __find_model__(self, input_language, output_language):
        return self.languageMap[input_language][output_language]

    def draw_map(self):
        s = "   "
        models = 0

        for input_language in self.languages:
            s += input_language + " "

        s += '\n'

        for input_language in self.languages:
            s += input_language + " "
            for output_language in self.languages:
                b = self.languageMap[input_language][output_language].works
                if b:
                    s += ' + '
                    models += 1
                else:
                    s += '   '
            s += '\n'

        s = f'{s}\nTotal languages: {len(AVAILABLE_LANGUAGES)}\nAmount of models: {models}'
        print(s)
        return s


def preload_models():
    for from_lang in AVAILABLE_LANGUAGES:
        for to_lang in AVAILABLE_LANGUAGES:
            if from_lang != to_lang:
                a = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{from_lang}-{to_lang}")
                b = AutoModelForSeq2SeqLM.from_pretrained(f"Helsinki-NLP/opus-mt-{from_lang}-{to_lang}")
                del a, b


if __name__ == "__main__":
    preload_models()
