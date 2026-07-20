# Programmable Keyboard

Remap F1–F12 to any keyboard shortcut, text snippet, or shell command — with a system tray app for easy management.

## Files

| File | Purpose |
|------|---------|
| `config.json` | Your key mappings — edit this to customise F-keys |
| `config.schema.json` | JSON schema (enables autocomplete in VS Code) |
| `engine.py` | Core interception engine — run this headless or import it |
| `tray.py` | System tray app (wraps the engine with a GUI menu) |
| `requirements.txt` | Python dependencies |

---

## Quick Start (Windows)

### 1. Install Python 3.10+
Download from https://python.org

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Run the tray app
```
python tray.py
```
A keyboard icon appears in the system tray. Right-click it to see your mappings, toggle the engine, or open `config.json` for editing.

### 4. (Optional) Run headless — no tray
```
python engine.py
```

### 5. (Optional) Auto-start on Windows login
Create a shortcut to `pythonw tray.py` and place it in:
```
shell:startup
```
(`Win+R` → type `shell:startup` → Enter)

---

## Editing Mappings

Open `config.json` and edit the `mappings` array.

### Shortcut action
Remap F1 to open a new browser tab:
```json
{
  "key": "F1",
  "label": "New Tab",
  "action": { "type": "shortcut", "shortcut": "ctrl+t" },
  "enabled": true
}
```

Supported modifiers: `ctrl`, `shift`, `alt`, `cmd` / `win`  
Supported keys: any single character, `tab`, `enter`, `space`, `backspace`, `escape`, arrow keys, `f1`–`f12`, etc.

### Type text action
Remap F2 to type a canned phrase:
```json
{
  "key": "F2",
  "label": "Sign-off",
  "action": { "type": "type_text", "text": "Best regards,\nWilliam" },
  "enabled": true
}
```

### Run command action
Remap F3 to open Notepad:
```json
{
  "key": "F3",
  "label": "Notepad",
  "action": { "type": "run_command", "command": "notepad.exe" },
  "enabled": true
}
```

After editing, right-click the tray icon → **Reload Config** (no restart needed).

---

## iOS — Using Apple Shortcuts

iOS restricts system-wide keyboard interception, but you can achieve similar F-key-like quick actions using the **Shortcuts** app:

1. Open **Shortcuts** app → tap **+** to create a new shortcut.
2. Add actions (open app, send message, toggle setting, run script via SSH, etc.).
3. Tap the shortcut name → **Add to Home Screen** for a one-tap button.
4. Or use **Back Tap** (Settings → Accessibility → Touch → Back Tap) to trigger a shortcut with a double/triple tap on the back of your iPhone.
5. For hardware keyboard users: in **Shortcuts** → shortcut settings → **Add Keyboard Shortcut** to assign a key combo.

For a USB/Bluetooth hardware keyboard connected to an iPad, any custom key combos set via Shortcuts will fire globally across apps.

---

## Architecture

```
config.json
     │
     ▼
engine.py  ──── pynput Listener ──── intercepts F-key press
     │                                      │
     │                               suppresses original key
     ▼
fire_action()
     ├── type: "shortcut"    → pynput Controller fires key combo
     ├── type: "type_text"   → pynput Controller types text
     └── type: "run_command" → subprocess.Popen runs shell command

tray.py  (wraps engine.py)
     └── pystray tray icon → menu: toggle / reload / edit config / quit
```

---

## Troubleshooting

**F-keys not intercepted on Windows**  
Run the script as Administrator (right-click → Run as administrator).

**Keys fire twice**  
Some keyboards send F-key events to multiple listeners. Set `"enabled": false` for mappings you don't use.

**Tray icon doesn't appear**  
Install Pillow: `pip install Pillow`
