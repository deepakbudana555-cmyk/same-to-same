# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 4 BUILDER ('INDIAN POST' — English Gujarat Samachar Edition)
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
ASSETS_DIR = DIR_SMAE / "Page_04_Assets"

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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 04 (100% Same-to-Same Editable English)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCyanBorder", "color": "#0088cc"}},
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
    font_family_override: str = None,
):
    if font_family_override and not custom_font_family:
        custom_font_family = font_family_override
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
    lo_pt: float = 6.8,
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

    best_cfg = (9.0, default_hscale, 0.0)
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
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 4 English Running Header...")
build_english_running_header(4, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: PORBANDAR 'REEL POLITICS' (COLS 1-3 TOP)
# ==============================================================================
print("Building Story 1 (Porbandar Reel Politics, Cols 1-3 Top)...")
place_exact_display_lines(
    82, 200, 1050, 246,
    lines=["Union Minister's 'Reel Politics' Sparks Backlash in Porbandar"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 254, 1050, 462,
    lines=[
        "Minister Holds Hotel Meet With Social",
        "Media Influencers to Woo Gen-Z Voters!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 468, 556, 620,
    text="Porbandar, Monday\nDuring his visit to Porbandar, Union Minister Dr. Mansukh Mandaviya hosted a special closed-door meeting with social media content creators and digital influencers at a city hotel,",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 470, 564, 618, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 468, 1050, 620,
    text="triggering sharp criticism in local political circles that he prioritized personal digital branding over addressing pressing civic and developmental grievances of residents.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 626, 1050, 742,
    lines=[
        "Anger Over Sidestepping Real Civic Issues: Citizens Say",
        "'Votes Will Come From Tangible Results, Not From Reels'"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 748, 386, 1188,
    text="Following directives from New Delhi to court Gen-Z and young voters, traditional public rallies were bypassed in favor of digital outreach, where the Union Minister hailed content creators as 'social media warriors' over dinner and gifts.\nYet core issues in Porbandar—unfulfilled industrial promises, youth unemployment, inflation, remunerative crop prices for farmers and acute shortages at the civil hospital—remain unresolved. Moreover, silence over the controversial pipeline project dumping toxic chemical",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(400, 750, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 748, 718, 1188,
    text="effluents from Jetpur's dyeing industry into Porbandar's sea, months of darkness at the fishing harbor, and unlit stretches toward Asmavati Ghat endangering fishermen have left citizens demanding accountability.\nLocals point out that banter, selfies and Instagram reels with a handful of pliant influencers cannot mask ground realities. Porbandar's electorate sees clearly through glossy social media filters and staged bonhomie.",
    target_lines=15,
    first_indent_pt=0.0,
)
draw_line(732, 750, 732, 1348, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 748, 1050, 918,
    text="Citizens firmly believe genuine popularity is earned only by resolving basic public grievances—and leaders must realize that electoral support comes from on-ground results, not viral reels.",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(746, 925, 1050, 925, swatch="[Black]", weight_pt=0.85)

# Story 2: Col 3 Middle (Ahmedabad Temperature 37C)
print("Building Story 2 (Ahmedabad Temperature, Col 3 Middle)...")
place_exact_display_lines(
    746, 932, 1050, 1012,
    lines=[
        "Ahmedabad Mercury to Hover",
        "Around 37°C for Next Five Days"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1018, 1050, 1348,
    text="Ahmedabad, Monday\nWith daytime heat persisting across the city, Ahmedabad recorded a maximum temperature of 37.1°C on Monday. Weather forecasters expect the city's maximum temperature to remain around 37°C over the next five days. Elsewhere across Gujarat, Rajkot recorded 40.8°C, Bhuj 39.0°C, Surat 37.7°C, Vadodara 37.6°C and Bhavnagar 36.4°C.",
    target_lines=11,
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. STORY 3: 'BY THE WAY' ('VAAT VAATMA') HUMOR COLUMN (COLS 4-5 TOP)
# ==============================================================================
print("Building Story 3 (By The Way Column, Cols 4-5 Top)...")
draw_box(1078, 195, 1718, 1352, stroke_swatch="GsCyanBorder", stroke_weight_pt=2.5)
draw_box(1088, 202, 1708, 308, fill_swatch="GsCyanBorder", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1100, 210, 1696, 300,
    lines=["BY THE WAY"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    1094, 314, 1702, 382,
    lines=["'Reservation Quota' in Navratri Passes?"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1092, 388, 1390, 1342,
    text="Just think about it... Energetic youngsters who truly deserve Navratri passes barely manage an average of one-and-a-half passes!\nMeanwhile, uncles and aunties who start panting after just three rounds of Garba sit on an average of four passes every single night!\nThat is why we firmly believe there should be a 'Reservation Quota' system for Garba passes!\nHere is how...\n* * *\nReserve 50 percent of all passes strictly for women! After all, it is women who make any Garba venue worth watching!\nAnd if some guy still sneaks in dressed like 'Bobby Darling', send him straight up to the stage!\n* * *\nKeep 10 percent of passes reserved for ENT specialists! Because the deafening blast of DJ speakers shakes even the toughest eardrums!\nYour ears go so numb that the next morning you wonder why you cannot hear your boss—when in fact you slept right through your 8 am alarm!\nIf ENT doctors are present right on the",
    target_lines=29,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1398, 390, 1398, 1340, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1406, 388, 1704, 1342,
    text="ground, revellers can get instant checkups!\n* * *\nSet aside 5 percent of passes for throat specialists! Because shouting for two minutes to greet friends over the roaring speakers leaves everyone with a raspy sore throat!\nEven if those doctors offer a 15 percent discount for on-the-spot treatment, it will be a blessing!\n* * *\nNext, allocate 25 percent of passes to college students, 12 percent to senior citizens, 10 percent to kids, and 2 percent to women police personnel. Fair enough?\n* * *\nAnd finally... reserve 50 percent exclusively for the 'spectator crowd' that only comes to watch!\nWait a second! You will say, 'Mannubhai, you have already counted 114 percent! Where will you squeeze in another 50 percent?'\nWell friends, isn't that exactly what Garba organizers do? They let in an extra 50 percent beyond capacity—leaving zero room on the ground to actually play Garba!\n- Mannu Sheikhchilli",
    target_lines=29,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. STORY 4: SOLAR POWER CUT (COLS 6-8 TOP)
# ==============================================================================
print("Building Story 4 (Solar Power Cut, Cols 6-8 Top)...")
place_exact_display_lines(
    1744, 200, 2715, 246,
    lines=["Generation Curtailed at Solar Plants Above Two Megawatts"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1744, 252, 2715, 412,
    lines=[
        "State Curtails Solar Power Generation",
        "to Benefit Private Thermal Power Firms"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 418, 2222, 594,
    text="(By Our Correspondent) Ahmedabad, Monday\nEven as power shortages push Gujarat toward a supply crunch, the state government is bafflingly forcing solar power producers to slash generation by 20% to 70%. Although solar energy is pollution-free and cannot be switched off while the sun shines, state utilities have ordered solar plants above",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 420, 2229, 592, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 418, 2715, 594,
    text="two megawatts to curtail output by 20% to 70% of installed capacity. With no grid-scale storage available to bank surplus daytime solar electricity, state power distribution companies have been emailing solar generators instructing them to feed only 30%, 40%, 50% or 80% of their capacity.",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 602, 2715, 720,
    lines=[
        "Despite Zero Storage Option for Daytime Solar Energy,",
        "State Directs Producers to Slash Power Generation"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 726, 2052, 1348,
    text="Meanwhile, industrial and residential electricity consumers across Gujarat are forced to bear high tariffs of around Rs 8 per unit. Although 1,500 to 2,000 solar generators with capacities above 2 MW supply clean power to state discoms at just Rs 2.76 to Rs 2.95 per unit under signed power purchase agreements, they are being forced to back down generation so costly power from private thermal plants can be purchased instead. On October 18, solar units were ordered to cut output by 20%, following earlier directives slashing generation by 50% to 70%.",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2064, 728, 2064, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 726, 2382, 1072,
    text="Because unutilized daytime solar power cannot be stored, nearly 1 crore units of clean electricity are wasted daily across 1,500 to 2,000 plants. On September 23, emails sent to over 1,500 solar generators instructed them to curtail grid injection by 50 percent.",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_line(2395, 728, 2395, 1072, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 726, 2715, 1072,
    text="Dispatches from the State Load Dispatch Centre (SLDC) in Vadodara reveal that prior to September 23, 2026, solar generators faced a 70% curtailment order, which was subsequently revised to a 50% supply cut across the state.",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_line(2076, 1080, 2715, 1080, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 5. STORY 5: SEVA SETU (COLS 7-8 MIDDLE)
# ==============================================================================
print("Building Story 5 (Seva Setu, Cols 7-8 Middle)...")
place_exact_display_lines(
    2076, 1088, 2715, 1134,
    lines=["Stark Reflection of Broken Routine Civic Administration"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    2076, 1140, 2715, 1280,
    lines=[
        "22,264 Citizens Had to Wait for",
        "'Seva Setu' Camps to Get Basic Benefits"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1286, 2715, 1404,
    text="Ahmedabad, Monday\nCivic authorities claim to have disposed of 22,264 applications across seven Seva Setu camps held in Ahmedabad so far—which equally proves that over twenty-two thousand citizens were forced to wait for special camps just to obtain routine government services!",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1410, 2715, 1510,
    lines=[
        "9,600 Applications Were Just for Health Wellness Cards!",
        "Routine Ward Applications Held Back to Inflate Camp Tally"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1516, 2382, 2132,
    text="While the state government launched Seva Setu camps to deliver doorstep public services, in Ahmedabad these camps expose the breakdown of routine ward administration. Worse still, to make Seva Setu camps appear successful on paper, officials reportedly hold back daily applications submitted at ward offices and process them only during camp days—causing further delays for applicants! Although authorities claim 56 government services are covered under Seva Setu, out of 22,264 applications in Ahmedabad, 9,604 were merely for Health Wellness Cards!",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2395, 1518, 2395, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1516, 2715, 1618,
    text="Health card enrollments are being used to inflate camp numbers. If elected representatives ensured",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(2408, 1624, 2715, 2020, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2416, 1630, 2706, 1712,
    lines=["Seva Setu Camp", "Application Tally"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2416, 1718, 2706, 2012,
    text="East Joint Camp        10,227\nWest Joint Camp         6,149\nNorth-West Zone           728\nEast Zone               1,096\nCentral Zone            1,260\nWest Zone               1,485",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2026, 2715, 2132,
    text="officials worked sincerely every day at ward offices, special Seva Setu camps would not be needed at all.",
    target_lines=3,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. STORY 6: DOUBLE DECKER FREIGHT TRAIN (COLS 3-4 MIDDLE)
# ==============================================================================
print("Building Story 6 (Double Decker Freight Train, Cols 3-4 Middle)...")
draw_line(746, 1356, 2052, 1356, swatch="[Black]", weight_pt=0.85)
place_exact_display_lines(
    746, 1364, 1382, 1406,
    lines=["Major Railway Initiative to Boost Freight Corridor Capacity"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1412, 1382, 1542,
    lines=[
        "1.5-Km-Long Double-Decker Freight",
        "Train Runs Between Mumbai & Ahmedabad"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1548, 1382, 1676,
    text="Ahmedabad, Monday\nMumbai and Ahmedabad serve as vital hubs for Gujarat's trade, industry and logistics. To accelerate cargo movement between the two industrial corridors, Indian Railways operated a 1.5-kilometer-long double-stack container freight train.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1682, 1382, 1782,
    lines=[
        "360-Container Freight Train Hauled by 12,000 HP",
        "Lead Locomotive and 9,000 HP Mid-Train Engine"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1788, 1050, 2175,
    text="According to railway officials, the 1.5-km double-stack container freight train was operated on the Mumbai-Ahmedabad route carrying 360 containers stacked across two tiers for the first time. The formation was powered by a 12,000 HP 'Make in India' electric locomotive in front and a 9,000 HP locomotive coupled in the middle.",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1064, 1790, 1064, 2175, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 1788, 1382, 2175,
    text="While Mumbai provides vital port connectivity and market access for Gujarat's industries, Ahmedabad anchors manufacturing across north and central Gujarat. Electric double-stack container trains are expected to streamline cargo movement between the two cities, though traders await tangible reductions in freight tariffs.",
    target_lines=13,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. STORY 7: MBBS EXTRA ATTEMPT (COLS 5-6 MIDDLE)
# ==============================================================================
print("Building Story 7 (MBBS Extra Attempt, Cols 5-6 Middle)...")
draw_line(1396, 1360, 1396, 2304, swatch="[Black]", weight_pt=0.75)
place_exact_display_lines(
    1412, 1364, 2052, 1406,
    lines=["Relief for Medical Batches Admitted in 2019-20 and Thereafter"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1412, 1412, 2052, 1542,
    lines=[
        "Unsuccessful MBBS Students Granted",
        "One Additional Attempt to Clear Exam"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1548, 2052, 1676,
    text="Ahmedabad, Monday\nTaking note of academic disruptions caused by Covid-19 and health exigencies, the National Medical Commission (NMC) has granted one additional attempt to clear the First Professional MBBS examination, giving batches from 2019-20 onward five total attempts.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1412, 1682, 2052, 1782,
    lines=[
        "NMC Expands First-Year MBBS Clearance Limit",
        "From Four Attempts to Five Under Special Norms"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1788, 1718, 2302,
    text="Considering Covid duty and medical hardships, the National Medical Commission had earlier allowed a one-time extra attempt for MBBS students admitted in 2019-20 and 2020-21. Following representations from universities and medical colleges on behalf of subsequent cohorts, the NMC has now extended the fifth attempt facility to students admitted in 2019-20 and later academic years.\nWhile standard regulations permit four attempts, this special fifth attempt",
    target_lines=16,
    first_indent_pt=9.0,
)
draw_line(1731, 1790, 1731, 2302, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 1788, 2052, 2060,
    text="is subject to strict conditions: the candidate must not have already availed a fifth attempt, their admission must remain active on university rolls, and the total duration of the MBBS course including compulsory rotating internship must not exceed ten years.",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_box(1744, 2068, 2052, 2302, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1752, 2076, 2044, 2294,
    text="Readers are advised that this publication does not guarantee the accuracy of claims made in any advertisement. Readers should independently verify all details before taking any decision.\n- Advertisement Manager",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. PLACE BOTTOM DRAMA ADS (.WEBP), PUBLIC NOTICES & IMPRINT BLOCKS (EDITABLE ENGLISH)
# ==============================================================================
print("Placing Page 4 Drama Ads (.webp), Public Notices & Imprint (100% Editable English Text)...")
place_png(75, 1210, 726, 3810, "ads_col12_bottom.png")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=38, right_lines=40, header_h=54):
    x_mid = (x1_px + x2_px) // 2
    draw_box(x1_px, y1_px, x2_px, y2_px, fill_swatch="[Paper]", fill_tint=1.0, stroke_swatch="[Black]", stroke_weight_pt=1.8)
    draw_box(x1_px, y1_px, x_mid - 4, y1_px + header_h, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
    place_exact_display_lines(
        x1_px + 10, y1_px + 6, x_mid - 14, y1_px + header_h - 4,
        lines=["PUBLIC NOTICE"],
        font_style="Bold",
        fill_swatch="[Paper]",
        align="center",
        stretch_lines=False,
    )
    draw_line(x_mid, y1_px + 10, x_mid, y2_px - 10, swatch="[Black]", weight_pt=0.75)
    place_exact_body_column(
        x1_px + 10, y1_px + header_h + 6, x_mid - 8, y2_px - 8,
        text=left_text,
        target_lines=left_lines,
        first_indent_pt=0.0,
        hi_pt=10.5,
        lo_pt=6.8,
    )
    place_exact_body_column(
        x_mid + 8, y1_px + 10, x2_px - 10, y2_px - 8,
        text=right_text,
        target_lines=right_lines,
        first_indent_pt=0.0,
        hi_pt=10.5,
        lo_pt=6.8,
    )


# Notice 0: Cols 1-2 Bottom over ads_col12_bottom.webp (82..718, 2962..3792)
place_public_notice_2col(
    82, 2962, 718, 3792,
    left_text=(
        "Notice is hereby given to the general public that old tenure agricultural land bearing Re-Survey Block/Survey No. 1179 (Old Survey No. 282 Paiki 4) admeasuring 4087 sq.mtrs. of Mouje Village Kuma, Taluka Viramgam, Sub-District Viramgam, Registration District Ahmedabad, is stated to be in the independent ownership, possession and enjoyment of Divyaben Rikeshbhai Patel free from all encumbrances, who has agreed to sell the same to our client, and our client has requested a Title Clearance Certificate from us. If any person has any right, title, interest, share, claim or charge over the said land, they must notify the"
    ),
    right_text=(
        "undersigned in writing by Registered A.D. with documentary proof within 7 (seven) days from publication hereof; failing which it shall be deemed that no person has any right, title, interest, claim or charge over the said land, or if any existed, the same stands waived, and a Title Clearance Certificate shall be issued in favor of our client and no objection shall be entertained thereafter.\n"
        "File No. 10401 | Date: 20-10-2026\n"
        "Sharad N. Darji (Advocate & Notary)\n"
        "(M.Com., LL.B.)\n"
        "Office: B-501, Satyamev Complex, Opp. New Gujarat High Court, S.G. Highway, Sola, Ahmedabad-380060.\n"
        "Phone No.: 079-29606800"
    ),
    left_lines=22,
    right_lines=24,
)


# Notice 1: Cols 3-4 Bottom (746..1382, 2200..3792)
draw_line(746, 2184, 1382, 2184, swatch="[Black]", weight_pt=0.85)
place_public_notice_2col(
    746, 2200, 1382, 3792,
    left_text=(
        "Notice is hereby given to the general public that property bearing Plot No. 13 admeasuring 225 sq.yds. (188.12 sq.mtrs.) together with residential construction standing thereon in the scheme known as 'Shreenath Bungalows', situate upon land bearing Re-Survey Block/Survey No. 478 (Old Block/Survey No. 206/1) admeasuring 5059 sq.mtrs. of Mouje Village Chandkheda, Taluka Sabarmati, Registration District Ahmedabad, Sub-District Ahmedabad-2 (Vadaj), is stated to be in the joint ownership, possession and enjoyment of Rameshbhai Manilal Patel and Shakuntalaben Rameshbhai Patel, free from all encumbrances, who have agreed to sell the same to our client, and our client has requested a Title Clearance and Marketability Certificate from us.\n"
        "If any bank, financial institution, firm or person has any share, right, title, interest, claim, charge, lien or banakhat right in the said property,"
    ),
    right_text=(
        "they are hereby called upon to notify the undersigned in writing by Registered A.D. with certified documentary proof within 7 (seven) days from the publication of this notice; failing which it shall be deemed that no other person or entity has any right, title, interest or claim in the said property, or if any existed, the same stands waived, and upon expiry of the notice period, a Title Clearance Certificate shall be issued in favor of our client and no subsequent objection shall be entertained.\n"
        "Date: 20/10/2026\n"
        "Rajesh K. Patel (Advocate)\n"
        "Office: 304, 3rd Floor, Satyamev Eminence, Science City Road, Sola, Ahmedabad-380060.\n"
        "Mob. No. 98250 45678"
    ),
    left_lines=38,
    right_lines=40,
)

# Col 5 Notice (1-col) + Col 6 English Imprint + Cols 5-6 Bottom Imprint
draw_box(1412, 2314, 1724, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
draw_box(1412, 2314, 1724, 2368, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1420, 2320, 1716, 2364,
    lines=["PUBLIC NOTICE"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1420, 2374, 1716, 3186,
    text=(
        "Residential Plot No. 24 admeasuring 180 sq.yds. situate in the housing scheme on non-agricultural land bearing Block/Survey No. 1428 of Mouje Saij, Taluka Kalol, Registration District Gandhinagar, Sub-District Kalol, is stated to be in the independent ownership and possession of Patel Kanubhai Maganbhai, who has requested a Title Clearance Certificate. Any person having any claim or objection should notify the undersigned by Regd. A.D. within 7 days.\n"
        "Date: 20/10/2026\n"
        "Ashwin J. Patel (Advocate)\n"
        "Navrangpura, Ahmedabad."
    ),
    target_lines=24,
    first_indent_pt=0.0,
    hi_pt=10.2,
    lo_pt=6.8,
)

# Col 6 Imprint Box (1738..2052, 2314..3194)
draw_box(1738, 2314, 2052, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1748, 2324, 2042, 3184,
    text=(
        "INDIAN POST (The Gujarat Samachar English)\n"
        "Printed and Published by Shreyans S. Shah on behalf of Lok Prakashan Ltd. and Printed at Lok Prakashan Ltd., Gujarat Samachar Bhavan, Khanpur, Ahmedabad and Published from Gujarat Samachar Bhavan, Khanpur, Ahmedabad.\n"
        "Editor: Shreyans S. Shah\n"
        "(Responsible for selection of news under the PRB Act).\n"
        "RNI No. 1609/57.\n"
        "Phone: (079) 25504010"
    ),
    target_lines=22,
    font_style="Bold",
    align="left",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)

# Cols 5-6 Bottom Imprint Box (1412..2052, 3206..3792)
draw_box(1412, 3206, 2052, 3792, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1422, 3216, 1724, 3782,
    text=(
        "Printer & Publisher on behalf of Lok Prakashan Limited: Shreyans Shantilal Shah\n"
        "Printed at Lok Prakashan Limited's Gujarat Samachar Bhavan, Khanpur, Ahmedabad-380001 and Published from the same address.\n"
        "Editor: Shreyans Shantilal Shah"
    ),
    target_lines=14,
    font_style="Bold",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)
draw_line(1732, 3216, 1732, 3782, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1742, 3216, 2042, 3782,
    text=(
        "(Responsible for selection of news under the P.R.B. Act)\n"
        "Head Office: Gujarat Samachar Bhavan, Khanpur, Ahmedabad-380001.\n"
        "Phone: (079) 25504010 (10 Lines)\n"
        "RNI No. 1609/57"
    ),
    target_lines=14,
    font_style="Bold",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)

# Cols 7-8 Bottom Two Public Notices (2076..2715, 2152..3792)
draw_line(2076, 2142, 2715, 2142, swatch="[Black]", weight_pt=0.85)
place_public_notice_2col(
    2076, 2154, 2715, 2964,
    left_text=(
        "Mouje - Gota\n"
        "Property bearing Flat No. A/402 in the residential scheme standing on non-agricultural land bearing Block/Survey No. 215, T.P. Scheme No. 32, Final Plot No. 54 of Mouje Village Gota, Taluka Ghatlodia, District Ahmedabad, Sub-District Ahmedabad-8 (Sola), owned and possessed independently by Patel Dineshbhai Ramanlal free from all encumbrances, has been agreed to be sold to our client, who has sought a Title Clearance Certificate."
    ),
    right_text=(
        "Any person or institution having any share, right, title, claim or charge over the said property must notify the undersigned in writing with documentary proof by Regd. A.D. within 7 days from publication hereof; failing which any such claim shall be deemed waived and a Title Clearance Certificate shall be issued.\n"
        "Date: 20/10/2026\n"
        "Ketan M. Patel (Advocate)\n"
        "Sola Road, Ahmedabad."
    ),
    left_lines=22,
    right_lines=24,
)
place_public_notice_2col(
    2076, 2978, 2715, 3792,
    left_text=(
        "Mouje - Bopal\n"
        "Property bearing Bungalow No. 12 in the residential scheme situate on land bearing Block No. 412, T.P. Scheme No. 3, Final Plot No. 88 of Mouje Village Bopal, Taluka Daskroi, Registration District Ahmedabad, Sub-District Ahmedabad-9 (Bopal), is stated to be in the sole ownership and possession of Shah Vinodchandra Chimanlal free from all encumbrances, who has requested a Title Clearance Certificate."
    ),
    right_text=(
        "Any person having any share, right, title, claim or charge over the said property must notify the undersigned in writing with documentary proof by Regd. A.D. within 7 days from publication hereof; after expiry of the period, no objection shall be entertained and a Title Clearance Certificate shall be issued.\n"
        "Date: 20/10/2026\n"
        "Nilesh R. Shah (Advocate)\n"
        "Bopal, Ahmedabad."
    ),
    left_lines=22,
    right_lines=24,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_04_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_04_English_SameToSame.dns"
    png_path = target_dir / "Page_04_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_04_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_04_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_04_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_04_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
