import configparser

import dearpygui.dearpygui as dpg
import sys
import ctypes
from configparser import ConfigParser
import sounddevice

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700


login_window_global = -1
settings_window_global = -1
language_settings_window_global = -1
voice_recording_window_global = -1
main_app_window_global = -1


class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        # Main settings
        self.volume = 100
        self.playback_speed = 1
        self.model_size = "medium"
        self.input_device_name = "default"
        # Language settings
        self.language = "english"
        self.language_model = "medium"

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
                self.language = config.get('language', 'language')
                self.language_model = config.get('language', 'language_model')
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
        config.add_section('language')
        config.set('language', 'language', self.language)
        config.set('language', 'language_model', self.language_model)
        with open(self.settings_file, 'w') as f:
            config.write(f)


settings_object_global = Settings('config.ini')


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


def get_eligible_languages():
    language_list = ["English", "Russian", "German", "Japanese", "Chinese"]
    return language_list


def get_eligible_models_for_language(language):
    language = str.lower(language)
    language_model = {
        "english": ["tiny", "base", "small", "medium", "large"],
        "russian": ["base", "small", "large"],
        "german": ["small", "medium", "large"],
        "japanese": ["base", "medium", "large"],
        "chinese": ["tiny", "medium", "large"],
    }
    return language_model[language]


def login_callback():
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')


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
    model_size_value = str.lower(dpg.get_value(sender))
    settings_object_global.model_size = model_size_value


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
    language_model_value = dpg.get_value(sender)
    settings_object_global.language_model = language_model_value


def save_settings_callback(sender):
    global settings_object_global
    settings_object_global.write_settings_to_file()


def main():
    global login_window_global
    global settings_window_global
    global language_settings_window_global
    global voice_recording_window_global
    global main_app_window_global

    global settings_object_global
    dpg.create_context()
    dpg.create_viewport(title='UnifAI', small_icon='unifai-icon-32x32.ico', large_icon='unifai-icon-64x64.ico', resizable=False, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    fix_icon_for_taskbar()
    dpg.setup_dearpygui()

    logo_dimensions = load_image_from_file("unifai-logo.png", "unifai-logo")

    settings_object_global.read_settings_from_file()

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
                with dpg.table_cell(tag="mycell") as ccell:
                    dpg.add_spacer(height=25)
                    dpg.add_image("unifai-logo", tag="logoimage", width=logo_dimensions[0] / 3, height=logo_dimensions[1] / 3)
                    dpg.add_spacer(height=20)

                    dpg.add_text("Login Screen", tag="logintext")
                    dpg.add_input_text(label="Server Address", tag="addressbox")
                    dpg.add_input_text(label="Username", tag="usernamebox")
                    dpg.add_input_text(label="Password", tag="passwordbox", password=True)
                    dpg.add_button(label="Log In", callback=login_callback, width=cell_width)
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
        dpg.set_primary_window(login_window_global, True)

    with dpg.window(label="Settings", autosize=True, show=False, on_close=save_settings_callback) as settings_window_global:
        dpg.add_slider_float(label="Volume", clamped=True, tag="settings_volume_slider_box", default_value=settings_object_global.volume, callback=change_volume_callback)
        dpg.add_slider_float(label="Playback Speed", clamped=True, tag="settings_playback_speed_slider_box", min_value=0.3, max_value=5, default_value=settings_object_global.playback_speed, callback=change_playback_speed_callback)
        dpg.add_combo(["Tiny", "Base", "Small", "Medium", "Large"], label="Model Size", tag="settings_model_size_combo_box", default_value=str.capitalize(settings_object_global.model_size), callback=change_model_size_callback)
        dpg.add_combo(get_input_device_names(), label="Input Device", tag="settings_input_device_combo_box", default_value=settings_object_global.input_device_name, callback=change_input_device_callback)
        dpg.add_button(label="Save Settings", callback=save_settings_callback)

    with dpg.window(label="Language Settings", autosize=True, show=False, on_close=save_settings_callback) as language_settings_window_global:
        dpg.add_combo(list(map(lambda x: str.capitalize(x), get_eligible_languages())), label="Language", tag="settings_language_combo_box", default_value=str.capitalize(settings_object_global.language), callback=change_language_callback)
        dpg.add_combo(get_eligible_models_for_language(settings_object_global.language), label="Language Model", tag="settings_language_model_combo_box", default_value=settings_object_global.language_model, callback=change_language_model_callback)
        dpg.add_button(label="Save Settings", callback=save_settings_callback)


    with dpg.viewport_menu_bar():
        dpg.add_menu_item(label="Settings", callback=open_settings_window_callback)
        dpg.add_menu_item(label="Language Settings", callback=open_language_settings_window_callback)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
