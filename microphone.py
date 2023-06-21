import pyaudio
import numpy as np
import logging
import traceback

from faster_whisper.vad import get_speech_timestamps, collect_chunks

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class Microphone:
    def __init__(self, device_index=None):
        self._build_mic_info()
        self._audio = pyaudio.PyAudio()

        self._device_index = device_index or self.get_matching_device_index()

        self.stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=self.num_channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
            input_device_index=self._device_index
        )

    def __enter__(self):
        logger.info('Started listening')
        self.is_running = True
        self.stream.start_stream()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        logging.info('Stopped listening on a mic')
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        if self.is_running:
            self._stop_stream()

        return True

    def _stop_stream(self):
        self.is_running = False
        self.stream.stop_stream()
        self.stream.close()
        self._audio.terminate()

    def get_matching_device_index(self):
        info = self._audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for device in range(num_devices):
            max_input_channels = self._audio.get_device_info_by_host_api_device_index(0, device).get('maxInputChannels')
            if max_input_channels <= 0:
                continue

            if self._audio.is_format_supported(
                    rate=self.sample_rate,
                    input_device=device,
                    input_format=self.audio_format,
                    input_channels=self.num_channels
            ):
                name = self._audio.get_device_info_by_index(device)['name']
                logger.info(f'Chosen device: {name}')
                return device
        else:
            logger.info(f'No audio devices found')
        logger.info('No matching audio devices found')

    def listen(self):
        vad_params = {
            'min_speech_duration_ms': 100,
            'min_silence_duration_ms': 700,
            'max_speech_duration_s': float('inf')
        }

        speech = np.array([], dtype=np.float32)

        try:
            while self.is_running:
                if not self.stream.is_active():
                    break

                data = self.stream.read(self.frames_per_buffer // 8)

                audio = np.frombuffer(data, np.int16).astype(np.float32) * (1 / 32768.0)
                speech_chunks = get_speech_timestamps(audio, **vad_params)

                collected_chunks = collect_chunks(audio, speech_chunks)
                if collected_chunks.any():
                    speech = np.concatenate((speech, collected_chunks))

                if speech.any():
                    yield speech
                    speech = np.array([], dtype=np.float32)
        except KeyboardInterrupt:
            self._stop_stream()

    def _build_mic_info(self):
        self.audio_format = pyaudio.paInt16
        self.sample_rate = 16000
        self.num_channels = 1
        self.is_running = False
        self.chunk_size = 30
        self.frames_per_buffer = self.chunk_size * self.sample_rate
