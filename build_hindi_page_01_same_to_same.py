# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 1 BUILDER ('आस-पास' — हिंदी गुजरात समाचार)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt (37.04 x 52.57 cm)
- Exact same layout, exact same frame positions/sizes, and accurate Hindi translation of Page 1.
- Masthead: Giant 'आस-पास' in 'DB Hindi Mast' + Hindi dateline & imprint lines + 'सहियर' Ear Panel.
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi' Bold/Regular).
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 01 (100% Same-to-Same Editable Hindi)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.5)


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
    target_hscale: float = 0.92,
    lead_ratio: float = 0.94,
    underline: bool = False,
    v_justify: str = "top",
    inset_pt=None,
    max_pt_scale: float = 0.98,
    custom_font_family: str = None,
):
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
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 18.0:
        ffam = "DB Madhurima"
        fsty = "Regular"
    else:
        ffam = "DB Hindi"
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
        for try_hs in (0.86, 0.80, 0.75, 0.70):
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
            for trk in ([0] if custom_font_family else range(18, -1, -3)):
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
    lo_pt: float = 8.0,
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

    best_cfg = (9.8, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.06:
            continue
        for hs100 in (98, 94, 90, 86, 82, 78):
            hs = round(hs100 / 100.0, 2)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "DB Hindi",
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
            "fontFamily": "DB Hindi",
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
# 1. LIVE EDITABLE HINDI MASTHEAD ('आस-पास') + EAR PANEL ('सहियर') + PHOTOS/ADS
# ==============================================================================
print("Building 100% Live Editable Hindi Masthead ('आस-पास') & Ear Panel ('सहियर')...")

# Top Dateline Left & Right above Masthead (y=152..192)
place_exact_display_lines(
    84, 152, 995, 190,
    lines=["पृष्ठ : २०+१६ मूल्य : रु. ५-००** ता. २० अक्टूबर २०२६ मंगलवार"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.90,
)
place_exact_display_lines(
    1025, 152, 2050, 190,
    lines=["अहमदाबाद, वडोदरा, सूरत, राजकोट, भावनगर, भुज और मुंबई से प्रकाशित दैनिक"],
    font_style="Bold",
    align="right",
    stretch_lines=True,
    target_hscale=0.90,
)

# Giant 'आस-पास' Masthead (x=84..2050, y=120..402) in 'DB Hindi Mast' (Gujarat Samachar Calligraphic Shaily)
place_exact_display_lines(
    84, 120, 2050, 402,
    lines=["आस-पास"],
    font_style="Bold",
    fill_swatch="[Black]",
    align="center",
    stretch_lines=True,
    target_hscale=1.38,
    lead_ratio=0.55,
    max_pt_scale=1.72,
    custom_font_family="Indian Post Mast",
)

# Masthead Bottom Imprint Lines (y=476..548)
draw_line(84, 476, 2050, 476, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    88, 479, 2048, 510,
    lines=["संस्थापक तंत्री : स्व. शांतिलाल अ. शाह ▶ संवत २०८२ शक १९४८ आश्विन शुक्ल - ९ वर्ष : ९४, अंक : २८५ ▶ फोन : २५५०८००१-२-३-४ ▶ http://www.gujaratsamachar.com   AHMEDABAD"],
    font_style="Regular",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(84, 512, 2050, 512, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    88, 515, 2048, 546,
    lines=["मैनेजिंग तंत्री : श्रेयांस शांतिलाल शाह ▶ मुद्रक एवं प्रकाशक : श्रेयांस शांतिलाल शाह खानपुर, अहमदाबाद-१ ▶ RNI Reg. No. 1562/57/REG.No. GAMC-28/2025-2026 Valid upto 31 Dec., 2026 Posting at A'bad RMS 1-2-3-4"],
    font_style="Regular",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
draw_line(84, 549, 2050, 549, swatch="[Black]", weight_pt=1.2)

# Top-Right Ear Panel ('सहियर', x=2076..2718, y=158..545)
draw_box(2076, 158, 2718, 355, fill_swatch="GsOrangeBorder", fill_tint=0.82, stroke_weight_pt=0.0)
draw_box(2076, 158, 2718, 545, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=3.0)
place_exact_display_lines(
    2220, 162, 2574, 200,
    lines=["पठन विशेष"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.95,
)
place_exact_display_lines(
    2096, 204, 2698, 384,
    lines=["सहियर"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=True,
    target_hscale=1.18,
    lead_ratio=0.65,
    max_pt_scale=1.18,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    2096, 408, 2698, 530,
    lines=[
        "• महिला स्वास्थ्य, सौंदर्य और करियर विशेषांक",
        "• त्योहारों में घर की सजावट और पारंपरिक व्यंजन"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)

# Place Photos & Commercial Ad Graphics
place_png(1412, 835, 2716, 1595, "ravana_dahan_photo.png")
place_png(1746, 2512, 2052, 2780, "tiger_train_photo.png")
place_png(1080, 3606, 1388, 3792, "gs_promo_pillar_only.png")
draw_box(1080, 3538, 1388, 3792, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    1086, 3542, 1382, 3602,
    lines=["आस-पास"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=True,
    target_hscale=1.0,
    custom_font_family="Indian Post Mast",
)
place_png(1411, 3085, 2718, 3802, "amul_ad_bg.png")
place_exact_display_lines(
    1445, 3110, 1650, 3230,
    lines=["अमूल", "दूध"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.95,
    lead_ratio=0.92,
)
place_exact_display_lines(
    1820, 3180, 2320, 3330,
    lines=["विजयादशमी की", "शुभकामनाएं"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.92,
    lead_ratio=0.94,
)
place_exact_display_lines(
    1720, 3728, 2410, 3792,
    lines=["अमूल दूध पीता है इंडिया"],
    font_style="Bold",
    fill_swatch="GsRedBanner",
    align="center",
    stretch_lines=False,
    target_hscale=0.94,
)
place_png(84, 3805, 2718, 3858, "cmyk_footer_bar.png")


# ==============================================================================
# 2. TOP-RIGHT RED BANNER BOX (Cols 7-8: रूस और यूक्रेन का अंतरिक्ष युद्ध चरम पर)
# ==============================================================================
print("Building Top-Right Red Banner Box...")
draw_box(2077, 562, 2715, 813, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="[Black]", stroke_weight_pt=1.0)
place_exact_display_lines(
    2105, 576, 2688, 790,
    lines=[
        "रूस और यूक्रेन का",
        "अंतरिक्ष युद्ध चरम पर"
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
    lines=["दुश्मन देश के सैटेलाइट को घेरने की दुनिया की पहली घटना"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(174, 639, 1962, 639, swatch="[Black]", weight_pt=1.6)

place_exact_display_lines(
    86, 645, 2048, 808,
    lines=["अमेरिकी सैटेलाइट का किया जा रहा पीछा"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)

# 2-Col Intro Left (Cols 1-2) + Dateline
place_exact_display_lines(
    580, 822, 722, 850,
    lines=["कीव, ता. १९"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    86, 852, 723, 915,
    text="रूस-यूक्रेन के बीच चल रहा युद्ध अब अगले स्तर पर पहुंच गया है। रूस के कॉसमॉस-२९१२ सैटेलाइट ने यूक्रेन की मदद कर रहे अमेरिकी रडार सैटेलाइट",
    target_lines=2,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=14.0,
    hi_pt=11.5,
    lo_pt=8.6,
)

draw_line(736, 830, 736, 898, swatch="[Black]", weight_pt=0.75)

# 2-Col Intro Right (Cols 3-4)
place_exact_body_column(
    749, 822, 1386, 914,
    text="आईसीआई-एक्स३६ सैटेलाइट का पीछा किया है। इससे अंतरिक्ष में सैटेलाइट की सुरक्षा को लेकर चिंता जताई जा रही है। विशेषज्ञ कह रहे हैं कि आधुनिक युद्ध में किसी देश द्वारा दुश्मन देश के सैटेलाइट का पीछा करने की यह पहली घटना है।",
    target_lines=3,
    font_style="Bold",
    align="leftJustified",
    first_indent_pt=0.0,
    hi_pt=11.5,
    lo_pt=8.6,
)

# 4-Col Subhead (Cols 1-4)
place_exact_display_lines(
    86, 920, 1386, 1076,
    lines=[
        "यूक्रेन को ड्रोन और मिसाइल का रियल टाइम डेटा देने वाले",
        "अमेरिकी सैटेलाइट का रूसी सैटेलाइट ने किया पीछा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)

# Col 1 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    85, 1088, 391, 1354,
    text="यूक्रेन के सलाहकार ब्रेस्केस्तनोव ने रूस के सैटेलाइट नेटवर्क को युद्ध में सबसे बड़ा खतरा बताया है। रूसी सैटेलाइट ने यूक्रेन के ड्रोन और मिसाइलों को रियल टाइम रडार डेटा देने वाले अमेरिका के सैटेलाइट का पीछा किया। एक तरह से अमेरिकी सैटेलाइट को अंतरिक्ष में घेरने की कोशिश कर यूक्रेन को मिलने वाले रियल टाइम रडार डेटा को प्रभावित",
    target_lines=9,
    first_indent_pt=10.0,
)

draw_line(404, 1105, 404, 1348, swatch="[Black]", weight_pt=0.75)

# Col 2 Upper Body (y=1088..1354, 9 lines)
place_exact_body_column(
    416, 1088, 722, 1354,
    text="१ से २ किलोमीटर जितनी ही दूरी थी। अंतरिक्ष के संदर्भ में यह बेहद कम दूरी मानी जाती है। निचली कक्षा में सैटेलाइट लगभग २७ हजार किलोमीटर प्रतिघंटे की रफ्तार से घूमते हैं। ऐसे में यह दूरी बेहद खतरनाक मानी जाती है। इससे सैटेलाइटों के बीच टक्कर का खतरा बढ़ सकता है।\nहालांकि, रूसी सैटेलाइट ने अमेरिकी",
    target_lines=9,
    first_indent_pt=0.0,
)

# Orange Callout Box across Cols 1-2 (x=84..723, y=1362..1476)
draw_box(84, 1362, 723, 1476, fill_swatch="[Paper]", fill_tint=1.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_exact_display_lines(
    90, 1368, 717, 1466,
    lines=[
        "रूसी सैटेलाइट रास्वेट ने यूक्रेन के ड्रोन-मिसाइलों का रियल",
        "टाइम कंट्रोल कर इलेक्ट्रॉनिक वॉरफेयर को किया नाकाम"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# Col 1 Lower Body (y=1484..1722, 8 lines)
place_exact_body_column(
    85, 1484, 391, 1722,
    text="करने की कोशिश की गई थी।\nअंतरिक्ष वैज्ञानिकों ने दर्ज किया कि रूसी सैटेलाइट ने अपनी कक्षा बार-बार बदलकर अमेरिकी सैटेलाइट के बेहद करीब जाने की कोशिश की। कई बार तो दोनों सैटेलाइटों के बीच मात्र कुछ किलोमीटर की ही दूरी रह गई थी। ७ अक्टूबर को तो दोनों सैटेलाइटों के बीच मात्र",
    target_lines=8,
    first_indent_pt=0.0,
)

draw_line(404, 1492, 404, 1715, swatch="[Black]", weight_pt=0.75)

# Col 2 Lower Body (y=1484..1694, 7 lines) + Jump line at y=1696..1724
place_exact_body_column(
    416, 1484, 722, 1694,
    text="रडार सैटेलाइट पर हमला नहीं किया है, परंतु भविष्य में यूक्रेन की मिसाइलों और ड्रोन को रियल टाइम रडार डेटा देने वाले सैटेलाइट पर हमला कर उसे दिशाहीन कर सकता है। यदि रूस यूक्रेन की मदद कर रहे अमेरिकी सैटेलाइट को नष्ट करता है तो अंतरिक्ष में अमेरिका-रूस के बीच",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    460, 1696, 680, 1724,
    lines=["(शेष पृष्ठ ९ पर)"],
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
    lines=["रूस ने यूक्रेन पर दागीं १६ बैलिस्टिक मिसाइलें"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(757, 1150, 1379, 1150, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    756, 1154, 1380, 1288,
    lines=[
        "सहयोगी देश अब खुफिया जानकारी",
        "साझा नहीं कर रहे हैं : ज़ेलेंस्की"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    757, 1298, 1046, 1326,
    lines=["(पीटीआई)            कीव, ता. १९"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    757, 1328, 1048, 1608,
    text="रूस ने बैलिस्टिक मिसाइलों और जेट पावर्ड ड्रोन का उपयोग करके यूक्रेन के एनर्जी इन्फ्रास्ट्रक्चर पर नए सिरे से हमले किए हैं, ऐसा यूक्रेन के राष्ट्रपति ज़ेलेंस्की ने एक बयान में कहा है।\nज़ेलेंस्की ने बताया कि यूक्रेन को इस हमले के संबंध में सहयोगी देशों से कोई पूर्व चेतावनी नहीं मिली",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_line(1068, 1318, 1068, 1585, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1086, 1298, 1378, 1580,
    text="थी। जबकि पहले ये देश ऐसी खुफिया जानकारी साझा करते थे। रूस से डीजल खरीदने की अमेरिका की घोषणा से पुतिन को फायदा हुआ है और ज़ेलेंस्की को मुश्किलों का सामना करना पड़ रहा है। ज़ेलेंस्की ने सोशल मीडिया पर बताया कि रात में रूस द्वारा किए गए हमले में यूक्रेन में एनर्जी",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1130, 1584, 1335, 1610,
    lines=["(शेष पृष्ठ ९ पर)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_display_lines(
    756, 1620, 1380, 1716,
    lines=[
        "यूक्रेन के एनर्जी इन्फ्रास्ट्रक्चर पर रूस के भीषण हमले",
        "पांच लाख से अधिक लोग बिजली से वंचित हुए"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
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
        "दशहरा अर्थात असत्य पर सत्य और अधर्म पर धर्म की विजय का प्रतीक। इस दिन रावण, मेघनाद और कुंभकर्ण के पुतलों का दहन किया जाता है। रामायण की कथा से",
        "जुड़ी यह परंपरा केवल धार्मिक उत्सव नहीं है, बल्कि मनुष्य को आत्ममंथन करने की प्रेरणा देने वाला अवसर भी है। रावण विद्वान, पराक्रमी और शक्तिशाली राजा था।",
        "फिर भी, उसका अहंकार, हठ और नैतिक मर्यादाओं का उल्लंघन उसके पतन का कारण बना। उसका चरित्र समझाता है कि ज्ञान, शक्ति और वैभव होने के बावजूद यदि व्यक्ति विवेक खो दे",
        "तो उसकी उपलब्धियां भी उसे विनाश से बचा नहीं सकतीं। रावण के दस सिरों को काम, क्रोध, लोभ, मोह, अहंकार और अन्य नकारात्मक प्रवृत्तियों से जोड़ा जाता है।",
        "ये दोष न केवल व्यक्ति के जीवन को, बल्कि उसके संबंधों और सामाजिक व्यवहार को भी प्रभावित करते हैं। रावण दहन का सच्चा अर्थ तभी सार्थक होता है, जब हम अपने",
        "जीवन में मौजूद दोषों का त्याग करने का संकल्प लें। और हां, भ्रष्टाचार, भेदभाव, नफरत और सत्ता के दुरुपयोग के खिलाफ खड़े होना भी इसी संदेश का एक हिस्सा है।"
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
# 6. STORY 3: DELHI KI BAAT (Col 1, x=84..392, y=1736..2499)
# ==============================================================================
print("Building Delhi Ki Baat (Col 1)...")
draw_line(84, 1730, 1388, 1730, swatch="[Black]", weight_pt=0.85)
draw_box(84, 1736, 392, 2499, fill_swatch="[Paper]", fill_tint=0.0, stroke_swatch="GsOrangeBorder", stroke_weight_pt=1.5)
place_png(91, 1742, 385, 1824, "delhi_dome_only.png")
draw_box(91, 1824, 385, 1882, fill_swatch="GsOrangeBorder", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    98, 1828, 378, 1878,
    lines=["दिल्ली की बात"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)

place_exact_display_lines(
    93, 1886, 383, 1948,
    lines=[
        "एसआईआर विवाद : रिजिजू",
        "और शशि थरूर आमने-सामने"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    200, 1953, 382, 1980,
    lines=["नई दिल्ली, ता. १९"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    93, 1983, 383, 2466,
    text="केंद्रीय मंत्री किरेन रिजिजू द्वारा एसआईआर के खिलाफ हो रहे विरोध प्रदर्शनों को लेकर दिए गए बयान पर कांग्रेस सांसद शशि थरूर ने प्रतिक्रिया दी है। शशि थरूर का कहना है कि भारत न तो बांग्लादेश है और न ही फ्रांस। उन्होंने कहा कि विपक्ष हिंसा का समर्थन नहीं करता, परंतु विपक्ष की मांग स्वतंत्र और निष्पक्ष चुनाव कराने की है। फ्रांस में जिस तरह बसों तथा पुलिस थानों में आग लगाने जैसी हिंसक घटनाएं होती हैं, ऐसे विरोध का विपक्षी दल कभी समर्थन नहीं करते। विपक्ष शांतिपूर्ण विरोध करने में विश्वास रखता है। किरेन रिजिजू ने सोशल मीडिया पर एक पोस्ट",
    target_lines=16,
    first_indent_pt=10.0,
)
place_exact_display_lines(
    125, 2466, 350, 2494,
    lines=["(शेष पृष्ठ ९ पर)"],
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
    lines=["भारत द्वारा रूसी तेल की खरीद के मुद्दे पर ट्रम्प का नरम रुख"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(420, 1789, 1383, 1789, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    417, 1793, 1385, 1974,
    lines=[
        "भारत-अमेरिका ट्रेड डील अंतिम",
        "चरण में : अमेरिकी विदेश मंत्री"
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
    lines=["वॉशिंगटन, ता. १९"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    417, 2018, 890, 2076,
    text="भारत और अमेरिका के बीच जल्द ही ट्रेड डील होने की संभावना है। यह जानकारी अमेरिका के विदेश मंत्री मार्को रुबियो",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=12.0,
)
draw_line(901, 1992, 901, 2074, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    912, 1990, 1385, 2076,
    text="द्वारा सोमवार को दी गई। भारत आ रहे अमेरिकी विदेश मंत्री ने कहा कि हम फिलहाल भारत के साथ ट्रेड डील को अंतिम रूप देने का प्रयास कर रहे हैं।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 2-4)
place_exact_display_lines(
    417, 2080, 1385, 2194,
    lines=[
        "भारत और अमेरिका के बीच व्यापार के अलावा रक्षा,",
        "टेक्नोलॉजी, ऊर्जा सहित कई क्षेत्रों में भी चर्चा की संभावना"
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
    text="रूसी क्रूड ऑयल खरीदने वाले भारत सहित पांच बड़े देशों पर १०० प्रतिशत टैरिफ लगाने के फैसले को फिलहाल टालने के पीछे का कारण बताते हुए अमेरिकी विदेश मंत्री मार्को ने कहा कि पिछले कुछ महीनों में हमने यह छूट दी क्योंकि इसका असर वैश्विक आपूर्ति और कीमतों पर पड़ रहा था। हर तरह से संतुलन बनाए रखना जरूरी होता है इसलिए यह फैसला फिलहाल",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(736, 2215, 736, 2485, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    749, 2208, 1054, 2498,
    text="टाल दिया गया है। भारत और अमेरिका दोनों ट्रेड डील यानी व्यापार समझौतों को अंतिम रूप देने के बेहद करीब पहुंच गए हैं।\nहालांकि डेयरी क्षेत्र का मुद्दा अभी भी अटका होने की खबरें हैं। अमेरिका फिलहाल भारतीय बाजार में डेयरी क्षेत्र में जगह बनाना चाहता है। हालांकि भारत इस फैसले के लिए अभी तैयार नहीं है। गौरतलब है कि अमेरिकी विदेश मंत्री",
    target_lines=10,
    first_indent_pt=0.0,
)
draw_line(1068, 2218, 1068, 3797, swatch="[Black]", weight_pt=0.85)
place_exact_body_column(
    1081, 2208, 1386, 2498,
    text="मार्को रुबियो फिलहाल भारत के दौरे पर आ रहे हैं। वे २० अक्टूबर को मुंबई में भारत के विदेश मंत्री एस. जयशंकर से मुलाकात करेंगे। भारत और अमेरिका के बीच वैश्विक रणनीतिक साझेदारी के साथ-साथ ऊर्जा, व्यापार, रक्षा, टेक्नोलॉजी आदि क्षेत्रों में भी द्विपक्षीय सहयोग के महत्वपूर्ण मुद्दों पर चर्चा होने की उम्मीद है।",
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
        "एआई साइबर क्राइम",
        "सिखाएगा : ५०००",
        "डॉलर के टोकन से १००",
        "कंपनियों के सर्वर ठप",
        "पढ़ें पृष्ठ नं. १३"
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
    lines=["बेधड़क"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.95,
    max_pt_scale=0.88,
)
place_exact_display_lines(
    1610, 2024, 1714, 2056,
    lines=["-मंजुल"],
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
        "साहब, हमलावरों को पहचानना",
        "बहुत मुश्किल है, क्या उन्होंने कभी",
        "सरकार के खिलाफ प्रदर्शन नहीं किया ?"
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
    lines=["दो आरोपी मूल रूप से हरियाणा के, एक बिहार का : एक मुंबई में रैपिडो राइडर"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 1850, 2716, 1850, swatch="[Black]", weight_pt=1.4)

place_exact_display_lines(
    1744, 1854, 2715, 2036,
    lines=[
        "टाइगर पर फायरिंग कर भागे",
        "तीनों कोटा में ट्रेन से पकड़े गए"
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
    lines=["(प्रतिनिधि द्वारा)                             मुंबई, ता. १९"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1745, 2090, 2216, 2210,
    text="बॉलीवुड अभिनेता टाइगर श्रॉफ पर रविवार शाम मुंबई के जुहू में हुई फायरिंग की घटना में तीन आरोपियों को राजस्थान के कोटा में गिरफ्तार किया गया है। मूल रूप से हरियाणा के रेहान उर्फ सुक्का ने टाइगर पर गोलियां बरसाई थीं जबकि मूल रूप से",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2226.5, 2066, 2226.5, 2206, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2238, 2062, 2715, 2210,
    text="बिहार के और मुंबई में रैपिडो राइडर के रूप में काम करने वाले रितिक कुमार उर्फ रोशन ने बाइक चलाने का काम संभाला था। हालांकि, फूलसिंह की गन ऐन वक्त पर लॉक हो जाने से टाइगर बच गया था। फूलसिंह के नाबालिग होने का दावा पहले किया गया था परंतु मुंबई पुलिस ने बताया कि वह १८ वर्ष का है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 6-8)
place_exact_display_lines(
    1745, 2214, 2715, 2324,
    lines=[
        "गोलीबारी के बाद सूरत पहुंचे, ट्रेन से दिल्ली",
        "जाकर नेपाल भागने की फिराक में थे"
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
    text="जुहू में फायरिंग के बाद तीनों आरोपी अंधेरी की तरफ भागे थे। अंधेरी रेलवे स्टेशन पहुंचकर उन्होंने वहां से बोरीवली जाने वाली लोकल ट्रेन पकड़ी थी। बोरीवली उतरने के बाद वे कैब से सूरत पहुंचे थे। सूरत से वे पुणे-जयपुर",
    target_lines=6,
    first_indent_pt=10.0,
)
# Col 6 Below Photo (y=2786..3060, 9 lines)
place_exact_body_column(
    1745, 2786, 2051, 3060,
    text="ट्रेन में बैठ गए थे। उन्होंने अंधेरी स्टेशन के पास बाइक छोड़ दी थी जिसे पुलिस ने जब्त कर लिया। सीसीटीवी फुटेज तथा टेक्निकल सर्विलांस के अलावा अंतरराज्यीय पुलिस समन्वय से मुंबई पुलिस ने तीनों का सुराग लगाया। राजस्थान पुलिस को सूचना दिए जाने के बाद कोटा स्टेशन पर स्थानीय पुलिस ने जाल बिछाया था। ट्रेन आते ही कुछ ही",
    target_lines=9,
    first_indent_pt=0.0,
)

draw_line(2064, 2352, 2064, 3054, swatch="[Black]", weight_pt=0.85)

# Col 7 Short Body (y=2338..2476, 5 lines)
place_exact_body_column(
    2077, 2338, 2382, 2476,
    text="मिनटों में पुलिस ने ट्रेन से तीनों को गिरफ्तार कर लिया। कोटा में उन्हें अदालत के समक्ष पेश किए जाने पर अदालत ने तीनों को मुंबई ले जाने के लिए ट्रांजिट रिमांड दिया।\nमुंबई में डीसीपी राजतिलक रोशन ने",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2339, 2395.5, 2470, swatch="[Black]", weight_pt=0.75)

# Col 8 Short Body (y=2338..2448, 4 lines) + Jump line
place_exact_body_column(
    2408, 2338, 2714, 2448,
    text="मीडिया को जानकारी देते हुए कहा कि तीन में से एक आरोपी १८ वर्ष का है और अन्य दो बाईस वर्ष के हैं। पकड़े गए तीन में से दो ने पांच से छह राउंड फायरिंग",
    target_lines=4,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2460, 2449, 2665, 2476,
    lines=["(शेष पृष्ठ ९ पर)"],
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
    lines=["लोगों के प्रदर्शन पर आंसू गैस के गोले छोड़े गए"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(2137, 2533, 2654, 2533, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    2076, 2538, 2714, 2678,
    lines=[
        "मणिपुर में उग्रवादियों की हिंसा",
        "जंगल में तीन गरीबों को मार डाला"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    2550, 2684, 2714, 2710,
    lines=["इम्फाल, ता. १९"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    2076, 2712, 2715, 2826,
    text="उग्रवादियों ने मणिपुर में सोमवार को जंगल से लकड़ी बीनने वाले तीन लोगों की गोली मारकर हत्या कर दी, जबकि तीन अन्य घायल हो गए और तीन अन्य लापता हैं। स्थानीय लोगों ने घटना के विरोध में प्रदर्शन कर दो मृतकों के शव मुख्यमंत्री आवास के बाहर रख दिए।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    2076, 2830, 2715, 2930,
    lines=[
        "प्रदर्शनकारियों ने शवों को सीएम आवास के बाहर रखा",
        "तीन श्रमिक घायल जबकि तीन अन्य लापता हुए"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 2940, 2382, 3060,
    text="अधिकारियों ने बताया कि उग्रवादियों ने इम्फाल पूर्व और कांगपोकपी जिले की सीमा पर लकड़ी इकट्ठा करने वाले लोगों के समूह पर गोलियां",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(2395.5, 2950, 2395.5, 3058, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2940, 2714, 3032,
    text="चलाईं जिससे अरुबम रोनिल (३५) और लैरेन लोकपम इनाओबी (५१) नामक श्रमिकों की गोली लगने से घटनास्थल",
    target_lines=3,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    2460, 3033, 2665, 3060,
    lines=["(शेष पृष्ठ ९ पर)"],
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
    lines=["रिलायंस की डिजिटल इकाई का ऐतिहासिक धमाका"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.92,
)
draw_line(128, 2574, 1013, 2574, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    88, 2580, 1052, 2774,
    lines=[
        "जियो प्लेटफॉर्म्स ने एंकर इन्वेस्टर्स",
        "से जुटाए रु. ८,११० करोड़"
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
    lines=["मुंबई, १९"],
    font_style="Regular",
    align="right",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    88, 2810, 548, 2918,
    text="रिलायंस इंडस्ट्रीज की डिजिटल सर्विस इकाई ‘जियो प्लेटफॉर्म्स’ द्वारा अपने बहुप्रतीक्षित इनिशियल पब्लिक ऑफरिंग (IPO) से पूर्व एंकर इन्वेस्टर्स के लिए शेयर आवंटन को अंतिम रूप दे दिया गया है। कंपनी ने एंकर निवेशकों",
    target_lines=4,
    first_indent_pt=10.0,
)
draw_line(566, 2792, 566, 2914, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2784, 1052, 2918,
    text="से रु. ८,११० करोड़ का फंड जुटाया है। बैंकिंग सूत्रों के अनुसार, जियो की एंकर बुक के लिए वैश्विक और घरेलू संस्थागत निवेशकों की ओर से अभूतपूर्व उत्साह देखा गया है और कुल मांग रु. २.५ लाख करोड़ के पार पहुंच गई है।",
    target_lines=5,
    first_indent_pt=0.0,
)

# 3-Col Subhead (Cols 1-3)
place_exact_display_lines(
    88, 2922, 1052, 3044,
    lines=[
        "LIC, ब्लैकरॉक और GIC सबसे बड़े निवेशक; संस्थागत",
        "निवेशकों की ओर से रु. २.५ लाख करोड़ से अधिक की रिकॉर्ड बुकिंग"
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
    text="भारतीय IPO इतिहास में संस्थागत निवेशकों की ओर से इतनी विशाल मांग मिलने की यह पहली घटना है। २१२ इन्वेस्टमेंट लाइन के जरिए ७० से अधिक वैश्विक दिग्गजों का निवेश जियो प्लेटफॉर्म्स की एंकर बुक में विश्व के सबसे बड़े सॉवरेन वेल्थ फंड्स, ग्लोबल एसेट मैनेजर्स, भारतीय म्यूचुअल फंड्स, बीमा कंपनियों और पेंशन फंड्स सहित ७० से अधिक बड़े निवेशकों ने २१२ स्कीम लाइन के जरिए भाग लिया है। लाइफ इंश्योरेंस कॉर्पोरेशन (LIC) रु. ५०० करोड़ के निवेश के साथ सबसे बड़े एकल एंकर निवेशक के रूप में उभरी है।\nब्लैकरॉक (BlackRock), कैपिटल इंटरनेशनल, फिडेलिटी मैनेजमेंट, सिंगापुर का सॉवरेन फंड GIC तथा देश के अग्रणी म्यूचुअल फंड्स जैसे SBI म्यूचुअल फंड, HDFC म्यूचुअल फंड और ICICI प्रूडेंशियल म्यूचुअल फंड को रु. ४२५-४२५ करोड़ के शेयर आवंटित किए गए हैं।\nआदित्य बिरला सन लाइफ MF, कैपिटल वर्ल्ड रु. ३०० करोड़ (प्रत्येक), श्रूडर्स (Schroders) रु. २९३ करोड़, कोटक",
    target_lines=25,
    first_indent_pt=10.0,
)
draw_line(405, 3060, 405, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3054, 720, 3792,
    text="MF, निप्पॉन इंडिया MF, नाइंटी वन रु. २०० करोड़ (प्रत्येक), जेपी मॉर्गन एसेट मैनेजमेंट रु. १८२ करोड़, ADIA, QIA, अलायंस, ड्रैगनियर ने रु. १५० करोड़ (प्रत्येक) का निवेश किया है।\nजियो प्लेटफॉर्म्स की इस एंकर बुक की सबसे बड़ी विशेषता लंबी अवधि का निवेश रखने वाले वैश्विक सॉवरेन फंड्स और पेंशन फंड्स की उपस्थिति है। GIC, अबू धाबी इन्वेस्टमेंट अथॉरिटी (ADIA) और कतर इन्वेस्टमेंट अथॉरिटी (QIA) के अलावा नॉर्वे के ‘नॉर्जेस बैंक इन्वेस्टमेंट मैनेजमेंट’, कैलिफोर्निया स्टेट टीचर्स रिटायरमेंट सिस्टम और फ्लोरिडा रिटायरमेंट सिस्टम जैसे अंतरराष्ट्रीय पेंशन फंड्स ने भी बड़ी रकम लगाई है। इसके अलावा भारत की अग्रणी इंश्योरेंस और पेंशन संस्थाएं जैसे HDFC लाइफ, SBI लाइफ, HDFC पेंशन, SBI पेंशन और ICICI प्रूडेंशियल भी इस आवंटन में शामिल हैं।\nफैमिली ऑफिसेज और ग्लोबल टेक्नोलॉजी स्पेशलिस्ट्स आईटी और ग्रोथ ओरिएंटेड बिजनेस में विशेषज्ञ",
    target_lines=25,
    first_indent_pt=0.0,
)
draw_line(730.5, 3060, 730.5, 3785, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3054, 1050, 3792,
    text="ऐसे ग्लोबल इन्वेस्टर्स जैसे ड्रैगनियर, जेनस हेंडरसन और फिडेलिटी के प्रसिद्ध ‘कॉन्ट्रा फंड’ ने भी जियो में निवेश किया है।\nस्थानीय स्तर पर देश के अग्रणी उद्योगपतियों के फैमिली ऑफिसेज ने भी भारी रुचि दिखाई है, जिनमें प्रेमजी फैमिली (विप्रो), HCL फैमिली, एनाम (Enam) और जेरोधा के रेनमैटर (Rainmatter) शामिल हैं। २१ अक्टूबर से आम जनता के लिए आईपीओ खुलेगा।\nएंकर बुक की अभूतपूर्व प्रतिक्रिया के बाद अब सबकी नजरें २१ अक्टूबर से शुरू हो रहे पब्लिक सब्सक्रिप्शन (Public Subscription) पर टिकी हैं।\nजियो प्लेटफॉर्म्स इस फंड का उपयोग अपने आधुनिक 5G नेटवर्क, क्लाउड कंप्यूटिंग, आर्टिफिशियल इंटेलिजेंस (AI) और एंटरप्राइज डिजिटल सेवाओं के विस्तार के लिए करेगी। प्राइस बैंड की अपर लिमिट पर यह भारतीय पूंजी बाजार के इतिहास का सबसे बड़ा IPO साबित होगा।",
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
    lines=["हिंसक प्रदर्शनों के मामले में २४०० से अधिक गिरफ्तार"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.90,
)
draw_line(1112, 2554, 1688, 2554, swatch="[Black]", weight_pt=1.2)
place_exact_display_lines(
    1080, 2559, 1718, 2698,
    lines=[
        "फ्रांस में हिंसा के बीच शहरों में कर्फ्यू,",
        "इमरजेंसी लगाने के मैक्रों के संकेत"
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
    lines=["(पीटीआई)                                                          पेरिस, ता. १९"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2738, 1718, 2884,
    text="फ्रांस के प्रधानमंत्री सेबेस्टियन लेकोर्नु ने सरकारी क्षेत्रीय प्रतिनिधियों को निर्देश दिए हैं कि वे प्रभावित इलाकों में सीमित और स्थानीय कर्फ्यू लगाएं। यह फैसला वीकएंड में हुई हिंसा के बाद लिया गया है, जिसमें पूरे देश में सिटी हॉल, अन्य सार्वजनिक इमारतों और हजारों व्यवसायों को निशाना बनाया गया था।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=14.0,
)
place_exact_display_lines(
    1080, 2888, 1719, 2988,
    lines=[
        "देश में ६० हजार से अधिक सुरक्षाकर्मी तैनात",
        "यूनियनों का पांच नवंबर को राष्ट्रीय हड़ताल का ऐलान"
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
    text="सरकार के शीर्ष अधिकारियों के साथ बैठक के बाद प्रधानमंत्री ने बताया कि शनिवार को भारी हिंसा और संपत्ति के बड़े नुकसान के बावजूद किसी की भी मौत नहीं हुई है जो एक चमत्कार है।\nउन्होंने हिंसक भीड़ का सामना कर रही पुलिस की कार्रवाई का बचाव भी किया। उन्होंने बताया कि किन इलाकों में कर्फ्यू लगाया जाएगा इसकी घोषणा अब बाद में की जाएगी।\nये निर्देश ऐसे समय आए हैं जब गृह मंत्री लॉरेंट नुनेज़ ने अपना इस्तीफा दे दिया है। हालांकि फ्रांस के राष्ट्रपति ने उनका इस्तीफा स्वीकार करने से इनकार कर दिया है।\nफ्रांस के राष्ट्रपति के कार्यालय ने एक बयान में बताया है कि वर्तमान स्थिति में कानून और व्यवस्था बनाए",
    target_lines=18,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3009, 1399.5, 3797, swatch="[Black]", weight_pt=0.85)

# Col 5 Short Top Body (y=2992..3038, 2 lines) + Jump line above Amul Ad
place_exact_body_column(
    1412, 2992, 1718, 3038,
    text="रखने के लिए गृह मंत्री लॉरेंट नुनेज़ का अपने पद पर बने रहना बेहद जरूरी",
    target_lines=2,
    first_indent_pt=0.0,
    hi_pt=9.6,
)
place_exact_display_lines(
    1460, 3044, 1670, 3067,
    lines=["(शेष पृष्ठ ९ पर)"],
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
    pd_path = target_dir / "Page_01_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_01_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_01_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_01_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_01_Hindi_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_01_Hindi_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_01_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
