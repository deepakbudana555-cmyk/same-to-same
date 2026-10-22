from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 10 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
==================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all 7 Business News Stories AND all 10 Market Price / Stock Tables on Page 10:
  1. ખાનગી બેંક,આઈટી, હેલ્થકેર શેરોમાં કડાકો : સેન્સેક્સ ૮૭૬ પોઈન્ટ ગબડીને ૭૩૮૫૩ (Cols 1-8 Top Box)
  2. FMCG કંપનીઓના માર્જિન દબાણ હેઠળઃ દિવાળી બાદ ભાવ વધવા સંભાવના (Cols 1-3 Mid-Top)
  3. દશેરા પૂર્વે સોનામાં બેતરફી વધઘટઃ ક્રૂડમાં ઉંચા મથાળે ઘટાડોઃ પ્લેટીનમમાં તેજી (Cols 1-3 Mid)
  4. જૂન ત્રિમાસિક માટે પાકિસ્તાનનો આર્થિક વિકાસ દર બે ટકા રહ્યો (Cols 1-2 Mid-Bot)
  5. રૂપિયો ફરી ઉંચકાયોઃ યુરોપમાં તોફાનો વધતાં યુરો ઝડપથી તૂટ્યો + ફોરેક્સ ભાવ + કેશ ફ્યુચર ઓપ્શન + સોના-ચાંદી બજાર (Cols 4-5 Mid)
  6. નાતાલ તથા નવા વર્ષ માટે અમેરિકા ખાતેથી ગારમેન્ટસના ઓર્ડરમાં ઘટાડો (Cols 6-8 Mid-Top)
  7. ખાદ્યતેલોમાં મિશ્ર હવામાનઃ દશેરા પૂર્વે માંગ વધીઃ દિવેલ તથા એરંડામાં આગેકૂચ + અમદાવાદ/રાજકોટ/મુંબઈ બજારો + NSE/BSE Tables (Cols 6-8 Mid-Bot)
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


def _utf8_byte_pos(text: str, char_pos: int) -> int:
    return len(text[:char_pos].encode("utf-8"))


def _apply_latin_arial_runs(sid: int, text: str, base_pt: float, font_style: str = "Regular"):
    latin_cmds = []
    eng_pt = round(base_pt * 0.76, 1)
    for m in re.finditer(r"[A-Za-z0-9‘’'\"“”/]+(?:\s+[A-Za-z0-9‘’'\"“”/]+)*", text):
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
        "title": "Gujarat Samachar — Page 10 (100% Same-to-Same Editable Gopika)"
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

    for try_pt10 in range(int(base_pt * 10), 75, -2):
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
                _apply_latin_arial_runs(sid, full_text, pt, "Bold")
                return fid, sid
    return fid, sid


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 10 Running Header...")
build_running_header(10, place_png, draw_box, place_exact_display_lines)

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
        ("(ગુજરાત સમાચાર પ્રતિનિધિ)                                        મુંબઈ, સોમવાર", "Regular", "leftJustified", 0.0),
        ("અમેરિકામાં બોન્ડ યીલ્ડ ફરી વધી આવતાં અને યુક્રેનના રશિયા પર મહાડ્રોન હુમલાને લઈ ફરી જીઓપોલિટીકલ ટેન્શન વધતાં અને આંતરરાષ્ટ્રીય બજારમાં ક્રૂડ ઓઈલના ભાવ ફરી વધી આવતાં વૈશ્વિક બજારોમાં ધોવાણ પાછળ ભારતીય શેર બજારોમાં પણ આજે કડાકો બોલાઈ ગયો હતો. ખાનગી બેંકોના ગત સપ્તાહના અંતે ત્રિમાસિક પરિણામો એકંદર અપેક્ષાથી સારા આવ્યા છતાં દેશમાં વધતી મોંઘવારી અને લોનના વધતાં દરોએ આગામી દિવસોમાં ડિફોલ્ટરોની સંખ્યા વધવાના જોખમ અને ડૂબત લોનનો આંક વધવાની પણ આશંકાએ આજે ખાનગી બેંક શેરોમાં કડાકો બોલાયો હતો. અલબત પીએસયુ બેંક શેરોમાં આજે રિકવરી જોવાઈ હતી.", "Regular", "leftJustified", 9.0),
        ("આજે-મંગળવારે દશેરા નિમિત્તે શેર બજારો બંધ રહેશે", "Subhead", "center", 0.0),
        ("કેપિટલ ગુડઝ-પાવર, હેલ્થકેર, ઓટોમોબાઈલ, આઈટી-સોફ્ટવેર સર્વિસીઝ, ટેકનોલોજી શેરો તેમ જ મેટલ-માઈનીંગ, કન્ઝયુમર ડયુરેબલ્સ, એફએમસીજી શેરોમાં વેચવાલીનું દબાણ વધતું જોવાયું હતું. સેન્સેક્સ ૮૭૬.૩૭ પોઈન્ટ તૂટીને ૭૩૮૫૨.૯૦ અને નિફ્ટી ૫૦ સ્પોટ ઈન્ડેક્સ ૨૫૭.૨૦ પોઈન્ટ ગબડીને ૨૨૮૮૮.૯૫ બંધ રહ્યા હતા. અમેરિકા અને ભારત વચ્ચે ટ્રેડ ડિલની વાટાઘાટ પોઝિટીવ બની રહ્યાના અને એકંદર પરિણામો સારા આવી રહ્યા છતાં વૈશ્વિક પરિબળોની સાથે મેગા આઈપીઓની તૈયારીએ લિક્વિડિટીની તંગીની જોગવાઈને લઈને પણ આજે બજારમાં સેલિંગ પ્રેશર જોવાયું હતું. દશેરા નિમિત્તે આજે-મંગળવારે ૨૦, ઓક્ટોબર ૨૦૨૬ના શેર બજારો બંધ રહેશે.", "Regular", "leftJustified", 9.0),
        ("કેપિટલ ગુડઝ ઈન્ડેક્સ ૭૩૪ પોઈન્ટ તૂટ્યો : એલજી\nઈક્વિપમેન્ટ, સુઝલોન, થર્મેક્સ, પોલીકેબ તૂટ્યા", "Subhead", "center", 0.0),
        ("કેપિટલ ગુડઝ-પાવર શેરોમાં આજે મોટું સેલિંગ થતાં ભાવો તૂટ્યા હતા. એલજી ઈક્વિપમેન્ટ રૂ.૨૭.૯૦ તૂટીને રૂ.૫૪૬.૮૦, સુઝલોન રૂ.૧.૫૮ ગબડીને રૂ.૪૦.૩૪, આઈનોક્સ વિન્ડ રૂ.૨.૫૪ તૂટીને રૂ.૬૪.૮૯, થર્મેક્સ રૂ.૯૧.૧૫ તૂટીને રૂ.૩૨૩૪.૯૦, પોલીકેબ રૂ.૧૯૮ તૂટીને રૂ.૮૦૨૦, ભારત ડાયનામિક્સ રૂ.૨૭ ઘટીને રૂ.૧૦૮૮, કિર્લોસ્કર એન્જિન રૂ.૪૮.૨૦ તૂટીને રૂ.૧૯૭૩.૧૦, જ્યોતી સીએનસી રૂ.૨૧.૬૦ ઘટીને રૂ.૯૭૫.૦૫, અપાર ઈન્ડસ્ટ્રીઝ રૂ.૩૧૭.૮૦ ઘટીને રૂ.૧૫,૭૩૩.૯૦, વારી એનર્જી રૂ.૪૧.૯૦ ઘટીને રૂ.૨૫૧૩.૧૦, મઝગાંવ ડોક રૂ.૩૭ ઘટીને રૂ.૨૦૫૪, કાર્બોરેન્ડમ યુનિવર્સલ રૂ.૨૧.૮૦ ઘટીને રૂ.૧૦૮૮.૫૦ રહ્યા હતા. બીએસઈ કેપિટલ ગુડઝ ઈન્ડેક્સ ૭૩૩.૫૨ પોઈન્ટ ગબડીને ૭૨૭૮૯.૭૧", "Regular", "leftJustified", 9.0),
    ],
    target_lines=32,
    base_pt=10.6,
)

