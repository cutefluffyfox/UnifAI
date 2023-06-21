from websockets.sync.client import connect
from faster_whisper import WhisperModel
from microphone import Microphone

from time import time
import numpy as np

import logging

import torch
import json

MODELS = ['tiny', 'tiny.en', 'base', 'base.en',
          'small', 'small.en', 'medium', 'medium.en',
          'large-v1', 'large-v2']

SERVER_URL = "127.0.0.1:5000"
logging.basicConfig(level=logging.INFO)


class FasterWhisper:
    def __init__(self, model_name: str, language=None, cache_directory=None):
        self._buffer = ""
        self.language = language

        if language == 'en':
            # There is no english version for large models
            if not model_name.endswith('.en') and not model_name.startswith('large'):
                model_name += '.en'

        assert(model_name in MODELS)

        self.model_name = model_name

        model_parameters = self.configure_model_parameters()
        self.model = WhisperModel(self.model_name, download_root=cache_directory, **model_parameters)
        self.transcription_parameters = self.configure_transcription_parameters()

    @staticmethod
    def configure_model_parameters():
        if torch.cuda.is_available():
            compute_type = 'float16'
            device = 'gpu'
            torch.device('cuda')
        else:
            compute_type = 'int8'
            device = 'cpu'
            torch.device('cpu')

        return {'compute_type': compute_type, 'device': device}

    def configure_transcription_parameters(self):
        parameters = {
            'language': self.language,
            'task': 'transcribe',
            'beam_size': 5,
            'best_of': 5,
            'patience': 1,
            'length_penalty': 1,
            'temperature': [
                0.0,
                0.2,
                0.4,
                0.6,
                0.8,
                1.0,
            ],
            'compression_ratio_threshold': 2.4,
            'log_prob_threshold': -1.0,
            'no_speech_threshold': 0.6,
            'condition_on_previous_text': True,
            'initial_prompt': self._buffer or None,
            'prefix': None,
            'suppress_blank': True,
            'suppress_tokens': [-1],
            'without_timestamps': False,
            'max_initial_timestamp': 1.0,
            'word_timestamps': False,
            'prepend_punctuations': "\"'“¿([{-",
            'append_punctuations': "\"'.。,，!！?？:：”)]}、",
            'vad_filter': False,
            'vad_parameters': None,
        }

        return parameters

    def transcribe_speech(self, audio: np.ndarray):
        text = ''
        segments, info = self.model.transcribe(audio, **self.transcription_parameters)
        language = info.language
        lang_prob = info.language_probability

        for segment in segments:
            # self._buffer += segment.text
            text += segment.text

        return {'text': text.strip(),
                'language': language,
                'language_probability': lang_prob}


if __name__ == '__main__':
    model = FasterWhisper(model_name='tiny')

    now = round(time())

    with connect(f'ws://{SERVER_URL}/ws/{now}') as ws:
        logging.info(f'Connected to the server {SERVER_URL}')
        with Microphone() as mic:
            for audio_segment in mic.stream():
                duration = audio_segment.shape[0] / mic.sample_rate

                data = model.transcribe_speech(audio_segment)
                data['duration'] = duration

                data = json.dumps(data)
                ws.send(data)
