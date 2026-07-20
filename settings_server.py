"""
Pratikey Settings Server
Visual browser-based settings: click a key, pick a category, pick an action.
No shortcuts or technical knowledge needed.
"""

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

def _get_config_path():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            config_dir = Path(os.environ.get('APPDATA', str(Path.home()))) / 'Pratikey'
        else:
            config_dir = Path.home() / "Library" / "Application Support" / "Pratikey"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"
        if not config_path.exists():
            import shutil
            bundled = Path(sys._MEIPASS) / "config.json"
            if bundled.exists():
                shutil.copy(bundled, config_path)
        return config_path
    return Path(__file__).parent / "config.json"

CONFIG_PATH = _get_config_path()
PORT        = 8765
FKEYS       = [f"F{i}" for i in range(1, 13)]

# ── Action categories ──────────────────────────────────────────────────────────
ACTIONS_JS = """
const CATEGORIES = {
  "Everyday": {
    emoji: "⭐",
    actions: [
      { label:"Copy",            emoji:"📋", action:{type:"shortcut",   shortcut:"cmd+c"} },
      { label:"Paste",           emoji:"📌", action:{type:"shortcut",   shortcut:"cmd+v"} },
      { label:"Cut",             emoji:"✂️", action:{type:"shortcut",   shortcut:"cmd+x"} },
      { label:"Undo",            emoji:"↩️", action:{type:"shortcut",   shortcut:"cmd+z"} },
      { label:"Redo",            emoji:"↪️", action:{type:"shortcut",   shortcut:"cmd+shift+z"} },
      { label:"Save",            emoji:"💾", action:{type:"shortcut",   shortcut:"cmd+s"} },
      { label:"Find",            emoji:"🔍", action:{type:"shortcut",   shortcut:"cmd+f"} },
      { label:"Select All",      emoji:"⬛", action:{type:"shortcut",   shortcut:"cmd+a"} },
      { label:"Print",           emoji:"🖨️",action:{type:"shortcut",   shortcut:"cmd+p"} },
      { label:"Screenshot",      emoji:"📸", action:{type:"shortcut",   shortcut:"cmd+shift+4"} },
      { label:"Lock Screen",     emoji:"🔒", action:{type:"shortcut",   shortcut:"ctrl+cmd+q"} },
      { label:"Google Search",   emoji:"🔎", action:{type:"run_command",command:"open https://www.google.com"} },
      { label:"Calculator",      emoji:"🔢", action:{type:"run_command",command:"open -a Calculator"} },
      { label:"Switch App",      emoji:"🔄", action:{type:"shortcut",   shortcut:"cmd+tab"} },
      { label:"New Tab",         emoji:"➕", action:{type:"shortcut",   shortcut:"cmd+t"} },
      { label:"Close Tab",       emoji:"✖️",action:{type:"shortcut",   shortcut:"cmd+w"} },
    ]
  },
  "Clipboard": {
    emoji: "📋",
    actions: [
      { label:"Copy",                    emoji:"📋", action:{type:"shortcut",   shortcut:"cmd+c"} },
      { label:"Paste",                   emoji:"📌", action:{type:"shortcut",   shortcut:"cmd+v"} },
      { label:"Cut",                     emoji:"✂️", action:{type:"shortcut",   shortcut:"cmd+x"} },
      { label:"Undo",                    emoji:"↩️", action:{type:"shortcut",   shortcut:"cmd+z"} },
      { label:"Redo",                    emoji:"↪️", action:{type:"shortcut",   shortcut:"cmd+shift+z"} },
      { label:"Select All",              emoji:"⬛", action:{type:"shortcut",   shortcut:"cmd+a"} },
      { label:"Paste Without Formatting",emoji:"📋", action:{type:"shortcut",   shortcut:"cmd+shift+alt+v"} },
      { label:"Copy Plain Text",         emoji:"📄", action:{type:"shortcut",   shortcut:"cmd+shift+c"} },
      { label:"Clear Clipboard",         emoji:"🗑️",action:{type:"run_command",command:"echo '' | pbcopy"} },
      { label:"Select Line",             emoji:"↔️", action:{type:"shortcut",   shortcut:"cmd+shift+right"} },
      { label:"Select Word",             emoji:"🔡", action:{type:"shortcut",   shortcut:"alt+shift+right"} },
    ]
  },
  "Documents": {
    emoji: "📄",
    actions: [
      { label:"Save",             emoji:"💾", action:{type:"shortcut",shortcut:"cmd+s"} },
      { label:"Save As",          emoji:"📥", action:{type:"shortcut",shortcut:"cmd+shift+s"} },
      { label:"Print",            emoji:"🖨️",action:{type:"shortcut",shortcut:"cmd+p"} },
      { label:"Find",             emoji:"🔍", action:{type:"shortcut",shortcut:"cmd+f"} },
      { label:"Find & Replace",   emoji:"🔄", action:{type:"shortcut",shortcut:"cmd+h"} },
      { label:"New Document",     emoji:"📝", action:{type:"shortcut",shortcut:"cmd+n"} },
      { label:"Open Document",    emoji:"📂", action:{type:"shortcut",shortcut:"cmd+o"} },
      { label:"Close Document",   emoji:"❌", action:{type:"shortcut",shortcut:"cmd+w"} },
      { label:"Rename File",      emoji:"✏️", action:{type:"shortcut",shortcut:"enter"} },
      { label:"Bold",             emoji:"𝐁",  action:{type:"shortcut",shortcut:"cmd+b"} },
      { label:"Italic",           emoji:"𝐼",  action:{type:"shortcut",shortcut:"cmd+i"} },
      { label:"Underline",        emoji:"U̲",  action:{type:"shortcut",shortcut:"cmd+u"} },
      { label:"Zoom In",          emoji:"🔍", action:{type:"shortcut",shortcut:"cmd+="} },
      { label:"Zoom Out",         emoji:"🔎", action:{type:"shortcut",shortcut:"cmd+-"} },
      { label:"Full Screen",      emoji:"⬛", action:{type:"shortcut",shortcut:"ctrl+cmd+f"} },
    ]
  },
  "Internet": {
    emoji: "🌐",
    actions: [
      { label:"New Tab",           emoji:"➕",  action:{type:"shortcut",   shortcut:"cmd+t"} },
      { label:"Close Tab",         emoji:"✖️", action:{type:"shortcut",   shortcut:"cmd+w"} },
      { label:"Reopen Closed Tab", emoji:"🔁", action:{type:"shortcut",   shortcut:"cmd+shift+t"} },
      { label:"Next Tab",          emoji:"▶️", action:{type:"shortcut",   shortcut:"cmd+shift+]"} },
      { label:"Previous Tab",      emoji:"◀️", action:{type:"shortcut",   shortcut:"cmd+shift+["} },
      { label:"Refresh",           emoji:"🔄", action:{type:"shortcut",   shortcut:"cmd+r"} },
      { label:"Back",              emoji:"⬅️", action:{type:"shortcut",   shortcut:"cmd+["} },
      { label:"Forward",           emoji:"➡️", action:{type:"shortcut",   shortcut:"cmd+]"} },
      { label:"New Window",        emoji:"🪟", action:{type:"shortcut",   shortcut:"cmd+n"} },
      { label:"Private Window",    emoji:"🔏", action:{type:"shortcut",   shortcut:"cmd+shift+n"} },
      { label:"Bookmark This",     emoji:"🔖", action:{type:"shortcut",   shortcut:"cmd+d"} },
      { label:"Downloads",         emoji:"⬇️", action:{type:"shortcut",   shortcut:"cmd+shift+j"} },
      { label:"Address Bar",       emoji:"🌐", action:{type:"shortcut",   shortcut:"cmd+l"} },
      { label:"Google Search",     emoji:"🔎", action:{type:"run_command",command:"open https://www.google.com"} },
      { label:"YouTube",           emoji:"▶️", action:{type:"run_command",command:"open https://youtube.com"} },
      { label:"Facebook",          emoji:"👥", action:{type:"run_command",command:"open https://facebook.com"} },
      { label:"X / Twitter",       emoji:"🐦", action:{type:"run_command",command:"open https://x.com"} },
      { label:"LinkedIn",          emoji:"💼", action:{type:"run_command",command:"open https://linkedin.com"} },
      { label:"Instagram",         emoji:"📷", action:{type:"run_command",command:"open https://instagram.com"} },
    ]
  },
  "Email": {
    emoji: "📧",
    actions: [
      { label:"New Email",      emoji:"✉️",  action:{type:"shortcut",shortcut:"cmd+n"} },
      { label:"Reply",          emoji:"↩️",  action:{type:"shortcut",shortcut:"cmd+r"} },
      { label:"Reply All",      emoji:"↩️",  action:{type:"shortcut",shortcut:"cmd+shift+r"} },
      { label:"Forward",        emoji:"➡️",  action:{type:"shortcut",shortcut:"cmd+shift+f"} },
      { label:"Send",           emoji:"📤",  action:{type:"shortcut",shortcut:"cmd+shift+d"} },
      { label:"Delete",         emoji:"🗑️", action:{type:"shortcut",shortcut:"delete"} },
      { label:"Archive",        emoji:"📦",  action:{type:"shortcut",shortcut:"ctrl+cmd+a"} },
      { label:"Mark as Read",   emoji:"✅",  action:{type:"shortcut",shortcut:"cmd+shift+u"} },
      { label:"Search Email",   emoji:"🔍",  action:{type:"shortcut",shortcut:"cmd+f"} },
      { label:"Add Attachment", emoji:"📎",  action:{type:"shortcut",shortcut:"cmd+shift+a"} },
      { label:"Open Gmail",     emoji:"📧",  action:{type:"run_command",command:"open https://mail.google.com"} },
      { label:"Open Outlook",   emoji:"📮",  action:{type:"run_command",command:"open -a 'Microsoft Outlook'"} },
    ]
  },
  "Files": {
    emoji: "📁",
    actions: [
      { label:"New Folder",    emoji:"📁", action:{type:"shortcut",   shortcut:"cmd+shift+n"} },
      { label:"Open Finder",   emoji:"🗂️",action:{type:"run_command",command:"open -a Finder"} },
      { label:"Home Folder",   emoji:"🏠", action:{type:"run_command",command:"open ~"} },
      { label:"Desktop",       emoji:"🖥️",action:{type:"run_command",command:"open ~/Desktop"} },
      { label:"Downloads",     emoji:"⬇️",action:{type:"run_command",command:"open ~/Downloads"} },
      { label:"Documents",     emoji:"📄", action:{type:"run_command",command:"open ~/Documents"} },
      { label:"Pictures",      emoji:"🖼️",action:{type:"run_command",command:"open ~/Pictures"} },
      { label:"Music",         emoji:"🎵", action:{type:"run_command",command:"open ~/Music"} },
      { label:"Delete File",   emoji:"🗑️",action:{type:"shortcut",   shortcut:"cmd+delete"} },
      { label:"Get Info",      emoji:"ℹ️", action:{type:"shortcut",   shortcut:"cmd+i"} },
      { label:"Quick Look",    emoji:"👁️",action:{type:"shortcut",   shortcut:"space"} },
      { label:"Empty Trash",   emoji:"🗑️",action:{type:"run_command",command:"osascript -e 'tell application Finder to empty the trash'"} },
    ]
  },
  "Computer": {
    emoji: "💻",
    actions: [
      { label:"Lock Screen",     emoji:"🔒", action:{type:"shortcut",   shortcut:"ctrl+cmd+q"} },
      { label:"Sleep",           emoji:"😴", action:{type:"run_command",command:"pmset sleepnow"} },
      { label:"Screenshot",      emoji:"📸", action:{type:"shortcut",   shortcut:"cmd+shift+4"} },
      { label:"Full Screenshot", emoji:"🖥️",action:{type:"shortcut",   shortcut:"cmd+shift+3"} },
      { label:"Screen Recording",emoji:"🎥", action:{type:"shortcut",   shortcut:"cmd+shift+5"} },
      { label:"Spotlight Search",emoji:"🔍", action:{type:"shortcut",   shortcut:"cmd+space"} },
      { label:"Force Quit",      emoji:"⚡", action:{type:"shortcut",   shortcut:"cmd+alt+esc"} },
      { label:"Switch App",      emoji:"🔄", action:{type:"shortcut",   shortcut:"cmd+tab"} },
      { label:"Mission Control", emoji:"🗂️",action:{type:"shortcut",   shortcut:"ctrl+up"} },
      { label:"Minimise Window", emoji:"⬇️",action:{type:"shortcut",   shortcut:"cmd+m"} },
      { label:"Full Screen",     emoji:"⬛", action:{type:"shortcut",   shortcut:"ctrl+cmd+f"} },
      { label:"System Settings", emoji:"⚙️",action:{type:"run_command",command:"open -a 'System Settings'"} },
      { label:"Calculator",      emoji:"🔢", action:{type:"run_command",command:"open -a Calculator"} },
      { label:"Open Finder",     emoji:"🗂️",action:{type:"run_command",command:"open -a Finder"} },
      { label:"Zoom In",         emoji:"🔍", action:{type:"shortcut",   shortcut:"cmd+="} },
      { label:"Zoom Out",        emoji:"🔎", action:{type:"shortcut",   shortcut:"cmd+-"} },
    ]
  },
  "Media": {
    emoji: "🎵",
    actions: [
      { label:"Play / Pause",    emoji:"⏯️", action:{type:"media_key",  key:"play_pause"} },
      { label:"Volume Up",       emoji:"🔊", action:{type:"media_key",  key:"volume_up"} },
      { label:"Volume Down",     emoji:"🔉", action:{type:"media_key",  key:"volume_down"} },
      { label:"Mute",            emoji:"🔇", action:{type:"media_key",  key:"volume_mute"} },
      { label:"Next Track",      emoji:"⏭️", action:{type:"media_key",  key:"next_track"} },
      { label:"Previous Track",  emoji:"⏮️", action:{type:"media_key",  key:"prev_track"} },
      { label:"Open Spotify",    emoji:"🎵", action:{type:"run_command",command:"open -a Spotify"} },
      { label:"Open YouTube",    emoji:"▶️", action:{type:"run_command",command:"open https://youtube.com"} },
      { label:"Open Netflix",    emoji:"🎬", action:{type:"run_command",command:"open https://netflix.com"} },
      { label:"Open Apple Music",emoji:"🎶", action:{type:"run_command",command:"open -a Music"} },
      { label:"Open Podcasts",   emoji:"🎙️",action:{type:"run_command",command:"open -a Podcasts"} },
    ]
  },
  "Office": {
    emoji: "🏢",
    actions: [
      { label:"Open Word",         emoji:"📝", action:{type:"run_command",command:"open -a 'Microsoft Word'"} },
      { label:"Open Excel",        emoji:"📊", action:{type:"run_command",command:"open -a 'Microsoft Excel'"} },
      { label:"Open PowerPoint",   emoji:"📽️",action:{type:"run_command",command:"open -a 'Microsoft PowerPoint'"} },
      { label:"Open Outlook",      emoji:"📮", action:{type:"run_command",command:"open -a 'Microsoft Outlook'"} },
      { label:"Open Teams",        emoji:"👥", action:{type:"run_command",command:"open -a 'Microsoft Teams'"} },
      { label:"Open Zoom",         emoji:"📹", action:{type:"run_command",command:"open -a Zoom"} },
      { label:"Open Slack",        emoji:"💬", action:{type:"run_command",command:"open -a Slack"} },
      { label:"Open Pages",        emoji:"📝", action:{type:"run_command",command:"open -a Pages"} },
      { label:"Open Numbers",      emoji:"📊", action:{type:"run_command",command:"open -a Numbers"} },
      { label:"Open Keynote",      emoji:"📽️",action:{type:"run_command",command:"open -a Keynote"} },
      { label:"Open Notes",        emoji:"📓", action:{type:"run_command",command:"open -a Notes"} },
      { label:"Open Calendar",     emoji:"📅", action:{type:"run_command",command:"open -a Calendar"} },
      { label:"Open Reminders",    emoji:"⏰", action:{type:"run_command",command:"open -a Reminders"} },
      { label:"WhatsApp",          emoji:"💬", action:{type:"run_command",command:"open -a WhatsApp"} },
      { label:"FaceTime",          emoji:"📞", action:{type:"run_command",command:"open -a FaceTime"} },
      { label:"Print",             emoji:"🖨️",action:{type:"shortcut",   shortcut:"cmd+p"} },
    ]
  },
  "Text Snippets": {
    emoji: "✏️",
    actions: [
      { label:"Today's Date",     emoji:"📅", action:{type:"type_text",text:"{DATE}"} },
      { label:"Current Time",     emoji:"🕐", action:{type:"type_text",text:"{TIME}"} },
      { label:"Date & Time",      emoji:"📆", action:{type:"type_text",text:"{DATE} {TIME}"} },
      { label:"Best Regards",     emoji:"👋", action:{type:"type_text",text:"Best regards,"} },
      { label:"Kind Regards",     emoji:"🤝", action:{type:"type_text",text:"Kind regards,"} },
      { label:"Thank You",        emoji:"🙏", action:{type:"type_text",text:"Thank you,"} },
      { label:"Please find attached", emoji:"📎", action:{type:"type_text",text:"Please find attached"} },
      { label:"Let me know",      emoji:"💬", action:{type:"type_text",text:"Please let me know if you have any questions."} },
      { label:"My Email",         emoji:"📧", action:{type:"type_text",text:"your.email@example.com"} },
      { label:"My Phone",         emoji:"📱", action:{type:"type_text",text:"your phone number"} },
      { label:"My Name",          emoji:"👤", action:{type:"type_text",text:"Your Name"} },
      { label:"My Signature",     emoji:"✍️",action:{type:"type_text",text:"Your Name\\nYour Title\\nyour.email@example.com"} },
      { label:"I hope this email finds you well", emoji:"💬", action:{type:"type_text",text:"I hope this email finds you well."} },
    ]
  },
  "AI": {
    emoji: "🤖",
    actions: [
      { label:"Open ChatGPT",   emoji:"🤖", action:{type:"run_command",command:"open https://chatgpt.com"} },
      { label:"Open Claude",    emoji:"✨", action:{type:"run_command",command:"open https://claude.ai"} },
      { label:"Open Gemini",    emoji:"💫", action:{type:"run_command",command:"open https://gemini.google.com"} },
      { label:"Open Copilot",   emoji:"🪟", action:{type:"run_command",command:"open https://copilot.microsoft.com"} },
      { label:"Open Perplexity",emoji:"🔍", action:{type:"run_command",command:"open https://perplexity.ai"} },
      { label:"Open Notion AI", emoji:"📓", action:{type:"run_command",command:"open https://notion.so"} },
      { label:"Open Notes",     emoji:"📓", action:{type:"run_command",command:"open -a Notes"} },
      { label:"Set Timer",      emoji:"⏱️",action:{type:"run_command",command:"open 'x-apple.timer://'"} },
    ]
  },
  "Custom": {
    emoji: "🛠️",
    actions: [],
    custom: true
  }
};
"""

