import configparser
import threading
import sqlite3

import dearpygui.dearpygui as dpg
import logging
import sys
import os
import ctypes
from configparser import ConfigParser
import sounddevice
from app.sounddevice_mic import Recorder

from client import synthesize_text, create_tables, play_sound, check_if_outdated, WebsocketClient

from model import FasterWhisper
from user import AbstractUser, User

from voice_cloning.downloader import PiperDownloader, FreeVC24Downloader
from voice_cloning.vc import VoiceCloningModel
from voice_cloning.piper import Piper

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

SERVER_URL = "10.91.7.179:8080/api/v1"
# SERVER_URL = "127.0.0.1:5000"
voice_sample = '../samples/sample_self.wav'

PIPER_MODEL = 'en_US-libritts-high'
SELF_UID = None
ws = None
available_language_models = {}

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

if not os.path.exists('../tmp'):
    os.mkdir('../tmp')

if not os.path.exists('../samples'):
    os.mkdir('../samples')

create_tables(conn)

login_window_global = -1
settings_window_global = -1
language_settings_window_global = -1
voice_recording_window_global = -1
main_app_window_global = -1
audio_record_window_global = -1
room_choose_window_global = -1
pending_switch_global = None
logged_in = False

viewport_menu_bar_global = -1
recorder = Recorder()
user = AbstractUser()


class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        # Main settings
        self.volume = 100
        self.playback_speed = 1.
        self.model_size = "base"
        self.input_device_name = "default"
        self.server_url = "10.91.7.179:8080/api/v1"
        # Language settings
        self.language = "en_GB"
        self.language_model = "alan-low"
        self.language_settings_initialized = "0"

    def read_settings_from_file(self):
        config = ConfigParser()
        read_result = config.read(self.settings_file)
        if not read_result:
            pass
        else:
            try:
                self.volume = config.getfloat('main', 'volume')
                self.playback_speed = config.getfloat('main', 'playback_speed')
                self.model_size = config.get('main', 'model_size')
                self.input_device_name = config.get('main', 'input_device_name')
                self.server_url = config.get('main', 'server_url')
                self.language = config.get('language', 'language')
                self.language_model = config.get('language', 'language_model')
                self.language_settings_initialized = config.get('language', 'language_settings_initialized')
            except:
                pass

    def write_settings_to_file(self):
        config = ConfigParser()
        with open(self.settings_file, 'w'):
            pass
        config.read(self.settings_file)
        config.add_section('main')
        config.set('main', 'volume', str(self.volume))
        config.set('main', 'playback_speed', str(self.playback_speed))
        config.set('main', 'model_size', self.model_size)
        config.set('main', 'input_device_name', self.input_device_name)
        config.set('main', 'server_url', self.server_url)
        config.add_section('language')
        config.set('language', 'language', self.language)
        config.set('language', 'language_model', self.language_model)
        config.set('language', 'language_settings_initialized', self.language_settings_initialized)
        with open(self.settings_file, 'w') as f:
            config.write(f)


settings_object_global = Settings('../config.ini')


def fix_icon_for_taskbar():
    """
    Lets us see the taskbar icon on Windows
    """
    # Define application ICON,
    #   make sure that dpg.viewport(large_icon=..., small_icon=...) kwargs are both set before this function is ran
    if (sys_platform := sys.platform) == "win32":
        # WINDOWS NEEDS THIS to make this possible
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("UnifAI")


def load_image_from_file(image_file, texture_tag: str):
    width, height, channels, data = dpg.load_image(image_file)

    with dpg.texture_registry(show=False):
        dpg.add_static_texture(width=width, height=height, default_value=data, tag=texture_tag)

    return width, height


def get_input_device_names():
    return list(map(lambda x: x['name'], list(filter(lambda x: x['max_input_channels'] > 1, sounddevice.query_devices()))))


def get_all_tts_models():
    with open("available_models.txt", "r") as avail_models_file:
        lines = list(map(lambda x: x.strip(), avail_models_file.readlines()))
        split_pairs = list(map(lambda x: x.split('-', 1), lines))
        language_models = {}
        for pair in split_pairs:
            language_models.setdefault(pair[0], []).append(pair[1])
        global available_language_models
        available_language_models = language_models
    return language_models


def get_eligible_languages():
    if not available_language_models:
        get_all_tts_models()
    language_list = list(available_language_models.keys())
    return language_list


def get_eligible_models_for_language(language):
    if not available_language_models:
        get_all_tts_models()
    return available_language_models[language]


