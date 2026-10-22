# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 2 BUILDER ('INDIAN POST' — English Gujarat Samachar Edition)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- Running Header: 'INDIAN POST' in 'Indian Post Mast' (Gujarat Samachar Calligraphic Shaily)
- All placed photos/graphics use .webp ('image/webp') for rapid drawing in Page Designer 1.0.
- 100% Editable English Text ('Georgia' & 'Times New Roman' Bold/Regular).
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
from gs_english_running_header import build_english_running_header

sys.stdout.reconfigure(encoding="utf-8")

PORT = 47123
S = 0.375
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


LIVE_DRAW = "--fast" not in sys.argv
FRAME_DELAY = 0.14 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.26 if LIVE_DRAW else 0.0
LINE_DELAY = 0.08 if LIVE_DRAW else 0.0

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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 02 (100% Same-to-Same Editable English)"
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
    extra_h = 28.0 if custom_font_family else 12.0
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
    cap_pt = 92.0

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
            max_hs_int = int(min(1.08, best_hs + 0.22) * 100)
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
    lo_pt: float = 7.4,
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
# 1. TOP RUNNING HEADER BAR & MAJOR VERTICAL COLUMN DIVIDERS
# ==============================================================================
print("Placing Page 2 English running header & main vertical rules...")
build_english_running_header(2, place_png, draw_box, place_exact_display_lines)
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
        "Sold at Rs 450-500 a Kg a Decade Ago, Jalebi",
        "Now Commands Rs 1,150 to Rs 1,500 Per Kg"
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
    text="No Vijayadashami celebration in Gujarat feels complete without a traditional feast of hot Fafda and Jalebi. With Dussehra tomorrow, Ahmedabad alone is set to witness Fafda-Jalebi sales worth Rs 150 crore to Rs 200 crore. Across the city, Fafda is selling at Rs 750 to Rs 850 per kg while Jalebi ranges from Rs 1,150 to Rs 1,500 per kg—with premium Kesar Jalebi touching Rs 1,500 a kg, or nearly Rs 30 for a single piece! Back in 2016, Fafda sold for Rs 360–450 per kg and Jalebi for Rs 450–500 per kg, marking a 167% to 233% surge in Fafda prices and a 264% to 344% jump in Jalebi prices over ten years. Most housing societies have already finalized Fafda-Jalebi breakfast menus and pre-booked delivery slots, while several Garba venues have rented out snack counters to cash in on the festive rush.                                  (Photo: Suresh Mistry)",
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
    lines=["Vastrapur Ganthiya Sealed; 24 Food Samples Collected from 15 Outlets"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(86, 1451, 1054, 1451, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 1456, 1052, 1640,
    lines=[
        "Hazardous Reused Frying Oil Found",
        "Even in Rs 800/Kg Fafda and Jalebi"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    370, 1644, 554, 1670,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 1672, 554, 1796,
    text="Citizens in Ahmedabad consume thousands of kilograms of Fafda and Jalebi on Dussehra. Exploiting this massive festive demand, unscrupulous vendors blatantly compromise public health. Acting on complaints, the AMC Food",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 1650, 568, 1794, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 1646, 1052, 1796,
    text="Department collected 24 samples of Fafda and Jalebi from 15 outlets across the city today for laboratory testing—though the stocks will long be consumed before test reports arrive! Meanwhile, 'Vastrapur Ganthiya' opposite Vastrapur Lake was sealed after its frying oil showed dangerously high TPC levels.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 1802, 1052, 1918,
    lines=[
        "Thousands of Kilos Fried Across City Lanes,",
        "Yet AMC Issues Notices to Merely 10 Units!"
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
    text="The Ahmedabad Municipal Corporation's Food Department conducted an inspection drive targeting Fafda-Jalebi",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(404, 1926, 404, 2008, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 1922, 718, 2010,
    text="notices to 10 units and recovered Rs 40,000 in fines. At Vastrapur Ganthiya in Sailabh Complex opposite",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(730.5, 1926, 730.5, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 1922, 1052, 2010,
    text="Notably, Fafda and Jalebi are sold here at Rs 800 per kg. Despite charging customers premium prices, the",
    target_lines=3,
    first_indent_pt=0.0,
)

# 2-Col Callout Box (x=86..724, y=2017..2401) + Col 3 Oil Meter Photo
draw_box(86, 2017, 724, 2401, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    98, 2024, 712, 2108,
    lines=[
        "Rampant Profiteering: Production Cost of Fafda",
        "Is Just Rs 175/Kg and Jalebi Merely Rs 225/Kg!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    98, 2112, 712, 2394,
    text="Beyond health hazards, rampant profiteering is underway across Ahmedabad in the name of festive Fafda-Jalebi sales. According to farsan trade insiders, factoring in gram flour (besan), edible oil, spices and commercial LPG, the actual production cost of one kilogram of Fafda barely touches Rs 175. Even today, pure farsan sells across the city for Rs 250 a kg—yet most shops charge Rs 700 to Rs 800 per kg for Fafda! Similarly, the production cost of Jalebi does not exceed Rs 225 per kg, yet outlets reap massive margins while the Collectorate's Civil Supplies Department turns a blind eye.",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_png(748, 2013, 1055, 2408, "oil_meter_photo.png")

place_exact_body_column(
    86, 2408, 392, 2586,
    text="vendors across the city today. Officials collected 24 samples of Fafda, Jalebi, chutney, frying oil, chili powder and kadhi from 14 outlets and sent them to the Public Health Laboratory. Citing hygiene",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(404, 2410, 404, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 2408, 718, 2586,
    text="Vastrapur Lake, on-spot testing of cooking oil revealed a Total Polar Compound (TPC) reading of 32—well above the permissible safety limit of 25—prompting officials to seal the outlet immediately.",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    744, 2410, 1052, 2586,
    text="outlet was frying snacks in degraded, toxic oil. Meanwhile, although thousands of kilos of Fafda-Jalebi are being fried in every neighborhood, enforcement action has been tokenistic.",
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
    lines=["Accused Continued Selling Fake Passes Even After FIR Was Registered!"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(187, 2657, 951, 2657, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 2664, 1052, 2848,
    lines=[
        "Conmen Used AI to Embed Fake QR",
        "Codes on Famous Ahmedabad Garba Passes"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    370, 2858, 554, 2884,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 2886, 554, 3014,
    text="Interrogation of two suspects arrested from Rajasthan for selling forged entry passes on Instagram for over 25 major Garba events across Ahmedabad and Gujarat revealed a startling modus operandi:",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 2862, 568, 3012, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2858, 1052, 3014,
    text="the duo grabbed official pass images from Instagram and used AI tools to superimpose fake booking QR codes. Cyber Crime police have recovered AI-edited pass templates along with WhatsApp chats with hundreds of duped buyers.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 3020, 1052, 3132,
    lines=[
        "Police Recover ChatGPT & AI Editing Tools Along",
        "With Buyer WhatsApp Chats from Arrested Duo"
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
    text="Major Navratri organizers rely on online platforms to sell digital passes. Exploiting this trend, cyber fraudsters created fake Instagram and Facebook pages offering tickets to premier Garba venues at less than half price. Cyber Crime police arrested Virendrasingh Rathod and Kishansingh Rathod from Rajasthan. To appear genuine, the duo ran paid Instagram promotions that reached over 40,000 users per post. Using ChatGPT and AI image editors, they took screenshots of official Garba passes from organizers' handles and seamlessly embedded counterfeit booking QR codes in the center so the passes looked",
    target_lines=21,
    first_indent_pt=10.0,
    hi_pt=10.8,
)
draw_line(404, 3144, 404, 3242, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3140, 718, 3236,
    text="completely authentic. They shared rate cards over WhatsApp and police have recovered",
    target_lines=3,
    first_indent_pt=0.0,
)
# Col 2 Event List Table Box (x=416..724, y=3252..3791)
draw_box(416, 3252, 724, 3791, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    424, 3258, 716, 3336,
    lines=[
        "Garba Events Targeted",
        "by the Fake Pass Gang"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(416, 3343, 724, 3343, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    422, 3346, 718, 3376,
    lines=["No. Event Name                Passes"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
draw_line(416, 3380, 724, 3380, swatch="[Black]", weight_pt=0.8)
place_exact_display_lines(
    422, 3384, 650, 3786,
    lines=[
        "1.   After 11:59",
        "2.   Mandapam",
        "3.   Chora Na Garba",
        "4.   Offbeat",
        "5.   Vanratri",
        "6.   Rang Morla",
        "7.   AEMS Ratri",
        "8.   Ratladi",
        "9.   Inner Circle",
        "10. Pancham Na Garba",
        "11. Anant Experience",
        "12. Efetone",
        "13. Safed Parinde",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.84,
)
place_exact_display_lines(
    652, 3384, 716, 3786,
    lines=[
        "118", "167", "122", "97", "51", "49", "31", "31", "20", "12", "6", "6", "6"
    ],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
draw_line(734, 3144, 734, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3140, 1052, 3792,
    text="extensive chat logs with buyers.\nThe accused even sent automated booking confirmation emails using more than 20 fake email accounts and routed payments through mule bank accounts. Even after FIRs were registered by Cyber Crime and Santej police, the duo kept shifting hideouts across Jodhpur, Bikaner and Sikar while continuing to sell fake passes online. Investigators found that Virendrasingh Rathod had pursued a BBA degree at an Ahmedabad college, giving him insider knowledge of the city's premier Navratri events.",
    target_lines=21,
    first_indent_pt=0.0,
)


# ==============================================================================
# 5. STORY 4: COLS 4-5 TOP (VIJAYADASHAMI 60-FT RAVANA DAHAN)
# ==============================================================================
print("Building Story 4 (Vijayadashami 60-ft Ravana Dahan, Cols 4-5)...")
place_exact_display_lines(
    1082, 202, 1716, 246,
    lines=["Shastra Pujan, Ramlila and Grand Celebrations Across City"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1082, 249, 1716, 249, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 254, 1718, 422,
    lines=[
        "Vijayadashami Today: 60-Ft",
        "Ravana Effigy to Be Torched"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1480, 426, 1718, 452,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 454, 1718, 544,
    text="Vijayadashami—celebrating the triumph of truth over evil—will be observed with devotion and grandeur tomorrow. According to Vedic scholars, the Vijayadashami muhurat commences at 12:50 pm.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 548, 1718, 642,
    lines=[
        "Sharadiya Navratri Culminates; Auspicious",
        "Vijayadashami Muhurat Begins After 12:50 PM"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 646, 1386, 1005,
    text="At Bhadaj's Hare Krishna Mandir, a towering 60-foot effigy of Ravana crafted over the past month by artisans from Uttar Pradesh will be consigned to flames at 8:00 pm tomorrow, preceded by a Sita-Ram Golden Chariot procession at 6:00 pm and Ramlila at 6:30 pm. At ISKCON Temple, a 25-foot Ravana effigy will be burned at 7:30 pm after Sandhya Aarti.\nMeanwhile, at AES Ground in",
    target_lines=12,
    first_indent_pt=10.0,
)
draw_line(1399.5, 650, 1399.5, 1004, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 646, 1718, 1005,
    text="Thaltej, a 51-foot Ravana effigy along with 35-foot effigies of Meghnada and Kumbhakarna will be torched at 5:30 pm amidst fireworks and folk performances. Grand Ravana Dahan events are also scheduled in Rakhial, Khokhra and numerous housing societies. Ahmedabad Fire Brigade has deployed fire tenders on standby across all registered venues.",
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
    lines=["Failed to Upload Mandatory Student Entries on Official Portal"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1065, 1718, 1065, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1070, 1718, 1220,
    lines=[
        "School Fined for Depriving 54",
        "RTE Students of Govt Financial Aid"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1480, 1222, 1718, 1246,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 1248, 1718, 1398,
    text="Children admitted under the Right to Education (RTE) Act receive Rs 3,000 in annual government assistance, provided their school uploads student details on the RTE portal. According to the City DEO, Solaris Public School in Sola failed to register its students on the portal, depriving 54 RTE children of their grant and drawing a Rs 10,000 penalty.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 1402, 1718, 1498,
    lines=[
        "City DEO Imposes Rs 10,000 Fine on Sola's Solaris",
        "Public School Under RTE Act Provisions"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 1504, 1386, 1806,
    text="Over 80,000 RTE students across Ahmedabad have received their Rs 3,000 annual grant this year. However, following a parent's complaint that students at Solaris Public School had not received the aid, an inquiry revealed the school had never uploaded the 54 RTE students' details on the RTE DBMS portal across multiple",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(1399.5, 1508, 1399.5, 1804, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1504, 1718, 1806,
    text="grades. Holding the school management accountable for gross negligence that left underprivileged students without assistance, the Ahmedabad City DEO imposed a Rs 10,000 fine under the RTE Act and directed the school to immediately complete the portal entries so the children's grants can be released.",
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
    lines=["Inspection Exposes Violations at Rakhial's Al Falah Islamic School"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1864, 1718, 1864, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1868, 1718, 2010,
    lines=[
        "DEO Recommends Cancelling School's",
        "Recognition for Unapproved Classes"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1480, 2012, 1718, 2036,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2038, 1718, 2188,
    text="Acting on a formal complaint against Al Falah Islamic School in Ahmedabad's Rakhial area, an investigation by the Ahmedabad City DEO revealed that the school admitted students far beyond sanctioned divisions in Classes 1 to 5 and ran Classes 6 to 8 without permission. The DEO has written to the Primary Education Department seeking cancellation of its recognition and nod for criminal action.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 2192, 1718, 2288,
    lines=[
        "Ahmedabad DEO Seeks State Nod to File Police",
        "Complaint and Revoke School's Affiliation"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 2294, 1386, 2826,
    text="The Ahmedabad City DEO has submitted a detailed inquiry report to the Directorate of Primary Education recommending derecognition of Al Falah Islamic School. Following an initial inspection in August, the school was fined Rs 10,000 and summoned for a hearing on August 24. A formal RTE inquiry committee subsequently submitted its findings on October 15, confirming that while the school only held permission since 2018 to operate Classes 1 to 5, physical inspection found students studying in unauthorized Classes 6 to 8.",
    target_lines=17,
    first_indent_pt=10.0,
)
draw_line(1399.5, 2298, 1399.5, 2824, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 2294, 1718, 2826,
    text="Furthermore, verification on the CTS student tracking portal revealed that students physically attending Classes 6 to 8 at Al Falah English Medium School were officially enrolled under the UDISE code of Cherry Blossom English School—an institution that has already shut down! With 1,252 students packed into Classes 1 to 5 beyond approved sections and unauthorized upper primary classes jeopardizing students' academic futures, the DEO has sought permission to lodge a police FIR.",
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
    lines=["At Sankalp Nagari Venue on Sarkhej-Sindhu Bhavan Road"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 2882, 1718, 2882, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 2888, 1718, 3048,
    lines=[
        "Unusual Crowd Surge Exposes",
        "Counterfeit Garba Ticket Racket"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1480, 3052, 1718, 3078,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 3080, 1718, 3230,
    text="A major racket printing and selling counterfeit entry passes for the Sankalp Nagari Garba on Sarkhej-Sindhu Bhavan Road has come to light. Alerted by crowd numbers far exceeding official offline sales, organizers changed Friday's pass design overnight—catching visitors carrying fake passes sold by one Vipul Bhimani. Sarkhej Police have registered an FIR.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 3234, 1718, 3334,
    lines=[
        "Organizers Redesign Friday Passes After Suspicion;",
        "Accused Printing Counterfeit Garba Tickets Identified"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 3340, 1386, 3792,
    text="Drupaddas Gandhi, a resident of Arihant Kutir Bungalows in Bopal, organized the Sankalp Nagari Garba with his partners on an AUDA plot along Sarkhej-Sindhu Bhavan Road. Alongside online bookings, the organizers printed 80,000 physical passes—8,000 per day across ten nights—for offline box-office sales outside the venue. During the first three nights of Navratri, organizers noticed that the crowd entering the ground was significantly larger than",
    target_lines=15,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3344, 1399.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 3340, 1718, 3792,
    text="the actual number of offline passes sold. Suspecting counterfeit tickets, the organizers quietly scrapped the pre-printed Friday passes and issued a brand-new design. That evening, several attendees arrived at the gates holding the old, cancelled passes. Questioning revealed they had purchased the tickets from a man identified as Vipul Bhimani, who had printed and sold duplicate Sankalp Nagari passes.",
    target_lines=15,
    first_indent_pt=0.0,
)


# ==============================================================================
# 9. STORY 8: COLS 6-8 TOP (RIVERFRONT 60-CR MULTILEVEL PARKING)
# ==============================================================================
print("Building Story 8 (Riverfront Multilevel Parking, Cols 6-8)...")
place_exact_display_lines(
    1744, 202, 2715, 254,
    lines=["Zero Public Utility Despite Massive Expenditure; Zero Rental Revenue"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 258, 2715, 258, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 264, 2715, 448,
    lines=[
        "Riverfront's Rs 60-Cr 'White Elephant'",
        "Multilevel Parking Shut for a Year"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2010, 456, 2208, 482,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 484, 2208, 604,
    text="Instances of the Ahmedabad Municipal Corporation and its subsidiary bodies—AMTS, BRTS and the Sabarmati Riverfront Development Corporation—squandering taxpayers' money continue to surface repeatedly.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 460, 2220, 602, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 456, 2715, 604,
    text="Standing as a monument to SRFDCL's administrative apathy, the Rs 60-crore multilevel parking facility opposite the Riverfront Flower Park has remained locked and unused for over a year—delivering neither parking relief to citizens nor rental income to the civic body!",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 608, 2715, 724,
    lines=[
        "Monument of Civic Failure: Authorities Now Seek to Lease",
        "Floors 1 to 5 of Parking Complex for Rs 36.42 Lakh a Year"
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
    text="Fresh tenders have been floated to lease out Floors 1 to 5 of the multilevel parking structure opposite the Riverfront",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(2064, 732, 2064, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 728, 2382, 820,
    text="system, the facility fell into disuse. Nearly a year ago, when the parking complex was first leased out, a contractor",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(2395.5, 732, 2395.5, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 728, 2715, 820,
    text="the facility remains shut—depriving visitors of parking while earning zero revenue for the civic administration.",
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
        "Civic Trick to Lower Lease Rent: Officials Slash",
        "150 Two-Wheeler & 350 Four-Wheeler Bays on Paper"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    2176, 934, 2700, 1152,
    text="Sabarmati Riverfront Development Corporation officials have devised a clever ploy to lower the reserve rental price. While the building was originally engineered to accommodate over 1,000 two-wheelers and 700 four-wheelers, the new tender lists capacity across the first five floors as just 876 two-wheelers and 372 four-wheelers—quietly slashing 500 vehicle bays!",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Parking Rate Table (Cols 6-7, x=1744..2384, y=1179..1441)
draw_box(1825, 1179, 2310, 1228, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1835, 1184, 2300, 1224,
    lines=["Multilevel Parking Tariff Rates"],
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
        "Duration",
        "Up to 2 Hours",
        "2 to 4 Hours",
        "Above 4 Hours",
        "After 12 Midnight",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2020, 1236, 2185, 1402,
    lines=["2-Wheeler", "Rs 10", "Rs 20", "Rs 30", "Rs 300"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2200, 1236, 2376, 1402,
    lines=["4-Wheeler", "Rs 20", "Rs 40", "Rs 50", "Rs 500"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    1748, 1406, 2376, 1438,
    lines=["(Overnight charge after midnight applies as a daily penalty.)"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)

# 7th Floor Restaurant Box (Cols 6-7, x=1744..2384, y=1448..1624)
draw_box(1744, 1448, 2384, 1624, stroke_swatch="[Black]", stroke_weight_pt=1.6)
place_exact_display_lines(
    1754, 1454, 2374, 1496,
    lines=["Seventh Floor Reserved for Rooftop Garden Restaurant"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1754, 1500, 2374, 1618,
    text="According to SRFDCL sources, the seventh floor of the parking complex has been reserved for a garden restaurant while the sixth floor has been kept exclusively for restaurant patrons—reducing general public parking bays and lowering the lease reserve price.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Col 8 Smart Parking Box (x=2402..2720, y=1177..1619)
draw_box(2402, 1177, 2720, 1619, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2410, 1184, 2712, 1268,
    lines=[
        "Smart Features of Riverfront",
        "Multilevel Parking Facility"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2410, 1272, 2712, 1612,
    text="The multilevel complex is equipped with CCTV surveillance, EV charging points, QR-code ticketing, digital payment kiosks, bay-occupancy sensors and automated boom barriers. Digital display boards automatically show real-time vacant bays per floor, and the facility integrates with a Smart Parking mobile app.",
    target_lines=12,
    font_style="Bold",
    first_indent_pt=10.0,
)

# Bottom 3 Columns of Riverfront Parking Story (y=1632..1904)
place_exact_body_column(
    1744, 1632, 2052, 1904,
    text="Flower Park at an annual rent of Rs 36.42 lakh. Built at a cost of Rs 60 crore to accommodate 700 cars and 1,000 two-wheelers, the smart parking complex was inaugurated in September 2023 when the incumbent Mayor served as Standing Committee Chairman. Even before citizens could familiarize themselves with its",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2064, 1634, 2064, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1632, 2382, 1904,
    text="bagged the contract for Rs 50 lakh a year. However, with monthly collections failing to cross even Rs 1 lakh, the operator surrendered the contract. Since the termination of that lease, the entire seven-storey structure has stood completely idle. Currently,",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2395.5, 1634, 2395.5, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1632, 2715, 1904,
    text="Citizens are asking who is accountable for wasting Rs 60 crore of public funds. Earlier, multilevel parking projects on Sindhu Bhavan Road and in Prahladnagar also courted controversy, raising questions over why civic authorities keep pouring crores into unviable parking complexes.",
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
    lines=["DRI Conducts 42-Hour Coordinated Crackdown Across Gujarat"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 1975, 2715, 1975, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 1982, 2715, 2168,
    lines=[
        "Gold Smuggling Syndicate Busted;",
        "Rs 18-Cr Gold Transactions Exposed, 3 Held"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2010, 2174, 2208, 2198,
    lines=["Ahmedabad, Monday"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 2200, 2208, 2296,
    text="The Directorate of Revenue Intelligence (DRI) has dismantled an organized gold smuggling syndicate routing foreign-origin gold into India through Ahmedabad and Surat international airports, arresting three",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 2178, 2220, 2294, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 2174, 2715, 2296,
    text="key operatives. The operation uncovered a tightly linked network of air passengers, receivers, middlemen, an illegal gold-melting unit operator in Vadodara and retail jewelry trade channels facilitating the disposal of smuggled bullion.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 2300, 2715, 2414,
    lines=[
        "Dubai Financier Linked to Racket; Illegal Melting Unit",
        "in Vadodara Connected to Ahmedabad & Surat Airports"
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
    text="DRI sleuths launched a 42-hour coordinated operation starting October 16, exposing the entire chain from passenger smuggling and airport handovers to illicit melting and retail jewelry sales. Transactions involving 13.017 kg of foreign-origin gold valued at Rs 18.41 crore were unearthed. Officials seized 890 grams of physical gold and recovered incriminating evidence linked to 6.41 kg of illicitly melted bullion.\nDuring follow-up searches at a jewelry showroom in Ahmedabad, officials uncovered records of unaccounted foreign-marked",
    target_lines=21,
    first_indent_pt=10.0,
)
draw_line(2064, 2424, 2064, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 2420, 2382, 2542,
    text="gold bars along with digital ledgers detailing another 5.8 kg of smuggled gold routed through a separate handler linked to",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2424, 2395.5, 2540, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2420, 2715, 2542,
    text="the syndicate's chief financier based in Dubai. All three key operatives have been arrested under the Customs Act.",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_box(2070, 2551, 2720, 2891, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2080, 2558, 2710, 2612,
    lines=["How the Gold Smuggling Syndicate Operated"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2080, 2616, 2710, 2884,
    text="*  Carrier passengers used ingenious concealment methods to smuggle gold past airport customs.\n*  Techniques included rhodium-coated gold wires, gold strips stitched inside trolley bag linings, and concealed pouches of gold paste.\n*  Upon exit, carriers handed the contraband to handlers outside Ahmedabad and Surat airports, who dispatched it via middlemen to an illegal melting unit in Vadodara.\n*  Once recast to erase foreign markings, the gold was supplied to an Ahmedabad jewelry showroom for cash sales.",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2900, 2382, 3058,
    text="Incriminating digital evidence and transaction logs covering 5.8 kg of smuggled bullion dispatched by the Dubai financier's network were seized during",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2904, 2395.5, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2900, 2715, 3058,
    text="the raid at the jewelry outlet. Three syndicate members have been placed under arrest under the provisions of the Customs Act, 1962, and further probe is underway.",
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
    lines=["Minor Dispute Over Scanning Entry Passes Turns Into Bloody Clash"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1748, 3119, 2710, 3119, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 3126, 2715, 3304,
    lines=[
        "Bouncers Attack Revellers With",
        "Swords & Chains at Mandli Garba"
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
    text="Gandhinagar / Kalol, Monday\nAmid the growing commercialization of Navratri venues, complaints of mismanagement and high-handedness by private bouncers are rising sharply. At the Mandli Garba in Nasmed near Kalol, an argument over scanning digital entry passes escalated into a bloody assault as bouncers armed with swords and iron chains attacked Garba revellers, leaving over five youths injured. Santej Police have registered an FIR.\nAccording to the complaint, Maulik Rashmiji Thakor, who runs Village Cafe in Rancharda, arrived at the Nasmed Mandli Garba around 1:00 am with his brother Tushar and friends Anil, Vivek, Setul, Vinod and Hiren Patel.",
    target_lines=16,
    first_indent_pt=10.0,
)
draw_line(2064, 3316, 2064, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 3312, 2382, 3792,
    text="Since all digital entry passes were stored on Maulik's mobile phone, he stood at the gate getting them scanned while several friends stepped inside.\nWhen a security bouncer ordered Hiren Patel to move ahead, Hiren politely replied he would enter once his friend finished scanning the passes. The bouncer lost his temper and began abusing him. Maulik and his brother stepped in to calm the situation, but the security personnel grew even more aggressive.",
    target_lines=16,
    first_indent_pt=0.0,
)
draw_line(2395.5, 3316, 2395.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 3312, 2715, 3792,
    text="Suddenly, one of the bouncers drew a sword from his waist and swung it at Maulik; as Maulik ducked, the hilt struck his head, leaving him bleeding. Within moments, nearly ten other bouncers wielding swords, bamboo sticks and iron chains charged at the group and assaulted the youths, triggering panic across the Garba venue.\nBased on the victims' complaint, Santej Police have booked the security bouncers for assault and rioting.",
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
    pd_path = target_dir / "Page_02_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_02_English_SameToSame.dns"
    png_path = target_dir / "Page_02_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_02_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_02_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_02_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_02_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