# ── Popular actions (curated) ──────────────────────────────────────────────────
POPULAR_ACTIONS_JS = """
const POPULAR = [
  { label:"New Tab",        emoji:"➕", colorClass:"icon-purple", desc:"Open a new browser tab",         shortcutHint:"⌘T",  action:{type:"shortcut",   shortcut:"cmd+t"} },
  { label:"Paste",          emoji:"📌", colorClass:"icon-orange", desc:"Paste from clipboard",            shortcutHint:"⌘V",  action:{type:"shortcut",   shortcut:"cmd+v"} },
  { label:"Copy",           emoji:"📋", colorClass:"icon-blue",   desc:"Copy selected content",           shortcutHint:"⌘C",  action:{type:"shortcut",   shortcut:"cmd+c"} },
  { label:"Undo",           emoji:"↩️", colorClass:"icon-blue",   desc:"Revert the last action",          shortcutHint:"⌘Z",  action:{type:"shortcut",   shortcut:"cmd+z"} },
  { label:"Redo",           emoji:"↪️", colorClass:"icon-green",  desc:"Redo the last undone action",     shortcutHint:"⌘⇧Z", action:{type:"shortcut",   shortcut:"cmd+shift+z"} },
  { label:"Save",           emoji:"💾", colorClass:"icon-green",  desc:"Save the current document",       shortcutHint:"⌘S",  action:{type:"shortcut",   shortcut:"cmd+s"} },
  { label:"Print",          emoji:"🖨️",colorClass:"icon-red",    desc:"Print the current page",          shortcutHint:"⌘P",  action:{type:"shortcut",   shortcut:"cmd+p"} },
  { label:"Screenshot",     emoji:"📸", colorClass:"icon-blue",   desc:"Capture part of your screen",     shortcutHint:"⌘⇧4", action:{type:"shortcut",   shortcut:"cmd+shift+4"} },
  { label:"Lock Screen",    emoji:"🔒", colorClass:"icon-amber",  desc:"Lock your Mac immediately",       shortcutHint:"⌃⌘Q", action:{type:"shortcut",   shortcut:"ctrl+cmd+q"} },
  { label:"Google Search",  emoji:"🔍", colorClass:"icon-teal",   desc:"Open Google in your browser",     shortcutHint:"",    action:{type:"run_command",command:"open https://www.google.com"} },
  { label:"Calculator",     emoji:"🔢", colorClass:"icon-purple", desc:"Open the Calculator app",         shortcutHint:"",    action:{type:"run_command",command:"open -a Calculator"} },
  { label:"Open App",       emoji:"🚀", colorClass:"icon-pink",   desc:"Open any app or website",         shortcutHint:"",    action:null, custom:true },
];
"""

