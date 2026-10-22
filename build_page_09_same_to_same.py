from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 9 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all Page 9 National/International Stories & Page 1 Continuations:
  1. દિલ્હીની વાત (પહેલા પાનાનું ચાલુ) (Cols 1-3 Top)
  2. અમેરિકન (પહેલા પાનાનું ચાલુ) (Col 3 Mid-Top)
  3. ફ્રાન્સમાં હિંસા (પહેલા પાનાનું ચાલુ) (Col 3 Mid)
  4. સહયોગી દેશો (પહેલા પાનાનું ચાલુ) (Col 3 Mid-Bot)
  5. ક્લાઈમેટ ચેન્જનું વધતુ જોખમ ધરતીના સાત સંકેતો રેકોર્ડ સ્તરે (Cols 4-5 Top)
  6. મણિપુરમાં (પહેલા પાનાનું ચાલુ) (Cols 4-5 Mid-Top)
  7. ટાઈગર પર (પહેલા પાનાનું ચાલુ) (Cols 4-6 Mid-Bot)
  8. વિશ્વના ૨૦ સૌથી પ્રદૂષિત શહેરોમાંથી ૧૩ ભારતના, દિલ્હીનો સમાવેશ નહીં (Cols 6-8 Top)
  9. દક્ષિણ ભારતમાં નૈઋત્યનું ચોમાસુ નિષ્ફળ જતા પાણીની અછત સર્જાઈ (Cols 7-8 Mid)
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


def _utf8_byte_pos(text: str, char_pos: int) -> int:
    return len(text[:char_pos].encode("utf-8"))


def _apply_latin_arial_runs(sid: int, text: str, base_pt: float, font_style: str = "Regular"):
    latin_cmds = []
    eng_pt = round(base_pt * 0.76, 1)
    for m in re.finditer(r"[A-Za-z0-9‘’'\"“”]+(?:\s+[A-Za-z0-9‘’'\"“”]+)*", text):
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
        "title": "Gujarat Samachar — Page 09 (100% Same-to-Same Editable Gopika)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.2)


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
    lo_pt: float = 8.0,
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
    """
    paras: list of tuples (text, is_subhead_or_center_bold, align, indent_pt)
    """
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

    for try_pt10 in range(int(base_pt * 10), 79, -2):
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
                    "fontFamily": "Gopika",
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
print("Placing Page 9 Running Header & Dividers...")
build_running_header(9, place_png, draw_box, place_exact_display_lines)

# Vertical & Horizontal dividers matching Page_09.png
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
# 2. COLS 1-3: દિલ્હીની વાત (પહેલા પાનાનું ચાલુ) + OTHER CONTINUATIONS
# ==============================================================================
print("Building Page 1 Continuations in Cols 1-3...")

