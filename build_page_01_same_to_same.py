# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 1 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt (37.04 x 52.57 cm)
- Graphics (PNG): Masthead, Sahiyar Ear Panel, Ravana Photo, Delhi Ni Vaat Dome Header,
  Bedhadak Cartoon Art, Tiger Accused Train Photo, GS 45 Promo Badge, Amul Ad, CMYK Bar.
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular, with embedded
  Latin English terms in 'Arial') matching every single headline, strapline, subhead,
  callout box, caption, dateline, and body column word-for-word and line-for-line!
"""

import json
import math
import os
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
ASSETS_DIR = DIR_SMAE / "Page_01_Assets"

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
    """
    Because Gopika.ttf maps ASCII A-Z/a-z/0-9 slots to legacy Gujarati glyphs, any Latin
    English words/numbers (e.g. LIC, GIC, IPO, BlackRock, SBI, HDFC, ICICI, MF, ADIA, QIA,
    HCL, Enam, Rainmatter, Public Subscription, 5G, AI, Schroders) inside a Gujarati story
    must use 'Arial' at ~78% of the Gopika point size so their cap height matches Gujarati!
    """
    latin_cmds = []
    eng_pt = round(base_pt * 0.76, 1)
    for m in re.finditer(r"[A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*", text):
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
FRAME_DELAY = 0.14 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.26 if LIVE_DRAW else 0.0
LINE_DELAY = 0.08 if LIVE_DRAW else 0.0


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
        si.wShowWindow = 0  # SW_HIDE for helper console
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
        "title": "Gujarat Samachar — Page 01 (100% Same-to-Same Editable Gopika)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.5)


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


def draw_box(x1_px, y1_px, x2_px, y2_px, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5, stroke_tint=1.0):
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
    target_hscale: float = 0.90,
    lead_ratio: float = 0.94,
    underline: bool = False,
    v_justify: str = "top",
    inset_pt=None,
    max_pt_scale: float = 0.98,
):
    """
    Places a 1-line, 2-line, or N-line Headline / Strapline / Subhead / Callout at the exact
    pixel bounding box [x1_px, y1_px, x2_px, y2_px] using editable 'Gopika' text.
    """
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
# 1. PLACE ALL CROPPED PNG GRAPHICS (MASTHEAD, EAR PANEL, PHOTOS, CARTOON, ADS)
# ==============================================================================
print("Placing cropped PNG graphics...")
place_png(80, 150, 2054, 550, "masthead_6col.png")
place_png(2076, 158, 2718, 545, "ear_panel_sahiyar.png")
place_png(1412, 835, 2716, 1595, "ravana_dahan_photo.png")
place_png(1746, 2512, 2052, 2780, "tiger_train_photo.png")
place_png(1080, 3538, 1388, 3792, "gs_promo_badge_45.png")
place_png(1411, 3085, 2718, 3802, "amul_ad.png")
place_png(84, 3805, 2718, 3858, "cmyk_footer_bar.png")


# ==============================================================================
# 2. TOP-RIGHT RED BANNER BOX (Cols 7-8: રશિયા અને યુક્રેનનું અંતરીક્ષ યુદ્ધ પરાકાષ્ઠાએ)
# ==============================================================================
print("Building Top-Right Red Banner Box...")
draw_box(2077, 562, 2715, 813, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="[Black]", stroke_weight_pt=1.0)
place_exact_display_lines(
    2105, 576, 2688, 790,
    lines=[
        "રશિયા અને યુક્રેનનું",
        "અંતરીક્ષ યુદ્ધ પરાકાષ્ઠાએ"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.84,
    lead_ratio=0.98,
)


# ==============================================================================
# 3. STORY 1: TOP-LEFT LEAD STORY (AMERICAN SATELLITE CHASED BY RUSSIAN SATELLITE)
# ==============================================================================
print("Building Story 1 (Satellite Lead Story)...")
place_exact_display_lines(
    174, 560, 1962, 634,
    lines=["દુશ્મન દેશના સેટેલાઈટને ઘેર્યો હોય એવી દુનિયાની પ્રથમ ઘટના"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(174, 639, 1962, 639, swatch="[Black]", weight_pt=1.6)

place_exact_display_lines(
    86, 645, 2048, 808,
    lines=["અમેરિકન સેટેલાઈટનો થઈ રહેલો પીછો"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.85,
)

# 2-Col Intro Left (Cols 1-2) + Dateline
place_exact_display_lines(
    580, 822, 722, 850,
    lines=["કીવ, તા. ૧૯"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    86, 852, 723, 915,
    text="રશિયા-યુક્રેન વચ્ચે ચાલી રહેલું યુદ્ધ નેક્સ્ટ લેવલે પહોંચી ગયું છે. રશિયાના કોસમોસ-૨૯૧૨ સેટેલાઈટે યુક્રેનને મદદ કરતાં અમેરિકન રડાર સેટેલાઈટ",
    target_lines=2,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=14.0,
    hi_pt=11.5,
    lo_pt=9.0,
)

draw_line(736, 830, 736, 898, swatch="[Black]", weight_pt=0.75)

# 2-Col Intro Right (Cols 3-4)
place_exact_body_column(
    749, 822, 1386, 914,
    text="આઈસીઆઈ-એક્સ૩૬ સેટેલાઈટનો પીછો કર્યો હતો. એનાથી અંતરીક્ષમાં સેટેલાઈટની સુરક્ષા બાબતે ચિંતા વ્યક્ત થઈ રહી છે. નિષ્ણાતો કહી રહ્યા છે કે મોડર્ન વોરફેરમાં કોઈ દેશે દુશ્મન દેશના સેટેલાઈટનો પીછો કર્યો હોય એવી ઘટના પહેલી વખત બની છે.",
    target_lines=3,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=0.0,
    hi_pt=11.5,
    lo_pt=9.0,
)

# 4-Col Subhead (Cols 1-4)
place_exact_display_lines(
    86, 920, 1386, 1076,
    lines=[
        "યુક્રેનને ડ્રોન અને મિસાઈલનો રીઅલ ટાઈમ ડેટા આપતા",
        "અમેરિકન સેટેલાઈટનો રશિયન સેટેલાઈટે પીછો કર્યો"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)

# Col 1 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    85, 1088, 391, 1354,
    text="યુક્રેનના સલાહકાર બ્રેસ્કેસ્તનોવે રશિયાના સેટેલાઈટ નેટવર્કને યુદ્ધમાં સૌથી મોટો ખતરો ગણાવ્યો હતો. રશિયન સેટેલાઈટે યુક્રેનના ડ્રોન અને મિસાઈલોને રીઅલ રડારનો ડેટા આપતા અમેરિકાના સેટેલાઈટને પીછો પકડ્યો હતો. એક રીતે અમેરિકન સેટેલાઈટને અંતરીક્ષમાં ઘેરવાની કોશિશ કરીને યુક્રેનને જે રીઅલ ટાઈમ રડાર ડેટા મળે છે તેને પ્રભાવિત",
    target_lines=9,
    first_indent_pt=10.0,
)

draw_line(404, 1105, 404, 1348, swatch="[Black]", weight_pt=0.75)

# Col 2 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    416, 1088, 722, 1354,
    text="૧થી ૨ કિલોમીટર જેટલું જ અંતર હતું. અવકાશના સંદર્ભમાં આ ખૂબ ઓછું અંતર કહેવાય. નીચલી ભ્રમણ કક્ષામાં સેટેલાઈટ લગભગ ૨૭ હજાર કિલોમીટર પ્રતિકલાકની ઝડપે ઘૂમે છે. ત્યારે આ અંતર બેહદ જોખમી ગણાય. એનાથી સેટેલાઈટો વચ્ચે ટક્કરનું જોખમ વધી શકે છે.\nજોકે, રશિયન સેટેલાઈટે અમેરિકન",
    target_lines=9,
    first_indent_pt=0.0,
)

# Orange Callout Box across Cols 1-2 (x=84..723, y=1362..1476)
draw_box(84, 1362, 723, 1476, fill_swatch="[Paper]", fill_tint=1.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    90, 1368, 717, 1466,
    lines=[
        "રશિયન સેટેલાઈટ રેસવેટે યુક્રેનના ડ્રોન-મિસાઈલોના રિયલ",
        "ટાઈમ કંટ્રોલ કરી ઈલેક્ટ્રોનિક વોરફેર નિષ્ફળ કરી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)

# Col 1 Lower Body (y=1484..1722, 8 lines)
place_exact_body_column(
    85, 1484, 391, 1722,
    text="કરવાની કોશિશ કરી હતી.\nઅંતરીક્ષ વિજ્ઞાનીઓ નોંધ્યું કે રશિયન સેટેલાઈટે તેની ભ્રમણકક્ષા વારંવાર બદલીને અમેરિકન સેટેલાઈટની સાવ નજીક જવાની કોશિશ કરી. કેટલીક વખત તો બંને સેટેલાઈટ વચ્ચે માત્ર થોડા કિલોમીટરનું જ અંતર રહી ગયું હતું. ૭મી ઓક્ટોબરે તો બંને સેટેલાઈટ વચ્ચે માત્ર",
    target_lines=8,
    first_indent_pt=0.0,
)

draw_line(404, 1492, 404, 1715, swatch="[Black]", weight_pt=0.75)

# Col 2 Lower Body (y=1484..1694, 7 lines) + Jump line at y=1696..1724
place_exact_body_column(
    416, 1484, 722, 1694,
    text="રડાર સેટેલાઈટ પર હુમલો કર્યો નથી, પરંતુ ભવિષ્યમાં યુક્રેનની મિસાઈલો અને ડ્રોનને રીઅલ ટાઈમ રડારનો ડેટા આપતા સેટેલાઈટ પર હુમલો કરીને તેને દિશાહીન કરી શકે છે. જો રશિયા યુક્રેનને મદદ કરતાં અમેરિકાનો સેટેલાઈટ તોડી નાખે તો અંતરીક્ષમાં અમેરિકા-રશિયા વચ્ચે જ",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    460, 1696, 680, 1724,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)

draw_line(736, 1100, 736, 1718, swatch="[Black]", weight_pt=0.75)

# ==============================================================================
# 4. STORY 1B: ZELENSKY ORANGE-BORDERED BOX (Cols 3-4, x=749..1387, y=1096..1726)
# ==============================================================================
print("Building Story 1B (Zelensky Orange Box)...")
draw_box(749, 1096, 1387, 1726, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    756, 1104, 1380, 1146,
    lines=["રશિયાએ યુક્રેનમાં ૧૬ બેલેસ્ટિક મિસાઈલો છોડી"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(757, 1150, 1379, 1150, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    756, 1154, 1380, 1288,
    lines=[
        "સહયોગી દેશો હવે ગુપ્ત માહિતી",
        "શેર કરી રહ્યાં નથી : ઝેલેન્સ્કી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    757, 1298, 1046, 1326,
    lines=["(પીટીઆઈ)            કીવ, તા. ૧૯"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    757, 1328, 1048, 1608,
    text="રશિયાએ બેલેસ્ટિક મિસાઈલો અને જેટ પાવર્ડ ડ્રોનનો ઉપયોગ કરીને યુક્રેનનાં એનર્જી ઈન્ફ્રાસ્ટ્રક્ચર પર નવેસરથી હુમલા કર્યા છે તેમ યુક્રેનનાં પ્રમુખ ઝેલેન્સ્કીએ એક નિવેદનમાં જણાવ્યું છે.\nઝેલેન્સ્કીએ જણાવ્યું છે કે યુક્રેનને આ હુમલા અંગે સહયોગી દેશો પાસેથી કોઈ પૂર્વ ચેતવણી મળી ન",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_line(1068, 1318, 1068, 1585, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1086, 1298, 1378, 1580,
    text="હતી. જ્યારે અગાઉ આ દેશો આવી ગુપ્ત માહિતી શેર કરતા હતાં. રશિયા પાસેથી ડીઝલ ખરીદવાની અમેરિકાની જાહેરાતથી પુતિનને ફાયદો થયો છે અને ઝેલેન્સ્કીને મુશ્કેલીનો સામનો કરવો પડી રહ્યો છે. ઝેલેન્સ્કીએ સોશિયલ મીડિયા પર જણાવ્યું હતું કે રાતે રશિયા દ્વારા કરવામાં આવેલા હુમલામાં યુક્રેનમાં એનર્જી",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1130, 1584, 1335, 1612,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_display_lines(
    756, 1616, 1380, 1716,
    lines=[
        "યુક્રેનના એનર્જી ઈન્ફ્રાસ્ટ્રક્ચર પર રશિયાના હુમલા",
        "પાંચ લાખથી વધુ લોકો વીજળીથી વંચિત થયા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

draw_line(1400, 838, 1400, 2494, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 5. RAVANA DAHAN PHOTO CAPTION (Cols 5-8, x=1412..2716, y=1608..1782)
# ==============================================================================
print("Building Ravana Dahan 6-line Bold Photo Caption...")
place_exact_display_lines(
    1412, 1608, 2716, 1780,
    lines=[
        "દશેરા એટલે અસત્ય પર સત્ય અને અધર્મ પર ધર્મના વિજયનું પ્રતીક. આ દિવસે રાવણ, મેઘનાદ અને કુંભકર્ણનાં પૂતળાંનું દહન કરવામાં આવે છે. રામાયણની કથા સાથે",
        "જોડાયેલી આ પરંપરા માત્ર ધાર્મિક ઉત્સવ નથી, પરંતુ માનવીને આત્મમંથન કરવાની પ્રેરણા આપતો અવસર પણ છે. રાવણ વિદ્વાન, પરાક્રમી અને શક્તિશાળી રાજા હતો.",
        "તેમ છતાં, તેનો અહંકાર, હઠ અને નૈતિક મર્યાદાઓનું ઉલ્લંઘન તેના પતનનું કારણ બન્યાં. તેનું પાત્ર સમજાવે છે કે જ્ઞાન, શક્તિ અને વૈભવ હોવા છતાં વ્યક્તિ જો વિવેક ગુમાવે",
        "તો તેની સિદ્ધિઓ પણ તેને વિનાશથી બચાવી શકતી નથી. રાવણનાં દસ માથાંને કામ, ક્રોધ, લોભ, મોહ, અહંકાર અને અન્ય નકારાત્મક વૃત્તિઓ સાથે સાંકળવામાં આવે છે.",
        "આ દોષો માત્ર વ્યક્તિના જીવનને જ નહીં, પરંતુ તેના સંબંધો અને સામાજિક વ્યવહારને પણ અસર કરે છે. રાવણ દહનનો સાચો અર્થ ત્યારે જ સાર્થક બને, જ્યારે આપણે પોતાના",
        "જીવનમાં રહેલા દોષોનો ત્યાગ કરવાનો સંકલ્પ કરીએ. અને હા, ભ્રષ્ટાચાર, ભેદભાવ, નફરત અને સત્તાના દુરુપયોગ સામે ઊભા રહેવું પણ આ સંદેશનો જ એક ભાગ છે."
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.96,
    max_pt_scale=0.92,
)
draw_line(1412, 1787, 2716, 1787, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 6. STORY 3: DELHI NI VAAT (Col 1, x=84..392, y=1736..2499)
# ==============================================================================
print("Building Delhi Ni Vaat (Col 1)...")
draw_line(84, 1730, 1388, 1730, swatch="[Black]", weight_pt=0.85)
draw_box(84, 1736, 392, 2499, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_png(91, 1742, 385, 1882, "delhi_vaat_header.png")

place_exact_display_lines(
    93, 1886, 383, 1948,
    lines=[
        "એસઆઈઆર વિવાદ : રીજીજુ",
        "અને શશી થરૂર સામસામે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    200, 1953, 382, 1980,
    lines=["નવીદિલ્હી, તા. ૧૯"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    93, 1983, 383, 2466,
    text="કેન્દ્રીય મંત્રી કિરેન રીજીજુએ એસઆઈઆર સામે થઈ રહેલા વિરોધ પ્રદર્શનો બાબતે કરેલા નિવેદન પર કોંગ્રેસના સાંસદ શશી થરૂરએ પ્રતિક્રિયા આપી છે. શશી થરૂરનું કહેવું છે કે ભારત ન તો બાંગ્લાદેશ છે, ન તો ફ્રાંસ. એમણે કહ્યું હતું કે વિરોધ પક્ષ હિંસાનું સમર્થન નથી કરતો, પરંતુ વિરોધપક્ષની માંગણી સ્વતંત્ર અને નિષ્પક્ષ ચૂંટણી યોજાય એ માટેની છે. ફ્રાંસમાં જે રીતે બસો તેમ જ પોલીસ સ્ટેશનોને આગ લગાડવા જેવી હિંસક ઘટનાઓ બને છે એવા વિરોધને વિરોધ પક્ષો કદી ટેકો આપે નહીં. વિરોધ પક્ષ શાંતિપૂર્ણ વિરોધ કરવામાં વિશ્વાસ રાખે છે. કિરેન રીજીજુએ સોશ્યલ મીડિયા પર એક પોસ્ટ",
    target_lines=16,
    first_indent_pt=10.0,
)
place_exact_display_lines(
    125, 2466, 350, 2494,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)

draw_line(404, 1745, 404, 2490, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 7. STORY 4: US-INDIA TRADE DEAL (Cols 2-4, x=416..1386, y=1733..2500)
# ==============================================================================
print("Building Story 4 (US-India Trade Deal, Cols 2-4)...")
place_exact_display_lines(
    418, 1734, 1384, 1784,
    lines=["ભારત દ્વારા રશિયન ઓઈલની ખરીદી મુદ્દે ટ્રમ્પનું ઢીલું વલણ"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(420, 1789, 1383, 1789, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    417, 1793, 1385, 1974,
    lines=[
        "ભારત-અમેરિકાની ટ્રેડ ડીલ આખરી",
        "તબક્કામાં : યુએસએના વિદેશ મંત્રી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 1.5-Col Intro Left (x=417..890) + 1.5-Col Intro Right (x=912..1385) divided at x=901
place_exact_display_lines(
    710, 1990, 890, 2016,
    lines=["વોશિંગ્ટન, તા. ૧૯"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    417, 2018, 890, 2076,
    text="ભારત અને અમેરિકાની વચ્ચે ટૂંક સમયમાં ટ્રેડ ડીલ થવાની શક્યતાઓ છે. આ માહિતી અમેરિકાના વિદેશમંત્રી માર્કો રૂબીયો",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=12.0,
)
draw_line(901, 1992, 901, 2074, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    912, 1990, 1385, 2076,
    text="દ્વારા સોમવારે આપવામાં આવી હતી. ભારત આવી રહેલા અમેરિકાના વિદેશમંત્રીએ કહ્યું હતું કે અમે હાલ ભારત સાથેની ટ્રેડ ડીલને અંતિમ સ્વરૂપ આપવાનો પ્રયાસ કરી રહ્યા છીએ.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 2-4)
place_exact_display_lines(
    417, 2080, 1385, 2194,
    lines=[
        "ભારત અને અમેરિકા વચ્ચે વેપાર ઉપરાંત સંરક્ષણ,",
        "ટેક્નોલોજી, ઉર્જા સહિતના ક્ષેત્રે પણ ચર્ચા થવાની શક્યતા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 3 Body Columns of US-India Trade Deal (y=2208..2498, 10 lines each)
place_exact_body_column(
    416, 2208, 722, 2498,
    text="રશિયન ક્રૂડ ઓઈલ ખરીદનારા ભારત સહિતના પાંચ મોટા દેશો પર ૧૦૦ ટકા ટેરિફ નાખવાના નિર્ણયને હાલ મુલતવી રાખવા પાછળનું કારણ જણાવતા અમેરિકાના વિદેશમંત્રી માર્કોએ કહ્યું હતું કે છેલ્લા કેટલાક મહિનામાં અમે આ છૂટ આપી કેમ કે તેની અસર વૈશ્વિક આપૂર્તિ અને કિંમતો પર પડી રહી હતી. તમામ રીતે સંતુલન જાળવવું જરૂરી હોય છે તેથી નિર્ણય હાલ",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(736, 2215, 736, 2485, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    749, 2208, 1054, 2498,
    text="પુરતો પડતો મુકવામાં આવ્યો છે. ભારત અને અમેરિકા બન્ને ટ્રેડ ડીલ એટલે કે વેપાર માટેના કરારોને અંતિમ સ્વરૂપ દેવાના નજીક પહોંચી ગયા છે.\nજોકે ડેરી ક્ષેત્રનો મુદ્દો હજુ પણ ઘોંચવામાં હોવાના અહેવાલો છે. અમેરિકા હાલ ભારતના માર્કેટમાં ડેરી ક્ષેત્રમાં જગ્યા બનાવવા માગે છે. જોકે ભારત આ નિર્ણય માટે હાલ તૈયાર નથી. નોંધનીય છે કે અમેરિકાના વિદેશમંત્રી",
    target_lines=10,
    first_indent_pt=0.0,
)
draw_line(1068, 2218, 1068, 3797, swatch="[Black]", weight_pt=0.85)
place_exact_body_column(
    1081, 2208, 1386, 2498,
    text="માર્કો રૂબિયો હાલ ભારતની મુલાકાત માટે આવી રહ્યા છે. તેઓ ૨૦મી ઓક્ટોબરના મુંબઈમાં ભારતના વિદેશમંત્રી એસ. જયશંકર સાથે મુલાકાત કરશે. ભારત અમેરિકા વચ્ચે વૈશ્વિક રણનીતિક ભાગીદારીની સાથે સાથે ઉર્જા, વેપાર, સંરક્ષણ, ટેક્નોલોજી વગેરે ક્ષેત્રમાં પણ દ્વિપક્ષીય સહયોગના મહત્વના મુદ્દાઓ પર ચર્ચા કરવાની આશા છે.",
    target_lines=10,
    first_indent_pt=0.0,
)


# ==============================================================================
# 8. STORY 5: COL 5 PROMO BOX + BEDHADAK CARTOON BOX (x=1411..1722, y=1795..2503)
# ==============================================================================
print("Building Col 5 Promo Box & Bedhadak Cartoon Box...")
draw_box(1411, 1796, 1719, 1993, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    1422, 1800, 1708, 1974,
    lines=[
        "એઆઈ સાયબર ક્રાઈમ",
        "શિખવાડશે : ૫૦૦૦",
        "ડોલરના ટોકનથી ૧૦૦",
        "કંપનીના સર્વર ખોરવ્યા",
        "વાંચો પાના નં.૧૩"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
    lead_ratio=0.92,
    max_pt_scale=0.90,
)

# Bedhadak Box
draw_box(1416, 2007, 1722, 2503, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
draw_line(1416, 2068, 1722, 2068, swatch="GsOrangeBorder", weight_pt=1.2)
draw_line(1416, 2405, 1722, 2405, swatch="GsOrangeBorder", weight_pt=1.2)

place_exact_display_lines(
    1422, 2010, 1580, 2056,
    lines=["બેધડક"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.95,
    max_pt_scale=0.88,
)
place_exact_display_lines(
    1610, 2024, 1714, 2056,
    lines=["-મંજુલ"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.92,
    max_pt_scale=0.88,
)
place_png(1419, 2071, 1719, 2402, "bedhadak_cartoon.png")
place_exact_display_lines(
    1424, 2408, 1714, 2494,
    lines=[
        "સાહેબ, હુમલાખોરોને ઓળખવા",
        "ખૂબજ મુશ્કેલ છે, શું તેમણે ક્યારેય",
        "સરકાર સામે દેખાવો નહીં કર્યા હોય ?"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.92,
    max_pt_scale=0.90,
)

draw_line(1732, 1797, 1732, 3053, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 9. STORY 6: TIGER SHROFF FIRING (Cols 6-8, x=1744..2716, y=1794..3065)
# ==============================================================================
print("Building Story 6 (Tiger Shroff Firing, Cols 6-8)...")
place_exact_display_lines(
    1744, 1794, 2715, 1844,
    lines=["બે આરોપી મૂળ હરિયાણાના, એક બિહારનો : એક મુંબઈમાં રેપિડો રાઈડર"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 1850, 2716, 1850, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    1744, 1854, 2715, 2036,
    lines=[
        "ટાઈગર પર ફાયરિંગ કરી ભાગેલા",
        "ત્રણ કોટામાં ટ્રેનમાંથી પકડાયા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 1.5-Col Intro Left + 1.5-Col Intro Right (divided at x=2226.5)
place_exact_display_lines(
    1745, 2060, 2216, 2088,
    lines=["(પ્રતિનિધિ દ્વારા)                             મુંબઈ, તા. ૧૯"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1745, 2090, 2216, 2210,
    text="બોલિવુડ અભિનેતા ટાઈગર શ્રોફ પર રવિવારની સાંજે મુંબઈના જુહૂમાં થયેલાં ફાયરિંગની ઘટનામાં ત્રણ આરોપીઓની રાજસ્થાનના કોટામાં ધરપકડ કરવામાં આવી છે. મૂળ હરિયાણાના રેહાન ઉર્ફે સુક્કાએ ટાઈગર પર ગોળીઓ વરસાવી હતી જ્યારે મૂળ",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2226.5, 2066, 2226.5, 2206, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2238, 2062, 2715, 2210,
    text="બિહારના અને મુંબઈમાં રેપિડો રાઈડર તરીકે કામ કરતો રિતિક કુમાર ઉર્ફે રોશને બાઈક ચલાવવાની કામગીરી સંભાળી હતી. જોકે, ફૂલસિંહની ગન અણીના વખતે લોક થઈ જતાં ટાઈગર બચી ગયો હતો. ફૂલસિંહ સગીર હોવાનો દાવો અગાઉ કરાયો હતો પરંતુ મુંબઈ પોલીસે જણાવ્યું હતું કે તે ૧૮ વર્ષનો છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 6-8)
place_exact_display_lines(
    1745, 2214, 2715, 2324,
    lines=[
        "ગોળીબાર બાદ સુરત પહોંચ્યા, ટ્રેનમાં દિલ્હી",
        "જઈ નેપાળ ભાગવાની ફિરાકમાં હતા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# Col 6 Above Photo (y=2338..2508, 6 lines)
place_exact_body_column(
    1745, 2338, 2051, 2508,
    text="જુહૂમાં ફાયરિંગ બાદ ત્રણેય આરોપી અંધેરી તરફ ભાગ્યા હતા. અંધેરી રેલવે સ્ટેશને પહોંચી તેમણે ત્યાંથી બોરીવલી જતી લોકલ ટ્રેન પકડી હતી. બોરીવલી ઉતરી ગયા બાદ તેઓ કેબ દ્વારા સુરત પહોંચ્યા હતા. સુરતથી તેઓ પુણે-જયપુર",
    target_lines=6,
    first_indent_pt=10.0,
)
# Col 6 Below Photo (y=2786..3060, 9 lines)
place_exact_body_column(
    1745, 2786, 2051, 3060,
    text="ટ્રેનમાં બેસી ગયા હતા. તેમણે અંધેરી સ્ટેશન પાસે બાઈક છોડી દીધી હતી તે પોલીસે જપ્ત કરી હતી. સીસીટીવી ફૂટેજ તથા ટેકનિકલ સર્વેલન્સ ઉપરાંત આંતરરાજ્ય પોલીસ સંકલન દ્વારા મુંબઈ પોલીસે ત્રણેયનું પગેરું મેળવ્યું હતું. રાજસ્થાન પોલીસને બાતમી આપી દેવાયા બાદ કોટા સ્ટેશને સ્થાનિક પોલીસે જાળ બિછાવી હતી. ટ્રેન આવી કે ગણતરીની",
    target_lines=9,
    first_indent_pt=0.0,
)

draw_line(2064, 2352, 2064, 3054, swatch="[Black]", weight_pt=0.85)

# Col 7 Short Body (y=2338..2476, 5 lines)
place_exact_body_column(
    2077, 2338, 2382, 2476,
    text="મિનિટમાં પોલીસે ટ્રેનમાંથી ત્રણેયની ધરપકડ કરી હતી. કોટામાં તેમને અદાલત સમક્ષ રજૂ કરાતાં અદાલતે ત્રણેયને મુંબઈ લઈ જવા ટ્રાન્ઝિટ રિમાન્ડ આપ્યા હતા.\nમુંબઈમાં ડીસીપી રાજતિલક રોશને",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2339, 2395.5, 2470, swatch="[Black]", weight_pt=0.75)

# Col 8 Short Body (y=2338..2448, 4 lines) + Jump line
place_exact_body_column(
    2408, 2338, 2714, 2448,
    text="મીડિયાને માહિતી આપતાં કહ્યું હતું કે ત્રણમાંથી એક આરોપી ૧૮ વર્ષનો છે અને બીજા બે બાવીસ વર્ષના છે. ઝડપાયેલા ત્રણમાંથી બેએ પાંચથી છ રાઉન્ડ ફાયરિંગ",
    target_lines=4,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2460, 2449, 2665, 2476,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)


# ==============================================================================
# 10. STORY 7: MANIPUR VIOLENCE (Cols 7-8, x=2076..2716, y=2482..3065)
# ==============================================================================
print("Building Story 7 (Manipur Violence, Cols 7-8)...")
draw_line(2079, 2482, 2718, 2482, swatch="[Black]", weight_pt=0.85)
place_exact_display_lines(
    2137, 2486, 2654, 2528,
    lines=["લોકોના દેખાવો સામે ટીયરગેસ છોડાયો"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(2137, 2533, 2654, 2533, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    2076, 2538, 2714, 2678,
    lines=[
        "મણિપુરમાં ઉગ્રવાદીઓની હિંસા",
        "જંગલમાં ત્રણ ગરીબોને ઠાર કર્યા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    2550, 2684, 2714, 2710,
    lines=["ઈમ્ફાલ,તા. ૧૯"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    2076, 2712, 2715, 2826,
    text="ઉગ્રવાદીઓએ મણિપુરમાં સોમવારે જંગલમાંથી લાકડાં વીણનારા ત્રણ જણની ગોળી મારીને હત્યા કરી છે, જ્યારે અન્ય ત્રણ જણ ઘવાયા છે, બીજા ત્રણ લોકો ગુમશુદા છે. સ્થાનિક લોકોએ બનાવના વિરોધમાં દેખાવો કરીને બે મૃતકોના શબને મુખ્યમંત્રીના ઘરની બહાર મૂકી દીધા.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    2076, 2830, 2715, 2930,
    lines=[
        "દેખાવકારોએ મૃતકોને સીએમ આવાસ બહાર મૂક્યા",
        "ત્રણ શ્રમિકો ઘાયલ જ્યારે બીજા ત્રણ લાપતા થયા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 2940, 2382, 3060,
    text="અધિકારીઓએ જણાવ્યું કે ઉગ્રવાદીઓએ ઈમ્ફાલ પૂર્વ અને કાંગપોકપી જિલ્લાની સરહદે લાકડાં ભેગા કરનારા લોકોના જૂથ પર ગોળીઓ",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(2395.5, 2950, 2395.5, 3058, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2940, 2714, 3032,
    text="છોડતા અરૂબમ રોનિલ (૩૫) અને લૈરેન લોકપમ ઈનાઓબી(૫૧) નામના શ્રમજીવીઓને ગોળી વાગતા ઘટનાસ્થળે",
    target_lines=3,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2460, 3033, 2665, 3060,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
draw_line(1413, 3069, 2716, 3069, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 11. STORY 8: JIO PLATFORMS IPO (Cols 1-3, x=84..1056, y=2502..3792)
# ==============================================================================
print("Building Story 8 (Jio Platforms IPO, Cols 1-3)...")
draw_line(84, 2503, 1056, 2503, swatch="[Black]", weight_pt=0.85)
place_exact_display_lines(
    128, 2518, 1013, 2568,
    lines=["રિલાયન્સની ડિજિટલ પાંખનો ઐતિહાસિક ધમાકો"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(128, 2574, 1013, 2574, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    88, 2580, 1052, 2774,
    lines=[
        "જિયો પ્લેટફોર્મ્સે એન્કર ઈન્વેસ્ટર્સ",
        "પાસેથી રૂ.૮,૧૧૦ કરોડ એકત્ર કર્યા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 1.5-Col Intro Left + 1.5-Col Intro Right
place_exact_display_lines(
    410, 2784, 548, 2810,
    lines=["મુંબઈ, ૧૯"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    88, 2810, 548, 2918,
    text="રિલાયન્સ ઈન્ડસ્ટ્રીઝની ડિજિટલ સર્વિસ પાંખ ‘જિયો પ્લેટફોર્મ્સ’ દ્વારા પોતાના બહુપ્રતિષ્ઠિત ઈનિશિયલ પબ્લિક ઓફરિંગ (IPO) પૂર્વે એન્કર ઈન્વેસ્ટર્સ માટે શેર ફાળવણી આખરી કરી દેવામાં આવી છે. કંપનીએ એન્કર રોકાણકારો",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(566, 2792, 566, 2914, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2784, 1052, 2918,
    text="પાસેથી રૂ. ૮,૧૧૦ કરોડનું ભંડોળ એકત્ર કર્યું છે. બેન્કિંગ વર્તુળોના જણાવ્યા અનુસાર, જિયોના એન્કર બુક માટે વૈશ્વિક અને દેશી સંસ્થાકીય રોકાણકારો તરફથી અભૂતપૂર્વ ઉત્સાહ જોવા મળ્યો છે અને કુલ માંગ રૂ. ૨.૫ લાખ કરોડને પાર પહોંચી ગઈ છે.",
    target_lines=5,
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 1-3)
place_exact_display_lines(
    88, 2922, 1052, 3044,
    lines=[
        "LIC, બ્લેકરોક અને GIC સૌથી મોટા રોકાણકારો; સંસ્થાકીય",
        "રોકાણકારો તરફથી રૂ.૨.૫ લાખ કરોડથી વધુનું રેકોર્ડબ્રેક બુકિંગ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 3 Body Columns of Jio IPO (y=3054..3792, 25 lines each)
place_exact_body_column(
    88, 3054, 392, 3792,
    text="ભારતીય IPO ઈતિહાસમાં સંસ્થાકીય રોકાણકારો તરફથી આટલી વિશાળ માંગ મળી હોય તેવી આ પ્રથમ ઘટના છે. ૨૧૨ ઈન્વેસ્ટમેન્ટ લાઈન દ્વારા ૭૦થી વધુ વૈશ્વિક દિગ્ગજોનું રોકાણ જિયો પ્લેટફોર્મ્સના એન્કર બુકમાં વિશ્વના સૌથી મોટા સોવરેન વેલ્થ ફંડ્સ, ગ્લોબલ એસેટ મેનેજર્સ, ભારતીય મ્યુચ્યુઅલ ફંડ્સ, વીમા કંપનીઓ અને પેન્શન ફંડ્સ સહિત ૭૦થી વધુ મોટા રોકાણકારોએ ૨૧૨ સ્કીમ લાઈન દ્વારા ભાગ લીધો છે.લાઈફ ઈન્સ્યોરન્સ કોર્પોરેશન (LIC) રૂ. ૫૦૦ કરોડના રોકાણ સાથે સૌથી મોટી એકલ એન્કર રોકાણકાર તરીકે ઉભરી આવી છે.\nબ્લેકરોક (BlackRock), કેપિટલ ઈન્ટરનેશનલ, ફિડેલિટિ મેનેજમેન્ટ, સિંગાપોરનું સોવરેન ફંડ GIC તેમજ દેશના અગ્રણી મ્યુચ્યુઅલ ફંડ્સ જેવા કે SBI મ્યુચ્યુઅલ ફંડ, HDFC મ્યુચ્યુઅલ ફંડ અને ICICI પ્રુડેન્શિયલ મ્યુચ્યુઅલ ફંડને રૂ. ૪૨૫-૪૨૫ કરોડના શેર ફાળવવામાં આવ્યા છે.\nઆદિત્ય બિરલા સન લાઈફ MF, કેપિટલ વર્લ્ડ રૂ. ૩૦૦ કરોડ (પ્રત્યેક) શ્રુડર્સ (Schroders)રૂ. ૨૯૩ કરોડ, કોટક",
    target_lines=25,
    first_indent_pt=10.0,
)
draw_line(405, 3060, 405, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3054, 720, 3792,
    text="MF, નિપ્પોન ઈન્ડિયા MF, નાઈન્ટી વન રૂ. ૨૦૦ કરોડ (પ્રત્યેક), જેપી મોર્ગન એસેટ મેનેજમેન્ટ રૂ. ૧૮૨ કરોડ ADIA, QIA, અલાયન્સ, ડ્રેગનિયર રૂ. ૧૫૦ કરોડ (પ્રત્યેક)નું રોકાણ કરેલ છે.\nજિયો પ્લેટફોર્મ્સના આ એન્કર બુકની સૌથી મોટી વિશેષતા લાંબા ગાળાનું રોકાણ ધરાવતા વૈશ્વિક સોવરેન ફંડ્સ અને પેન્શન ફંડ્સની હાજરી છે. GIC, અબુ ધાબી ઈન્વેસ્ટમેન્ટ ઓથોરિટી (ADIA) અને કતાર ઈન્વેસ્ટમેન્ટ ઓથોરિટી (QIA) ઉપરાંત નોર્વેજના ‘નોર્જેસ બેન્ક ઈન્વેસ્ટમેન્ટ મેનેજમેન્ટ’, કેલિફોર્નિયા સ્ટેટ ટીચર્સ રિટાયરમેન્ટ સિસ્ટમ અને ફ્લોરિડા રિટાયરમેન્ટ સિસ્ટમ જેવા આંતરરાષ્ટ્રીય પેન્શન ફંડ્સે પણ મોટી રકમ રોકી છે.આ ઉપરાંત ભારતની અગ્રણી ઈન્સ્યોરન્સ અને પેન્શન સંસ્થાઓ જેવી કે HDFC લાઈફ, SBI લાઈફ, HDFC પેન્શન, SBI પેન્શન અને ICICI પ્રુડેન્શિયલ પણ આ ફાળવણીમાં સામેલ છે.\nફેમિલી ઓફિસિસ અને ગ્લોબલ ટેકનોલોજી સ્પેશિયાલિસ્ટ્સ આઈટી અને ગ્રોથ ઓરિએન્ટેડ બિઝનેસમાં નિષ્ણાત",
    target_lines=25,
    first_indent_pt=0.0,
)
draw_line(730.5, 3060, 730.5, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3054, 1050, 3792,
    text="એવા ગ્લોબલ ઈન્વેસ્ટર્સ જેવા કે ડ્રેગનિયર, જેનસ હેન્ડરસન અને ફિડેલિટિના પ્રખ્યાત ‘કોન્ટ્રા ફંડ’ એ પણ જિયોમાં રોકાણ કર્યું છે.\nસ્થાનિક સ્તરે દેશના અગ્રણી ઉદ્યોગપતિઓના ફેમિલી ઓફિસિસે પણ ભારે રસ દાખવ્યો છે, જેમાં પ્રેમજી ફેમિલી (વિપ્રો), HCL ફેમિલી, એનામ (Enam) અને ઝેરોધાના રેનમેટર (Rainmatter) નો સમાવેશ થાય છે. ૨૧ ઓક્ટોબરથી આમ જનતા માટે આઈપીઓ ખુલશે.\nએન્કર બુકના અભૂતપૂર્વ પ્રતિસાદ બાદ હવે સૌની નજર ૨૧ ઓક્ટોબરથી શરૂ થઈ રહેલા જાહેર ભરણા (Public Subscription) પર મંડાયેલી છે.\nજિયો પ્લેટફોર્મ્સ આ ભંડોળનો ઉપયોગ તેના આધુનિક 5G નેટવર્ક, ક્લાઉડ કમ્પ્યુટિંગ, આર્ટિફિશિયલ ઈન્ટેલિજન્સ (AI) અને એન્ટરપ્રાઈઝ ડિજિટલ સેવાઓના વિસ્તરણ માટે કરશે. પ્રાઈસ બેન્ડની અપર લિમિટ પર આ ભારતીય મૂડી બજારના ઈતિહાસનો સૌથી મોટો IPO સાબિત થશે.",
    target_lines=25,
    first_indent_pt=0.0,
)


# ==============================================================================
# 12. STORY 9: FRANCE CURFEW & PROTESTS (Cols 4-5, x=1080..1720, y=2506..3535)
# ==============================================================================
print("Building Story 9 (France Curfew, Cols 4-5)...")
draw_line(1080, 2506, 1720, 2506, swatch="[Black]", weight_pt=0.85)
place_exact_display_lines(
    1112, 2510, 1688, 2550,
    lines=["હિંસક દેખાવો મુદ્દે ૨૪૦૦થી વધુની ધરપકડ"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(1112, 2554, 1688, 2554, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    1080, 2559, 1718, 2698,
    lines=[
        "ફ્રાન્સમાં હિંસા વચ્ચે શહેરોમાં કરફ્યુ,",
        "ઈમર્જન્સી લાદવાના મૈક્રોના સંકેત"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1080, 2708, 1718, 2736,
    lines=["(પીટીઆઈ)                                                          પેરિસ, તા. ૧૯"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2738, 1718, 2884,
    text="ફ્રાન્સનાં વડાપ્રધાન સેબેસ્ટિયન લેકોર્નુએ સરકારી ક્ષેત્રીય પ્રતિનિધિઓને નિર્દેશ આપ્યા છે કે તે અસરગ્રસ્ત વિસ્તારોમાં મર્યાદિત અને સ્થાનિક કરફ્યુ નાખે. આ નિર્ણય વીકએન્ડમાં થયેલી હિંસા પછી લેવામાં આવ્યો છે. જેમાં સમગ્ર દેશમાં સિટી હોલ, અન્ય જાહેર ઈમારતો અને હજારો વ્યવસાયોને નિશાન બનાવવામાં આવ્યા હતાં.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=14.0,
)
place_exact_display_lines(
    1080, 2888, 1719, 2988,
    lines=[
        "દેશમાં ૬૦ હજારથી વધુ સુરક્ષા કર્મચારી તૈનાત",
        "યુનિયનોનું પાંચ નવેમ્બરે રાષ્ટ્રીય હડતાળનું એલાન"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# Col 4 Body (y=2996..3526, 18 lines)
place_exact_body_column(
    1080, 2996, 1386, 3526,
    text="સરકારનાં ટોચનાં અધિકારીઓ સાથે બેઠક પછી વડાપ્રધાને જણાવ્યું હતું કે શનિવારે ભારે હિંસા અને સંપત્તિનાં મોટા નુકસાન છતાં કોઈનું પણ મોત થયું નથી જે એક ચમત્કાર છે.\nતેમણે હિંસક ભીડનો સામનો કરી રહેલ પોલીસની કામગીરીનો બચાવ પણ કર્યો હતો. તેમણે જણાવ્યું હતું કે ક્યાં વિસ્તારોમાં કરફ્યુ નાખવામાં આવશે તે હવે પછી જાહેર કરવામાં આવશે.\nઆ નિર્દેશ એવા સમયે આવ્યા છે જ્યારે ગૃહ પ્રધાન લોરેંટ નુનેઝે પોતાનું રાજીનામું આપી દીધું છે. જો ફ્રાન્સનાં પ્રમુખે તેમનું રાજીનામું સ્વીકાર કરવાનો ઈનકાર કરી દીધો છે.\nફ્રાન્સનાં પ્રમુખનાં કાર્યાલયે એક નિવેદનમાં જણાવ્યું છે કે વર્તમાન સ્થિતિમાં કાયદો અને વ્યવસ્થા જાળવી",
    target_lines=18,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3009, 1399.5, 3797, swatch="[Black]", weight_pt=0.85)

# Col 5 Short Top Body (y=2996..3044, 2 lines) + Jump line above Amul Ad
place_exact_body_column(
    1412, 2996, 1718, 3044,
    text="રાખવા માટે ગૃહ પ્રધાન લોરેંટ નુનેઝનું તેમના પદ પર ચાલુ રહેવું ખૂબ જ જરૂરી",
    target_lines=2,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1460, 3045, 1670, 3067,
    lines=["(અનુસંધાન ૯મે પાને)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)


# ==============================================================================
# 13. SAVE OPEN FILE (.pagedesigner) & EXPORT FULL-RES PNG + PDF
# ==============================================================================
cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_01_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_01_SameToSame.dns"
    png_path = target_dir / "Page_01_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_01_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_01_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
