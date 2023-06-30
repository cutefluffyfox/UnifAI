import logging

from downloader import PiperDownloader, FreeVC24Downloader
from vc import VoiceCloningModel
from piper import Piper

voice_sample = '../sandbox/voice/rus_ai.ogg'

# lang = 'en-us'
# text = "Good morning china. now i have ice cream i love ice cream. But 'Fast and Furious 9' is better than ice cream"

lang = 'de'
text = 'Guten Morgen, China. Jetzt habe ich Eis, ich liebe Eis. Aber „Fast and Furious 9“ ist besser als Eis'

# lang = 'ru'
# text = 'Доброе утро китай. теперь у меня есть мороженое, я люблю мороженое. Но «Форсаж 9» лучше мороженого'

# lang = 'zh-CN'
# text = '早上好中国. 现在我有冰激淋 我很喜欢冰激淋. 但是《速度与激情9》比冰激淋'


FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

piper = PiperDownloader('de_DE-thorsten-medium')
piper.download()

FreeVC24Downloader().download()

piper = Piper('de_DE-thorsten-medium')
piper.synthesize_and_save(
    text,
    output_file='piper.wav',
    length_scale=1.5
)

vc = VoiceCloningModel()
vc.synthesise('piper.wav', voice_path=voice_sample)