# Sections 2-3 Headline inside top box (746..2050, y=208..424)
place_exact_display_lines(
    746, 208, 2050, 424,
    lines=[
        "ખાનગી બેંક,આઈટી, હેલ્થકેર શેરોમાં કડાકો",
        ": સેન્સેક્સ ૮૭૬ પોઈન્ટ ગબડીને ૭૩૮૫૩"
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
        ("બંધ રહ્યો હતો.", "Regular", "leftJustified", 0.0),
        ("આઈટી શેરોમાં ફરી ધોવાણ : ઓરિઓનપ્રો, ઓરમ, જેનેસીસ\nઈન્ટર., આઈજીમો, સારેકન, સોનાટા ગબડ્યા", "Subhead", "center", 0.0),
        ("આઈટી-સોફ્ટવેર સર્વિસીઝ, ટેકનોલોજી શેરોમાં તેજી અટકીને આજે ફરી ફંડોની વેચવાલી નીકળતાં ધોવાણ થયું હતું. કેપીઆઈટી રૂ.૧૮.૭૫ ઘટીને રૂ.૫૩૬, સોનાટા સોફ્ટવેર રૂ.૭.૮૫ ઘટીને રૂ.૨૪૦.૦૫, એડીએસએલ રૂ.૩.૩૫ ઘટીને રૂ.૧૦૩.૧૫ ડેલિવરી રૂ.૧૬.૯૫ ઘટીને રૂ.૫૨૭.૧૫, ઈમુદ્રા રૂ.૧૬.૬૫ ઘટીને રૂ.૫૩૯.૪૦, ટાટા ટેકનોલોજી રૂ.૧૮.૦૦ ઘટીને રૂ.૭૦૫.૩૦ રહ્યા હતા. બીએસઈ આઈટી ઈન્ડેક્સ ૪૧૯.૮૬ પોઈન્ટ તૂટીને ૨૯૯૭૭.૧૬ બંધ રહ્યો હતો.", "Regular", "leftJustified", 9.0),
        ("ક્રુડના ભાવ વધતાં ઓટો શેરોમાં ફંડોની ફરી વેચવાલી : ભારત\nફોર્જ, એક્સાઈડ, ટાટા મોટર્સ, હ્યુન્ડાઈ ઘટ્યા", "Subhead", "center", 0.0),
        ("ક્રુડ ઓઈલના આંતરરાષ્ટ્રીય ભાવ વધતાં હવે ફરી પેટ્રોલ, ડિઝલના ભાવમાં તોળાતા વધારા અને મોંઘવારીથી પ્રજા ત્રાહિમામ પોકારવા લાગી હોઈ તહેવારોની સીઝનમાં વાહનોનું બુકિંગ અપેક્ષિત નહીં હોવાના અહેવાલ વચ્ચે આજે ફંડોએ ઓટોમોબાઈલ શેરોમાં વેચવાલી કરી હતી. ભારત ફોર્જ રૂ.૯૦.૫૫ ઘટીને રૂ.૧૭૯૧.૪૦, એક્સાઈડ રૂ.૧૦.૫૦ ઘટીને રૂ.૩૬૦.૩૫, ટાટા મોટર્સ પેસેન્જર વ્હીકલ રૂ.૭.૫૦ ઘટીને રૂ.૨૭૯.૪૦, ઉનો મિન્ડા રૂ.૨૨.૭૦ ઘટીને રૂ.૧૦૮૭.૫૦,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Section 3 inside top box (1412..2050, y=428..974)
place_mixed_paras_column(
    1412, 428, 2050, 974,
    paras=[
        ("હ્યુન્ડાઈ મોટર રૂ.૨૭.૯૫ ઘટીને રૂ.૧૯૫૯.૦૫, બજાજ ઓટો રૂ.૧૧૭ ઘટીને રૂ.૧૦,૩૦૦, એમઆરએફ રૂ.૯૫૧.૩૦ ઘટીને રૂ.૧,૨૧,૮૫૬.૯૫ રહ્યા હતા. બીએસઈ ઓટો ઈન્ડેક્સ ૪૧૭.૯૦ પોઈન્ટ તૂટીને ૫૬૬૦૬.૫૭ બંધ રહ્યો હતો.", "Regular", "leftJustified", 0.0),
        ("હેલ્થકેર ઈન્ડેક્સ ૫૦૩ પોઈન્ટ ગબડ્યો : વન ગ્લોબલ, થ્રીબી\nબ્લેક, સોલારા, ફર્મેન્ટા, થેમીસ મેડી ઘટ્યા", "Subhead", "center", 0.0),
        ("અમેરિકા સાથે ભારતની ટ્રેડ ડિલ અંતિમ તબક્કામાં હોવાના સંકેત છતાં હેલ્થકેર ક્ષેત્રે કોઈ ખાસ મોટી ડિલ નહીં થવાની ધારણાએ આજે ફંડોની હેલ્થકેર-ફાર્મા શેરોમાં મોટી વેચવાલી થઈ હતી. સોલારા રૂ.૪૮.૮૫ ઘટીને રૂ.૬૪૭.૪૫, ફર્મેન્ટા રૂ.૨૮.૫૦ ઘટીને રૂ.૪૫૯.૪૦, થેમીસ મેડી રૂ.૬.૧૫ ઘટીને રૂ.૧૦૦.૪૦, આરતી મેડી રૂ.૪૧.૩૦ ઘટીને રૂ.૮૩૩.૮૫ રહ્યા હતા. બીએસઈ હેલ્થકેર ઈન્ડેક્સ ૫૦૩.૩૩ પોઈન્ટ ગબડીને ૪૭૭૬૪.૬૬ બંધ રહ્યો હતો.", "Regular", "leftJustified", 9.0),
        ("ખાનગી બેંકોના સારા પરિણામ છતાં શેરો તૂટ્યા : એક્સિસ\nરૂ.૫૦ તૂટ્યો : યુનિયન બેંક, પીએનબી વધ્યા", "Subhead", "center", 0.0),
        ("ખાનગી બેંકોના ગત સપ્તાહના અંતે એક્સિસ બેંક, આઈસીઆઈસીઆઈ બેંક, એચડીએફસી બેંકના અપેક્ષાથી એકંદર સારા પરિણામ છતાં ફંડોએ આજે ખાનગી બેંક શેરોમાં મોટી વેચવાલી કરી હતી. જો કે પીએસયુ બેંક શેરોમાં સિલેક્ટિવ ખરીદી રહી હતી. એક્સિસ બેંકના સારા પરિણામ છતાં શેર રૂ.૪૯.૫૫ તૂટીને રૂ.૧૨૩૬.૯૦,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Sections 2-3 Bottom Banner inside top box (746..2050, y=986..1150)
place_exact_display_lines(
    746, 986, 2050, 1150,
    lines=[
        "નિફ્ટી ૨૫૭ પોઈન્ટ ગબડીને ૨૨૮૮૯ : રોકાણકારોની સંપત્તિમાં",
        "રૂ.૪.૬૯ લાખ કરોડનું ધોવાણ : FIIની રૂ.૧૧૪૯ કરોડની વેચવાલી"
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
        ("એચડીએફસી બેંક રૂ.૧૬.૫૦ ઘટીને રૂ.૭૧૧.૬૦, આઈસીઆઈસીઆઈ બેંક રૂ.૧૪.૮૦ ઘટીને રૂ.૧૩૮૨, રહ્યા હતા. પીએસયુ બેંક શેરોમાં ત્રિમાસિક પરિણામનું આકર્ષણ રહ્યું હતું. યુનિયન બેંક ઓફ ઈન્ડિયા રૂ.૮.૫૦ વધીને રૂ.૧૮૦.૫૦, પીએનબી રૂ.૫.૫૫ વધીને રૂ.૧૨૧.૯૫, બેંક ઓફ ઈન્ડિયા રૂ.૪.૮૫ વધીને રૂ.૧૩૭.૧૦, બેંક ઓફ બરોડા રૂ.૮ વધીને રૂ.૨૩૮, સ્ટેટ બેંક રૂ.૧૦.૭૫ વધીને રૂ.૯૭૨.૪૫, કેનેરા બેંક રૂ.૩.૪૦ વધીને રૂ.૧૨૨ રહ્યા હતા. બીએસઈ બેંકેક્સ ઈન્ડેક્સ ૨૯૧.૪૯ પોઈન્ટ ઘટીને ૬૨૪૭૭.૯૪ બંધ રહ્યો હતો.", "Regular", "leftJustified", 0.0),
        ("કન્ઝયુમર ડયુરેબલ્સ શેરોમાં વેચવાલી : ક્રોમ્પ્ટન, અંબર\nએન્ટર., ડિક્સન, વોલ્ટાસ, કલ્યાણ જવેલર્સ ઘટ્યા", "Subhead", "center", 0.0),
        ("કન્ઝયુમર ડયુરેબલ્સ શેરોમાં પણ ફંડોની આજે વેચવાલી જોવાઈ હતી. ક્રોમ્પ્ટન રૂ.૮.૩૦ ઘટીને રૂ.૨૦૯.૯૦, અંબર એન્ટરપ્રાઈસીઝ રૂ.૧૬૪.૬૫ ઘટીને રૂ.૬૫૨૦.૩૫, હવેલ્સ ઈન્ડિયા રૂ.૨૫.૪૫ ઘટીને રૂ.૧૦૯૮.૩૫, ડિક્સન ટેકનોલોજી રૂ.૨૨૯ ઘટીને રૂ.૧૨,૧૦૦, કલ્યાણ જવેલર્સ રૂ.૫.૫૦ ઘટીને રૂ.૫૫૨, ટાઈટન રૂ.૩૦ ઘટીને રૂ.૪૪૨૦ રહ્યા હતા. બીએસઈ કન્ઝયુમર ડયુરેબલ્સ ઈન્ડેક્સ ૫૪૫.૭૧ પોઈન્ટ ઘટીને ૫૯૯૫૯.૪૮ બંધ રહ્યો હતો.", "Regular", "leftJustified", 9.0),
        ("FPIs/FIIની કેશમાં રૂ.૧૧૪૯ કરોડની ચોખ્ખી વેચવાલી :\nDIIની રૂ.૩૨૦૧ કરોડની ચોખ્ખી ખરીદી", "Subhead", "center", 0.0),
        ("ફોરેન પોર્ટફોલિયો ઈન્વેસ્ટરો-એફપીઆઈઝ, એફઆઈઆઈઝની આજે સોમવારે કેશ સેગ્મેન્ટમાં રૂ.૧૧૪૮.૬૪ કરોડના શેરોની ચોખ્ખી વેચવાલી કરી હતી. કુલ રૂ.૧૧,૨૪૦.૬૪ કરોડની ખરીદી સામે કુલ રૂ.૧૨,૩૮૯.૨૮ કરોડની વેચવાલી કરી હતી. સ્થાનિક સંસ્થાકીય રોકાણકારો-ડીઆઈઆઈની પણ આજે રૂ.૩૨૦૧.૧૯ કરોડના શેરોની ચોખ્ખી ખરીદી રહી હતી. કુલ રૂ.૧૪,૭૮૧.૩૧ કરોડની ખરીદી સામે કુલ રૂ.૧૧,૫૮૦.૧૨ કરોડની વેચવાલી કરી હતી.", "Regular", "leftJustified", 9.0),
        ("શેરોમાં રોકાણકારોની સંપત્તિ-માર્કેટ કેપિટલાઈઝેશન રૂ.૪.૬૯\nલાખ કરોડ ઘટીને રૂ.૪૬૭.૯૩ લાખ કરોડ", "Subhead", "center", 0.0),
        ("શેરોમાં વ્યાપક વેચવાલીએ રોકાણકારોની સંપત્તિ એટલે કે બીએસઈમાં લિસ્ટેડ કંપનીઓનું એકત્રિત માર્કેટ કેપિટલાઈઝેશન આજે એક દિવસમાં રૂ.૪.૬૯ લાખ કરોડ ધોવાઈને રૂ.૪૬૭.૯૩ લાખ કરોડ રહ્યું હતું.", "Regular", "leftJustified", 9.0),
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
# 4. STORY 2 (COLS 1-3, y=1168..1898): FMCG કંપનીઓના માર્જિન દબાણ હેઠળ
# ==============================================================================
print("Building Story 2 (FMCG Margins, Cols 1-3)...")
place_exact_display_lines(
    82, 1168, 1051, 1342,
    lines=[
        "FMCG કંપનીઓના માર્જિન દબાણ",
        "હેઠળઃ દિવાળી બાદ ભાવ વધવા સંભાવના"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 1348, 556, 1412,
    text="મુંબઈ, તા. ૧૯\nકાચા માલના ભાવમાં વધારાને પરિણામે નફાશક્તિ પર દબાણ આવતાને",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    576, 1348, 1051, 1412,
    text="પગલે વર્તમાન નાણાં વર્ષના પાછલા છ મહિનામાં એફએમસીજી ક્ષેત્રની કંપનીઓ સતત માર્જિન દબાણનો સામનો કરી રહી છે.",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1416, 1051, 1462,
    lines=["કાચા માલમાં ભાવ વધારાથી તેમના ઉત્પાદન ખર્ચમાં વૃદ્ધિ"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1468, 388, 1898,
    text=(
        "માર્જિન દબાણ છતાં કંપનીઓ દિવાળીની માગ પર અસર ન થાય તેને ધ્યાનમાં રાખી હાલમાં ભાવ વધારો કરવાનું ટાળી રહી છે અને દિવાળી બાદ સ્થિતિમાં સુધાર નહીં આવે તો એફએમસીજી પ્રોડક્ટસમાં ભાવ વધારો આવવાની શક્યતા રહેલી છે.\n"
        "જૂન ત્રિમાસિકમાં ઘટાડો થયા બાદ કાચા માલના ખર્ચમાં સપ્ટેમ્બર ત્રિમાસિકમાં વધારો થયો છે. જેને કારણે માર્જિન પર દબાણ આવ્યું છે. માર્જિન પર દબાણ છતાં કંપનીઓ કન્ઝયુમર માગમાં ઘટાડો ન થાય તેની ખાતરી રાખવા ભાવ વધારો ટાળી રહી છે, એમ એફએમસીજી"
    ),
    target_lines=15,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 1468, 720, 1898,
    text=(
        "ક્ષેત્રના એક વિશ્લેષકે જણાવ્યું હતું.\n"
        "એફએમસીજી પ્રોડક્ટસના ઉત્પાદનમાં વપરાતા કાચા માલ જેમ કે ક્રુડ તેલ, ઓઈલના બાય-પ્રોડક્ટસ, પેકેજિંગ સામગ્રી, ખાંડ તથા ખાદ્ય તેલના ભાવમાં તાજેતરના સમયમાં વધારો જોવા મળ્યો છે. કાચા માલના ખર્ચમાં વધારાને કારણે એફએમસીજી ક્ષેત્રની કંપનીઓના સપ્ટેમ્બર ત્રિમાસિકના પરિણામો નબળા આવવાની શક્યતા નકારાતી નથી.\n"
        "ફુગાવામાં થઈ રહેલો વધારો એફએમસીજી ઉદ્યોગ માટે ચિંતાનો વિષય બની રહ્યો છે.\n"
        "ફિનિશ્ડ પ્રોડક્ટસના ભાવ વધારવાને"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 1468, 1051, 1898,
    text=(
        "બદલે કાર્યક્ષમતામાં વધારો કરીને અને કોસ્ટ કટિંગના પગલાં મારફત કંપનીઓ કાચા માલના ભાવ વધારાના બોજને હળવો કરવાની નીતિ અપનાવી રહી હોવાનું પણ વિશ્લેષકે ઉમેર્યું હતું.\n"
        "દિવાળી બાદ કૃષિ કોમોડિટીસની કિંમતોમાં વધારો થવાની શક્યતા રહેલી છે. કૃષિ જણસોના ભાવમાં વધુ વધારાથી રેડી ટુ ઈટ જેવા ખાદ્ય પદાર્થના ઉત્પાદકો દ્વારા કિંમતમાં વધારો જોવા મળવા સંભવ છે. વર્તમાન વર્ષે અલ નિનોની અસરને કારણે ચોમાસુ નબળુ રહેતા કૃષિ પેદાશોના ઉત્પાદન પર અસર પડી છે."
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. STORY 3 (COLS 1-3, y=1910..2960): દશેરા પૂર્વે સોનામાં બેતરફી વધઘટ
# ==============================================================================
print("Building Story 3 (Gold/Crude/Platinum, Cols 1-3)...")
place_exact_display_lines(
    82, 1910, 1051, 2082,
    lines=[
        "દશેરા પૂર્વે સોનામાં બેતરફી વધઘટઃ ક્રૂડમાં",
        "ઉંચા મથાળે ઘટાડોઃ પ્લેટીનમમાં તેજી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 2088, 556, 2166,
    text="(વાણિજ્ય પ્રતિનિધિ) મુંબઈ, સોમવાર\nમુંબઈ ઝવેરી બજારમાં આજે સોના-ચાંદીના ભાવ ઉંચા ખુલ્યા પછી નીચા બંધ રહ્યા હતા. સોનાના ભાવ જીએસટી વગર",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    576, 2088, 1051, 2166,
    text="૯૯૫ના રૂ.૧૪૫૫૦૦ વાળા રૂ.૧૪૫૮૨૦ ખુલી રૂ.૧૪૫૩૬૦ બંધ રહ્યા હતા. જ્યારે ૯૯૯ના ભાવ રૂ.૧૪૬૧૦૦ વાળા રૂ.૧૪૬૪૦૪ ખુલી રૂ.૧૪૫૯૪૪ બંધ રહ્યા હતા.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 2172, 1051, 2218,
    lines=["વિશ્વ બજારમાં સોનાના ભાવ વધી ઉંચામાં ૪૨૦૦ ડોલર નજીક"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 2224, 388, 2556,
    text=(
        "મુંબઈ ચાંદીના ભાવ જીએસટી વગર કિલોના રૂ.૨૦૯૫૦૦ વાળા રૂ.૨૦૮૭૫૦ બંધ રહ્યા હતા. મુંબઈ સોના-ચાંદીમાં જીએસટી સાથેના ભાવ જોકે આ ભાવથી ૩ ટકા ઉંચા રહ્યા હતા. દરમિયાન, મુંબઈ બજારમાં પ્લેટીનમના ભાવ ૧૦ ગ્રામદીઠ રૂ.૫૮૪૮૨ વાળા આજે સવારે રૂ.૫૯૮૮૦ ખુલી રૂ.૫૭૦૨૬ બંધ રહ્યા હતા.\n"
        "દરમિયાન, અમદાવાદ ઝવેરી બજારમાં"
    ),
    target_lines=11,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2224, 720, 2556,
    text=(
        "આજે સોનાના ભાવ ૧૦ ગ્રામના રૂ.૩૦૦ વધી ૯૯૫ના રૂ.૧૫૦૭૦૦ તથા ૯૯૯ના રૂ.૧૫૧૦૦૦ રહ્યા હતા. અમદાવાદ ચાંદીના ભાવ કિલોના રૂ.૨૧૩૦૦૦ રહ્યા હતા વિશ્વ બજારમાં આજે સોનાના ભાવ ઔંસદીઠ ૪૧૬૫થી ૪૧૬૬ વાળા ઉંચામાં ભાવ ૪૧૯૦થી ૪૧૯૧ થઈ ૪૧૭૫થી ૪૧૭૬ ડોલર રહ્યા હતા. સોના પાછળ વૈશ્વિક ચાંદીના ભાવ પણ ઔંસના ૫૬.૯૯ વાળા વધી ઉંચામાં ભાવ ૫૭.૮૫"
    ),
    target_lines=11,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 2224, 1051, 2958,
    text=(
        "થઈ ૫૭.૭૪થી ૫૭.૭૫ ડોલર રહ્યા હતા. પ્લેટીનમના ભાવ ૧૬૩૫ વાળા ૧૬૫૯ થઈ ૧૬૫૦થી ૧૬૫૧ ડોલર રહ્યા હતા. પેલેડીયમના ભાવ ૧૧૧૬ વાળા ઉંચામાં ભાવ ૧૧૪૦ થઈ ૧૧૩૮ ડોલર રહ્યા હતા. વૈશ્વિક કોપરના ભાવ આજે ૦.૨૭ ટકા પ્લસમાં રહ્યા હતા. દરમિયાન, વિશ્વ બજારમાં આજે ક્રુડતેલના ભાવ વધતા અટકી ફરી ઘટાડા પર રહ્યા હતા.\n"
        "બ્રેન્ટ ક્રૂડના ભાવ બેરલના જે ઉંચામાં ૧૧૦ ડોલર સુધી પહોંચ્યા હતા તે ભાવ આજે ઘટી નીચામાં ૧૦૬.૮૨ થઈ ૧૦૮.૬૨ ડોલર રહ્યા હતા. યુએસ ક્રૂડના ભાવ ઘટી નીચામાં ૯૯.૨૪ થઈ ૧૦૧.૩૩ ડોલર રહ્યા હતા. નવી માગ ધીમી હતી. ભારતમાં ઓઈલ ઈમ્પોર્ટ બિલ સપ્ટેમ્બરમાં ૧૪ ટકા વધી ૧૫.૪૦ અબજ ડોલર થયાના સમાચાર હતા. ગયા વર્ષે સપ્ટેમ્બરમાં આ આંકડો ૧૦.૫૦ અબજ ડોલર નોંધાયો હતો.\n"
        "દેશમાં સપ્ટેમ્બરમાં આ આંકડો ૧૦.૫૦ અબજ ડોલર નોંધાયો હતો. દેશમાં સપ્ટેમ્બરમાં ક્રૂડની ઈમ્પોર્ટ ૭ ટકા વધી હતી જ્યારે ઈમ્પોર્ટ બિલમાં ૧૪ ટકાનો વધારો થયો હતો."
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. STORY 4 (COLS 1-2, y=2568..2958): જૂન ત્રિમાસિક માટે પાકિસ્તાનનો આર્થિક વિકાસ દર બે ટકા રહ્યો
# ==============================================================================
print("Building Story 4 (Pakistan GDP Growth, Cols 1-2 Mid-Bot)...")
place_exact_display_lines(
    82, 2568, 720, 2684,
    lines=[
        "જૂન ત્રિમાસિક માટે પાકિસ્તાનનો",
        "આર્થિક વિકાસ દર બે ટકા રહ્યો"
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
        "મુંબઈ, તા. ૧૯\n"
        "વર્તમાન નાણાં વર્ષ માટે ભારતના આર્થિક વિકાસ દરના અંદાજમાં વૈશ્વિક રેટિંગ એજન્સીઓ વધારો કરી રહી છે જ્યારે પાકિસ્તાનના આર્થિક વિકાસ દર નબળો પડી રહ્યાનું પ્રાપ્ત ડેટા જણાવે છે.\n"
        "૨૦૨૬ના જૂન ત્રિમાસિકમાં પાકિસ્તાનનો આર્થિક વિકાસ દર અપેક્ષા"
    ),
    target_lines=9,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2690, 720, 2958,
    text=(
        "કરતા નીચો રહી બે ટકા રહ્યો છે જ્યારે ભારતનો આ ગાળાનો જીડીપી અપેક્ષા કરતા વધુ આવી ૭.૮૦ ટકા જોવા મળ્યો છે. જૂન ત્રિમાસિક માટે પાકિસ્તાનનો જીડીપી અંદાજ ૩.૫૦ ટકા મુકાયો હતો.\n"
        "મધ્ય પૂર્વની અશાંતિએ પાકિસ્તાનના વેપાર પર અસર કરી હોવાનું સ્થાનિક સુત્રો જણાવી રહ્યા છે."
    ),
    target_lines=9,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. STORY 5 (COLS 4-5, y=1168..3030): રૂપિયો ફરી ઉંચકાયો + ફોરેક્સ ભાવ + કેશ ફ્યુચર ઓપ્શન + સોના-ચાંદી બજાર
# ==============================================================================
print("Building Story 5 (Rupee/Euro, Forex Table, Cash Future Option & Gold-Silver Market, Cols 4-5)...")
place_exact_display_lines(
    1078, 1168, 1718, 1310,
    lines=[
        "રૂપિયો ફરી ઉંચકાયોઃ યુરોપમાં",
        "તોફાનો વધતાં યુરો ઝડપથી તૂટ્યો"
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
        "(વાણિજ્ય પ્રતિનિધિ) મુંબઈ, સોમવાર\n"
        "મુંબઈ કરન્સી બજારમાં આજે રૂપિયા સામે ડોલરના ભાવમાં ઘટાડો નોંધાયો હતો. ડોલરના ભાવ જે શનિવારે બંધ બજારે ઉંચામાં ૮૫.૦૬ સુધી પહોંચ્યા હતા તે ભાવ આજે સવારે રૂ. ૮૪.૯૯ ખુલ્યા પછી નીચામાં ભાવ રૂ.૮૪.૭૫ તથા ઉંચામાં ભાવ રૂ.૮૪.૯૯ થઈ રૂ.૮૪.૯૨ બંધ રહ્યા હતા."
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1078, 1464, 1718, 1568,
    lines=[
        "ડોલરનો ઈન્ડેક્સ વધી ઉંચામાં ૧૦૨ પારઃ ભારતમાં છ",
        "મહિના ઈમ્પોર્ટ કવર થાય એટલું ફોરેક્સ રિઝર્વ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# ફોરેક્સ ભાવ Box in Col 4 (1078..1385, y=1575..1818)
draw_box(1078, 1575, 1385, 1818, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
draw_box(1078, 1575, 1385, 1624, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=0.5)
place_exact_display_lines(
    1086, 1580, 1377, 1620,
    lines=["ફોરેક્સ ભાવ"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    1086, 1630, 1210, 1812,
    lines=["ડોલર", "પાઉન્ડ", "યુરો", "યેન", "બ્રેન્ટ ક્રૂડ"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    1215, 1630, 1378, 1812,
    lines=["રૂા. ૮૪.૯૨", "રૂા. ૧૨૬.૫૧", "રૂા. ૧૦૬.૪૦", "રૂા. ૦.૬૦", "૧૦૮ ડોલર"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)

place_exact_body_column(
    1078, 1824, 1385, 2396,
    text=(
        "વિશ્વ બજારમાં ડોલરના ભાવ જોકે યુરોપીયન કરન્સી સામે વધ્યા હતા. યુરોપના વિવિધ શહેરોમાં યુવાનો તોફાને ચડતાં વિશ્વ બજારમાં યુરોપીયન કરન્સી યુરોના ભાવ દબાણ હેઠળ જોવા મળ્યા હતા. વિશ્વ બજારમાં ડોલરનો ગ્લોબલ ઈન્ડેક્સ આજે વધ્યો હતો. ડોલરનો વૈશ્વિક ઈન્ડેક્સ નીચામાં ૧૦૧.૭૭ તથા ઉંચામાં ૧૦૨.૦૮ રહી ૧૦૧.૯૩ રહ્યાના સમાચાર હતા.\n"
        "ચીનમાં બહાર પડનારા જીડીપીના ડેટા પર બજારની નજર રહી હતી. ઈન્ડોનેશિયાની કરન્સીના ભાવ તાજેતરમાં ગબડી એક ડોલર સામે ૧૯ હજાર સુધી ઉતરી જતાં ૩ મહિનાના તળિયે ઈન્ડોનેશિયાની કરન્સી ગબડી ગયાના વાવડ મળ્યા હતા. મુંબઈ બજારમાં રૂપિયા સામે યુરોના ભાવ ૪૬ પૈસા ગબડી નીચામાં ભાવ રૂ.૧૦૬.૨૧ થઈ રૂ.૧૦૬.૪૦ રહ્યા હતા."
    ),
    target_lines=20,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1575, 1718, 2396,
    text=(
        "બ્રિટિશ પાઉન્ડના ભાવ નવ પૈસા ઘટી નીચામાં ભાવ રૂ.૧૨૬.૨૬ થઈ રૂ.૧૨૬.૫૧ રહ્યા હતા. જાપાનની કરન્સી આજે રૂપિયા સામે ૦.૧૭ ટકા ઘટી હતી. ચીનની કરન્સી રૂપિયા સામે ૦.૦૫ ટકા પ્લસમાં રહી હતી. મુંબઈ શેરબજારમાં આજે ઘટાડો તથા વિશ્વ બજારમાં ક્રૂડતેલના ભાવમાં વધ્યા ભાવથી ઘટાડાની ઈમ્પેક્ટ પણ મુંબઈ કરન્સી બજારમાં ડોલર તથા રૂપિયા ભાવ પર દેખાઈ હતી.\n"
        "ભારતના તાજેતરમાં ફોરેક્સ રિઝર્વમાં ઘટાડો થયા પછી હવે કરન્સી બજારમાં રિઝર્વ બેન્કની સક્રિયતા કેવી રહે છે તેના પર બજારના ખેલાડીઓની નજર રહી હતી. કરન્સી બજારમાં સટ્ટારૂપી સોદા તથા તત્વોને કાબુમાં રાખવા રિઝર્વ બેન્ક દ્વારા વિવિધ પગલાંઓ ભરાતા થયા છે અને તેની ઈમ્પેક્ટ પણ કરન્સી બજારમાં દેખાઈ હતી.\n"
        "ભારતમાં હાલ જે ફોરેક્સ રિઝર્વ છે તે આશરે ૬ મહિના તથા ૨૦ દિવસના ઈમ્પોર્ટ કવર માટે ચાલે એટલું પૂરતું છે. ડોલર સામે તાજેતરમાં રૂપિયો ભલે ઉંચકાયો છે પરંતુ આગળ ઉપર ડોલરના ભાવ ફરી ઉંચા જવાની તથા કદાચ રૂ.૧૦૦ને આંબી જવાની શક્યતા જાણકારો બતાવી રહ્યા હતા."
    ),
    target_lines=28,
    first_indent_pt=9.0,
)

# કેશ ફ્યુચર ઓપ્શન Box in Col 4 (1078..1385, y=2410..2958) & Col 5 Top-Bot (1412..1718, y=2410..2639)
draw_box(1078, 2410, 1385, 2488, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1086, 2418, 1377, 2480,
    lines=["કેશ ફ્યુચર ઓપ્શન"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1078, 2494, 1385, 2958,
    paras=[
        ("ફ્યુચર માર્કેટ", "Subhead", "center", 0.0),
        ("- યુનિયન બેંક ઓફ ઈન્ડિયા : (૧૮૧)નો ઓક્ટોબર માસનો ફ્યુચર ૧૮૧ ઉપર ૧૭૪ નો સ્ટોપલોસ રાખી ખરીદો. આગામી દિવસોમાં ટાર્ગેટ-૧ ૧૮૬, ટાર્ગેટ -૨ ૧૮૮ સુધી સુધારાની શક્યતા છે.", "Regular", "leftJustified", 9.0),
        ("- ઓરોબિંદો ફાર્મા : (૧૬૧૮)નો ઓક્ટોબર માસનો ફ્યુચર ૧૬૧૮ નીચે ૧૬૪૦ સ્ટોપલોસ રાખી વેચો. આગામી દિવસોમાં ટાર્ગેટ-૧ ૧૫૯૦, ટાર્ગેટ -૨ ૧૫૬૦ સુધી ઘટાડાની શક્યતા છે.", "Regular", "leftJustified", 9.0),
        ("કેશ માર્કેટ", "Subhead", "center", 0.0),
        ("- ગેબ્રિયલ ઈન્ડિયા : (૧૪૮૬) ૧૪૮૬ ઉપર ૧૪૪૫ સ્ટોપલોસ રાખી ખરીદો. આગામી દિવસોમાં ટાર્ગેટ -૧", "Regular", "leftJustified", 9.0),
    ],
    target_lines=16,
    base_pt=9.6,
)
place_mixed_paras_column(
    1412, 2410, 1718, 2639,
    paras=[
        ("૧૫૦૦, ટાર્ગેટ-૨ ૧૫૩૦ સુધી સુધારાની શક્યતા છે.", "Regular", "leftJustified", 0.0),
        ("- ન્યુલેન્ડ લેબોરેટરીઝ : (૧૯૨૨૦) ૧૯૨૨૦ નીચે ૧૯૩૫૦ સ્ટોપલોસ રાખી વેચો. આગામી દિવસોમાં ટાર્ગેટ -૧ ૧૯૦૦૦, ટાર્ગેટ -૨ ૧૮૪૦૦ સુધી ઘટાડાની શક્યતા છે.", "Regular", "leftJustified", 9.0),
        ("- નિલેશ કોટક", "Bold", "right", 0.0),
    ],
    target_lines=8,
    base_pt=9.6,
)
draw_line(1412, 2642, 1718, 2642, weight_pt=0.85)

# સોના-ચાંદી બજાર Box in Col 5 (1412..1718, y=2655..3025)
draw_box(1412, 2655, 1718, 2732, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1420, 2663, 1710, 2724,
    lines=["સોના-ચાંદી બજાર"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1412, 2738, 1558, 3025,
    paras=[
        ("અમદાવાદ", "Subhead", "center", 0.0),
        ("ચાંદી ચોરસા ૨૧૦૦૦૦-૨૧૩૦૦૦\nચાંદી રૂપુ ૨૦૯૮૦૦-૨૧૨૮૦૦\nચાંદી સિક્કા જુના ૨૪૦૦-૨૭૦૦\nસોનું (૯૯.૯) ૧૪૯૦૦૦-૧૫૧૦૦૦\nસોનું (૯૯.૫) ૧૪૮૭૦૦-૧૫૦૭૦૦\nહોલમાર્ક ૧૪૭૯૮૦", "Regular", "left", 0.0),
        ("મુંબઈ", "Subhead", "center", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)
place_mixed_paras_column(
    1566, 2738, 1718, 3025,
    paras=[
        ("ચાંદી ૨૦૮૭૫૦\nસોનું (૯૯.૫)૧૪૫૩૬૦\nસોનું (૯૯.૯) ૧૪૫૯૪૪", "Regular", "left", 0.0),
        ("રાજકોટ", "Subhead", "center", 0.0),
        ("ચાંદી ૨૧૨૦૦૦\n૨૪ કેરેટ ૧૦ ગ્રામ ૧૫૨૫૦૦\nસીક્કા (૧ ગ્રામ)૧૫૩૦૦\n૨૨ કેરેટ ૧૦ ગ્રામ ૧૩૯૫૦૦", "Regular", "left", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)

# ==============================================================================
# 8. STORY 6 (COLS 6-8, y=1168..1862): નાતાલ તથા નવા વર્ષ માટે અમેરિકા ખાતેથી ગારમેન્ટસના ઓર્ડરમાં ઘટાડો
# ==============================================================================
print("Building Story 6 (US/EU Garment Orders, Cols 6-8)...")
place_exact_display_lines(
    1744, 1168, 2712, 1342,
    lines=[
        "નાતાલ તથા નવા વર્ષ માટે અમેરિકા",
        "ખાતેથી ગારમેન્ટસના ઓર્ડરમાં ઘટાડો"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1744, 1348, 2218, 1438,
    text="મુંબઈ, તા. ૧૯\nઆગામી નાતાલ તથા નવા વર્ષ માટે અમેરિકા ખાતેથી રેડી મેડ ગારમેન્ટસના ભારતીય નિકાસકારોને ઓર્ડરમાં",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 1348, 2712, 1438,
    text="ઘટાડો થયો છે પરંતુ યુનાઈટેડ કિંગડમ (યુકે) તથા યુરોપ ખાતેથી માગ સારી રહેતા દેશના ગારમેન્ટ ઉદ્યોગ માટે સ્થિતિ રાહતરૂપ બની છે.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1444, 2712, 1492,
    lines=["યુકે તથા યુરોપ ખાતેથી માગ સારી રહેતા નિકાસકારોને રાહત"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1498, 2050, 1862,
    text=(
        "ભૌગોલિકરાજકીય અનિશ્ચિતતા વચ્ચે અમેરિકામાં ઊંચા ફુગાવાને કારણે ખરીદદારો સાવચેતીનો સૂર ધરાવી રહ્યા છે.\n"
        "અમેરિકાની બજારમાં નબળાઈને કારણે ભારતના એપરલ નિકાસકારો માટે વર્તમાન નાણાં વર્ષના પ્રથમ છ મહિના ડોલરની દ્રષ્ટિએ નબળા રહ્યા છે એમ એપરલ એક્સપોર્ટ પ્રમોશન કાઉન્સિલના સુત્રોએ જણાવ્યું હતું.\n"
        "સપ્ટેમ્બરમાં રેડીમેડ ગારમેન્ટની નિકાસ ૧.૧૦ અબજ ડોલર રહી હતી જે"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 1498, 2382, 1862,
    text=(
        "વાર્ષિક ધોરણે ૧૩.૭૦ ટકા વૃદ્ધિ દર્શાવે છે, પરંતુ એપ્રિલથી સપ્ટેમ્બરના ગાળાની એકંદર નિકાસ ૬.૨૦ ટકા ઘટી ૭.૨૦ અબજ ડોલર રહી હોવાનું પણ સુત્રોએ ઉમેર્યું હતું. ગયા વર્ષના સમાન ગાળામાં આ આંક ૭.૭૦ અબજ ડોલર રહ્યો હતો.\n"
        "રૂપિયાની દ્રષ્ટિએ સપ્ટેમ્બરમાં નિકાસ વાર્ષિક ધોરણે ૨૨.૯૦ ટકા વધી રૂપિયા ૧૦૮૨૪.૬૦ કરોડ રહી હતી. વર્તમાન નાણાં વર્ષના પ્રથમ છ મહિનામાં રૂપિયાની દ્રષ્ટિએ ગારમેન્ટ નિકાસ ૩.૪૦ ટકા વધી રૂપિયા ૬૯૩૦૦ કરોડ રહી છે."
    ),
    target_lines=12,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1498, 2712, 1862,
    text=(
        "આગામી નાતાલ તથા નવા વર્ષ માટે અમેરિકા ખાતેથી ગારમેન્ટ માટેના ઓર્ડરમાં ૨૫-૩૦ ટકા ઘટાડો જોવા મળ્યો હોવાનું તિરુપુરના નિકાસકારો દાવો કરી રહ્યા છે.\n"
        "જો કે યુરોપ તથા યુકે ખાતેથી ઓર્ડર સંતોષકારક રહ્યા છે અને ભૌગોલિકરાજકીય તાણને પરિણામે જહાજોની હેરફેર પર પડેલી અસરને ધ્યાનમાં રાખી નિકાસકારોએ સામાન્ય કરતા વહેલો માલ રવાના કર્યો છે જેથી તે સમયસર પહોંચી જાય."
    ),
    target_lines=12,
    first_indent_pt=9.0,
)

# ==============================================================================
# 9. STORY 7 (COLS 6-8, y=1874..3255): ખાદ્યતેલોમાં મિશ્ર હવામાન + MARKET TABLES
# ==============================================================================
print("Building Story 7 (Edible Oil Market & Market/Stock Tables, Cols 6-8)...")
place_exact_display_lines(
    1744, 1874, 2712, 2050,
    lines=[
        "ખાદ્યતેલોમાં મિશ્ર હવામાનઃ દશેરા પૂર્વે",
        "માંગ વધીઃ દિવેલ તથા એરંડામાં આગેકૂચ"
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
        "(વાણિજ્ય પ્રતિનિધિ)\n"
        "મુંબઈ,સોમવાર\n"
        "મુંબઈ તેલ-બિયાં બજારમાં આજે વિવિધ દેશી તથા આયાતી ખાદ્યતેલોના ભાવ બેતરફી સાંકડી વધઘટ વચ્ચે અથડાતા રહ્યા હતા. દરમિયાન, દિવેલ તથા હાજર એરંડામાં રેકોર્ડ તેજી આગળ વધી હતી. તહેવારો તથા દશેરા પૂર્વે બજારમાં આજે મોસમી માગ જળવાઈ રહી હતી. વિશ્વ બજારમાં આજે મલેશિયા ખાતે પામતેલ વાયદાના ભાવ નવેમ્બરના ૨૨ પોઈન્ટ તથા ડિસેમ્બરના ૧૦ પોઈન્ટ નરમ રહ્યા હતા. વિશ્વ બજારમાં ક્રૂડતેલના ભાવ વધ્યા મથાળેથી ઘટતાં વૈશ્વિક ખાદ્યતેલોના ભાવ પર તેની ઈમ્પેક્ટ દેખાઈ હતી. મુંબઈ હાજર બજારમાં દિવેલના ભાવ ૧૦"
    ),
    target_lines=17,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 2056, 2382, 2155,
    text=(
        "કિલોદીઠ વધુ રૂ.૧૮ ઉછળતાં હાજર એરંડાના ભાવ ક્વિ.દીઠ રૂ.૮૪૨૦ વાળા રૂ.૮૫૧૫ બોલાતા થયા હતા. સૌરાષ્ટ્ર"
    ),
    target_lines=3,
    first_indent_pt=0.0,
)

# પામતેલ વાયદામાં પ્રવર્તતી નરમાઈ Red Callout Box in Col 7 (2076..2382, y=2161..2270)
draw_box(2076, 2161, 2382, 2270, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    2086, 2168, 2372, 2262,
    lines=[
        "પામતેલ વાયદામાં",
        "પ્રવર્તતી નરમાઈ"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)

place_exact_body_column(
    2076, 2276, 2382, 2442,
    text=(
        "ખાતે સિંગતેલના ભાવ રૂ.૧૭૭૫થી ૧૮૦૦ તથા કોટન વોશના ભાવ રૂ.૧૫૧૦થી ૧૫૧૫ રહ્યા નિર્દેશો હતા.\n"
        "સૌરાષ્ટ્ર ખાતે મગફળીના ભાવ ૨૦ કિલોના જાતવાર રૂ.૧૪૦૦થી ૧૭૦૦"
    ),
    target_lines=5,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2056, 2712, 2442,
    text=(
        "રહ્યા હતા. દરમિયાન, મુંબઈ હાજર બજારમાં આજે ૧૦ કિલોદીઠ ભાવ સિંગતેલના રૂ.૧૮૩૦ જ્યારે કપાસિયા તેલના ભાવ રૂ.૧૫૯૫ રહ્યા હતા. મુંબઈ આયાતી પામતેલના ભાવ રૂ.૧૪૪૫ તથા સોયાતેલના ભાવ રૂ.૧૪૭૦ તથા સનફલાવરના ભાવ રૂ.૧૫૮૫ તથા રિફાઈન્ડના ભાવ રૂ.૧૬૮૦ બોલાઈ રહ્યા હતા. સૌરાષ્ટ્ર ખાતે મોડી સાંજે સિંગતેલના ભાવ રૂ.૧૭૭૫ થી ૧૮૦૦ તથા કોટન વોશના ભાવ રૂ.૧૫૧૫ અને પામતેલના ભાવ રૂ.૧૪૦૨ રહ્યા હતા."
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# રાજકોટ છેલ્લા ભાવ & ચીમનભાઈ માર્કેટ in Col 6 (1744..2050, y=2562..3025)
draw_line(1744, 2562, 2050, 2562, weight_pt=0.85)
draw_box(1744, 2580, 2050, 2656, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2588, 2042, 2648,
    lines=["રાજકોટ છેલ્લા ભાવ"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1744, 2662, 2050, 2786,
    text=(
        "રાજકોટ સીંગતેલ લુઝ ૧૮૦૦\n"
        "રાજકોટ મગફળી ૧૭૮૦-૧૭૯૦\n"
        "સોનુ ૨૪ કેરેટ ૧૫૨૫૦૦\n"
        "૧ કિલો ચાંદી ૨૧૨૦૦૦"
    ),
    target_lines=4,
    align="left",
    first_indent_pt=0.0,
)
draw_box(1744, 2795, 2050, 2869, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2803, 2042, 2861,
    lines=["ચીમનભાઈ માર્કેટ"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1744, 2875, 2050, 3025,
    paras=[
        ("૨૦ કિલો", "Subhead", "center", 0.0),
        ("બટાકા દેશી ૧૦૦-૨૦૦\nબટાકા ડીસા ૨૪૦-૩૨૦\nડુંગળી મહારાષ્ટ્ર ૭૦૦-૧૦૪૦\nડુંગળી એમપી ૭૦૦-૮૪૦", "Regular", "left", 0.0),
    ],
    target_lines=5,
    base_pt=9.6,
)

# અમદાવાદના બજારો in Col 7 (2076..2382, y=2448..2796)
draw_line(2076, 2448, 2712, 2448, weight_pt=0.85)
draw_box(2076, 2464, 2382, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2472, 2374, 2531,
    lines=["અમદાવાદના બજારો"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    2076, 2545, 2224, 2796,
    paras=[
        ("તેલતેલીબિયા", "Subhead", "left", 0.0),
        ("સિંગતેલ નવો ડબો (૧૫ કિલો) ૨૯૫૦-૩૧૫૦\nસિંગતેલ નવો ડબ્બો (૧૫ લીટર) ૨૯૫૦\nકપાસીયાતેલ નવો ડબો (૧૫ કિલો) ૨૫૮૦-૨૭૮૦\nરાઈસ બ્રાન્ડ (૧૫ કિલો) ૨૫૫૦\nસોયાબીન નવો ડબો ૨૬૦૦", "Regular", "left", 0.0),
    ],
    target_lines=12,
    base_pt=8.4,
)
place_exact_body_column(
    2232, 2545, 2382, 2796,
    text=(
        "દિવેલ ૨૪૦૦\n"
        "પામોલીન જુનો ડબો ૨૩૩૦\n"
        "પામોલીન નવો ડબો ૨૪૫૦\n"
        "કોપરેલ ૪૪૦૦\n"
        "વનસ્પતિ ૨૦૦૦-૨૩૦૦\n"
        "મોળું સરસીયું ૨૯૦૦\n"
        "તીખું સરસીયું ૩૦૫૦\n"
        "સનફલાવર ૨૬૫૦\n"
        "મકાઈ તેલ ૨૪૫૦"
    ),
    target_lines=11,
    align="left",
    first_indent_pt=0.0,
)

# છેલ્લા ભાવ in Col 8 (2408..2712, y=2464..2796)
draw_box(2408, 2464, 2712, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2472, 2704, 2531,
    lines=["છેલ્લા ભાવ"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2408, 2545, 2712, 2796,
    text=(
        "મુંબઈ ચાંદી ૨૦૮૭૫૦\n"
        "મુંબઈ સોનું (૯૯.૫) ૧૪૫૩૬૦\n"
        "મુંબઈ સોનું (૯૯.૯) ૧૪૫૯૪૪\n"
        "અમ. ચાંદી ૨૧૩૦૦૦\n"
        "અમ. સોનું (૯૯.૯) ૧૫૧૦૦૦\n"
        "અમ. સોનું (૯૯.૫) ૧૫૦૭૦૦\n"
        "અમ. સિંગતેલ નવો ડબો ૩૧૫૦\n"
        "અમ. કપાસિયા નવો ૨૭૮૦"
    ),
    target_lines=8,
    align="left",
    first_indent_pt=0.0,
)

# NSE સૌથી વધુ ઘટ્યા (Col 7, 2076..2382, y=2805..3255) & BSE સૌથી વધુ ઘટ્યા (Col 8, 2408..2712, y=2805..3255)
draw_box(2076, 2805, 2382, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2813, 2374, 2872,
    lines=["NSE સૌથી વધુ ઘટ્યા"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2076, 2886, 2195, 2916, lines=["કંપની"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2196, 2886, 2305, 2916, lines=["બંધ ભાવ"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2306, 2886, 2382, 2944, lines=["ઘટાડો", "(ટકામાં)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2076, 2948, 2382, 2948, weight_pt=0.75)
place_exact_display_lines(
    2076, 2954, 2210, 3254,
    lines=[
        "એક્સિસ બેંક",
        "ટાટા મોટર્સ પેસે.",
        "ઈન્ફોસીસ",
        "બજાજ ફાય",
        "એપોલો હોસ્પિ.",
        "અલ્ટ્રાટેક",
        "HDFC બેંક",
        "ટ્રેન્ટ",
        "હિંદ લીવર",
        "NTPC",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2212, 2954, 2318, 3254,
    lines=[
        "૧૨૩૬.૦૦",
        "૨૭૮.૦૦",
        "૧૧૩૦.૭૦",
        "૯૫૭.૩૫",
        "૭૭૦૦.૦૦",
        "૧૦૬૫૦.૦૦",
        "૭૧૨.૦૦",
        "૨૮૯૧.૬૦",
        "૧૮૫૩.૨૦",
        "૩૦૯.૦૦",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2322, 2954, 2382, 3254,
    lines=[
        "૪.૧૯",
        "૩.૦૯",
        "૨.૬૩",
        "૨.૫૨",
        "૨.૪૧",
        "૨.૩૬",
        "૨.૩૧",
        "૨.૨૭",
        "૨.૧૪",
        "૧.૯૫",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

draw_box(2408, 2805, 2712, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2813, 2704, 2872,
    lines=["BSE સૌથી વધુ ઘટ્યા"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2408, 2886, 2525, 2916, lines=["કંપની"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2526, 2886, 2635, 2916, lines=["બંધ ભાવ"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2636, 2886, 2712, 2944, lines=["ઘટાડો", "(ટકામાં)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2408, 2948, 2712, 2948, weight_pt=0.75)
place_exact_display_lines(
    2408, 2954, 2542, 3254,
    lines=[
        "એક્સિસ બેંક",
        "અલ્ટ્રાટેક",
        "ઈન્ફોસીસ",
        "બજાજ ફાય",
        "ટ્રેન્ટ",
        "NTPC",
        "HDFC બેંક",
        "હિંદ લીવર",
        "બજાજ ફીન",
        "ભારતી એરટેલ",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2544, 2954, 2650, 3254,
    lines=[
        "૧૨૩૬.૯૦",
        "૧૦૬૨૦.૧૦",
        "૧૧૩૦.૦૦",
        "૯૫૭.૦૦",
        "૨૮૮૬.૦૦",
        "૩૦૯.૦૦",
        "૭૧૧.૬૦",
        "૧૮૫૬.૯૫",
        "૧૭૦૨.૭૫",
        "૧૮૭૨.૭૫",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2654, 2954, 2712, 3254,
    lines=[
        "૩.૮૫",
        "૨.૮૨",
        "૨.૭૨",
        "૨.૫૪",
        "૨.૪૩",
        "૨.૩૭",
        "૨.૨૭",
        "૨.૧૬",
        "૧.૯૭",
        "૧.૬૯",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

# ==============================================================================
# 10. BOTTOM PUBLIC NOTICES (જાહેર નોટિસ) — 100% EDITABLE GOPIKA TEXT & CMYK BAR
# ==============================================================================
print("Building Page 10 Bottom Public Notices (100% Editable Gopika Text)...")

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

# 1. Cols 1-2 Bottom Notice (82..718, 2970..3790)
place_public_notice_2col(
    82, 2970, 718, 3790,
    left_text=(
        "મોજે શીવપુરા\n"
        "ડીસ્ટ્રીક અમદાવાદ, તાલુકો વિરમગામ ના મોજે ગામ શીવપુરા ની સીમનાં ખાતા નંબર ૩૪૧ ના બ્લોક/સર્વે નંબર ૧૦૪ (જુનો સર્વે નંબર ૭૮) ની કુલ ૧-૦૮-૨૫ હે.આરે.ચો.મી. યાને કે ૧૦૮૨૫ ચો.મી. વાળી ખેતીની જમીન (૧) ભગવાનભાઈ હંસરાજભાઈ (૨) જગજીવનભાઈ હંસરાજભાઈ (૩) મીનાબેન ભવાનભાઈ ની પત્ની (૪) કિન્નરીબેન ભવાનભાઈ ની દીકરી તે અમિતકુમારના પત્ની (૫) જીજ્ઞેશકુમાર ભવાનભાઈ પટેલ તથા (૫) આનંદકુમાર જગજીવનભાઈ પટેલનાઓની સહિયારી માલિકી અને પ્રત્યક્ષ કબજા ભોગવટાની તેમજ તેઓના જાત ખેડ હક્કની અને તમામ પ્રકારના કાનૂની વિવાદો અને બોજાથી મુક્ત આવેલ હોવાનું જણાવીને અમારી પાસેથી ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાય ની માંગણી કરેલ છે. આથી સદરહુ જમીન કે તેના કોઈપણ ભાગ ઉપર અન્ય કોઈ નો કોઈ પણ પ્રકાર નો હક્ક, હિસ્સો, ખેડ હક્ક, બોજો, તેમજ રસ્તાનો હક્ક, બાનાખતનો હક્ક,"
    ),
    right_text=(
        "ચાર્જ, ગણોતહક્ક, ઈઝમેન્ટ રાઈટ્સ કે અન્ય કોઈપણ પ્રકારનો લાગભાગ, કબજા-હક્ક, હિત, હિસ્સો, દાવો,તકરાર વિગેરે જે કાંઈપણ હોય તો તેમને તે અંગેની લેખિત જાણ, તેને લગતા લેખિત પુરાવાની પ્રમાણિત નકલો સહીત સ્પીડ પોસ્ટ, એ.ડી. પોસ્ટ દ્વારા આ નોટીસ પ્રસિદ્ધ થયેથી દિન- ૧૫ (પંદર) માં અમોને નીચેના સરનામે કરવી અને જો તેમ કરવામાં નહિ આવેતો સદરહુ જમીન ઉપર અન્ય કોઈનો કોઈપણ પ્રકારનો હક્ક, હિસ્સો, બોજો, રસ્તાનો કે બાનાખતનો હક્ક કે કોઈપણ હક્ક-દાવો વિગેરે કાંઈપણ નથી અને હોય તો તે જતો યાને વેવ કરેલ છે તેમ સમજી મુદત વીતે ટાઈટલ અંગેના અભિપ્રાયનું સર્ટીફીકેટ ઈસ્યુ કરી દઈશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહિ, જેની નોંધ લેશો.\n"
        "અમદાવાદ\n"
        "તારીખ : ૨૦/૧૦/૨૦૨૬\n"
        "જૈમિન રોહિતભાઈ પટેલ, એડવોકેટ\n"
        "૩૧૩૫, ત્રીજો માળ, ટી.આર.પી. મોલ, ઈસ્ટ કોર્ટ, બોપલ, અમદાવાદ-૩૮૦૦૫૮.\n"
        "મો. નં. ૯૯૭૮૯ ૩૨૧૯૯"
    ),
    left_lines=24,
    right_lines=26,
)

# 2. Cols 3-4 Bottom Notice (746..1385, 2970..3790)
place_public_notice_2col(
    746, 2970, 1385, 3790,
    left_text=(
        "મોજેઃ વાવોલ\n"
        "આથી જાહેર જનતા ને જણાવવા નું કે રજીસ્ટ્રેશન ડીસ્ટ્રીકટ ગાંધીનગર, સબ ડીસ્ટ્રીકટ કલોલ, તાલુકા કલોલ ના મોજે ગામ : વાવોલ ની સીમના ખાતા નંબરઃ ૧૩૦૦ ના બ્લોક/સર્વે નંબરઃ ૭૫૮/૦૦૪ (જુના સર્વે નંબરઃ ૧૯૧) ની હે. આરે. ચો.મી ૦-૫૯-૪૫ આકારઃ ૬.૦૮ ની જુની શરત ની ખેતીની જમીન ઉત્પલભાઈ જગદીશભાઈ અમીન રહે. એ/૫૦૧, સમસ્ત એપાર્ટમેન્ટ અર્પણ માનવ મંડળ ની પાછળ,વસ્ત્રાપુર,અમદાવાદ-૩૮૦૦૧૫ ની સ્વતંત્ર માલિકી અને કબજા ભોગવટાની તેમજ તમામ પ્રકારના બોજા રહિત ની આવેલી હોવાનું જણાવી અમારા અસીલ ને બિનખેતી કરાવી ને આપવા ની શરતે વેચાણ આપવા નું નક્કી કરેલ છે અને અમારી પાસે સદરહુ મિલકતના ટાઈટલ ક્લીયરન્સ સર્ટીફીકેટની માંગણી કરેલ છે. તો સદરહુ મિલકત ઉપર કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક-હિસ્સો, દાવો, હિત-સંબંધ, બાનાખત, ઈજમેન્ટ, રાઈટ્સ કે જામીનગીરી તથા"
    ),
    right_text=(
        "ભરણ-પોષણ ના હક્કો કે કોઈપણ વ્યક્તિ, બેન્ક, પેઢી કે સંસ્થા નો બોજો કે દાવો આવેલ હોય તો આ નોટિસ પ્રસિદ્ધ થયેથી દિન-૭ (સાત) માં તમામ પુરાવાની પ્રમાણિત નકલ સહિત લેખિત જાણ રજી.એ.ડી. થી નીચેના સરનામે કરવી. જો મુદતમાં જાણ કરવામાં નહીં આવે તો ઉપરોક્ત દર્શાવેલ મિલકત પરત્વે કોઈનો કોઈપણ પ્રકારનો લાગભાગ, બોજો, હક્ક-હિસ્સો, હિત-સંબંધ કે ભરણ-પોષણના હક્કો કે દાવો આવેલ નથી અને આવેલ હોય તો તે તમામ રાજીખુશીથી જતા (વેવ) કરેલ છે તેમ સમજી મુદત વીત્યે થી અમારા અસીલને ઉપરોક્ત દર્શાવેલ મિલકતનું ટાઈટલ ક્લીયરન્સ સર્ટીફીકેટ આપવામાં આવશે ત્યારબાદ કોઈનો કોઈપણ પ્રકારનો દાવો કે તકરાર ચાલશે નહીં તેની લગતા વળગતાઓએ અને જાહેર જનતાએ નોંધ લેવી.\n"
        "તારીખઃ ૧૯/૧૦/૨૦૨૬\n"
        "હેમરાજ આર દેસાઈ (એડવોકેટ)\n"
        "(૮૩૪૭૨ ૬૩૨૫૩)\n"
        "એફ.એફ.-૮,સેન્ટર પ્લાઝા, સાર્થક ચાર રસ્તા, સોલા રોડ,ઘાટલોડિયા, અમદાવાદ-૩૮૦૦૬૧"
    ),
    left_lines=24,
    right_lines=26,
)

# 3. Cols 5-6 Bottom Notice (1412..2050, 3036..3790)
place_public_notice_2col(
    1412, 3036, 2050, 3790,
    left_text=(
        "જત-ડીસ્ટ્રીકટ સબ ડીસ્ટ્રીકટ અમદાવાદ-૧૪(વસ્ત્રાલ)ના તાલુકા દશક્રોઈ ના મોજે ગામ ઝાણું ની સિમના ખાતા નં. ૧૬૮ ના રે.સર્વે નં. ૧૩૧૮ (જુના બ્લોક/સર્વે નં.-૪૭૭/પૈકી) ની હે.આરે.ચો.મી ૧-૦૬-૭૩ આકાર રૂ. ૨.૦૪ પૈસાવાળી જુની શરતની ખેતી લાયક જમીન તથા રે.સર્વે નં.-૧૩૧૭ (જુના બ્લોક/સર્વે નં.-૪૭૭) ની હે.આરે.ચો.મી ૦-૦૧-૨૪ આકાર રૂ. ૦.૦૬ પૈસાવાળી જુની શરતની ખેતી લાયક જમીન મળી કુલ હે.આરે.ચો.મી ૧-૦૭-૯૭ જુની શરતની ખેતી લાયક જમીન (૧) કાન્તિભાઈ મુળજીભાઈ (૨) પરષોત્તમભાઈ ઉર્ફે પ્રિતેશભાઈ મુળજીભાઈ ના નામે સંયુક્ત માલિકી કબજા ભોગવટામાં આવેલ છે તથા તમામ પ્રકારના બોજાઓમાંથી મુક્ત હોવાનું જણાવી સદર જમીન અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ હોય અમારા અસીલએ અમારી પાસેથી સદર જમીનના ટાઈટલ કલીયર અને માર્કેટેબલ હોવાના"
    ),
    right_text=(
        "અભિપ્રાય અંગેના સર્ટીફીકેટ ની માંગણી કરેલ છે તો સદર જમીનમાં કોઈના બાનાખત, વેચાણ, બક્ષિસ,પાવર,વારસો, હિત,ગીરો કે કબ્જા હક્ક વગેરે અગર કોઈ કોર્ટનો મનાઈ હુકમ ચાલુ હોય તો તેની જાણ લેખિતમાં દસ્તાવેજી પુરાવા સહિત આ નોટિસ પ્રસિદ્ધ થયેથી દિવસ-૧૫ (પંદર) માં નીચેના સરનામે રજી.પોસ્ટથી કરવી (કાયદાથી માન્ય પુરાવા વગર મોકલેલ વાંધા અરજીને ધ્યાને લીધા સિવાય સીધા દફતરે કરવામાં આવશે.) ઉક્ત સમયમર્યાદા વિત્યા બાદ આવનાર વાંધા કે હક્ક દાવા ઉપર કોઈપણ પ્રકારનો લક્ષ આપ્યા સિવાય સદર જમીનનું ટાઈટલ કલીયર સર્ટીફીકેટ ઈસ્યુ કરવામાં આવશે તેની નોંધ લેશોજી.\n"
        "19 OCT 2026\n"
        "નિલેશકુમાર બી.પટેલ\n"
        "(એડવોકેટ એન્ડ નોટરી)\n"
        "ઓફિસ-એ/૧, (ગ્રા.ફ્લોર) મૂર્તિધામ પાર્ક રસપાન ચાર રસ્તા પાસે, નિકોલ, અમદાવાદ-૩૮૨૩૫૦\n"
        "મો.નં.- ૭૮૭૪૩૭૪૪૬૬"
    ),
    left_lines=22,
    right_lines=24,
)

# 4. Cols 7-8 Bottom Notice (2076..2712, 3266..3790)
place_public_notice_2col(
    2076, 3266, 2712, 3790,
    left_text=(
        "રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદ, સબ ડીસ્ટ્રીકટ ધોળકાના ધોળકા તાલુકાના મોજે સરોડા ગામની સીમના બ્લોક/સર્વે નં.૩૨૧ ની કુલ ૧૮૨૧૧ ચો.મીટર (જેમાં ૭૦૮ ચો.મી. પોત ખરાબા સહિત) પૈકી વગર વહેંચાયેલ અમારા હિસ્સાની પ૯૪૫ ચો.મીટર જુ.શ.ની ખેતીની જમીન, શંકરભાઈ ભીમાભાઈ મકવાણા દ્વારા તેઓની સ્વતંત્ર માલિકી અને પ્રત્યક્ષ કબજા ભોગવટામાં આવેલ હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે અને અમારા અસીલે ઉપરોક્ત જમીન અંગે અમારી પાસે ટાઈટલ ક્લીયરન્સ સર્ટીફિકેટની માંગણી કરેલ છે. સબબ"
    ),
    right_text=(
        "સર્વે શખ્સો કે જેઓ ઉપરોક્ત જમીન ઉપર કોઈપણ પ્રકારનો હક્ક, હિત, હિસ્સો, બોજો, બાનાખતના હક્કો ઈત્યાદી ધરાવતા હોય તો તેમણે આ જાહેર નોટીસ પ્રસિધ્ધ થયેથી દિન- ૭ (સાત) ની અંદર દસ્તાવેજી પુરાવા સહિત લેખીતમાં નીચેના સરનામે જાણ કરવાની રહેશે, અને જો તેમ કરવામાં કસુર કે વિલંબ થશે તો ઉપરોક્ત જમીનનું ટાઈટલ ક્લીયરન્સ સર્ટીફિકેટ ઈશ્યુ કરવામાં આવશે, જેની નોંધ લેવી.\n"
        "અમદાવાદ\n"
        "તા. ૨૦-૧૦-૨૦૨૬\n"
        "અમીત વી. પટેલ, એડવોકેટ\n"
        "૯૩, નાલંદા કોમ્પલેક્ષ, વસ્ત્રાપુર, અમદાવાદ-૩૮૦૦૧૫.\n"
        "મો. : ૯૫૧૦૧૮૮૫૦૫."
    ),
    left_lines=16,
    right_lines=18,
)

place_png(0, 3796, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_10_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_10_SameToSame.dns"
    png_path = target_dir / "Page_10_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_10_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_10_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
