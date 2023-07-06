from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
import multiprocessing
import json
import uvicorn
import asyncio
import uuid

import tempfile
from typing import Dict


app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.users: Dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        result = {'action': 'getUid', 'uid': str(uuid.uuid4())}

        await websocket.send_text(json.dumps(result))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_translated_message(data, websocket: WebSocket):
        target_languages = {}
        data = json.loads(data)
        result = {'action': 'synthesis', 'translation': data['text'], 'sender_uid': data['uid']}
        await websocket.send_text(json.dumps(result))


manager = ConnectionManager()


def process_sample_data(file: tempfile.SpooledTemporaryFile):
    """
    :param file: Audio file to be consumed by voice cloning model
    """
    pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print('Received:', data)
            await manager.send_translated_message(data, websocket)
    except WebSocketDisconnect as e:
        print('Disconnecting', e)
        manager.disconnect(websocket)


@app.post("/uploadSampleData")
async def post(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    print(f'Received file: {file.filename}')
    background_tasks.add_task(process_sample_data, file.file)
    return {'filename': file.filename}


@app.get("/")
async def read():
    return {"msg": "hello world"}


if __name__ == '__main__':
    num_workers = multiprocessing.cpu_count() * 2 + 1
    uvicorn.run(app, host='127.0.0.1', port=5000, log_level='info')