place_mixed_paras_column(
    82, 200, 388, 2288,
    paras=[
        ("દિલ્હીની વાત", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("મૂકીને આરોપ કર્યો હતો કે કેટલાક નેતાઓ અને ભારત વિરોધી તત્વો મળીને દેશમાં હિંસા ફેલાવવા યુવાનોને ભડકાવી રહ્યા છે.", "Regular", "leftJustified", 0.0),
        ("તિહાર જેલમાં સીજેપી નેતાઓ હાઈ સિક્યુરીટી વોર્ડમાં", "Subhead", "center", 0.0),
        ("વગર પરવાનગીએ જંતર મંતરમાં પ્રવેશ કરવાની કોશિષ કરનાર ક્રોધરોય જનતા પાર્ટીના આસુતોષ રાંકા અને સૌરવ દાસને દિલ્હીની તિહાર જેલમાં હાઈ સિક્યુરીટી વોર્ડમાં રાખવામાં આવ્યા છે. જેલના સત્તાધિશોએ એમની કોટડીની બહાર વધારાના સુરક્ષા કર્મચારીઓ મૂક્યા તેમ જ દિવસના સમયે બીજા કેદીઓ સાથે બહાર નીકળીને મળે નહીં એનું પણ ધ્યાન રાખવામાં આવ્યું. જેલના રેકોર્ડ પ્રમાણે રાંકાનો કેદી નંબર ૧૭૮૪ અને દાસનો કેદી નંબર ૩૭૫૨ છે. શરૂઆતમાં બંને ને જેલ નંબર ૨માં રાખવામાં આવ્યા હતા, પરંતુ પછીથી રાંકાને જેલ નંબર ૪માં ખસેડવામાં આવ્યા હતા. જેલના પરિસરમાં બીજા બ્લોકોની સરખામણીએ આ બંનેને જ્યાં રાખવામાં આવ્યા છે ત્યાં કેદીઓની સંખ્યા ઓછી છે. ચોવીસે કલાક એમના પર નજર રાખવામાં આવે છે.", "Regular", "leftJustified", 9.0),
        ("‘૨૦૨૩ના ચૂંટણી કમિશન કાયદાને ટેકો આપીને ભુલ કરી’", "Subhead", "center", 0.0),
        ("વાયએસઆરસીપીના પ્રમુખ અને આંધ્રપ્રદેશના ભૂતપૂર્વ મુખ્યમંત્રી વાયએસ જગન મોહન રેડ્ડીએ કબુલ કર્યું છે કે, મુખ્ય ચૂંટણી કમિશનર અને બીજા ચૂંટણી કમિશનરોની નિમણૂકને લઈને ૨૦૨૩માં બનાવવામાં આવેલા કાયદાને એમણે ટેકો આપીને ભુલ કરી હતી. નિષ્પક્ષ ચૂંટણી પ્રક્રિયા માટે એમણે સુધારો કરવાની માંગણી કરી છે. રેડ્ડીનું કહેવું છે કે, ચૂંટણી કરાવવા માટેની જવાબદારી જેમના પર છે એમને પસંદ કરવાની સત્તા સત્તાધારી પક્ષ પાસે હોવી જોઈએ નહીં. પહેલાની પદ્ધતિ એટલે કે ચૂંટણી કમિશનર નિમવાની સત્તા વડાપ્રધાન, વિરોધ પક્ષના નેતા અને ભારતના મુખ્ય ન્યાયાધીશને આપવામાં આવતી હતી. પરીક્ષકની નિમણૂક વિદ્યાર્થી દ્વારા નહી થઈ શકે. જો કોઈ નિષ્પક્ષ સંસ્થા દ્વારા ચૂંટણી કમિશનરોની નિમણૂક નહીં થાય તો ચૂંટણી કમિશનએ ટીકાનો સામનો કરવો પડી શકે છે.", "Regular", "leftJustified", 9.0),
        ("લખનૌમાં ઉલટી ગંગા, એબીવીપીનું જ્ઞાનેશ કુમારના સમર્થનમાં પ્રદર્શન", "Subhead", "center", 0.0),
        ("સીઈસી જ્ઞાનેશ કુમારના રાજીનામા માટે દિલ્હી સહિત દેશ આખામાં દેખાવો થઈ રહ્યા છે. જોકે હવે ભાજપની વિદ્યાર્થી પાંખ અખિલ ભારતીય વિદ્યાર્થી પરિષદ (એબીવીપી)એ લખનૌમાં જ્ઞાનેશ કુમારને ટેકો આપવા માટે પ્રદર્શન કર્યું છે.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

place_mixed_paras_column(
    414, 200, 720, 2288,
    paras=[
        ("લોકશાહી નબળી પડે છે. એબીવીપીએ ‘અરાજકતા રોકો, લોકતંત્ર અપનાવો’ અભિયાન હેઠળ ‘છાત્ર હુંકાર’ વિરોધ પ્રદર્શનનું આયોજન કર્યું છે. લખનૌ યુનિવર્સિટીના ગેટ નંબર ૩ નજીક એબીવીપીના સેંકડો કાર્યકરો ભેગા થયા હતા અને એમણે સુત્રો પોકાર્યા હતા. એમણે કોંગ્રેસ પાર્ટી મુર્દાબાદના સુત્રો પોકારીને અભિષેક દિપકે અને ધ્રુવ રાંઠીને દેશદ્રોહી ગણાવ્યા હતા.", "Regular", "leftJustified", 0.0),
        ("જુબીન નૌટિયાલના પિતા કોંગ્રેસમાં જોડાયા", "Subhead", "center", 0.0),
        ("દહેરાદૂન જિલ્લા પંચાયતના ભૂતપૂર્વ પ્રમુખ અને ગાયક જુબીન નૌટિયાલના પિતા રામ શરણ નૌટિયાલ કોંગ્રેસમાં જોડાઈ ગયા છે. થોડા દિવસો પહેલા એમણે ભાજપમાંથી રાજીનામું આપ્યું હતું. એમણે જ્યારે ભાજપમાંથી રાજીનામું આપ્યું ત્યારે જ એવી ચર્ચા થતી હતી કે તેઓ કોંગ્રેસમાં જોડાશે. એઆઈસીસીના રાષ્ટ્રીય મહામંત્રી કુમારી શૈલજાએ એમને કોંગ્રેસ પ્રવેશ આપ્યો હતો. રામ શરણ નૌટિયાલએ રાજકારણની શરૂઆત કોંગ્રેસમાંથી કરી હતી. તેઓ ઉત્તરાખંડ કોંગ્રેસના ઉપપ્રમુખ પણ રહ્યા હતા. ૨૦૧૪ના વર્ષમાં નૌટિયાલ ભાજપમાં જોડાયા હતા. ત્યાર પછી ૨૦૨૨ની ચૂંટણીમાં ભાજપે એમને ચકરાતા બેઠકની ટિકિટ આપી હતી. જોકે તેઓ જીતી શક્યા નહોતા. કોંગ્રેસમાં જોડાયા પછી નૌટિયાલએ કહ્યું હતું કે, ‘પક્ષ મારા માટે શું વિચારે છે એ હું કહી શકું નહીં, પરંતુ મારૂ મન કોંગ્રેસ વગર માનતું નહોતુ. એટલે હું ફરીથી કોંગ્રેસમાં જોડાયો.’", "Regular", "leftJustified", 9.0),
        ("બદનસીબી નોટીસ બાબતે સુધાકર સિંહની સ્પીકરને રાવ", "Subhead", "center", 0.0),
        ("બિહારના ભોજપુર જિલ્લામાં આવેલા બૌલોટી ગામમાં ભરત ભૂષણ તિવારીના કહેવાતા બનાવટી એન્કાઉન્ટરનો કિસ્સો હવે સંસદીય સ્તર પર પહોંચી ગયો છે. આ બાબતે સવાલો કરનાર આરજેડીના સાંસદ સુધાકર સિંહએ બિહારના સિનિયર આઈપીએસ અધિકારી કુંદન કૃષ્ણન તરફથી મોકલવામાં આવેલી બદનસીબી નોટીસ સંદર્ભે લોકસભાના અધ્યક્ષ ઓમ બિરલાને હસ્તક્ષેપની માંગણી કરી છે. સુધાકર સિંહે પત્ર લખીને સંપૂર્ણ કિસ્સાની તપાસ કરવા તેમજ પ્રથમ દ્રષ્ટિએ જે હકીકત જાણવા મળે એને સંસદની વિશેષાધિકાર સમિતિ પાસે મોકલવાની માંગણી કરી છે. કુંદન કૃષ્ણનએ એમના અંગત વકીલ મારફતે આ નોટીસ મોકલી હતી. સાંસદનું કહેવું છે કે નોટીસમાં જાહેર માફી સાથે પાંચ કરોડ રૂપિયાના વળતરની માંગણી પણ થઈ છે.", "Regular", "leftJustified", 9.0),
        ("ટાઈગર શ્રોફ પર ફાયરીંગ કરાવનાર અનિલ પંડીત કોણ છે?", "Subhead", "center", 0.0),
        ("અમેરિકામાં બેઠેલા ગેંગસ્ટર અનિલ પંડીતનું નામ ફરી એકવાર ચર્ચામાં આવ્યું છે. રવિવારે સાંજે મુંબઈના ખાર વિસ્તારમાં અભિનેતા ટાઈગર શ્રોફની કાર પર ફાયરીંગ કરવામાં આવ્યું હતું. ત્યાર પછી બહાર આવેલા વિડિયોમાં અનિલ પંડીત અને હરમન સંધુએ આ", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

# Col 3 Top: continuation of દિલ્હીની વાત (y=200..716)
place_exact_body_column(
    746, 200, 1051, 716,
    text=(
        "ઘટનાની જવાબદારી લીધી છે. પંડીતએ ઓડિયોમાં સલમાન ખાન અને એના પરિવારને પણ ધમકી આપી છે. અનિલ પંડીતનું નામ આ પહેલા હરિયાણામાં થયેલા એક ફાયરીંગમાં બહાર આવ્યું હતું. આ વર્ષના માર્ચ મહિનામાં પાણીપતની એક મની એક્સચેન્જ ઓફિસ પર દિવસે ગોળીબાર કરવામાં આવ્યો હતો. સોશિયલ મીડિયા પર લોરેન્સ બિશ્નોઈ ગેંગ સાથે જોડાયેલી વ્યક્તિઓએ આ ગોળીબાર કરાવ્યો હોવાની જવાબદારી લીધી હતી. એ વખતે અમેરિકા રહેતા અનિલ પંડીત અને રણદીપ મલીકના નામ બહાર આવ્યા હતા. એ વખતે પંજાબના એક ગાયક - રૈપર બાદશાહને પણ ધમકીઓ આપવામાં આવી હતી."
    ),
    target_lines=17,
    first_indent_pt=0.0,
)

# Col 3 Mid-Top: અમેરિકન (પહેલા પાનાનું ચાલુ) (y=732..1188)
place_mixed_paras_column(
    746, 732, 1051, 1188,
    paras=[
        ("અમેરિકન", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("સેટેલાઈટને તોડવાની સ્પર્ધા જામી શકે છે અને તો એ દુનિયાના કોમ્યુનિકેશન સિસ્ટમ માટે બહુ મોટું જોખમ સર્જાઈ શકે છે. રશિયાએ કોસમોસ-૨૫૯૨ સેટેલાઈટ હજુ આ વર્ષે એપ્રિલમાં જ લોંચ કર્યો હતો. તે વખતે શક્ય છે યુક્રેનની આધુનિક મિસાઈલો અને ડ્રોનની રડાર સિસ્ટમ ખોરવી નાખવાની ગણતરી સાથે જ તેને લોંચ કર્યો હોય.", "Regular", "leftJustified", 0.0),
        ("આ ઘટના પછી પહેલી વખત રશિયા-યુક્રેન વચ્ચેનું યુદ્ધ જમીનથી ઉપર અંતરીક્ષ સુધી પહોંચી ગયું છે.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)

# Col 3 Mid: ફ્રાન્સમાં હિંસા (પહેલા પાનાનું ચાલુ) (y=1202..1472)
place_mixed_paras_column(
    746, 1202, 1051, 1472,
    paras=[
        ("ફ્રાન્સમાં હિંસા", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("છે. ફ્રાન્સ પ્રમુખે હિંસા રોકવા માટે પોલીસ માટે નવી રણનીતિ ઘડવાના પણ નિર્દેશ આપ્યા છે. રવિવારે અનેક શહેરોમાં દેખાવકારોએ રસ્તા પર પડેલી કચરાપેટીઓ, સાયકલો, વાહનોને આગ ચાંપી હતી.", "Regular", "leftJustified", 0.0),
    ],
    target_lines=9,
    base_pt=10.5,
)

# Col 3 Mid-Bot: સહયોગી દેશો (પહેલા પાનાનું ચાલુ) (y=1486..2288)
place_mixed_paras_column(
    746, 1486, 1051, 2288,
    paras=[
        ("સહયોગી દેશો", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("ઈન્ફ્રાસ્ટ્રક્ચરની ૧૦ સુવિધાઓને નુકસાન પહોંચાડવામાં આવ્યું છે.", "Bold", "leftJustified", 0.0),
        ("આ હુમલાને કારણે પાંચ લાખથી વધુ લોકો વીજળી, હિટિંગ અને પાણીના પૂરવઠાથી વંચિત થઈ ગયા છે. કીવ અને તેની આસપાસનાં વિસ્તારોમાં ૧૬ બેલેસ્ટિક મિસાઈલો છોડવામાં આવી હતી. રશિયાએ યુક્રેનમાં ટ્રેનો, શોપિંગ મોલ, ગેસ સ્ટેશન, સુપરમાર્કેટ અને અન્ય જગ્યાઓ પર હુમલાઓ કરીને સામાન્ય જનજીવનમાં અવરોધ ઉભો કરવાનો પ્રયત્ન કર્યો છે.", "Regular", "leftJustified", 9.0),
        ("આ દરમિયાન યુક્રેન યુદ્ધ અંગે અમેરિકા-ચીન-રશિયાની વચ્ચે મંત્રણાની સંભાવનાઓને ફગાવી દીધી છે.", "Bold", "leftJustified", 9.0),
        ("લિથુઆનિયાનાં વડાપ્રધાન મિંડાઉગાસ સિન્કેવિસિયસે સોમવારે જણાવ્યું હતું કે સ્ટારલિંક બેઝ પર આગ લગાવવાનાં પ્રયત્ન પછી લિથુઆનિયામાં સુરક્ષા વધારવામાં આવી છે.", "Regular", "leftJustified", 9.0),
    ],
    target_lines=26,
    base_pt=10.5,
)

# ==============================================================================
# 3. COLS 4-5 TOP: ક્લાઈમેટ ચેન્જનું વધતુ જોખમ ધરતીના સાત સંકેતો રેકોર્ડ સ્તરે
# ==============================================================================
print("Building Climate Change Story (Cols 4-5 Top)...")
place_exact_display_lines(
    1078, 200, 1718, 250,
    lines=["વિજ્ઞાનીઓની સોળ માપદંડોનો અભ્યાસ કરીને ચેતવણી"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1078, 256, 1718, 434,
    lines=[
        "ક્લાઈમેટ ચેન્જનું વધતુ જોખમ",
        "ધરતીના સાત સંકેતો રેકોર્ડ સ્તરે"
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
        "નવી દિલ્હી, તા. ૧૯\n"
        "૧૪ ઓક્ટોબર, ૨૦૨૬ના રોજ બાયોસાયન્સ જર્નલમાં પ્રકાશિત અહેવાલ મુજબ, જળવાયુ પરિવર્તનનો ખતરો સતત વધી રહ્યો છે. વિજ્ઞાનીઓએ પૃથ્વીની સ્થિતિ દર્શાવતા સોળ મહત્વપૂર્ણ સંકેતોનો અભ્યાસ કર્યો, જેમાંથી સાત રેકોર્ડ સ્તરે પહોંચ્યા છે. હવામાં કાર્બન ડાયોક્સાઈડ અને મિથેનનું વધતું પ્રમાણ, પીગળતા ગ્લેશિયરો અને સમુદ્રની વધતી સપાટી દર્શાવે છે કે માનવીય પ્રવૃત્તિઓ પૃથ્વીને સતત ગરમ કરી રહી છે."
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 600, 1718, 694,
    lines=[
        "ગ્રીનહાઉસ ગેસો અને પીગળતા ગ્લેશિયરોએ ચિંતા",
        "વધારી, ફોસિલ ઈંધણનો ઉપયોગ ઘટાડવો અનિવાર્ય"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 700, 1385, 1092,
    text=(
        "અહેવાલ મુજબ વર્ષ ૨૦૨૬માં કાર્બન ડાયોક્સાઈડ, મિથેન અને નાઈટ્રસ ઓક્સાઈડનું સરેરાશ પ્રમાણ રેકોર્ડ સ્તરે રહ્યું છે. આ ગ્રીનહાઉસ વાયુઓ વાતાવરણમાં ગરમી રોકે છે, જેના કારણે પૃથ્વીનું તાપમાન વધે છે. ગ્રીનલેન્ડની બરફની ચાદરનું વજન અને હિમનદીઓની જાડાઈ ઐતિહાસિક નીચલા સ્તરે પહોંચ્યા છે. સમુદ્રમાં ગરમીનો સંગ્રહ અને જળસ્તર વધવાથી પૂર, દરિયાકાંઠાના વિસ્તારોમાં નુકસાન તેમજ પર્યાવરણીય જોખમો વધી રહ્યા છે.\n"
        "વિજ્ઞાનીઓએ ચેતવણી આપી છે કે તાપમાનમાં સતત વધારો થવાથી ક્લાઈમેટ"
    ),
    target_lines=13,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 700, 1718, 1092,
    text=(
        "ટિપિંગ પોઈન્ટ જેવી સ્થિતિ ઊભી થઈ શકે છે, જેમાં પર્યાવરણમાં થતા મોટા ફેરફારો રોકવા અથવા અગાઉની સ્થિતિમાં લાવવા મુશ્કેલ બને છે. જોકે, આવા તમામ ફેરફારો થઈ ચૂક્યા હોવાનો અહેવાલ દાવો નથી કરતો. બીજી તરફ સૌર અને પવન ઊર્જાની ઉત્પાદનક્ષમતા તેમજ બેટરીમાં વીજળી સંગ્રહ કરવાની સુવિધા વધી છે. વર્ષ ૨૦૨૫માં પ્રાચીન ટ્રોપિકલ જંગલોનું નુકસાન પણ ઘટ્યું હતું. આ સકારાત્મક પ્રગતિ છતાં કોલસા, તેલ અને ગેસનો કુલ વપરાશ ઘટ્યો નથી. વધતી ઊર્જાની માગને કારણે સ્વચ્છ ઊર્જા તરફનું પરિવર્તન વધુ ઝડપી બનાવવું જરૂરી છે."
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. COLS 4-5 MID: મણિપુરમાં (પહેલા પાનાનું ચાલુ) (y=1106..1568)
# ==============================================================================
print("Building Manipur Continuation (Cols 4-5 Mid)...")
place_mixed_paras_column(
    1078, 1106, 1385, 1568,
    paras=[
        ("મણિપુરમાં", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("એમના મોત થયા, જ્યારે ક્ષેત્રિમાયુમ સુશીલ (૩૨) નું એક ખાનગી હોસ્પિટલમાં મોત થયું.", "Regular", "leftJustified", 0.0),
        ("ઘાયલ થયેલા અન્ય ત્રણ નાગરિકો એન સૂરજ (૧૮), મેડસનામ સોમેન્દ્રો(૫૩) અને કે. બોસન (૪૫) ને સારવાર પૂરી પડાઈ રહી છે. આ લોકો સહિતનું ૧૬ જણનું જૂથ સવારે ૭ના સુમારે પોતાના ગામ પાસેની પહાડીઓ પરથી બળતણ માટેના લાકડા લેવા ગયા હતા. એ વખતે એમના પર હુમલો ઝીંકી દેવાયો હતો. આથી રોષે ભરાયેલા", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1106, 1718, 1568,
    text=(
        "લોકસમૂહે બનાવના વિરોધમાં મુખ્યમંત્રીના ઘરની બહાર દેખાવો કરતા મુખ્યમંત્રી વાઈ ખેમચંદ સિંહે ઘાયલ થયેલા લોકોના હોસ્પિટલમાં જઈને ખબર-અંતર પૂછ્યા, પરંતુ પત્રકારોના કોઈ પ્રશ્નનો જવાબ આપ્યો નહિ.\n"
        "પોલીસે પ્રદર્શનકારીઓને વિખેરવા માટે અશ્રુવાયુના ટોટા ફોડ્યા. મોડેથી મૃતકોના શબોને જવાહરલાલ નહેરુ ઈન્સ્ટિટ્યુટ ઓફ મેડિકલ સાયન્સીસ ખાતે લઈ જવાયા. મુખ્યમંત્રીના ઘર અને ત્યાં સુધી પહોંચતા રસ્તાઓ પર સુરક્ષા વધારી દેવાઈ છે. આ બનાવ પછી સમગ્ર ઈમ્ફાલમાં બજારો અને દુકાનો બંધ રહ્યા."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. COLS 4-6 MID-BOT: ટાઈગર પર (પહેલા પાનાનું ચાલુ) (y=1580..2288)
# ==============================================================================
print("Building Tiger Shroff Continuation (Cols 4-6 Mid-Bot)...")
place_mixed_paras_column(
    1078, 1580, 1385, 2288,
    paras=[
        ("ટાઈગર પર", "Header", "center", 0.0),
        ("(પહેલા પાનાનું ચાલુ)", "Bold", "center", 0.0),
        ("કર્યું હતું. રિતિક કુમાર ઉર્ફે રોશન રેપિડો બાઈક રાઈડર હોવાથી તે બાઈક ચલાવવામાં કુશળ હતો અને તેને તમામ રસ્તાની માહિતી હતી. આથી તેણે બાઈક ચલાવી હતી. રિતિકે જ બોરીવલી પહોંચી ત્યાથી એપ દ્વારા સુરતની કેબ બુક કરી હતી. ડીસીપીએ જણાવ્યું હતું કે શૂટર દ્વારા ગોળીબારમાં વપરાયેલી મોટરસાઈકલ અંધેરી વિસ્તારમાંથી મળી આવી હતી. ત્રણે શંકાસ્પદો પાસેથી કોઈ શ મળી આવ્યું નથી. અમે આરોપીઓને રાજસ્થાનથી મુંબઈ લાવી રહ્યા છીએ.", "Regular", "leftJustified", 0.0),
        ("ડીસીપીએ કહ્યું કે ટાઈગર શ્રોફ દ્વારા જીવના જોખમની કોઈ ફરિયાદ પહેલા મળી ન હતી. અભિનેતા પર ગોળીબાર કરવા પાછળનો હેતુ હજી સુધી સ્પષ્ટ થયો નથી. શંકાસ્પદ હુમલાખોરોની પૂછપરછ કર્યા પછી અમે ગોળીબારનું ચોક્કસ કારણ જાણી શકીશું.", "Regular", "leftJustified", 9.0),
        ("દેખીતી રીતે જ આરોપીઓએ બાઈક,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=23,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1580, 1718, 2260,
    text=(
        "લોકલ ટ્રેન, કેબ ફરી લાંબા અંતરની ટ્રેન એમ જુદા જુદા પરિવહન વિકલ્પોનો ઉપયોગ કરી તપાસ એજન્સીઓને ગૂંચવવા પ્રયાસ કર્યો હતો. પરંતુ દિલ્હી, ગુજરાત અને રાજસ્થાન પોલીસ દળોની સક્રિય ટેકનિકલ અને ઓપરેશનલ સહાય સાથે ક્રાઈમ બ્રાન્ચની ૨૦ વિશેષ ટીમો દ્વારા હાથ ધરવામાં આવેલા ઝડપી આંતરરાજ્ય ઓપરેશનમાં ઘટનાના ૧૫ કલાકની અંદર રાજસ્થાનના કોટામાં ટ્રેનમાંથી ત્રણેયને ઝડપી લેવાયા હતા.\n"
        "સુરતથી તેઓ પૂણે-જયપુર ટ્રેનમાં બેઠા હતા. તેઓ ચોક્કસ ક્યાં કમ્પાર્ટમેન્ટમાં બેઠા છે તેની માહિતી પણ મુંબઈ પોલીસે મેળવી લીધી હતી. સચોટ માહિતીને આધારે કોટા પોલીસે ટ્રેનમાં તરત જ આ કમ્પાર્ટમેન્ટમાં પહોંચી ત્રણેયને પકડી લીધા હતા.\n"
        "રિતિકે હુમલામાં વપરાયેલી બાઈક હજુ ગઈ ૧૧મી સપ્ટેમ્બરે જ ખરીદી હતી. તેણે તેના માલિકીના કાગળો પણ ટ્રાન્સફર કરાવ્યા ન હતા. ૨૦૨૨થી આ બાઈકની"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 1580, 2050, 2260,
    text=(
        "માલિકી અલગ અલગ ચાર લોકો વચ્ચે બદલાઈ હતી. રિતિકને બાઈક કોણે ઉપલબ્ધ કરાવી અને તેના પૈસા ક્યાંથી આવ્યા તેના આધારે પોલીસ આ ગોળીબારના સૂત્રધારો સુધી પહોંચી શકે છે.\n"
        "ત્રણમાંથી બે આરોપીઓ એક જ સ્થળના રહેવાસી અને એકબીજાના પરિચિત હતા. સીસીટીવી ફૂટેજમાં કેપ પહેરેલો આરોપી દેખાયો છે તે રેહાન હતો. ગોળીબારમાં બે હથિયારોનો ઉપયોગ થયો હતો. અનેક રાઉન્ડ ફાયર થયા હતા. તમામ આરોપીઓ સામે હત્યાના પ્રયાસ સહિતની કલમો લગાડવામાં આવી છે. પોલીસ ગોળીબારની જવાબદારી લેતી લોરેન્સ બિશ્નોઈ ગેંગની સોશિયલ મીડિયા પોસ્ટની સત્યતા વિશે પણ હજુ તપાસ કરી રહી છે એમ ડીસીપીએ જણાવ્યું હતું. ટાઈગર શ્રોફને આ પહેલાં કોઈ દ્વારા ધમકી મળ્યાની કોઈ ફરિયાદ પોલીસ રેકોર્ડ પર નથી."
    ),
    target_lines=22,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. COLS 6-8 TOP: વિશ્વના ૨૦ સૌથી પ્રદૂષિત શહેરોમાંથી ૧૩ ભારતના, દિલ્હીનો સમાવેશ નહીં
# ==============================================================================
print("Building 20 Most Polluted Cities Story (Cols 6-8 Top)...")
place_exact_display_lines(
    1744, 200, 2712, 252,
    lines=["ઈન્ડોનેશિયા-મલેશિયાના શહેરો પણ યાદીમાં સામેલ"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1744, 258, 2712, 434,
    lines=[
        "વિશ્વના ૨૦ સૌથી પ્રદૂષિત શહેરોમાંથી",
        "૧૩ ભારતના, દિલ્હીનો સમાવેશ નહીં"
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
        "નવી દિલ્હી, તા. ૧૯\n"
        "વિશ્વના સૌથી પ્રદૂષિત શહેરોની વૈશ્વિક રેન્કિંગમાં ભારતનું વર્ચસ્વ જોવા મળ્યું, જેમાં ૨૦માંથી ૧૩ શહેરોમાં સૌથી વધુ હવા પ્રદૂષણના સ્તર નોંધાયા. જોકે, ભારતમાં હવાની ગુણવત્તા બગડવા"
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 440, 2712, 556,
    text=(
        "સાથે ઘણીવાર જોડાયેલું દિલ્હી તે સમયે સૂચિમાં નહોતું. એક્યુઆઈએ સોમવારે જાહેર કરેલા ડેટા મુજબ, ઉત્તર પ્રદેશના બુલંદ શહેરને વૈશ્વિક સ્તરે ત્રીજું સ્થાન મળ્યું, જ્યાં યુએસ એક્યુઆઈ રીડિંગ ૧૯૮ હતું, જે અસ્વસ્થ કેટેગરીમાં આવે છે."
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 562, 2712, 652,
    lines=[
        "પ્રદૂષણ અંગેના રિયલ ટાઈમ વૈશ્વિક રેન્કિંગમાં",
        "દિલ્હીમાં હવાની ગુણવત્તાનું સ્તર બદલાતું રહ્યું"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 658, 2050, 1568,
    text=(
        "ત્રિપુરાનું અગરતલા એક્યુઆઈ ૧૮૧ સાથે ચોથા સ્થાને હતું. ટોપ ૨૦માં સામેલ અન્ય ભારતીય શહેરોમાં રાજસ્થાનના પાલી અને ઉત્તર પ્રદેશના મુઝફ્ફરનગરનો સમાવેશ થાય છે, બંનેમાં એક્યુઆઈ ૧૭૪ નોંધાયો. મધ્ય પ્રદેશના બુરહાનપુરમાં પણ એક્યુઆઈ ૧૭૪ હતો, જ્યારે હરિયાણાના રોહતકમાં ૧૭૨. રાજસ્થાનના કોટામાં ૧૭૦, મુંબઈમાં ૧૬૭, હાપુરમાં ૧૬૬, હિસારમાં ૧૬૫, બીકાનેરમાં ૧૬૫ અને બરેલીમાં ૧૬૪ નોંધાયા હતા. આ રીડિંગ્સે ભારતના આ શહેરોને વિશ્વના સૌથી પ્રદૂષિત શહેરી વિસ્તારોમાં મૂકી દીધા છે.\n"
        "ઈન્ડોનેશિયાના અનેક શહેરો પ્રદૂષિત શહેરોમાં ટોચની નજીક હતા. મધ્ય કાલિમંતાનના પલંગકરાયા પ્રથમ સ્થાને રહ્યું, જે યુએસ એક્યુઆઈ ૨૪૨ સાથે ગંભીર કેટેગરીમાં આવે છે. પલેમ્બાંગમાં ૨૦૭ નોંધાયો, જે પણ ગંભીર કેટેગરીમાં છે. સામ્પિત અને જામ્બી અનુક્રમે ૧૮૦ અને ૧૭૬ એક્યુઆઈ સાથે પાંચમા અને છઠ્ઠા સ્થાને રહ્યા. મલેશિયાના પુત્રજયા, કુઆલા લમ્પુર અને પેટાલિંગ જયા પણ ટોપ ૨૦માં સામેલ હતા. જોકે દિલ્હી વૈશ્વિક ટોપ ૨૦ શહેરોના રેન્કિંગમાં નહોતું, તેની હવાની ગુણવત્તા રાત્રે બગડી હતી."
    ),
    target_lines=29,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 658, 2382, 1122,
    text=(
        "રાજધાનીના ઐતિહાસિક એક્યુઆઈ ગ્રાફમાં સોમવારે યુએસ એક્યુઆઈ મહત્તમ ૧૯૧ સુધી પહોંચ્યો હતો, પછી દિવસ દરમિયાન ઘટ્યો. ૧૮ ઓક્ટોબરે સાંજે ૫:૦૧ વાગ્યે લઘુત્તમ ૧૨૬ નોંધાયો હતો.\n"
        "દિલ્હીનો એક્યુઆઈ સવારની ટોચથી ઘટીને ૧૯ ઓક્ટોબરની બપોરે ૧૩૦ના આંકડા સુધી આવ્યું. આ રીડિંગ્સ દર્શાવે છે કે હવા પ્રદૂષણ શહેરો અને કલાકો વચ્ચે કેટલું બદલાઈ શકે છે. વાસ્તવિક સમયની રેન્કિંગમાં કોઈ શહેરની સ્થિતિ માત્ર એક સ્નેપશોટ છે અને હવામાનની સ્થિતિ, ઉત્સર્જન અને"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 658, 2712, 1122,
    text=(
        "વાતાવરણીય પરિભ્રમણ બદલાતાં તે બદલાઈ શકે છે. એક્યુઆઈ.ઈન રેન્કિંગ યુએસ એર ક્વૉલિટી ઈન્ડેક્સનો ઉપયોગ કરે છે, જેમાં ૧૫૧થી ૨૦૦ વચ્ચેના રીડિંગ્સ અસ્વસ્થ કેટેગરીમાં આવે છે, જ્યારે ૨૦૦થી ઉપરના મૂલ્યો ખૂબ અસ્વસ્થ અથવા ગંભીર પ્રદૂષણ દર્શાવે છે. કોઈ શહેર વૈશ્વિક રેન્કિંગમાંથી બહાર હોય ત્યારે પણ ઊંચું પ્રદૂષણ સ્વાસ્થ્ય માટે જોખમ ઊભું કરી શકે છે. ખાસ કરીને બાળકો, વૃદ્ધો અને શ્વસન અથવા હૃદય-રક્તવાહિની સમસ્યાવાળા લોકો માટે જોખમ વધી શકે છે."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. COLS 7-8 MID: દક્ષિણ ભારતમાં નૈઋત્યનું ચોમાસુ નિષ્ફળ જતા પાણીની અછત સર્જાઈ
# ==============================================================================
print("Building South India Monsoon Story (Cols 7-8 Mid)...")
place_exact_display_lines(
    2076, 1136, 2712, 1184,
    lines=["કર્ણાટક અને આંધ્ર પ્રદેશના ઘણાં વિસ્તારોમાં દુષ્કાળ જાહેર"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    underline=True,
)
place_exact_display_lines(
    2076, 1188, 2712, 1344,
    lines=[
        "દક્ષિણ ભારતમાં નૈઋત્યનું ચોમાસુ",
        "નિષ્ફળ જતા પાણીની અછત સર્જાઈ"
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
        "નવી દિલ્હી, તા. ૧૯\n"
        "દક્ષિણ ભારતના જળાશયોમાં જળસંગ્રહ ઓછો થયો હોવાથી આગામી મહિનાઓમાં કૃષિ, પેય જળ અને વીજળી ઉત્પાદન વિગેરે માટે સમસ્યા ઊભી થશે. દક્ષિણ ભારત જૂનથી સપ્ટેમ્બર દરમિયાન સાઉથ વેસ્ટ મોન્સૂન અને ઓક્ટોબર ડિસેમ્બર દરમિયાન નોર્થ ઈસ્ટ મોન્સૂન પર નિર્ભર છે. આ નોર્થ ઈસ્ટ મોન્સૂન તમિલનાડુ, પુડુચેરી, આંધ્ર પ્રદેશના સાગરી કાંઠાઓનો કેટલોક હિસ્સો અને કર્ણાટકના દક્ષિણ ભાગમાં પડે છે. સાઉથવેસ્ટ મોન્સૂન (નૈઋત્યનું ચોમાસુ) અને નોર્થ ઈસ્ટ મોન્સૂન (પૂર્વોત્તર ચોમાસુ) આમ બે વાર દ.ભારતના ઘણાં વિસ્તારોમાં વરસાદ પડે છે."
    ),
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1560, 2712, 1650,
    lines=[
        "પીવાના પાણીની અછત અને પાકની",
        "નિષ્ફળતા જેવી સમસ્યાઓ ઉભી થઈ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1656, 2382, 2142,
    text=(
        "ચોમાસા પછી જળાશયોમાં સંગ્રહ થયેલા પાણીનો ઉપયોગ સિંચાઈ, ઘરમાંની જરૂરતો અને વીજળી ઉત્પાદન માટે કરવામાં આવે છે. પાણીની ડિમાન્ડ, ભૂજળની ઉપલબ્ધતા અને હવે પછી વરસાદ પડશે તેના આધારે વિવિધ ક્ષેત્રના જળસંકટની ગંભીરતા જણાશે. આંધ્ર પ્રદેશના સોમશિલા જળાશયમાં કુલ ક્ષમતાના ફક્ત ૨૨.૦૫ ટકા, શ્રી શૈલમમાં ૩૩.૬૪ ટકા, તમિલનાડુના મેટ્ટુરમાં ૩૨.૪૯ ટકા, કેરળના ઈડુક્કીમાં ૧૦.૬૨ ટકા, કર્ણાટકના ઘટપ્રભામાં ૨૨.૫૬ ટકા અને તુંગભદ્રામાં ૨૨.૫૪ ટકા છે. કેરળના શોલાયારમાં ૨૩.૬૨ ટકા અને પેરિયારમાં ૪૬.૪૩ ટકા જળસંગ્રહ થયો છે. કાવેરી નદી બેસિનમાં જળસંગ્રહની કુલ ક્ષમતામાં"
    ),
    target_lines=16,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 1656, 2712, 2142,
    text=(
        "૬૦.૫૦ ટકા અને પેન્નાર બેસિનમાં ૭૨.૩૨ ટકા જળસંગ્રહ ઓછો થયો છે.\n"
        "કૃષ્ણા બેસિનમાં સામાન્યથી ૩૨.૫૯ ટકા ઓછો સંગ્રહ થયો છે. પેન્નારથી કન્યાકુમારી સુધી વહેતી નદીઓ અને તાદરીથી કન્યાકુમારી સુધી વહેતી નદીઓના બેસિનમાં પાણીનો જળસંગ્રહ ઓછો થયો છે. ઈન્ડિયા મિટિઓરોલોજિકલ ડિપાર્ટમેન્ટ (આઈએમડી- ભારતીય હવામાન વિભાગ)ના આંકડા દર્શાવે છે ૧ જૂન અને ૩૦ સપ્ટેમ્બર વચ્ચે કર્ણાટકમાં વરસાદની અછત ૩૦ ટકા અને આંધ્ર પ્રદેશમાં ૨૫ ટકા નોંધાઈ હતી. કર્ણાટકના અંતરિયાળ વિસ્તારોમાં અને આંધ્ર પ્રદેશના રાયલસી ક્ષેત્રમાં વરસાદની અછતની ગંભીર અસર થઈ છે."
    ),
    target_lines=16,
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. BOTTOM PUBLIC NOTICES (જાહેર નોટિસ) — 100% EDITABLE GOPIKA TEXT & CMYK BAR
# ==============================================================================
print("Building Page 9 Bottom Public Notices (100% Editable Gopika Text)...")

def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=52):
    x_mid = (x1_px + x2_px) // 2
    draw_box(x1_px, y1_px, x2_px, y2_px, stroke_swatch="[Black]", stroke_weight_pt=1.8)
    draw_box(x1_px, y1_px, x_mid - 4, y1_px + header_h, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
    place_exact_display_lines(
        x1_px + 10, y1_px + 6, x_mid - 14, y1_px + header_h - 4,
        lines=["જાહેર નોટિસ"],
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
        "જત ડિસ્ટ્રીકટ અમદાવાદ સબ ડિસ્ટ્રીકટ અને તાલુકા સાણંદના ગામ મોજે ચેખલાની સીમના (જુના બ્લોક નંબર - ૨૫૩ પૈકી, ૩૧૯ પૈકી, ૩૨૧, ૩૨૨ પૈકી, ૩૨૩ પૈકી, ૩૨૪ પૈકી, ૩૨૫ પૈકી) એકત્રીત બ્લોક નંબર - ૩૨૧ વિગેરેની જમીન ઉપર આવેલ સિલ્વર સ્પ્રિંગ્સ ના નામથી ઓળખાતી યોજનામાં આવેલ પ્લોટો પૈકી સબ પ્લોટ નંબર - ૧૨૩ ની ૪૨૨.૨૪ ચોરસમીટર ના ક્ષેત્રફળની રહેણાંકના હેતુ માટેની બિનખેતીની જમીન જવલંતભાઈ વોહરા એચ.યુ.એફ. નામે આવેલ એચ.યુ.એફ. ના કર્તા જવલંતભાઈ વોહરા નુ તા.૧૩-૧૨-૨૦૧૫ ના રોજ અવસાન થતા નામદાર કોર્ટના વારસાઈ પ્રમાણપત્રના આધારે નયનાબેન જવલંતભાઈ વોહરા એ તેઓની સ્વતંત્ર માલીકી કબજા ભોગવટાની તમામ પ્રકારના બોજા મુક્ત આવેલ હોવાનું જણાવીને સદર જમીન અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે અને આ અંગે અમારા"
    ),
    right_text=(
        "અસીલએ અમારી પાસે સદરહુ જમીનના ટાઈટલ ક્લીયરન્સ સર્ટિફીકેટની માંગણી કરેલ છે.\n"
        "સદરહુ જમીન ઉપર કોઈપણ વ્યક્તિ કે સંસ્થાનો કોઈપણ પ્રકારનો હક્ક, દાવો, લાગભાગ, લીઝ, ગીરો કે બોજો હોય તો તે અંગેના લેખિત પુરાવા સાથે અમોને દિન-૭ (સાત)માં નીચેના સરનામે જાણ કરવી અને જો તેમ કરવામાં કસુર થશે તો સદરહુ જમીન ઉપર કોઈનો કોઈપણ પ્રકારનો બોજો કે હક્ક દાવા કે અધિકાર નથી અને જો હોય તો તે તમામ જતા કરેલ છે તેમ સમજી અમો સદરહુ જમીનનું ટાઈટલ ક્લીયરન્સ સર્ટીફીકેટ ઈશ્યુ કરીશું. ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં. જેની નોંધ લેવી.\n"
        "અમદાવાદ. તા. ૨૦-૧૦-૨૦૨૬.\n"
        "મુકેશ જી. પંડ્યા, એડવોકેટ\n"
        "૪૦૩, વિશ્વનાથ નોર્થ વ્યુ, એલ.ડી. એન્જીનીયરીંગ કોલેજની સામે, સેંટ ઝેવિયર્સ કોલેજની પાસે, નવરંગપુરા, અમદાવાદ.\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 2. Cols 1-2 Bottom Notice (82..718, 3052..3845)
place_public_notice_2col(
    82, 3052, 718, 3845,
    left_text=(
        "આથી જાહેર જનતાને જણાવવાનું કે, રજીસ્ટ્રેશન ડિસ્ટ્રીકટ અમદાવાદના સબ-ડિસ્ટ્રીકટ અને તાલુકા બાવળાના ગામ મોજે દુર્ગા ની સીમના નવા સર્વે/બ્લોક નંબર-૨૬૪(જુના સર્વે/બ્લોક નંબર-૧૬૩)ની કુલ ૨૮૮૯૨ ચોરસમીટર તથા નવા સર્વે નંબર-૨૬૬(જુના સર્વે/બ્લોક નંબર-૧૬૪)ની કુલ ૩૦૩૦૨ ચોરસમીટર ખેતીની જમીન હેમુભાઈ કાળુભાઈ, મધુ ભાઈ કાળુભાઈ, મયારામ ભાઈ કાળુભાઈ, બુટાભાઈ કાળુભાઈ, સાગરભાઈ ધરમશીભાઈ, સમજુબેન તે પોપટભાઈની વિધવા પત્ની, ટીલુભાઈ પોપટભાઈ, વશુબેન પોપટભાઈ તથા લાભુભાઈ પોપટભાઈએ તેઓની સંપુર્ણપણે સંયુક્ત, માલિકી, કબજા, ભોગવટાની તમામ બોજા રહીત હોવાનું જણાવી અમારી પાસેથી સદરહુ જમીનના ટાઈટલ્સ કલીયર અને માર્કેટેબલ હોવા બદલના પ્રમાણપત્રની માંગણી કરેલ છે. તો સદરહુ જમીન ઉપર જો કોઈનો"
    ),
    right_text=(
        "કોઈપણ પ્રકારનો લાગ-ભાગ,હક્ક,હીત,હીસ્સો,દાવો કે બોજો હોય તો તેઓએ આ નોટીસ પ્રસિધ્ધ થયેથી દિન-૭(સાત)માં અમોને તે બદલના જરૂરી પુરાવાઓ સહીત લેખિતમાં જાણ નીચેના સરનામે કરવી જો તેમ કરવામાં નહીં આવે તો સદરહુ જમીન ઉપર અન્ય કોઈપણ વ્યક્તિનો કોઈપણ પ્રકારનો લાગ-ભાગ,હક્ક,હીત,હીસ્સો,દાવો કે બોજો નથી અને હોય તો તે જતો કરેલ છે તેમ માનીને અમો સદરહુ જમીનનું ટાઈટલ્સ કલીયરન્સ સર્ટીફીકેટ આપીશું અને ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં.\n"
        "તારીખ-૨૦/૧૦/૨૦૨૬\n"
        "કૌશિક.જી.પટેલ\n"
        "(એડવોકેટ એન્ડ નોટરી)\n"
        "ઓફીસ :-૧૨,બીજો માળ, જે. બી. આર.આર્કેડ,આર.કે.રોયલ હોલની બાજુમાં,સાયન્સ સીટી રોડ, સોલા, અમદાવાદ-૩૮૦૦૬૦.\n"
        "મો.નં.૯૮૨૪૬૭૮૭૬૯"
    ),
    left_lines=23,
    right_lines=25,
)

# 3. Cols 3-4 Top Notice (746..1385, 2320..2990)
place_public_notice_2col(
    746, 2320, 1385, 2990,
    left_text=(
        "જત રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૮ (સોલા) ના તાલુકા ઘાટલોડીયા ના મોજે ગામ સોલાની સીમના એકત્રિત રેવન્યુ સરવે નં.૪૭૭ યાને ટી.પી. સ્કીમ નં.૪૨ ના ફાઈનલ પ્લોટ નં.૫૮/૧ અને ૫૮/૨ ની બીનખેતીની જમીનમાં બાંધવામાં આવેલ ‘સમક બંગલોઝ’ એ નામની યોજનામાં આવેલ રહેણાંકના પ્લોટ / બંગલોઝ ટાઈપની મિલકતો પૈકી સબ પ્લોટ/ બંગલા નં.૩૩ ની આશરે ૨૧૦ ચો.મી. યાને ૨૫૧ ચો.વાર જમીનમાં આશરે ૧૪૫.૭૮ ચો.મી. (એ.એમ.સી. ના ટેક્ષ બીલ મુજબ) ના બાંધકામવાળી મિલકત તથા યોજનાની જમીનમાં પોષાતા વગર વહેંચાયેલ જમીનના હક્ક હિસ્સા સહિતની મિલકત (૧) અરૂણાબેન રસિકભાઈ રાવલ (૨) કલ્પન રસિકભાઈ રાવલ તથા (૩) કેતકી તે રસિકલાલ રાવલ પુત્રી અને"
    ),
    right_text=(
        "સંજયકુમાર રાવલના પત્ની ની કુલ સંયુક્ત માલીકી કબજા ભોગવટાની આવેલ છે અને અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે તેમ જણાવી અમારી પાસે ટાઈટલ સર્ટીફીકેટની માંગણી કરેલ છે. જે અંગે બીજા કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિસ્સો, બોજો કે અલાખો હોય તો દિન-૭ માં રજી.એ.ડી.પોસ્ટથી પુરાવા સહિત લેખિત જાણ કરવી, નહી તો તેઓએ પોતાનો હક્ક, હિત, હિસ્સો જતો કરેલ છે તેમ માની ટાઈટલ કલીયર સર્ટીફીકેટ અંગેની કાર્યવાહી કરવામાં આવશે. જેની સર્વેએ નોંધ લેવી.\n"
        "તા.૧૯/૧૦/૨૦૨૬\n"
        "સ્થળઃ અમદાવાદ\n"
        "મારી મારફતે,\n"
        "મહેન્દ્રસિંહ બી.સિસોદીયા (એડવોકેટ)\n"
        "(મો) ૯૮૨૫૭૮૬૨૨૫\n"
        "બી/૨૨, ઋતુરાજ સોસાયટી, સુભાષ ચોક પાસે, ગુરૂકુલ રોડ, મેમનગર, અમદાવાદ-૫૨."
    ),
    left_lines=20,
    right_lines=22,
)

# 4. Cols 3-4 Bottom Notice (746..1385, 3002..3845)
place_public_notice_2col(
    746, 3002, 1385, 3845,
    left_text=(
        "આથી અમો એડવોકેટશ્રી એમ.એસ.કાઝી તે અમારા અસીલ નિર્ભયનગર કો.ઓ.હા.સો.લિ. રજીસ્ટ્રેશન નં.ઘ-૬૪૧ ના ચેરમેન-સેક્રેટરીની સુચના અને ફરમાઈશથી આ જાહેર નોટીસ આપી જણાવીએ છીએ કે- ડીસ્ટ્રીકટ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૫(નારોલ), મણીનગર તાલુકાના મોજે દાણીલીમડાના સ.નં.૨૦/૨, ટી.પી.સ્કીમ નં.૩૭, ફા.પ્લોટ નં.૮૩, સેકટર-૨ માં આવેલ નિર્ભયનગર કો.ઓ.હા.સો.લિ.રજીસ્ટર નં.ઘ-૬૪૧ ના ટેનામેન્ટ નં.૧૧-બી વાળી મીલકત મુળ એલોટી મેમ્બર શાંતાબેન કાંતિલાલ સોની હતા. તેઓને સોસાયટીના શેર નં.૨૪૬ થી ૨૫૦ ઈસ્યુ કરેલા અને ઓરીજીનલ શેર સર્ટીફીકેટ તેમને આપવામાં આવેલ. શાંતાબેન કાંતિલાલ સોની તા.૧૫-૯- ૨૦૦૪ ના રોજ અવસાન પામેલા છે અને તેમને આપેલ શેર સર્ટીફીકેટ ભુલથી અને શરતચુકથી ખોવાઈ ગયેલ છે અને ઘણી શોધખોળ કરતા મળી"
    ),
    right_text=(
        "આવતુ નથી તેમ જણાવેલ. તેમના વારસો પૈકી ભુપેન્દ્ર કાંતિલાલ સોની અને સુદીપ વ્રજવલ્લભ સોનીએ સોસાયટીમાં ડુપ્લીકેટ શેર સર્ટીફીકેટ મેળવવા અરજી કરેલ છે. સદરહુ વારસદારોને ડુપ્લીકેટ શેર સર્ટીફીકેટ આપવા સામે કોઈને વાંધો કે તકરાર હોય તો આ નોટીસ પ્રસિધ્ધ થયેથી દિન-૭ માં સોસાયટીના ચેરમેન-સેક્રેટરીને તથા અમો એડવોકેટશ્રીને લેખિતમાં વાંધા તકરારો મોકલી આપવા. જો કોઈ વાંધા તકરાર નહીં આવે તો તેઓને ડુપ્લીકેટ શેર સર્ટીફીકેટ કાઢી આપવામાં આવશે. ત્યારબાદ કોઈનો વાંધો કે તકરાર ચાલશે નહીં તેની નોંધ લેશો.\n"
        "અમદાવાદ તાઃ-૨૦-૧૦-૨૦૨૬\n"
        "ચેરમેન/સેક્રેટરીની સહી\n"
        "(નિર્ભયનગર કો.ઓ.હા.સો.લિ.)\n"
        "મારી મારફતે\n"
        "(એમ.એસ. કાઝી) એડવોકેટ\n"
        "8/A, Nirbhaynagar Co.op. Hou. Society Ltd. Shahalam, Ahmedabad-28"
    ),
    left_lines=24,
    right_lines=26,
)

# 5. Cols 5-6 Top Notice (1412..2050, 2292..3028)
place_public_notice_2col(
    1412, 2292, 2050, 3028,
    left_text=(
        "જત ડિસ્ટ્રીકટ અમદાવાદ સબ ડિસ્ટ્રીકટ અને તાલુકા સાણંદના ગામ મોજે રેથલની સીમના એકત્રીત સર્વે/બ્લોક નંબર - ૨૨૦ ( સર્વે નંબર - ૧૨૭, ૨૧૨, ૨૧૮, ૨૧૯, ૨૨૧, ૨૨૪, ૨૩૧, ૨૩૭, ૨૪૬, ૨૬૮, ૨૭૪, ૨૯૨, ૨૯૫, ૩૯૮, ૪૦૦, ૪૧૦, ૪૧૧, ૪૧૫, ૪૧૬, ૪૧૭, ૪૨૩, ૪૨૪) વિગેરેની રહેણાંકના હેતુવાળી બીનખેતીની જમીન ઉપર મુકવામાં આવેલ પ્લોટીંગની સ્કિમ જે સુરમ્ય એબોડ તરીકે ઓળખાય છે. તેમાં આવેલ સબ પ્લોટ નંબર - એઈ - ૨૩ ની ૫૩૩ ચોરસવાર (એલોટમેન્ટ લેટર મુજબ - ૫૭૦ ચોરસવાર સુપર એરીયા)ની રહેણાંકના હેતુની બીનખેતીની જમીન અંકીત અજયકુમાર મર્ચન્ટ તથા અવની અંકીત મર્ચન્ટ એ તેઓની સંયુક્ત માલીકી કબજા ભોગવટાની તમામ પ્રકારના બોજા મુક્ત આવેલ હોવાનું જણાવીને સદર જમીન અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે અને આ અંગે અમારા અસીલએ અમારી"
    ),
    right_text=(
        "પાસે સદરહુ જમીનના ટાઈટલ ક્લીયરન્સ સર્ટિફીકેટની માંગણી કરેલ છે. સદરહુ પ્લોટની જમીન ઉપર કોઈપણ વ્યક્તિ કે સંસ્થાનો કોઈપણ પ્રકારનો હક્ક, દાવો, લાગભાગ, લીઝ, ગીરો કે બોજો હોય તો તે અંગેના લેખિત પુરાવા સાથે અમોને દિન-૭ (સાત)માં નીચેના સરનામે રજી. એ.ડી. થી જાણ કરવી અને જો તેમ કરવામાં કસુર થશે તો સદરહુ જમીન ઉપર કોઈનો કોઈપણ પ્રકારનો બોજો કે હક્ક દાવા કે અધિકાર નથી અને જો હોય તો તે તમામ જતા કરેલ છે તેમ સમજીને અમો સદરહુ જમીનનું ટાઈટલ ક્લીયરન્સ સર્ટીફીકેટ ઈશ્યુ કરીશું. ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં. જેની નોંધ લેવી.\n"
        "અમદાવાદ. તા. ૨૦-૧૦-૨૦૨૬.\n"
        "મુકેશ જી.પંડ્યા, એડવોકેટ\n"
        "૪૦૩, વિશ્વનાથ નોર્થ વ્યુ, એલ.ડી. એન્જીનીયરીંગ કોલેજની સામે, સેંટ ઝેવિયર્સ કોલેજની પાસે, નવરંગપુરા, અમદાવાદ.\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 6. Cols 5-6 Bottom Notice (1412..2050, 3040..3845)
place_public_notice_2col(
    1412, 3040, 2050, 3845,
    left_text=(
        "રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદના સબ-ડીસ્ટ્રીકટ અને તાલુકા બાવળા મોજે ભાયલાની સીમના ખાતા નં. ૫૯૫ ના બ્લોક/સર્વે નં. ૧૫૩ પૈકી ૧ ની હે-આર-ચો.મી. ૦-૬૫-૮૬ આકાર રૂા.૩.૪૦ વાળી યાને કે ૬૫૮૬ સમ.ચો.મી. ક્ષેત્રફળ ધરાવતી જુની શરતની પિયત ખેતીની જમીનવાળી મિલકત વનરાજસિંહ રામસંગભાઈ પરમાર ની સ્વતંત્ર માલીકી અને કબજા ભોગવટાની તથા ધી ભાયલા ગ્રુપ સેવા સહકારી મંડળી લી.ના લીધેલ લોનના બોજા સિવાયના, તમામ બોજાઓથી મુક્ત હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે. અને તેઓએ સદરહું નંબર અને માપવાળી મિલકત અંગેના ટાઈટલ કલીયર સર્ટીફીકેટની અમારી પાસેથી માંગણી કરેલ છે. જેથી સદરહું મિલકત ઉપર જે કોઈનો હક્ક, દાવો, લીસ પેન્ડસી, અલાખો, લાગભાગ, ખોરાકી, પોષાકી, લીયન, બોજો, તકરાર કે ભરણ પોષણનો હક્કદાવો,"
    ),
    right_text=(
        "ઈઝમેન્ટ રાઈટ, ચાર્જ, બાનાખતના હક્ક કે અન્ય કોઈપણ પ્રકારનો, હક્ક, હીસ્સો કે હીત સંબંધ વિગેરે કાંઈપણ હોયતો તેમણે આ જાહેર નોટીસ પ્રસિધ્ધ થયેથી દિન-૭ (સાત) માં અમોને દસ્તાવેજી લેખીત પુરાવા સહીત નીચેના સરનામે જાણ કરવી. જો તેમ કરવામાં કસુર યા વિલંબ થશે તો મજકુર મિલકત ઉપર કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક,હીસ્સો, હીત સંબંધ, બોજો, ચાર્જ નથી અને હોય તો તેમણે પોતાનો હક્ક જતો [Waive] કરેલ છે, તેમ સમજીને ટાઈટલ કલીયર સર્ટીફીકેટ ઈસ્યુ કરી દેવામાં આવશે. ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહી જેની જાહેર જનતાએ નોંધ લેવી.\n"
        "તા.૨૦-૧૦-૨૦૨૬.\n"
        "R. D. Savalia (Advocate)\n"
        "ઓફીસ : રોહિત એસ્ટેટ, ઉજાલા સર્કલની સામે, એસ.જી. હાઈવે, સરખેજ, અમદાવાદ - ૩૮૨૨૧૦.\n"
        "મો.:૯૮૯૮૦૦૧૭૮૧"
    ),
    left_lines=23,
    right_lines=25,
)

# 7. Cols 7-8 Top Notice (2076..2712, 2158..2964)
place_public_notice_2col(
    2076, 2158, 2712, 2964,
    left_text=(
        "મોજે વિસલપુર\n"
        "ડીસ્ટ્રીક અમદાવાદ, તાલુકો દશક્રોઈના મોજે ગામ વિસલપુર ની સીમનાં ખાતા નંબર ૨૦૩૩ ના બ્લોક/સર્વે નંબર ૭૭૩ પૈકી ૨ વાળી કુલ ૦-૧૩-૯૬ હે.આરે.ચો.મી. યાને કે ૧૩૯૬ ચો.મી. વાળી જમીન તે બિનખેતી થયા અગાઉ સર્વે નંબર ૭૭૩નો હિસ્સો છે તે સર્વે નંબર ૭૭૩ વાળી સમગ્ર ૨૩૫૯ ચો.મી. જમીનનો સમાવેશ ડ્રાફ્ટ ટી.પી. સ્કીમ નંબર ૪૩૦ માં થતા તેને ફાળવવા માં આવેલ, તે ફાઈનલ પ્લોટ નંબર ૧૨૭ વાળી ૧૩૯૬ ચો.મી. બિનખેતી વાળી જમીન (૧) સંદીપકુમાર જયંતિલાલ પટેલ (૨) મેહુલકુમાર અરવિંદભાઈ પટેલનાઓની સંયુક્ત માલિકી કબજા ભોગવટા ની, બિન બોજા ની તેમજ કાનૂની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસેથી ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાય ની માંગણી કરેલ છે. આથી સદરહુ"
    ),
    right_text=(
        "જમીનમાં કોઈનો બોજો, ચાર્જ, ખેડહક્ક, ગણોતહક્ક, ઈઝમેન્ટ રાઈટ્સ કે અન્ય કોઈપણ પ્રકારનો લાગભાગ, કબજા-હક્ક, હિત, હિસ્સો, દાવો,તકરાર કે બોજો હોય તો તેમણે આ નોટીસ પ્રસિદ્ધ થયેથી નીચેનાં સરનામે દિન-૧૫ માં લેખિત પુરાવા સહીત રજી.એ.ડી.થી જાણ કરવી જો તેમ કરવામાં નહિ આવે તો મુદત વીત્યે સદરહુ જમીન ઉપર કોઈનો કોઈપણ પ્રકારનો બોજો, હક્ક-દાવો કે અધિકાર રહેલો નથી અને જો હોય તો તે જતો (વેવ) કરેલ છે તેવું સમજી સદરહુ જમીન નું ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાય નું સર્ટીફીકેટ ઈસ્યુ કરી દઈશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહિ.\n"
        "અમદાવાદ\n"
        "તારીખ : ૨૦/૧૦/૨૦૨૬\n"
        "જૈમિન રોહિતભાઈ પટેલ, એડવોકેટ\n"
        "૩૧૩૫, ત્રીજો માળ, ટી.આર.પી. મોલ, ઈસ્ટ કોર્ટ, બોપલ, અમદાવાદ-૩૮૦૦૫૮.\n"
        "મો. નં. ૯૯૭૮૯ ૩૨૧૯૯"
    ),
    left_lines=22,
    right_lines=24,
)

# 8. Cols 7-8 Bottom Notice (2076..2712, 2978..3845)
place_public_notice_2col(
    2076, 2978, 2712, 3845,
    left_text=(
        "આથી જાહેર નોટીસ આપી જાહેર જનતાને જણાવવાનું કે, રજીસ્ટ્રેશન ડીસ્ટ્રીકટ ગાંધીનગર સબ ડીસ્ટ્રીકટ ગાંધીનગર ઝોન - ૩ ના તાલુકા ગાંધીનગરના મોજે ગામ ઈસનપુર મોટાની સીમના ખાતા નંબર ૧૨૩૬ ના બ્લોક નંબર ૧૨૯૧ (જુના બ્લોક નંબર ૬૬૪ ના જુના રેવન્યુ સર્વે નંબર ૬૮૪) ની કુલ હે.આરે.ચો.મી. ૦-૨૭-૩૫, આકાર રૂા.૧.૪૫ પૈસાવાળી ખેતીની જમીન., કપીલાબેન રામાભાઈ પટેલની કુલ સ્વતંત્ર સંયુક્ત માલીકીપણા અને કબજા ભોગવટાની તથા બોજા રહીત હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે., અને અમારા અસીલે અમારી પાસે સદર જમીનના ટાઈટલ કલીયરન્સ સર્ટીફીકેટની માંગણી કરેલ છે. સદર જમીન ઉપર કપીલાબેન રામાભાઈ પટેલ એ કોઈપણ બેંક, વ્યક્તિ, પેઢી કે ખાનગી સંસ્થા પાસેથી લોન ધિરાણ મેળવી બોજો ઉત્પન્ન કરેલ નથી કે હાલમાં ચાલુ નથી., તેમજ સદરહુ જમીન અન્ય કોઈપણ ત્રાહિત વ્યક્તિ શખ્સને લખી આપી ટ્રાન્સફર એસાઈન કરેલ નથી કે સદર જમીનમાં હાલ કોઈપણ જાતની રેવન્યુ તકરારો કે દિવાની તકરારો ચાલતી નથી કે પેન્ડીંગ નથી કે કોઈપણ"
    ),
    right_text=(
        "જાતનું હુકમનામું થયેલ નથી કે મનાઈ હુકમ ચાલુ નથી., તેમજ સદર જમીન ઉપર અન્ય કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક હીત, હીસ્સો, દાવો, અલાખો, બોજો, ચાર્જ, લીયન હોય તો આ જાહેર નોટીસ પ્રસિધ્ધ થયેથી દિન-૭ માં અમોને લેખિત પુરાવાઓ સહીત રજી.એ.ડી.થી નીચે જણાવેલ સરનામે જાણ કરવી અને જો તેમ કરવામાં કસુર થશે તો મુદત વીતે સદર જમીનમાં અન્ય કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હીત, હીસ્સો, દાવો, અલાખો, બોજો, ચાર્જ, લીયન નથી અને જો હોય તો તે જતો કર્યો છે તેમ સમજી સદર જમીનનું ટાઈટલ કલીયરન્સ સર્ટીફીકેટ ઈસ્યુ કરવામાં આવશે., અને ત્યારબાદ સદર જમીન અમારા અસીલ વેચાણ રાખવા અંગેની કાર્યવાહી હાથ ધરશે., તો ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં, તેની જાહેર જનતાએ નોંધ લેવી.\n"
        "અમદાવાદ\n"
        "તારીખઃ- ૧૯/૧૦/૨૦૨૬\n"
        "નેહલ એન. શાહ એસોસીએટ્સ\n"
        "સૌરિન રાજેશભાઈ શાહ, એડવોકેટ\n"
        "૪૦૮, શાંતિમોલ, નવરંગ ટાવર સામે, સાર્થક સ્કુલ પાસે, સત્તાધાર ચાર રસ્તા પાસે, ઘાટલોડીયા, અમદાવાદ.\n"
        "મો.નં.- ૭૯૮૪૯૩૦૧૩૭"
    ),
    left_lines=25,
    right_lines=27,
)

place_png(0, 3855, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_09_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_09_SameToSame.dns"
    png_path = target_dir / "Page_09_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_09_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_09_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
