"""
Pratikey — Floating F-Key HUD
Platform-aware overlay bar showing current F-key → action mappings.
  macOS  — NSWindow via AppKit, anchored just above the dock
  Windows — tkinter borderless window, anchored at bottom of screen
"""

import json
import sys
import threading
from pathlib import Path


# ── Windows HUD (tkinter) ─────────────────────────────────────────────────────

class _FKeyHUDWindows:
    BAR_HEIGHT = 32

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.visible     = False
        self._root       = None
        self._frame      = None
        self._thread     = None

    def show(self):
        self.visible = True
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_tk, daemon=True)
            self._thread.start()
        elif self._root:
            self._root.after(0, self._root.deiconify)

    def hide(self):
        self.visible = False
        if self._root:
            self._root.after(0, self._root.withdraw)

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()
        return self.visible

    def update(self):
        if self._root and self.visible:
            self._root.after(0, self._do_refresh)

    def _run_tk(self):
        try:
            import tkinter as tk
            self._root = tk.Tk()
            self._root.overrideredirect(True)   # no title bar / border
            self._root.attributes('-topmost', True)
            self._root.configure(bg='#1a0d01')

            sw = self._root.winfo_screenwidth()
            sh = self._root.winfo_screenheight()
            self._root.geometry(f'{sw}x{self.BAR_HEIGHT}+0+{sh - self.BAR_HEIGHT}')

            self._frame = tk.Frame(self._root, bg='#1a0d01')
            self._frame.pack(fill='both', expand=True)

            self._do_refresh()
            self._root.mainloop()
        except Exception as e:
            print(f'[HUD-Win] error: {e}')

    def _do_refresh(self):
        if not self._frame:
            return
        for w in self._frame.winfo_children():
            w.destroy()

        mappings = self._load_mappings()
        bg = '#1a0d01'

        if not mappings:
            import tkinter as tk
            tk.Label(self._frame, text='No F-key mappings configured',
                     fg='#666', bg=bg, font=('Segoe UI', 9)).pack(expand=True)
            return

        import tkinter as tk
        for i, (fkey, label) in enumerate(mappings):
            if i > 0:
                tk.Label(self._frame, text='|', fg='#444', bg=bg,
                         font=('Segoe UI', 9)).pack(side='left', padx=2)
            tk.Label(self._frame, text=fkey, fg='#F59E0B', bg=bg,
                     font=('Consolas', 9, 'bold')).pack(side='left', padx=(6, 0))
            tk.Label(self._frame, text=' → ', fg='#555', bg=bg,
                     font=('Segoe UI', 9)).pack(side='left')
            tk.Label(self._frame, text=label, fg='#EEEEEE', bg=bg,
                     font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))

    def _load_mappings(self):
        try:
            cfg = json.loads(self.config_path.read_text())
            return [(m['key'], m['label']) for m in cfg.get('mappings', [])
                    if m.get('enabled', True) and m.get('label', '').strip()]
        except Exception:
            return []


# ── macOS HUD (AppKit NSWindow) ───────────────────────────────────────────────

