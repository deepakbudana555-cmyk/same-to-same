from gs_english_running_header import build_english_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 10 BUILDER FOR INDIAN POST (GUJARAT SAMACHAR ENGLISH)
====================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable English Text ('Georgia' & 'Times New Roman')
  across all Page 10 Business/Market Stories, Forex/Bullion/Stock Tables,
  and 4 Bottom Public Notices (PUBLIC NOTICE)!
- Placed Assets: Loaded in .webp format for fast drawing in Page Designer 1.0.
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
S = 0.375
PAGE_W_PT = round(2800 * S, 2)
PAGE_H_PT = round(3974 * S, 2)

RND_ROOT = Path(__file__).resolve().parent
DIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"
DIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"
ASSETS_DIR = DIR_SMAE / "Page_10_Assets"

LIVE_DRAW = "--fast" not in sys.argv
FRAME_DELAY = 0.06 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.10 if LIVE_DRAW else 0.0
LINE_DELAY = 0.03 if LIVE_DRAW else 0.0

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
        "title": "INDIAN POST (Gujarat Samachar English) — Page 10 (100% Same-to-Same Editable English)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.2)


def resolve_webp_path(base_dir: Path, filename: str) -> str:
    webp_cand = base_dir / (Path(filename).stem + ".webp")
    if webp_cand.exists():
        return str(webp_cand.resolve()).replace("\\", "/")
    return str((base_dir / filename).resolve()).replace("\\", "/")


def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):
    img_path = resolve_webp_path(ASSETS_DIR, filename)
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
    font_family_override: str = None,
    font_style_override: str = None,
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

    if font_family_override:
        use_font_family = font_family_override
        use_font_style = font_style_override or "Regular"
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 18.0:
        use_font_family = "Georgia"
        use_font_style = "Bold"
    else:
        use_font_family = "Times New Roman"
        use_font_style = font_style

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
                "fontFamily": use_font_family,
                "fontStyle": use_font_style,
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
                        "fontFamily": use_font_family,
                        "fontStyle": use_font_style,
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
            "fontFamily": use_font_family,
            "fontStyle": use_font_style,
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
    lo_pt: float = 6.8,
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

    best_cfg = (9.5, default_hscale, 0.0)
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
            lines_now = st.get("lines", 999)
            overset = st.get("overset")
            if overset is None:
                diff = abs(lines_now - target_lines)
                if diff < best_diff:
                    best_diff = diff
                    best_cfg = (pt, hs, 0.0)
                if lines_now == target_lines:
                    break
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
    return fid, sid


