#!/bin/bash
# ==============================================================================
# 1-Click macOS Launcher — Gujarat Samachar / आस-पास / INDIAN POST Live Studio
# ==============================================================================
cd "$(dirname "$0")"
REPO_ROOT="$(pwd)"

echo "=============================================================================="
echo "  GUJARAT SAMACHAR / आस-पास / INDIAN POST — 3-Edition Live Studio (macOS)"
echo "=============================================================================="

# 1. Install all bundled fonts into ~/Library/Fonts on macOS
mkdir -p "$HOME/Library/Fonts"
if [ -d "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Document Fonts" ]; then
    cp -f "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Document Fonts/"*.ttf "$HOME/Library/Fonts/" 2>/dev/null
    cp -f "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Document Fonts/"*.otf "$HOME/Library/Fonts/" 2>/dev/null
    echo "[OK] Installed all Gujarati, Hindi (आस-पास Calligraphic) and English (INDIAN POST) fonts to ~/Library/Fonts"
fi

# 2. Configure Page Designer 1.0 TCP Control Port (47123)
launchctl setenv PAGEDESIGNER_CONTROL_PORT 47123 2>/dev/null
export PAGEDESIGNER_CONTROL_PORT=47123

# 3. Ensure Python 3 + Pillow are available
PY_BIN="python3"
if ! $PY_BIN -c "import PIL" >/dev/null 2>&1; then
    echo "[INFO] Setting up local Python virtual environment (.venv) with Pillow..."
    python3 -m venv "$REPO_ROOT/.venv"
    "$REPO_ROOT/.venv/bin/pip" install --quiet --upgrade pip Pillow fonttools
    PY_BIN="$REPO_ROOT/.venv/bin/python3"
elif [ -x "$REPO_ROOT/.venv/bin/python3" ]; then
    PY_BIN="$REPO_ROOT/.venv/bin/python3"
fi

# 4. Launch the Live Studio Web App (Port 47898) and connect to Page Designer 1.0 (Port 47123)
exec "$PY_BIN" "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Gujarati_Page_Designer_App/launch_gujarati_page_designer_app.py"
