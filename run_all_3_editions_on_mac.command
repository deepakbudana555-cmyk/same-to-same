#!/bin/bash
# ==============================================================================
# 1-Click macOS Auto-Runner — Draw All 30 Pages (Gujarati -> Hindi -> English)
# Live Inside Page Designer 1.0 on macOS
# ==============================================================================
cd "$(dirname "$0")"
REPO_ROOT="$(pwd)"

mkdir -p "$HOME/Library/Fonts"
if [ -d "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Document Fonts" ]; then
    cp -f "$REPO_ROOT/SAME TO SAME GUJRATI NEWS/Document Fonts/"*.ttf "$HOME/Library/Fonts/" 2>/dev/null
fi

launchctl setenv PAGEDESIGNER_CONTROL_PORT 47123 2>/dev/null
export PAGEDESIGNER_CONTROL_PORT=47123

PY_BIN="python3"
if [ -x "$REPO_ROOT/.venv/bin/python3" ]; then
    PY_BIN="$REPO_ROOT/.venv/bin/python3"
elif ! $PY_BIN -c "import PIL" >/dev/null 2>&1; then
    python3 -m venv "$REPO_ROOT/.venv"
    "$REPO_ROOT/.venv/bin/pip" install --quiet --upgrade pip Pillow fonttools
    PY_BIN="$REPO_ROOT/.venv/bin/python3"
fi

"$PY_BIN" -c "import sys; sys.path.insert(0, 'SAME TO SAME GUJRATI NEWS/Gujarati_Page_Designer_App'); import launch_gujarati_page_designer_app as a; a.install_bundled_fonts_for_os(); a.localize_pagedesigner_asset_links()"

exec "$PY_BIN" "$REPO_ROOT/run_all_3_editions_live_in_pagedesigner.py"
