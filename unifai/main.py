from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import time



class TTTT:
    def __init__(self, inputLanguage = "en", outputLanguage = "ru"):

        self.tokenizer = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{inputLanguage}-{outputLanguage}")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(f"Helsinki-NLP/opus-mt-{inputLanguage}-{outputLanguage}")
        self.translate('')


    def translate(self, input):
        translated = self.model.generate(**self.tokenizer(input, return_tensors="pt", padding=True))

        s = ''
        for t in translated:
            s += self.tokenizer.decode(t, skip_special_tokens=True)

        return s



print("GPU found: ", torch.cuda.is_available())


tttt = TTTT()


def t(s):
    start = time.time()
    o = tttt.translate(s)
    print("time:", time.time() - start, "trans:", o)


text = """Three rings for the Elven-kings under the sky,
Seven for the Dwarf-lords in their halls of stone,
Nine for mortal men doomed to die,
One for the Dark Lord on his dark throne;
In the Land of Mordor where the shadows lie.
One ring to rule them all, one ring to find them,
One ring to bring them all, and in the darkness bind them;
In the Land of Mordor where the shadows lie.""".split('\n')

for l in text:
    t(l)

print('\n')
tttt = TTTT('ru', 'en')

text = """Я помню чудное мгновенье:
Передо мной явилась ты,
Как мимолетное виденье,
Как гений чистой красоты.

В томленьях грусти безнадежной,
В тревогах шумной суеты,
Звучал мне долго голос нежный
И снились милые черты.

Шли годы. Бурь порыв мятежный
Рассеял прежние мечты,
И я забыл твой голос нежный,
Твои небесные черты.

В глуши, во мраке заточенья
Тянулись тихо дни мои
Без божества, без вдохновенья,
Без слез, без жизни, без любви.""".split('\n')

for l in text:
    if len(l) > 0:
        t(l)
    else:
        print()

