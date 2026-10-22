# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 5 BUILDER ('INDIAN POST' — English Gujarat Samachar Edition)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- Running Header: 'INDIAN POST' in 'Indian Post Mast' (Gujarat Samachar Calligraphic Shaily)
- All placed ads/photos use .webp ('image/webp') for rapid drawing in Page Designer 1.0.
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
ASSETS_DIR = DIR_SMAE / "Page_05_Assets"

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
        "margins": p(82.0),
        "title": "INDIAN POST (English Gujarat Samachar) — Page 05 (100% Same-to-Same Editable English)"
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
    return fid, sid


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 5 English Running Header...")
build_english_running_header(5, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: NAVA VADAJ SPORTS CENTER (COLS 1-2 TOP)
# ==============================================================================
print("Building Story 1 (Nava Vadaj Sports Center, Cols 1-2 Top)...")
place_exact_display_lines(
    82, 200, 718, 244,
    lines=["Cronies Enriched Under Civic Administration"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 250, 718, 390,
    lines=[
        "Nava Vadaj Sports Complex to Be Leased",
        "Out for Merely Rs 5 Lakh Annual Fee"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 396, 718, 550,
    text="Ahmedabad, Monday\nPreparations are underway to hand over a brand-new Rs 4.67-crore Sports Complex in Nava Vadaj—equipped with AC badminton courts, a volleyball court and box cricket—to a private operator for a paltry annual lease fee of just Rs 5 lakh!",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    82, 556, 718, 650,
    lines=[
        "Built at a Cost of Rs 4.67 Crore, Complex Features",
        "AC Badminton, Volleyball & Box Cricket Arenas"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 656, 224, 945,
    text="The Ahmedabad Municipal Corporation has embarked on massive spending in the name of sports infrastructure. Whether ordinary citizens benefit or not,",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_box(232, 656, 718, 945, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    240, 662, 710, 704,
    lines=["Monthly User Fees Fixed for Sports Complex"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
)
place_exact_body_column(
    240, 708, 710, 938,
    text="Badminton Court (AC)   Rs 500 to Rs 4,000\nVolleyball Court       Rs 200 to Rs 3,000\nYoga-Meditation (AC)   Rs 200 to Rs 2,000\nChess                  Rs 150 to Rs 2,000\nCarrom                 Rs 100\nLibrary (AC)           Rs 300\nBox Cricket            Rs 700 to Rs 1,200",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    82, 952, 392, 1188,
    text="favored private contractors are set to reap windfall profits as sports complexes built with crores of taxpayers' rupees are handed over at throwaway lease rates.\nWorse still, citizens using these public-funded facilities are charged steep commercial rates! The Nava Vadaj Sports",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(400, 954, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 952, 718, 1188,
    text="Complex is the latest example. Though built to promote youth sports, its membership fees have been fixed so high that poor and middle-class families cannot afford them—yet the operator pays AMC just Rs 5 lakh a year!",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(82, 1194, 718, 1194, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 3. STORY 2: MGNREGA UNPAID WAGES (COLS 1-2 BOTTOM)
# ==============================================================================
print("Building Story 2 (MGNREGA Unpaid Wages, Cols 1-2 Bottom)...")
place_exact_display_lines(
    82, 1200, 718, 1244,
    lines=["Festivals Turn Bleak Without Hard-Earned Wages"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 1250, 718, 1390,
    lines=[
        "MGNREGA Workers & Supervisors",
        "Await Rs 3.43 Crore in Unpaid Dues"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1396, 392, 1988,
    text="Ahmedabad, Monday\nPoor rural laborers toiling under the sun across Gujarat are being forced to run from pillar to post for their rightful wages. Workers employed under the Mahatma Gandhi National Rural Employment Guarantee Act (MGNREGA) have not been paid their wages since June 20, 2026. Although the law mandates direct bank transfer within 15 days of completing work, administrative apathy has left thousands of poor families penniless during Navratri and Dussehra.\nIn Bhavnagar district alone, Rs 2.69 crore in laborers' wages remains unpaid, while MGNREGA field supervisors are owed another Rs 1.44 crore—leaving crores stuck in bureaucratic files.",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(400, 1398, 400, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 1396, 718, 1988,
    text="Across Gujarat as a whole, unpaid MGNREGA wage arrears have mounted to Rs 43 crore, making it difficult for daily-wage households even to light their kitchen stoves during the festive season.\nEnacted by the UPA government to guarantee rural livelihood security, the MGNREGA statute explicitly stipulates that wages must be credited within 15 days, failing which workers are legally entitled to delay compensation. Yet under the current administration, statutory safeguards remain confined to paper as rural laborers wait months for their hard-earned dues.",
    target_lines=19,
    first_indent_pt=0.0,
)
draw_line(732, 198, 732, 1996, swatch="[Black]", weight_pt=0.75)

# ==============================================================================
# 4. STORY 3: WORLD OSTEOPOROSIS DAY (COLS 3-4 TOP)
# ==============================================================================
print("Building Story 3 (World Osteoporosis Day, Cols 3-4 Top)...")
place_exact_display_lines(
    746, 200, 1382, 244,
    lines=["On 'World Osteoporosis Day' Today, Doctors Warn:"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 250, 1382, 390,
    lines=[
        "One in Every Three Adult Women",
        "Suffers From Weakened Bones"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 396, 1382, 550,
    text="Ahmedabad, Monday\nOsteoporosis is a condition in which bones become porous, brittle and fragile from within. Known as a 'silent killer' because it shows no early symptoms, osteoporosis affects one in every three women and one in every five men over the age of 50.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 556, 1382, 650,
    lines=[
        "Sedentary Indoor Lifestyles Leave Over 70%",
        "of Urban Residents Deficient in Vitamin D"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 656, 1056, 1125,
    text="October 20 is observed globally each year as World Osteoporosis Day. According to orthopedic specialists, changing urban lifestyles and staying indoors have left 70% to 80% of city dwellers deficient in Vitamin D. Citizens should not wait until a fracture occurs to care for bone health, nor dismiss weakening bones as an inevitable part of aging. Lifelong dietary and exercise habits directly shape skeletal strength.",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(1064, 658, 1064, 1125, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 656, 1382, 1125,
    text="According to a clinical survey in Gujarat among adults aged 40 to 80, 22% fell in the high-risk category for hip fractures and 24% for major osteoporotic fractures. Dr. Jatin Vakharia emphasized that a calcium-rich balanced diet, adequate Vitamin D levels and regular weight-bearing exercise preserve bone density. Post-menopausal women, seniors and those with prior fractures should undergo timely bone mineral density screening.",
    target_lines=15,
    first_indent_pt=0.0,
)
draw_line(746, 1132, 1382, 1132, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 5. STORY 4: BAPUNAGAR 24 LAKH HEROIN SEIZURE (COLS 3-4 BOTTOM)
# ==============================================================================
print("Building Story 4 (Bapunagar 24 Lakh Heroin Seizure, Cols 3-4 Bottom)...")
place_exact_display_lines(
    746, 1140, 1382, 1184,
    lines=["Near Sonaria Blocks in Bapunagar Area"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1190, 1382, 1330,
    lines=[
        "Two Held With Rs 24 Lakh Heroin",
        "While Peddling Drugs on Street!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1336, 1382, 1465,
    text="Ahmedabad, Monday\nExposing brazen street-corner narcotics peddling in Ahmedabad, Bapunagar Police arrested two men red-handed with heroin worth Rs 24.82 lakh and booked five persons—including a woman mastermind smuggling consignments from Rajasthan.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1472, 1382, 1568,
    lines=[
        "Five Booked Including Woman Handler & Rajasthan",
        "Supplier Contacted via WhatsApp to Source Heroin"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1574, 1056, 1988,
    text="Acting on a tip-off, a Bapunagar Police team nabbed two men sitting on a Burgman scooter near Sonaria Blocks while selling heroin on the street. Police seized 53.890 grams of heroin worth Rs 10.77 lakh from Rohit Bhairosingh Rajput and 70.22 grams worth Rs 14.05 lakh from Anand Somabhai Prajapati, both residents of Sonaria Blocks. During interrogation, the duo confessed they worked for local handlers Nanu alias Bhavesh Natwarbhai Patni and Tinaben Pappubhai Patni.",
    target_lines=14,
    first_indent_pt=9.0,
)
draw_line(1064, 1576, 1064, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 1574, 1382, 1988,
    text="The carriers traveled to Sanchore in Rajasthan and coordinated over WhatsApp to pick up the narcotics. Having already smuggled six to seven consignments into Ahmedabad, the duo received Rs 10,000 per trip to Rajasthan plus retail commission. Seizing 124.111 grams of heroin worth Rs 24.82 lakh in total, Bapunagar Police have launched a hunt for Tinaben, Nanu Patni and the Rajasthan-based supplier.",
    target_lines=14,
    first_indent_pt=0.0,
)
draw_line(82, 1996, 1382, 1996, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 6. PLACE INDIAN BANK AD & VIJAY SALES AD (.WEBP)
# ==============================================================================
print("Placing Indian Bank & Vijay Sales Advertisements (.webp)...")
place_png(1400, 188, 2725, 2010, "ad_indian_bank_right.png")
place_png(0, 2010, 2800, 3974, "ad_vijay_sales_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_05_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_05_English_SameToSame.dns"
    png_path = target_dir / "Page_05_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_05_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_05_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_05_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_05_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
