from gs_english_running_header import build_english_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 9 BUILDER FOR INDIAN POST (GUJARAT SAMACHAR ENGLISH)
===================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable English Text ('Georgia' & 'Times New Roman')
  across all Page 9 National/International Stories, Page 1 Continuations,
  and 8 Bottom Public Notices (PUBLIC NOTICE)!
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
ASSETS_DIR = DIR_SMAE / "Page_09_Assets"

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
        "title": "INDIAN POST (Gujarat Samachar English) — Page 09 (100% Same-to-Same Editable English)"
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
    hscale: float = 0.87,
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
        if pt > lead_pt * 1.06:
            continue
        for hs100 in (90, 87, 84, 81, 78):
            hs = round(hs100 / 100.0, 2)
            cmds = []
            b_cursor = 0
            for p_text, p_style, p_align, p_indent in paras:
                b_len = utf8_len(p_text)
                b_start = b_cursor
                b_end = b_cursor + b_len
                b_cursor = b_end + 1
                p_sz = round(pt * 1.08, 1) if p_style == "Subhead" else (round(pt * 1.32, 1) if p_style == "Header" else pt)
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
# 1. RUNNING HEADER & VERTICAL GRID DIVIDERS
# ==============================================================================
print("Placing Page 9 English Running Header & Dividers...")
build_english_running_header(9, draw_box, place_exact_display_lines)

draw_line(1064, 198, 1064, 2292, weight_pt=0.85)  # Between Col 3 and Col 4
draw_line(1731, 198, 1731, 1574, weight_pt=0.85)  # Between Col 5 and Col 6 (top)
draw_line(2063, 1574, 2063, 2265, weight_pt=0.85)  # Between Col 6 and Col 7 (mid)

draw_line(746, 723, 1051, 723, weight_pt=0.85)    # Col 3 divider 1
draw_line(746, 1194, 1051, 1194, weight_pt=0.85)  # Col 3 divider 2
draw_line(746, 1478, 1051, 1478, weight_pt=0.85)  # Col 3 divider 3

draw_line(1078, 1099, 1718, 1099, weight_pt=0.85)  # Cols 4-5 divider 1
draw_line(1078, 1574, 2050, 1574, weight_pt=0.85)  # Cols 4-6 divider 2
draw_line(2076, 1130, 2712, 1130, weight_pt=0.85)  # Cols 7-8 divider

# ==============================================================================
# 2. COLS 1-3: TALK OF DELHI (CONTINUED FROM PAGE 1) + OTHER CONTINUATIONS
# ==============================================================================
print("Building Page 1 Continuations in Cols 1-3...")

