import sys

import grpc
import translate_pb2 as stub
import translate_pb2_grpc as service
from concurrent.futures import ThreadPoolExecutor
import TTTT
import logging

PORT = '50051'
SERVER_ADDRESS = '0.0.0.0'


class TTTTService(service.TranslatorServicer):
    def __init__(self, model: TTTT.TTTT):
        super().__init__()
        self.model = model

    def Translate(self, request, context):
        text = request.text
        input_language = request.fromLang
        output_language = request.toLang

        try:
            result = self.model.translate(text, input_language, output_language)
            logging.info(msg = f"translation complete!!!\ninput({input_language}):\n{text}\noutput({output_language}):\n{result}")
            return stub.TranslationResponse(status=0, text=result)
        except:
            logging.warning(msg = f"translation not complete({input_language}-{output_language}) :( \ninput:\n{text}")
            return stub.TranslationResponse(status=1, text="")


def main():
    logging.info("Initializing TTTT")
    tttt = TTTT.TTTT()
    logging.info(msg = f"Starting server. Listening on port {PORT}.")
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    service.add_TranslatorServicer_to_server(TTTTService(tttt), server)
    server.add_insecure_port(f'{SERVER_ADDRESS}:{PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, filemode="w")
    # logging.basicConfig(level=logging.INFO, filename="TTTT_logs.log", filemode="w")

    try:
        main()
    except KeyboardInterrupt:
        logging.info(msg = 'Server stopped.')
        exit(0)