def login_callback():
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    global user
    user = User(username=dpg.get_value('usernamebox'),
                password=dpg.get_value('passwordbox'),
                voice_sample_path=voice_sample,
                server_url=dpg.get_value("addressbox"),
                db_connection=conn)
    user.login()
    user.send_sample_data()

    if not os.path.exists('../samples/sample_self.wav'):
        go_to_recording_screen()
    else:
        go_to_room_choose_screen()

    global logged_in
    logged_in = True
    show_menu_buttons()


def register_callback():
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    global user
    user = User(username=dpg.get_value('usernamebox'),
                password=dpg.get_value('passwordbox'),
                voice_sample_path=voice_sample,
                server_url=dpg.get_value("addressbox"),
                db_connection=conn)
    user.register()
    user.send_sample_data()

    if not os.path.exists('../samples/sample_self.wav'):
        go_to_recording_screen()
    else:
        go_to_room_choose_screen()

    global settings_object_global
    if settings_object_global.language_settings_initialized == "0":
        dpg.show_item(language_settings_window_global)
    global logged_in
    logged_in = True
    show_menu_buttons()


def go_to_recording_screen():
    dpg.show_item(voice_recording_window_global)
    dpg.hide_item(dpg.get_active_window())
    dpg.set_primary_window(voice_recording_window_global, True)


def start_recording_callback():
    print('started recording')
    recorder.is_recording = True
    threading.Thread(target=recorder.record_audio_to_file).start()


def stop_recording_callback():
    global user
    recorder.is_recording = False
    print('stopped callback')
    user.send_sample_data()
    go_to_room_choose_screen()


def go_to_room_choose_screen():
    dpg.show_item(room_choose_window_global)
    dpg.hide_item(dpg.get_active_window())
    dpg.set_primary_window(room_choose_window_global, True)


def join_room_callback():
    global user
    global settings_object_global
    global ws
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    roomName = dpg.get_value('roomnamebox')

    user.join_room(int(roomName))
    dpg.set_value("room_choosing_id_text", 'Current room id: ' + roomName)


def create_room_callback():
    global user
    global ws
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    roomName = dpg.get_value('roomnamebox')

    room_id = user.create_room(admin_id=0, description='test', name=roomName)
    dpg.set_value("room_choosing_id_text", 'Current room id: ' + str(room_id))


def connect_room_callback():
    global user
    global settings_object_global
    global ws
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    roomName = dpg.get_value('roomnamebox')

    dpg.show_item(main_app_window_global)
    dpg.hide_item(dpg.get_active_window())
    dpg.set_primary_window(main_app_window_global, True)
    ws = WebsocketClient(f"ws://{settings_object_global.server_url}/room/{int(roomName)}/connect"
                         f"?lang={settings_object_global.language.split('_')[0]}",
                         bearer_token=user.access_token,
                         db_connection=conn,
                         speech_speed=settings_object_global.playback_speed)
    dpg.set_value("roomidtext", 'Current room id: ' + str(user.get_current_room_id()))


def leave_room_callback():
    global user
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')
    user.leave_room(user.get_current_room_id())

    dpg.show_item(room_choose_window_global)
    dpg.hide_item(dpg.get_active_window())
    dpg.set_primary_window(room_choose_window_global, True)
    ws.close_connection()
    dpg.set_value("room_choosing_id_text", "")


def open_settings_window_callback():
    dpg.show_item(settings_window_global)


def open_language_settings_window_callback():
    dpg.show_item(language_settings_window_global)


def change_volume_callback(sender):
    global settings_object_global
    volume_value = dpg.get_value(sender)
    settings_object_global.volume = volume_value


def change_playback_speed_callback(sender):
    global settings_object_global
    playback_speed_value = dpg.get_value(sender)
    settings_object_global.playback_speed = playback_speed_value


def change_model_size_callback(sender):
    global settings_object_global
    global stt_model
    model_size_value = str.lower(dpg.get_value(sender))
    settings_object_global.model_size = model_size_value
    stt_model = FasterWhisper(model_name=model_size_value)


def change_input_device_callback(sender):
    global settings_object_global
    input_device_name_value = dpg.get_value(sender)
    settings_object_global.input_device_name = input_device_name_value


def change_language_callback(sender):
    global settings_object_global
    language_value = dpg.get_value(sender)
    settings_object_global.language = language_value
    eligible_models = get_eligible_models_for_language(language_value)
    dpg.configure_item("settings_language_model_combo_box", items=eligible_models)
    dpg.set_value("settings_language_model_combo_box", eligible_models[0])


