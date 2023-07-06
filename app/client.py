import websocket

import threading

from model import FasterWhisper
from datetime import datetime
from playsound import playsound

import tempfile
import logging
import json
import rel
import sys
import os

from sounddevice_mic import Microphone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'voice_clonning'))

from voice_clonning.settings import SPEECH_SPEED, PIPER_MODEL
from voice_clonning.downloader import PiperDownloader, FreeVC24Downloader
from voice_clonning.vc import VoiceCloningModel
from voice_clonning.piper import Piper

SERVER_URL = "127.0.0.1:5000"
SELF_UID = None

FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

FreeVC24Downloader().download()
PiperDownloader(PIPER_MODEL).download()

stt_model = FasterWhisper(model_name='base')
piper = Piper(PIPER_MODEL, use_cuda='auto')
vc = VoiceCloningModel()

current_room = {}


def synthesize_text(text: str, uid: int):
    # file_name = f'{str(uuid.uuid4())}.wav'
    with tempfile.NamedTemporaryFile(suffix='wav') as tmp:
        file_name = tmp.name

        piper.synthesize_and_save(text, output_file=file_name, length_scale=SPEECH_SPEED)
        if uid in current_room:
            print('Cloning voice...')
            vc.synthesise_and_save(speech_path=file_name, voice_path=current_room[uid], output_file=file_name)
        else:
            print(f'No sample audio for {uid} found, proceeding without voice cloning')

        playsound(file_name)

    return


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
                data = stt_model.transcribe_speech(audio_segment)
                data['duration'] = duration
                data['delay'] = (datetime.now() - t1).total_seconds()
                data['uid'] = SELF_UID
                print(data)
                data = json.dumps(data)
                if data:
                    self.send_message(data)
        return

    @staticmethod
    def on_message(ws, message):
        global SELF_UID
        message = json.loads(message)
        print("Received back from server:", message['translation'])

        if message['action'] == 'synthesis':
            threading.Thread(target=synthesize_text, args=(message['translation'], message['sender_uid'],)).start()
        elif message['action'] == 'getUid':
            SELF_UID = message["uid"]
            print(f'Server assigned uid: {SELF_UID}')
            current_room[SELF_UID] = '../sandbox/voice/test.ogg'
        else:
            print('Unknown message:', message)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws, close_status_code, close_msg):
        if close_status_code or close_msg:
            print("Close status code: " + str(close_status_code))
            print("Close message: " + str(close_msg))

    def on_open(self, ws):
        threading.Thread(target=self.run).start()

    def send_message(self, message):
        if self.ws:
            self.ws.send(message)


def main():
    ws = WebsocketClient(f"ws://{SERVER_URL}/ws")


if __name__ == '__main__':
    main()
