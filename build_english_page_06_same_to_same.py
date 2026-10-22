from gs_english_running_header import build_english_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 6 BUILDER FOR INDIAN POST (ENGLISH GUJARAT SAMACHAR)
===================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable English Text ('Georgia' & 'Times New Roman')
  for Gauchar Land Encroachment PIL, Gujarat Power Crisis Continuation,
  4 Obituaries (In Memoriam / Sad Demise), and 15 Public Notices (PUBLIC NOTICE)!
- Placed Assets (.webp): All obituary photos & bottom CMYK bar placed in .webp format!
"""

import json
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
ASSETS_DIR = DIR_SMAE / "Page_06_Assets"

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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 06 (100% Same-to-Same Editable English)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.2)


def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):
    webp_cand = ASSETS_DIR / (Path(filename).stem + ".webp")
    asset_file = webp_cand if webp_cand.exists() else (ASSETS_DIR / filename)
    img_path = str(asset_file.resolve()).replace("\\", "/")
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
    custom_font_family: str = None,
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

    if custom_font_family:
        use_font_family = custom_font_family
        use_font_style = "Regular"
    elif font_family_override:
        use_font_family = font_family_override
        use_font_style = font_style_override or "Regular"
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 16.0:
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
        for try_hs in (0.85, 0.80, 0.75, 0.70, 0.65):
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

    best_cfg = (9.0, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.08:
            continue
        for hs100 in (94, 90, 87, 84, 81, 78, 75):
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


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 6 English Running Header...")
build_english_running_header(6, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: GAUCHAR LAND ENCROACHMENT PIL (COLS 2-4 TOP)
# ==============================================================================
print("Building Story 1 (Gauchar Land Encroachment PIL, Cols 2-4 Top)...")
place_exact_display_lines(
    414, 200, 1382, 245,
    lines=["PIL Over Encroachment on Gauchar Pasture Land in Antrol Village of Vav"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    414, 250, 1382, 412,
    lines=[
        "High Court Seeks Action Report",
        "on Removal of Gauchar Encroachments"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    414, 418, 718, 902,
    text="Ahmedabad, Monday\nA Public Interest Litigation (PIL) has been filed before the Gujarat High Court regarding alleged illegal encroachments on Gamtal and Gauchar pasture land and the construction of commercial shops rented out inside the local school campus at Antrol village in Vav-Tharad taluka of Banaskantha district. Hearing the petition, a division bench comprising Acting Chief Justice Manas Ranjan Pathak and Justice Nikhil S. Kariel directed the District Development Officer (DDO) to submit a detailed report on the steps taken by authorities to clear the Gauchar land.",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(732, 420, 732, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 418, 1050, 1094,
    text="During the hearing of the PIL concerning illegal encroachments on Gauchar and Gamtal land in Antrol village of Vav-Tharad, the petitioner submitted that unauthorized kaccha and pucca houses have been built across village Gamtal and cattle-grazing pasture lands. Furthermore, commercial structures have been erected right inside the local primary school campus and shops have been directly let out on rent. Thus, in flagrant violation of statutory rules and legal provisions, public pasture land, village site land and even school premises have been exploited for commercial gain.\nThe petitioner pointed out that repeated written representations had been submitted to the village Sarpanch, Talati, Taluka Development Officer, District Development Officer and the Banaskantha District Collector",
    target_lines=21,
    first_indent_pt=9.0,
)
draw_line(1064, 420, 1064, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 418, 1382, 1094,
    text="demanding stern action, but complete administrative inaction forced the petitioner to approach the Gujarat High Court. Seeking immediate directions to state authorities to demolish unauthorized constructions and restore the Gamtal and Gauchar pasture lands of Antrol village, the petitioner urged the court to intervene. Taking note of the submissions, the High Court directed the local District Development Officer to verify whether illegal encroachments exist on the Gauchar land of Antrol village as alleged, and if so, to place on record by the next date of hearing what concrete steps have been taken by local authorities to remove them. The High Court scheduled the next hearing for October 30.",
    target_lines=21,
    first_indent_pt=0.0,
)
draw_line(1396, 198, 1396, 1096, swatch="[Black]", weight_pt=0.75)

# ==============================================================================
# 3. STORY 2: GUJARAT POWER CRISIS CONTINUATION (COLS 5-6 TOP)
# ==============================================================================
print("Building Story 2 (Gujarat Power Crisis Continuation, Cols 5-6 Top)...")
place_exact_display_lines(
    1412, 200, 1718, 294,
    lines=["Power Crisis in Gujarat", "(Continued from Last Page)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1412, 300, 1718, 548,
    text="has erupted across the state. Crucially, to mask the acute power shortage, the government is now hiding behind English jargon like 'load shedding' and 'staggering holiday'. Reports indicate that industries in Rajkot, Jamnagar, Junagadh, Bhavnagar and Surat are being pressured to shut down operations for 4 to 8 hours once a week.",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(1731, 200, 1731, 548, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 200, 2052, 548,
    text="The Diwali and New Year festive season represents the peak annual earning window for traders and manufacturers. How can factories maintain production without electricity? Unscheduled power cuts threaten to trigger order cancellations worth crores of rupees, compounding the distress of small industrialists and raising fears that lakhs of workers could lose their livelihoods right before Diwali.",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_box(1412, 556, 2052, 602, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 560, 2046, 598,
    lines=["Power Cuts Hit Villages While Kevadia Colony Glows With Festive Lights"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 608, 2052, 822,
    text="As a severe power crisis looms over Gujarat, surging electricity demand has forced the state government to seek emergency central allocations. While the state administration has appealed to citizens to conserve electricity, the government itself continues to squander massive power on official extravaganzas. With grand preparations underway once again for the Ekta Parade celebrations at Kevadia Colony, farmer leaders have questioned why a government preaching austerity to rural citizens refuses to curb lavish electricity consumption at state functions.",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_box(1412, 828, 2052, 874, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 832, 2046, 870,
    lines=["After Power Shortage, Severe Water Crisis Looms Over Saurashtra"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 880, 2052, 1096,
    text="Compounding the electricity crisis, an acute drinking water shortage now threatens Rajkot and the entire Saurashtra region. Following a weak monsoon, reservoirs and canals lie nearly empty, and even the much-publicized 'SAUNI Yojana' pipelines are running dry. If water levels are already critical at the onset of winter, summer could bring severe scarcity. With Rabi sowing underway and Diwali days away, farmers face the twin blows of power cuts and water scarcity.",
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(746, 1100, 2052, 1100, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 4. OBITUARIES & PUBLIC NOTICES — 100% EDITABLE ENGLISH TEXT & .WEBP PHOTOS
# ==============================================================================
print("Building Page 6 Obituaries & Public Notices (100% Editable English Text)...")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=50):
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
    draw_line(x_mid, y1_px + 10, x_mid, y2_px - 10, swatch="[Black]", weight_pt=0.75)
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


# --- OBITUARY 1: B.K. (Col 1 Top: 82..392, 198..912) ---
draw_box(82, 198, 392, 912, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(86, 202, 388, 292, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    90, 206, 384, 288,
    lines=["Generous at Heart & Healer of Every Worry,", "B.K.", "Will Forever Live On in Our Memories."],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_png(92, 296, 374, 518, "obit1_bk_photo.png")
place_exact_display_lines(
    90, 522, 384, 548,
    lines=["Journey - 04/11/59 to 18/10/26"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    90, 554, 384, 756,
    text=(
        "Well-read and deeply wise at heart!\n"
        "Always ready to help everyone in need,\n"
        "his noble and caring personality\n"
        "will never be forgotten.\n"
        "“Spreading showers of laughter and\n"
        "lighting up every gathering of friends”\n"
        "Heartfelt tributes to the memory of B.K."
    ),
    target_lines=7,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
draw_line(92, 760, 382, 760, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    90, 764, 384, 870,
    text=(
        "Nrupesh Shah, Mayur Shah,\n"
        "Yogesh Shah, Kamal Satiya,\n"
        "Jigar Shah, Saurabh Jhaveri,\n"
        "Utpal Shah, Late Saurin Sheth."
    ),
    target_lines=4,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
draw_box(86, 874, 388, 908, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    90, 878, 384, 904,
    lines=["The Entire Chaos Family."],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)

# --- OBITUARY 2: ANAVIL DEMISE (Cols 1-2: 82..718, 924..1284) ---
draw_box(82, 924, 718, 1284, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(96, 934, 292, 1136, "obit2_vinodbhai_photo.png")
draw_box(300, 932, 710, 976, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    308, 936, 702, 972,
    lines=["ANAVIL SAD DEMISE"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    300, 980, 710, 1052,
    text="With profound grief we inform that our beloved kinsman Vinodbhai Hariprasad Desai passed away on Sunday, October 18. God's will is supreme.",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(300, 1056, 710, 1134, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    306, 1060, 704, 1130,
    lines=[
        "Prayer Meeting will be held on Wednesday, October 21, 2026",
        "at Vasant Wadi, Near Giraffe Circle, Behind Balvatika, Maninagar",
        "between 9:00 AM and 11:00 AM."
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 1140, 708, 1280,
    text=(
        "In Grief: Nitaben (Nilaben) Vinodbhai Desai (Wife)\n"
        "Rahul Vinodbhai Desai (Son)    Hemantbhai Hariprasad Desai (Brother)\n"
        "Hiral Rahul Desai (Daughter-in-law)    Girish Hariprasad Desai (Brother)\n"
        "Alay Vinodbhai Desai (Son)    Late Mukesh Hariprasad Desai (Brother)\n"
        "Shweta Alay Desai (Daughter-in-law)    Sujal (Grandson), Pruthal (Granddaughter)\n"
        "Hariprasad Gandabhai Desai Family (Khara Abrama)"
    ),
    target_lines=6,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 3: KRUNAL AJITKUMAR CHOKSI (Cols 1-2: 82..718, 1296..1654) ---
draw_box(82, 1296, 718, 1654, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(86, 1300, 250, 1560, "obit3_krunal_photo.png")
draw_box(254, 1300, 714, 1330, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    260, 1302, 708, 1328,
    lines=["SAD DEMISE"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    256, 1334, 712, 1444,
    text=(
        "My beloved son Krunal Ajitkumar Choksi\n"
        "sadly passed away on Wednesday, 07/10/2026.\n"
        "The Prayer Meeting (Besna) will be held on Tuesday, 20/10/2026\n"
        "from 9:30 AM to 11:30 AM at the venue below."
    ),
    target_lines=4,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
draw_box(254, 1448, 714, 1504, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    260, 1452, 708, 1500,
    lines=[
        "Venue: Ground Floor, Chandramauleshwar Hall,",
        "Rangsagar Road, Narayan Nagar, Paldi, Ahmedabad"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    256, 1508, 712, 1558,
    lines=[
        "Ajitkumar Natwarlal Choksi",
        "Veenaben Ajitkumar Choksi"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    90, 1564, 710, 1648,
    text=(
        "Dhara Palak Shah | Viyeta Alap Shah | Sweety Krunal Choksi (Wife)\n"
        "Palak Nileshbhai Shah | Alap Kirtibhai Shah | Sara Krunal Choksi (Daughter)\n"
        "(Sister & Brother-in-law) | (Sister & Brother-in-law) | Clara Krunal Choksi (Daughter)"
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 4: LATE SITABA GIRDHARLAL PATEL (Cols 1-2: 82..718, 1666..2236) ---
draw_box(82, 1666, 718, 2236, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(210, 1668, 590, 1712, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    220, 1672, 580, 1708,
    lines=["SAD DEMISE"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_png(306, 1720, 495, 1952, "obit4_sitaba_photo.png")
place_exact_body_column(
    90, 1958, 710, 2036,
    text=(
        "Our revered mother Late Sitaba Girdharlal Patel left for heavenly abode\n"
        "on Sunday, 18-10-2026. As per the wishes of the departed soul, Besna and Laukik rituals\n"
        "will not be held. We gratefully acknowledge your love, prayers and condolences."
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    140, 2040, 660, 2070,
    lines=["In Grief: Late Girdharlal Vitthaldas Patel"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 2074, 392, 2180,
    text=(
        "Manubhai Girdharlal Patel\n"
        "Dilipbhai Girdharlal Patel\n"
        "Jitesh Manubhai Patel\n"
        "Ankit Manubhai Patel"
    ),
    target_lines=4,
    font_style="Bold",
    align="left",
    first_indent_pt=0.0,
)
draw_line(400, 2074, 400, 2180, swatch="[Black]", weight_pt=0.85)
place_exact_body_column(
    408, 2074, 708, 2180,
    text=(
        "Samir Dilipbhai Patel\n"
        "Roy Jitesh Patel\n"
        "Veenaben Chandulal Patel\n"
        "Hasumatiben Dineshkumar Patel"
    ),
    target_lines=4,
    font_style="Bold",
    align="left",
    first_indent_pt=0.0,
)
draw_box(84, 2184, 716, 2234, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    92, 2188, 708, 2230,
    lines=[
        "And the Entire Vitthaldas Ranchhoddas Patel Family",
        "Gulab Park, S.T. Road, Siddhpur"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)

# --- COLS 1-2 PUBLIC NOTICES (2 Notices: y=2254..2998 and y=3014..3792) ---
place_public_notice_2col(
    82, 2254, 718, 2998,
    left_text=(
        "Mouje - Jaspur\n"
        "In the residential plotting scheme known as Shilps Green Agro Owners Association (Shilpgram-1) situate upon non-agricultural land bearing Block No. 683 etc. of Mouje Village Jaspur, Taluka Kalol, Registration Sub-District Kalol, District Gandhinagar, open plots in Sector No. 16 bearing (A) Private Sub-Plot No. 16/J admeasuring 892 sq.mtrs. (732 sq.mtrs. net plot area) and (B) Private Sub-Plot No. 16/K admeasuring 892 sq.mtrs. (732 sq.mtrs. net plot area) together with undivided share in internal roads and common plot are stated to be in the independent ownership, possession and enjoyment of Kalpan Shankarlal Shah, free from all encumbrances and legal disputes, who has requested our Title Clearance Opinion regarding the said"
    ),
    right_text=(
        "property. If any person has any encumbrance, charge, lien, banakhat right, possession right or claim/share in the said property, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below; failing which it shall be deemed that no person has any right in the said property, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Clearance Opinion Certificate and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=22,
    right_lines=24,
)

place_public_notice_2col(
    82, 3014, 718, 3792,
    left_text=(
        "Out of land admeasuring 639.86 sq.yds. (535 sq.mtrs.) bearing Survey Nos. 490/2, 491/2 and 492/2, T.P. Scheme No. 55, Final Plot No. 83/5 (Old F.P. No. 158) of Mouje Village Isanpur, Taluka Maninagar, Registration Sub-District Ahmedabad-5 (Narol), District Ahmedabad, property comprising 393.86 sq.yds. (329.31 sq.mtrs.) land together with cellar, ground floor and first floor construction admeasuring 394.60 sq.mtrs., open land and all ancillary rights from sky to earth has been stated by our client Parmar Shaileshbhai Ramnikbhai to be in his independent ownership, possession and enjoyment, and he has requested a"
    ),
    right_text=(
        "Title Clearance Certificate from us. If any bank, person, institution, firm or company has any claim, right, title, interest, share, charge or lien over the said property, they must notify the undersigned Advocate in writing with documentary proof within 7 (seven) days at the address below; failing which, upon expiry of the period, it shall be deemed that no person has any right, title, interest or share, or if any existed, the same has been waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained.\n"
        "Ahmedabad. Date: 17/10/2026\n"
        "Paresh Sureshbhai Adhiya\n"
        "Advocate & Notary\n"
        "901, Maple Trade Centre, Near Surdhara Circle, SAL Hospital Road, Thaltej, Ahmedabad-380054.\n"
        "(Mob.) 9898458201"
    ),
    left_lines=23,
    right_lines=25,
)

# --- COLS 3-4 PUBLIC NOTICES (4 Notices: y=1082..1684, 1698..2354, 2368..3054, 3076..3792) ---
place_public_notice_2col(
    746, 1082, 1382, 1684,
    left_text=(
        "Notice is hereby given to the general public that agricultural land bearing New Survey/Block No. 238 (Old Survey/Block No. 93) admeasuring 41895 sq.mtrs. in total of Mouje Village Durga, Taluka & Sub-District Bavla, Registration District Ahmedabad, is stated by Natwarbhai Ukabhai and Govindbhai Ukabhai to be in their absolute joint ownership, possession and enjoyment, free from all encumbrances, and they have requested a certificate of clear and marketable title for the said land from us. If any person has any claim, right, title, interest, share or charge over the said land, they must notify us in writing with"
    ),
    right_text=(
        "supporting documentary proof within 7 (seven) days from the publication of this notice at the address given below; failing which it shall be deemed that no other person has any claim, right, title, interest, share or encumbrance over the said land, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection of any kind shall be entertained.\n"
        "Date: 20/10/2026\n"
        "Kaushik G. Patel\n"
        "(Advocate & Notary)\n"
        "(B.Sc., LL.B.)\n"
        "Office: 12, 2nd Floor, J.B.R. Arcade, Beside R.K. Royal Hall, Science City Road, Sola, Ahmedabad-380060.\n"
        "Mob. No. 9824678769"
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    746, 1698, 1382, 2354,
    left_text=(
        "Notice is hereby given to the general public that non-agricultural open residential land bearing Sub-Plot No. A/84 in Part-A of Aarohi Plots Owners Association, admeasuring 400 sq.yds. (334.46 sq.mtrs.), situate upon non-agricultural land bearing Block No. 789 of Mouje Village Ghuma, Taluka Ghatlodia, Sub-District Ahmedabad-9 (Bopal), Registration District Ahmedabad, is stated to be in the independent ownership, possession and enjoyment of Rameshbhai Madhavlal Patel, who has requested a clear and marketable Title Clearance Certificate from us. If any person, bank, firm or institution has any claim, right, title, interest or share"
    ),
    right_text=(
        "or any other encumbrance over the said property, they must send written notice with certified copies of documentary proof by Registered Post A.D. within 7 (seven) days from publication hereof at the address below. (Objections without proof will not be considered.) Failing which, it shall be deemed that no other person has any claim, right, title, interest, share or charge over the said property, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate. Please take note.\n"
        "Date: 19/10/2026\n"
        "Manoj K. Sidhav, Advocate\n"
        "301-302, Elite, Opp. Shapath Hexa, Beside Sola Overbridge, S.G. Highway, Sola, Ahmedabad-380060.\n"
        "Office Phone No. 079-35856314"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 2368, 1382, 3054,
    left_text=(
        "Mouje - Jaspur\n"
        "In the residential plotting scheme known as Shilps Green Agro Owners Association (Shilpgram-1) situate upon non-agricultural land bearing Block No. 606/3 etc. of Mouje Village Jaspur, Taluka Kalol, Registration Sub-District Kalol, District Gandhinagar, open plot property bearing Private Sub-Plot No. 1/J admeasuring 2589 sq.mtrs. together with undivided rights in internal roads and common plot is stated to be in the independent ownership, possession and enjoyment of Vatsal Suryakant Patel, free from all encumbrances and legal disputes, who has requested our Title Clearance Opinion. If any person has any encumbrance, charge, lien, banakhat right,"
    ),
    right_text=(
        "possession right or claim/share in the said property, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below; failing which it shall be deemed that no person has any right in the said property, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Clearance Opinion Certificate and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 3076, 1382, 3792,
    left_text=(
        "Mouje - Vansajada (Dhe.)\n"
        "In the scheme known as 'The Other Side' comprising internal roads, common plot and clubhouse upon non-agricultural land bearing Re-Survey Block Nos. 178 and 179 (Old Block Nos. 70 and 71) etc. of Mouje Village Vansajada (Dhe.), Taluka Kalol, Registration Sub-District Kalol, District Gandhinagar, property bearing Plot/Villa No. C/296 admeasuring 354 sq.mtrs. plot area with 132 sq.mtrs. carpet area construction standing thereon is stated to be in the independent ownership, possession and enjoyment of Shailesh Ramniklal Mehta, free from all encumbrances and legal disputes, who has requested our Title Clearance Opinion. If any person has any encumbrance, charge,"
    ),
    right_text=(
        "lien, banakhat right, possession right or claim/share in the said property, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below; failing which it shall be deemed that no person has any right in the said property, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Clearance Opinion Certificate and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=21,
    right_lines=23,
)

# --- COLS 5-6 PUBLIC NOTICES (4 Notices: y=1162..1794, 1810..2414, 2434..3090, 3104..3792) ---
place_public_notice_2col(
    1412, 1162, 2052, 1794,
    left_text=(
        "In the residential building known as 'SPARSH' situate upon non-agricultural land bearing Block No. 658 (Old Survey No. 522/4), Draft T.P. Scheme No. 3 (Ghuma), Final Plot No. 119 of Mouje Ghuma, Taluka Ghatlodia, District Ahmedabad, property bearing Block 'A', Third Floor, Flat No. 304 admeasuring approx. 80.03 sq.mtrs. (carpet area) together with approx. 33.37 sq.mtrs. undivided land share is owned by Brijpalsinh Bhupatsinh Vaghrola, Dattakunvarba Brijpalsinh Vaghrola, Bhupatsinh Vaghrola and Kanchanben Bhupatsinh Vaghrola, who have stated the property is clear, marketable and free from all encumbrances and requested a Title Clearance Certificate. Over the said property,"
    ),
    right_text=(
        "if any bank, institution or person has any right, claim, share, mortgage, charge or interest, they must notify us in writing with documentary proof within 7 (seven) days from publication hereof at the address below; failing which, upon expiry of the period, it shall be deemed that no person has any encumbrance, right, claim or title over the said property, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained. Ahmedabad.\n"
        "Date: 19/10/2026\n"
        "Satish H. Pujara\n"
        "(Advocate & Notary)\n"
        "F.F./5, Hare-Krishna Complex, Opp. SBI Bank, Bopal, Ahmedabad.\n"
        "Mob. No. 9033033890"
    ),
    left_lines=19,
    right_lines=21,
)

place_public_notice_2col(
    1412, 1810, 2052, 2414,
    left_text=(
        "Old tenure agricultural land bearing Re-Survey/Block No. 876 (Old Survey No. 498) under Khata No. 1515 admeasuring 0-85-64 Hectare-Are-Sq.Mtrs., assessment Rs. 4.50, of Mouje Harsoli, Taluka Dahegam, Registration Sub-District Dahegam, District Gandhinagar, is stated by Rameshbhai Ravjibhai Dobariya to be in his independent ownership, possession and enjoyment, free from all encumbrances, with clear and marketable title, and having agreed to sell the same to our client, he has requested a Title Clearance and Marketability Certificate from us. If any person or institution has"
    ),
    right_text=(
        "any right, title, interest, share, claim, charge or objection in the said land, they must notify us in writing with certified proof by Regd. A.D. within 7 (seven) days (objections without certified proof will not be considered); failing which it shall be deemed that no person or institution has any right, title, interest, share, claim, charge or objection, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained.\n"
        "Dinesh B. Patel, Advocate\n"
        "Office: 403 & 404, Block-C, 4th Floor, Revati Plaza, Nr. Bhakti Circle, Off S.P. Ring Road, New Nikol, Ahmedabad - 380049.\n"
        "Mob. No. 98790 57290."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    1412, 2434, 2052, 3090,
    left_text=(
        "Mouje - Shertha\n"
        "Agricultural land bearing Re-Survey Block No. 858 (Old Block No. 1550) admeasuring Hectare-Are-Sq.Mtrs. 0-92-75 of Mouje Village Shertha, Taluka Gandhinagar, Registration Sub-District Gandhinagar (Zone-1), District Gandhinagar, is stated to be in the joint ownership, possession and enjoyment of Ramiben alias Ramilaben D/o Bhikhaji & W/o Rajnikant Thakor and Lasiben alias Lilaben D/o Bhikhaji & W/o Bhodaji Thakor, free from all encumbrances and legal disputes, who have requested our Title Clearance Opinion. If any person has any encumbrance, charge, tenancy right, ganot right, easement right or any other possession"
    ),
    right_text=(
        "right or claim/share in the said land, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below; failing which it shall be deemed that no person has any right in the said land, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Clearance Opinion Certificate and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    1412, 3104, 2052, 3792,
    left_text=(
        "Mouje - Fuletra\n"
        "Out of agricultural land bearing Re-Survey No. 1196 (Old Survey No. 993) admeasuring Hectare-Are-Sq.Mtrs. 0-27-67 of Mouje Village Fuletra, Taluka Kadi, Registration Sub-District Kadi, District Mehsana, the southern half admeasuring Hectare-Are-Sq.Mtrs. 0-13-83.50 is stated to be in the joint ownership, possession and enjoyment of (1) Rabari Shantaben Wd/o Nathabhai, (2) Rabari Vishnubhai Nathabhai, (3) Rabari Vikrambhai Nathabhai, and (4) Rabari Sitaben Nathabhai, free from all encumbrances and legal disputes, who have requested our Title Clearance Opinion. If any person has any encumbrance, charge, tenancy right, ganot right, easement right or any other"
    ),
    right_text=(
        "possession right or claim/share in the said land, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below; failing which it shall be deemed that no person has any right in the said land, or if any existed, the same stands waived, and upon expiry of the period we shall issue the Title Clearance Opinion Certificate and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=20,
    right_lines=22,
)

# --- COLS 7-8 PUBLIC NOTICES (5 Notices: y=202..658, 680..1282, 1312..1968, 1988..2850, 2868..3792) ---
place_public_notice_2col(
    2076, 202, 2715, 658,
    left_text=(
        "Out of agricultural land bearing Survey/Block No. 721 (Old Survey/Block No. 1178 prior to promulgation) admeasuring Hectare-Are-Sq.Mtrs. 2-54-87 of Mouje Bareja, Taluka Daskroi, District Ahmedabad, the northern portion admeasuring Hectare-Are-Sq.Mtrs. 0-94-09 of old tenure agricultural land is stated to be in the independent ownership, possession and enjoyment of Mehndiraza Arifali Noorani, who has requested a Title Clearance Certificate; therefore if any other"
    ),
    right_text=(
        "person has any claim, right, title, interest or share in the said land, they must notify us in writing with documentary proof by Regd. A.D. within 7 days at the address below, after which no objection or dispute shall be entertained and any such claim or right shall be deemed waived and a Title Clearance Certificate shall be issued.\n"
        "Nilesh N. Patel, Associates\n"
        "Paresha B. Patel (Advocate)\n"
        "507, 5th Floor, Shivalik Satyamev, S.P. Ring Road, Ambli, Ahmedabad. Mob. 9054684159"
    ),
    left_lines=14,
    right_lines=16,
)

place_public_notice_2col(
    2076, 680, 2715, 1282,
    left_text=(
        "Old tenure agricultural land bearing Re-Survey/Block No. 879 (Old Survey No. 493) under Khata No. 1514 admeasuring 0-64-60 Hectare-Are-Sq.Mtrs., assessment Rs. 3.25, of Mouje Harsoli, Taluka Dahegam, Registration Sub-District Dahegam, District Gandhinagar, is stated by Rameshbhai Ravjibhai Dobariya to be in his independent ownership, possession and enjoyment, free from all encumbrances, with clear and marketable title, and having agreed to sell the same to our client, he has requested a Title Clearance and Marketability Certificate from us. If any person or institution has"
    ),
    right_text=(
        "any right, title, interest, share, claim, charge or objection in the said land, they must notify us in writing with certified proof by Regd. A.D. within 7 (seven) days (objections without certified proof will not be considered); failing which it shall be deemed that no person or institution has any right, title, interest, share, claim, charge or objection, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained.\n"
        "Dinesh B. Patel, Advocate\n"
        "Office: 403 & 404, Block-C, 4th Floor, Revati Plaza, Nr. Bhakti Circle, Off S.P. Ring Road, New Nikol, Ahmedabad - 380049.\n"
        "Mob. No. 98790 57290."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    2076, 1312, 2715, 1968,
    left_text=(
        "Mouje - Lhor\n"
        "Non-agricultural land bearing City Survey No. NA754 admeasuring 3164 sq.mtrs., allotted upon inclusion of Re-Survey No. 754 (Old Survey No. 451) in City Survey Ward: Lhor (N.A.) of Mouje Village Lhor, Taluka Kadi, Registration Sub-District Kadi, District Mehsana, is stated to be in the independent ownership, possession and enjoyment of Dakshini Romi Shailesh, free from all encumbrances and legal disputes, who has requested our Title Clearance Opinion. If any person has any encumbrance, charge, banakhat right, development right or any other possession right or claim/share in the said land, they must notify us at the address below within"
    ),
    right_text=(
        "7 days in writing with documentary proof by Regd. A.D.; failing which it shall be deemed that no person has any right in the said land, or if any existed, the same stands waived, and upon expiry of the period a Title Clearance Opinion Certificate shall be issued and no objection or dispute shall be entertained thereafter.\n"
        "Date: 20-10-2026\n"
        "Manish Kanubhai Patel, Advocate,\n"
        "Chirag Dashrathbhai Patel, Advocate,\n"
        "Amit Dashrathbhai Patel, Advocate,\n"
        "Het Shankarbhai Patel, Advocate,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "Addr.: A/202, 2nd Floor, S.G. Business Hub, Nr. Gota Overbridge, S.G. Highway, Gota, Ahmedabad.\n"
        "Mob. 8879344333"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    2076, 1988, 2715, 2850,
    left_text=(
        "Notice is hereby given to the general public that out of land bearing Survey No. 671 (Old Survey/Block No. 877/2 Paiki) admeasuring 16294 sq.mtrs. of Mouje Village Rajoda, Taluka & Registration Sub-District Bavla, District Ahmedabad, after deducting 530 sq.mtrs. acquired for N.H. No. 8-A, the remaining 15764 sq.mtrs. N.A. permitted land is stated by Shilpaben Rakeshbhai Shah, residing at 20, 'Paras', Vidyanagar Society, Usmanpura, Ahmedabad, to be in her absolute independent ownership, direct possession and enjoyment, free from all encumbrances, and having agreed to sell the same to our client, she has requested a Title Clearance Certificate from us. Therefore, any person, firm, bank, financial institution or entity claiming by sale, inheritance, gift, license, possession, mortgage, lien, charge, maintenance, easement, exchange, developer or financier or"
    ),
    right_text=(
        "under any banakhat agreement, power of attorney, possession agreement, settlement, decree, court proceeding or as family member/heir or otherwise having any right, claim or title over the said land must notify us in writing with certified documentary proof by Speed Post within 7 (seven) days from publication hereof at the address below; failing which it shall be deemed that no person has any claim, right or share in the said land, or if any existed, the same stands WAIVED, and upon expiry of the period a Title Clearance Certificate shall be issued and our client shall complete the sale deed formalities, after which no objection shall be entertained.\n"
        "Date: 18/10/2026 | File No. 24009\n"
        "B R PATEL & Co.\n"
        "Advocates, Solicitors & Corporate Attorneys\n"
        "15, Dolly Apartment, Ambawadi Circle, Ahmedabad-380006.\n"
        "Phone: 26466400, 26466401"
    ),
    left_lines=25,
    right_lines=27,
)

place_public_notice_2col(
    2076, 2868, 2715, 3792,
    left_text=(
        "In the sim of Mouje: Shahwadi, Taluka Vatva, District Ahmedabad: (1) Survey/Block No. 255/1, Khata No. 241 admeasuring 0-39-46 Hectare-Are-Sq.Mtrs. owned and possessed by Mrudulaben Dipakkumar Sheth; (2) Survey/Block No. 268, Khata No. 243 admeasuring 0-61-71 Hectare-Are-Sq.Mtrs. owned and possessed by Kirtikumar alias Kiritbhai Jamnadas Sheth; (3) Survey/Block No. 277, Khata No. 242 admeasuring 0-42-49 Hectare-Are-Sq.Mtrs. owned and possessed by Dipakkumar Jamnadas Sheth; and (4) 825 sq.mtrs. out of Survey/Block No. 278/1, Khata No. 170 admeasuring 0-20-23 Hectare-Are-Sq.Mtrs. owned and possessed by Rajeshriben Kirtikumar Sheth—aggregating 1-51-91 Hectare-Are-Sq.Mtrs. allotted Joint Final Plot No. 77/1+86+93+94 in T.P. Scheme No. 125 (Saijpur-Gopalpur-Shahwadi)—"
    ),
    right_text=(
        "the N.A. land receivable therefrom is stated to be free from all third-party ownership rights, shares, inheritance claims or encumbrances, and for the purpose of selling the same to our client, our opinion on clear title has been requested. If any person has any inheritance right, share, claim, charge, banakhat right, lien, attachment or interest over any of the said lands, they must notify us in writing with true copies of documentary proof within 7 (seven) days from publication hereof at the address below; failing which any such rights or claims shall be deemed voluntarily waived, a Title Certificate shall be issued upon expiry of the period, and the sale deed formalities shall be completed.\n"
        "Date: 20/10/2026\n"
        "Nimish V. Desai, Advocate,\n"
        "V.D. DESAI & CO.\n"
        "212, 'Aakashrath', 2nd Floor, Opp. National Handloom, Law Garden, Ahmedabad\n"
        "Phone: (Mob) 99982 17354"
    ),
    left_lines=27,
    right_lines=29,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_06_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_06_English_SameToSame.dns"
    png_path = target_dir / "Page_06_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_06_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_06_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_06_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_06_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
