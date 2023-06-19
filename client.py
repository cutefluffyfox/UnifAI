from websockets.sync.client import connect
from faster_whisper import WhisperModel

from time import time
import numpy as np
import torch
import json

MODELS = ['tiny', 'tiny.en', 'base', 'base.en',
          'small', 'small.en', 'medium', 'medium.en',
          'large-v1', 'large-v2']

SERVER_URL = "127.0.0.1:5000"


class FasterWhisper:
    def __init__(self, model_name: str, language=None, cache_directory=None):
        self.model_name = model_name
        if language == 'en':
            # There is no english version for large models
            if not model_name.endswith('.en') and not model_name.startswith('large'):
                model_name += '.en'

        assert(model_name in MODELS)

        model_parameters = self.configure_model_parameters()
        self.model = WhisperModel(self.model_name, download_root=cache_directory, **model_parameters)
        self.transcription_parameters = self.configure_transcription_parameters()

    def configure_model_parameters(self):
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
        return {
            "beam_size": 5,
            "best_of": 5,
            "patience": 1,
            "length_penalty": 1,
            "temperatures": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "condition_on_previous_text": False,
            "initial_prompt": None,
            "prefix": None,
            "suppress_blank": True,
            "suppress_tokens": [-1],
            "without_timestamps": True,
            "max_initial_timestamp": 0.0,
            "word_timestamps": False,
            "prepend_punctuations": "\"'“¿([{-",
            "append_punctuations": "\"'.。,，!！?？:：”)]}、",
            "suppress_numerals": False,
        }

    def speech_to_text(self, audio: np.ndarray):
        text = ''
        segments, info = self.model.transcribe(audio, **self.transcription_parameters)

        for segment in segments:
            text += segment.text

        return text


if __name__ == '__main__':
    model = FasterWhisper(model_name='small')
    now = round(time())

    with connect(f'ws://{SERVER_URL}/ws/{now}') as ws:
        while True:
            data = {'text': input(), 'end_of_sentence': False}
            data = json.dumps(data)
            ws.send(data)
            message = json.loads(ws.recv())
            print(f"Received: {message['translation']}")
