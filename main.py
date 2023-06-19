import dearpygui.dearpygui as dpg
import sys
import ctypes

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700


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


def login_callback():
    print(f'Server address: {dpg.get_value("addressbox")}, username: {dpg.get_value("usernamebox")}')


def main():
    dpg.create_context()
    dpg.create_viewport(title='UnifAI', small_icon='unifai-icon-32x32.ico', large_icon='unifai-icon-64x64.ico', resizable=False, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    fix_icon_for_taskbar()
    dpg.setup_dearpygui()

    logo_dimensions = load_image_from_file("unifai-logo.png", "unifai-logo")

    with dpg.window(label="Primary Window", autosize=True, no_title_bar=True, no_move=True) as window:
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
                    dpg.add_button(label="Log In", callback=login_callback, width=cell_width)
                with dpg.table_cell():
                    dpg.add_spacer(width=(WINDOW_WIDTH - cell_width) / 2 - 30)
                    pass
        dpg.set_primary_window(window, True)

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
