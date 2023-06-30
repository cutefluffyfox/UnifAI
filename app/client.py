import websocket

import _thread as thread

from model import FasterWhisper
from datetime import datetime
from time import time

import logging
import json
import rel

try:
    from pyaudio_mic import Microphone
except ImportError:
    from sounddevice_mic import Microphone

SERVER_URL = "127.0.0.1:5000"
logging.basicConfig(level=logging.INFO)


model = FasterWhisper(model_name='base')


class WebsocketClient:
    def __init__(self, url):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(url,
                                         on_message=lambda ws, msg: self.on_message(ws, msg),
                                         on_error=lambda ws, msg: self.on_error(ws, msg),
                                         on_close=lambda ws, css, cs: self.on_close(ws, css, cs),
                                         on_open=lambda ws: self.on_open(ws))
        self.url = url
        self.ws.run_forever(dispatcher=rel, reconnect=5)
        rel.dispatch()

    def run(self):
        with Microphone() as mic:
            for audio_segment in mic.stream():
                duration = audio_segment.shape[0] / mic.sample_rate

                t1 = datetime.now()
                data = model.transcribe_speech(audio_segment)
                data['duration'] = duration
                data['delay'] = (datetime.now() - t1).total_seconds()
                print(data)
                data = json.dumps(data)
                if data:
                    self.send_message(data)

    @staticmethod
    def on_message(ws, message):
        message = json.loads(message)
        print("Received back from server:", message['translation'])

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws, close_status_code, close_msg):
        if close_status_code or close_msg:
            print("close status code: " + str(close_status_code))
            print("close message: " + str(close_msg))

    def on_open(self, ws):
        thread.start_new_thread(self.run, ())

    def send_message(self, message):
        if self.ws:
            self.ws.send(message)


def main():
    now = round(time())

    ws = WebsocketClient(f"ws://{SERVER_URL}/ws/{now}")


if __name__ == '__main__':
    main()
