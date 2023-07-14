import websocket

import threading

from model import FasterWhisper
from datetime import datetime

import numpy as np
import sqlite3
import sounddevice
import soundfile
import requests
import uuid
import logging
import json
import rel
import os

from user import User
from sounddevice_mic import Microphone

from voice_cloning.settings import SPEECH_SPEED, PIPER_MODEL
from voice_cloning.downloader import PiperDownloader, FreeVC24Downloader
from voice_cloning.vc import VoiceCloningModel
from voice_cloning.piper import Piper


SERVER_URL = "10.91.7.180:8080/api/v1"
# SERVER_URL = "127.0.0.1:5000"
voice_sample = '../samples/test.ogg'

SELF_UID = None

FORMAT = '%(asctime)s : %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

# FreeVC24Downloader().download()
# PiperDownloader(PIPER_MODEL).download()

stt_model = FasterWhisper(model_name='base')
piper = Piper(PIPER_MODEL, use_cuda='auto')
vc = VoiceCloningModel()

db_name = 'storage.db'
conn = sqlite3.connect(db_name, check_same_thread=False)


def play_sound(file_name: str):
    with soundfile.SoundFile(file_name, 'r', channels=1, format='int16', subtype='PCM_16') as file:
        data, sample_rate = soundfile.read(file, dtype='int16')

        data = np.concatenate((data, np.zeros(sample_rate // 2)))
        sounddevice.play(data, sample_rate, blocking=True)

    try:
        assert file.closed
        os.remove(file_name)
    except Exception as E:
        logger.info('Error while deleting temporary audio:', E)
        pass


def create_tables(connection: sqlite3.Connection):
    create_samples = """CREATE TABLE IF NOT EXISTS user_samples (
                    user_id INTEGER PRIMARY KEY,
                    last_update text NOT NULL,
                    sample_path text NOT NULL
                );"""

    create_info = """CREATE TABLE IF NOT EXISTS user (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username text NOT NULL,
                    password text NOT NULL,
                    access_token text NOT NULL,
                    refresh_token text NOT NULL,
                    transcription_model text,
                    synthesis_language text
                );"""

    cur = connection.cursor()
    cur.execute(create_samples)
    cur.execute(create_info)
    cur.close()


def synthesize_text(text: str, sender_id: int, db_connection: sqlite3.Connection):
    file_name = f'../tmp/{str(uuid.uuid4())}.wav'

    piper.synthesize_and_save(text,
                              output_file=file_name,
                              length_scale=SPEECH_SPEED)
    cur = db_connection.cursor()
    cur.execute('SELECT sample_path FROM user_samples WHERE user_id = ?', (sender_id,))

    if (result := cur.fetchone()) is not None:
        voice_sample_path = result['voice_path']
        logger.info(f'Cloning voice with {voice_sample_path} sample...')

        vc.synthesise_and_save(speech_path=file_name,
                               voice_path=voice_sample_path,
                               output_file=file_name)
    else:
        logger.info(f'No sample audio for {sender_id} found, proceeding without voice cloning')

    threading.Thread(target=play_sound, args=(os.path.abspath(file_name),)).start()
    cur.close()

    return


def check_if_outdated(last_update: str, latest_update: str):
    dt = datetime.fromisoformat(last_update)
    return dt > datetime.fromisoformat(latest_update)


class WebsocketClient:
    def __init__(self, url, bearer_token: str, db_connection: sqlite3.Connection):
        # websocket.enableTrace(True)
        self.bearer_token = bearer_token
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open,
                                         header={'Authorization': f'Bearer {self.bearer_token}'})
        self.url = url
        self.ws.run_forever(dispatcher=rel, reconnect=5)
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

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

    def on_message(self, ws, message):
        message = json.loads(message)
        print("Received back from server:", message)

        if message['type'] == 'synthesis':
            threading.Thread(target=synthesize_text, args=(message['text'], message['sender_id'], self.conn,)).start()
        elif message['type'] == 'room_users':
            for users in message['users']:
                user_id = users['user_id']
                last_update = users['last_update']
                voice_sample_path = f'../samples/{user_id}.ogg'
                is_outdated = False

                cur = self.conn.cursor()
                cur.execute('SELECT user_id FROM user_samples WHERE user_id = ?', (user_id,))

                if (user_exists := cur.fetchone()) is not None:
                    cur.execute('SELECT last_update FROM user_samples WHERE user_id = ?', (user_id,))
                    stored_last_update = cur.fetchone()['last_update']
                    is_outdated = check_if_outdated(stored_last_update, last_update)
                else:
                    cur.execute(f"INSERT INTO user_samples(user_id, last_update, sample_path)"
                                f"VALUES('{user_id}', '{last_update}', '{voice_sample_path}')")

                if not user_exists or is_outdated:
                    print(f'User #{user_id} sample is not stored or is outdated, requesting sample from server')
                    audio = requests.get(f'http://{SERVER_URL}/user/audio/{user_id}',
                                         headers={'Authorization': f'Bearer {self.bearer_token}'})

                    if audio.status_code != 200:
                        print('Error on audio retrieval:', audio.text)

                    with open(voice_sample_path, 'wb') as f:
                        f.write(audio.content)

                    cur.execute(f"UPDATE user_samples SET last_update='{last_update}', "
                                f"sample_path='{voice_sample_path}' WHERE user_id={user_id}")

                    # current_room[user_id] = {'voice_sample_path': voice_sample_path, 'last_update': last_update}
                cur.close()
        else:
            print('Unrecognised message:', message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
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

    if not os.path.exists('../samples'):
        os.mkdir('../samples')

    create_tables(conn)

    oleg = User(username='KpyTou_4yBaK',
                password='olegtachki2012',
                voice_sample_path=voice_sample,
                db_connection=conn)

    oleg.send_sample_data()
    room_id = oleg.create_room()
    print('Created room with id', room_id)
    input()

    ws = WebsocketClient(f"ws://{SERVER_URL}/room/{room_id}/connect?lang=ru",
                         bearer_token=oleg.access_token,
                         db_connection=conn)


if __name__ == '__main__':
    main()