class _FKeyHUDMac:
    """
    Floating heads-up display for F-key mappings.

    All public methods (show/hide/toggle/update) MUST be called on the
    AppKit main thread — use AppHelper.callLater() from other threads.
    """

    BAR_HEIGHT = 32   # points

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self._panel  = None
        self._screen_width = 1440
        self.visible = False

    # ── Public API ────────────────────────────────────────────────────────────

    def show(self):
        """Show the HUD bar (main thread only)."""
        self.visible = True
        self._init_panel()
        self._refresh()
        if self._panel:
            self._panel.orderFrontRegardless()
            print(f"[HUD] Shown. isVisible={self._panel.isVisible()}")

    def hide(self):
        """Hide the HUD bar (main thread only)."""
        self.visible = False
        if self._panel:
            self._panel.orderOut_(None)

    def toggle(self):
        """Toggle visibility. Returns new visible state."""
        if self.visible:
            self.hide()
        else:
            self.show()
        return self.visible

    def update(self):
        """Re-read config and refresh labels (main thread only)."""
        if self._panel and self.visible:
            self._refresh()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _load_mappings(self):
        """Return [(fkey, label), ...] for enabled mappings that have a label."""
        try:
            cfg = json.loads(self.config_path.read_text())
            return [
                (m["key"], m["label"])
                for m in cfg.get("mappings", [])
                if m.get("enabled", True) and m.get("label", "").strip()
            ]
        except Exception:
            return []

    def _init_panel(self):
        if self._panel is not None:
            return
        try:
            import AppKit

            screen = AppKit.NSScreen.mainScreen()
            if screen is None:
                print("[HUD] No main screen found")
                return

            sf = screen.frame()         # full screen (includes menu bar)
            vf = screen.visibleFrame()  # below menu bar, above dock

            # visible_top = bottom of menu bar (highest Y in visible area)
            visible_top = vf.origin.y + vf.size.height
            w = sf.size.width

            print(f"[HUD] sf={sf}  vf={vf}  visible_top={visible_top}  w={w}")

            # Create window with placeholder frame (position set below via setFrameTopLeftPoint_)
            init_frame = AppKit.NSMakeRect(0, 0, w, self.BAR_HEIGHT)

            win = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                init_frame,
                AppKit.NSWindowStyleMaskBorderless,
                AppKit.NSBackingStoreBuffered,
                False,
            )

            win.setLevel_(3)   # NSFloatingWindowLevel — above all normal windows
            win.setBackgroundColor_(
                AppKit.NSColor.colorWithRed_green_blue_alpha_(0.10, 0.07, 0.02, 1.0)
            )
            win.setOpaque_(True)
            win.setHasShadow_(False)
            win.setIgnoresMouseEvents_(True)
            win.setCollectionBehavior_(
                1    # NSWindowCollectionBehaviorCanJoinAllSpaces
                | 16  # NSWindowCollectionBehaviorStationary
                | 64  # NSWindowCollectionBehaviorIgnoresCycle
            )

            # Position at BOTTOM of visible area (just above the dock).
            # setFrameTopLeftPoint_ sets the TOP-LEFT corner, so top = dock_top + bar_height.
            dock_top = vf.origin.y   # top of dock = bottom of visible area
            win.setFrameTopLeftPoint_(AppKit.NSMakePoint(sf.origin.x, dock_top + self.BAR_HEIGHT))
            print(f"[HUD] Set top-left to ({sf.origin.x}, {visible_top})  final frame={win.frame()}")

            self._panel = win
            self._screen_width = w
            print("[HUD] NSWindow created OK")

        except Exception as e:
            import traceback
            print(f"[HUD] init error: {e}")
            traceback.print_exc()

    def _refresh(self):
        """Rebuild all NSTextField subviews from the current config."""
        if not self._panel:
            return
        try:
            import AppKit

            content = self._panel.contentView()
            for sv in list(content.subviews()):
                sv.removeFromSuperview()

            mappings = self._load_mappings()
            W = self._screen_width
            H = self.BAR_HEIGHT

            ORANGE = AppKit.NSColor.colorWithRed_green_blue_alpha_(0.96, 0.62, 0.04, 1.0)
            WHITE  = AppKit.NSColor.colorWithWhite_alpha_(0.94, 1.0)
            DIM    = AppKit.NSColor.colorWithWhite_alpha_(0.40, 1.0)

            print(f"[HUD] Refreshing with {len(mappings)} mappings, W={W}")

            if not mappings:
                tf = self._make_label(
                    "Open Pratikey Settings to configure your F-keys",
                    DIM, 10.5, AppKit
                )
                tf.setFrame_(AppKit.NSMakeRect(W / 2 - 180, (H - 15) / 2, 360, 15))
                tf.setAlignment_(AppKit.NSTextAlignmentCenter)
                content.addSubview_(tf)
                return

            n      = len(mappings)
            slot_w = W / n

            for i, (fkey, label) in enumerate(mappings):
                x = i * slot_w

                if i > 0:
                    sep = self._make_label("|", DIM, 11, AppKit)
                    sep.setFrame_(AppKit.NSMakeRect(x - 4, (H - 15) / 2, 8, 15))
                    sep.setAlignment_(AppKit.NSTextAlignmentCenter)
                    content.addSubview_(sep)

                PAD  = 10
                FK_W = 24

                fk = self._make_label(fkey, ORANGE, 10.5, AppKit)
                try:
                    fk.setFont_(AppKit.NSFont.monospacedSystemFontOfSize_weight_(10.5, 0.6))
                except Exception:
                    pass
                fk.setFrame_(AppKit.NSMakeRect(x + PAD, (H - 15) / 2, FK_W, 15))
                content.addSubview_(fk)

                ar = self._make_label("->", DIM, 10, AppKit)
                ar.setFrame_(AppKit.NSMakeRect(x + PAD + FK_W + 3, (H - 15) / 2, 16, 15))
                content.addSubview_(ar)

                lbl_x = x + PAD + FK_W + 21
                lbl_w = slot_w - PAD - FK_W - 21 - 4
                act = self._make_label(label, WHITE, 10.5, AppKit)
                act.setFrame_(AppKit.NSMakeRect(lbl_x, (H - 15) / 2, lbl_w, 15))
                act.cell().setLineBreakMode_(AppKit.NSLineBreakByTruncatingTail)
                content.addSubview_(act)

        except Exception as e:
            import traceback
            print(f"[HUD] refresh error: {e}")
            traceback.print_exc()

    @staticmethod
    def _make_label(text, color, size, AppKit):
        """Helper: create a non-interactive, transparent NSTextField."""
        tf = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, 100, 20)
        )
        tf.setEditable_(False)
        tf.setSelectable_(False)
        tf.setBezeled_(False)
        tf.setDrawsBackground_(False)
        tf.setTextColor_(color)
        tf.setFont_(AppKit.NSFont.systemFontOfSize_(size))
        tf.setStringValue_(text)
        return tf


# ── Public factory ────────────────────────────────────────────────────────────

def FKeyHUD(config_path: Path):
    """Return the right HUD implementation for the current platform."""
    if sys.platform == 'win32':
        return _FKeyHUDWindows(config_path)
    else:
        return _FKeyHUDMac(config_path)
