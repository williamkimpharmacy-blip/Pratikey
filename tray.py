"""
Pratikey — Programmable F-Key Remapper
System tray app: shows mappings, open settings, toggle on/off.
"""

import json
import sys
import threading
from pathlib import Path

APP_NAME    = "Pratikey"
APP_VERSION = "1.0.0"

try:
    import pystray
    from PIL import Image
except ImportError:
    print("Missing dependencies. Run: pip install pystray pillow")
    sys.exit(1)

from engine import KeyboardEngine, CONFIG_PATH
from settings_server import start_server, open_settings, stop_server
from hud import FKeyHUD

ICON_DIR   = Path(__file__).parent / "icons"
engine     = None
tray_icon  = None   # Global reference so menu can be refreshed from anywhere
hud        = None   # Floating F-key overlay bar


def load_icon(size=64):
    ico_path = ICON_DIR / "pratikey.ico"
    png_path = ICON_DIR / f"pratikey_{size}.png"

    for path in [png_path, ico_path]:
        if path.exists():
            try:
                return Image.open(str(path)).convert("RGBA").resize((size, size))
            except Exception:
                pass

    # Orange fallback icon
    from PIL import ImageDraw
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad  = max(2, size // 12)
    draw.rounded_rectangle([pad, pad, size-pad, size-pad],
                           radius=size//5, fill=(245, 158, 11, 255))
    # White "P" stroke
    stroke = max(2, size // 8)
    cx, cy = size // 2, size // 2
    draw.rectangle([cx-stroke, pad*2, cx, size-pad*2], fill="white")
    draw.ellipse([cx-stroke, pad*2, size-pad*2, cy], fill="white")
    draw.ellipse([cx-stroke+stroke, pad*2+stroke, size-pad*2-stroke, cy-stroke], fill=(245,158,11,255))
    return img


def _live_fkey_text(fkey):
    """Returns a callable that pystray invokes fresh each time the menu opens."""
    def text_fn(item):
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            for m in cfg.get("mappings", []):
                if m.get("key") == fkey and m.get("enabled", True) and m.get("label"):
                    return f"  {fkey}  →  {m['label']}"
        except Exception:
            pass
        return f"  {fkey}  →  (empty)"
    return text_fn


def build_menu(icon=None):
    items = []

    # Header
    items.append(pystray.MenuItem(f"{APP_NAME} v{APP_VERSION}", None, enabled=False))
    items.append(pystray.Menu.SEPARATOR)

    # Mapping rows — text is a callable so it re-reads config every time menu opens
    from engine import CONFIG_PATH as _CP
    try:
        fkeys = [m["key"] for m in json.loads(_CP.read_text()).get("mappings", [])]
    except Exception:
        fkeys = [f"F{i}" for i in range(1, 13)]

    if fkeys:
        for fkey in fkeys:
            items.append(pystray.MenuItem(_live_fkey_text(fkey), None, enabled=False))
    else:
        items.append(pystray.MenuItem("  No mappings active", None, enabled=False))

    items.append(pystray.Menu.SEPARATOR)

    # Toggle floating HUD bar
    def toggle_hud(icon, item):
        if hud:
            if sys.platform == 'darwin':
                try:
                    from PyObjCTools import AppHelper
                    AppHelper.callLater(0.05, _toggle_hud_and_rebuild)
                except Exception:
                    _toggle_hud_and_rebuild()
            else:
                _toggle_hud_and_rebuild()

    items.append(pystray.MenuItem(
        lambda item: "Hide Key Guide Bar" if (hud and hud.visible) else "Show Key Guide Bar",
        toggle_hud
    ))

    # Settings (opens browser UI)
    def open_settings_menu(icon, item):
        open_settings()

    items.append(pystray.MenuItem("Settings…", open_settings_menu))

    # Toggle engine
    def toggle(icon, item):
        is_active  = engine.toggle()
        state      = "ON" if is_active else "OFF"
        icon.title = f"{APP_NAME} — {state}"
        icon.menu  = pystray.Menu(*build_menu())

    items.append(pystray.MenuItem(
        lambda item: f"{'Disable' if engine.active else 'Enable'} Pratikey",
        toggle
    ))

    items.append(pystray.Menu.SEPARATOR)

    # Quit
    def quit_app(icon, item):
        engine.stop()
        stop_server()
        icon.stop()

    items.append(pystray.MenuItem("Quit Pratikey", quit_app))

    return items


def _rebuild_tray_menu():
    """Rebuild tray menu — must run on the AppKit main thread."""
    if tray_icon:
        tray_icon.menu = pystray.Menu(*build_menu())


def _toggle_hud_and_rebuild():
    """Toggle HUD visibility then refresh tray menu label (main thread only)."""
    if hud:
        hud.toggle()
    _rebuild_tray_menu()


def on_engine_reload():
    """Called by settings server after saving — reloads engine and refreshes tray menu + HUD."""
    engine.reload()
    try:
        from PyObjCTools import AppHelper
        if tray_icon:
            AppHelper.callLater(0.1, _rebuild_tray_menu)
        if hud:
            AppHelper.callLater(0.15, hud.update)
    except Exception:
        if tray_icon:
            _rebuild_tray_menu()
        if hud:
            hud.update()


def check_accessibility():
    """
    Check for Accessibility permission on macOS.
    First tries the native Quartz API prompt; falls back to
    an osascript dialog that opens System Settings automatically.
    """
    # ── Try native Quartz API first ───────────────────────────
    try:
        import Quartz
        if Quartz.AXIsProcessTrusted():
            return True
        opts = {Quartz.kAXTrustedCheckOptionPrompt: True}
        Quartz.AXIsProcessTrustedWithOptions(opts)
        return False
    except Exception:
        pass

    # ── Fallback: osascript dialog + open System Settings ─────
    try:
        import subprocess
        script = (
            'display dialog '
            '"Pratikey needs Accessibility permission to detect your F-keys.\\n\\n'
            'Click OK to open System Settings, then:\\n'
            '1. Go to Privacy & Security → Accessibility\\n'
            '2. Click + and add Pratikey\\n'
            '3. Toggle Pratikey ON\\n'
            '4. Relaunch Pratikey from the menu bar" '
            'buttons {"OK"} default button "OK" '
            'with title "Pratikey — Setup Required" with icon caution'
        )
        # Run dialog in background so app continues starting
        subprocess.Popen(['osascript', '-e', script])
        # Open System Settings straight to Accessibility page
        subprocess.Popen([
            'open',
            'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
        ])
    except Exception:
        pass

    return False


def main():
    global engine, hud

    # Request Accessibility permission on first launch (macOS only)
    if sys.platform == "darwin":
        check_accessibility()

    engine = KeyboardEngine()

    # Start settings web server in background
    start_server(engine_reload_callback=on_engine_reload)

    # Start key engine in background thread
    threading.Thread(target=engine.start, daemon=True).start()

    # Create the floating HUD
    hud = FKeyHUD(CONFIG_PATH)

    # Run tray on main thread
    global tray_icon
    icon = pystray.Icon(
        "pratikey",
        load_icon(64),
        f"{APP_NAME} — ON",
        menu=pystray.Menu(*build_menu()),
    )
    tray_icon = icon

    # Schedule HUD show after the run loop starts
    if sys.platform == "darwin":
        try:
            from PyObjCTools import AppHelper
            AppHelper.callLater(0.5, hud.show)
        except Exception:
            pass
    else:
        # Windows: tkinter HUD runs in its own thread, safe to call directly
        threading.Timer(0.5, hud.show).start()

    icon.run()


if __name__ == "__main__":
    main()