def change_language_model_callback(sender):
    global settings_object_global
    global piper
    language_model_value = dpg.get_value(sender)
    settings_object_global.language_model = language_model_value
    model = settings_object_global.language + '-' + language_model_value
    PiperDownloader(model).download()
    piper = Piper(model, use_cuda='auto')


def change_server_url_callback(sender):
    global settings_object_global
    server_url_value = dpg.get_value(sender)
    if len(server_url_value) > 3:
        settings_object_global.server_url = dpg.get_value(sender)


def save_settings_callback(sender):
    global settings_object_global
    settings_object_global.write_settings_to_file()


def language_save_settings_callback(sender):
    global settings_object_global
    settings_object_global.language_settings_initialized = "1"
    save_settings_callback(sender)


def logout_callback(sender):
    dpg.show_item(login_window_global)
    dpg.hide_item(dpg.get_active_window())
    dpg.set_primary_window(login_window_global, True)
    global logged_in
    logged_in = False
    hide_menu_buttons()


def change_password_callback(sender):
    pass


def record_new_voice_sample_callback(sender):
    if logged_in:
        dpg.hide_item(dpg.get_active_window())
        dpg.show_item(voice_recording_window_global)
        dpg.set_primary_window(voice_recording_window_global, True)


menu_buttons = []


def hide_menu_buttons():
    for menu_b in menu_buttons:
        dpg.hide_item(menu_b)


def show_menu_buttons():
    for menu_b in menu_buttons:
        dpg.show_item(menu_b)


