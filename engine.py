"""
Pratikey — Programmable F-Key Remapper
Core engine: intercepts F-keys and fires mapped shortcuts/actions based on config.json
"""

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Controller
except ImportError:
    print("pynput not installed. Run: pip install pynput")
    sys.exit(1)

def _get_config_path():
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle — use writable user directory
        if sys.platform == 'win32':
            config_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / 'Pratikey'
        else:
            config_dir = Path.home() / "Library" / "Application Support" / "Pratikey"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"
        # Copy bundled default config on first launch
        if not config_path.exists():
            import shutil
            bundled = Path(sys._MEIPASS) / "config.json"
            if bundled.exists():
                shutil.copy(bundled, config_path)
        return config_path
    return Path(__file__).parent / "config.json"

CONFIG_PATH = _get_config_path()
controller = Controller()

# Map F-key name strings to pynput Key constants
FKEY_MAP = {
    "F1": Key.f1, "F2": Key.f2, "F3": Key.f3, "F4": Key.f4,
    "F5": Key.f5, "F6": Key.f6, "F7": Key.f7, "F8": Key.f8,
    "F9": Key.f9, "F10": Key.f10, "F11": Key.f11, "F12": Key.f12,
}

# Map modifier name strings to pynput Key constants
MODIFIER_MAP = {
    "ctrl": Key.ctrl, "control": Key.ctrl,
    "shift": Key.shift,
    "alt": Key.alt,
    "cmd": Key.cmd, "meta": Key.cmd, "win": Key.cmd,
}


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def parse_shortcut(shortcut_str: str):
    """
    Parse 'ctrl+shift+t' into ([modifier Keys], KeyCode/Key).
    Returns (modifiers, key) or raises ValueError.
    """
    parts = [p.strip().lower() for p in shortcut_str.split("+")]
    modifiers = []
    key = None

    for part in parts:
        if part in MODIFIER_MAP:
            modifiers.append(MODIFIER_MAP[part])
        else:
            # Single character
            if len(part) == 1:
                key = KeyCode.from_char(part)
            elif part.startswith("f") and part[1:].isdigit():
                key = FKEY_MAP.get(part.upper())
            else:
                # Named keys (tab, enter, space, backspace, etc.)
                named = {
                    "tab": Key.tab, "enter": Key.enter, "return": Key.enter,
                    "space": Key.space, "backspace": Key.backspace,
                    "delete": Key.delete, "escape": Key.esc, "esc": Key.esc,
                    "home": Key.home, "end": Key.end,
                    "pageup": Key.page_up, "pagedown": Key.page_down,
                    "left": Key.left, "right": Key.right,
                    "up": Key.up, "down": Key.down,
                }
                key = named.get(part)
                if key is None:
                    raise ValueError(f"Unknown key: {part!r}")

    if key is None:
        raise ValueError(f"No main key found in shortcut: {shortcut_str!r}")

    return modifiers, key


def fire_shortcut(shortcut_str: str):
    modifiers, key = parse_shortcut(shortcut_str)
    # Press all modifiers
    for mod in modifiers:
        controller.press(mod)
    # Press and release the main key
    controller.press(key)
    controller.release(key)
    # Release modifiers in reverse
    for mod in reversed(modifiers):
        controller.release(mod)


# Media key name → pynput Key constant
MEDIA_KEY_MAP = {
    "play_pause":  Key.media_play_pause,
    "volume_up":   Key.media_volume_up,
    "volume_down": Key.media_volume_down,
    "volume_mute": Key.media_volume_mute,
    "next_track":  Key.media_next,
    "prev_track":  Key.media_previous,
}


def fire_action(action: dict):
    action_type = action.get("type")
    if action_type == "shortcut":
        shortcut = action.get("shortcut", "")
        if shortcut:
            time.sleep(0.05)
            fire_shortcut(shortcut)
    elif action_type == "media_key":
        media_key = MEDIA_KEY_MAP.get(action.get("key", ""))
        if media_key:
            time.sleep(0.05)
            controller.press(media_key)
            controller.release(media_key)
    elif action_type == "type_text":
        from datetime import datetime
        text = action.get("text", "")
        now  = datetime.now()
        text = text.replace("{DATE}", now.strftime("%d %B %Y"))
        text = text.replace("{TIME}", now.strftime("%H:%M"))
        time.sleep(0.05)
        controller.type(text)
    elif action_type == "run_command":
        command = action.get("command", "")
        if command:
            subprocess.Popen(command, shell=True)


class KeyboardEngine:
    def __init__(self):
        self.active = True
        self.mappings = {}  # pynput Key -> action dict
        self._reload_config()
        self._listener = None

    def _reload_config(self):
        try:
            cfg = load_config()
            self.mappings = {}
            for entry in cfg.get("mappings", []):
                if not entry.get("enabled", True):
                    continue
                key_name = entry.get("key", "").upper()
                pynput_key = FKEY_MAP.get(key_name)
                if pynput_key and "action" in entry:
                    self.mappings[pynput_key] = entry["action"]
            print(f"[Pratikey] Loaded {len(self.mappings)} active mapping(s).")
        except Exception as e:
            print(f"[Pratikey] Config load error: {e}")

    def reload(self):
        self._reload_config()

    def on_press(self, key):
        if not self.active:
            return
        action = self.mappings.get(key)
        if action:
            threading.Thread(target=fire_action, args=(action,), daemon=True).start()

    def _wait_for_accessibility(self):
        """Poll until macOS grants Accessibility permission, then return."""
        try:
            import Quartz, time
            while not Quartz.AXIsProcessTrusted():
                print("[Pratikey] Waiting for Accessibility permission...")
                time.sleep(1)
            print("[Pratikey] Accessibility granted.")
        except Exception:
            pass  # Can't check — proceed anyway

    def start(self):
        print("[Pratikey] Engine starting.")
        self._wait_for_accessibility()
        self._listener = keyboard.Listener(on_press=self.on_press, suppress=False)
        self._listener.start()
        self._listener.join()

    def stop(self):
        if self._listener:
            self._listener.stop()
        print("[Pratikey] Engine stopped.")

    def toggle(self):
        self.active = not self.active
        state = "enabled" if self.active else "disabled (pass-through)"
        print(f"[Engine] {state}")
        return self.active


if __name__ == "__main__":
    engine = KeyboardEngine()
    try:
        engine.start()
    except KeyboardInterrupt:
        engine.stop()
