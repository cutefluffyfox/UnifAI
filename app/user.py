import sqlite3
import requests
import logging
import jwt

SERVER_URL = "10.91.7.180:8080/api/v1"
# SERVER_URL = "127.0.0.1:5000"
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class User:
    def __init__(self, username: str, password: str, voice_sample_path: str, db_connection: sqlite3.Connection):
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.password = password
        self.voice_sample_path = voice_sample_path
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

        self.register()

    def get_headers(self):
        return {'Authorization', f'Bearer {self.access_token}'}

    def register(self):
        cur = self.conn.cursor()
        cur.execute('SELECT user_id FROM user WHERE username = ?', (self.username,))
        if cur.fetchone() is not None:
            logger.info('Attempt to register an already existing user')
            return

        r = requests.post(f'http://{SERVER_URL}/auth/register', json={
            'username': self.username,
            'password': self.password,
        })

        if r.status_code != 200:
            logger.info(f'Registration error: {r.text}')
            return

        tokens = r.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

        cur.execute(f"INSERT INTO user(username, password, access_token, "
                    f"refresh_token, transcription_model, synthesis_language)"
                    f"VALUES('{self.username}', '{self.password}', '{self.access_token}', "
                    f"'{self.refresh_token}', NULL, NULL)")
        cur.close()

    def login(self):
        cur = self.conn.cursor()
        cur.execute('SELECT user_id FROM user WHERE username = ?', (self.username,))
        if cur.fetchone() is None:
            logger.info('Attempt to log in without registering')
            return

        r = requests.post(f'http://{SERVER_URL}/auth/login', json={
            'username': self.username,
            'password': self.password,
        })

        if r.status_code != 200:
            print('Login error:', r.text)
            return

        tokens = r.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

        cur.execute(f"UPDATE user SET access_token='{self.access_token}', "
                    f"refresh_token='{self.refresh_token}' WHERE username='{self.username}'")
        cur.close()
        logger.info(f'Logged in, got access_token: {self.access_token}, refresh_token: {self.refresh_token}')

    def send_sample_data(self):
        self.refresh_token_if_needed()

        with open(self.voice_sample_path, 'rb') as audio_sample:
            r = requests.post(f'http://{SERVER_URL}/user/audio',
                              files={'audio': audio_sample},
                              headers=self.get_headers())

            if r.status_code != 200:
                logger.info(f'Error while sending sample data: {r.text}')
            else:
                logger.info(f'Successfully sent audio sample to server, response: {r.json()["message"]}')

    def create_room(self, admin_id=0, description='description', name='name'):
        self.refresh_token_if_needed()

        r = requests.post(f'http://{SERVER_URL}/room/create', headers=self.get_headers(), json={
            'admin_id': admin_id,
            'description': description,
            'name': name
        })

        if r.status_code != 200:
            logger.info(f'Error while creating room: {r.text}')

        return int(r.json()['message'].split(': ')[1])

    def join_room(self, room_id: int):
        self.refresh_token_if_needed()

        r = requests.post(f'http://{SERVER_URL}/room/{room_id}/join', headers=self.get_headers())

        if r.status_code != 200:
            logger.info(f'Error while joining room: {r.text}')

        # return int(r.json()['message'].split(': ')[1])

    def refresh_token_if_needed(self):
        expire_date = jwt.decode(self.refresh_token, algorithms=['HS256'])

        r = requests.post(f'http://{SERVER_URL}/auth/refresh', headers=self.get_headers())

        if r.status_code != 200:
            logger.info(f'Error while refreshing token pair: {r.text}')

        tokens = r.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

        cur = self.conn.cursor()
        cur.execute(f"UPDATE user SET access_token='{self.access_token}', "
                    f"refresh_token='{self.refresh_token}' WHERE username='{self.username}'")
        cur.close()
        logger.info('Successfully refreshed token pair')
