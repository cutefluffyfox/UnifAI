import websocket

import threading

from model import FasterWhisper
from datetime import datetime
from playsound import playsound

import requests
import uuid
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

SERVER_URL = "10.91.7.180:8080/api/v1"
# SERVER_URL = "127.0.0.1:5000"
voice_sample = '../sandbox/voice/test.ogg'
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''
SELF_UID = None

FORMAT = '%(asctime)s : %(message)s'
logger = logging.getLogger(__name__)
logging.basicConfig(format=FORMAT, level=logging.INFO)

# FreeVC24Downloader().download()
# PiperDownloader(PIPER_MODEL).download()

stt_model = FasterWhisper(model_name='base')
piper = Piper(PIPER_MODEL, use_cuda='auto')
vc = VoiceCloningModel()

current_room = {}


def play_sound(file_name: str):
    playsound(file_name)
    os.remove(file_name)


def synthesize_text(text: str, sender_id: int):
    file_name = f'../tmp/{str(uuid.uuid4())}.wav'

    piper.synthesize_and_save(text,
                              output_file=file_name,
                              length_scale=SPEECH_SPEED)

    if sender_id in current_room:
        print(f'Cloning voice with {current_room[sender_id]} sample...')
        logger.info(f'Cloning voice with {current_room[sender_id]} sample...')
        vc.synthesise_and_save(speech_path=file_name,
                               voice_path=current_room[sender_id]['voice_sample_path'],
                               output_file=file_name)
    else:
        print(f'No sample audio for {sender_id} found, proceeding without voice cloning')
        logger.info(f'No sample audio for {sender_id} found, proceeding without voice cloning')

    threading.Thread(target=play_sound, args=(os.path.abspath(file_name),)).start()

    return


def login_user(username: str, password: str):
    global ACCESS_TOKEN, REFRESH_TOKEN
    r = requests.post(f'http://{SERVER_URL}/auth/login', json={
        'username': username,
        'password': password,
    })

    if r.status_code != 200:
        print('Login error:', r.text)
        return

    tokens = r.json()
    ACCESS_TOKEN = tokens['access_token']
    REFRESH_TOKEN = tokens['refresh_token']
    print(f'Logged in, got access_token: {ACCESS_TOKEN}, refresh_token: {REFRESH_TOKEN}')


def register_user(username: str, password: str):
    global ACCESS_TOKEN, REFRESH_TOKEN
    r = requests.post(f'http://{SERVER_URL}/auth/register', json={
        'username': username,
        'password': password,
    })
    if r.status_code != 200:
        print('Registration error:', r.text)
        return

    tokens = r.json()
    ACCESS_TOKEN = tokens['access_token']
    REFRESH_TOKEN = tokens['refresh_token']
    print(f'Registered, got access_token: {ACCESS_TOKEN}, refresh_token: {REFRESH_TOKEN}')


def send_sample_data(voice_sample_path: str):
    global ACCESS_TOKEN

    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    with open(voice_sample_path, 'rb') as audio_sample:
        r = requests.post(f'http://{SERVER_URL}/user/audio',
                          files={'audio': audio_sample},
                          headers=headers)

        if r.status_code != 200:
            print('Error while sending sample data:', r.text)
        else:
            print('Successfully sent audio sample to server')
            print(r.json()['message'])


def create_room(admin_id=0, description='test', name='test'):
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    r = requests.post(f'http://{SERVER_URL}/room/create', headers=headers, json={
        'admin_id': admin_id,
        'description': description,
        'name': name
    })

    if r.status_code != 200:
        print('Error while creating room:', r.text)

    return int(r.json()['message'].split(': ')[1])


def check_if_outdated(last_update: int, user_id):
    return last_update > current_room[user_id]['last_update']


class WebsocketClient:
    def __init__(self, url, bearer_token=''):
        # websocket.enableTrace(True)
        self.bearer_token = bearer_token
        self.ws = websocket.WebSocketApp(url,
                                         on_message=lambda ws, msg: self.on_message(ws, msg),
                                         on_error=lambda ws, msg: self.on_error(ws, msg),
                                         on_close=lambda ws, css, cs: self.on_close(ws, css, cs),
                                         on_open=self.on_open,
                                         header={'Authorization': f'Bearer {self.bearer_token}'})
        self.url = url
        self.ws.run_forever(dispatcher=rel, reconnect=5)
        rel.dispatch()

    def run(self):
        with Microphone() as mic:
            for audio_segment in mic.stream():
                data = stt_model.transcribe_speech(audio_segment)
                print(data)
                data = json.dumps(data)
                if data:
                    self.send_message(data)
        return

    @staticmethod
    def on_message(ws, message):
        global ACCESS_TOKEN
        message = json.loads(message)
        print("Received back from server:", message)

        if message['type'] == 'synthesis':
            threading.Thread(target=synthesize_text, args=(message['text'], message['sender_id'],)).start()
        elif message['type'] == 'room_users':
            for users in message['users']:
                user_id = users['user_id']
                last_update = users['last_update']

                if user_id not in current_room or check_if_outdated(last_update, user_id):
                    print(f'User id {user_id} sample is not stored or is outdated, requesting sample from server')
                    voice_sample_path = f'../sandbox/voice/{user_id}.ogg'
                    audio = requests.get(f'http://{SERVER_URL}/user/audio/{user_id}',
                                         headers={'Authorization': f'Bearer {ACCESS_TOKEN}'})

                    with open(voice_sample_path, 'wb') as f:
                        f.write(audio.content)

                    current_room[user_id] = {'voice_sample_path': voice_sample_path, 'last_update': last_update}
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
        print('Opened websocket connection with server')
        threading.Thread(target=self.run, daemon=True).start()

    def send_message(self, message):
        if self.ws:
            self.ws.send(message)


def main():
    if not os.path.exists('../tmp'):
        os.mkdir('../tmp')

    login_user('BEBRA228', 'bebra2010')
    send_sample_data(voice_sample)
    room_id = create_room()
    print('Created room with id', room_id)

    ws = WebsocketClient(f"ws://{SERVER_URL}/room/{room_id}/connect?lang=ru", bearer_token=ACCESS_TOKEN)


if __name__ == '__main__':
    main()