def place_mixed_paras_column(
    x1_px: float,
    y1_px: float,
    x2_px: float,
    y2_px: float,
    paras: list,
    target_lines: int,
    base_pt: float = 10.6,
):
    box_h_pt = p(y2_px - y1_px)
    lead_pt = round(box_h_pt / max(1, target_lines), 2)
    full_text = "\n".join(p_item[0] for p_item in paras)
    r = cmd("frame.create", {
        "spread": 0,
        "rect": [p(x1_px), p(y1_px), p(x2_px), round(p(y2_px) + 8.0, 2)],
        "content": "text",
        "text": full_text
    })
    fid, sid = r["id"], r["story"]

    for try_pt10 in range(int(base_pt * 10), 69, -2):
        pt = round(try_pt10 / 10.0, 1)
        if pt > lead_pt * 1.08:
            continue
        for hs100 in (90, 87, 84, 81, 78, 75):
            hs = round(hs100 / 100.0, 2)
            cmds = []
            b_cursor = 0
            for p_text, p_style, p_align, p_indent in paras:
                b_len = utf8_len(p_text)
                b_start = b_cursor
                b_end = b_cursor + b_len
                b_cursor = b_end + 1
                p_sz = round(pt * 1.12, 1) if p_style == "Subhead" else (round(pt * 1.28, 1) if p_style == "Header" else pt)
                f_st = "Bold" if p_style in ("Subhead", "Header", "Bold") else "Regular"
                cmds.append({"command": "text.select", "params": {"story": sid, "anchor": b_start, "focus": b_end}})
                cmds.append({"command": "type.char", "params": {"attrs": {
                    "fontFamily": "Times New Roman",
                    "fontStyle": f_st,
                    "size": p_sz,
                    "leading": {"kind": "points", "value": lead_pt},
                    "fill": "[Black]",
                    "fillTint": 1.0,
                    "hScale": hs,
                    "tracking": 0.0
                }}})
                cmds.append({"command": "type.para", "params": {"attrs": {
                    "align": p_align,
                    "firstLineIndent": p_indent,
                    "spaceBefore": 0.0,
                    "spaceAfter": 0.0,
                    "hyphenate": False
                }}})
            cmds.append({"command": "story.get", "params": {"story": sid}})
            st = batch(cmds)[-1]
            if st.get("overset") is None and st.get("lines", 999) <= target_lines + 1:
                return fid, sid
    return fid, sid


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 10 English Running Header...")
build_english_running_header(10, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: TOP RED-BORDERED BOX (COLS 1-8, y=202..1156)
# ==============================================================================
print("Building Story 1 (Sensex/Nifty Market Crash, Cols 1-8 Top Red Box)...")
draw_box(84, 202, 2715, 1156, stroke_swatch="GsRedBanner", stroke_weight_pt=2.2)
draw_line(736, 206, 736, 1152, weight_pt=0.85)
draw_line(1400, 428, 1400, 976, weight_pt=0.85)
draw_line(2063, 206, 2063, 1152, weight_pt=0.85)
draw_line(736, 980, 2063, 980, weight_pt=0.85)

# Section 1 inside top box (92..724, y=208..1150)
place_mixed_paras_column(
    92, 208, 724, 1150,
    paras=[
        ("(By Our Financial Correspondent)               Mumbai, Monday", "Regular", "leftJustified", 0.0),
        ("Indian equity markets suffered a sharp sell-off on Monday, tracking weak global cues triggered by rising US Treasury bond yields, heightened geopolitical tensions following Ukraine's massive drone offensive on Russia, and a rebound in international crude oil prices. Despite private sector banks reporting better-than-expected quarterly earnings over the weekend, concerns over persistent inflation, elevated lending rates, and potential increases in non-performing assets (NPAs) sparked heavy selling in private banking stocks—even as PSU bank counters staged a selective recovery.", "Regular", "leftJustified", 9.0),
        ("Stock Markets Closed Today (Tuesday) for Dussehra", "Subhead", "center", 0.0),
        ("Selling pressure intensified across Capital Goods, Power, Healthcare, Automobile, IT-Software Services, Technology, Metal-Mining, Consumer Durables, and FMCG stocks. The BSE Sensex plunged 876.37 points to close at 73,852.90, while the NSE Nifty 50 spot index tumbled 257.20 points to settle at 22,888.95. Despite constructive India-US trade deal talks and resilient corporate earnings, liquidity tightening ahead of mega IPO subscriptions weighed heavily on market sentiment. Stock markets will remain closed on Tuesday, October 20, 2026, on account of Dussehra.", "Regular", "leftJustified", 9.0),
        ("Capital Goods Index Drops 734 Pts: Elgi\nEquipments, Suzlon, Thermax, Polycab Slide", "Subhead", "center", 0.0),
        ("Heavy institutional selling hit Capital Goods and Power stocks. Elgi Equipments fell Rs 27.90 to Rs 546.80, Suzlon slipped Rs 1.58 to Rs 40.34, Inox Wind lost Rs 2.54 to Rs 64.89, Thermax dropped Rs 91.15 to Rs 3,234.90, Polycab fell Rs 198 to Rs 8,020, Bharat Dynamics eased Rs 27 to Rs 1,088, Kirloskar Oil Engines declined Rs 48.20 to Rs 1,973.10, Jyoti CNC fell Rs 21.60 to Rs 975.05, Apar Industries shed Rs 317.80 to Rs 15,733.90, Waaree Energies lost Rs 41.90 to Rs 2,513.10, Mazagon Dock slipped Rs 37 to Rs 2,054, and Carborundum Universal fell Rs 21.80 to Rs 1,088.50. The BSE Capital Goods Index tumbled 733.52 points to 72,789.71", "Regular", "leftJustified", 9.0),
    ],
    target_lines=32,
    base_pt=10.6,
)

# Sections 2-3 Headline inside top box (746..2050, y=208..424)
place_exact_display_lines(
    746, 208, 2050, 424,
    lines=[
        "Heavy Sell-Off in Private Bank, IT & Healthcare",
        "Stocks: Sensex Plunges 876 Pts to Close at 73,853"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)

# Section 2 inside top box (746..1388, y=428..974)
place_mixed_paras_column(
    746, 428, 1388, 974,
    paras=[
        ("at the close.", "Regular", "leftJustified", 0.0),
        ("Fresh Selling in IT Stocks: Aurionpro, Aurum,\nGenesys Intl, Izmo, Saregama, Sonata Decline", "Subhead", "center", 0.0),
        ("IT-Software Services and Technology stocks witnessed renewed fund selling after a brief pause. KPIT Technologies fell Rs 18.75 to Rs 536, Sonata Software lost Rs 7.85 to Rs 240.05, ADSL slipped Rs 3.35 to Rs 103.15, Delhivery declined Rs 16.95 to Rs 527.15, eMudhra shed Rs 16.65 to Rs 539.40, and Tata Technologies dropped Rs 18.00 to Rs 705.30. The BSE IT Index fell 419.86 points to close at 29,977.16.", "Regular", "leftJustified", 9.0),
        ("Rising Crude Weighs on Auto Stocks: Bharat Forge,\nExide, Tata Motors, Hyundai Motor Slip", "Subhead", "center", 0.0),
        ("With global crude oil prices firming up—sparking fears of fuel price hikes—and festive vehicle bookings trailing street expectations, funds offloaded Automobile stocks. Bharat Forge dropped Rs 90.55 to Rs 1,791.40, Exide Industries fell Rs 10.50 to Rs 360.35, Tata Motors Passenger Vehicles eased Rs 7.50 to Rs 279.40, Uno Minda slipped Rs 22.70 to Rs 1,087.50,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Section 3 inside top box (1412..2050, y=428..974)
place_mixed_paras_column(
    1412, 428, 2050, 974,
    paras=[
        ("Hyundai Motor declined Rs 27.95 to Rs 1,959.05, Bajaj Auto shed Rs 117 to Rs 10,300, and MRF lost Rs 951.30 to Rs 1,21,856.95. The BSE Auto Index dropped 417.90 points to close at 56,606.57.", "Regular", "leftJustified", 0.0),
        ("Healthcare Index Tumbles 503 Pts: One Global, 3B\nBlackBio, Solara, Fermenta, Themis Medi Fall", "Subhead", "center", 0.0),
        ("Despite indications that India-US trade negotiations are in their final stage, expectations of limited concessions for pharmaceuticals prompted funds to pare Healthcare and Pharma holdings. Solara Active fell Rs 48.85 to Rs 647.45, Fermenta Biotech dropped Rs 28.50 to Rs 459.40, Themis Medicare eased Rs 6.15 to Rs 100.40, and Aarti Pharmalabs lost Rs 41.30 to Rs 833.85. The BSE Healthcare Index slumped 503.33 points to 47,764.66.", "Regular", "leftJustified", 9.0),
        ("Private Banks Slide Despite Strong Q2 Earnings:\nAxis Drops Rs 50; Union Bank & PNB Gain", "Subhead", "center", 0.0),
        ("Even though Axis Bank, ICICI Bank, and HDFC Bank posted healthy quarterly numbers over the weekend, funds booked profits in private banking heavyweights while rotating into PSU banks. Axis Bank tumbled Rs 49.55 to Rs 1,236.90,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Sections 2-3 Bottom Banner inside top box (746..2050, y=986..1150)
place_exact_display_lines(
    746, 986, 2050, 1150,
    lines=[
        "Nifty Drops 257 Pts to 22,889: Investor Wealth Erodes",
        "by Rs 4.69 Lakh Crore; FIIs Net Sell Rs 1,149 Crore"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)

# Section 4 inside top box (2076..2706, y=208..1150)
place_mixed_paras_column(
    2076, 208, 2706, 1150,
    paras=[
        ("HDFC Bank fell Rs 16.50 to Rs 711.60, and ICICI Bank shed Rs 14.80 to Rs 1,382. Conversely, strong earnings momentum lifted PSU banks: Union Bank of India rose Rs 8.50 to Rs 180.50, PNB gained Rs 5.55 to Rs 121.95, Bank of India added Rs 4.85 to Rs 137.10, Bank of Baroda advanced Rs 8 to Rs 238, State Bank of India rose Rs 10.75 to Rs 972.45, and Canara Bank gained Rs 3.40 to Rs 122. The BSE Bankex fell 291.49 points to 62,477.94.", "Regular", "leftJustified", 0.0),
        ("Consumer Durables Under Pressure: Crompton,\nAmber Ent, Dixon, Voltas, Kalyan Jewellers Drop", "Subhead", "center", 0.0),
        ("Consumer Durables counters also witnessed profit booking. Crompton Greaves fell Rs 8.30 to Rs 209.90, Amber Enterprises dropped Rs 164.65 to Rs 6,520.35, Havells India shed Rs 25.45 to Rs 1,098.35, Dixon Technologies tumbled Rs 229 to Rs 12,100, Kalyan Jewellers eased Rs 5.50 to Rs 552, and Titan declined Rs 30 to Rs 4,420. The BSE Consumer Durables Index fell 545.71 points to 59,959.48.", "Regular", "leftJustified", 9.0),
        ("FPIs/FIIs Net Sell Rs 1,149 Crore in Cash;\nDIIs Net Buy Rs 3,201 Crore of Equities", "Subhead", "center", 0.0),
        ("Foreign Portfolio Investors (FPIs/FIIs) were net sellers to the tune of Rs 1,148.64 crore in the cash segment on Monday, buying equities worth Rs 11,240.64 crore against gross sales of Rs 12,389.28 crore. Domestic Institutional Investors (DIIs) recorded net purchases of Rs 3,201.19 crore, buying Rs 14,781.31 crore and selling Rs 11,580.12 crore.", "Regular", "leftJustified", 9.0),
        ("BSE Market Capitalization Shrinks by Rs 4.69\nLakh Crore to Rs 467.93 Lakh Crore", "Subhead", "center", 0.0),
        ("Broad-based selling across equities eroded investor wealth—measured by the total market capitalization of BSE-listed companies—by Rs 4.69 lakh crore in a single session to Rs 467.93 lakh crore.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=32,
    base_pt=10.6,
)

# ==============================================================================
# 3. VERTICAL & HORIZONTAL GRID DIVIDERS FOR MIDDLE STORIES
# ==============================================================================
draw_line(1064, 1164, 1064, 2960, weight_pt=0.85)  # Between Col 3 and Col 4
draw_line(1731, 1164, 1731, 3030, weight_pt=0.85)  # Between Col 5 and Col 6
draw_line(82, 1904, 1051, 1904, weight_pt=0.85)    # Under FMCG story
draw_line(82, 2562, 720, 2562, weight_pt=0.85)     # Under Gold story (Cols 1-2)
draw_line(1744, 1868, 2712, 1868, weight_pt=0.85)  # Under Garment story (Cols 6-8)

# ==============================================================================
# 4. STORY 2 (COLS 1-3, y=1168..1898): FMCG COMPANIES FACE MARGIN PRESSURE
# ==============================================================================
print("Building Story 2 (FMCG Margins, Cols 1-3)...")
place_exact_display_lines(
    82, 1168, 1051, 1342,
    lines=[
        "FMCG Companies Face Margin Pressure:",
        "Price Hikes Likely After Diwali"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 1348, 556, 1412,
    text="Mumbai, Oct 19\nRising raw material prices have squeezed profitability across",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    576, 1348, 1051, 1412,
    text="India's fast-moving consumer goods (FMCG) sector over the first six months of the current fiscal year.",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1416, 1051, 1462,
    lines=["Higher Input Costs Drive Up Manufacturing Expenses Across the Sector"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1468, 388, 1898,
    text=(
        "Despite mounting margin pressure, consumer goods makers are holding back on immediate price increases so as not to dampen festive Diwali demand—and are expected to hike product prices after Diwali if input costs do not cool.\n"
        "After moderating in the June quarter, raw material costs rebounded sharply during the September quarter, compressing operating margins. Even so, FMCG companies have deferred price hikes to protect volume growth during the peak festive season, according to an"
    ),
    target_lines=15,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 1468, 720, 1898,
    text=(
        "industry analyst.\n"
        "Key inputs used in FMCG manufacturing—including crude oil derivatives, packaging materials, sugar, and edible oils—have all registered sharp price increases in recent weeks. Analysts warn that elevated input costs could weigh on the September-quarter earnings of major FMCG companies.\n"
        "Persistent food and commodity inflation remains a primary concern for the sector.\n"
        "Rather than raising retail sticker prices immediately,"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 1468, 1051, 1898,
    text=(
        "companies are focusing on operational efficiencies and cost-cutting measures to absorb part of the raw material shock, the analyst added.\n"
        "Agricultural commodity prices are projected to firm up further after Diwali, which could compel makers of packaged and ready-to-eat food products to pass on higher costs to consumers. El Nino-induced monsoon unevenness this year has also impacted domestic farm output."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. STORY 3 (COLS 1-3, y=1910..2960): TWO-WAY SWINGS IN GOLD AHEAD OF DUSSEHRA
# ==============================================================================
print("Building Story 3 (Gold/Crude/Platinum, Cols 1-3)...")
place_exact_display_lines(
    82, 1910, 1051, 2082,
    lines=[
        "Two-Way Swings in Gold Ahead of Dussehra;",
        "Crude Retreats From Highs, Platinum Gains"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 2088, 556, 2166,
    text="(By Our Commercial Correspondent) Mumbai, Monday\nGold and silver prices in the Mumbai bullion market opened higher on Monday before paring gains at the close. Excluding GST, standard gold",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    576, 2088, 1051, 2166,
    text="(995) opened at Rs 1,45,820 against Rs 1,45,500 and closed at Rs 1,45,360, while pure gold (999) opened at Rs 1,46,404 against Rs 1,46,100 and settled at Rs 1,45,944.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 2172, 1051, 2218,
    lines=["Global Spot Gold Climbs Near $4,200 an Ounce in Intraday Trade"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 2224, 388, 2556,
    text=(
        "In Mumbai, silver (excluding GST) closed at Rs 2,08,750 per kg against its previous close of Rs 2,09,500. Including 3% GST, retail bullion prices traded correspondingly higher. Meanwhile, platinum per 10 grams opened higher at Rs 59,880 against Rs 58,482 before closing at Rs 57,026.\n"
        "In the Ahmedabad bullion market,"
    ),
    target_lines=11,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2224, 720, 2556,
    text=(
        "gold rose Rs 300 per 10 grams on Monday, with 995 quoted at Rs 1,50,700 and 999 at Rs 1,51,000, while silver ruled steady at Rs 2,13,000 per kg. In international markets, spot gold rose from $4,165–4,166 per ounce to an intraday high of $4,190–4,191 before trading at $4,175–4,176. Tracking gold, global silver climbed from $56.99 per ounce to a high of $57.85"
    ),
    target_lines=11,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 2224, 1051, 2958,
    text=(
        "before settling at $57.74–57.75. Platinum advanced from $1,635 to $1,659 before trading at $1,650–1,651 an ounce, while palladium rose from $1,116 to $1,140 and settled at $1,138. Global copper edged up 0.27%. Meanwhile, international crude oil prices retreated from their recent highs.\n"
        "Brent crude, which had recently touched $110 per barrel, dipped to an intraday low of $106.82 before trading at $108.62 on Monday, while US WTI crude slipped to $99.24 before recovering to $101.33 amid subdued fresh buying. Meanwhile, India's crude oil import bill rose 14% year-on-year in September to $15.40 billion, compared with $10.50 billion in September last year.\n"
        "In volume terms, India's September crude oil imports increased 7% while the total import value rose 14%."
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. STORY 4 (COLS 1-2, y=2568..2958): PAKISTAN'S GDP GROWTH SLOWS TO 2% IN JUNE QUARTER
# ==============================================================================
print("Building Story 4 (Pakistan GDP Growth, Cols 1-2 Mid-Bot)...")
place_exact_display_lines(
    82, 2568, 720, 2684,
    lines=[
        "Pakistan's GDP Growth Slows",
        "to 2% in the June Quarter"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 2690, 388, 2958,
    text=(
        "Mumbai, Oct 19\n"
        "While global rating agencies are upgrading India's economic growth projections for the current fiscal year, official data indicates that Pakistan's economic recovery is losing steam.\n"
        "For the June quarter of 2026, Pakistan's GDP growth came in below expectations"
    ),
    target_lines=9,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2690, 720, 2958,
    text=(
        "at just 2.0%, compared with India's stronger-than-expected GDP expansion of 7.80% during the same period. Economists had projected Pakistan's June-quarter GDP growth at 3.50%.\n"
        "Trade disruptions stemming from Middle East instability weighed heavily on Pakistan's external sector, local sources noted."
    ),
    target_lines=9,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. STORY 5 (COLS 4-5, y=1168..3030): RUPEE RECOVERS + FOREX RATES + CASH FUTURES OPTIONS + BULLION MARKET
# ==============================================================================
print("Building Story 5 (Rupee/Euro, Forex Table, Cash Future Option & Gold-Silver Market, Cols 4-5)...")
place_exact_display_lines(
    1078, 1168, 1718, 1310,
    lines=[
        "Rupee Recovers as Euro Slides",
        "Sharply Amid European Unrest"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1078, 1316, 1718, 1458,
    text=(
        "(By Our Commercial Correspondent) Mumbai, Monday\n"
        "The Indian rupee firmed up against the US dollar in the Mumbai interbank forex market on Monday. Having touched Rs 85.06 in offshore trade over the weekend, the dollar opened at Rs 84.99, dipped to an intraday low of Rs 84.75, and closed at Rs 84.92."
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1078, 1464, 1718, 1568,
    lines=[
        "Dollar Index Climbs Past 102 Globally; India's",
        "Forex Reserves Sufficient for 6 Months of Imports"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# FOREX RATES Box in Col 4 (1078..1385, y=1575..1818)
draw_box(1078, 1575, 1385, 1818, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
draw_box(1078, 1575, 1385, 1624, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=0.5)
place_exact_display_lines(
    1086, 1580, 1377, 1620,
    lines=["FOREX RATES"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    1086, 1630, 1210, 1812,
    lines=["US Dollar", "UK Pound", "Euro", "Yen", "Brent Crude"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    1215, 1630, 1378, 1812,
    lines=["Rs 84.92", "Rs 126.51", "Rs 106.40", "Rs 0.60", "$108/bbl"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)

place_exact_body_column(
    1078, 1824, 1385, 2396,
    text=(
        "In overseas currency markets, the US dollar strengthened against major European peers as violent youth protests across several European cities weighed heavily on the euro. The global US Dollar Index rose from an intraday low of 101.77 to a high of 102.08 before trading around 101.93.\n"
        "Traders also awaited upcoming Chinese GDP data, while Indonesia's rupiah slipped to a three-month low near 19,000 per dollar. In Mumbai, the euro dropped 46 paise against the rupee, touching a low of Rs 106.21 before closing at Rs 106.40."
    ),
    target_lines=20,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1575, 1718, 2396,
    text=(
        "The British pound eased 9 paise to close at Rs 126.51 after touching Rs 126.26 intraday. The Japanese yen slipped 0.17% against the rupee, while the Chinese yuan edged up 0.05%. While domestic equity losses weighed on sentiment, the pullback in global crude oil prices supported the rupee.\n"
        "Following the recent dip in India's foreign exchange reserves, currency dealers closely tracked the Reserve Bank of India's market intervention. Regulatory measures initiated by the RBI to curb speculative forward positions helped stabilize intraday volatility.\n"
        "India's current forex reserves remain sufficient to cover approximately 6 months and 20 days of imports. Although the rupee recovered slightly on Monday, currency analysts caution that persistent global headwinds could push the dollar higher over the medium term."
    ),
    target_lines=28,
    first_indent_pt=9.0,
)

# CASH FUTURES OPTIONS Box in Col 4 (1078..1385, y=2410..2958) & Col 5 Top-Bot (1412..1718, y=2410..2639)
draw_box(1078, 2410, 1385, 2488, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1086, 2418, 1377, 2480,
    lines=["CASH FUTURES OPTIONS"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1078, 2494, 1385, 2958,
    paras=[
        ("Futures Market", "Subhead", "center", 0.0),
        ("- Union Bank of India (181): Buy October Futures above Rs 181 with a stop-loss at Rs 174 for short-term upside targets of Rs 186 (Target-1) and Rs 188 (Target-2).", "Regular", "leftJustified", 9.0),
        ("- Aurobindo Pharma (1618): Sell October Futures below Rs 1,618 with a stop-loss at Rs 1,640 for downside targets of Rs 1,590 (Target-1) and Rs 1,560 (Target-2).", "Regular", "leftJustified", 9.0),
        ("Cash Market", "Subhead", "center", 0.0),
        ("- Gabriel India (1486): Buy above Rs 1,486 with a stop-loss at Rs 1,445 for upside Target-1", "Regular", "leftJustified", 9.0),
    ],
    target_lines=16,
    base_pt=9.6,
)
place_mixed_paras_column(
    1412, 2410, 1718, 2639,
    paras=[
        ("of Rs 1,500 and Target-2 of Rs 1,530 in the coming sessions.", "Regular", "leftJustified", 0.0),
        ("- Neuland Laboratories (19220): Sell below Rs 19,220 with a stop-loss at Rs 19,350 for downside targets of Rs 19,000 (Target-1) and Rs 18,400 (Target-2).", "Regular", "leftJustified", 9.0),
        ("- Nilesh Kotak", "Bold", "right", 0.0),
    ],
    target_lines=8,
    base_pt=9.6,
)
draw_line(1412, 2642, 1718, 2642, weight_pt=0.85)

# BULLION MARKET Box in Col 5 (1412..1718, y=2655..3025)
draw_box(1412, 2655, 1718, 2732, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1420, 2663, 1710, 2724,
    lines=["BULLION MARKET"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1412, 2738, 1558, 3025,
    paras=[
        ("Ahmedabad", "Subhead", "center", 0.0),
        ("Silver Bar 210000-213000\nSilver Fine 209800-212800\nOld Coin 2400-2700\nGold (99.9) 149000-151000\nGold (99.5) 148700-150700\nHallmark 147980", "Regular", "left", 0.0),
        ("Mumbai", "Subhead", "center", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)
place_mixed_paras_column(
    1566, 2738, 1718, 3025,
    paras=[
        ("Silver 208750\nGold (99.5) 145360\nGold (99.9) 145944", "Regular", "left", 0.0),
        ("Rajkot", "Subhead", "center", 0.0),
        ("Silver 212000\n24 Carat 10g 152500\nCoin (1g) 15300\n22 Carat 10g 139500", "Regular", "left", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)

# ==============================================================================
# 8. STORY 6 (COLS 6-8, y=1168..1862): US GARMENT ORDERS FOR CHRISTMAS & NEW YEAR DECLINE
# ==============================================================================
print("Building Story 6 (US/EU Garment Orders, Cols 6-8)...")
place_exact_display_lines(
    1744, 1168, 2712, 1342,
    lines=[
        "US Garment Orders for Christmas",
        "and New Year Decline Sharply"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1744, 1348, 2218, 1438,
    text="Mumbai, Oct 19\nExport orders placed by US buyers with Indian readymade garment manufacturers for the upcoming",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 1348, 2712, 1438,
    text="Christmas and New Year holiday season have declined, though steady demand from the UK and Europe has provided welcome relief to the apparel sector.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1444, 2712, 1492,
    lines=["Healthy Demand From UK and European Buyers Cushions Indian Exporters"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1498, 2050, 1862,
    text=(
        "Amid geopolitical uncertainty and persistent inflation in the United States, American retail chains have adopted a cautious inventory strategy.\n"
        "Due to softness in the US market, the first six months of the current fiscal year remained subdued in dollar terms for Indian apparel exporters, sources in the Apparel Export Promotion Council (AEPC) said.\n"
        "Readymade garment exports stood at $1.10 billion in September,"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 1498, 2382, 1862,
    text=(
        "marking a 13.70% year-on-year increase for the month; however, cumulative exports during April–September declined 6.20% to $7.20 billion compared with $7.70 billion in the year-ago period, sources added.\n"
        "In rupee terms, September apparel exports rose 22.90% year-on-year to Rs 10,824.60 crore, while April–September garment exports grew 3.40% to Rs 69,300 crore."
    ),
    target_lines=12,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1498, 2712, 1862,
    text=(
        "Exporters in Tirupur report a 25% to 30% drop in Christmas and New Year garment orders from the United States.\n"
        "However, order bookings from the UK and European Union remain satisfactory, and exporters have shipped consignments ahead of schedule to bypass maritime shipping delays caused by geopolitical tensions."
    ),
    target_lines=12,
    first_indent_pt=9.0,
)

# ==============================================================================
# 9. STORY 7 (COLS 6-8, y=1874..3255): MIXED TREND IN EDIBLE OILS + MARKET TABLES
# ==============================================================================
print("Building Story 7 (Edible Oil Market & Market/Stock Tables, Cols 6-8)...")
place_exact_display_lines(
    1744, 1874, 2712, 2050,
    lines=[
        "Mixed Trend in Edible Oils: Festive Demand Rises",
        "Ahead of Dussehra; Castor Oil & Seed Extend Rally"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1744, 2056, 2050, 2556,
    text=(
        "(By Our Commercial Correspondent)\n"
        "Mumbai, Monday\n"
        "Domestic and imported cooking oils traded within a narrow two-way range in the Mumbai oilseeds market on Monday, while castor oil and spot castor seed extended their record rally. Seasonal festive demand ahead of Dussehra supported spot sentiment. In overseas markets, Malaysian palm oil futures eased 22 points for November and 10 points for December delivery as global crude oil prices retreated from recent highs. In Mumbai spot trade, castor oil jumped Rs 18 per 10"
    ),
    target_lines=17,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 2056, 2382, 2155,
    text=(
        "kg, lifting spot castor seed from Rs 8,420 to Rs 8,515 per quintal. In Saurashtra,"
    ),
    target_lines=3,
    first_indent_pt=0.0,
)

# Palm Oil Futures Soften Red Callout Box in Col 7 (2076..2382, y=2161..2270)
draw_box(2076, 2161, 2382, 2270, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    2086, 2168, 2372, 2262,
    lines=[
        "Softness Persists in",
        "Palm Oil Futures"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)

place_exact_body_column(
    2076, 2276, 2382, 2442,
    text=(
        "groundnut oil was quoted at Rs 1,775–1,800 and cottonseed washed oil at Rs 1,510–1,515.\n"
        "Groundnut prices in Saurashtra ruled at Rs 1,400–1,700 per 20 kg"
    ),
    target_lines=5,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2056, 2712, 2442,
    text=(
        "depending on variety. In the Mumbai spot market, 10 kg groundnut oil stood at Rs 1,830 and cottonseed oil at Rs 1,595, while imported palm oil was quoted at Rs 1,445, soyabean oil at Rs 1,470, crude sunflower oil at Rs 1,585, and refined sunflower oil at Rs 1,680. Late evening quotes in Saurashtra placed groundnut oil at Rs 1,775–1,800, cotton wash at Rs 1,515, and palm oil at Rs 1,402."
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# RAJKOT CLOSING RATES & CHIMANBHAI MARKET in Col 6 (1744..2050, y=2562..3025)
draw_line(1744, 2562, 2050, 2562, weight_pt=0.85)
draw_box(1744, 2580, 2050, 2656, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2588, 2042, 2648,
    lines=["RAJKOT CLOSING RATES"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1744, 2662, 2050, 2786,
    text=(
        "Groundnut Oil Loose 1800\n"
        "Rajkot Groundnut 1780-1790\n"
        "Gold 24 Carat 152500\n"
        "Silver (1 Kg) 212000"
    ),
    target_lines=4,
    align="left",
    first_indent_pt=0.0,
)
draw_box(1744, 2795, 2050, 2869, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2803, 2042, 2861,
    lines=["CHIMANBHAI MARKET"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1744, 2875, 2050, 3025,
    paras=[
        ("Per 20 Kg", "Subhead", "center", 0.0),
        ("Potato Desi 100-200\nPotato Deesa 240-320\nOnion Maharashtra 700-1040\nOnion MP 700-840", "Regular", "left", 0.0),
    ],
    target_lines=5,
    base_pt=9.6,
)

# AHMEDABAD MARKETS in Col 7 (2076..2382, y=2448..2796)
draw_line(2076, 2448, 2712, 2448, weight_pt=0.85)
draw_box(2076, 2464, 2382, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2472, 2374, 2531,
    lines=["AHMEDABAD MARKETS"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    2076, 2545, 2224, 2796,
    paras=[
        ("Oils & Oilseeds", "Subhead", "left", 0.0),
        ("Groundnut New Tin (15kg) 2950-3150\nGroundnut New Tin (15L) 2950\nCottonseed New Tin (15kg) 2580-2780\nRice Bran (15kg) 2550\nSoyabean New Tin 2600", "Regular", "left", 0.0),
    ],
    target_lines=12,
    base_pt=8.4,
)
place_exact_body_column(
    2232, 2545, 2382, 2796,
    text=(
        "Castor Oil 2400\n"
        "Palmolein Old Tin 2330\n"
        "Palmolein New Tin 2450\n"
        "Coconut Oil 4400\n"
        "Vanaspati 2000-2300\n"
        "Sweet Mustard 2900\n"
        "Pungent Mustard 3050\n"
        "Sunflower 2650\n"
        "Corn Oil 2450"
    ),
    target_lines=11,
    align="left",
    first_indent_pt=0.0,
)

# CLOSING RATES in Col 8 (2408..2712, y=2464..2796)
draw_box(2408, 2464, 2712, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2472, 2704, 2531,
    lines=["CLOSING RATES"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2408, 2545, 2712, 2796,
    text=(
        "Mumbai Silver 208750\n"
        "Mumbai Gold (99.5) 145360\n"
        "Mumbai Gold (99.9) 145944\n"
        "Ahd. Silver 213000\n"
        "Ahd. Gold (99.9) 151000\n"
        "Ahd. Gold (99.5) 150700\n"
        "Ahd. Groundnut Oil 3150\n"
        "Ahd. Cottonseed Oil 2780"
    ),
    target_lines=8,
    align="left",
    first_indent_pt=0.0,
)

# NSE TOP LOSERS (Col 7, 2076..2382, y=2805..3255) & BSE TOP LOSERS (Col 8, 2408..2712, y=2805..3255)
draw_box(2076, 2805, 2382, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2813, 2374, 2872,
    lines=["NSE TOP LOSERS"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2076, 2886, 2195, 2916, lines=["Company"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2196, 2886, 2305, 2916, lines=["Close"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2306, 2886, 2382, 2944, lines=["Fall", "(in %)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2076, 2948, 2382, 2948, weight_pt=0.75)
place_exact_display_lines(
    2076, 2954, 2210, 3254,
    lines=[
        "Axis Bank",
        "Tata Motors PV",
        "Infosys",
        "Bajaj Finance",
        "Apollo Hosp.",
        "UltraTech",
        "HDFC Bank",
        "Trent",
        "Hind. Unilever",
        "NTPC",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2212, 2954, 2318, 3254,
    lines=[
        "1236.00",
        "278.00",
        "1130.70",
        "957.35",
        "7700.00",
        "10650.00",
        "712.00",
        "2891.60",
        "1853.20",
        "309.00",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2322, 2954, 2382, 3254,
    lines=[
        "4.19",
        "3.09",
        "2.63",
        "2.52",
        "2.41",
        "2.36",
        "2.31",
        "2.27",
        "2.14",
        "1.95",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

draw_box(2408, 2805, 2712, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2813, 2704, 2872,
    lines=["BSE TOP LOSERS"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2408, 2886, 2525, 2916, lines=["Company"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2526, 2886, 2635, 2916, lines=["Close"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2636, 2886, 2712, 2944, lines=["Fall", "(in %)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2408, 2948, 2712, 2948, weight_pt=0.75)
place_exact_display_lines(
    2408, 2954, 2542, 3254,
    lines=[
        "Axis Bank",
        "UltraTech",
        "Infosys",
        "Bajaj Finance",
        "Trent",
        "NTPC",
        "HDFC Bank",
        "Hind. Unilever",
        "Bajaj Finserv",
        "Bharti Airtel",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2544, 2954, 2650, 3254,
    lines=[
        "1236.90",
        "10620.10",
        "1130.00",
        "957.00",
        "2886.00",
        "309.00",
        "711.60",
        "1856.95",
        "1702.75",
        "1872.75",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2654, 2954, 2712, 3254,
    lines=[
        "3.85",
        "2.82",
        "2.72",
        "2.54",
        "2.43",
        "2.37",
        "2.27",
        "2.16",
        "1.97",
        "1.69",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

# ==============================================================================
# 10. BOTTOM PUBLIC NOTICES (PUBLIC NOTICE) — 100% EDITABLE ENGLISH TEXT & CMYK BAR
# ==============================================================================
print("Building Page 10 Bottom Public Notices (100% Editable English Text)...")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=52):
    x_mid = (x1_px + x2_px) // 2
    draw_box(x1_px, y1_px, x2_px, y2_px, stroke_swatch="[Black]", stroke_weight_pt=1.8)
    draw_box(x1_px, y1_px, x_mid - 4, y1_px + header_h, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
    place_exact_display_lines(
        x1_px + 10, y1_px + 6, x_mid - 14, y1_px + header_h - 4,
        lines=["PUBLIC NOTICE"],
        font_style="Bold",
        fill_swatch="[Paper]",
        align="center",
        stretch_lines=False,
    )
    draw_line(x_mid, y1_px + 10, x_mid, y2_px - 10, weight_pt=0.75)
    place_exact_body_column(
        x1_px + 10, y1_px + header_h + 6, x_mid - 8, y2_px - 8,
        text=left_text,
        target_lines=left_lines,
        first_indent_pt=0.0,
        hi_pt=10.2,
        lo_pt=6.8,
    )
    place_exact_body_column(
        x_mid + 8, y1_px + 10, x2_px - 10, y2_px - 8,
        text=right_text,
        target_lines=right_lines,
        first_indent_pt=0.0,
        hi_pt=10.2,
        lo_pt=6.8,
    )


# 1. Cols 1-2 Bottom Notice (82..718, 2970..3790)
place_public_notice_2col(
    82, 2970, 718, 3790,
    left_text=(
        "Mouje Shivpura\n"
        "Agricultural land bearing Block/Survey No. 104 (Old Survey No. 78) under Khata No. 341 admeasuring 1-08-25 Hec-Are-Sq.Mtrs. (10825 sq.mtrs.) of Mouje Village Shivpura, Taluka Viramgam, District Ahmedabad, is stated by (1) Bhagwanbhai Hansrajbhai, (2) Jagjivanbhai Hansrajbhai, (3) Meenaben W/o Bhavanbhai, (4) Kinnariben D/o Bhavanbhai & W/o Amitkumar, (5) Jigneshkumar Bhavanbhai Patel, and (6) Anandkumar Jagjivanbhai Patel to be in their joint ownership, direct possession and enjoyment free from all legal disputes and encumbrances, and they have requested a Title Clearance Opinion from us. Any person having any right, share, tenancy right, encumbrance, right of way, banakhat right,"
    ),
    right_text=(
        "charge, easement right, claim or dispute over the said land or any part thereof must notify us in writing with certified copies of documentary proof by Speed Post / Regd. A.D. within 15 (fifteen) days from publication hereof at the address below; failing which it shall be deemed that no other person has any right, share, encumbrance or claim over the said land, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Opinion Certificate, after which no objection shall be entertained.\n"
        "Ahmedabad | Date: 20/10/2026\n"
        "Jaimin Rohitbhai Patel, Advocate\n"
        "3135, 3rd Floor, T.R.P. Mall, East Court, Bopal, Ahmedabad-380058.\n"
        "Mob. No. 99789 32199"
    ),
    left_lines=24,
    right_lines=26,
)

# 2. Cols 3-4 Bottom Notice (746..1385, 2970..3790)
place_public_notice_2col(
    746, 2970, 1385, 3790,
    left_text=(
        "Mouje: Vavol\n"
        "Notice is hereby given to the general public that old tenure agricultural land bearing Block/Survey No. 758/004 (Old Survey No. 191) under Khata No. 1300 admeasuring Hec-Are-Sq.Mtrs. 0-59-45 (Assessment Rs. 6.08) of Mouje Village Vavol, Taluka & Sub-District Kalol, Registration District Gandhinagar, is stated by Utpalbhai Jagdishbhai Amin (residing at A/501, Samast Apartment, B/h Arpan Manav Mandal, Vastrapur, Ahmedabad-380015) to be in his independent ownership, possession and enjoyment free from all encumbrances, and he has agreed to sell the same to our client subject to N.A. conversion and requested a Title Clearance Certificate from us. Any person having any right, share, claim, banakhat, easement, guarantee,"
    ),
    right_text=(
        "maintenance right or encumbrance of any person, bank, firm or institution over the said property must notify us in writing with certified copies of all documentary proof by Regd. A.D. within 7 (seven) days from publication hereof at the address below; failing which it shall be deemed that no person has any right, encumbrance, share or claim over the said property, or if any existed, the same stands voluntarily waived, and upon expiry of the period the Title Clearance Certificate shall be issued to our client.\n"
        "Date: 19/10/2026\n"
        "Hemraj R. Desai (Advocate)\n"
        "(83472 63253)\n"
        "FF-8, Center Plaza, Sarthak Char Rasta, Sola Road, Ghatlodia, Ahmedabad-380061"
    ),
    left_lines=24,
    right_lines=26,
)

# 3. Cols 5-6 Bottom Notice (1412..2050, 3036..3790)
place_public_notice_2col(
    1412, 3036, 2050, 3790,
    left_text=(
        "Old tenure agricultural land bearing Revenue Survey No. 1318 (Old Block/Survey No. 477/Paiki) admeasuring Hec-Are-Sq.Mtrs. 1-06-73 (Assessment Rs. 2.04) and Revenue Survey No. 1317 (Old Block/Survey No. 477) admeasuring Hec-Are-Sq.Mtrs. 0-01-24 (Assessment Re. 0.06), aggregating Hec-Are-Sq.Mtrs. 1-07-97 under Khata No. 168 of Mouje Village Zanu, Taluka Daskroi, Sub-District Ahmedabad-14 (Vastral), is registered in the joint ownership, possession and enjoyment of (1) Kantibhai Muljibhai and (2) Parshottambhai alias Priteshbhai Muljibhai free from all encumbrances, and they have agreed to sell the same to our client, who has requested a Title Clear and Marketable"
    ),
    right_text=(
        "Opinion Certificate from us. Any person having any banakhat, sale, gift, power of attorney, inheritance, mortgage, possession right or court stay order over the said land must notify us in writing with documentary proof by Regd. Post within 15 (fifteen) days from publication hereof at the address below (objections without legally valid proof shall be filed without consideration). Upon expiry of the period, the Title Clearance Certificate shall be issued without regard to any subsequent claim.\n"
        "19 OCT 2026 | Nileshkumar B. Patel\n"
        "(Advocate & Notary)\n"
        "Office: A/1 (Ground Floor), Murtidham Park, Nr. Raspan Char Rasta, Nikol, Ahmedabad-382350. Mob.: 7874374466"
    ),
    left_lines=22,
    right_lines=24,
)

# 4. Cols 7-8 Bottom Notice (2076..2712, 3266..3790)
place_public_notice_2col(
    2076, 3266, 2712, 3790,
    left_text=(
        "Out of old tenure agricultural land bearing Block/Survey No. 321 admeasuring 18211 sq.mtrs. (including 708 sq.mtrs. kharaba) of Mouje Village Saroda, Taluka & Sub-District Dholka, Registration District Ahmedabad, an undivided share admeasuring 5945 sq.mtrs. is stated by Shankarbhai Bhimabhai Makwana to be in his independent ownership and direct possession and he has agreed to sell the same to our client, who has requested a Title Clearance Certificate from us. Therefore,"
    ),
    right_text=(
        "all persons having any right, interest, share, encumbrance or banakhat right over the said land must notify us in writing with documentary proof within 7 (seven) days from publication hereof at the address below; failing which the Title Clearance Certificate for the said land shall be issued.\n"
        "Ahmedabad | Date: 20-10-2026\n"
        "Amit V. Patel, Advocate\n"
        "93, Nalanda Complex, Vastrapur, Ahmedabad-380015.\n"
        "Mob. : 9510188505."
    ),
    left_lines=16,
    right_lines=18,
)

place_png(0, 3796, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_10_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_10_English_SameToSame.dns"
    png_path = target_dir / "Page_10_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_10_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_10_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_10_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_10_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
