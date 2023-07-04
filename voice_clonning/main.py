# python build-in libraries
import logging

# downloadable library to play audio files
from playsound import playsound

# all voice-cloning related libraries
from downloader import PiperDownloader, FreeVC24Downloader
from vc import VoiceCloningModel
from piper import Piper


# Configure logging
FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


# Define all required key variables
speech_speed = 1.2
voice_sample = '../sandbox/voice/rus_ai.ogg'
output_file = 'tts-sts.wav'
model = 'en_US-libritts-high'
text = "Good morning china. now i have ice cream i love ice cream. But 'Fast and Furious 9' is better than ice cream"


# Download models
FreeVC24Downloader().download()
PiperDownloader(model).download()


# Define all models (after downloading)
piper = Piper(model, use_cuda='auto')
vc = VoiceCloningModel()


# Full pipeline
piper.synthesize_and_save(text, output_file=output_file, length_scale=speech_speed)
vc.synthesise_and_save(speech_path=output_file, voice_path=voice_sample, output_file=output_file)
# playsound(output_file)

