import sqlite3
import requests
import logging
import time
import jwt
from abc import ABC, abstractmethod, abstractproperty

SERVER_URL = "10.91.8.138:8080/api/v1"
# SERVER_URL = "127.0.0.1:5000"
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class AbstractUser:
    def __init__(self):
        self.access_token = None

    @abstractmethod
    def get_current_room_id(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def send_sample_data(self):
        pass

    @abstractmethod
    def create_room(self, admin_id=0, description='description', name='name'):
        pass

    @abstractmethod
    def join_room(self, room_id: int):
        pass

    @abstractmethod
    def leave_room(self, room_id: int):
        pass

    @abstractmethod
    def get_headers(self):
        pass

    @abstractmethod
    def refresh_token_if_needed(self):
        pass


class User(AbstractUser):
    @property
    def current_room_id(self):
        return self._current_room_id

    def __init__(self, username: str, password: str, voice_sample_path: str, db_connection: sqlite3.Connection):
        self.access_token = None
        self.refresh_token = None
        self.username = username
        self.password = password
        self.voice_sample_path = voice_sample_path
        self.current_room_id = 0

        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

        self.register()

    def get_headers(self):
        print('Headers:', self.access_token)
        return {'Authorization': f'Bearer {self.access_token}'}

    def register(self):
        cur = self.conn.cursor()
        cur.execute('SELECT user_id FROM user WHERE username = ?', (self.username,))
        if cur.fetchone() is not None:
            print('Attempt to register an already existing user')
            cur.execute('SELECT access_token, refresh_token FROM user WHERE username = ?', (self.username,))
            self.access_token, self.refresh_token = cur.fetchone()
            return

        r = requests.post(f'http://{SERVER_URL}/auth/register', json={
            'username': self.username,
            'password': self.password,
        })
        print(f'Registering user {self.username}')

        if r.status_code != 200:
            print(f'Registration error: {r.text}')
            return

        tokens = r.json()
        print(tokens)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

        cur.execute(f"INSERT INTO user(username, password, access_token, refresh_token) "
                    f"VALUES('{self.username}', '{self.password}', '{self.access_token}', '{self.refresh_token}');")
        self.conn.commit()
        cur.close()

    def login(self):
        cur = self.conn.cursor()
        cur.execute('SELECT user_id FROM user WHERE username = ?', (self.username,))
        if cur.fetchone() is None:
            print('Attempt to log in without registering')
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
        self.conn.commit()
        cur.close()
        print(f'Logged in, got access_token: {self.access_token}, refresh_token: {self.refresh_token}')

    def send_sample_data(self):
        self.refresh_token_if_needed()

        with open(self.voice_sample_path, 'rb') as audio_sample:
            r = requests.post(f'http://{SERVER_URL}/user/audio',
                              files={'audio': audio_sample},
                              headers=self.get_headers())

            if r.status_code != 200:
                print(f'Error while sending sample data: {r.text}')
            else:
                print(f'Successfully sent audio sample to server, response: {r.json()["message"]}')

    def create_room(self, admin_id=0, description='description', name='name'):
        self.refresh_token_if_needed()

        r = requests.post(f'http://{SERVER_URL}/room/create', headers=self.get_headers(), json={
            'admin_id': admin_id,
            'description': description,
            'name': name
        })

        if r.status_code != 200:
            print(f'Error while creating room: {r.text}')

        self.current_room_id = int(r.json()['message'].split(': ')[1])

        return self.current_room_id

    def join_room(self, room_id: int):
        self.refresh_token_if_needed()

        r = requests.get(f'http://{SERVER_URL}/room/{room_id}/join', headers=self.get_headers())
        self.current_room_id = room_id

        if r.status_code != 200:
            print(f'Error while joining room: {r.text}')

    def leave_room(self, room_id: int):
        self.refresh_token_if_needed()

        r = requests.get(f'http://{SERVER_URL}/room/{room_id}/leave', headers=self.get_headers())

        if r.status_code != 200:
            print(f'Error while leaving room: {r.text}')

    def refresh_token_if_needed(self):
        payload = jwt.decode(self.refresh_token, algorithms=['HS256'], options={"verify_signature": False})

        if int(time.time()) < payload['exp']:
            return

        r = requests.post(f'http://{SERVER_URL}/auth/refresh', headers=self.get_headers())

        if r.status_code != 200:
            print(f'Error while refreshing token pair: {r.text}')

        tokens = r.json()
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']

        cur = self.conn.cursor()
        cur.execute(f"UPDATE user SET access_token='{self.access_token}', "
                    f"refresh_token='{self.refresh_token}' WHERE username='{self.username}'")
        self.conn.commit()
        cur.close()
        print('Successfully refreshed token pair')

    def get_current_room_id(self):
        return self.current_room_id

    @current_room_id.setter
    def current_room_id(self, value):
        self._current_room_id = value
