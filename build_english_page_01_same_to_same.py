# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 1 BUILDER ('INDIAN POST' — English Gujarat Samachar Edition)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt (37.04 x 52.57 cm)
- Exact same layout, exact same frame positions/sizes, and accurate factual English translation of Page 1.
- Masthead: Giant 'INDIAN POST' in 'Indian Post Mast' (Gujarat Samachar Calligraphic Shaily) + English dateline & imprint lines + 'SAHIYAR' Ear Panel.
- All placed ads/photos use .webp ('image/webp') for rapid drawing in Page Designer 1.0.
- News Content: 100% Editable English Text ('Georgia' & 'Times New Roman' Bold/Regular).
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


# ==============================================================================
# INITIALIZE DOCUMENT & SWATCHES (WITH LIVE VISUAL STEP-BY-STEP DRAWING)
# ==============================================================================
LIVE_DRAW = "--fast" not in sys.argv
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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 01 (100% Same-to-Same Editable English)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.5)


def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):
    p_obj = ASSETS_DIR / filename
    webp_obj = p_obj.with_suffix(".webp")
    if webp_obj.exists():
        p_obj = webp_obj
    img_path = str(p_obj.resolve()).replace("\\", "/")
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
    target_hscale: float = 0.92,
    lead_ratio: float = 0.94,
    underline: bool = False,
    v_justify: str = "top",
    inset_pt=None,
    max_pt_scale: float = 0.98,
    custom_font_family: str = None,
):
    if lines == ["INDIAN POST"] and not custom_font_family:
        custom_font_family = "Indian Post Mast"
        max_pt_scale = max(max_pt_scale, 1.35)
        lead_ratio = min(lead_ratio, 0.72)

    n_lines = len(lines)
    full_text = "\n".join(lines)
    box_h_pt = p(y2_px - y1_px)
    extra_h = 90.0 if custom_font_family else 12.0
    fit_rect = [p(x1_px), p(y1_px), p(x2_px), round(p(y2_px) + extra_h, 2)]
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

    if custom_font_family:
        ffam = custom_font_family
        fsty = "Regular"
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 16.0:
        ffam = "Georgia"
        fsty = "Bold"
    else:
        ffam = "Times New Roman"
        fsty = font_style

    line_lead_pt = round(max(7.5, (box_h_pt * 0.92) / n_lines), 1)
    max_pt_by_box = round((box_h_pt / n_lines) * max_pt_scale, 1)
    cap_pt = 240.0 if custom_font_family else 92.0

    lo = int(6.0 * 5)
    hi = int(min(cap_pt, max_pt_by_box) * 5)
    best_pt = 8.0
    best_hs = target_hscale

    while lo <= hi:
        mid = (lo + hi) // 2
        pt = round(mid / 5.0, 1)
        lead = round(max(line_lead_pt, pt * lead_ratio), 1)
        st = batch([
            {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
            {"command": "type.char", "params": {"attrs": {
                "fontFamily": ffam,
                "fontStyle": fsty,
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
        for try_hs in (0.86, 0.80, 0.75, 0.70, 0.65):
            lo2 = int(best_pt * 5)
            hi2 = int(min(cap_pt, max_pt_by_box) * 5)
            while lo2 <= hi2:
                mid = (lo2 + hi2) // 2
                pt = round(mid / 5.0, 1)
                lead = round(max(line_lead_pt, pt * lead_ratio), 1)
                st = batch([
                    {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                    {"command": "type.char", "params": {"attrs": {
                        "fontFamily": ffam,
                        "fontStyle": fsty,
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
            "fontFamily": ffam,
            "fontStyle": fsty,
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

    if stretch_lines:
        byte_cursor = 0
        for line_str in lines:
            b_len = utf8_len(line_str)
            b_start = byte_cursor
            b_end = byte_cursor + b_len
            byte_cursor = b_end + 1

            line_hs = best_hs
            max_hs_cap = 1.65 if custom_font_family else 1.08
            max_hs_int = int(min(max_hs_cap, best_hs + (0.55 if custom_font_family else 0.22)) * 100)
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
    lo_pt: float = 7.6,
    default_hscale: float = 0.92,
):
    box_h_pt = p(y2_px - y1_px)
    lead_pt = round(box_h_pt / max(1, target_lines), 2)
    clean_text = text.strip()
    r = cmd("frame.create", {
        "spread": 0,
        "rect": [p(x1_px), p(y1_px), p(x2_px), round(p(y2_px) + 6.0, 2)],
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

    best_cfg = (9.4, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.06:
            continue
        for hs100 in (98, 94, 90, 86, 82, 78, 74):
            hs = round(hs100 / 100.0, 2)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "Times New Roman",
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
            "fontFamily": "Times New Roman",
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
    if LIVE_DRAW:
        time.sleep(CONTENT_DELAY)
    return fid, sid, pt, hs


# ==============================================================================
# 1. LIVE EDITABLE ENGLISH MASTHEAD ('INDIAN POST') + EAR PANEL ('SAHIYAR') + WEBP ADS
# ==============================================================================
print("Building 100% Live Editable English Masthead ('INDIAN POST') & Ear Panel ('SAHIYAR')...")

# Top Dateline Left & Right above Masthead (y=152..190)
place_exact_display_lines(
    84, 152, 995, 190,
    lines=["Pages: 20+16  Price: Rs. 5.00**  Tuesday, Oct 20, 2026"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.90,
)
place_exact_display_lines(
    1025, 152, 2050, 190,
    lines=["Published Daily from Ahmedabad, Vadodara, Surat, Rajkot, Bhavnagar, Bhuj & Mumbai"],
    font_style="Bold",
    align="right",
    stretch_lines=True,
    target_hscale=0.88,
)

# Giant 'INDIAN POST' Masthead (x=84..2050, y=120..402) in 'Indian Post Mast' (Gujarat Samachar Calligraphic Shaily)
place_exact_display_lines(
    84, 120, 2050, 402,
    lines=["INDIAN POST"],
    font_style="Bold",
    fill_swatch="[Black]",
    align="center",
    stretch_lines=True,
    target_hscale=1.08,
    lead_ratio=0.55,
    max_pt_scale=1.70,
    custom_font_family="Indian Post Mast",
)

# Masthead Bottom Imprint Lines (y=476..548)
draw_line(84, 476, 2050, 476, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    88, 479, 2048, 510,
    lines=["Founder Editor: Late Shantilal A. Shah ▶ Samvat 2082 Shake 1948 Aso Sud-9 Year: 94, Issue: 285 ▶ Tel: 25508001-2-3-4 ▶ http://www.gujaratsamachar.com   AHMEDABAD"],
    font_style="Regular",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(84, 512, 2050, 512, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    88, 515, 2048, 546,
    lines=["Managing Editor: Shreyans Shantilal Shah ▶ Printer & Publisher: Shreyans Shantilal Shah, Khanpur, Ahmedabad-1 ▶ RNI Reg. No. 1562/57/REG.No. GAMC-28/2025-2026 Valid upto 31 Dec., 2026 Posting at A'bad RMS 1-2-3-4"],
    font_style="Regular",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
draw_line(84, 549, 2050, 549, swatch="[Black]", weight_pt=1.2)

# Top-Right Ear Panel ('SAHIYAR', x=2076..2718, y=158..545)
draw_box(2076, 158, 2718, 355, fill_swatch="GsOrangeBorder", fill_tint=0.82, stroke_weight_pt=0.0)
draw_box(2076, 158, 2718, 545, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=3.0)
place_exact_display_lines(
    2200, 162, 2594, 200,
    lines=["SPECIAL SUPPLEMENT"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.92,
)
place_exact_display_lines(
    2096, 208, 2698, 376,
    lines=["SAHIYAR"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=True,
    target_hscale=1.05,
    lead_ratio=0.65,
    max_pt_scale=1.18,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    2096, 408, 2698, 530,
    lines=[
        "• Women's Health, Wellness & Career Special",
        "• Festive Home Decor & Traditional Recipes"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.88,
)

# Place Photos & Commercial Ad Graphics (as .webp)
place_png(1412, 835, 2716, 1595, "ravana_dahan_photo.png")
place_png(1746, 2512, 2052, 2780, "tiger_train_photo.png")
place_png(1080, 3606, 1388, 3792, "gs_promo_pillar_only.png")
draw_box(1080, 3538, 1388, 3792, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    1086, 3542, 1382, 3602,
    lines=["INDIAN POST"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=True,
    target_hscale=0.95,
    custom_font_family="Indian Post Mast",
)
place_png(1411, 3085, 2718, 3802, "amul_ad_bg.png")
place_exact_display_lines(
    1445, 3110, 1650, 3230,
    lines=["AMUL", "MILK"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.95,
    lead_ratio=0.92,
)
place_exact_display_lines(
    1820, 3180, 2320, 3330,
    lines=["HAPPY", "VIJAYADASHAMI"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
    lead_ratio=0.94,
)
place_exact_display_lines(
    1720, 3728, 2410, 3792,
    lines=["AMUL DOODH PEETA HAI INDIA"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=False,
    target_hscale=0.92,
)
place_png(84, 3805, 2718, 3858, "cmyk_footer_bar.png")


# ==============================================================================
# 2. TOP-RIGHT RED BANNER BOX (Cols 7-8: Russia-Ukraine Space War Escalates)
# ==============================================================================
print("Building Top-Right Red Banner Box...")
draw_box(2077, 562, 2715, 813, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="[Black]", stroke_weight_pt=1.0)
place_exact_display_lines(
    2105, 576, 2688, 790,
    lines=[
        "Russia-Ukraine Space",
        "War Reaches Peak"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.88,
    lead_ratio=0.98,
)


# ==============================================================================
# 3. STORY 1: TOP-LEFT LEAD STORY (AMERICAN SATELLITE CHASED BY RUSSIAN SATELLITE)
# ==============================================================================
print("Building Story 1 (Satellite Lead Story)...")
place_exact_display_lines(
    174, 560, 1962, 634,
    lines=["World's First Incident of Intercepting an Enemy Nation's Satellite in Orbit"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(174, 639, 1962, 639, swatch="[Black]", weight_pt=1.6)

place_exact_display_lines(
    86, 645, 2048, 808,
    lines=["US Satellite Shadowed in Space"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)

# 2-Col Intro Left (Cols 1-2) + Dateline
place_exact_display_lines(
    550, 822, 722, 850,
    lines=["Kyiv, Oct 19"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    86, 852, 723, 915,
    text="The ongoing Russia-Ukraine conflict has escalated into outer space as Russia's Cosmos-2912 satellite actively stalked the US radar satellite",
    target_lines=2,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=14.0,
    hi_pt=11.5,
    lo_pt=8.4,
)

draw_line(736, 830, 736, 898, swatch="[Black]", weight_pt=0.75)

# 2-Col Intro Right (Cols 3-4)
place_exact_body_column(
    749, 822, 1386, 914,
    text="ICEYE-X36 assisting Ukraine. This unprecedented orbital pursuit has sparked grave concern over satellite security. Defense experts say this marks the first instance in modern warfare of one nation's satellite shadowing an adversary's spacecraft.",
    target_lines=3,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=0.0,
    hi_pt=11.5,
    lo_pt=8.4,
)

# 4-Col Subhead (Cols 1-4)
place_exact_display_lines(
    86, 920, 1386, 1076,
    lines=[
        "Russian Satellite Stalks US Radar Spacecraft Supplying",
        "Real-Time Drone and Missile Targeting Data to Ukraine"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# Col 1 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    85, 1088, 391, 1354,
    text="Ukrainian defense advisor Beskrestnov described Russia's expanding satellite network as the single biggest threat in the ongoing war. The Russian spacecraft closely pursued the American radar satellite providing real-time targeting data for Ukrainian drones and missiles, attempting to encircle the US craft in orbit and disrupt critical intelligence",
    target_lines=9,
    first_indent_pt=10.0,
)

draw_line(404, 1105, 404, 1348, swatch="[Black]", weight_pt=0.75)

# Col 2 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    416, 1088, 722, 1354,
    text="just 1 to 2 kilometers apart. In orbital mechanics, such proximity is considered perilously close. Low-Earth orbit satellites travel at nearly 27,000 kilometers per hour, meaning even a minor trajectory shift risks a catastrophic high-speed collision.\nAlthough the Russian satellite did not physically strike the American",
    target_lines=9,
    first_indent_pt=0.0,
)

# Orange Callout Box across Cols 1-2 (x=84..723, y=1362..1476)
draw_box(84, 1362, 723, 1476, fill_swatch="[Paper]", fill_tint=1.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    90, 1368, 717, 1466,
    lines=[
        "Russian Satellite 'Rassvet' Enables Real-Time Drone &",
        "Missile Control, Neutralizing Ukrainian Electronic Warfare"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)

# Col 1 Lower Body (y=1484..1722, 8 lines)
place_exact_body_column(
    85, 1484, 391, 1722,
    text="feeds to Kyiv's forces.\nSpace tracking scientists recorded that the Russian satellite repeatedly altered its orbital altitude to maneuver dangerously close to the US spacecraft. On October 7, the two satellites closed to within a distance of",
    target_lines=8,
    first_indent_pt=0.0,
)

draw_line(404, 1492, 404, 1715, swatch="[Black]", weight_pt=0.75)

# Col 2 Lower Body (y=1484..1694, 7 lines) + Jump line at y=1696..1724
place_exact_body_column(
    416, 1484, 722, 1694,
    text="radar satellite, analysts warn Russia could jam or blind spacecraft supplying real-time missile guidance to Ukraine. Any direct attack on a US-operated satellite would risk triggering a direct orbital confrontation between Washington and Moscow",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    450, 1696, 690, 1724,
    lines=["(Cont. on Page 9)"],
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
    lines=["Russia Fires 16 Ballistic Missiles at Ukraine"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(757, 1150, 1379, 1150, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    756, 1154, 1380, 1288,
    lines=[
        "Allied Nations No Longer Sharing",
        "Timely Intelligence: Zelenskyy"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    757, 1298, 1046, 1326,
    lines=["(PTI)                  Kyiv, Oct 19"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    757, 1328, 1048, 1608,
    text="Russia launched a fresh wave of strikes targeting Ukraine's energy infrastructure using ballistic missiles and jet-powered drones, Ukrainian President Volodymyr Zelenskyy stated on Monday.\nZelenskyy revealed that Ukraine received no prior intelligence warning from partner nations ahead of the",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_line(1068, 1318, 1068, 1585, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1086, 1298, 1378, 1580,
    text="barrage, whereas Western allies previously shared such early alerts routinely. He added that Washington's recent relaxation on Russian diesel purchases has emboldened Putin while compounding Kyiv's defense challenges. Posting on social media, Zelenskyy said the overnight Russian strikes damaged critical power",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1120, 1584, 1345, 1610,
    lines=["(Cont. on Page 9)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_display_lines(
    756, 1620, 1380, 1716,
    lines=[
        "Massive Russian Strikes Hit Ukrainian Energy Grid;",
        "Over Five Lakh Citizens Left Without Electricity"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    max_pt_scale=0.86,
)

draw_line(1400, 838, 1400, 2494, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 5. RAVANA DAHAN PHOTO CAPTION (Cols 5-8, x=1412..2716, y=1608..1782)
# ==============================================================================
print("Building Ravana Dahan 6-line Bold Photo Caption...")
place_exact_display_lines(
    1412, 1608, 2716, 1780,
    lines=[
        "Dussehra symbolizes the eternal triumph of truth over falsehood and righteousness over evil. On this auspicious day, effigies of Ravana, Meghnada and Kumbhakarna are",
        "consigned to flames. Rooted in the epic Ramayana, this tradition is not merely a religious festivity but a profound call for human introspection. Ravana was a learned",
        "scholar and mighty ruler, yet his arrogance, obstinacy and transgression of moral boundaries led to his downfall. His life reminds us that even supreme knowledge, power",
        "and wealth cannot save a person who loses wisdom and restraint. Ravana's ten heads represent lust, anger, greed, delusion, pride and other destructive human vices.",
        "These inner flaws corrode not only personal character but also social harmony. Burning Ravana's effigy becomes truly meaningful only when we pledge to conquer",
        "the vices within ourselves—and stand firmly against corruption, discrimination, hatred and the abuse of power in society."
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.96,
    max_pt_scale=0.92,
)
draw_line(1412, 1787, 2716, 1787, swatch="[Black]", weight_pt=0.85)


# ==============================================================================
# 6. STORY 3: DELHI DIARY (Col 1, x=84..392, y=1736..2499)
# ==============================================================================
print("Building Delhi Diary (Col 1)...")
draw_line(84, 1730, 1388, 1730, swatch="[Black]", weight_pt=0.85)
draw_box(84, 1736, 392, 2499, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_png(91, 1742, 385, 1824, "delhi_dome_only.png")
draw_box(91, 1824, 385, 1882, fill_swatch="GsOrangeBorder", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    98, 1828, 378, 1878,
    lines=["DELHI DIARY"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)

place_exact_display_lines(
    93, 1886, 383, 1948,
    lines=[
        "SIR Row: Kiren Rijiju and",
        "Shashi Tharoor Cross Swords"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_display_lines(
    185, 1953, 382, 1980,
    lines=["New Delhi, Oct 19"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    93, 1983, 383, 2466,
    text="Congress MP Shashi Tharoor hit back sharply at Union Minister Kiren Rijiju over his remarks regarding ongoing protests against the Special Intensive Revision (SIR). Tharoor asserted that India is neither Bangladesh nor France. Emphasizing that the opposition never condones violence, he stated that their sole demand is for free, fair and transparent elections. Unlike the violent unrest in France involving the torching of buses and police stations, India's opposition parties firmly believe in peaceful democratic protest. Rijiju had earlier posted on social media",
    target_lines=16,
    first_indent_pt=10.0,
)
place_exact_display_lines(
    120, 2466, 355, 2494,
    lines=["(Cont. on Page 9)"],
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
    lines=["Trump Adopts Softer Stance on India's Purchase of Russian Crude Oil"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(420, 1789, 1383, 1789, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    417, 1793, 1385, 1974,
    lines=[
        "India-US Trade Deal in Final",
        "Stage: US Secretary of State"
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
    690, 1990, 890, 2016,
    lines=["Washington, Oct 19"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    417, 2018, 890, 2076,
    text="A landmark bilateral trade agreement between India and the United States is likely to be sealed soon, US Secretary of State Marco Rubio",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=12.0,
)
draw_line(901, 1992, 901, 2074, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    912, 1990, 1385, 2076,
    text="announced on Monday. Ahead of his official visit to India, Rubio stated that both nations are actively working to finalize the comprehensive trade pact.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 2-4)
place_exact_display_lines(
    417, 2080, 1385, 2194,
    lines=[
        "Beyond Trade, High-Level Talks Likely to Cover Defense,",
        "Critical Technology, Energy Security and Strategic Ties"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# 3 Body Columns of US-India Trade Deal (y=2208..2498, 10 lines each)
place_exact_body_column(
    416, 2208, 722, 2498,
    text="Explaining Washington's decision to defer the proposed 100 percent secondary tariff on five major buyers of Russian crude oil including India, Secretary of State Marco Rubio noted that waivers were granted in recent months to prevent severe disruptions to global oil supply and prices. Maintaining market stability required postponing the punitive",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(736, 2215, 736, 2485, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    749, 2208, 1054, 2498,
    text="tariff measure. Both India and the United States are now very close to concluding their bilateral trade agreement.\nHowever, differences reportedly persist over market access in the dairy sector. While the US seeks wider entry for American dairy products in India, New Delhi remains firm on protecting domestic farmers. US Secretary of State",
    target_lines=10,
    first_indent_pt=0.0,
)
draw_line(1068, 2218, 1068, 3797, swatch="[Black]", weight_pt=0.85)
place_exact_body_column(
    1081, 2208, 1386, 2498,
    text="Marco Rubio is scheduled to arrive in India and meet External Affairs Minister S. Jaishankar in Mumbai on October 20. The two leaders are expected to review the India-US Global Strategic Partnership alongside key bilateral priorities across energy, trade, defense and advanced technology.",
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
        "AI Teaches Cyber Crime:",
        "$5,000 Token Cripples",
        "Servers of 100 Firms",
        "See Page No. 13"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.88,
    lead_ratio=0.92,
    max_pt_scale=0.90,
)

# Bedhadak Box
draw_box(1416, 2007, 1722, 2503, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
draw_line(1416, 2068, 1722, 2068, swatch="GsOrangeBorder", weight_pt=1.2)
draw_line(1416, 2405, 1722, 2405, swatch="GsOrangeBorder", weight_pt=1.2)

place_exact_display_lines(
    1422, 2010, 1595, 2056,
    lines=["FRANKLY"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.92,
    max_pt_scale=0.88,
)
place_exact_display_lines(
    1600, 2024, 1714, 2056,
    lines=["-Manjul"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
    max_pt_scale=0.88,
)
place_png(1419, 2071, 1719, 2402, "bedhadak_cartoon.png")
place_exact_display_lines(
    1424, 2408, 1714, 2494,
    lines=[
        "Sir, identifying the attackers",
        "is very hard—have they never",
        "protested against the govt?"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.82,
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
    lines=["Two Accused Hail from Haryana, One from Bihar; One Worked as Rapido Rider in Mumbai"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
draw_line(1744, 1850, 2716, 1850, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    1744, 1854, 2715, 2036,
    lines=[
        "Three Shooters Who Fired at Tiger",
        "Shroff Nabbed from Train in Kota"
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
    lines=["(By Our Correspondent)                     Mumbai, Oct 19"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1745, 2090, 2216, 2210,
    text="Three suspects wanted in the Sunday evening firing outside Bollywood actor Tiger Shroff's residence in Mumbai's Juhu were arrested from a train in Kota, Rajasthan. Rehan alias Sukka, a native of Haryana, opened fire while",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2226.5, 2066, 2226.5, 2206, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2238, 2062, 2715, 2210,
    text="Ritik Kumar alias Roshan—originally from Bihar and working as a Rapido bike-taxi rider in Mumbai—rode the getaway motorcycle. A third shooter, Phoolsingh, saw his pistol jam at the crucial moment. Though initially claimed to be a minor, Mumbai Police confirmed Phoolsingh is 18 years old.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 6-8)
place_exact_display_lines(
    1745, 2214, 2715, 2324,
    lines=[
        "Fled to Surat by Cab After Juhu Firing; Planned",
        "to Reach Delhi by Train and Escape into Nepal"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)

# Col 6 Above Photo (y=2338..2508, 6 lines)
place_exact_body_column(
    1745, 2338, 2051, 2508,
    text="After firing outside the Juhu building, the trio sped toward Andheri, abandoned their motorcycle near Andheri railway station, and boarded a local train to Borivali. From Borivali, they hired a cab to Surat and boarded the Pune-Jaipur",
    target_lines=6,
    first_indent_pt=10.0,
)
# Col 6 Below Photo (y=2786..3060, 9 lines)
place_exact_body_column(
    1745, 2786, 2051, 3060,
    text="Express. Mumbai Police seized the abandoned bike at Andheri and tracked the suspects through CCTV footage, technical surveillance and interstate police coordination. Alerted by Mumbai Crime Branch, Rajasthan Police laid a trap at Kota railway station and nabbed all three within minutes of the train's arrival.",
    target_lines=9,
    first_indent_pt=0.0,
)

draw_line(2064, 2352, 2064, 3054, swatch="[Black]", weight_pt=0.85)

# Col 7 Short Body (y=2338..2476, 5 lines)
place_exact_body_column(
    2077, 2338, 2382, 2476,
    text="Produced before a local court in Kota, the trio was granted transit remand to be brought back to Mumbai for interrogation.\nBriefing reporters in Mumbai, DCP Rajtilak Roshan",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2339, 2395.5, 2470, swatch="[Black]", weight_pt=0.75)

# Col 8 Short Body (y=2338..2448, 4 lines) + Jump line
place_exact_body_column(
    2408, 2338, 2714, 2448,
    text="stated that one of the arrested accused is 18 years old while the other two are aged 22. Two of the assailants fired five to six rounds at the",
    target_lines=4,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2450, 2449, 2675, 2476,
    lines=["(Cont. on Page 9)"],
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
    lines=["Police Fire Tear Gas Shells to Disperse Angry Protesters"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(2137, 2533, 2654, 2533, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    2076, 2538, 2714, 2678,
    lines=[
        "Militant Attack in Manipur:",
        "Three Poor Villagers Shot Dead"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    2530, 2684, 2714, 2710,
    lines=["Imphal, Oct 19"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    2076, 2712, 2715, 2826,
    text="Armed militants shot dead three villagers collecting firewood in a forest in Manipur on Monday, leaving three others injured and three more missing. Outraged locals staged a fierce protest and placed two victims' bodies outside the Chief Minister's residence.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    2076, 2830, 2715, 2930,
    lines=[
        "Protesters Place Victims' Bodies Outside CM Residence;",
        "Three Laborers Injured While Three Others Remain Missing"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    2076, 2940, 2382, 3060,
    text="Officials said heavily armed militants opened indiscriminate fire on a group of villagers gathering firewood along the border of Imphal East and Kangpokpi",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(2395.5, 2950, 2395.5, 3058, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2940, 2714, 3032,
    text="districts, killing laborers Arubam Ronil (35) and Lairenjam Inaobi (51) on the spot while critically",
    target_lines=3,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2450, 3033, 2675, 3060,
    lines=["(Cont. on Page 9)"],
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
    lines=["Historic Market Blockbuster by Reliance's Digital Arm"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(128, 2574, 1013, 2574, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    88, 2580, 1052, 2774,
    lines=[
        "Jio Platforms Raises Rs 8,110",
        "Crore from Anchor Investors"
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
    395, 2784, 548, 2810,
    lines=["Mumbai, Oct 19"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    88, 2810, 548, 2918,
    text="Jio Platforms, the digital services subsidiary of Reliance Industries, has finalized its share allocation to anchor investors ahead of its much-anticipated Initial Public Offering (IPO), raising",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(566, 2792, 566, 2914, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2784, 1052, 2918,
    text="Rs 8,110 crore from marquee institutions. According to investment banking sources, Jio's anchor book witnessed unprecedented demand from global and domestic institutional investors, with total bids crossing Rs 2.5 lakh crore.",
    target_lines=5,
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 1-3)
place_exact_display_lines(
    88, 2922, 1052, 3044,
    lines=[
        "LIC, BlackRock & GIC Lead Anchor Book; Institutional",
        "Investors Place Record Bids Exceeding Rs 2.5 Lakh Crore"
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
    text="This marks the largest institutional demand ever recorded in Indian IPO history. Over 70 global and domestic financial giants participated across 212 investment scheme lines in Jio Platforms' anchor book, including the world's largest sovereign wealth funds, global asset managers, Indian mutual funds, insurance companies and pension funds. Life Insurance Corporation of India (LIC) emerged as the single largest anchor investor with an allocation of Rs 500 crore.\nGlobal titans BlackRock, Capital International, Fidelity Management, Singapore's sovereign wealth fund GIC, and top domestic mutual funds including SBI Mutual Fund, HDFC Mutual Fund and ICICI Prudential Mutual Fund were allocated shares worth Rs 425 crore each.\nAditya Birla Sun Life MF and Capital World secured Rs 300 crore each, Schroders Rs 293 crore, while Kotak",
    target_lines=25,
    first_indent_pt=10.0,
)
draw_line(405, 3060, 405, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3054, 720, 3792,
    text="MF, Nippon India MF and Ninety One received Rs 200 crore each, JPMorgan Asset Management Rs 182 crore, and ADIA, QIA, Allianz and Dragoneer invested Rs 150 crore apiece.\nA standout feature of Jio Platforms' anchor book is the strong participation of long-only sovereign wealth and pension funds. Alongside GIC, Abu Dhabi Investment Authority (ADIA) and Qatar Investment Authority (QIA), leading international pension funds such as Norway's Norges Bank Investment Management, California State Teachers' Retirement System (CalSTRS) and Florida Retirement System committed substantial capital. Leading Indian insurers and pension funds including HDFC Life, SBI Life, HDFC Pension, SBI Pension and ICICI Prudential also joined.\nGlobal technology specialists and growth-focused funds",
    target_lines=25,
    first_indent_pt=0.0,
)
draw_line(730.5, 3060, 730.5, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3054, 1050, 3792,
    text="such as Dragoneer, Janus Henderson and Fidelity's flagship Contrafund also secured allocations in Jio.\nDomestically, prominent billionaire family offices showed robust appetite, including Premji Invest (Wipro), the HCL Family Office, Enam Holdings and Zerodha's Rainmatter. The IPO opens for public subscription on October 21.\nFollowing the overwhelming anchor response, market attention now turns to the public issue opening tomorrow.\nJio Platforms plans to deploy the proceeds to expand its next-generation 5G network, cloud computing infrastructure, artificial intelligence (AI) platforms and enterprise digital services. At the upper price band, the issue stands as the largest IPO in Indian capital market history.",
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
    lines=["Over 2,400 Arrested Amid Violent Nationwide Unrest"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(1112, 2554, 1688, 2554, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    1080, 2559, 1718, 2698,
    lines=[
        "Curfew Imposed in French Cities Amid",
        "Riots; Macron Hints at Emergency"
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
    lines=["(PTI)                                                        Paris, Oct 19"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2738, 1718, 2884,
    text="French Prime Minister Sebastien Lecornu has instructed regional prefects to impose targeted local curfews across violence-hit districts. The directive follows weekend riots in which city halls, public buildings and thousands of businesses were vandalized across France.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=14.0,
)
place_exact_display_lines(
    1080, 2888, 1719, 2988,
    lines=[
        "Over 60,000 Security Personnel Deployed Across France;",
        "Trade Unions Call Nationwide Strike on November 5"
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
    text="Speaking after an emergency security meeting with top officials, the Prime Minister remarked that despite widespread arson and heavy property destruction on Saturday night, it was a miracle that no fatalities occurred.\nHe strongly defended police officers confronting violent mobs and said specific curfew zones would be notified shortly.\nThe orders came hours after Interior Minister Laurent Nunez tendered his resignation, which President Emmanuel Macron refused to accept.\nIn an official statement, the Elysee Palace emphasized that maintaining law and order under the current crisis requires",
    target_lines=18,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3009, 1399.5, 3797, swatch="[Black]", weight_pt=0.85)

# Col 5 Short Top Body (y=2992..3038, 2 lines) + Jump line above Amul Ad
place_exact_body_column(
    1412, 2992, 1718, 3038,
    text="Interior Minister Laurent Nunez to remain firmly in command of security operations",
    target_lines=2,
    first_indent_pt=0.0,
    hi_pt=9.6,
)
place_exact_display_lines(
    1450, 3044, 1680, 3067,
    lines=["(Cont. on Page 9)"],
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
    pd_path = target_dir / "Page_01_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_01_English_SameToSame.dns"
    png_path = target_dir / "Page_01_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_01_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_01_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_01_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_01_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
