# -*- coding: utf-8 -*-
"""
MASTER 10-PAGE COMBINER & LIVE PAGE DESIGNER LOADER FOR GUJARAT SAMACHAR
========================================================================
Combines Page_01_SameToSame.pagedesigner through Page_10_SameToSame.pagedesigner
into a single 10-spread document:
  - Gujarat_Samachar_All_10_Pages_SameToSame.pagedesigner
  - Gujarat_Samachar_All_10_Pages_SameToSame.dns
in both:
  - E:\\RND\\SAME TO SMAE GUJRATI NEWS
  - E:\\RND\\SAME TO SAME GUJRATI NEWS
and opens it in Page Designer 1.0 in Edit Mode (Normal Screen Mode, Frame Edges ON, Guides ON).
"""

import ctypes
import json
import shutil
import socket
import sys
import time
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 47123
RND_ROOT = Path(__file__).resolve().parent
DIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"
DIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"


def build_combined_10_page_document() -> Path:
    t0 = time.perf_counter()
    base_doc = None
    combined_spreads = []
    combined_stories = {}
    combined_assets = {}
    combined_swatches_by_name = {}
    zip_asset_blobs = {}
    mimetype_bytes = b"application/vnd.pagedesigner.document"
    meta_bytes = None
    base_parent_id = 3

    for page_num in range(1, 11):
        offset = (page_num - 1) * 10000
        src_pd = DIR_SAME / f"Page_{page_num:02d}_SameToSame.pagedesigner"
        if not src_pd.exists():
            src_pd = DIR_SMAE / f"Page_{page_num:02d}_SameToSame.pagedesigner"
        if not src_pd.exists():
            raise FileNotFoundError(f"Missing {src_pd}")

        with zipfile.ZipFile(src_pd, "r") as zf:
            names = set(zf.namelist())
            if "mimetype" in names and mimetype_bytes is None:
                mimetype_bytes = zf.read("mimetype")
            if "meta.json" in names and meta_bytes is None:
                meta_bytes = zf.read("meta.json")
            doc = json.loads(zf.read("document.json").decode("utf-8"))

            if base_doc is None:
                base_doc = json.loads(json.dumps(doc))
                if base_doc.get("parents"):
                    base_parent_id = base_doc["parents"][0].get("id", 3)

            for sw in doc.get("swatches", []):
                sw_name = sw.get("name")
                if sw_name and sw_name not in combined_swatches_by_name:
                    combined_swatches_by_name[sw_name] = sw

            sp = json.loads(json.dumps(doc["spreads"][0]))
            sp["id"] = int(sp.get("id", 5)) + offset
            for pg in sp.get("pages", []):
                pg["id"] = int(pg.get("id", 4)) + offset
                pg["parent"] = base_parent_id

            def remap_items(items):
                for it in items:
                    it["id"] = int(it["id"]) + offset
                    ct = it.get("content", {})
                    t = ct.get("type")
                    if t == "group":
                        remap_items(ct.get("items", []))
                    elif t == "text" and "story" in ct:
                        ct["story"] = int(ct["story"]) + offset
                    elif t == "graphic" and "asset" in ct:
                        ct["asset"] = int(ct["asset"]) + offset

            remap_items(sp.get("items", []))
            combined_spreads.append(sp)

            for sid_str, st in doc.get("stories", {}).items():
                new_sid = int(sid_str) + offset
                st_copy = json.loads(json.dumps(st))
                st_copy["id"] = new_sid
                st_copy["frames"] = [int(fid) + offset for fid in st_copy.get("frames", [])]
                combined_stories[str(new_sid)] = st_copy

            for aid_str, ainfo in doc.get("assets", {}).items():
                new_aid = int(aid_str) + offset
                a_copy = json.loads(json.dumps(ainfo))
                a_copy["id"] = new_aid
                combined_assets[str(new_aid)] = a_copy
                for ext in (".webp", ".png", ".jpg", ".jpeg", ".tif"):
                    old_entry = f"assets/{aid_str}{ext}"
                    if old_entry in names:
                        zip_asset_blobs[f"assets/{new_aid}{ext}"] = zf.read(old_entry)
                        break

    base_doc["title"] = "Gujarat Samachar — All 10 Pages (100% Editable Gopika)"
    base_doc["spreads"] = combined_spreads
    base_doc["stories"] = combined_stories
    base_doc["assets"] = combined_assets
    base_doc["swatches"] = list(combined_swatches_by_name.values())
    base_doc["nextId"] = 110000

    doc_bytes = json.dumps(base_doc, ensure_ascii=False).encode("utf-8")

    out_paths = []
    for target_dir in (DIR_SAME, DIR_SMAE):
        target_dir.mkdir(parents=True, exist_ok=True)
        pd_out = target_dir / "Gujarat_Samachar_All_10_Pages_SameToSame.pagedesigner"
        dns_out = target_dir / "Gujarat_Samachar_All_10_Pages_SameToSame.dns"
        with zipfile.ZipFile(pd_out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            zout.writestr("mimetype", mimetype_bytes, compress_type=zipfile.ZIP_STORED)
            if meta_bytes:
                zout.writestr("meta.json", meta_bytes)
            zout.writestr("document.json", doc_bytes)
            for k, v in zip_asset_blobs.items():
                zout.writestr(k, v)
        shutil.copy2(pd_out, dns_out)
        out_paths.append(pd_out)

    print(f"Combined 10-page document built in {time.perf_counter() - t0:.2f}s -> {out_paths[0]}")
    return out_paths[0]


def open_in_pagedesigner_edit_mode(pd_path: Path, page_num: int = 1):
    try:
        user32 = ctypes.windll.user32
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    if "Page Designer" in buf.value and "Studio" not in buf.value:
                        user32.ShowWindow(hwnd, 9)
                        user32.SetForegroundWindow(hwnd)
            return True
        user32.EnumWindows(EnumWindowsProc(_cb), 0)
    except Exception:
        pass

    sock = socket.create_connection(("127.0.0.1", PORT), timeout=15)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    f_in = sock.makefile("r", encoding="utf-8")
    req_id = [0]

    def rpc(method, params=None):
        req_id[0] += 1
        payload = {"id": req_id[0], "method": method, "params": params or {}}
        sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        return json.loads(f_in.readline())

    def cmd(command, params=None):
        return rpc("engine.execute", {"command": command, "params": params or {}})

    cmd("file.open", {"path": str(pd_path)})
    ui_now = rpc("ui.inspect").get("result", {}).get("ui", {})
    cmd("view.screenMode", {"mode": "normal"})
    if not ui_now.get("frameEdges", False):
        cmd("view.frameEdges")
    if not ui_now.get("guides", False):
        cmd("view.guides")
    cmd("view.goToPage", {"page": page_num})
    cmd("view.fitPage")
    sock.close()


if __name__ == "__main__":
    combined_pd = build_combined_10_page_document()
    open_in_pagedesigner_edit_mode(combined_pd, page_num=1)
