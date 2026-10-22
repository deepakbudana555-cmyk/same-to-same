# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 3 BUILDER ('INDIAN POST' — English Gujarat Samachar Edition)
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
ASSETS_DIR = DIR_SMAE / "Page_03_Assets"

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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 03 (100% Same-to-Same Editable English)"
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
# 1. PLACE RUNNING HEADER & ADVERTISEMENTS (.WEBP)
# ==============================================================================
print("Placing Page 3 English Running Header & Advertisements...")
build_english_running_header(3, place_png, draw_box, place_exact_display_lines)

# Story 1: Cols 1-3 (Online Courses Internship & Training Policy)
print("Building Story 1 (Online Courses Internship Policy, Cols 1-3)...")
place_exact_display_lines(
    82, 200, 1050, 244,
    lines=["Launched for the First Time in the State by Gujarat University"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    82, 250, 1050, 412,
    lines=[
        "New Policy Soon for Internships",
        "& Training in Online Degree Courses"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
)
place_exact_body_column(
    82, 418, 398, 594,
    text="Ahmedabad, Monday\nGujarat University—the first state university in Gujarat to launch full-fledged online degree programs—will soon formulate a dedicated policy governing mandatory internships and on-the-job training under the National Education Policy (NEP).",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(406, 420, 406, 592, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 418, 1050, 594,
    text="Currently, regular offline students across state universities complete physical internships during their fifth semester. Since physical on-site training is impractical for remote learners enrolled in online programs, the university is drafting guidelines to enable structured virtual internships.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 602, 1050, 718,
    lines=[
        "With Physical Training Impractical as in Regular Courses,",
        "Students Will Be Permitted to Complete Online Internships"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 724, 386, 822,
    text="Three years after receiving UGC approval to offer three undergraduate and",
    target_lines=3,
    first_indent_pt=9.0,
)
draw_line(400, 726, 400, 820, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 724, 718, 822,
    text="enrolled in the inaugural October intake across six online degree programs:",
    target_lines=3,
    first_indent_pt=0.0,
)
# Callout Box: BA-BCom Online Demand
draw_box(82, 830, 718, 1158, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    94, 838, 706, 932,
    lines=[
        "Strong Demand for Online BA-BCom:",
        "Admissions Surge 50% Within a Single Year"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    94, 938, 706, 1150,
    text="Total enrollments across Gujarat University's six online programs have reached 1,143, driven by a 50% surge in demand for online BA and BCom degrees. After 154 admissions in last October's maiden batch and 343 in the February intake, 646 students joined in July this year—including 243 in BA and 301 in BCom. The university has now sought UGC nod to launch online MBA, Journalism, MCA and Library Science programs.",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=10.0,
)
place_exact_body_column(
    82, 1164, 386, 1236,
    text="three postgraduate online courses, Gujarat University finally launched",
    target_lines=2,
    first_indent_pt=0.0,
)
draw_line(400, 1166, 400, 1236, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 1164, 718, 1236,
    text="BA English, BCom General, BCA, MA English, MCom General and",
    target_lines=2,
    first_indent_pt=0.0,
)
draw_line(732, 726, 732, 1468, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 724, 1050, 1468,
    text="MSc Mathematics. Following the October batch, admissions were conducted in February and July, taking total enrollment across three admission cycles to 1,143 students.\nUnder NEP norms, mandatory fifth-semester internships apply equally to online undergraduate students. While last year's inaugural cohort of 154 students is currently in the third semester, they will enter the fifth semester next academic year and must complete compulsory internships and on-the-job training. Since Gujarat University is currently the sole state university running these UGC-approved online degrees, an expert committee will frame the online internship assessment policy.",
    target_lines=23,
    first_indent_pt=9.0,
)
draw_line(1064, 198, 1064, 1482, swatch="[Black]", weight_pt=0.75)

# Story 2: Col 4 Top (PSI Non-Bailable Warrant)
print("Building Story 2 (PSI Non-Bailable Warrant, Col 4 Top)...")
place_exact_display_lines(
    1078, 200, 1382, 286,
    lines=[
        "Non-Bailable Warrant Against",
        "PSI for Skipping Court Testimony"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 292, 1382, 745,
    text="Ahmedabad, Monday\nTaking serious note of repeated non-appearance to depose as a witness in a six-year-old case of obstructing public servants on duty, the Ahmedabad Rural Court issued a non-bailable warrant against former Nikol Police Station PSI S.V. Chhasathiya. Alarmed by the warrant, the officer rushed to court seeking its cancellation; while the court recalled the warrant, it imposed a Rs 1,000 fine as a stern warning.",
    target_lines=14,
    first_indent_pt=9.0,
)
draw_line(1078, 753, 1382, 753, swatch="[Black]", weight_pt=0.85)

# Story 3: Col 4 Bottom (21,000 Cr Narco-Terror Case)
print("Building Story 3 (21,000 Cr Narco-Terror Drugs Case, Col 4 Bottom)...")
place_exact_display_lines(
    1078, 760, 1382, 844,
    lines=[
        "Bail Denied to Sarabjit Singh in",
        "Rs 21,000-Cr Narco-Terror Case"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1078, 850, 1382, 1472,
    text="Ahmedabad, Monday\nA Special NIA Court here has firmly rejected the regular bail plea of accused Sarabjit Singh alias Sethi, who was arrested red-handed in Punjab with 450 grams of heroin in connection with the Rs 21,000-crore Mundra Port international narco-terror drug haul. The NIA judge observed that a strong prima facie case exists against the accused involving grave threats to national security and cross-border terror financing. On September 13, 2021, authorities had seized 2,988.21 kg of Afghan heroin concealed inside semi-processed talc stone containers shipped via Iran to Mundra Port in Kutch.",
    target_lines=20,
    first_indent_pt=9.0,
)
draw_line(1395, 198, 1395, 1482, swatch="[Black]", weight_pt=0.75)
draw_line(746, 1482, 1382, 1482, swatch="[Black]", weight_pt=0.85)

# Place Advertisements (Kalamandir/Aakar, Lokmanya, TBZ, Bajaj Pulsar as .webp)
place_png(75, 1260, 726, 2005, "ad_kalamandir_aakar.png")
place_png(740, 1490, 1400, 2005, "ad_lokmanya.png")
place_png(1402, 188, 2725, 2005, "ad_tbz_right.png")
place_png(0, 2005, 2800, 3974, "ad_bajaj_pulsar_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_03_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_03_English_SameToSame.dns"
    png_path = target_dir / "Page_03_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_03_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_03_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_03_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_03_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
