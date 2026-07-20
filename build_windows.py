"""
Pratikey — Windows Build Script
Run on a Windows machine or via GitHub Actions.
Produces: dist\Pratikey-1.0.0.zip  (ready to share / post online)

Usage:
    python build_windows.py
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

APP_VERSION = "1.0.0"
APP_NAME    = "Pratikey"

def run(cmd, desc=""):
    if desc:
        print(f"  {desc}...", end=" ", flush=True)
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("FAILED")
        print(f"  ERROR running: {cmd}")
        sys.exit(1)
    if desc:
        print("OK")

def main():
    root = Path(__file__).parent
    os.chdir(root)

    print()
    print("=" * 52)
    print(f"  {APP_NAME} {APP_VERSION} — Windows Build Script")
    print("=" * 52)
    print()

    # ── 1. Check Python ───────────────────────────────────────
    pyver = sys.version.split()[0]
    print(f"  Python {pyver} - OK")

    # ── 2. Install dependencies ───────────────────────────────
    print("  Installing dependencies...")
    deps = "pynput pystray pillow pyinstaller pywin32"
    run(f'pip install {deps} --quiet', "")
    print("  Dependencies ready - OK")

    # ── 3. Clean previous build ───────────────────────────────
    print("  Cleaning previous build...", end=" ", flush=True)
    shutil.rmtree("dist/Pratikey", ignore_errors=True)
    shutil.rmtree("build",         ignore_errors=True)
    zip_out = Path(f"dist/{APP_NAME}-{APP_VERSION}-windows.zip")
    zip_out.unlink(missing_ok=True)
    print("OK")

    # ── 4. PyInstaller ────────────────────────────────────────
    print()
    print(f"  Building {APP_NAME}.exe  (this takes 2-4 minutes)...")
    print()
    result = subprocess.run(
        "pyinstaller pratikey.spec --noconfirm",
        shell=True
    )
    if result.returncode != 0:
        print()
        print("  ERROR: PyInstaller failed.")
        print("  Run manually: pyinstaller pratikey.spec --noconfirm")
        sys.exit(1)

    exe_path = Path("dist/Pratikey/Pratikey.exe")
    if not exe_path.exists():
        print("  ERROR: Pratikey.exe not found after build.")
        sys.exit(1)

    print()
    print(f"  dist/Pratikey/Pratikey.exe built - OK")

    # ── 5. ZIP for distribution ───────────────────────────────
    print(f"  Creating {zip_out.name}...", end=" ", flush=True)
    zip_out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_DEFLATED) as zf:
        src = Path("dist/Pratikey")
        for file in src.rglob("*"):
            if file.is_file():
                zf.write(file, Path(APP_NAME) / file.relative_to(src))
    print("OK")

    # ── 6. Done ───────────────────────────────────────────────
    size_mb = zip_out.stat().st_size / 1_048_576
    print()
    print("=" * 52)
    print(f"  Build Complete!")
    print("=" * 52)
    print()
    print(f"  File:    dist\\{zip_out.name}  ({size_mb:.1f} MB)")
    print()
    print("  To install:")
    print("    1. Extract the ZIP")
    print("    2. Run Pratikey.exe")
    print("    3. Click 'More info' → 'Run anyway' if SmartScreen appears")
    print("    4. Allow in Settings → Privacy → Input monitoring (if prompted)")
    print()
    print("  To auto-start with Windows, right-click Pratikey.exe")
    print("  → Create shortcut → paste into:")
    print(r"  shell:startup  (Win+R to open)")
    print()

if __name__ == "__main__":
    main()