def main():
    global login_window_global
    global settings_window_global
    global language_settings_window_global
    global voice_recording_window_global
    global main_app_window_global
    global audio_record_window_global
    global room_choose_window_global

    global settings_object_global
    dpg.create_context()
    dpg.create_viewport(title='UnifAI', small_icon='unifai-icon-32x32.ico', large_icon='unifai-icon-64x64.ico', resizable=False, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    fix_icon_for_taskbar()
    dpg.setup_dearpygui()

    logo_dimensions = load_image_from_file("../unifai-logo.png", "unifai-logo")

    settings_object_global.read_settings_from_file()

    # Main Login Window
    with dpg.window(label="Login", autosize=True, no_title_bar=True, no_move=True) as login_window_global:
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
            cell_width = logo_dimensions[0] / 3
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)
            dpg.add_table_column(width=cell_width, width_stretch=True)
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)

            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
                with dpg.table_cell() as ccell:
                    dpg.add_spacer(height=25)
                    dpg.add_image("unifai-logo", width=logo_dimensions[0] / 3, height=logo_dimensions[1] / 3)
                    dpg.add_spacer(height=20)

                    dpg.add_text("Login Screen")
                    dpg.add_input_text(label="Server Address", tag="addressbox", default_value=settings_object_global.server_url, callback=change_server_url_callback)
                    dpg.add_input_text(label="Username", tag="usernamebox")
                    dpg.add_input_text(label="Password", tag="passwordbox", password=True)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Log In", callback=login_callback, width=cell_width / 2)
                        dpg.add_button(label="Register", callback=register_callback, width=cell_width / 2)
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
        dpg.set_primary_window(login_window_global, True)

    # Voice Record
    with dpg.window(label="Voice record", autosize=True, no_title_bar=True, no_move=True, show=False) as voice_recording_window_global:
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
            cell_width = logo_dimensions[0] / 3
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)
            dpg.add_table_column(width=cell_width, width_stretch=True)
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)

            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
                with dpg.table_cell() as ccell2:
                    dpg.add_spacer(height=25)
                    dpg.add_image("unifai-logo", width=logo_dimensions[0] / 3,
                                  height=logo_dimensions[1] / 3)
                    dpg.add_spacer(height=20)

                    dpg.add_text("Voice Recording")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Start", callback=start_recording_callback, width=cell_width / 2)
                        dpg.add_button(label="Stop", callback=stop_recording_callback, width=cell_width / 2)
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass

    # Room Picking
    with dpg.window(label="Room Choosing", autosize=True, no_title_bar=True, no_move=True,
                    show=False) as room_choose_window_global:
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
            cell_width = logo_dimensions[0] / 3
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)
            dpg.add_table_column(width=cell_width, width_stretch=True)
            dpg.add_table_column(width=(WINDOW_WIDTH - cell_width) / 2, width_stretch=True)

            with dpg.table_row():
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
                with dpg.table_cell() as ccell2:
                    dpg.add_spacer(height=25)
                    dpg.add_image("unifai-logo", width=logo_dimensions[0] / 3,
                                  height=logo_dimensions[1] / 3)
                    dpg.add_spacer(height=20)

                    dpg.add_text("Room Choosing")
                    dpg.add_input_text(label="Room Name", tag="roomnamebox")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Join", callback=join_room_callback, width=cell_width / 3)
                        dpg.add_button(label="Register", callback=create_room_callback, width=cell_width / 3)
                        dpg.add_button(label="Connect", callback=connect_room_callback, width=cell_width / 3)
                    dpg.add_button(label="Log Out", callback=logout_callback, width=cell_width + 8)
                    dpg.add_text("", tag="room_choosing_id_text")
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass

    # MAIN APP WINDOW
    with dpg.window(label="Room Choosing", autosize=True, no_title_bar=True, no_move=True,
                    show=False) as main_app_window_global:
        cell_width = WINDOW_WIDTH
        dpg.add_spacer(height=25)

        dpg.add_button(label="Leave Room", callback=leave_room_callback, width=cell_width)
        dpg.add_text(label='Current room id:', tag="roomidtext")
        with dpg.table(header_row=False, policy=dpg.mvTable_SizingStretchProp):
            dpg.add_table_column(width=cell_width, width_stretch=True)
            with dpg.table_row():
                with dpg.table_cell() as ccell2:
                    dpg.add_spacer(height=25)
                    # dpg.add_text('')
                    #    dpg.add_text("Hello!")
                    #dpg.add_image("unifai-logo", width=logo_dimensions[0] / 3,
                    #              height=logo_dimensions[1] / 3)
                    #dpg.add_spacer(height=20)

                    #dpg.add_text("Room Choosing")
                    #dpg.add_input_text(label="Room Name", tag="roomnamebox")
                    #with dpg.group(horizontal=True):
                    #    dpg.add_button(label="Join", callback=join_room_callback, width=cell_width / 2)
                    #    dpg.add_button(label="Register", callback=register_room_callback, width=cell_width / 2)

    # Settings Window
    with dpg.window(label="Settings", autosize=True, show=False, on_close=save_settings_callback) as settings_window_global:
        dpg.add_slider_float(label="Volume", clamped=True, tag="settings_volume_slider_box", default_value=settings_object_global.volume, callback=change_volume_callback)
        dpg.add_slider_float(label="Playback Speed", clamped=True, tag="settings_playback_speed_slider_box", min_value=0.3, max_value=5, default_value=settings_object_global.playback_speed, callback=change_playback_speed_callback)
        dpg.add_combo(["tiny", "base", "small", "medium", "large-v2"], label="Model Size", tag="settings_model_size_combo_box", default_value=settings_object_global.model_size, callback=change_model_size_callback)
        dpg.add_combo(get_input_device_names(), label="Input Device", tag="settings_input_device_combo_box", default_value=settings_object_global.input_device_name, callback=change_input_device_callback)
        dpg.add_button(label="Save Settings", callback=save_settings_callback)

    # Language Settings Window
    with dpg.window(label="Language Settings", autosize=True, show=False, on_close=language_save_settings_callback) as language_settings_window_global:
        dpg.add_combo(get_eligible_languages(), label="Language", tag="settings_language_combo_box", default_value=settings_object_global.language, callback=change_language_callback)
        dpg.add_combo(get_eligible_models_for_language(settings_object_global.language), label="Language Model", tag="settings_language_model_combo_box", default_value=settings_object_global.language_model, callback=change_language_model_callback)
        dpg.add_button(label="Save Settings", callback=language_save_settings_callback)

    global viewport_menu_bar_global
    global menu_buttons
    with dpg.viewport_menu_bar(show=False) as viewport_menu_bar_global:
        menu_buttons += [dpg.add_menu_item(label="Settings", callback=open_settings_window_callback, show=False, tag="settingsmenu")]
        menu_buttons += [dpg.add_menu_item(label="Language Settings", callback=open_language_settings_window_callback, show=False, tag="languagesmenu")]
        menu_buttons += [dpg.add_menu_item(label="Change Password", callback=change_password_callback, show=False, tag="changepassmenu")]
        menu_buttons += [dpg.add_menu_item(label="Record New Voice Sample", callback=record_new_voice_sample_callback, show=False, tag="recordnewvoicemenu")]
    dpg.hide_item(viewport_menu_bar_global)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    dpg.hide_item(viewport_menu_bar_global)


if __name__ == "__main__":
    main()
