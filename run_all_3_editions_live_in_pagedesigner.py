# -*- coding: utf-8 -*-
import json
import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path

if sys.platform == "win32":
    import ctypes

RND_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RND_ROOT / "SAME TO SAME GUJRATI NEWS" / "Gujarati_Page_Designer_App"))
import launch_gujarati_page_designer_app as app


def launch_and_maximize_pagedesigner():
    """Ensure Page Designer 1.0 is launched visibly and maximized/focused in the foreground on Windows or macOS."""
    port = app.ensure_visible_pagedesigner(bring_to_front=True)
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

            def _cb(hwnd, _lparam):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        if "Page Designer" in buf.value and "Studio" not in buf.value:
                            user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                            user32.SetForegroundWindow(hwnd)
                            return False
                return True

            user32.EnumWindows(WNDENUMPROC(_cb), 0)
        except Exception:
            pass
    elif sys.platform == "darwin":
        app.bring_pagedesigner_to_front()
    return port


def run_edition_live_sync(ed_key: str, step_delay: float = 0.012, page_pause: float = 0.35):
    cfg = app.EDITION_CONFIG[ed_key]
    launch_and_maximize_pagedesigner()

    combined_pd = app.DIR_SAME / f"{cfg['combined_name']}.pagedesigner"
    if not combined_pd.exists():
        combined_pd = app._rebuild_combined_for_edition(ed_key)
    with zipfile.ZipFile(combined_pd, "r") as zf:
        doc = json.loads(zf.read("document.json").decode("utf-8"))

    sock, call = app.pd_rpc_session()
    try:
        call("ui.focus", {})
    except Exception:
        pass

    call("engine.execute", {"command": "file.open", "params": {"path": str(combined_pd)}})
    ui_state = call("ui.inspect", {}).get("result", {}).get("ui", {})
    call("engine.execute", {"command": "view.screenMode", "params": {"mode": "normal"}})
    if not ui_state.get("frameEdges", False):
        call("engine.execute", {"command": "view.frameEdges", "params": {}})
    if not ui_state.get("guides", False):
        call("engine.execute", {"command": "view.guides", "params": {}})

    launch_and_maximize_pagedesigner()
    time.sleep(0.20)
    print(f"=== RUNNING {ed_key.upper()} ({cfg['masthead_title']}) LIVE IN PAGE DESIGNER (10 PAGES) ===", flush=True)

    for pnum in range(1, 11):
        sp = doc["spreads"][pnum - 1]
        leaf_ids, first_head_id = app._collect_sorted_leaf_item_ids_and_first_headline(sp.get("items", []))
        call("engine.execute", {"command": "view.goToPage", "params": {"page": pnum}})
        call("engine.execute", {"command": "view.fitPage", "params": {}})
        call("engine.execute", {"command": "edit.deselectAll", "params": {}})
        call("engine.execute", {"command": "object.setFlags", "params": {"ids": leaf_ids, "hidden": True}})
        time.sleep(0.08)

        chunk_sz = 5 if len(leaf_ids) > 100 else 4
        for i in range(0, len(leaf_ids), chunk_sz):
            batch_ids = leaf_ids[i : i + chunk_sz]
            call("engine.execute", {"command": "object.setFlags", "params": {"ids": batch_ids, "hidden": False}})
            time.sleep(step_delay)

        if first_head_id:
            call("engine.execute", {"command": "object.select", "params": {"ids": [first_head_id]}})
        print(f"  -> {ed_key.upper()} Page {pnum:02d} drawn live ({len(leaf_ids)} editable items)", flush=True)
        time.sleep(page_pause)

    # Return to Page 01 at end of edition
    call("engine.execute", {"command": "view.goToPage", "params": {"page": 1}})
    call("engine.execute", {"command": "view.fitPage", "params": {}})
    sp1 = doc["spreads"][0]
    _, first_head_p1 = app._collect_sorted_leaf_item_ids_and_first_headline(sp1.get("items", []))
    if first_head_p1:
        call("engine.execute", {"command": "object.select", "params": {"ids": [first_head_p1]}})
    sock.close()


if __name__ == "__main__":
    print("=== STEP 0: LAUNCHING PAGE DESIGNER 1.0 ===", flush=True)
    port = launch_and_maximize_pagedesigner()
    print(f"Page Designer 1.0 running and focused on control port {port}", flush=True)
    time.sleep(0.6)

    # 1. GUJARATI (ગુજરાત સમાચાર — All 10 Pages)
    run_edition_live_sync("gujarati", step_delay=0.012, page_pause=0.30)
    time.sleep(0.9)

    # 2. HINDI (आस-पास — All 10 Pages)
    run_edition_live_sync("hindi", step_delay=0.012, page_pause=0.30)
    time.sleep(0.9)

    # 3. ENGLISH (INDIAN POST — All 10 Pages)
    run_edition_live_sync("english", step_delay=0.012, page_pause=0.30)

    print("=== ALL 3 EDITIONS (GUJARATI -> HINDI -> ENGLISH, 30 PAGES TOTAL) EXECUTED LIVE IN PAGE DESIGNER 1.0 ===", flush=True)
