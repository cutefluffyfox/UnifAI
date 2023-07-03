from TTS.api import TTS


class VoiceCloningModel:
    """Wrapper around FreeVC24 model"""
    def __init__(self):
        self.sts = TTS('voice_conversion_models/multilingual/vctk/freevc24')

    def synthesise_and_save(self, speech_path: str, voice_path: str, output_file: str = 'tts-sts.mp3'):
        """Do voice conversion for `speech_path` with voice `voice_path`"""
        self.sts.voice_conversion_to_file(source_wav=speech_path, target_wav=voice_path, file_path=output_file)

