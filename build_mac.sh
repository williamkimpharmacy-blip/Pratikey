#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  Pratikey — macOS Build Script
#  Produces:  dist/Pratikey.app   (drag-to-Applications)
#             dist/Pratikey.dmg   (share / post on website)
# ─────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"

ORANGE='\033[38;5;214m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

APP_NAME="Pratikey"
APP_VERSION="1.0.0"
BUNDLE_ID="com.pratikey.app"

echo ""
echo -e "${ORANGE}${BOLD}  ╔═══════════════════════════════════════╗${RESET}"
echo -e "${ORANGE}${BOLD}  ║   Pratikey — macOS Build Script       ║${RESET}"
echo -e "${ORANGE}${BOLD}  ╚═══════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Check platform ─────────────────────────────────────────
if [[ "$OSTYPE" != "darwin"* ]]; then
  echo -e "${RED}✗ This script is macOS only.${RESET}"
  exit 1
fi

# ── 2. Check Python ───────────────────────────────────────────
echo -ne "  Checking Python 3...  "
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}✗ Not found. Install from https://python.org${RESET}"
  exit 1
fi
PYVER=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ $PYVER${RESET}"

# ── 3. Install Python dependencies ────────────────────────────
echo -ne "  Installing dependencies...  "
pip3 install pynput pystray pillow pyinstaller pyobjc-framework-Quartz --break-system-packages -q 2>/dev/null \
  || pip3 install pynput pystray pillow pyinstaller pyobjc-framework-Quartz -q
echo -e "${GREEN}✓ Done${RESET}"

# ── 4. Generate .icns from PNGs ───────────────────────────────
echo -ne "  Building icon (.icns)...  "
ICONSET="icons/pratikey.iconset"
rm -rf "$ICONSET"
mkdir -p "$ICONSET"

# macOS iconset requires specific sizes with @2x variants
cp "icons/pratikey_16.png"  "${ICONSET}/icon_16x16.png"
cp "icons/pratikey_32.png"  "${ICONSET}/icon_16x16@2x.png"
cp "icons/pratikey_32.png"  "${ICONSET}/icon_32x32.png"
cp "icons/pratikey_64.png"  "${ICONSET}/icon_32x32@2x.png"
cp "icons/pratikey_128.png" "${ICONSET}/icon_128x128.png"
cp "icons/pratikey_256.png" "${ICONSET}/icon_128x128@2x.png"
cp "icons/pratikey_256.png" "${ICONSET}/icon_256x256.png"
cp "icons/pratikey_512.png" "${ICONSET}/icon_256x256@2x.png"
cp "icons/pratikey_512.png" "${ICONSET}/icon_512x512.png"

# Need 512@2x (1024px) — upscale from 512
if [ -f "icons/pratikey_512.png" ]; then
  sips -z 1024 1024 "icons/pratikey_512.png" --out "${ICONSET}/icon_512x512@2x.png" &>/dev/null || true
fi

iconutil -c icns "$ICONSET" -o icons/pratikey.icns
rm -rf "$ICONSET"
echo -e "${GREEN}✓ icons/pratikey.icns${RESET}"

# ── 5. Clean previous build ───────────────────────────────────
echo -ne "  Cleaning previous build...  "
rm -rf dist/Pratikey dist/Pratikey.app build/
echo -e "${GREEN}✓ Clean${RESET}"

# ── 6. Run PyInstaller ────────────────────────────────────────
echo ""
echo -e "  ${ORANGE}${BOLD}Building Pratikey.app...${RESET}"
echo -e "  ${DIM}(This takes 1–3 minutes)${RESET}"
echo ""
pyinstaller pratikey.spec --noconfirm 2>&1 | grep -E "^(INFO|WARNING|ERROR|Building)" | head -30

if [ ! -d "dist/Pratikey.app" ]; then
  echo ""
  echo -e "${RED}✗ Build failed. Run: pyinstaller pratikey.spec --noconfirm${RESET}"
  exit 1
fi
echo ""
echo -e "  ${GREEN}✓ dist/Pratikey.app built${RESET}"

# ── 6b. Ad-hoc code sign (required for Accessibility on macOS) ──
echo -ne "  Signing app...  "
codesign --force --deep --sign - dist/Pratikey.app &>/dev/null
echo -e "${GREEN}✓ Signed${RESET}"

# ── 7. Build DMG ──────────────────────────────────────────────
echo ""
echo -ne "  Creating Pratikey.dmg...  "

DMG_NAME="Pratikey-${APP_VERSION}.dmg"
DMG_TMP="dist/_dmg_tmp"
DMG_OUT="dist/${DMG_NAME}"

rm -rf "$DMG_TMP" "$DMG_OUT"
mkdir -p "$DMG_TMP"

# Copy app into staging folder
cp -R "dist/Pratikey.app" "$DMG_TMP/"

# Symlink to /Applications for easy drag-install
ln -s /Applications "$DMG_TMP/Applications"

# Create the DMG
hdiutil create \
  -volname "Pratikey $APP_VERSION" \
  -srcfolder "$DMG_TMP" \
  -ov \
  -format UDZO \
  -imagekey zlib-level=9 \
  "$DMG_OUT" &>/dev/null

rm -rf "$DMG_TMP"
echo -e "${GREEN}✓ dist/${DMG_NAME}${RESET}"

# ── 8. Done ───────────────────────────────────────────────────
echo ""
echo -e "  ${ORANGE}${BOLD}╔═══════════════════════════════════════╗${RESET}"
echo -e "  ${ORANGE}${BOLD}║   Build Complete!                     ║${RESET}"
echo -e "  ${ORANGE}${BOLD}╚═══════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${BOLD}Files created:${RESET}"
echo -e "  📦  dist/Pratikey.app       ← drag to /Applications"
echo -e "  💿  dist/${DMG_NAME}  ← share/post online"
echo ""
echo -e "  ${BOLD}To install locally:${RESET}"
echo -e "  ${DIM}cp -R dist/Pratikey.app /Applications/${RESET}"
echo ""
echo -e "  ${BOLD}Important — first-time users:${RESET}"
echo -e "  ${DIM}1. Double-click the DMG${RESET}"
echo -e "  ${DIM}2. Drag Pratikey → Applications${RESET}"
echo -e "  ${DIM}3. Right-click Pratikey → Open (first launch only)${RESET}"
echo -e "  ${DIM}4. Allow Accessibility in System Settings → Privacy${RESET}"
echo ""
echo -e "  ${ORANGE}Note: App Store distribution is not possible for this${RESET}"
echo -e "  ${ORANGE}app type — Apple's sandbox blocks global keyboard access.${RESET}"
echo -e "  ${ORANGE}Direct download (like Raycast, Alfred, Karabiner) is${RESET}"
echo -e "  ${ORANGE}the standard way to ship this kind of utility.${RESET}"
echo ""
