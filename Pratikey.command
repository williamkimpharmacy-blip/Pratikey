#!/bin/bash
# ─────────────────────────────────────────────────────────────
#  Pratikey Launcher
#  Double-click this file to start Pratikey.
# ─────────────────────────────────────────────────────────────

# Move to the folder this script lives in
cd "$(dirname "$0")"

# ── Colours ───────────────────────────────────────────────────
ORANGE='\033[38;5;214m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

clear
echo ""
echo -e "  ${ORANGE}${BOLD}██████╗ ██████╗  █████╗ ████████╗██╗██╗  ██╗███████╗██╗   ██╗${RESET}"
echo -e "  ${ORANGE}${BOLD}██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██║██║ ██╔╝██╔════╝╚██╗ ██╔╝${RESET}"
echo -e "  ${ORANGE}${BOLD}██████╔╝██████╔╝███████║   ██║   ██║█████╔╝ █████╗   ╚████╔╝ ${RESET}"
echo -e "  ${ORANGE}${BOLD}██╔═══╝ ██╔══██╗██╔══██║   ██║   ██║██╔═██╗ ██╔══╝    ╚██╔╝  ${RESET}"
echo -e "  ${ORANGE}${BOLD}██║     ██║  ██║██║  ██║   ██║   ██║██║  ██╗███████╗   ██║   ${RESET}"
echo -e "  ${ORANGE}${BOLD}╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ${RESET}"
echo ""
echo -e "  ${DIM}One key. Endless possibilities.${RESET}"
echo ""
echo -e "  ─────────────────────────────────────────────────"
echo ""

# ── Check Python 3 ────────────────────────────────────────────
echo -ne "  Checking Python 3...  "
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}✗ Not found${RESET}"
  echo ""
  echo -e "  ${YELLOW}Python 3 is required. Install it from:${RESET}"
  echo -e "  ${BOLD}https://www.python.org/downloads/${RESET}"
  echo ""
  read -p "  Press Enter to open that page..." _
  open "https://www.python.org/downloads/"
  exit 1
fi
PYVER=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYVER${RESET}"

# ── Check / install dependencies ──────────────────────────────
DEPS=("pynput" "pystray" "pillow")
MISSING=()

echo -ne "  Checking dependencies...  "
for dep in "${DEPS[@]}"; do
  if ! python3 -c "import $dep" &>/dev/null; then
    MISSING+=("$dep")
  fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
  echo -e "${GREEN}✓ All installed${RESET}"
else
  echo -e "${YELLOW}Installing ${MISSING[*]}...${RESET}"
  echo ""
  python3 -m pip install "${MISSING[@]}" --break-system-packages --quiet
  if [ $? -ne 0 ]; then
    # Try without --break-system-packages (older Python)
    python3 -m pip install "${MISSING[@]}" --quiet
  fi
  echo -e "  ${GREEN}✓ Dependencies ready${RESET}"
fi

# ── Grant Accessibility permission hint (macOS) ───────────────
echo ""
echo -e "  ${DIM}Tip: If keys don't work, go to System Settings → Privacy${RESET}"
echo -e "  ${DIM}→ Accessibility and add Terminal (or this app).${RESET}"
echo ""
echo -e "  ─────────────────────────────────────────────────"
echo ""
echo -e "  ${ORANGE}${BOLD}Starting Pratikey...${RESET}  ${DIM}(look for the 🔑 icon in your menu bar)${RESET}"
echo ""

# ── Launch ────────────────────────────────────────────────────
# Run binary directly so Terminal's Accessibility permission applies
if [ -f "/Applications/Pratikey.app/Contents/MacOS/Pratikey" ]; then
  /Applications/Pratikey.app/Contents/MacOS/Pratikey
else
  python3 tray.py
fi

# If it exits unexpectedly, pause so the user can read any error
echo ""
echo -e "  ${YELLOW}Pratikey stopped.${RESET}"
echo ""
read -p "  Press Enter to close..." _