# ── CSS ────────────────────────────────────────────────────────────────────────
_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: #0d1626;
  color: #e2e8f0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  height: 100vh;
  overflow: hidden;
}
.app-shell { display: flex; height: 100vh; overflow: hidden; }

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #0a1020;
  border-right: 1px solid #1e2d4a;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 16px;
  border-bottom: 1px solid #1a2540;
  flex-shrink: 0;
}
.logo-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 900; color: white;
  flex-shrink: 0;
}
.logo-name { font-size: 15px; font-weight: 700; color: #f1f5f9; }
.logo-tag  { font-size: 10px; color: #475569; margin-top: 1px; }

.sidebar-nav { flex: 1; padding: 8px; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 9px; cursor: pointer;
  transition: background 0.15s; margin-bottom: 2px;
  border: none; background: transparent; width: 100%;
  text-align: left; color: #64748b;
  border-left: 3px solid transparent;
}
.nav-item:hover { background: #111e35; color: #94a3b8; }
.nav-item.active { background: #111e35; color: #e2e8f0; border-left-color: #F59E0B; }
.nav-icon { font-size: 16px; width: 22px; flex-shrink: 0; }
.nav-title { font-size: 13px; font-weight: 600; display: block; }
.nav-sub   { font-size: 10px; color: #475569; margin-top: 1px; display: block; }
.nav-item.active .nav-sub { color: #64748b; }

.tips-box {
  margin: 8px; background: #111e35; border-radius: 12px;
  padding: 12px; flex-shrink: 0;
}
.tips-head { display: flex; align-items: center; gap: 6px; margin-bottom: 5px; }
.tips-head span { font-size: 15px; }
.tips-head strong { font-size: 13px; color: #e2e8f0; }
.tips-body { font-size: 11px; color: #64748b; line-height: 1.5; }
.quick-guide-btn {
  width: 100%; margin-top: 10px; background: #1a2540; border: none;
  border-radius: 8px; padding: 8px 12px; color: #94a3b8;
  font-size: 11px; font-weight: 600; cursor: pointer; font-family: inherit;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.quick-guide-btn:hover { background: #1e2d4a; color: #e2e8f0; }

/* ── Onboarding overlay ── */
.ob-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.72);
  display: flex; align-items: center; justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity 0.3s;
}
.ob-overlay.show { opacity: 1; pointer-events: all; }
.ob-card {
  background: #111e35; border-radius: 24px;
  width: 500px; max-width: 90vw;
  padding: 44px 44px 36px;
  position: relative;
  box-shadow: 0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.06);
}
.ob-close {
  position: absolute; top: 16px; right: 16px;
  background: none; border: none; color: #475569;
  cursor: pointer; font-size: 18px; line-height: 1; padding: 4px 8px; border-radius: 6px;
}
.ob-close:hover { background: #1a2540; color: #94a3b8; }
.ob-slide { display: none; animation: obFadeIn 0.25s ease; }
.ob-slide.active { display: block; }
@keyframes obFadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.ob-illo {
  font-size: 62px; text-align: center; margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(245,158,11,0.3));
}
.ob-step { font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;
  color: #F59E0B; text-align: center; margin-bottom: 8px; }
.ob-title { font-size: 22px; font-weight: 700; text-align: center; color: #e2e8f0; margin-bottom: 10px; }
.ob-body { font-size: 14px; text-align: center; color: #94a3b8; line-height: 1.75; margin-bottom: 28px; }
.ob-body strong { color: #e2e8f0; }
.ob-tip {
  background: #0d1626; border-radius: 10px; padding: 12px 16px;
  font-size: 12px; color: #64748b; text-align: center;
  margin-bottom: 28px; margin-top: -12px; line-height: 1.6;
}
.ob-tip code { background: #1a2540; border-radius: 4px; padding: 1px 6px; color: #F59E0B; font-family: monospace; }
.ob-dots { display: flex; justify-content: center; gap: 6px; margin-bottom: 24px; }
.ob-dot {
  height: 6px; width: 6px; border-radius: 3px;
  background: #1e2d4a; cursor: pointer;
  transition: width 0.25s, background 0.25s;
}
.ob-dot.active { width: 22px; background: #F59E0B; }
.ob-btns { display: flex; gap: 10px; }
.ob-btn-skip {
  flex: 1; background: transparent; border: 1px solid #1e2d4a;
  color: #64748b; border-radius: 10px; padding: 12px;
  cursor: pointer; font-size: 14px; transition: all 0.2s;
}
.ob-btn-skip:hover { border-color: #334155; color: #94a3b8; }
.ob-btn-next {
  flex: 2; background: linear-gradient(135deg,#F59E0B,#D97706);
  border: none; color: white; border-radius: 10px; padding: 12px;
  cursor: pointer; font-size: 14px; font-weight: 600; transition: filter 0.2s;
}
.ob-btn-next:hover { filter: brightness(1.1); }

/* ── Main content ── */
.main-content {
  flex: 1; display: flex; flex-direction: column;
  height: 100vh; overflow: hidden; min-width: 0;
}
.main-scrollable { flex: 1; overflow-y: auto; }
.main-scrollable::-webkit-scrollbar { width: 4px; }
.main-scrollable::-webkit-scrollbar-track { background: transparent; }
.main-scrollable::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 2px; }

.page-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 24px; border-bottom: 1px solid #1a2540;
  background: #0d1626;
}
.page-header-left { display: flex; align-items: center; gap: 14px; }
.page-hdr-icon {
  width: 46px; height: 46px; background: #1a2540; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0;
}
.page-title h1 { font-size: 20px; font-weight: 700; color: #f1f5f9; }
.page-title p  { font-size: 12px; color: #64748b; margin-top: 2px; }
.reset-btn {
  background: transparent; border: 1px solid #1e2d4a; border-radius: 8px;
  color: #64748b; font-size: 12px; font-weight: 600; padding: 7px 14px;
  cursor: pointer; transition: 0.15s; font-family: inherit;
  display: flex; align-items: center; gap: 5px;
}
.reset-btn:hover { border-color: #F59E0B; color: #F59E0B; }

.keys-section { padding: 20px 24px; }
.keys-section h2 {
  font-size: 11px; font-weight: 700; color: #475569;
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px;
}
.keys-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px;
}

.key-card {
  background: #111e35; border: 1.5px solid #1a2d4a; border-radius: 14px;
  padding: 14px 10px 12px; cursor: pointer; position: relative;
  transition: border-color 0.15s, transform 0.1s, background 0.15s;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  min-height: 108px;
}
.key-card:hover      { border-color: #F59E0B; background: #152238; transform: translateY(-2px); }
.key-card.active-key { border-color: #F59E0B; background: #152238; }
.key-card.empty      { border-style: dashed; border-color: #1a2540; }
.key-num {
  position: absolute; top: 7px; left: 9px;
  font-size: 10px; font-weight: 700; color: #475569;
}
.key-badge {
  position: absolute; top: 5px; right: 7px;
  width: 17px; height: 17px; border-radius: 50%;
  background: #22c55e; display: flex; align-items: center; justify-content: center;
  font-size: 9px; color: white; font-weight: 700;
}
.key-badge.off { background: #1e2d4a; color: #475569; }
.key-icon {
  width: 44px; height: 44px; border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; margin-top: 6px;
}
.key-label { font-size: 10px; font-weight: 600; color: #94a3b8; text-align: center; line-height: 1.3; }

/* Icon colours */
.icon-purple  { background: linear-gradient(135deg,#6d28d9,#8b5cf6); }
.icon-orange  { background: linear-gradient(135deg,#c2410c,#f97316); }
.icon-blue    { background: linear-gradient(135deg,#1d4ed8,#3b82f6); }
.icon-green   { background: linear-gradient(135deg,#065f46,#10b981); }
.icon-red     { background: linear-gradient(135deg,#b91c1c,#ef4444); }
.icon-amber   { background: linear-gradient(135deg,#92400e,#f59e0b); }
.icon-teal    { background: linear-gradient(135deg,#0f766e,#14b8a6); }
.icon-pink    { background: linear-gradient(135deg,#9d174d,#ec4899); }
.icon-indigo  { background: linear-gradient(135deg,#3730a3,#6366f1); }
.icon-dark    { background: linear-gradient(135deg,#1e3a5f,#2563eb); }
.icon-default { background: #1a2540; }

/* ── Tip banner ── */
.tip-banner {
  margin: 0 24px 20px;
  background: linear-gradient(135deg,#111e35,#0d1a2e);
  border: 1px solid #1a2d4a; border-radius: 14px;
  padding: 14px 18px; display: flex; align-items: center; gap: 12px;
}
.tip-star { font-size: 26px; flex-shrink: 0; }
.tip-txt strong { color: #F59E0B; font-size: 13px; }
.tip-txt p { color: #475569; font-size: 11px; margin-top: 2px; }

/* ── Bottom bar ── */
.bottom-bar {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  padding: 14px 24px; border-top: 1px solid #1a2540;
  background: #0d1626; flex-shrink: 0;
}
.save-btn {
  background: linear-gradient(135deg,#F59E0B,#D97706);
  color: #0d1626; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 700; padding: 11px 44px;
  cursor: pointer; transition: opacity 0.15s, transform 0.1s; font-family: inherit;
  display: flex; align-items: center; gap: 7px;
}
.save-btn:hover { opacity: 0.9; transform: scale(1.01); }
.cancel-btn {
  background: transparent; border: 1px solid #1e2d4a; border-radius: 10px;
  color: #64748b; font-size: 14px; font-weight: 600; padding: 11px 24px;
  cursor: pointer; transition: 0.15s; font-family: inherit;
}
.cancel-btn:hover { border-color: #475569; color: #94a3b8; }

/* ── Right panel ── */
.right-panel {
  width: 370px; flex-shrink: 0;
  background: #080f1c; border-left: 1px solid #1a2540;
  display: flex; flex-direction: column; height: 100vh;
  overflow: hidden; max-width: 0;
  transition: max-width 0.3s cubic-bezier(0.4,0,0.2,1);
}
.right-panel.open { max-width: 370px; }

.panel-hdr {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 18px 16px 14px; border-bottom: 1px solid #1a2540; flex-shrink: 0;
}
.panel-key-name { font-size: 17px; font-weight: 700; color: #f1f5f9; }
.panel-sub { font-size: 11px; color: #475569; margin-top: 2px; }
.panel-close {
  background: #111e35; border: none; border-radius: 8px;
  width: 27px; height: 27px; cursor: pointer; color: #64748b; font-size: 15px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.panel-close:hover { background: #1a2540; color: #e2e8f0; }

.panel-search {
  padding: 10px 14px; flex-shrink: 0; position: relative;
}
.panel-search input {
  width: 100%; background: #111e35; border: 1px solid #1a2540;
  border-radius: 10px; color: #e2e8f0; font-size: 13px;
  padding: 8px 52px 8px 34px; font-family: inherit;
}
.panel-search input:focus { outline: none; border-color: #F59E0B; }
.panel-search input::placeholder { color: #334155; }
.srch-ico { position: absolute; left: 26px; top: 50%; transform: translateY(-50%); color: #334155; font-size: 13px; pointer-events: none; }
.srch-kbd {
  position: absolute; right: 26px; top: 50%; transform: translateY(-50%);
  background: #1a2540; border-radius: 4px; padding: 2px 5px;
  font-size: 10px; color: #475569;
}

.panel-tabs {
  display: flex; padding: 0 14px 10px; gap: 5px;
  overflow-x: auto; flex-shrink: 0;
}
.panel-tabs::-webkit-scrollbar { display: none; }
.tab-btn {
  background: transparent; border: 1px solid #1a2540; border-radius: 20px;
  color: #475569; font-size: 11px; font-weight: 600; padding: 5px 12px;
  cursor: pointer; white-space: nowrap; transition: 0.15s; font-family: inherit;
}
.tab-btn:hover { border-color: #F59E0B; color: #F59E0B; }
.tab-btn.active { background: #F59E0B; border-color: #F59E0B; color: #0d1626; }

.panel-body { flex: 1; overflow-y: auto; padding: 0 14px 8px; }
.panel-body::-webkit-scrollbar { width: 3px; }
.panel-body::-webkit-scrollbar-thumb { background: #1a2540; border-radius: 2px; }

.action-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 7px; }

.action-card {
  background: #111e35; border: 1.5px solid transparent; border-radius: 11px;
  padding: 11px 5px; cursor: pointer; display: flex; flex-direction: column;
  align-items: center; gap: 6px; transition: 0.15s; position: relative;
}
.action-card:hover { border-color: #F59E0B; background: #152238; }
.action-card.selected { border-color: #F59E0B; }
.action-card.selected::after {
  content: "✓"; position: absolute; top: 4px; right: 5px;
  width: 15px; height: 15px; background: #F59E0B; border-radius: 50%;
  font-size: 8px; color: #0d1626; font-weight: 900;
  display: flex; align-items: center; justify-content: center;
  line-height: 15px; text-align: center;
}
.action-ico { width: 38px; height: 38px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 19px; }
.action-lbl { font-size: 9.5px; font-weight: 600; color: #94a3b8; text-align: center; line-height: 1.3; }

/* Category grid inside panel */
.cat-grid-p { display: grid; grid-template-columns: repeat(2,1fr); gap: 7px; }
.cat-card-p {
  background: #111e35; border: 1.5px solid #1a2540; border-radius: 11px;
  padding: 12px 10px; cursor: pointer; display: flex; align-items: center;
  gap: 8px; transition: 0.15s;
}
.cat-card-p:hover { border-color: #F59E0B; background: #152238; }
.cat-card-emoji { font-size: 20px; }
.cat-card-name  { font-size: 12px; font-weight: 600; color: #cbd5e1; display: block; }
.cat-card-count { font-size: 10px; color: #475569; display: block; }

.back-row {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 0 10px; color: #475569; cursor: pointer;
  font-size: 12px; font-weight: 600; user-select: none;
}
.back-row:hover { color: #94a3b8; }

.view-all-btn {
  display: flex; align-items: center; justify-content: space-between;
  width: calc(100% - 28px); margin: 6px 14px;
  background: #111e35; border: 1px solid #1a2540; border-radius: 10px;
  color: #64748b; font-size: 12px; font-weight: 600;
  padding: 10px 14px; cursor: pointer; transition: 0.15s; font-family: inherit;
  flex-shrink: 0;
}
.view-all-btn:hover { border-color: #F59E0B; color: #F59E0B; }

/* Action detail bar */
.action-detail {
  padding: 10px 14px; border-top: 1px solid #1a2540;
  display: none; align-items: center; gap: 8px; flex-shrink: 0;
}
.action-detail.show { display: flex; }
.det-icon { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; flex-shrink: 0; }
.det-info { flex: 1; min-width: 0; }
.det-name { font-size: 12px; font-weight: 700; color: #f1f5f9; }
.det-desc { font-size: 10px; color: #475569; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.det-sc {
  background: #111e35; border: 1px solid #1a2540; border-radius: 5px;
  padding: 2px 6px; font-size: 10px; color: #64748b; white-space: nowrap; flex-shrink: 0;
}
.det-fav {
  background: transparent; border: none; cursor: pointer;
  font-size: 16px; color: #334155; transition: color 0.15s; flex-shrink: 0;
}
.det-fav:hover, .det-fav.active { color: #F59E0B; }

/* Empty state */
.empty-state { text-align: center; padding: 28px 12px; color: #334155; font-size: 12px; line-height: 1.6; }
.empty-state .e-ico { font-size: 28px; margin-bottom: 8px; }

/* Custom form */
.custom-tabs { display: flex; gap: 5px; margin-bottom: 12px; }
.ctab-btn {
  flex: 1; padding: 7px; border-radius: 8px; border: 1px solid #1a2540;
  background: #111e35; color: #475569; font-size: 11px; font-weight: 600;
  cursor: pointer; font-family: inherit; transition: 0.15s;
}
.ctab-btn.active { background: #F59E0B; border-color: #F59E0B; color: #0d1626; }
.form-group { margin-bottom: 11px; }
.form-lbl { display: block; font-size: 10px; color: #475569; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 5px; }
.form-inp {
  width: 100%; background: #111e35; border: 1px solid #1a2540;
  border-radius: 8px; color: #e2e8f0; font-size: 12px;
  padding: 9px 11px; font-family: inherit;
}
.form-inp:focus { outline: none; border-color: #F59E0B; }
.form-hint { font-size: 10px; color: #334155; margin-top: 3px; }
.assign-btn {
  width: 100%; background: #F59E0B; color: #0d1626; border: none;
  border-radius: 9px; font-size: 13px; font-weight: 700;
  padding: 10px; cursor: pointer; font-family: inherit; margin-top: 4px;
}
.assign-btn:hover { background: #D97706; }

/* Placeholder sections */
.placeholder-body { padding: 24px; color: #475569; font-size: 13px; }
"""

# ── Static JavaScript ──────────────────────────────────────────────────────────
_JS_STATIC = """
// ── State ──────────────────────────────────────────────────────────────────
let activeKey   = null;
let activeTab   = 'popular';
let activeCat   = null;
let hoveredItem = null;
let searchQ     = '';
let savedState  = null;

let recentActions  = [];
let favoriteLabels = [];
try {
  recentActions  = JSON.parse(localStorage.getItem('pk_recent') || '[]');
  favoriteLabels = JSON.parse(localStorage.getItem('pk_favs')   || '[]');
} catch(e) {}

// ── Category → icon colour ─────────────────────────────────────────────────
const CAT_COLOR = {
  'Everyday':      'icon-purple',
  'Clipboard':     'icon-orange',
  'Documents':     'icon-blue',
  'Internet':      'icon-teal',
  'Email':         'icon-red',
  'Files':         'icon-green',
  'Computer':      'icon-indigo',
  'Media':         'icon-dark',
  'Office':        'icon-blue',
  'Text Snippets': 'icon-amber',
  'AI':            'icon-pink',
  'Custom':        'icon-default',
};

function colorFor(item) {
  if (item && item.colorClass) return item.colorClass;
  for (const [cname, cat] of Object.entries(CATEGORIES)) {
    if (cat.actions && cat.actions.find(a => a.label === item.label))
      return CAT_COLOR[cname] || 'icon-default';
  }
  return 'icon-default';
}

// ── Sidebar navigation ─────────────────────────────────────────────────────
function setSection(name, btn) {
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.querySelectorAll('[id^="sec-"]').forEach(el => el.style.display = 'none');
  const el = document.getElementById('sec-' + name);
  if (el) el.style.display = '';
  const bb = document.getElementById('bottom-bar');
  if (bb) bb.style.display = name === 'fkeys' ? '' : 'none';
  if (name === 'categories') renderCatBrowse();
}

// ── Keyboard render ────────────────────────────────────────────────────────
function getKeyColor(d) {
  if (!d.label) return 'icon-default';
  const pop = POPULAR.find(p => p.label === d.label);
  if (pop) return pop.colorClass;
  return colorFor(d);
}

function renderKeyboard() {
  const grid = document.getElementById('keys-grid');
  if (!grid) return;
  grid.innerHTML = '';
  FKEYS.forEach(fkey => {
    const d   = state[fkey];
    const has = d.action && d.action.type;
    const on  = d.enabled;
    const cc  = has ? getKeyColor(d) : 'icon-default';
    const card = document.createElement('div');
    card.className = 'key-card' + (has ? '' : ' empty') + (activeKey === fkey ? ' active-key' : '');
    card.innerHTML =
      '<span class="key-num">' + fkey + '</span>' +
      '<span class="key-badge ' + (on ? '' : 'off') + '">' + (on ? '✓' : '') + '</span>' +
      '<div class="key-icon ' + cc + '">' + (d.emoji || (has ? '⚡' : '+')) + '</div>' +
      '<span class="key-label">' + (d.label || 'Empty') + '</span>';
    card.onclick = () => openPanel(fkey);
    grid.appendChild(card);
  });
}

// ── Panel open/close ───────────────────────────────────────────────────────
function openPanel(fkey) {
  activeKey = fkey;
  document.getElementById('panel-key-name').textContent = 'Setting ' + fkey;
  document.getElementById('right-panel').classList.add('open');
  document.getElementById('panel-search').value = '';
  searchQ = ''; activeCat = null;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const pt = document.getElementById('tab-popular');
  if (pt) pt.classList.add('active');
  activeTab = 'popular';
  renderPanelBody();
  renderKeyboard();
  hideDetail();
}

function closePanel() {
  document.getElementById('right-panel').classList.remove('open');
  activeKey = null;
  renderKeyboard();
  hideDetail();
}

// ── Tabs ───────────────────────────────────────────────────────────────────
function setTab(tab) {
  activeTab = tab; activeCat = null; searchQ = '';
  document.getElementById('panel-search').value = '';
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const el = document.getElementById('tab-' + tab);
  if (el) el.classList.add('active');
  document.getElementById('view-all-btn').style.display = tab === 'popular' ? '' : 'none';
  renderPanelBody();
}

// ── Panel body render ──────────────────────────────────────────────────────
function renderPanelBody() {
  const body = document.getElementById('panel-body');
  if (!body) return;

  if (searchQ) { renderSearch(searchQ); return; }

  if (activeTab === 'popular') {
    body.innerHTML = '<div class="action-grid" id="action-grid"></div>';
    renderActionGrid(document.getElementById('action-grid'), POPULAR);
    return;
  }
  if (activeTab === 'all') {
    if (!activeCat) { renderCatPicker(body); }
    else             { renderCatActions(body, activeCat); }
    return;
  }
  if (activeTab === 'recent') {
    body.innerHTML = '<div class="action-grid" id="action-grid"></div>';
    if (!recentActions.length) {
      body.innerHTML = '<div class="empty-state"><div class="e-ico">🕐</div>No recent actions yet.</div>';
    } else {
      renderActionGrid(document.getElementById('action-grid'), recentActions);
    }
    return;
  }
  if (activeTab === 'favorites') {
    const favs = [];
    Object.values(CATEGORIES).forEach(cat => {
      (cat.actions || []).forEach(a => { if (favoriteLabels.includes(a.label)) favs.push(a); });
    });
    POPULAR.forEach(a => { if (favoriteLabels.includes(a.label) && !favs.find(f => f.label === a.label)) favs.push(a); });
    body.innerHTML = '<div class="action-grid" id="action-grid"></div>';
    if (!favs.length) {
      body.innerHTML = '<div class="empty-state"><div class="e-ico">♥</div>No favourites yet.<br>Hover an action and click ☆ to save it.</div>';
    } else {
      renderActionGrid(document.getElementById('action-grid'), favs);
    }
    return;
  }
}

// ── Category picker (inside panel) ────────────────────────────────────────
function renderCatPicker(container) {
  let html = '<div class="cat-grid-p">';
  Object.entries(CATEGORIES).forEach(([name, cat]) => {
    const count = cat.custom ? 'Custom' : (cat.actions || []).length + ' actions';
    // Use data attribute to avoid any quote-escaping in onclick
    html += '<div class="cat-card-p" data-catname="' + encodeURIComponent(name) + '">'
          + '<span class="cat-card-emoji">' + cat.emoji + '</span>'
          + '<div><span class="cat-card-name">' + name + '</span>'
          + '<span class="cat-card-count">' + count + '</span></div></div>';
  });
  html += '</div>';
  container.innerHTML = html;
  // Attach handlers after render — no inline onclick needed
  container.querySelectorAll('[data-catname]').forEach(card => {
    card.onclick = () => openCat(decodeURIComponent(card.dataset.catname));
  });
}

function openCat(catName) {
  activeCat = catName;
  renderCatActions(document.getElementById('panel-body'), catName);
}

function renderCatActions(container, catName) {
  const cat = CATEGORIES[catName];
  if (!cat) return;
  if (cat.custom) { renderCustomForm(container); return; }
  container.innerHTML =
    '<div class="back-row" id="back-row-el">&#8592; ' + catName + '</div>'
    + '<div class="action-grid" id="action-grid"></div>';
  const br = document.getElementById('back-row-el');
  if (br) br.onclick = goBackCats;
  renderActionGrid(document.getElementById('action-grid'), cat.actions);
}

function goBackCats() {
  activeCat = null;
  renderCatPicker(document.getElementById('panel-body'));
}

// ── Action grid ────────────────────────────────────────────────────────────
function renderActionGrid(container, items) {
  if (!container) return;
  const curLabel = activeKey ? state[activeKey].label : '';
  container.innerHTML = '';
  (items || []).forEach(item => {
    if (!item || !item.label) return;
    const cc   = colorFor(item);
    const card = document.createElement('div');
    card.className  = 'action-card' + (item.label === curLabel ? ' selected' : '');
    card.dataset.lbl = item.label;
    card.innerHTML   =
      '<div class="action-ico ' + cc + '">' + item.emoji + '</div>'
      + '<span class="action-lbl">' + item.label + '</span>';
    if (item.custom) {
      card.onclick = () => {
        // Navigate to the Custom category form
        setTab('all');
        activeCat = 'Custom';
        renderCatActions(document.getElementById('panel-body'), 'Custom');
      };
    } else {
      card.onclick = () => assignAction(item);
    }
    card.onmouseenter = () => showDetail(item, cc);
    container.appendChild(card);
  });
  // Clear key button
  const clr = document.createElement('div');
  clr.className   = 'action-card';
  clr.innerHTML   = '<div class="action-ico icon-default">🚫</div><span class="action-lbl">Clear Key</span>';
  clr.onclick     = clearKey;
  container.appendChild(clr);
}

// ── Assign / Clear ─────────────────────────────────────────────────────────
function assignAction(item) {
  if (!activeKey) return;
  state[activeKey] = { key: activeKey, label: item.label, emoji: item.emoji, action: item.action, enabled: true };
  recentActions = [item, ...recentActions.filter(r => r.label !== item.label)].slice(0, 20);
  try { localStorage.setItem('pk_recent', JSON.stringify(recentActions)); } catch(e) {}
  renderKeyboard();
  // re-highlight in grid
  document.querySelectorAll('.action-card').forEach(c => {
    c.classList.toggle('selected', c.dataset.lbl === item.label);
  });
}

function clearKey() {
  if (!activeKey) return;
  state[activeKey] = { key: activeKey, label: '', emoji: '', action: {}, enabled: false };
  renderKeyboard();
  document.querySelectorAll('.action-card').forEach(c => c.classList.remove('selected'));
  hideDetail();
}

// ── Detail bar ─────────────────────────────────────────────────────────────
function showDetail(item, cc) {
  hoveredItem = item;
  const det = document.getElementById('action-detail');
  det.className = 'action-detail show';
  document.getElementById('det-icon').className = 'det-icon ' + (cc || 'icon-default');
  document.getElementById('det-icon').textContent = item.emoji;
  document.getElementById('det-name').textContent = item.label;
  document.getElementById('det-desc').textContent = item.desc || actionDesc(item);
  const sc = document.getElementById('det-sc');
  const hint = item.shortcutHint || (item.action && item.action.shortcut ? fmtSC(item.action.shortcut) : '');
  sc.textContent = hint; sc.style.display = hint ? '' : 'none';
  const fb = document.getElementById('det-fav');
  const isFav = favoriteLabels.includes(item.label);
  fb.textContent = isFav ? '★' : '☆';
  fb.className = 'det-fav' + (isFav ? ' active' : '');
}

function hideDetail() {
  const det = document.getElementById('action-detail');
  if (det) det.className = 'action-detail';
  hoveredItem = null;
}

function actionDesc(item) {
  if (!item.action) return '';
  switch (item.action.type) {
    case 'shortcut':    return 'Shortcut: ' + fmtSC(item.action.shortcut);
    case 'run_command': return item.action.command;
    case 'media_key':   return 'Media: ' + item.action.key;
    case 'type_text':   return 'Types: ' + item.action.text;
    default: return '';
  }
}

function fmtSC(sc) {
  return (sc || '').replace('cmd','⌘').replace('shift','⇧').replace('ctrl','⌃').replace('alt','⌥').replace(/\+/g,' ');
}

function toggleDetailFav() {
  if (!hoveredItem) return;
  const lbl = hoveredItem.label;
  const idx = favoriteLabels.indexOf(lbl);
  if (idx >= 0) favoriteLabels.splice(idx, 1);
  else          favoriteLabels.push(lbl);
  try { localStorage.setItem('pk_favs', JSON.stringify(favoriteLabels)); } catch(e) {}
  showDetail(hoveredItem, colorFor(hoveredItem));
}

// ── Search ─────────────────────────────────────────────────────────────────
function onSearch(q) {
  searchQ = q;
  document.getElementById('view-all-btn').style.display = 'none';
  if (!q.trim()) {
    renderPanelBody();
    if (activeTab === 'popular') document.getElementById('view-all-btn').style.display = '';
    return;
  }
  renderSearch(q);
}

function renderSearch(q) {
  const ql = q.toLowerCase();
  const results = [];
  Object.values(CATEGORIES).forEach(cat => {
    (cat.actions || []).forEach(a => {
      if (a.label.toLowerCase().includes(ql) && !results.find(r => r.label === a.label))
        results.push(a);
    });
  });
  const body = document.getElementById('panel-body');
  body.innerHTML = '<div class="action-grid" id="action-grid"></div>';
  if (results.length) {
    renderActionGrid(document.getElementById('action-grid'), results);
  } else {
    body.innerHTML = '<div class="empty-state"><div class="e-ico">🔍</div>No results for "' + q + '"</div>';
  }
}

// ── Custom form ────────────────────────────────────────────────────────────
let customTab = 'shortcut';

function renderCustomForm(container) {
  container.innerHTML =
    '<div class="back-row" id="custom-back-el">&#8592; Custom</div>'
    + '<div class="custom-tabs" id="custom-tabs-el">'
    + '<button class="ctab-btn active" data-tab="shortcut">&#9000; Shortcut</button>'
    + '<button class="ctab-btn" data-tab="text">&#9998; Text</button>'
    + '<button class="ctab-btn" data-tab="app">&#128640; App/URL</button>'
    + '</div><div id="ctab-content"></div>';
  const cb = document.getElementById('custom-back-el');
  if (cb) cb.onclick = goBackCats;
  document.querySelectorAll('#custom-tabs-el .ctab-btn').forEach(btn => {
    btn.onclick = () => setCtab(btn.dataset.tab, btn);
  });
  renderCtabContent('shortcut');
}

function setCtab(tab, btn) {
  customTab = tab;
  document.querySelectorAll('#custom-tabs-el .ctab-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderCtabContent(tab);
}

function renderCtabContent(tab) {
  const c = document.getElementById('ctab-content');
  if (!c) return;
  if (tab === 'shortcut') {
    c.innerHTML =
      '<div class="form-group"><label class="form-lbl">Label</label><input class="form-inp" id="c-lbl" placeholder="e.g. My Shortcut"></div>'
      + '<div class="form-group"><label class="form-lbl">Shortcut</label><input class="form-inp" id="c-sc" placeholder="e.g. cmd+shift+k"><p class="form-hint">Use: cmd  ctrl  shift  alt + key</p></div>'
      + '<button class="assign-btn" id="c-assign">Assign to Key</button>';
  } else if (tab === 'text') {
    c.innerHTML =
      '<div class="form-group"><label class="form-lbl">Label</label><input class="form-inp" id="c-lbl" placeholder="e.g. My Signature"></div>'
      + '<div class="form-group"><label class="form-lbl">Text to type</label><textarea class="form-inp" id="c-txt" rows="4" placeholder="Any text..." style="resize:vertical"></textarea><p class="form-hint">Use {DATE} and {TIME} as placeholders</p></div>'
      + '<button class="assign-btn" id="c-assign">Assign to Key</button>';
  } else {
    c.innerHTML =
      '<div class="form-group"><label class="form-lbl">Label</label><input class="form-inp" id="c-lbl" placeholder="e.g. Open Chrome"></div>'
      + '<div class="form-group"><label class="form-lbl">App name or URL</label><input class="form-inp" id="c-app" placeholder="e.g. Spotify  or  https://mysite.com"><p class="form-hint">App name or full URL</p></div>'
      + '<button class="assign-btn" id="c-assign">Assign to Key</button>';
  }
  // Attach handler via JS — avoids any quote-escaping in innerHTML
  const ab = document.getElementById('c-assign');
  if (ab) ab.onclick = () => doCustom(tab);
}

function doCustom(type) {
  if (!activeKey) return;
  const lbl = (document.getElementById('c-lbl') || {}).value?.trim() || 'Custom';
  let emoji = '⌨️', action;
  if (type === 'shortcut') {
    const sc = (document.getElementById('c-sc') || {}).value?.trim();
    if (!sc) { alert('Please enter a shortcut.'); return; }
    action = { type: 'shortcut', shortcut: sc };
  } else if (type === 'text') {
    const t = (document.getElementById('c-txt') || {}).value;
    if (!t) { alert('Please enter some text.'); return; }
    emoji = '✏️'; action = { type: 'type_text', text: t };
  } else {
    const app = (document.getElementById('c-app') || {}).value?.trim();
    if (!app) { alert('Please enter an app name or URL.'); return; }
    emoji = '🚀';
    const cmd = app.startsWith('http') ? 'open ' + app : 'open -a "' + app + '"';
    action = { type: 'run_command', command: cmd };
  }
  state[activeKey] = { key: activeKey, label: lbl, emoji, action, enabled: true };
  renderKeyboard();
  closePanel();
}

// ── Categories browse section ──────────────────────────────────────────────
function renderCatBrowse() {
  const c = document.getElementById('cat-browse');
  if (!c) return;
  let html = '<div class="cat-grid-p" style="grid-template-columns:repeat(3,1fr)">';
  Object.entries(CATEGORIES).forEach(([name, cat]) => {
    const count = cat.custom ? '' : (cat.actions || []).length + ' actions';
    html += '<div class="cat-card-p"><span class="cat-card-emoji">' + cat.emoji + '</span>'
          + '<div><span class="cat-card-name">' + name + '</span>'
          + '<span class="cat-card-count">' + count + '</span></div></div>';
  });
  html += '</div>';
  c.innerHTML = html;
}

// ── Save / Cancel / Reset ──────────────────────────────────────────────────
function saveAll() {
  const mappings = Object.values(state).filter(d => d.action && d.action.type);
  savedState = JSON.stringify(state);
  fetch('/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mappings })
  }).then(r => r.json()).then(data => {
    if (data.ok) {
      const btn = document.querySelector('.save-btn');
      const orig = btn.innerHTML;
      btn.innerHTML = '✓ Saved!';
      btn.style.background = 'linear-gradient(135deg,#22c55e,#16a34a)';
      setTimeout(() => { btn.innerHTML = orig; btn.style.background = ''; }, 2000);
    }
  }).catch(() => alert('Save failed. Is Pratikey running?'));
}

function cancelChanges() {
  if (savedState) { state = JSON.parse(savedState); renderKeyboard(); }
  closePanel();
}

function resetAll() {
  if (!confirm('Reset all F-keys to empty?')) return;
  FKEYS.forEach(fkey => { state[fkey] = { key: fkey, label: '', emoji: '', action: {}, enabled: false }; });
  renderKeyboard(); closePanel();
}

// ── Onboarding ─────────────────────────────────────────────────────────────
var obSlide = 0;
var OB_TOTAL = 5;

function showOnboarding() {
  obSlide = 0;
  renderObSlide();
  document.getElementById('ob-overlay').classList.add('show');
}

function hideOnboarding() {
  document.getElementById('ob-overlay').classList.remove('show');
  try { localStorage.setItem('pk_welcomed', '1'); } catch(e) {}
}

function nextSlide() {
  if (obSlide < OB_TOTAL - 1) {
    obSlide++;
    renderObSlide();
  } else {
    hideOnboarding();
  }
}

function goToSlide(n) {
  obSlide = n;
  renderObSlide();
}

function renderObSlide() {
  for (var i = 0; i < OB_TOTAL; i++) {
    var el = document.getElementById('ob-slide-' + i);
    if (el) el.classList.toggle('active', i === obSlide);
  }
  document.querySelectorAll('.ob-dot').forEach(function(d, i) {
    d.classList.toggle('active', i === obSlide);
  });
  var btn = document.getElementById('ob-next');
  if (btn) btn.innerHTML = (obSlide === OB_TOTAL - 1) ? "Let&#39;s go! &#127881;" : 'Next &#8594;';
  var skip = document.getElementById('ob-skip');
  if (skip) skip.style.display = (obSlide === OB_TOTAL - 1) ? 'none' : '';
}

// ── Init ───────────────────────────────────────────────────────────────────
function init() {
  savedState = JSON.stringify(state);
  renderKeyboard();
  // Show onboarding on first ever visit
  try {
    if (!localStorage.getItem('pk_welcomed')) showOnboarding();
  } catch(e) {}
}
init();
"""

# ── HTML template ──────────────────────────────────────────────────────────────
_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pratikey — Settings</title>
<style>/*CSS*/</style>
</head>
<body>
<div class="app-shell">

  <!-- ── Left Sidebar ── -->
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-icon">P</div>
      <div>
        <div class="logo-name">Pratikey</div>
        <div class="logo-tag">One key. Endless possibilities.</div>
      </div>
    </div>
    <nav class="sidebar-nav">
      <button class="nav-item active" onclick="setSection('fkeys',this)">
        <span class="nav-icon">⌨️</span>
        <span><span class="nav-title">F-Keys</span><span class="nav-sub">Customize your F-keys</span></span>
      </button>
      <button class="nav-item" onclick="setSection('categories',this)">
        <span class="nav-icon">⊞</span>
        <span><span class="nav-title">Categories</span><span class="nav-sub">Browse all actions</span></span>
      </button>
      <button class="nav-item" onclick="setSection('snippets',this)">
        <span class="nav-icon">✏️</span>
        <span><span class="nav-title">Text Snippets</span><span class="nav-sub">Your saved snippets</span></span>
      </button>
      <button class="nav-item" onclick="setSection('prefs',this)">
        <span class="nav-icon">⚙️</span>
        <span><span class="nav-title">Settings</span><span class="nav-sub">General preferences</span></span>
      </button>
      <button class="nav-item" onclick="setSection('backup',this)">
        <span class="nav-icon">☁️</span>
        <span><span class="nav-title">Backup &amp; Restore</span><span class="nav-sub">Import or export</span></span>
      </button>
      <button class="nav-item" onclick="setSection('about',this)">
        <span class="nav-icon">ℹ️</span>
        <span><span class="nav-title">About</span><span class="nav-sub">App information</span></span>
      </button>
    </nav>
    <div class="tips-box">
      <div class="tips-head"><span>💡</span><strong>Tips</strong></div>
      <div class="tips-body">Hover over any key to quickly see what it does.</div>
      <button class="quick-guide-btn" onclick="showOnboarding()">&#128218; View Quick Guide</button>
    </div>
  </aside>

  <!-- ── Main Content ── -->
  <main class="main-content">
    <div class="main-scrollable">

      <!-- F-Keys section -->
      <div id="sec-fkeys">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">⌨️</div>
            <div class="page-title">
              <h1>F-Key Settings</h1>
              <p>Click any key below to change what it does — no shortcuts needed!</p>
            </div>
          </div>
          <button class="reset-btn" onclick="resetAll()">↺ Reset All</button>
        </div>
        <div class="keys-section">
          <h2>Your F-Keys</h2>
          <div class="keys-grid" id="keys-grid"></div>
        </div>
        <div class="tip-banner">
          <span class="tip-star">⭐</span>
          <div class="tip-txt">
            <strong>Tip:</strong> Click any key to instantly assign an action from 100+ presets!
            <p>Make your keyboard work exactly the way you want.</p>
          </div>
        </div>
      </div>

      <!-- Categories section -->
      <div id="sec-categories" style="display:none">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">⊞</div>
            <div class="page-title"><h1>Categories</h1><p>Browse all available actions</p></div>
          </div>
        </div>
        <div class="placeholder-body" id="cat-browse"></div>
      </div>

      <!-- Other sections -->
      <div id="sec-snippets" style="display:none">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">✏️</div>
            <div class="page-title"><h1>Text Snippets</h1><p>Your saved text snippets</p></div>
          </div>
        </div>
        <div class="placeholder-body">Text Snippets section coming soon.</div>
      </div>
      <div id="sec-prefs" style="display:none">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">⚙️</div>
            <div class="page-title"><h1>Settings</h1><p>General preferences</p></div>
          </div>
        </div>
        <div class="placeholder-body">Settings section coming soon.</div>
      </div>
      <div id="sec-backup" style="display:none">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">☁️</div>
            <div class="page-title"><h1>Backup &amp; Restore</h1><p>Import or export your configuration</p></div>
          </div>
        </div>
        <div class="placeholder-body">Backup &amp; Restore coming soon.</div>
      </div>
      <div id="sec-about" style="display:none">
        <div class="page-header">
          <div class="page-header-left">
            <div class="page-hdr-icon">ℹ️</div>
            <div class="page-title"><h1>About Pratikey</h1><p>App information</p></div>
          </div>
        </div>
        <div class="placeholder-body" style="color:#94a3b8">
          <p style="font-size:16px;font-weight:700">Pratikey v1.0.0</p>
          <p style="margin-top:6px;color:#475569">One key. Endless possibilities.</p>
        </div>
      </div>

    </div><!-- end .main-scrollable -->

    <!-- Bottom bar (Save / Cancel) -->
    <div class="bottom-bar" id="bottom-bar">
      <button class="save-btn" onclick="saveAll()">✓ Save &amp; Apply</button>
      <button class="cancel-btn" onclick="cancelChanges()">Cancel</button>
    </div>
  </main>

  <!-- ── Right Panel ── -->
  <aside class="right-panel" id="right-panel">
    <div class="panel-hdr">
      <div>
        <div class="panel-key-name" id="panel-key-name">Setting F1</div>
        <div class="panel-sub">Choose what this key does</div>
      </div>
      <button class="panel-close" onclick="closePanel()">✕</button>
    </div>

    <div class="panel-search">
      <span class="srch-ico">🔍</span>
      <input type="text" id="panel-search" placeholder="Search actions..." oninput="onSearch(this.value)">
      <span class="srch-kbd">⌘F</span>
    </div>

    <div class="panel-tabs">
      <button class="tab-btn active" id="tab-popular"   onclick="setTab('popular')">⭐ Popular</button>
      <button class="tab-btn"        id="tab-all"        onclick="setTab('all')">All Categories</button>
      <button class="tab-btn"        id="tab-recent"     onclick="setTab('recent')">🕐 Recent</button>
      <button class="tab-btn"        id="tab-favorites"  onclick="setTab('favorites')">♥ Favourites</button>
    </div>

    <div class="panel-body" id="panel-body">
      <div class="action-grid" id="action-grid"></div>
    </div>

    <button class="view-all-btn" id="view-all-btn" onclick="setTab('all')">
      View All Categories <span>›</span>
    </button>

    <div class="action-detail" id="action-detail">
      <div class="det-icon icon-default" id="det-icon"></div>
      <div class="det-info">
        <div class="det-name" id="det-name"></div>
        <div class="det-desc" id="det-desc"></div>
      </div>
      <div class="det-sc" id="det-sc" style="display:none"></div>
      <button class="det-fav" id="det-fav" onclick="toggleDetailFav()">☆</button>
    </div>
  </aside>

<!-- ── Onboarding overlay ────────────────────────────────────── -->
<div class="ob-overlay" id="ob-overlay">
  <div class="ob-card">
    <button class="ob-close" onclick="hideOnboarding()">&#x2715;</button>

    <!-- Slide 0: Welcome -->
    <div class="ob-slide active" id="ob-slide-0">
      <div class="ob-illo">&#128273;</div>
      <div class="ob-step">Welcome</div>
      <div class="ob-title">Welcome to Pratikey</div>
      <div class="ob-body">Your F-keys, your rules.<br>This quick guide gets you set up in under a minute.</div>
    </div>

    <!-- Slide 1: Click an F-key -->
    <div class="ob-slide" id="ob-slide-1">
      <div class="ob-illo">&#9000;</div>
      <div class="ob-step">Step 1 of 4</div>
      <div class="ob-title">Click any F-Key</div>
      <div class="ob-body">You have <strong>12 programmable keys</strong> on the grid.<br>Click any key card to open the action picker on the right side.</div>
    </div>

    <!-- Slide 2: Choose an action -->
    <div class="ob-slide" id="ob-slide-2">
      <div class="ob-illo">&#9889;</div>
      <div class="ob-step">Step 2 of 4</div>
      <div class="ob-title">Pick an Action</div>
      <div class="ob-body">Choose from <strong>100+ built-in actions</strong> — shortcuts, media controls, text snippets, apps and websites.<br>Or create a fully custom action.</div>
    </div>

    <!-- Slide 3: Save -->
    <div class="ob-slide" id="ob-slide-3">
      <div class="ob-illo">&#128190;</div>
      <div class="ob-step">Step 3 of 4</div>
      <div class="ob-title">Save &amp; Apply</div>
      <div class="ob-body">Hit the orange <strong>Save &amp; Apply</strong> button at the bottom of the screen.<br>Your keys activate <strong>instantly</strong> — no restart needed.</div>
    </div>

    <!-- Slide 4: Accessibility -->
    <div class="ob-slide" id="ob-slide-4">
      <div class="ob-illo">&#128737;</div>
      <div class="ob-step">Step 4 of 4</div>
      <div class="ob-title">Grant One Permission</div>
      <div class="ob-body">For Pratikey to detect your F-keys, grant Accessibility access.</div>
      <div class="ob-tip">
        &#8594; <strong>System Settings</strong> &#8594; <strong>Privacy &amp; Security</strong><br>
        &#8594; <strong>Accessibility</strong> &#8594; add <code>Pratikey</code><br>
        You only need to do this once.
      </div>
    </div>

    <div class="ob-dots" id="ob-dots">
      <div class="ob-dot active"  onclick="goToSlide(0)"></div>
      <div class="ob-dot"         onclick="goToSlide(1)"></div>
      <div class="ob-dot"         onclick="goToSlide(2)"></div>
      <div class="ob-dot"         onclick="goToSlide(3)"></div>
      <div class="ob-dot"         onclick="goToSlide(4)"></div>
    </div>

    <div class="ob-btns">
      <button class="ob-btn-skip" id="ob-skip" onclick="hideOnboarding()">Skip</button>
      <button class="ob-btn-next" id="ob-next" onclick="nextSlide()">Next &#8594;</button>
    </div>
  </div>
</div>

</div><!-- end .app-shell -->

<script>
/*JS_DATA*/
/*JS_STATIC*/
</script>
</body>
</html>"""


# ── Build HTML ─────────────────────────────────────────────────────────────────
def build_html(cfg):
    mappings_by_key = {m["key"]: m for m in cfg.get("mappings", [])}
    parts = []
    for fkey in FKEYS:
        m = mappings_by_key.get(fkey, {})
        entry = {
            "key":     fkey,
            "label":   m.get("label", ""),
            "emoji":   m.get("emoji", ""),
            "action":  m.get("action", {}),
            "enabled": m.get("enabled", False),
        }
        parts.append(f'"{fkey}": {json.dumps(entry)}')
    current_js = "{\n  " + ",\n  ".join(parts) + "\n}"

    injected = (
        ACTIONS_JS + "\n"
        + POPULAR_ACTIONS_JS + "\n"
        + f"const FKEYS = {json.dumps(FKEYS)};\n"
        + f"let state = {current_js};\n"
    )

    html = _HTML
    html = html.replace("/*CSS*/",       _CSS)
    html = html.replace("/*JS_DATA*/",   injected)
    html = html.replace("/*JS_STATIC*/", _JS_STATIC)
    return html


# ── HTTP handler ───────────────────────────────────────────────────────────────
_engine_reload_callback = None

class SettingsHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        try:
            cfg  = json.loads(CONFIG_PATH.read_text())
            html = build_html(cfg).encode()
            self._send(200, "text/html; charset=utf-8", html)
        except Exception as e:
            self._send(500, "text/html", f"<pre>{e}</pre>".encode())

    def do_POST(self):
        if self.path != "/save":
            self._send(404, "text/plain", b"Not found"); return
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length))
        cfg    = json.loads(CONFIG_PATH.read_text())
        cfg["mappings"] = body.get("mappings", [])
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
        if _engine_reload_callback:
            _engine_reload_callback()
        self._send(200, "application/json", json.dumps({"ok": True}).encode())

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


_server = None
_server_thread = None

def start_server(engine_reload_callback=None):
    global _server, _server_thread, _engine_reload_callback
    _engine_reload_callback = engine_reload_callback
    if _server is not None: return
    _server = HTTPServer(("127.0.0.1", PORT), SettingsHandler)
    _server_thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _server_thread.start()
    print(f"[Pratikey] Settings server: http://127.0.0.1:{PORT}")

def open_settings():
    webbrowser.open(f"http://127.0.0.1:{PORT}")

def stop_server():
    global _server
    if _server:
        _server.shutdown()
        _server = None

if __name__ == "__main__":
    start_server()
    open_settings()
    input("Press Enter to stop...\n")
    stop_server()
