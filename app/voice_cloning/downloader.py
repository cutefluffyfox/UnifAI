import os
import json
import shutil
import logging
import hashlib

from TTS.api import TTS
from huggingface_hub import hf_hub_download


def calculate_md5(file_name) -> str:
    """Calculates file md5 hash"""
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Downloader:
    """Base class for model downloader"""
    home = os.path.expanduser("~")
    cwd = os.getcwd()
    models_path = os.path.join(os.path.dirname(cwd), 'models')

    def __init__(self, model: str, model_path: list[str]):
        self.model = model
        self.path = os.path.join(*model_path)

    def download(self):
        """Download model defined in self"""
        pass

    def delete(self):
        """Delete model defined in self"""
        logging.info(f'Finding {self.path} folder')

        if os.path.exists(self.path):
            logging.info('Found folder and initialized removal')
            shutil.rmtree(self.path)
            logging.info('Successfully removed')
        else:
            logging.warning(f'Did not found folder at path "{self.path}"')

    def setup_folder(self, model_name: str = None) -> str:
        """Setup models/Piper folder (downloads config from hugging face, creates directories)"""
        self.check_and_create_dir(self.models_path)

        model_dir = os.path.join(self.models_path, self.model)
        self.check_and_create_dir(model_dir)

        if model_name is None:
            return model_dir

        model_name_dir = os.path.join(model_dir, model_name)
        self.check_and_create_dir(model_name_dir)
        return model_name_dir

    @staticmethod
    def check_and_create_dir(dir_name):
        """Helper function to create folder if not exists"""
        if not os.path.exists(dir_name):
            logging.info(f'Creating {dir_name} directory')
            os.mkdir(dir_name)


class FreeVC24Downloader(Downloader):
    """FreeVC24 model downloader & deleter"""

    def __init__(self):
        self.vc_location = [self.home, '.local', 'share', 'tts', 'voice_conversion_models--multilingual--vctk--freevc24']
        super().__init__('FreeVC24', self.vc_location)

    def download(self):
        """Download FreeVC24 model via Coqui-tts library API"""
        logging.info(f'Downloading {self.model} model')
        TTS().download_model_by_name('voice_conversion_models/multilingual/vctk/freevc24')
        logging.info(f'Successfully downloaded {self.model}')


class PiperDownloader(Downloader):
    """Piper models downloader & deleter"""
    def __init__(self, model: str):
        self.model_name = model
        self.tts_location = [os.path.dirname(self.cwd), 'models', 'Piper', model]
        super().__init__('Piper', self.tts_location)

    @staticmethod
    def get_available_models():
        """Provides all models that are available for user to download"""
        available_path = os.path.join(Downloader.cwd, '../app/available_models.txt')
        with open(available_path, 'r', encoding='UTF-8') as file:
            models = file.read().splitlines()
        return models

    def get_model_info(self) -> dict:
        """Provides all info about model from config file"""
        piper_dir = self.setup_folder()

        config_path = os.path.join(piper_dir, 'voices.json')
        logging.info(f'Searching for a config file at {config_path}')
        if not os.path.exists(config_path):
            logging.warning('Did not found models.json config file, initializing download')
            hf_hub_download(
                repo_id="rhasspy/piper-voices",
                filename="voices.json",
                local_dir=piper_dir
            )
            logging.info('Successfully downloaded config file')

        logging.info('Reading config file')
        with open(config_path, encoding='UTF-8') as config_file:
            config = json.load(config_file)
        logging.info('Successfully parsed confid file')

        if config.get(self.model_name) is None:
            logging.critical(f'Did not found model {self.model_name} in voices.json')
            raise FileNotFoundError(f'Model {self.model_name} do not exist in /models/Piper/voices.json')

        return config[self.model_name]

    def download(self):
        """Download and configure Piper model from official `rhasspy/piper-voices` hugging face"""
        available = self.get_available_models()
        if self.model_name not in available:
            logging.warning(f'Tried to download unexciting/non-licenced model {self.model_name}')
            raise RuntimeError(f'Tried to download unsupported model `{self.model_name}`. '
                               f'Please check list of all available models via PiperDownloader.get_available_models()')

        model_dir = self.setup_folder(self.model_name)

        model_info = self.get_model_info()

        downloaded_md5 = dict()
        for downloaded in os.listdir(model_dir):
            downloaded_md5[downloaded] = calculate_md5(os.path.join(model_dir, downloaded))

        for file, file_desc in model_info['files'].items():

            if any(file.endswith(downloaded_file) and file_desc['md5_digest'] == md5 for downloaded_file, md5 in downloaded_md5.items()):
                logging.info(f'File {file} already exists in {model_dir}, skipping')
                continue

            logging.info(f'Downloading {file} (size {file_desc["size_bytes"]} bytes)')
            hf_hub_download(
                repo_id="rhasspy/piper-voices",
                filename=file,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
            logging.info(f'Successfully downloaded {file}')

        logging.info('Starting to change files structure')
        for path, directories, files in os.walk(model_dir):
            for file in files:
                current_path = os.path.join(path, file)
                new_path = os.path.join(model_dir, file)

                if current_path == new_path:
                    continue

                logging.info(f'Initialized new path for {file}')
                shutil.move(current_path, new_path)
                logging.info(f'Moved file {current_path} to {new_path}')

        logging.info('Clearing empty directory from hugging face')
        for path, directories, files in os.walk(model_dir):
            for directory in directories:
                dir_path = os.path.join(path, directory)
                logging.info(f'Initializing removal of {dir_path}')
                shutil.rmtree(dir_path)
                logging.info(f'Successfully deleted {dir_path} and all subdirectories')
            break
