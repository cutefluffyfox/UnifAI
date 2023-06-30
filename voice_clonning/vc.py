from TTS.api import TTS


class VoiceCloningModel:
    def __init__(self):
        self.sts = TTS('voice_conversion_models/multilingual/vctk/freevc24')

    def load(self):
        pass

    def stop(self):
        pass

    def synthesise(self, speech_path: str, voice_path: str, output_file: str = 'tts-sts.mp3'):
        self.sts.voice_conversion_to_file(source_wav=speech_path, target_wav=voice_path, file_path=output_file)

