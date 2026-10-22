from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 2 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt (37.04 x 52.57 cm)
- Graphics (PNG): Top Running Header Bar, Jalebi-Fafda Frying Photo, Riverfront Multilevel
  Parking Photo, Oil TPC Meter Photo, and Bottom CMYK Bar.
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular, with embedded
  Latin English terms in 'Arial') across all 10 stories/boxes of Page 2!
"""

import json
import re
import shutil
import socket
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PORT = 47123
S = 0.375  # 1 px = 0.375 pt -> 2800 px = 1050.0 pt, 3974 px = 1490.25 pt
PAGE_W_PT = round(2800 * S, 2)
PAGE_H_PT = round(3974 * S, 2)

RND_ROOT = Path(__file__).resolve().parent
DIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"
DIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"
ASSETS_DIR = DIR_SMAE / "Page_02_Assets"

try:
    sock = socket.create_connection(("127.0.0.1", PORT), timeout=2.0)
except Exception:
    sys.path.insert(0, str(DIR_SAME / "Gujarati_Page_Designer_App"))
    import launch_gujarati_page_designer_app as _launcher
    _launcher.ensure_visible_pagedesigner(bring_to_front=False)
    sock = socket.create_connection(("127.0.0.1", PORT), timeout=15)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
f_in = sock.makefile("r", encoding="utf-8")
req_id = 0


def rpc(method, params=None):
    global req_id
    req_id += 1
    payload = {"id": req_id, "method": method, "params": params or {}}
    sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
    line = f_in.readline()
    resp = json.loads(line)
    if not resp.get("ok"):
        raise RuntimeError(f"RPC {method} failed: {resp}")
    return resp.get("result")


def cmd(command, params=None):
    return rpc("engine.execute", {"command": command, "params": params or {}})


def batch(commands):
    return rpc("engine.batch", {"commands": commands})


def p(px_val: float) -> float:
    return round(px_val * S, 2)


def rect_pt(x1_px: float, y1_px: float, x2_px: float, y2_px: float):
    return [p(x1_px), p(y1_px), p(x2_px), p(y2_px)]


def utf8_len(s: str) -> int:
    return len(s.encode("utf-8"))


def _utf8_byte_pos(text: str, char_pos: int) -> int:
    return len(text[:char_pos].encode("utf-8"))


def _apply_latin_arial_runs(sid: int, text: str, base_pt: float, font_style: str = "Regular"):
    latin_cmds = []
    eng_pt = round(base_pt * 0.76, 1)
    for m in re.finditer(r"[A-Za-z0-9‘’'\"“”]+(?:\s+[A-Za-z0-9‘’'\"“”]+)*", text):
        b0 = _utf8_byte_pos(text, m.start())
        b1 = _utf8_byte_pos(text, m.end())
        latin_cmds.append({"command": "text.select", "params": {"story": sid, "anchor": b0, "focus": b1}})
        latin_cmds.append({"command": "type.char", "params": {"attrs": {
            "fontFamily": "Arial",
            "fontStyle": font_style,
            "size": eng_pt,
        }}})
    if latin_cmds:
        batch(latin_cmds)


# ==============================================================================
# INITIALIZE DOCUMENT & SWATCHES (WITH LIVE VISUAL STEP-BY-STEP DRAWING)
# ==============================================================================
LIVE_DRAW = True
FRAME_DELAY = 0.10 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.18 if LIVE_DRAW else 0.0
LINE_DELAY = 0.05 if LIVE_DRAW else 0.0


def _bring_pagedesigner_to_front():
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR),
                ("lpDesktop", wintypes.LPWSTR), ("lpTitle", wintypes.LPWSTR),
                ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD), ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
                ("hStdInput", wintypes.HANDLE), ("hStdOutput", wintypes.HANDLE),
                ("hStdError", wintypes.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD), ("dwThreadId", wintypes.DWORD),
            ]

        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(STARTUPINFOW)
        si.lpDesktop = "WinSta0\\Default"
        si.dwFlags = 1
        si.wShowWindow = 0
        pi = PROCESS_INFORMATION()
        one_liner = (
            'python -c "import ctypes; u=ctypes.windll.user32; '
            'WNDENUMPROC=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p); '
            'cb=lambda h,l:(u.IsWindowVisible(h) and \'Page Designer\' in (lambda b:(u.GetWindowTextW(h,b,255),b.value)[1])(ctypes.create_unicode_buffer(256)) and (u.ShowWindow(h,3),u.SetWindowPos(h,-1,0,0,0,0,3),u.SetWindowPos(h,-2,0,0,0,0,3),u.SetForegroundWindow(h))) or True; '
            'u.EnumWindows(WNDENUMPROC(cb),0)"'
        )
        cmd_buf = ctypes.create_unicode_buffer(one_liner)
        if kernel32.CreateProcessW(None, cmd_buf, None, None, False, 0x08000000, None, None, ctypes.byref(si), ctypes.byref(pi)):
            kernel32.WaitForSingleObject(pi.hProcess, 2000)
            kernel32.CloseHandle(pi.hProcess)
            kernel32.CloseHandle(pi.hThread)
    except Exception:
        pass


_bring_pagedesigner_to_front()
t0 = time.perf_counter()

try:
    ui_state = rpc("ui.inspect")
    for _ in range(len(ui_state.get("documents", []))):
        rpc("app.close", {"discard": True})
except Exception:
    pass

batch([
    {"command": "file.new", "params": {
        "width": PAGE_W_PT,
        "height": PAGE_H_PT,
        "pages": 1,
        "facingPages": False,
        "columns": 8,
        "gutter": p(26.5),
        "margins": p(84.0),
        "title": "Gujarat Samachar — Page 02 (100% Same-to-Same Editable Gopika)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.4)


# ==============================================================================
# HELPER FUNCTIONS FOR GRAPHICS, BOXES, LINES, AND EXACT GOPIKA TYPOGRAPHY
# ==============================================================================
def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):
    webp_cand = ASSETS_DIR / (Path(filename).stem + ".webp")
    use_file = webp_cand if webp_cand.exists() else (ASSETS_DIR / filename)
    img_path = str(use_file.resolve()).replace("\\", "/")
    r = cmd("frame.create", {
        "spread": 0,
        "rect": rect_pt(x1_px, y1_px, x2_px, y2_px),
        "content": "graphic"
    })
    fid = r["id"]
    if LIVE_DRAW:
        cmd("object.stroke", {"ids": [fid], "swatch": "GsOrangeBorder", "weight": 1.2, "tint": 1.0})
        time.sleep(FRAME_DELAY)
    batch([
        {"command": "file.place", "params": {"path": img_path, "frame": fid}},
        {"command": "object.fit", "params": {"ids": [fid], "mode": "fillProportionally"}},
        {"command": "object.stroke", "params": {"ids": [fid], "swatch": "[Black]", "weight": 0.0, "tint": 0.0}},
    ])
    if LIVE_DRAW:
        time.sleep(CONTENT_DELAY)
    return fid


def draw_box(x1_px, y1_px, x2_px, y2_px, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="[Black]", stroke_weight_pt=1.5, stroke_tint=1.0):
    r = cmd("frame.create", {
        "spread": 0,
        "rect": rect_pt(x1_px, y1_px, x2_px, y2_px),
        "content": "text",
        "text": ""
    })
    fid = r["id"]
    cmds = []
    if fill_tint > 0.0:
        cmds.append({"command": "object.fill", "params": {"ids": [fid], "swatch": fill_swatch, "tint": fill_tint}})
    if stroke_weight_pt > 0.0:
        cmds.append({"command": "object.stroke", "params": {"ids": [fid], "swatch": stroke_swatch, "weight": stroke_weight_pt, "tint": stroke_tint}})
    if cmds:
        batch(cmds)
    if LIVE_DRAW:
        time.sleep(FRAME_DELAY)
    return fid


def draw_line(x1_px, y1_px, x2_px, y2_px, swatch="[Black]", weight_pt=0.85, tint=1.0):
    r = cmd("line.create", {
        "spread": 0,
        "a": [p(x1_px), p(y1_px)],
        "b": [p(x2_px), p(y2_px)]
    })
    lid = r["id"]
    cmd("object.stroke", {"ids": [lid], "swatch": swatch, "weight": weight_pt, "tint": tint})
    if LIVE_DRAW:
        time.sleep(LINE_DELAY)
    return lid


def place_exact_display_lines(
    x1_px: float,
    y1_px: float,
    x2_px: float,
    y2_px: float,
    lines: list,
    font_style: str = "Bold",
    fill_swatch: str = "[Black]",
    align: str = "left",
    stretch_lines: bool = True,
    target_hscale: float = 0.88,
    lead_ratio: float = 0.92,
    underline: bool = False,
    v_justify: str = "top",
    inset_pt=None,
    max_pt_scale: float = 0.94,
):
    n_lines = len(lines)
    full_text = "\n".join(lines)
    box_h_pt = p(y2_px - y1_px)
    fit_rect = [p(x1_px), p(y1_px), p(x2_px), round(p(y2_px) + 10.0, 2)]
    r = cmd("frame.create", {
        "spread": 0,
        "rect": fit_rect,
        "content": "text",
        "text": "" if LIVE_DRAW else full_text
    })
    fid, sid = r["id"], r["story"]
    if LIVE_DRAW:
        cmd("object.stroke", {"ids": [fid], "swatch": "GsOrangeBorder", "weight": 0.8, "tint": 1.0})
        time.sleep(FRAME_DELAY)
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 0}},
            {"command": "text.insert", "params": {"text": full_text}},
            {"command": "object.stroke", "params": {"ids": [fid], "swatch": "[Black]", "weight": 0.0, "tint": 0.0}},
        ])
    if inset_pt is not None:
        cmd("object.textFrameOptions", {"ids": [fid], "columns": 1, "gutter": 0.0, "inset": inset_pt, "verticalJustification": v_justify})

    line_lead_pt = round(max(7.5, (box_h_pt * 0.92) / n_lines), 1)
    max_pt_by_box = round((box_h_pt / n_lines) * max_pt_scale, 1)

    lo = int(6.0 * 5)
    hi = int(min(92.0, max_pt_by_box) * 5)
    best_pt = 8.0
    best_hs = target_hscale

    while lo <= hi:
        mid = (lo + hi) // 2
        pt = round(mid / 5.0, 1)
        lead = round(max(line_lead_pt, pt * lead_ratio), 1)
        st = batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": "Gopika",
                "fontStyle": font_style,
                "size": pt,
                "leading": {"kind": "points", "value": lead},
                "fill": fill_swatch,
                "fillTint": 1.0,
                "hScale": target_hscale,
                "tracking": 0.0,
                "underline": underline
            }}},
            {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False, "spaceBefore": 0.0, "spaceAfter": 0.0}}},
            {"command": "story.get", "params": {"story": sid}},
        ])[-1]
        if st.get("lines") == n_lines and st.get("overset") is None:
            best_pt = pt
            lo = mid + 1
        else:
            hi = mid - 1

    if best_pt < max_pt_by_box * 0.88:
        for try_hs in (0.85, 0.80, 0.75, 0.70):
            lo2 = int(best_pt * 5)
            hi2 = int(min(92.0, max_pt_by_box) * 5)
            while lo2 <= hi2:
                mid = (lo2 + hi2) // 2
                pt = round(mid / 5.0, 1)
                lead = round(max(line_lead_pt, pt * lead_ratio), 1)
                st = batch([
                    {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                    {"command": "type.char", "params": {"attrs": {
                        "fontFamily": "Gopika",
                        "fontStyle": font_style,
                        "size": pt,
                        "leading": {"kind": "points", "value": lead},
                        "hScale": try_hs,
                        "tracking": 0.0,
                    }}},
                    {"command": "story.get", "params": {"story": sid}},
                ])[-1]
                if st.get("lines") == n_lines and st.get("overset") is None:
                    if pt > best_pt:
                        best_pt = pt
                        best_hs = try_hs
                    lo2 = mid + 1
                else:
                    hi2 = mid - 1

    final_lead = round(max(line_lead_pt, best_pt * lead_ratio), 1)
    batch([
        {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "Gopika",
            "fontStyle": font_style,
            "size": best_pt,
            "leading": {"kind": "points", "value": final_lead},
            "fill": fill_swatch,
            "fillTint": 1.0,
            "hScale": best_hs,
            "tracking": 0.0,
            "underline": underline
        }}},
        {"command": "type.para", "params": {"attrs": {"align": align, "hyphenate": False, "spaceBefore": 0.0, "spaceAfter": 0.0}}},
    ])

    _apply_latin_arial_runs(sid, full_text, best_pt, font_style)

    if stretch_lines:
        byte_cursor = 0
        for line_str in lines:
            b_len = utf8_len(line_str)
            b_start = byte_cursor
            b_end = byte_cursor + b_len
            byte_cursor = b_end + 1

            line_hs = best_hs
            max_hs_int = int(min(1.06, best_hs + 0.22) * 100)
            min_hs_int = int(best_hs * 100)
            for hs100 in range(max_hs_int, min_hs_int - 1, -2):
                hs_val = round(hs100 / 100.0, 2)
                st = batch([
                    {"command": "text.select", "params": {"story": sid, "anchor": b_start, "focus": b_end}},
                    {"command": "type.char", "params": {"attrs": {"hScale": hs_val, "tracking": 0.0}}},
                    {"command": "story.get", "params": {"story": sid}},
                ])[-1]
                if st.get("lines") == n_lines and st.get("overset") is None:
                    line_hs = hs_val
                    break
            for trk in range(18, -1, -3):
                st = batch([
                    {"command": "text.select", "params": {"story": sid, "anchor": b_start, "focus": b_end}},
                    {"command": "type.char", "params": {"attrs": {"hScale": line_hs, "tracking": float(trk)}}},
                    {"command": "story.get", "params": {"story": sid}},
                ])[-1]
                if st.get("lines") == n_lines and st.get("overset") is None:
                    break

    if LIVE_DRAW:
        time.sleep(CONTENT_DELAY)

    return fid, sid, best_pt


def place_exact_body_column(
    x1_px: float,
    y1_px: float,
    x2_px: float,
    y2_px: float,
    text: str,
    target_lines: int,
    font_style: str = "Regular",
    align: str = "leftJustified",
    first_indent_pt: float = 9.0,
    hi_pt: float = 11.8,
    lo_pt: float = 8.4,
    default_hscale: float = 0.88,
):
    box_h_pt = p(y2_px - y1_px)
    lead_pt = round(box_h_pt / max(1, target_lines), 2)
    clean_text = text.strip()
    r = cmd("frame.create", {
        "spread": 0,
        "rect": [p(x1_px), p(y1_px), p(x2_px), round(p(y2_px) + 5.0, 2)],
        "content": "text",
        "text": "" if LIVE_DRAW else clean_text
    })
    fid, sid = r["id"], r["story"]
    if LIVE_DRAW:
        cmd("object.stroke", {"ids": [fid], "swatch": "GsOrangeBorder", "weight": 0.8, "tint": 1.0})
        time.sleep(FRAME_DELAY)
        batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 0}},
            {"command": "text.insert", "params": {"text": clean_text}},
            {"command": "object.stroke", "params": {"ids": [fid], "swatch": "[Black]", "weight": 0.0, "tint": 0.0}},
        ])

    best_cfg = (10.0, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.06:
            continue
        for hs100 in (94, 90, 87, 84, 81, 78):
            hs = round(hs100 / 100.0, 2)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "Gopika",
                    "fontStyle": font_style,
                    "size": pt,
                    "leading": {"kind": "points", "value": lead_pt},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                    "hScale": hs,
                    "tracking": 0.0
                }}},
                {"command": "type.para", "params": {"attrs": {
                    "align": align,
                    "firstLineIndent": first_indent_pt,
                    "spaceBefore": 0.0,
                    "spaceAfter": 0.0,
                    "hyphenate": False
                }}},
                {"command": "story.get", "params": {"story": sid}},
            ])[-1]
            if st.get("overset") is None:
                lines_got = st.get("lines") or 0
                diff = abs(lines_got - target_lines)
                if lines_got == target_lines:
                    best_cfg = (pt, hs, 0.0)
                    best_diff = 0
                    break
                elif diff < best_diff:
                    best_diff = diff
                    best_cfg = (pt, hs, 0.0)
        if best_diff == 0:
            break

    pt, hs, trk = best_cfg
    batch([
        {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
        {"command": "type.char", "params": {"attrs": {
            "fontFamily": "Gopika",
            "fontStyle": font_style,
            "size": pt,
            "leading": {"kind": "points", "value": lead_pt},
            "fill": "[Black]",
            "fillTint": 1.0,
            "hScale": hs,
            "tracking": trk
        }}},
        {"command": "type.para", "params": {"attrs": {
            "align": align,
            "firstLineIndent": first_indent_pt,
            "spaceBefore": 0.0,
            "spaceAfter": 0.0,
            "hyphenate": False
        }}},
    ])
    _apply_latin_arial_runs(sid, clean_text, pt, font_style)
    if any("A" <= ch <= "Z" or "a" <= ch <= "z" or "0" <= ch <= "9" for ch in clean_text):
        st_after = cmd("story.get", {"story": sid})
        while (st_after.get("lines", 0) > target_lines or st_after.get("overset") is not None) and hs > 0.72:
            hs = round(hs - 0.02, 2)
            batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {"hScale": hs}}},
            ])
            _apply_latin_arial_runs(sid, clean_text, pt, font_style)
            st_after = cmd("story.get", {"story": sid})
    if LIVE_DRAW:
        time.sleep(CONTENT_DELAY)
    return fid, sid, pt, hs


# ==============================================================================
# 1. TOP RUNNING HEADER BAR & MAJOR VERTICAL COLUMN DIVIDERS
# ==============================================================================
print("Placing Page 2 running header & main vertical rules...")
build_running_header(2, place_png, draw_box, place_exact_display_lines)
draw_line(1068, 200, 1068, 3792, swatch="[Black]", weight_pt=0.9)
draw_line(1732, 200, 1732, 3792, swatch="[Black]", weight_pt=0.9)
place_png(84, 3805, 2718, 3858, "cmyk_footer_bar_p2.png")


# ==============================================================================
# 2. STORY 1: TOP-LEFT 3-COL BOXED FEATURE (JALEBI-FAFDA PRICES)
# ==============================================================================
print("Building Story 1 (Jalebi-Fafda Boxed Feature, Cols 1-3)...")
draw_box(84, 204, 1056, 1390, stroke_swatch="[Black]", stroke_weight_pt=2.2)
place_exact_display_lines(
    96, 216, 1044, 376,
    lines=[
        "દાયકા અગાઉ રૂપિયા ૪૫૦-૫૦૦ પ્રતિ કિલોએ",
        "વેચાતી જલેબીના ભાવ હવે રૂ. ૧૧૫૦ થી ૧૫૦૦"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_png(95, 386, 1044, 1065, "jalebi_fafda_photo.png")
place_exact_body_column(
    96, 1072, 1044, 1378,
    text="ફાફડા-જલેબીની જયાફત માણ્યા વગર વિજયા દશમીની ઉજવણી જાણે અધૂરી જ ગણાય છે. આવતીકાલે વિજયા દશમીનું પર્વ છે ત્યારે અમદાવાદમાં અંદાજે રૂપિયા ૧૫૦ કરોડથી રૂપિયા ૨૦૦ કરોડના ફાફડા-જલેબીનું વેચાણ થશે. અમદાવાદમાં ફાફડા રૂપિયા ૭૫૦-રૂપિયા ૮૫૦ પ્રતિ કિલો જ્યારે જલેબી રૂપિયા ૧૧૫૦-રૂપિયા ૧૫૦૦ પ્રતિ કિલોના ભાવે વેચાઈ રહી છે. જેમાં પ્રીમિયમ કેસર જલેબીના ભાવ રૂપિયા ૧૫૦૦ છે. રૂપિયા ૧૫૦૦ પ્રતિ કિલોના ભાવે જલેબીમાં એક નંગ માટે અંદાજે રૂપિયા ૩૦ ચૂકવવા પડે. વર્ષ ૨૦૧૬માં ફાફડા રૂપિયા ૩૬૦-રૂપિયા ૪૫૦ પ્રતિ કિલો, જલેબી રૂપિયા ૪૫૦-રૂપિયા ૫૦૦ પ્રતિ કિલોએ વેચાતી હતી. આ બંને ટોચની કિંમતની સરખામણી કરીએ તો ફાફડામાં અંદાજે ૧૬૭ ટકાથી ૨૩૩ ટકા જ્યારે જલેબીમાં અંદાજે ૨૬૪ ટકાથી ૩૪૪ ટકાનો વધારો થયો છે. આવતીકાલે મોટાભાગની સોસાયટીમાં ફાફડા જલેબીનું મેનુ ફિક્સ કરી દેવાયું છે. કેટલાક લોકોએ ટાઈમ સ્લોટ પ્રમાણે ફાફડા જલેબીના ઓર્ડર આપી દીધા છે. અનેક સોસાયટી કે જ્યાં મોટી સંખ્યામાં ખેલૈયાઓ એકત્ર થતાં હોય તેમણે નાસ્તાના કાઉન્ટર ભાડે આપીને કમાણી કરી લેવામાં આવી છે.                                                          (તસ્વીર : સુરેશ મિસ્ત્રી)",
    target_lines=10,
    font_style="Bold",
    first_indent_pt=0.0,
)


# ==============================================================================
# 3. STORY 2: MIDDLE-LEFT 3-COL STORY (VASTRAPUR GANTHIYA / HARMFUL FRYING OIL)
# ==============================================================================
print("Building Story 2 (Vastrapur Ganthiya / Harmful Oil, Cols 1-3)...")
place_exact_display_lines(
    86, 1400, 1052, 1446,
    lines=["વસ્ત્રાપુર ગાંઠિયા સીલ, ૧૫ સ્થળેથી ૨૪ નમૂના લેવાયા"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(86, 1451, 1054, 1451, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 1456, 1052, 1640,
    lines=[
        "૮૦૦ રૂપિયના કિલો ફાફડા, જલેબીમાં",
        "પણ હાનિકારક દાઝીયા તેલનો ઉપયોગ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    390, 1644, 554, 1670,
    lines=["અમદાવાદ, સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 1672, 554, 1796,
    text="અમદાવાદ શહેરમાં દશેરાના પર્વમાં હજારો કિલો ફાફડા-જલેબી લોકો આરોગી જાય છે. આ માંગનો ગેરલાભ ઉઠાવી ભેળસેળિયા તત્વો જાહેર આરોગ્ય સાથે ચેડાં કરવામાં કોઈ કસર છોડતા નથી. ત્યારે મ્યુનિ.ના ફૂડ વિભાગ દ્વારા આજે",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 1650, 568, 1794, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 1646, 1052, 1796,
    text="આખા શહેરમાં ૧૫ સ્થળેથી ફાફડા-જલેબીના ૨૪ નમૂના લઈ તપાસ માટે મોકલ્યા છે. જોકે તેનું પરિણામ આવશે, ત્યાં સુધીમાં દુકાનો પરના ફાફડા-જલેબી વેચાઈ ગયા હશે! બીજી તરફ ખાદ્ય તેલમાં ટીપીસીનું પ્રમાણ વધારે આવતા વસ્ત્રાપુર તળાવ સામેનું વસ્ત્રાપુર ગાંઠિયા સીલ કરી દેવાયું છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 1802, 1052, 1918,
    lines=[
        "શહેરમાં શેરીએ શેરીએ તૈયાર થયેલા હજારો કિલો",
        "ફાફડા-જલેબીમાં સબ સલામત! ફક્ત ૧૦ને નોટિસ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    86, 1922, 392, 2010,
    text="અમદાવાદ મ્યુનિ.ના ફૂડ વિભાગ દ્વારા આજે શહેરમાં ફાફડા-જલેબી અંગે તપાસ હાથ ધરવામાં આવી હતી. જેમાં",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(404, 1926, 404, 2008, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 1922, 718, 2010,
    text="બદલ ૧૦ એકમોને નોટિસ આપી રૂ.૪૦ હજાર પેનલ્ટી વસૂલ કરાઈ છે. જ્યારે વસ્ત્રાપુર તળાવ સામે સૈલાભ",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(730.5, 1926, 730.5, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 1922, 1052, 2010,
    text="ઉલ્લેખનિય છે કે, અહીં ફાફડા અને જલેબી ૮૦૦ રૂપિયે કિલો વેચાય છે. આટલી તોતિંગ રકમ વસૂલ્યા બાદ પણ હાનિકારક",
    target_lines=3,
    first_indent_pt=0.0,
)

# 2-Col Callout Box (x=86..724, y=2017..2401) + Col 3 Oil Meter Photo
draw_box(86, 2017, 724, 2401, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    98, 2024, 712, 2108,
    lines=[
        "બેફામ નફાખોરી : ફાફડાની પડતર કિંમત",
        "૧૭૫ રૂપિયા અને જલેબીની ૨૨૫!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    98, 2112, 712, 2394,
    text="આરોગ્યની વાત એક તરફ રાખીએ તો અમદાવાદ શહેરમાં ફાફડા-જલેબીના નામે બેફામ નફાખોરી પણ થઈ રહી છે. ફરસાણના વેપારીઓના જણાવ્યા અનુસાર ચણાનો લોટ, તેલ, મસાલા, રાંધણ ગેસ વગેરેની કિંમત ગણવામાં આવે તો એક કિલો ફાફડાની પડતર કિંમત વધીને રૂ.૧૭૫ પ્રતિ કિલો માંડ થાય છે. આજે પણ શહેરમાં ૨૫૦ રૂપિયે કિલો શુદ્ધ ફરસાણ વેચાય જ છે. પરંતુ મોટાભાગની દુકાનોમાં ફાફડાના ૭૦૦થી ૮૦૦ રૂપિયા ભાવ વસૂલાય છે. આવી રીતે જ જલેબીની પડતર કિંમત ૨૨૫ રૂપિયા પ્રતિ કિલોથી વધારે આવે નહીં, તેમાં પણ તોતિંગ નફો વસૂલાય છે. કલેક્ટર કચેરીના પુરવઠા વિભાગ દ્વારા ક્યારેય આ દિશામાં કોઈ તપાસ કરીને પગલાં લેવાતા નથી.",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_png(748, 2013, 1055, 2408, "oil_meter_photo.png")

place_exact_body_column(
    86, 2408, 392, 2586,
    text="શહેરના નામી-અનામી એવા ૧૪ સ્થળો પરથી ફાફડા, જલેબી, ચટણી, ખાદ્ય તેલ, મરચુ પાઉડર, કઢી વગેરે વસ્તુઓના ૨૪ નમૂના લઈને તપાસ માટે પબ્લિક હેલ્થ લેબોરેટરીમાં મોકલવામાં આવ્યા છે. આ ચેકિંગ દરમિયાન થોડી અનિયમિતતાઓ",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(404, 2410, 404, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 2408, 718, 2586,
    text="કોમ્પલેક્સમાં આવેલા વસ્ત્રાપુર ગાંઠિયા ખાતે તપાસ કરતા અહીં ખાદ્ય તેલમાં ટીપીસી એટલે કે ટોટલ પોલાર કમ્પાઉન્ડનું પ્રમાણ ૩૨ આવ્યું હતું. જે સામાન્ય રીતે ૨૫થી વધુ ન હોવું જોઈએ. આ બેદરકારી બદલ આ એકમ સીલ કરાયું છે. અત્રે",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    744, 2410, 1052, 2586,
    text="એવા દાઝીયા તેલનો ઉપયોગ થઈ રહ્યો હતો. બીજી તરફ શહેરમાં શેરીએ શેરીએ હજારો કિલો ફાફડા-જલેબી તૈયાર થયા છે. પરંતુ શહેરમાં સબસલામત હોય તેમ આંગળીના વેઢે ગણી શકાય એટલા એકમો સામે જ કાર્યવાહી થઈ છે.",
    target_lines=6,
    first_indent_pt=0.0,
)


# ==============================================================================
# 4. STORY 3: BOTTOM-LEFT 3-COL STORY (GARBA FAKE PASS AI QR SCAM)
# ==============================================================================
print("Building Story 3 (Garba Fake Pass AI QR Scam, Cols 1-3)...")
draw_line(84, 2592, 1056, 2592, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    187, 2602, 951, 2652,
    lines=["ગુનો દાખલ થયા બાદ પણ કેટલાક પાસ વેચ્યા !"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(187, 2657, 951, 2657, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 2664, 1052, 2848,
    lines=[
        "અમદાવાદનાં જાણીતા ગરબાના નકલી",
        "પાસ પર QR લગાવવા AIનો ઉપયોગ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    390, 2858, 554, 2884,
    lines=["અમદાવાદ,સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 2886, 554, 3014,
    text="અમદાવાદ અને ગુજરાતના વિવિધ શહેરોના ૨૫થી વધુ મોટા ગરબાના આયોજનના બોગસ પાસનું ઈન્સ્ટાગ્રામ પરથી વેચાણ કરવાના મામલે રાજસ્થાનથી ઝડપાયેલા આરોપીઓની પુછપરછમાં ચોંકાવનારો ખુલાસો થયો હતો કે તે ઈન્સ્ટાગ્રામ",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 2862, 568, 3012, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2858, 1052, 3014,
    text="પરથી વિવિધ આયોજનની ઈમેજ મેળવીને તેને એઆઈથી એડિટ કરીને બુકીંગના ક્યુઆર કોડ લગાવતા હતા. પોલીસને એઆઈથી એડિટ કરાયેલી વિવિધ ઈમેજ અને ગ્રાહકો સાથે થયેલી વોટ્સએપ ચેટ પણ મળી આવી હતી. જે અંગે પોલીસે વધુ તપાસ શરૂ કરી છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 3020, 1052, 3132,
    lines=[
        "આરોપી પાસેથી ચેટજીપીટી સહિતના એઆઈ ટુલ્સ",
        "અને ગ્રાહકો સાથે થયેલી વોટસ એપ ચેટ મળી આવી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    86, 3140, 392, 3792,
    text="નવરાત્રીના મોટા આયોજકો પાસનું વેચાણ કરવા માટે ઓનલાઈન પ્લેટફોર્મનો ઉપયોગ કરતા હોય છે. જેનો ગેરલાભ લઈને કેટલાંક લોકોએ ઈન્સ્ટાગ્રામ અને ફેસબુક પર બોગસ આઈડી બનાવીને તેના દ્વારા વિવિધ આયોજનોની ટિકિટ અડધાથી ઓછી કિંમતે વેચાણ કરવાના કૌભાંડમાં સાયબર ક્રાઈમ દ્વારા વિરેન્દ્રસિંહ રાઠોડ અને કિશનસિંહ રાઠોડની રાજસ્થાનથી ધરપકડ કરવામાં આવી હતી. બંને જણાએ લોકોને વિશ્વાસમાં લેવા માટે ઈન્સ્ટાગ્રામ પર પેઈડ આઈડી બનાવ્યા હતા. જેથી પ્રોફેશનલ લાગે અને તેમની એક એક પોસ્ટ ૪૦ હજાર લોકો સુધી પહોંચતી હતી. નકલી પાસ તૈયાર કરવા માટે તે ચેટ જીપીટી એઆઈ એપ્લીકેશનનો ઉપયોગ કરતા હતા અને ગરબાના વિવિધ આયોજકોના ઈન્સ્ટાગ્રામ આઈડીથી ઈમેજનો સ્ક્રીન શોટ લઈને તેને એઆઈથી એડિટ કરીને વચ્ચે બુકીંગના ક્યુઆર કોડ લગાવતા હતા. જેથી પાસ વાસ્તવિક",
    target_lines=21,
    first_indent_pt=10.0,
    hi_pt=10.8,
)
draw_line(404, 3144, 404, 3242, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3140, 718, 3236,
    text="દેખાતો હતો. તે વોટ્સએપ પર વિવિધ આયોજકોના ગરબાના પાસની વિગતો પણ આપતા હતા. પોલીસને કેટલાંક",
    target_lines=3,
    first_indent_pt=0.0,
)
# Col 2 Event List Table Box (x=416..724, y=3252..3791)
draw_box(416, 3252, 724, 3791, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    424, 3258, 716, 3336,
    lines=[
        "આરોપીઓ ક્યા ક્યા",
        "ઈવેન્ટના પાસ વેચ્યા હતા"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(416, 3343, 724, 3343, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    422, 3346, 718, 3376,
    lines=["ક્રમ  ઈવેન્ટનું નામ          પાસની સંખ્યા"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
draw_line(416, 3380, 724, 3380, swatch="[Black]", weight_pt=0.8)
place_exact_display_lines(
    422, 3384, 650, 3786,
    lines=[
        "૧.   આફ્ટર ૧૧ પ૯",
        "૨.   મંડપમ",
        "૩.   ચોકના ગરબા",
        "૪.   ઓફબીટ",
        "૫.   વનરાત્રી",
        "૬.   રંગ મોરલા",
        "૭.   એઈએમએસ રાત્રી",
        "૮.   રાતલડી",
        "૯.   ઈનર સર્કલ",
        "૧૦. પંચમના ગરબા",
        "૧૧. અનંત એક્સીપીરીયન્સ",
        "૧૨. ઈફેટોન",
        "૧૩. સફેદ પરિન્દે",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    652, 3384, 716, 3786,
    lines=[
        "૧૧૮", "૧૬૭", "૧૨૨", "૯૭", "૫૧", "૪૯", "૩૧", "૩૧", "૨૦", "૧૨", "૬", "૬", "૬"
    ],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
draw_line(734, 3144, 734, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3140, 1052, 3792,
    text="ગ્રાહકો સાથે થયેલી ચેટની વિગતો પણ મળી છે.\nગરબાના બનાવટી પાસનું બુકીંગ થયાની જાણ તે ઈ-મેઈલ પણ કરતા હતા. આ માટે તેમણે ૨૦થી વધુ બોગસ ઈ-મેઈલ આઈડી પણ બનાવ્યા હતા. સાથેસાથે નાણાંના વ્યવહાર કરવા માટે મ્યુલ બેંક એકાઉન્ટનો ઉપયોગ કરતા હતા. આરોપીઓ વિરૂદ્ધ સાયબર ક્રાઈમમાં તેમજ સાંતેજમાં ગુનો નોંધાયો હતો. જેથી પોલીસથી બચવા અને આ દરમિયાન પણ પાસનું વેચાણ કરવા માટે જોધપુર, બિકાનેર અને સીકરમાં અલગ અલગ સ્થળો પર છુપાતા હતા. પોલીસને જાણવા મળ્યું હતું કે વિરેન્દ્રસિંહ રાઠોડે અમદાવાદની એક કોલેજમાં બીબીએનો અભ્યાસ કર્યો હતો. જેથી અમદાવાદની નવરાત્રી અંગે સારી એવી માહિતી ધરાવતો હતો. જેથી તેણે અન્ય આરોપી સાથે મળીને આ સમગ્ર કૌભાંડ આચર્યું હતું.",
    target_lines=21,
    first_indent_pt=0.0,
)


# ==============================================================================
# 5. STORY 4: COLS 4-5 TOP (VIJAYADASHAMI 60-FT RAVANA DAHAN)
# ==============================================================================
print("Building Story 4 (Vijayadashami 60-ft Ravana Dahan, Cols 4-5)...")
place_exact_display_lines(
    1082, 202, 1716, 246,
    lines=["શસ્ત્ર પૂજન, રામ લીલા સહિતના આયોજનો"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1082, 249, 1716, 249, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 254, 1718, 422,
    lines=[
        "આજે વિજયાદશમી : ૬૦",
        "ફૂટના રાવણનું દહન કરાશે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 426, 1718, 452,
    lines=["અમદાવાદ,સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 454, 1718, 544,
    text="અસત્ય પર સત્યના વિજયના પર્વ ‘વિજયા દશમી’ ની આવતીકાલે આસ્થા-ઉલ્લાસપૂર્વક ઉજવણી કરવામાં આવશે. શાસ્ત્રવિદોના મતે આવતીકાલે બપોરે ૧૨:૫૦થી વિજયાદશમીનો પ્રારંભ થશે.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 548, 1718, 642,
    lines=[
        "શારદીય નવરાત્રીની સમાપ્તિ થશે, બપોરે",
        "૧૨:૫૦ પછી વિજયા દશમીનો પ્રારંભ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 646, 1386, 1005,
    text="ભાડજના હરેકૃષ્ણ મંદિર ખાતે આવતીકાલે રાત્રે ૮ કલાકે ૬૦ ફૂટના રાવણના પૂતળાનું દહન કરાશે. રાવણનું પૂતળું બનાવવા માટે છેલ્લા એક મહિનાથી ઉત્તર પ્રદેશના કારીગરો આવેલા છે. રાવણ દહન પૂર્વે સાંજે ૬ કલાકે સીતા-રામ સ્વર્ણ રથયાત્રા અને સાંજે ૬:૩૦ના રામ લીલાનું મંચન કરવામાં આવશે. ઈસ્કોન મંદિરમાં સાંજે ૬:૩૦ના સંધ્યા આરતી બાદ મંદિરના પાછળના પ્રાંગણમાં સાંજે ૭:૩૦ના ૨૫ ફૂટના રાવણના પૂતળાનું દહન કરાશે.\nઆ ઉપરાંત એઈએસ ગ્રાઉન્ડ-થલતેજ",
    target_lines=12,
    first_indent_pt=10.0,
)
draw_line(1399.5, 650, 1399.5, 1004, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 646, 1718, 1005,
    text="ખાતે સાંજે ૫:૩૦ના ૫૧ ફૂટ ઊંચા રાવણ, ૩૫-૩૫ ફૂટના મેઘનાદ-કુંભકર્ણના પૂતળાનું દહન થશે. આ ઉપરાંત આતશબાજી, ડાયરા સહિતના કાર્યક્રમનું પણ આયોજન કરાશે. રખિયાલ, ખોખરા ખાતે પણ રાવણ દહનનું આયોજન કરાયું છે. કેટલીક સોસાયટી અને ક્લબમાં પણ રાવણ દહનનું આયોજન કરવામાં આવેલું છે. રાવણ દહનને પગલે ફાયર બ્રિગેડ દ્વારા પણ તૈયારીઓ પૂરી કરી દેવામાં આવી છે. રાવણ દહન અંગે જ્યાંથી પણ અરજી આવી છે ત્યાં ફાયર બ્રિગેડની ખાસ ગાડીઓ તૈનાત રહેશે.",
    target_lines=12,
    first_indent_pt=0.0,
)


# ==============================================================================
# 6. STORY 5: COLS 4-5 UPPER-MID (RTE 54 STUDENTS SOLARIS SCHOOL PENALTY)
# ==============================================================================
print("Building Story 5 (RTE Solaris School Penalty, Cols 4-5)...")
draw_line(1080, 1013, 1720, 1013, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 1018, 1718, 1060,
    lines=["નિયમ મુજબ પોર્ટલ પર એન્ટ્રી જ ન કરીને"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1065, 1718, 1065, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1070, 1718, 1220,
    lines=[
        "RTEના ૫૪ બાળકોને સહાયથી",
        "વંચિત રાખનારી સ્કૂલને પેનલ્ટી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 1222, 1718, 1246,
    lines=["અમદાવાદ,સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 1248, 1718, 1398,
    text="આરટીઈમાં પ્રવેશ લેનારા બાળકોને દર વર્ષે સરકાર દ્વારા ૩ હજાર રૂપિયાની આર્થિક સહાય આપવામાં આવે છે.પરંતુ આ સહાય માટે સ્કૂલે બાળકોની આરટીઈ પોર્ટલ પર ફરજીયાત એન્ટ્રી કરવાની હોય છે.શહેર ડીઈઓના જણાવ્યા મુજબ સોલાની સોલારીસ પબ્લિક સ્કૂલે બાળકોની એન્ટ્રી જ ન કરતા ચાલુ વર્ષે ૫૪ બાળકો આરટીઈની સહાયથી વંચિત રહ્યા છે.જેથી આ સ્કૂલને દસ હજાર રૂપિયાનો દંડ કરાયો છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 1402, 1718, 1498,
    lines=[
        "સોલા વિસ્તારની સોલારિસ પબ્લિક સ્કૂલને એક્ટના",
        "નિયમ મુજબ ડીઈઓ દ્વારા રૂપિયા ૧૦ હજાર દંડ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 1504, 1386, 1806,
    text="આ વર્ષે આરટીઈ હેઠળના કુલ ૮૦ હજારથી વધુ બાળકોને ૩ હજાર રૂપિયાની સહાય ચુકવી દેવામાં આવી છે.પરંતુ સોલારીસ પબ્લિક સ્કૂલમાં બાળકોને સહાય ન મળતા એક વાલીએ ફરિયાદ કરી હતી.જેના આધારે તપાસ કરતા ધ્યાને આવ્યુ હતું કે સોલારીસ સ્કૂલે આરટીઈના બાળકોની એન્ટ્રી આરટીઈ ડીબીએમએસ પોર્ટલ પર કરી જ ન હતી. જુદા જુદા ધોરણના કુલ ૫૪ બાળકો આ સ્કૂલમાં",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(1399.5, 1508, 1399.5, 1804, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1504, 1718, 1806,
    text="આરટીઈ હેઠળ પ્રવેશ મેળવીને ભણી રહ્યા છે.સ્કૂલે બેદરકારી દાખવીને એન્ટ્રી જ ન કરતા બાળકો સહાયથી વંચિત રહ્યા હતા. જેથી અમદાવાદ શહેર ડીઈઓએ આરટીઈ એક્ટની જોગવાઈ મુજબ સ્કૂલને દસ હજાર રૂપિયાનો દંડ ફટકાર્યો છે.જો કે સ્કૂલની ભૂલને લીધે બાળકો સહાયથી વંચિત રહી ગયા છે ત્યારે હવે બાળકોની એન્ટ્રી કરાવવા સ્કૂલને આદેશ કરાયો છે. હવે એન્ટ્રી બાદ જ સહાય મળશે.",
    target_lines=10,
    first_indent_pt=0.0,
)


# ==============================================================================
# 7. STORY 6: COLS 4-5 LOWER-MID (RAKHIAL AL FALAH ISLAMIC SCHOOL)
# ==============================================================================
print("Building Story 6 (Rakhial Al Falah School, Cols 4-5)...")
draw_line(1080, 1810, 1720, 1810, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 1816, 1718, 1860,
    lines=["રખિયાલની અલ ફલાહ ઈસ્લામિક શાળામાં"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1864, 1718, 1864, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1868, 1718, 2010,
    lines=[
        "મંજૂરી વિના વર્ગો ચલાવાતા સ્કૂલની",
        "માન્યતા રદ કરવા સરકારને રિપોર્ટ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 2012, 1718, 2036,
    lines=["અમદાવાદ,સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2038, 1718, 2188,
    text="અમદાવાદના રખિયાલ વિસ્તારની અલ ફલાહ ઈસ્લામિક સ્કૂલ સામે મળેલી ફરિયાદના આધારે અમદાવાદ શહેર ડીઈઓ દ્વારા તપાસ કરાઈ હતી.તપાસ રિપોર્ટ મુજબ સ્કૂલ દ્વારા ધો.૧થી૫માં માન્ય વર્ગો કરતા વધુ વિદ્યાર્થીઓને પ્રવેશ આપવામાં આવેલ છે તેમજ મંજૂરી વિના ધો.૬થી૮માં વર્ગો ચાલુ રાખવામાં આવ્યા છે.આ તપાસ રિપોર્ટના આધારે શહેર ડીઈઓએ પ્રાથમિક શિક્ષણ વિભાગને આ સ્કૂલની માન્યતા રદ કરવા અને કાયદેસરની કાર્યવાહીની મંજૂરી આપવા દરખાસ્ત કરી છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 2192, 1718, 2288,
    lines=[
        "સ્કૂલ સામે પોલીસ ફરિયાદ કરવાની મંજૂરી આપવા,",
        "માન્યતા રદ કરવા અમદાવાદ ડીઈઓની દરખાસ્ત"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 2294, 1386, 2826,
    text="સરકારના પ્રાથમિક શિક્ષણ વિભાગની નિયામક કચેરીને અમદાવાદ શહેર ડીઈઓ દ્વારા અલ ફલાહ ઈસ્લામિક સ્કૂલ સામેનો તપાસ રિપોર્ટ મોકલીને માન્યતા રદ કરવા ભલામણ કરવામાં આવી છે.ડીઈઓએ જણાવ્યુ હતું કે અધિકારીઓ દ્વારા ગત ઓગસ્ટમાં તપાસ રિપોર્ટ રજૂ કરાયો હતો.ત્યારબાદ સ્કૂલને ૧૦ હજારનો દંડ કરવામાં આવ્યો હતો અને ૨૪ ઓગસ્ટે સુનાવણીમાં રૂબરૂ સ્કૂલના પ્રતિનિધિઓને બોલાવાયા હતા.ત્યારબાદ આરટીઈ મુજબની તપાસ કમિટી રચાઈ હતી.જેનો રિપોર્ટ પણ ૧૫ ઓક્ટોબરે રજૂ કરાયો હતો.આ રિપોર્ટ મુજબ ૨૦૧૮માં સ્કૂલને ધો.૧થી૫ની જ મંજૂરી મળી છે.પરંતુ રૂબરૂ તપાસમાં ૬થી૮ના વિદ્યાર્થીઓ અલગ અલગ વર્ગમાં જોવા મળ્યા હતા.ધો.૬થી૮ના",
    target_lines=17,
    first_indent_pt=10.0,
)
draw_line(1399.5, 2298, 1399.5, 2824, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 2294, 1718, 2826,
    text="વિદ્યાર્થીઓના સીટીએસ પોર્ટલના ટ્રેકિંગની વિગતો મુજબ હાલ અલ ફલાહ ઈંગ્લિશ મીડિયમ સ્કૂલમાં જે વિદ્યાર્થીઓ ભણે છે તેઓની તપાસ કરતા યુડાયસ નંબર મુજબ ચેરી બ્લોસમ ઈંગ્લિશ સ્કૂલ નામે જોવા મળે છે.આ સ્કૂલ બંધ થયેલ છે.આમ આ સ્કૂલમાં ધો.૧થી૫માં માન્ય વર્ગો કરતા વધુ વિદ્યાર્થીઓને પ્રવેશ અપાયા છે અને મંજૂરી વિના ધો.૬થી૮ની શાળા ચલાવાય છે.સ્કૂલમાં કુલ ૧૨૫૨ વિદ્યાર્થીઓ ધો.૧થી૫માં છે.આમ તપાસ દરમિયાન ધ્યાને આવ્યુ કે અલ ફલાહ સ્કૂલ દ્વારા કેટલાય વિદ્યાર્થીઓના અભ્યાસ તેમજ ભવિષ્ય સાથે ચેડા કરવામાં આવ્યા છે. અમદાવાદ શહેર ડીઈઓએ આ સ્કૂલની માન્યતા રદ કરવા અને સ્કૂલ સામે પોલીસ ફરિયાદની મંજૂરી આપવા સરકારને દરખાસ્ત મોકલી છે.",
    target_lines=17,
    first_indent_pt=0.0,
)


# ==============================================================================
# 8. STORY 7: COLS 4-5 BOTTOM (SARKHEJ-SINDHU BHAVAN GARBA FAKE TICKETS)
# ==============================================================================
print("Building Story 7 (Sankalp Nagari Garba Fake Tickets, Cols 4-5)...")
draw_line(1080, 2832, 1720, 2832, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 2838, 1718, 2880,
    lines=["સરખેજ-સિંધુ ભવન ખાતે સંકલ્પ નગરીમાં"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 2882, 1718, 2882, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 2888, 1718, 3048,
    lines=[
        "ગરબામાં વધુ પડતી ભીડ જોતાં",
        "નકલી ટિકિટનું કૌભાંડ ઝડપાયું"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 3052, 1718, 3078,
    lines=["અમદાવાદ,સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 3080, 1718, 3230,
    text="શહેરના સરખેજ સિંધુ ભવન રોડ યોજવામાં આવેલા સંકલ્પનગરી ગરબાના બનાવટી પાસ છપાવીને બારોબાર વેચાણ કરવાનું મોટું કૌભાંડ સામે આવ્યું છે. જેમાં ઓફલાઈન વેચાણ કરવામાં આવતા પાસ કરતા વધારે ભીડ આવતા આયોજકોને શંકા ઉપજી હતી. જેથી તેમણે શુક્રવારે યોજાનારા ગરબાના પાસની ડિઝાઈન બદલી હતી અને તે દિવસે આવેલા નકલી પાસ લઈને આવેલા લોકો મળી આવ્યા હતા. જે પાસ વિપુલ ભીમાણી નામના વ્યક્તિએ વેચાણ કર્યાનું સામે આવ્યું હતું. આ મામલે સરખેજ પોલીસે ગુનો નોંધીને તપાસ શરૂ કરી છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 3234, 1718, 3334,
    lines=[
        "આયોજકોએ શંકા બાદ પાસની ડિઝાઈન બદલતા",
        "ગરબાના નકલી પાસ બનાવનાર આરોપી ઝડપાયો"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 3340, 1386, 3792,
    text="બોપલમાં આવેલા અરિહંત કુટીર બંગ્લોઝમાં રહેતા દ્રુપદાસ ગાંધીએ સરખેજ સિંધુ ભવન રોડ ઓડાના પ્લોટમાં તેમના ભાગીદારો સાથે મળીને સંકલ્પનગરી ગરબાનું આયોજન કર્યું હતું. તેમણે ઓનલાઈન પાસ વેચાણ સાથે ઓફલાઈન પાસ વેચાણ કરવા માટે એક દિવસના આઠ હજાર લેખે દશ દિવસના ૮૦ હજાર પાસ છપાવ્યા હતા. જેનું વેચાણ ગરબા ગ્રાઉન્ડની બહાર કરવામાં આવતું હતું. નવરાત્રીના પ્રથમ ત્રણ દિવસ દરમિયાન આયોજકોના ધ્યાનમાં આવ્યું હતું કે ઓફલાઈન ગરબાના પાસનું જે રીતે વિતરણ થાય તેના કરતા",
    target_lines=15,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3344, 1399.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 3340, 1718, 3792,
    text="વધારે લોકો ગરબા રમવા માટે આવે છે. જેથી નકલી પાસનું વેચાણ થતું હોવાની આશંકા વ્યક્ત કરવામાં આવી હતી. બાદમાં આયોજકોએ શુક્રવારે વેચાણ માટે અગાઉ તૈયાર કરેલા પાસ રદ કરીને નવી ડિઝાઈન તૈયાર કરી હતી. આ દિવસે કેટલાંક લોકો સાંજના સમયે અગાઉથી રદ કરાયેલા પાસ લઈને આવ્યા હતા. જેથી તે પૈકી કેટલાંક લોકોને પુછતા જાણવા મળ્યું હતું કે વિપુલ ભીમાણી નામના વ્યક્તિ પાસેથી આ પાસ ખરીદ્યા હતા. આમ, વિપુલ ભીમાણી નામનો વ્યક્તિ સંકલ્પનગરીના નકલી પાસ છપાવીને વેચાણ કરતો હતો.",
    target_lines=15,
    first_indent_pt=0.0,
)


# ==============================================================================
# 9. STORY 8: COLS 6-8 TOP (RIVERFRONT 60-CR MULTILEVEL PARKING)
# ==============================================================================
print("Building Story 8 (Riverfront Multilevel Parking, Cols 6-8)...")
place_exact_display_lines(
    1744, 202, 2715, 254,
    lines=["તોતિંગ ખર્ચ બાદ પ્રજાને સુવિધા નહીં, ભાડાની આવક પણ શૂન્ય"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 258, 2715, 258, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 264, 2715, 448,
    lines=[
        "રિવરફ્રન્ટનું ૬૦ કરોડનું ધોળા હાથી સમાન",
        "મલ્ટિલેવલ પાર્કિંગ એક વર્ષથી ઘરજમાઈ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2030, 456, 2208, 482,
    lines=["અમદાવાદ, સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 484, 2208, 604,
    text="અમદાવાદ મ્યુનિ.ની સાથે તેને સંલગ્ન એએમટીએસ, બીઆરટીએસ કે સાબરમતી રિવરફ્રન્ટ ડેવલપમેન્ટ કોર્પોરેશન જેવા એકમો પણ પ્રજાના પૈસાનું પાણી કરી રહ્યા હોવાની વિગતો વારંવાર સામે આવતી રહે છે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 460, 2220, 602, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 456, 2715, 604,
    text="એસઆરએફડીસીએલ તંત્રની અણઆવડતના નમૂના સમાન ફ્લાવર પાર્ક સામેનું રૂ.૬૦ કરોડનું મલ્ટિલેવલ પાર્કિંગ એક વર્ષથી ઘરજમાઈ પડ્યું છે. તોતિંગ રકમનો ખર્ચ કર્યા બાદ પ્રજાને નથી તો પાર્કિંગની સુવિધા મળી રહી કે નથી તંત્રને ભાડાની આવક થઈ રહી!",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 608, 2715, 724,
    lines=[
        "તંત્રની અણઆવડતનો નમૂનો : હવે એકથી પાંચ માળનું",
        "પાર્કિંગ રૂપિયા ૩૬.૪૨ લાખમાં ભાડે આપવા કવાયત્"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 728, 2052, 820,
    text="અમદાવાદના સાબરમતી રિવરફ્રન્ટ પર ફ્લાવર પાર્ક સામે આવેલા મલ્ટિલેવલ પાર્કિંગના એકથી પાંચ માળ રૂ.૩૬.૪૨",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(2064, 732, 2064, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 728, 2382, 820,
    text="સ્માર્ટ સિસ્ટમથી લોકો પૂરા પરિચિત થાય, ત્યાં સુધીમાં તો તેના વળતા પાણી શરૂ થઈ ગયા હતા. એકાદ વર્ષ પહેલાં જ્યારે આ",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(2395.5, 732, 2395.5, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 728, 2715, 820,
    text="અહીં પાર્કિંગની સુવિધા બંધ છે. માટે લોકોને તેનો લાભ મળતો નથી, સામાપક્ષે તંત્રને પણ કોઈ આવક થઈ રહી નથી.",
    target_lines=3,
    first_indent_pt=0.0,
)

# 3-Col Double-Bordered Photo & Story Box (x=1744..2716, y=832..1167)
draw_box(1744, 832, 2716, 1167, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(1754, 842, 2706, 1157, stroke_swatch="[Black]", stroke_weight_pt=0.8)
place_png(1756, 843, 2167, 1157, "riverfront_parking_photo.png")
place_exact_display_lines(
    2176, 848, 2700, 930,
    lines=[
        "ભાડું ઘટાડવા તંત્રનું તિકડમ્ : ૧૫૦ ટુવ્હીલર અને",
        "૩૫૦ ફોરવ્હીલરનું પાર્કિંગ કાપી નંખાયું"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2176, 934, 2700, 1152,
    text="સાબરમતી રિવરફ્રન્ટ ડેવલપમેન્ટ કોર્પોરેશનના અધિકારીઓએ પાર્કિંગનું ભાડું ઘટાડવા માટે એક તિકડમ્ કર્યું છે. આ પાર્કિંગમાં આમ તો ૧૦૦૦થી વધુ ટુવ્હીલર અને ૭૦૦થી વધુ ફોરવ્હીલર પાર્ક થઈ શકે તેવી વ્યવસ્થા છે. પરંતુ નવા ટેન્ડર મુજબ પહેલા અને બીજા માળે ૮૭૬ ટુવ્હીલર તથા ૩૭૨ ફોરવ્હીલર પાર્કિંગની વ્યવસ્થા બતાવવામાં આવી છે. એટલે કે ૫૦૦ વાહનોના પાર્કિંગને કાપી નાંખવામાં આવ્યા છે.",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Parking Rate Table (Cols 6-7, x=1744..2384, y=1179..1441)
draw_box(1825, 1179, 2310, 1228, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1835, 1184, 2300, 1224,
    lines=["મલ્ટિલેવલ પાર્કિંગના ભાડાનો દર"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
for ry in (1234, 1268, 1302, 1336, 1370, 1404, 1441):
    draw_line(1744, ry, 2384, ry, swatch="[Black]", weight_pt=0.8)
place_exact_display_lines(
    1748, 1236, 2010, 1402,
    lines=[
        "સમય",
        "૨ કલાક સુધી",
        "૨થી ૪ કલાક માટે",
        "૪ કલાકથી વધારે",
        "રાત્રે ૧૨ વાગ્યા પછી",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2030, 1236, 2180, 1402,
    lines=["ટુવ્હીલર", "રૂ.૧૦", "રૂ.૨૦", "રૂ.૩૦", "રૂ.૩૦૦"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2210, 1236, 2376, 1402,
    lines=["ફોરવ્હીલર", "રૂ.૨૦", "રૂ.૪૦", "રૂ.૫૦", "રૂ.૫૦૦"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    1748, 1406, 2376, 1438,
    lines=["(રાત્રિના સમયની રકમ પેનલ્ટી સ્વરૂપે પ્રતિ દિવસની છે.)"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)

# 7th Floor Restaurant Box (Cols 6-7, x=1744..2384, y=1448..1624)
draw_box(1744, 1448, 2384, 1624, stroke_swatch="[Black]", stroke_weight_pt=1.6)
place_exact_display_lines(
    1754, 1454, 2374, 1496,
    lines=["સાતમો માળ ગાર્ડન રેસ્ટોરન્ટ માટે અનામત રખાયો"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1754, 1500, 2374, 1618,
    text="એસઆરએફડીસીએલના સૂત્રોના જણાવ્યા અનુસાર પાર્કિંગનો સાતમો માળ ગાર્ડન રેસ્ટોરન્ટ માટે રિઝર્વ રખાયો છે. તેમજ તેના પાર્કિંગ માટે છઠ્ઠો માળ ખાલી રખાયો છે. એટલે વાહન પાર્કિંગની સંખ્યા ઘટી જવાથી ભાડાની કુલ રકમમાં ઘટાડો થયો છે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Col 8 Smart Parking Box (x=2402..2720, y=1177..1619)
draw_box(2402, 1177, 2720, 1619, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2410, 1184, 2712, 1268,
    lines=[
        "રિવરફ્રન્ટ મલ્ટિલેવલ",
        "પાર્કિંગની સ્માર્ટ સુવિધાઓ"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2410, 1272, 2712, 1612,
    text="આ મલ્ટિલેવલ પાર્કિંગમાં સીસીટીવી કેમેરાથી માંડીને ઈલેક્ટ્રિક વાહનના ચાર્જિંગ પોઈન્ટ, ક્યુઆર કોડવાળી ટિકિટ, પેમેન્ટ માટેનું ડિજિટલ મશિન, વાહનના પાર્કિંગ માટેના સેન્સર, બૂમ બેરિયર સહિતની સ્માર્ટ વ્યવસ્થાઓ છે. અહીં કેટલા વાહનો પાર્ક થયેલા છે અને કેટલી જગ્યા ખાલી છે? વગેરે ઓટોમેટિક ખ્યાલ આવી જાય, તેવું ડિજિટલ ડિસ્પ્લે બોર્ડ પણ છે. સ્માર્ટ પાર્કિંગની મોબાઈલ એપ્લિકેશન સાથે આ પાર્કિંગ જોડાયેલું છે.",
    target_lines=12,
    font_style="Bold",
    first_indent_pt=10.0,
)

# Bottom 3 Columns of Riverfront Parking Story (y=1632..1904)
place_exact_body_column(
    1744, 1632, 2052, 1904,
    text="લાખના વાર્ષિક ભાડે આપવાની કવાયત શરૂ કરવામાં આવી છે. તંત્ર માટે ગળાનું હાડકું થઈ ગયેલા આ પાર્કિંગના ભૂતકાળમાં જઈએ તો હાલના મેયર જ્યારે સ્ટેન્ડિંગ કમિટીના ચેરમેન હતા, ત્યારે સપ્ટેમ્બર ૨૦૨૩માં આ મલ્ટિલેવલ સ્માર્ટ પાર્કિંગનું લોકાર્પણ કરાયું હતું. રૂ.૬૦ કરોડના ખર્ચે ૭૦૦ કાર અને ૧૦૦૦ ટુવ્હીલર પાર્ક થઈ શકે તેવા આ પાર્કિંગની",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2064, 1634, 2064, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1632, 2382, 1904,
    text="પાર્કિંગ ભાડે આપવાની કવાયત કરવામાં આવી, ત્યારે કોન્ટ્રાક્ટરે ૫૦ લાખ રૂપિયામાં પાર્કિંગ ભાડે રાખ્યું હતું. પરંતુ તેની સામે મહિને એકાદ લાખ રૂપિયાની પણ આવક ન થઈ રહી હોવાથી કોન્ટ્રાક્ટરે આ કરાર રદ કરવા રજૂઆત કરી હતી. આ કરાર રદ થઈ ગયા બાદ સાત માળના મલ્ટિલેવલ પાર્કિંગની આ આખી ઈમારત હાલમાં બિનઉપયોગી પડી છે. હાલમાં",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2395.5, 1634, 2395.5, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1632, 2715, 1904,
    text="ત્યારે પ્રજાના ૬૦ કરોડ રૂપિયાનું આવી રીતે આંધણ કરવા બદલ જવાબદાર કોણ? તેવો સવાલ ઉઠ્યો છે. અત્રે ઉલ્લેખનિય છે કે, અગાઉ સિંધુ ભવન રોડ અને પ્રહલાદ નગરના મલ્ટિલેવલ પાર્કિંગ પણ વિવાદમાં આવી ચૂક્યા છે. અમદાવાદમાં નિષ્ફળ ગયેલા મલ્ટિલેવલ પાર્કિંગ માટે મ્યુનિ.ના અધિકારીઓ અને શાસકો શા માટે કરોડો રૂપિયા વેડફે છે? તે લોકોને સમજાતું નથી.",
    target_lines=9,
    first_indent_pt=0.0,
)


# ==============================================================================
# 10. STORY 9: COLS 6-8 MID (DRI 42-HR RAID / 18-CR GOLD SMUGGLING SYNDICATE)
# ==============================================================================
print("Building Story 9 (DRI 18-Cr Gold Smuggling Syndicate, Cols 6-8)...")
draw_line(1744, 1910, 2716, 1910, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1744, 1916, 2715, 1968,
    lines=["ડીઆરઆઈએ ૪૨ કલાક દરોડા પાડી કરેલી કાર્યવાહી"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 1975, 2715, 1975, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 1982, 2715, 2168,
    lines=[
        "ગોલ્ડ સ્મગલિંગ કરતી સિન્ડિકેટ ઝડપાઈ",
        "૧૮ કરોડનું સોનું જપ્ત : ૩ની ધરપકડ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2030, 2174, 2208, 2198,
    lines=["અમદાવાદ, સોમવાર"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 2200, 2208, 2296,
    text="અમદાવાદ અને સુરતના ઈન્ટરનેશનલ એરપોર્ટ દ્વારા ભારતમાં વિદેશથી સોનું લાવતી એક સંગઠિત ગોલ્ડ સ્મગલિંગ સિન્ડિકેટનો ડિરેક્ટોરેટ ઓફ રેવન્યુ ઈન્ટેલિજન્સે પર્દાફાશ કર્યો છે અને ૩",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 2178, 2220, 2294, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 2174, 2715, 2296,
    text="વ્યક્તિની ધરપકડ કરી છે. આ ઓપરેશનમાં સ્મગલિંગ કરેલા સોનાની હેરફેર અને નિકાલને સુગમ બનાવવામાં મુસાફરો, હેન્ડલર્સ, મધ્યસ્થીઓ, સોનું ઓગાળવાની સુવિધાના ઓપરેટર અને જ્વેલરી ટ્રેડ ચેનલની પરસ્પર જોડાયેલી ભૂમિકા સામે આવી છે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 2300, 2715, 2414,
    lines=[
        "દુબઈના ફાયનાન્સરની સંડોવણી : વડોદરામાં ગેરકાયદે સોનું",
        "ઓગાળવાના એકમ સાથે અમદાવાદ, સુરત એરપોર્ટમાં નેટવર્ક"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 2420, 2052, 3058,
    text="ડીઆરઆઈના અધિકારીઓએ ૧૬ ઓક્ટોબરથી ૪૨ કલાક સુધી સંકલિત દરોડા પાડ્યા હતા. જેમાં હવાઈ મુસાફરો દ્વારા તસ્કરી, હેન્ડલર્સને સોંપણી, ગેરકાયદેસર રીતે ઓગાળવું, અને જ્વેલરી આઉટલેટ દ્વારા વેચાણ સહિતના રેકેટનો ઘટસ્ફોટ થયો હતો. કુલ રૂ. ૧૮.૪૧ કરોડની કિંમતના ૧૩.૦૧૭ કિલો વિદેશી મૂળના સોનાના સોદા ખુલ્લા પડ્યા હતા.આ સંકલિત ઓપરેશનના પરિણામે આશરે ૮૯૦ ગ્રામ સોનું જપ્ત કરવામાં આવ્યું હતું અને ૬.૪૧ કિલો ગેરકાયદેસર રીતે ઓગાળેલા સોના સંબંધિત ગુનાહિત પુરાવા રિકવર કરવામાં આવ્યા હતા.\nઆ સંકલિત ઓપરેશનના પરિણામે આશરે ૮૯૦ ગ્રામ સોનું જપ્ત કરવામાં આવ્યું હતું અને ૬.૪૧ કિલો ગેરકાયદેસર રીતે ઓગાળેલા સોના સંબંધિત ગુનાહિત પુરાવા રિકવર કરવામાં આવ્યા હતા. જ્વેલરી શોપ પર વધુ તપાસ દરમિયાન",
    target_lines=21,
    first_indent_pt=10.0,
)
draw_line(2064, 2424, 2064, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 2420, 2382, 2542,
    text="બિનહિસાબી વિદેશી મૂળના સોનાના બિસ્કિટ (બાર્સ) અને દુબઈ સ્થિત સિન્ડિકેટના મુખ્ય ફાયનાન્સર સાથે જોડાયેલા એક અલગ હેન્ડલર દ્વારા",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2424, 2395.5, 2540, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2420, 2715, 2542,
    text="સોનાના બિસ્કિટ અને દુબઈ સ્થિત સિન્ડિકેટના મુખ્ય ફાયનાન્સર સાથે જોડાયેલા એક અલગ હેન્ડલર દ્વારા મોકલવામાં આવેલા આશરે ૫.૮ કિલો",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_box(2070, 2551, 2720, 2891, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2080, 2558, 2710, 2612,
    lines=["ગોલ્ડ સ્મગલિંગનું નેટવર્ક કઈ રીતે ચાલતું હતું?"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2080, 2616, 2710, 2884,
    text="*  મુસાફરો દ્વારા સોનું છુપાવવાની અનોખી પદ્ધતિઓનો ઉપયોગ કરીને દેશમાં સોનાની તસ્કરી કરાતી.\n*  જેમાં રોડિયમ કોટેડ સોનાના પાતળા વાયર, ટ્રોલી બેગની અંદરના લાઈનિંગમાં જડેલું સોનું અને બેગના અંદરના ભાગમાં છુપાવેલી ગોલ્ડ પેસ્ટનો સમાવેશ.\n*  આગમન પછી, આ સોનું એરપોર્ટની બહાર હેન્ડલર્સને સોંપવામાં આવતું હોવાનો આક્ષેપ છે અને મધ્યસ્થીઓ દ્વારા વડોદરા સ્થિત સોનું ઓગાળવાની એક ગેરકાયદેસર યુનિટ સુધી પહોંચાડાતું.\n*  ત્યારબાદ ઓગાળવામાં આવેલું સોનું રોકડ સામે વેચાણ માટે અમદાવાદની એક જ્વેલરી શોપમાં સપ્લાય કરવામાં આવતું હતું.",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2900, 2382, 3058,
    text="મોકલવામાં આવેલા આશરે ૫.૮ કિલો તસ્કરી કરેલા સોનાના સોદા સંબંધિત રેકોર્ડ્સ રિકવર કરવામાં આવ્યા હતા.\nજ્વેલરી શોપ પર વધુ તપાસ દરમિયાન બિનહિસાબી વિદેશી મૂળના",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2904, 2395.5, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2900, 2715, 3058,
    text="તસ્કરી કરેલા સોનાના સોદા સંબંધિત રેકોર્ડ્સ રિકવર કરવામાં આવ્યા હતા.કસ્ટમ્સ એક્ટ, ૧૯૬૨ ની જોગવાઈઓ હેઠળ ત્રણ વ્યક્તિઓની ધરપકડ કરવામાં આવી છે.",
    target_lines=5,
    first_indent_pt=0.0,
)


# ==============================================================================
# 11. STORY 10: COLS 6-8 BOTTOM (MANDLI GARBA BOUNCERS SWORD ATTACK)
# ==============================================================================
print("Building Story 10 (Mandli Garba Bouncers Sword Attack, Cols 6-8)...")
draw_line(1744, 3064, 2716, 3064, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1748, 3068, 2710, 3114,
    lines=["પાસ સ્કેન કરાવવા બાબતે થયેલી તકરાર લોહિયાળ બની"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1748, 3119, 2710, 3119, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 3126, 2715, 3304,
    lines=[
        "મંડળી ગરબામાં બાઉન્સરો ખેલૈયા",
        "ઉપર તલવારો લઈને તૂટી પડ્યા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 3312, 2052, 3792,
    text="ગાંધીનગર,કલોલ,સોમવાર\nકોમર્શિયલ ગરબાના વધતા જતા ચલણ વચ્ચે તેમાં અવ્યવસ્થા અને બાઉન્સરોની દાદાગીરીના કિસ્સાઓ બહાર આવે છે ત્યારે કલોલના નાસમેદ ખાતે મંડળી ગરબામાં પાસ સ્કેન કરવા બાબતે થયેલી તકરારે ઉગ્ર રૂપ ધારણ કર્યું હતું અને બાઉન્સરો તલવાર અને લોખંડની સાંકળો લઈને ખેલૈયા ઉપર તૂટી પડ્યા હતા. જેમાં પાંચથી વધુ યુવાનો ઘાયલ થયા હતા. આ મામલે હાલ સાંતેજ પોલીસ દ્વારા ગુનો દાખલ કરાયો છે.\nમળતી વિગતો પ્રમાણે રાંચરડામાં વિલેજ કાફે ચલાવતા મૌલીક રશ્મીજી ઠાકોર ગઈ રાત્રે એક વાગ્યાના પોતાના ભાઈ તુષાર અને મિત્રો અનિલ ઠાકોર, વિવેક ઠાકોર, સેતુલ ઠાકોર, વિનોદ ઠાકોર, હીરેન પટેલ,",
    target_lines=16,
    first_indent_pt=10.0,
)
draw_line(2064, 3316, 2064, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 3312, 2382, 3792,
    text="વિશાલ ઠાકોર તથા રાહુલ ઠાકોર સાથે નાસમેદ ગામની સીમમાં યોજાયેલા મંડળી ગરબા ખાતે ગરબા જોવા માટે ગયા હતા. આ તમામના એન્ટ્રી પાસ મૌલીકના મોબાઈલમાં હોવાથી તેઓ ગેટ પર પાસ સ્કેન કરાવતા હતા, જ્યારે તેમના કેટલાક મિત્રો અંદર ગયા હતા.\nદરમિયાન, ત્યાં હાજર એક સરદારજી બાઉન્સરે હીરેન પટેલને અંદર જવાનું કહેતા હીરેને પોતાના મિત્રના પાસ સ્કેન થયા પછી સાથે જવાનું જણાવતા બાઉન્સર ઉશ્કેરાઈ ગયો હતો અને બોલાચાલી કરવા લાગ્યો હતો. મામલો વધુ ન વણસે તે માટે મૌલીક અને તેમના ભાઈએ વચ્ચે પડીને બાઉન્સરને સમજાવવાનો પ્રયાસ કર્યો હતો, પરંતુ બાઉન્સરો વધુ આક્રમક બની ગયા હતા. તે",
    target_lines=16,
    first_indent_pt=0.0,
)
draw_line(2395.5, 3316, 2395.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 3312, 2715, 3792,
    text="વેળાએ અચાનક એક સરદારજી બાઉન્સરે પોતાની કમરમાંથી તલવાર કાઢીને મૌલીક પર પ્રહાર કરતા તે નીચે નમી જતા તલવારની મૂઠ તેમના માથાના ભાગે વાગી હતી અને લોહી વહેવા લાગ્યું હતું. આ થોડી જ પળોમાં અન્ય દસેક જેટલા સરદારજી બાઉન્સરો હાથમાં તલવારો, વાંસના બંબુ અને લોખંડની સાંકળો લઈને દોડી આવ્યા હતા અને યુવાનો પર જીવલેણ હુમલો કર્યો હતો. આ ઘટનાને પગલે અહીં ભારે દોડધામ મચી ગઈ હતી અને ગરબા રમવા માટે આવેલા ખેલૈયાઓ પણ ડરી ગયા હતા.\nફરિયાદના આધારે સાંતેજ પોલીસે અજાણ્યા સરદારજી સિક્યુરિટી બાઉન્સરો વિરુદ્ધ ગુનો નોંધીને કાયદેસરની સઘન તપાસ શરૂ કરી છે.",
    target_lines=16,
    first_indent_pt=0.0,
)


# ==============================================================================
# 12. SAVE OPEN FILE (.pagedesigner) & EXPORT FULL-RES PNG + PDF
# ==============================================================================
cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_02_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_02_SameToSame.dns"
    png_path = target_dir / "Page_02_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_02_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_02_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
