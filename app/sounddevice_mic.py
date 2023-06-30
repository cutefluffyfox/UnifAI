import numpy as np
import logging
import traceback
import sounddevice as sd

from faster_whisper.vad import get_speech_timestamps, collect_chunks

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class Microphone:
    def __init__(self, device_index=None):
        self._build_mic_info()
        # self._device_index = device_index or sd.default.device
        self._stream = sd.InputStream(
            channels=self.num_channels,
            samplerate=self.sample_rate,
            device=device_index,
            blocksize=self.chunk_size,
            dtype='int16'
        )

    def __enter__(self):
        logger.info('Started listening')
        self.is_running = True
        self._stream.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        logging.info('Stopped listening on a mic')
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        if self.is_running:
            self._stream.stop()

        return True

    def stream(self):
        vad_params = {
            'min_speech_duration_ms': 100,
            'min_silence_duration_ms': 700,
            'max_speech_duration_s': float('inf')
        }

        speech = np.array([], dtype=np.float32)

        try:
            while self.is_running:
                data = self._stream.read(self.frames_per_buffer // 8)[0]

                audio = np.frombuffer(data, np.int16).astype(np.float32) * (1 / 32768.0)
                speech_chunks = get_speech_timestamps(audio, **vad_params)

                collected_chunks = collect_chunks(audio, speech_chunks)
                if collected_chunks.any():
                    speech = np.concatenate((speech, collected_chunks))

                if speech.any():
                    yield speech
                    speech = np.array([], dtype=np.float32)
        except KeyboardInterrupt:
            self._stream.close()

    def _build_mic_info(self):
        self.sample_rate = 16000
        self.num_channels = 1
        self.is_running = False
        self.chunk_size = 30
        self.frames_per_buffer = self.chunk_size * self.sample_rate
