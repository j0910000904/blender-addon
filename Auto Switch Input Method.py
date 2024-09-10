bl_info = {
    "name": "Auto Switch Input Method",
    "blender": (4, 10, 0),
    "category": "System",
    "version": (1, 0),
    "author": "LIN CHUN CHE",
    "description": "Automatically switch input method to English if it's in Chinese.",
}

import bpy
import ctypes

HKL_NEXT = 1
CHINESE_KEYBOARD_LAYOUT = 0x0804
ENGLISH_KEYBOARD_LAYOUT = 0x0409

user32 = ctypes.WinDLL('user32', use_last_error=True)

def get_current_keyboard_layout():
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    layout_id = user32.GetKeyboardLayout(thread_id)
    return layout_id & 0xFFFF

def switch_to_english():
    user32.ActivateKeyboardLayout(ENGLISH_KEYBOARD_LAYOUT, 0)

def check_input_method():
    current_layout = get_current_keyboard_layout()
    if str(current_layout) == str(1028):
        switch_to_english()
    return 0.1

def register():
    bpy.app.timers.register(check_input_method, first_interval=0.1)

def unregister():
    bpy.app.timers.unregister(check_input_method)

if __name__ == "__main__":
    register()
