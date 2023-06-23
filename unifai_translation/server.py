from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from typing import Dict
from decouple import config
import multiprocessing
import uvicorn
import tempfile
import model

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_translated_message(self, data: Dict, websocket: WebSocket):
        target_languages = {}
        result = {'translation': data['text']}
        await websocket.send_json(result)


manager = ConnectionManager()


app = FastAPI()

def process_sample_data(file: tempfile.SpooledTemporaryFile):
    """
    :param file: Audio file to be consumed by voice cloning model
    """
    pass


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_translated_message(data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/uploadSampleData")
async def post(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    print(f'Received file: {file.filename}')
    background_tasks.add_task(process_sample_data, file.file)
    return {'filename': file.filename}


@app.post('/auth/login')
async def login(user: model.User):
    pass


@app.post('/auth/register')
async def register():
    pass 


@app.post('/auth/refresh')
async def refresh():
    pass


@app.get("/")
async def read():
    return {"msg": "hello world"}


def main():
    num_workers = multiprocessing.cpu_count() * 2 + 1
    uvicorn.run(app, host='127.0.0.1', port=5000, log_level='info')


if __name__ == '__main__':
    main()