place_mixed_paras_column(
    82, 200, 388, 2288,
    paras=[
        ("Talk of Delhi", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("alleging that certain opposition leaders and anti-India elements are colluding to incite the country's youth and foment unrest.", "Regular", "leftJustified", 0.0),
        ("CJP Leaders Lodged in Tihar High-Security Ward", "Subhead", "center", 0.0),
        ("Ashutosh Ranka and Saurav Das of the Krodhroy Janata Party (CJP), who were arrested while attempting to enter Jantar Mantar without permission, have been lodged in the high-security ward of Delhi's Tihar Jail. Prison authorities have deployed additional security personnel outside their cells and ensured that they do not mingle with other inmates during daytime hours. According to prison records, Ranka has been assigned inmate number 1784 and Das inmate number 3752. Initially both were kept in Jail No. 2, before Ranka was shifted to Jail No. 4. Compared to other blocks of the prison complex, the high-security ward houses far fewer inmates and remains under 24-hour surveillance.", "Regular", "leftJustified", 9.0),
        ("‘Supporting 2023 EC Appointment Law Was a Mistake’", "Subhead", "center", 0.0),
        ("YSRCP chief and former Andhra Pradesh Chief Minister Y.S. Jagan Mohan Reddy has admitted that his party made a mistake by supporting the 2023 law governing the appointment of the Chief Election Commissioner and Election Commissioners. Calling for immediate reforms to ensure fair elections, Reddy stated that the ruling party should not hold a majority say in appointing the umpires of democracy. Under the earlier Supreme Court-mandated mechanism, Election Commissioners were selected by a panel comprising the Prime Minister, the Leader of the Opposition, and the Chief Justice of India. An examiner cannot be appointed by a student; unless an impartial body selects Election Commissioners, the Poll Panel will continue to face credibility questions.", "Regular", "leftJustified", 9.0),
        ("ABVP Stages Rally in Lucknow Supporting CEC Gyanesh Kumar", "Subhead", "center", 0.0),
        ("While protests demanding the resignation of CEC Gyanesh Kumar are taking place in Delhi and several states, the BJP's student wing Akhil Bharatiya Vidyarthi Parishad (ABVP) staged a rally in Lucknow in support of Gyanesh Kumar.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

place_mixed_paras_column(
    414, 200, 720, 2288,
    paras=[
        ("weakens democratic institutions. Under its 'Stop Anarchy, Embrace Democracy' campaign, the ABVP organized a 'Chhatra Hunkar' demonstration near Gate No. 3 of Lucknow University. Hundreds of ABVP activists gathered at the campus gate, raising slogans against the Congress party and calling activist Abhishek Deepak and YouTuber Dhruv Rathee anti-national.", "Regular", "leftJustified", 0.0),
        ("Jubin Nautiyal's Father Joins Congress in Uttarakhand", "Subhead", "center", 0.0),
        ("Former Dehradun Zila Panchayat Chairman Ram Sharan Nautiyal—father of popular playback singer Jubin Nautiyal—has formally joined the Congress party days after resigning from the BJP. Speculation about his return to the Congress had been rife ever since he quit the ruling party. AICC National General Secretary Kumari Selja inducted him into the party. Ram Sharan Nautiyal began his political career in the Congress and previously served as Vice-President of the Uttarakhand Pradesh Congress Committee before joining the BJP in 2014. He contested the 2022 Uttarakhand Assembly election on a BJP ticket from Chakrata but lost. Speaking after his induction, Nautiyal said, 'I cannot say what role the party envisions for me, but my heart was never at peace outside the Congress, which is why I have returned home.'", "Regular", "leftJustified", 9.0),
        ("RJD MP Sudhakar Singh Seeks Speaker's Intervention Over IPS Officer's Notice", "Subhead", "center", 0.0),
        ("The controversy over the alleged fake encounter of Bharat Bhushan Tiwari in Baulauti village of Bihar's Bhojpur district has now reached Parliament. RJD MP Sudhakar Singh, who had questioned the police version of the encounter, has written to Lok Sabha Speaker Om Birla seeking his intervention after senior Bihar IPS officer Kundan Krishnan served him a legal defamation notice. Singh urged the Speaker to initiate an inquiry and refer the matter to the Parliamentary Committee of Privileges, noting that the IPS officer's private legal notice demanded a public apology and Rs 5 crore in damages from an elected Member of Parliament.", "Regular", "leftJustified", 9.0),
        ("Who Is Gangster Anil Pandit Behind Tiger Shroff Firing?", "Subhead", "center", 0.0),
        ("The name of US-based gangster Anil Pandit has surfaced once again after shots were fired at actor Tiger Shroff's car in Mumbai's Khar area on Sunday evening. In a video message circulated after the incident, Anil Pandit and Harman Sandhu claimed", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

# Col 3 Top: continuation of Talk of Delhi (y=200..716)
place_exact_body_column(
    746, 200, 1051, 716,
    text=(
        "responsibility for the firing. In the audio clip, Pandit also issued threats to actor Salman Khan and his family. Anil Pandit's name had previously surfaced during a brazen daylight firing outside a money exchange office in Panipat, Haryana, in March this year. Associates linked to the Lawrence Bishnoi gang had claimed responsibility on social media at the time, naming US-based operatives Anil Pandit and Randeep Malik, who had also issued extortion threats to Punjabi singer-rapper Badshah."
    ),
    target_lines=17,
    first_indent_pt=0.0,
)

# Col 3 Mid-Top: American Satellite (Continued from Page 1) (y=732..1188)
place_mixed_paras_column(
    746, 732, 1051, 1188,
    paras=[
        ("American Satellite", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("triggering an anti-satellite arms race in orbit that could pose a grave threat to global communication networks. Russia launched the Cosmos-2592 satellite in April this year, and defense analysts believe it may have been deployed to jam radar and satellite guidance systems used by Ukraine's advanced missiles and long-range drones.", "Regular", "leftJustified", 0.0),
        ("With this orbital confrontation, the Russia-Ukraine conflict has effectively extended from the ground into outer space for the first time.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)

# Col 3 Mid: Violence in France (Continued from Page 1) (y=1202..1472)
place_mixed_paras_column(
    746, 1202, 1051, 1472,
    paras=[
        ("Violence in France", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("the country. The French President has also directed national police forces to formulate a new strategy to contain urban riots after protesters set fire to roadside trash bins, bicycles, and parked vehicles across multiple French cities on Sunday night.", "Regular", "leftJustified", 0.0),
    ],
    target_lines=9,
    base_pt=10.5,
)

# Col 3 Mid-Bot: Allied Nations (Continued from Page 1) (y=1486..2288)
place_mixed_paras_column(
    746, 1486, 1051, 2288,
    paras=[
        ("Allied Nations", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("damaging 10 critical energy infrastructure facilities across Ukraine.", "Bold", "leftJustified", 0.0),
        ("The overnight barrage left more than 500,000 residents without electricity, heating, and water supply. Sixteen ballistic missiles were fired at Kyiv and its surrounding regions as Russia targeted passenger trains, shopping malls, gas stations, and supermarkets to disrupt civilian life.", "Regular", "leftJustified", 9.0),
        ("Meanwhile, prospects of trilateral peace talks involving the US, China, and Russia over the Ukraine war have been ruled out.", "Bold", "leftJustified", 9.0),
        ("Lithuanian Prime Minister Mindaugas Sinkevicius announced on Monday that security has been heightened across Lithuania following an attempted arson attack at a Starlink ground facility.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=26,
    base_pt=10.5,
)

# ==============================================================================
# 3. COLS 4-5 TOP: RISING THREAT OF CLIMATE CHANGE: SEVEN VITAL SIGNS AT RECORD LEVELS
# ==============================================================================
print("Building Climate Change Story (Cols 4-5 Top)...")
place_exact_display_lines(
    1078, 200, 1718, 250,
    lines=["Scientists Issue Stark Warning After Assessing 16 Planetary Indicators"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1078, 256, 1718, 434,
    lines=[
        "Rising Threat of Climate Change: Seven",
        "of Earth's Vital Signs Hit Record Levels"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1078, 440, 1718, 594,
    text=(
        "New Delhi, Oct 19\n"
        "According to a global assessment published in the journal BioScience on October 14, 2026, the threat of climate change is accelerating rapidly. Scientists tracked 16 planetary vital signs measuring the health of the Earth, finding that seven have reached record-breaking extremes. Surging atmospheric carbon dioxide and methane concentrations, melting glaciers, and rising sea levels underscore how human activity continues to heat the planet."
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 600, 1718, 694,
    lines=[
        "Greenhouse Gases and Melting Glaciers Deepen Alarm;",
        "Rapid Phase-Down of Fossil Fuels Imperative"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 700, 1385, 1092,
    text=(
        "The report notes that average atmospheric concentrations of carbon dioxide, methane, and nitrous oxide hit all-time highs in 2026. These heat-trapping greenhouse gases have driven global temperatures upward while pushing Greenland's ice-sheet mass and mountain glacier thickness to historic lows. Ocean heat accumulation and rising sea levels are intensifying coastal flooding, erosion, and ecological disruption.\n"
        "Scientists warn that sustained warming risks triggering irreversible"
    ),
    target_lines=13,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 700, 1718, 1092,
    text=(
        "climate tipping points where large-scale environmental shifts become self-reinforcing and impossible to reverse—though the report notes that not all tipping points have yet been crossed. On the positive side, global solar and wind power generation as well as battery storage capacity have expanded significantly, and primary tropical forest loss declined in 2025. Despite these gains, overall consumption of coal, oil, and gas has not fallen, making an accelerated transition to clean energy urgent."
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. COLS 4-5 MID: IN MANIPUR (CONTINUED FROM PAGE 1) (y=1106..1568)
# ==============================================================================
print("Building Manipur Continuation (Cols 4-5 Mid)...")
place_mixed_paras_column(
    1078, 1106, 1385, 1568,
    paras=[
        ("In Manipur", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("succumbed to his injuries on the spot, while Kshetrimayum Sushil (32) died at a private hospital.", "Regular", "leftJustified", 0.0),
        ("Three other injured villagers—N. Suraj (18), Medsanam Somendro (53), and K. Bosan (45)—are undergoing treatment. They were part of a group of 16 villagers who had gone to collect firewood in the nearby hills around 7 AM when armed militants opened fire on them, sparking", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1106, 1718, 1568,
    text=(
        "widespread outrage. As angry residents staged demonstrations outside the Chief Minister's residence, Chief Minister Y. Khemchand Singh visited the hospital to inquire after the injured villagers but declined to answer questions from reporters.\n"
        "Police fired tear-gas shells to disperse protesters marching toward the high-security zone. The bodies of the deceased were shifted to the Jawaharlal Nehru Institute of Medical Sciences (JNIMS), and markets and commercial establishments across Imphal remained shut in protest."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. COLS 4-6 MID-BOT: ON TIGER (CONTINUED FROM PAGE 1) (y=1580..2288)
# ==============================================================================
print("Building Tiger Shroff Continuation (Cols 4-6 Mid-Bot)...")
place_mixed_paras_column(
    1078, 1580, 1385, 2288,
    paras=[
        ("On Tiger", "Header", "center", 0.0),
        ("(Continued from Page 1)", "Bold", "center", 0.0),
        ("during the escape. Because Ritik Kumar alias Roshan worked as a Rapido bike rider and knew Mumbai's arterial roads well, he rode the getaway motorcycle and later booked an app-based cab from Borivali to Surat. The DCP stated that the motorcycle used by the shooter has been recovered from Andheri, though no firearms were found on the three suspects detained in Rajasthan. They are being brought to Mumbai on transit remand.", "Regular", "leftJustified", 0.0),
        ("The DCP added that Tiger Shroff had not filed any prior complaint regarding threats to his life, and the exact motive behind the firing will be established once the suspects are interrogated.", "Regular", "leftJustified", 9.0),
        ("Investigators noted that the accused switched between a motorcycle,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=23,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1580, 1718, 2260,
    text=(
        "suburban local trains, an inter-city cab, and a long-distance express train to shake off pursuing agencies. However, in a swift multi-state operation involving 20 Mumbai Crime Branch teams with technical and operational assistance from Delhi, Gujarat, and Rajasthan police forces, all three suspects were intercepted aboard a train in Kota, Rajasthan, within 15 hours of the attack.\n"
        "From Surat, the trio had boarded the Pune–Jaipur Express. Mumbai Police tracked the exact coach they were traveling in, enabling Kota Police to board the compartment and apprehend all three suspects immediately.\n"
        "Ritik had purchased the motorcycle used in the attack on September 11 without transferring ownership records. Since 2022, the vehicle had"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 1580, 2050, 2260,
    text=(
        "changed hands among four different individuals. Tracing who arranged the motorcycle and funded its purchase is expected to lead investigators to the mastermind behind the firing.\n"
        "Two of the three accused hail from the same locality and knew each other beforehand. The suspect seen wearing a cap in CCTV footage has been identified as Rehan. Police confirmed that two firearms were used to fire multiple rounds during the incident, and charges including attempt to murder have been registered. Crime Branch officials are also verifying the authenticity of social media posts claiming responsibility on behalf of the Lawrence Bishnoi gang."
    ),
    target_lines=22,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. COLS 6-8 TOP: 13 OF WORLD'S 20 MOST POLLUTED CITIES ARE IN INDIA; DELHI NOT ON LIST
# ==============================================================================
print("Building 20 Most Polluted Cities Story (Cols 6-8 Top)...")
place_exact_display_lines(
    1744, 200, 2712, 252,
    lines=["Cities From Indonesia and Malaysia Also Feature in Global Ranking"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1744, 258, 2712, 434,
    lines=[
        "13 of World's 20 Most Polluted Cities",
        "Are in India; Delhi Not on the List"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1744, 440, 2218, 556,
    text=(
        "New Delhi, Oct 19\n"
        "Indian cities dominated the global ranking of the world's most polluted urban centers on Monday, accounting for 13 of the top 20 cities recording the highest air pollution levels. Notably, Delhi—which is"
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 440, 2712, 556,
    text=(
        "frequently synonymous with severe air quality deterioration in India—was absent from the top 20 list at the time. According to data released by AQI.in on Monday, Bulandshahr in Uttar Pradesh ranked third globally with an Unhealthy US AQI reading of 198."
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 562, 2712, 652,
    lines=[
        "Real-Time Global Pollution Rankings Show Sharp",
        "Hourly Fluctuations in Delhi's Air Quality Index"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 658, 2050, 1568,
    text=(
        "Agartala in Tripura ranked fourth globally with an AQI of 181. Other Indian cities in the global top 20 included Pali in Rajasthan and Muzaffarnagar in Uttar Pradesh, both recording an AQI of 174. Burhanpur in Madhya Pradesh also logged an AQI of 174, while Rohtak in Haryana stood at 172, followed by Kota (170), Mumbai (167), Hapur (166), Hisar (165), Bikaner (165), and Bareilly (164)—placing all thirteen Indian urban centers among the world's most polluted cities.\n"
        "Several Indonesian cities occupied the top slots in the ranking. Palangkaraya in Central Kalimantan ranked first worldwide with a Very Unhealthy US AQI of 242, followed by Palembang at 207. Sampit and Jambi ranked fifth and sixth with AQI readings of 180 and 176 respectively, while Malaysia's Putrajaya, Kuala Lumpur, and Petaling Jaya also featured in the top 20. Although Delhi stayed outside the global top 20 during the daytime snapshot, its air quality worsened overnight."
    ),
    target_lines=29,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 658, 2382, 1122,
    text=(
        "According to the national capital's hourly AQI graph, Delhi's US AQI peaked at 191 on Monday morning before moderating during the afternoon, having touched a low of 126 at 5:01 PM on October 18.\n"
        "By Monday afternoon on October 19, Delhi's AQI had eased from its morning peak to around 130. Experts note that real-time rankings represent a momentary snapshot that shifts rapidly with wind speed, local emissions, and"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 658, 2712, 1122,
    text=(
        "atmospheric circulation. The AQI.in tracker uses the US Air Quality Index scale, under which readings between 151 and 200 are classified as 'Unhealthy' and values above 200 indicate 'Very Unhealthy' or 'Hazardous' pollution. Even when a city temporarily drops out of the global top 20, elevated particulate levels pose serious health risks for children, senior citizens, and patients with respiratory or cardiac ailments."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. COLS 7-8 MID: FAILURE OF SOUTHWEST MONSOON TRIGGERS WATER SCARCITY IN SOUTH INDIA
# ==============================================================================
print("Building South India Monsoon Story (Cols 7-8 Mid)...")
place_exact_display_lines(
    2076, 1136, 2712, 1184,
    lines=["Drought Declared Across Several Regions of Karnataka and Andhra Pradesh"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    underline=True,
)
place_exact_display_lines(
    2076, 1188, 2712, 1344,
    lines=[
        "Failure of Southwest Monsoon Triggers",
        "Acute Water Scarcity in South India"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    2076, 1348, 2712, 1554,
    text=(
        "New Delhi, Oct 19\n"
        "Depleted reservoir storage across southern India threatens to trigger severe shortages for irrigation, drinking water, and hydropower generation in the coming months. Southern states depend on both the Southwest Monsoon (June to September) and the Northeast Monsoon (October to December), which brings crucial rainfall to Tamil Nadu, Puducherry, coastal Andhra Pradesh, and southern interior Karnataka."
    ),
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1560, 2712, 1650,
    lines=[
        "Drinking Water Shortages and Crop",
        "Distress Mount Across Key River Basins"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1656, 2382, 2142,
    text=(
        "Water stored in major reservoirs at the end of the monsoon is vital for winter crop irrigation, domestic supply, and power generation. Current storage data reveals alarming deficits: Somasila reservoir in Andhra Pradesh holds just 22.05% of capacity, Srisailam 33.64%, Tamil Nadu's Mettur dam 32.49%, Kerala's Idukki 10.62%, and Karnataka's Ghataprabha and Tungabhadra reservoirs 22.56% and 22.54% respectively. Kerala's Sholayar holds 23.62% and Periyar 46.43%. Overall water storage in the Cauvery river basin has plunged by"
    ),
    target_lines=16,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 1656, 2712, 2142,
    text=(
        "60.50%, while the Pennar basin shows a 72.32% storage deficit.\n"
        "Storage in the Krishna river basin stands 32.59% below normal, and east- and west-flowing river basins between Pennar, Tadri, and Kanyakumari have also recorded sharp declines. India Meteorological Department (IMD) data shows that between June 1 and September 30, rainfall deficits reached 30% in Karnataka and 25% in Andhra Pradesh, hitting interior Karnataka and the Rayalaseema region particularly hard."
    ),
    target_lines=16,
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. BOTTOM PUBLIC NOTICES (PUBLIC NOTICE) — 100% EDITABLE ENGLISH TEXT & CMYK BAR
# ==============================================================================
print("Building Page 9 Bottom Public Notices (100% Editable English Text)...")


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


# 1. Cols 1-2 Top Notice (82..718, 2320..3040)
place_public_notice_2col(
    82, 2320, 718, 3040,
    left_text=(
        "Non-agricultural residential land bearing Sub-Plot No. 123 admeasuring 422.24 sq.mtrs. in the scheme known as 'Silver Springs' situate on Consolidated Block No. 321 etc. (Old Block Nos. 253 Paiki, 319 Paiki, 321, 322 Paiki, 323 Paiki, 324 Paiki, 325 Paiki) of Mouje Village Chekhla, Taluka & Sub-District Sanand, District Ahmedabad, stood in the name of Jwalantbhai Vohra H.U.F. Following the demise of Karta Jwalantbhai Vohra on 13-12-2015, and pursuant to the Succession Certificate issued by the Hon'ble Court, Nayanaben Jwalantbhai Vohra has stated the said property to be in her independent ownership, possession and enjoyment free from all encumbrances and has agreed to sell the same to our client, who"
    ),
    right_text=(
        "has requested a Title Clearance Certificate from us regarding the said property.\n"
        "Any person or institution having any right, claim, interest, lease, mortgage or encumbrance over the said land must notify us in writing with documentary proof within 7 (seven) days at the address below; failing which it shall be deemed that no person has any right, claim or encumbrance, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained.\n"
        "Ahmedabad. Date: 20-10-2026.\n"
        "Mukesh G. Pandya, Advocate\n"
        "403, Vishwanath North View, Opp. L.D. Engineering College, Nr. St. Xavier's College, Navrangpura, Ahmedabad.\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 2. Cols 1-2 Bottom Notice (82..718, 3052..3845)
place_public_notice_2col(
    82, 3052, 718, 3845,
    left_text=(
        "Notice is hereby given to the general public that agricultural land bearing New Survey/Block No. 264 (Old Survey/Block No. 163) admeasuring 28892 sq.mtrs. and New Survey No. 266 (Old Survey/Block No. 164) admeasuring 30302 sq.mtrs. of Mouje Village Durga, Taluka & Sub-District Bavla, Registration District Ahmedabad, is stated by Hemubhai Kalubhai, Madhubhai Kalubhai, Mayarambhai Kalubhai, Butabhai Kalubhai, Sagarbhai Dharamshibhai, Samjuben Wd/o Popatbhai, Tilubhai Popatbhai, Vashuben Popatbhai and Labhubhai Popatbhai to be in their joint ownership, possession and enjoyment free from all encumbrances, and they have requested a Title Clear and Marketable Certificate from us. Any person having"
    ),
    right_text=(
        "any right, title, interest, share, claim or encumbrance over the said land must notify us in writing with documentary proof within 7 (seven) days from publication hereof at the address below; failing which it shall be deemed that no other person has any right, title, interest, share, claim or encumbrance over the said land, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection of any kind shall be entertained.\n"
        "Date: 20/10/2026\n"
        "Kaushik G. Patel\n"
        "(Advocate & Notary)\n"
        "Office: 12, 2nd Floor, J.B.R. Arcade, Beside R.K. Royal Hall, Science City Road, Sola, Ahmedabad-380060.\n"
        "Mob. No. 9824678769"
    ),
    left_lines=23,
    right_lines=25,
)

# 3. Cols 3-4 Top Notice (746..1385, 2320..2990)
place_public_notice_2col(
    746, 2320, 1385, 2990,
    left_text=(
        "Sub-Plot/Bungalow No. 33 admeasuring 210 sq.mtrs. (251 sq.yds.) land with 145.78 sq.mtrs. construction (as per AMC Tax Bill) and undivided share in the scheme land of 'Samak Bungalows', situate on Final Plot Nos. 58/1 and 58/2 of T.P. Scheme No. 42 (Consolidated Revenue Survey No. 477) of Mouje Village Sola, Taluka Ghatlodia, Sub-District Ahmedabad-8 (Sola), Registration District Ahmedabad, is stated by (1) Arunaben Rasikbhai Raval, (2) Kalpan Rasikbhai Raval, and (3) Ketki D/o Rasiklal Raval &"
    ),
    right_text=(
        "W/o Sanjaykumar Raval to be in their joint ownership, possession and enjoyment, and they have agreed to sell the same to our client and requested a Title Certificate from us. Any person having any right, share, claim or encumbrance must notify us in writing with proof by Regd. A.D. within 7 days, failing which any such right shall be deemed waived and Title Clearance proceedings shall be completed.\n"
        "Date: 19/10/2026 | Place: Ahmedabad\n"
        "Through me,\n"
        "Mahendrasinh B. Sisodiya (Advocate)\n"
        "(Mob) 9825786225\n"
        "B/22, Rituraj Society, Nr. Subhash Chowk, Gurukul Road, Memnagar, Ahmedabad-52."
    ),
    left_lines=20,
    right_lines=22,
)

# 4. Cols 3-4 Bottom Notice (746..1385, 3002..3845)
place_public_notice_2col(
    746, 3002, 1385, 3845,
    left_text=(
        "Under instructions from the Chairman/Secretary of our client Nirbhaynagar Co-op. Housing Society Ltd. (Reg. No. GH-641), we Advocate M.S. Kazi hereby give public notice that Tenement No. 11-B in Nirbhaynagar Co-op. Housing Society Ltd., Sector-2, Final Plot No. 83, T.P. Scheme No. 37, Survey No. 20/2 of Mouje Danilimda, Taluka Maninagar, Sub-District Ahmedabad-5 (Narol), was originally allotted to member Shantaben Kantilal Soni holding Share Nos. 246 to 250. Shantaben Kantilal Soni passed away on 15-09-2004, and the original Share Certificate issued to her has been misplaced and cannot be traced despite diligent"
    ),
    right_text=(
        "search. Her legal heirs Bhupendra Kantilal Soni and Sudip Vrajvallabh Soni have applied to the Society for issuance of a Duplicate Share Certificate. Any person having any objection or claim regarding the issuance of a Duplicate Share Certificate to the said heirs must submit written objections to the Society's Chairman/Secretary and to us within 7 days from publication hereof, failing which the Duplicate Share Certificate shall be issued.\n"
        "Ahmedabad Date: 20-10-2026\n"
        "Sd/- Chairman/Secretary\n"
        "(Nirbhaynagar Co-op. Housing Society Ltd.)\n"
        "Through me: (M.S. Kazi) Advocate\n"
        "8/A, Nirbhaynagar Co.op. Hou. Society Ltd. Shahalam, Ahmedabad-28"
    ),
    left_lines=24,
    right_lines=26,
)

# 5. Cols 5-6 Top Notice (1412..2050, 2292..3028)
place_public_notice_2col(
    1412, 2292, 2050, 3028,
    left_text=(
        "Non-agricultural residential land bearing Sub-Plot No. AE-23 admeasuring 533 sq.yds. (570 sq.yds. super area as per Allotment Letter) in the plotting scheme known as 'Suramya Abode', situate on Consolidated Survey/Block No. 220 (Survey Nos. 127, 212, 218, 219, 221, 224, 231, 237, 246, 268, 274, 292, 295, 398, 400, 410, 411, 415, 416, 417, 423, 424) of Mouje Village Rethal, Taluka & Sub-District Sanand, District Ahmedabad, is stated by Ankit Ajaykumar Merchant and Avni Ankit Merchant to be in their joint ownership, possession and enjoyment free from all encumbrances, and they have agreed to sell the same to our client, who has requested"
    ),
    right_text=(
        "a Title Clearance Certificate from us regarding the said plot. Any person or institution having any right, claim, interest, lease, mortgage or encumbrance over the said land must notify us in writing with documentary proof by Regd. A.D. within 7 (seven) days at the address below; failing which it shall be deemed that no person has any right, claim or encumbrance, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection shall be entertained.\n"
        "Ahmedabad. Date: 20-10-2026.\n"
        "Mukesh G. Pandya, Advocate\n"
        "403, Vishwanath North View, Opp. L.D. Engineering College, Nr. St. Xavier's College, Navrangpura, Ahmedabad.\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 6. Cols 5-6 Bottom Notice (1412..2050, 3040..3845)
place_public_notice_2col(
    1412, 3040, 2050, 3845,
    left_text=(
        "Old tenure irrigated agricultural land bearing Block/Survey No. 153 Paiki 1 under Khata No. 595 admeasuring Hec-Are-Sq.Mtrs. 0-65-86 (6586 sq.mtrs.) of Mouje Bhayla, Taluka & Sub-District Bavla, Registration District Ahmedabad, is stated by Vanrajsinh Ramsangbhai Parmar to be in his independent ownership, possession and enjoyment free from all encumbrances except a crop loan from The Bhayla Group Seva Sahakari Mandali Ltd., and he has agreed to sell the same to our client, who has requested a Title Clearance Certificate from us. Any person having any right, claim, lis pendens, share, maintenance claim, lien,"
    ),
    right_text=(
        "easement right, charge, banakhat right or any other interest over the said property must notify us in writing with documentary proof within 7 (seven) days from publication hereof at the address below; failing which it shall be deemed that no person has any right, claim, interest, charge or encumbrance over the said property, or if any existed, the same stands waived, and we shall issue the Title Clearance Certificate, after which no objection of any kind shall be entertained.\n"
        "Date: 20-10-2026.\n"
        "R. D. Savalia (Advocate)\n"
        "Office: Rohit Estate, Opp. Ujala Circle, S.G. Highway, Sarkhej, Ahmedabad - 382210.\n"
        "Mob.: 9898001781"
    ),
    left_lines=23,
    right_lines=25,
)

# 7. Cols 7-8 Top Notice (2076..2712, 2158..2964)
place_public_notice_2col(
    2076, 2158, 2712, 2964,
    left_text=(
        "Mouje Visalpur\n"
        "Non-agricultural land bearing Final Plot No. 127 admeasuring 1396 sq.mtrs. allotted under Draft T.P. Scheme No. 430 against Block/Survey No. 773 Paiki 2 admeasuring 0-13-96 Hec-Are-Sq.Mtrs. (1396 sq.mtrs., forming part of original Survey No. 773 admeasuring 2359 sq.mtrs.) under Khata No. 2033 of Mouje Village Visalpur, Taluka Daskroi, District Ahmedabad, is stated by (1) Sandipkumar Jayantilal Patel and (2) Mehulkumar Arvindbhai Patel to be in their joint ownership, possession and enjoyment free from all encumbrances and legal disputes, and they have requested a Title Clearance Opinion from us. Any person having"
    ),
    right_text=(
        "any encumbrance, charge, tenancy right, easement right, claim, share or dispute over the said land must notify us in writing with documentary proof by Regd. A.D. within 15 days from publication hereof at the address below; failing which, upon expiry of the period, it shall be deemed that no person has any right, claim or encumbrance, or if any existed, the same stands waived, and we shall issue the Title Clearance Opinion Certificate, after which no objection shall be entertained.\n"
        "Ahmedabad | Date: 20/10/2026\n"
        "Jaimin Rohitbhai Patel, Advocate\n"
        "3135, 3rd Floor, T.R.P. Mall, East Court, Bopal, Ahmedabad-380058.\n"
        "Mob. No. 99789 32199"
    ),
    left_lines=22,
    right_lines=24,
)

# 8. Cols 7-8 Bottom Notice (2076..2712, 2978..3845)
place_public_notice_2col(
    2076, 2978, 2712, 3845,
    left_text=(
        "Notice is hereby given to the general public that agricultural land bearing Block No. 1291 (Old Block No. 664 / Old Revenue Survey No. 684) under Khata No. 1236 admeasuring Hec-Are-Sq.Mtrs. 0-27-35 (Assessment Re. 1.45) of Mouje Village Isanpur Mota, Taluka Gandhinagar, Sub-District Gandhinagar Zone-3, Registration District Gandhinagar, is stated by Kapilaben Ramabhai Patel to be in her independent ownership, possession and enjoyment free from all encumbrances, and she has agreed to sell the same to our client, who has requested a Title Clearance Certificate from us. No bank loan, mortgage, transfer, assignment, revenue or civil litigation,"
    ),
    right_text=(
        "decree or stay order is pending against the said land. Any person having any right, title, interest, share, claim, charge or lien over the said land must notify us in writing with documentary proof by Regd. A.D. within 7 days from publication hereof at the address below; failing which, upon expiry of the period, it shall be deemed that no other person has any right, claim, charge or lien over the said land, or if any existed, the same stands waived, and the Title Clearance Certificate shall be issued.\n"
        "Ahmedabad | Date: 19/10/2026\n"
        "Nehal N. Shah Associates\n"
        "Saurin Rajeshbhai Shah, Advocate\n"
        "408, Shantimall, Opp. Navrang Tower, Nr. Sattadhar Char Rasta, Ghatlodia, Ahmedabad. Mob.: 7984930137"
    ),
    left_lines=25,
    right_lines=27,
)

place_png(0, 3855, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_09_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_09_English_SameToSame.dns"
    png_path = target_dir / "Page_09_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_09_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_09_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_09_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_09_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
