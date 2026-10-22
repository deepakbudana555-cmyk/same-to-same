from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 7 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all 5 Business News stories (Edible Oil Imports, Sugar MSP, IT Mutual
  Funds, Jio Platforms IPO, Global Urea Prices)!
- Graphics/Ads (PNG): Top Running Header Bar, 3 Story Photos/Charts,
  and Honda Bottom Half-Page Ad.
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
ASSETS_DIR = DIR_SMAE / "Page_07_Assets"

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
        "title": "Gujarat Samachar — Page 07 (100% Same-to-Same Editable Gopika)"
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
    lo_pt: float = 8.4,
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


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 7 Running Header...")
build_running_header(7, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: EDIBLE OIL IMPORTS (COLS 1-5 TOP)
# ==============================================================================
print("Building Story 1 (Edible Oil Imports, Cols 1-5 Top)...")
place_exact_display_lines(
    82, 200, 1718, 340,
    lines=["ખાદ્યતેલની આયાતમાં ૩.૭%, કિંમતમાં ૧૧%નો વધારો"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.82,
)
place_exact_body_column(
    82, 346, 1050, 434,
    text="અમદાવાદ, તા. ૧૯\nતહેવારોની મોસમની માંગને પહોંચી વળવા ખાદ્યતેલના વેપારીઓએ નોંધપાત્ર પ્રમાણમાં ખાદ્યતેલની આયાત કરી હતી. નવેમ્બર-સપ્ટેમ્બર ૨૦૨૫-૨૬ દરમિયાન ભારતની ખાદ્યતેલની આયાત ૩.૨૭% વધીને",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1064, 348, 1064, 432, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 346, 1718, 434,
    text="૧૫.૧૬૪ મિલિયન ટન થઈ હતી, જે એક વર્ષ અગાઉ ૧૪.૬૮૩ મિલિયન ટન હતી. આ આયાતમાં પામ તેલનો હિસ્સો સૌથી મોટો હતો. સપ્ટેમ્બરમાં, મુખ્ય ખાદ્યતેલોના ભાવમાં પાછલા વર્ષની સરખામણીમાં ૯.૭ થી ૧૧.૨%નો વધારો થયો છે. ડોલર સામે રૂપિયામાં નબળો પડવો એ આનું મુખ્ય કારણ હતું.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 438, 1718, 496,
    lines=["નબળા રૂપિયાને કારણે ખાદ્ય તેલના ભાવમાં વધારો : આયાતમાં પામ તેલનો હિસ્સો સૌથી મોટો"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 504, 386, 1018,
    text="ક્રૂડ પામ તેલના વધુ આગમનને કારણે પામ તેલની આયાત ૫.૩૨% વધીને ૭.૩૫૨ મિલિયન ટન થઈ છે. સોયાબીન તેલની આયાત ૩.૨૫% વધીને ૫.૧૭૬ મિલિયન ટન, જ્યારે સૂર્યમુખી તેલની આયાત ૧.૯૦% ઘટીને ૨.૬૨૪ મિલિયન ટન થઈ હતી. રિફાઈન્ડ ખાદ્ય તેલની આયાત ઘટીને ૦.૭૪ મિલિયન ટન, જ્યારે ક્રૂડ તેલની આયાત વધીને ૧૪.૪૨૩ મિલિયન ટન થઈ હતી.\nરિફાઈન્ડ તેલ કરતાં ક્રૂડ તેલની આયાતમાં મોટો ફેરફાર જોવા મળ્યો છે. રિફાઈન્ડ ખાદ્ય તેલની આયાત ૧.૬૮૯ મિલિયન ટનથી ઘટીને ૦.૭૪ મિલિયન ટન થઈ, જેનાથી કુલ આયાતમાં તેનો હિસ્સો ૧૨% થી ઘટીને ૫% થઈ ગયો.",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 504, 400, 1018, swatch="[Black]", weight_pt=0.75)
place_png(414, 504, 1050, 926, "edible_oil_photo.png")
place_exact_body_column(
    414, 932, 718, 1018,
    text="ક્રૂડ ખાદ્ય તેલની આયાત ૧૨.૯૯૩ મિલિયન ટનથી વધીને ૧૪.૪૨૩ મિલિયન ટન થઈ. આ મુખ્યત્વે એટલા",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(732, 934, 732, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 932, 1050, 1018,
    text="માટે હતું કારણ કે ક્રૂડ પામ તેલ રિફાઈન્ડ પામોલિન આયાતને બદલે બદલાઈ ગયું.\nઆર્જેન્ટિના ભારતમાં ખાદ્ય તેલનો",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(1064, 504, 1064, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 504, 1382, 1018,
    text="સૌથી મોટો સપ્લાયર રહ્યો છે. તેણે કુલ ૩.૪૪૩ મિલિયન ટન ખાદ્ય તેલની નિકાસ કરી છે, જેમાં ૨.૭૧૪ મિલિયન ટન ક્રૂડ સોયાબીન તેલ અને ૭.૨૯ મિલિયન ટન સૂર્યમુખી તેલનો સમાવેશ થાય છે.\nમલેશિયાએ ૨.૮૭૬ મિલિયન ટન પામ તેલ પૂરું પાડ્યું હતું, જ્યારે ઈન્ડોનેશિયાએ ૨.૯૦૫ મિલિયન ટન નિકાસ કર્યું હતું. નેપાળે પણ ભારતમાં ૬.૮૨ મિલિયન ટન શુદ્ધ તેલની નિકાસ કરી હતી, જેમાં ૬.૦૫ મિલિયન ટન શુદ્ધ સોયાબીન તેલનો સમાવેશ થાય છે. નેપાળે શૂન્ય આયાત ડ્યુટીનો લાભ મેળવ્યો હતો.\nગત વર્ષની સરખામણીમાં સપ્ટેમ્બર ૨૦૨૬માં ખાદ્ય તેલના ભાવમાં",
    target_lines=17,
    first_indent_pt=0.0,
)
draw_line(1396, 504, 1396, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 504, 1718, 1018,
    text="નોંધપાત્ર વધારો થયો હતો. આંતરરાષ્ટ્રીય ભાવમાં વધારો અને રૂપિયાનું અવમૂલ્યન આ પાછળના મુખ્ય કારણો હતા. નબળા રૂપિયાને કારણે ખાદ્ય તેલના ભાવમાં વધારો થયો હતો\nજાણકારોના જણાવ્યા અનુસાર, આ દરમિયાન રૂપિયો યુએસ ડોલર સામે રૂા. ૮૮.૩૨થી રૂા. ૯૫.૫૧ પર નબળો પડ્યો, જે લગભગ ૮.૧% ઘટ્યો. આનાથી આયાતી તેલનો ખર્ચ વધુ વધ્યો. ઊંચા આયાત વોલ્યુમ, આંતરરાષ્ટ્રીય ભાવમાં વધારો અને ઘટતા રૂપિયાને કારણે ભારત માટે ખાદ્ય તેલની આયાતનો ખર્ચ વધી રહ્યો છે. તે જ સમયે, ક્રૂડ તેલ તરફના પરિવર્તનથી સોર્સિંગ પદ્ધતિઓ પણ બદલાઈ રહી છે.",
    target_lines=17,
    first_indent_pt=0.0,
)
draw_line(82, 1024, 1718, 1024, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 3. STORY 2: SUGAR MSP HIKE DEMAND (COLS 1-3 BOTTOM)
# ==============================================================================
print("Building Story 2 (Sugar MSP Hike Demand, Cols 1-3 Bottom)...")
place_exact_display_lines(
    82, 1032, 1050, 1218,
    lines=[
        "ખાંડની MSP રૂ. ૩૧ થી વધારીને",
        "રૂ. ૫૦ કરવાની માંગણી તીવ્ર બની"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    82, 1224, 556, 1344,
    text="અમદાવાદ, તા. ૧૯\nમહારાષ્ટ્રમાં ખાંડ મિલના કામદારોએ ખેડૂતોની માંગણીઓના સમર્થનમાં ૨૨ તારીખથી અનિશ્ચિત હડતાળની ધમકી આપી છે. ખેડૂતો અને કામદારો બંનેની પ્રાથમિક માંગ ખાંડના લઘુત્તમ વેચાણ ભાવ (MSP)માં વધારો કરવાની છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 1226, 564, 1342, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 1224, 1050, 1344,
    text="ખેડૂતો કહે છે કે ખાંડ મિલોની નબળી આર્થિક સ્થિતિને કારણે, તેઓ શેરડી માટે સમયસર ચુકવણી મેળવી શકતા નથી. તેઓ માને છે કે ખાંડના લઘુત્તમ વેચાણ ભાવ રૂ. ૫૦ પ્રતિ કિલો વધારવાથી ખાંડ ઉદ્યોગ અને શેરડીના ખેડૂતોને રાહત મળશે. વધુમાં, તેની ગ્રાહકો પર ખાસ અસર થશે નહીં.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1350, 1050, 1468,
    lines=[
        "ખાંડનો લઘુત્તમ વેચાણ ભાવ સાત વર્ષથી પ્રતિ કિલો રૂ. ૩૧",
        "પર અટકી ગયો છે, જ્યારે શેરડીનો FRP વધી રહ્યો છે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1474, 386, 1995,
    text="ખેડૂતો ખાંડના લઘુત્તમ વેચાણ ભાવને વર્તમાન રૂ. ૩૧ રૂપિયા પ્રતિ કિલોથી વધારીને રૂ. ૫૦ રૂપિયા પ્રતિ કિલો કરવાની માંગ કરી રહ્યા છે. તેઓ ઈથેનોલના ખરીદ ભાવને રૂ. ૫૮ રૂપિયાથી વધારીને રૂ. ૭૦ રૂપિયા પ્રતિ લિટર કરવાની પણ માંગ કરી રહ્યા છે.\nછેલ્લા સાત વર્ષમાં શેરડીના વાજબી અને લાભદાયી ભાવ (FRP)માં ૨૬ ટકાથી વધુનો વધારો થયો છે, પરંતુ ખાંડના લઘુત્તમ વેચાણ ભાવમાં માત્ર એક જ વાર સુધારો કરવામાં આવ્યો છે. ફેબ્રુઆરી ૨૦૧૯ પછી ખાંડનો લઘુત્તમ વેચાણ ભાવ વધ્યો નથી અને તે ૩૧ રૂપિયા પ્રતિ કિલો પર સ્થિર રહ્યો છે.",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 1476, 400, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 1474, 718, 1995,
    text="ખાંડ ઉદ્યોગનો સૌથી મોટો ખર્ચ શેરડીની ખરીદી પર થાય છે. ૨૦૨૦-૨૧માં શેરડીનો વાજબી અને લાભદાયી ભાવ ૨,૮૫૦ રૂપિયા પ્રતિ ટન હતો, જે ૨૦૨૬-૨૭ની પિલાણ સીઝન માટે વધારીને ૩,૬૫૦ રૂપિયા પ્રતિ ટન કરવામાં આવ્યો છે. તેનાથી વિપરીત, ફેબ્રુઆરી ૨૦૧૯ થી ખાંડનો લઘુત્તમ વેચાણ ભાવ પ્રતિ ક્વિન્ટલ રૂ. ૩,૧૦૦ પર સ્થિર રહ્યો છે.\nઉત્પાદન ખર્ચ અને અન્ય ખર્ચમાં સતત વધારાને ધ્યાનમાં રાખીને, ખાંડ ઉદ્યોગ લાંબા સમયથી લઘુત્તમ વેચાણ ભાવમાં વધારો કરવાની માંગ કરી રહ્યો છે. ખાંડ ઉદ્યોગના કામદારો ૨૨મી તારીખથી અનિશ્ચિત હડતાળ પર જવાની",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(732, 1476, 732, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 1474, 1050, 1995,
    text="તૈયારી કરી રહ્યા છે\nમહારાષ્ટ્રમાં ખાંડ ઉદ્યોગના કર્મચારીઓએ ૨૨મી તારીખથી અનિશ્ચિત હડતાળ પર જવાની ધમકી આપી છે, જેમાં ખાંડનો લઘુત્તમ વેચાણ ભાવ પ્રતિ કિલો રૂ. ૫૦ કરવાનો સમાવેશ થાય છે. તેમનું કહેવું છે કે લઘુત્તમ વેચાણ ભાવ વધારવાથી રાજ્યની ખાંડ મિલોની નાણાકીય સ્થિતિમાં સુધારો થશે.\nઉદ્યોગના સૂત્રોએ જણાવ્યું હતું કે કેન્દ્ર સરકારે છેલ્લા સાત વર્ષથી ખાંડના લઘુત્તમ વેચાણ ભાવમાં વધારો કર્યો નથી. પરિણામે, બેંકો ખાંડના સ્ટોક સામે જામીનગીરી તરીકે ખાંડ મિલોને લોન આપતી વખતે સાવચેતી રાખે છે.",
    target_lines=17,
    first_indent_pt=0.0,
)
draw_line(1064, 1028, 1064, 1995, swatch="[Black]", weight_pt=0.75)

# ==============================================================================
# 4. STORY 3: IT MUTUAL FUNDS HOLDINGS (COLS 4-5 BOTTOM)
# ==============================================================================
print("Building Story 3 (IT Mutual Funds Holdings, Cols 4-5 Bottom)...")
place_exact_display_lines(
    1078, 1032, 1718, 1185,
    lines=[
        "સપ્ટેમ્બર ત્રિમાસિકમાં IT કંપનીઓમાં",
        "મ્યુ. ફંડોનું હોલ્ડિંગ્સ તળિયે ઉતર્યું"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1078, 1192, 1718, 1318,
    text="મુંબઈ, તા. ૧૯\nઆર્ટિફિશિયલ ઈન્ટેલિજન્સ (એઆઈ) સંબંધિત ચિંતા, વૈશ્વિક ગ્રાહકો દ્વારા નબળા ખર્ચ તથા વિકાસ પર પ્રતિકૂળ અસરને પરિણામે વર્તમાન નાણાં વર્ષના સપ્ટેમ્બર ત્રિમાસિક ગાળામાં આઈટી કંપનીઓમાં મ્યુચ્યુઅલ ફંડસનો હોલ્ડિંગ્સ ઓલ ટાઈમ નીચી સપાટીએ પહોંચ્યું છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 1324, 1718, 1435,
    lines=[
        "ફન્ડોની યાદીમાં અગાઉ અગ્રેસર રહેતી",
        "આઈટી કંપનીઓ હવે પાછલા ક્રમે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_png(1078, 1455, 1382, 1585, "it_funds_chart.png")
place_exact_body_column(
    1078, 1592, 1382, 1995,
    text="આઈટી ક્ષેત્ર પર દબાણને પરિણામે ઈન્ફોસિસ તથા ટીસીએસ જેવી ટોચની આઈટી કંપનીઓ જે એક સમયે ફન્ડોની યાદીમાં અગ્રેસર રહેતી હતી તે હવે યાદીમાંથી નીકળી ગઈ છે.\n૨૦૨૫ના અંતે ફન્ડોની ઈક્વિટી એસેટ અન્ડર મેનેજમેન્ટ (એયુએમ)માં આઈટી સ્ટોકસનો હિસ્સો જે ૭.૬૦ ટકા હતો તે સપ્ટેમ્બર ત્રિમાસિકના અંતે ઘટી ૫.૩૦ ટકા પર આવી ગયો છે.\nઆઈટી સ્ટોકસમાં વર્તમાન કરેકશન માટે ડી-રેટિંગ કારણભૂત છે નહીં કે તેમની આવકમાં ઘટાડો એમ એક રિસર્ચ પેઢીના",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1396, 1442, 1396, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1442, 1718, 1995,
    text="રિપોર્ટમાં જણાવાયું હતું.\nડીસેમ્બર, ૨૦૨૫ના અંતે ફન્ડો પાસેના આઈટી સ્ટોકસનું એકંદર મૂલ્ય જે રૂપિયા ૩.૮૮ લાખ કરોડ રહ્યું હતું તે સપ્ટેમ્બર ત્રિમાસિકમાં ઘટી રૂપિયા ૨.૯૭ લાખ કરોડ રહ્યું હતું. નવેમ્બર, ૨૦૨૫માં આ મૂલ્ય રૂપિયા ૪.૦૩ લાખ કરોડ વિક્રમી રહ્યું હતું.\n૨૦૨૬ના પ્રારંભમાં મ્યુચ્યુઅલ ફન્ડસના ટોચના પાંચ હોલ્ડિંગ્સમાં ઈન્ફોસિસનો સમાવેશ થતો હતો તે સપ્ટેમ્બરમાં ઘટી ૧૦માં સ્થાને પહોંચી ગઈ છે. આવીજ સ્થિતિ ટીસીએસ તથા અન્ય આઈટી કંપનીઓના સ્ટોકસમાં જોવા મળી છે.\nએઆઈને કારણે આઈટી ક્ષેત્ર પર પ્રતિકૂળ અસર પડશે તેવી ગણતરીએ ફન્ડ મેનેજરો આઈટી ક્ષેત્રમાંથી પીછેહઠ કરી રહી હોવાનું પણ રિપોર્ટમાં જણાવાયું હતું.",
    target_lines=18,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. STORY 4: JIO PLATFORMS IPO (COLS 6-8 TOP RED BOX)
# ==============================================================================
print("Building Story 4 (Jio Platforms IPO, Cols 6-8 Top Red Box)...")
draw_box(1744, 202, 2715, 1447, stroke_swatch="GsRedBanner", stroke_weight_pt=2.5)
place_exact_display_lines(
    1754, 208, 2705, 254,
    lines=["શેર દીઠ રૂ.૧૦૬૫થી રૂ.૧૧૧૯ પ્રાઈસ બેન્ડ નક્કી કરાઈ"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1754, 260, 2705, 452,
    lines=[
        "જિયો પ્લેટફોર્મ્સનો રૂ.૩૦,૨૧૩ કરોડનો",
        "IPO ભારતમાં વિક્રમ સર્જવાની તૈયારીમાં"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 460, 2056, 954,
    text="મુંબઈ, તા. ૧૫\nરિલાયન્સ ઈન્ડસ્ટ્રીઝની ડિજિટલ અને ટેલિકોમ કંપની જિયો પ્લેટફોર્મ્સ લિમિટેડનો સંપૂર્ણ ફ્રેશ ૨૭ કરોડ શેરોનો રૂ.૩૦,૨૧૩ કરોડનો આઈપીઓ-ઈનિશિયલ પબ્લિક ઓફરિંગ ભારતીય શેર બજારના ઈતિહાસમાં સૌથી મોટો આઈપીઓ બનવાની તૈયારીમાં છે. કંપનીએ આજે આઈપીઓ માટે શેર દીઠ રૂ.૧૦૬૫થી રૂ.૧૧૧૯ પ્રાઈસ બેન્ડ નક્કી કરી છે. આઈપીઓ ૨૧, ઓક્ટોબરના ખુલશે અને ૨૩, ઓક્ટોબર ૨૦૨૬ના બંધ થશે. જે પ્રાઈસ બેન્ડના ઉપરના ભાવે વેલ્યુ આશરે રૂ.૧૦.૩ લાખ કરોડ એટલે કે લગભગ ૧૦૮ અબજ ડોલર થાય છે. આઈપીઓમાં શેર માટે લઘુતમ લોટ ૧૨ શેર રાખવામાં આવ્યો છે.\nકંપનીના મેનેજિંગ ડિરેક્ટર આકાશ અંબાણીએ જણાવ્યું હતું કે, આ સંપૂર્ણ ઈસ્યુ ફ્રેશ શેરોનો છે. જિયો પ્લેટફોર્મ્સ દેવા મુક્ત, એટલે કે નેટ ડેટ ફ્રી કંપની બનવાની દિશામાં આગળ વધી રહી છે. આઈપીઓમાંથી મળનારી રકમનો ઉપયોગ",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_box(1758, 960, 2056, 1066, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    1764, 966, 2050, 1060,
    lines=[
        "કંપની નેટ ડેટ ફ્રી બનવાની દિશામાં",
        "આગળ વધી રહી છે : આકાશ અંબાણી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 1072, 2056, 1318,
    text="મુખ્યત્વે રિલાયન્સ જિયો ઈન્ફોકોમના દેવાની ચુકવણી માટે કરવામાં આવશે. જિયોની ભવિષ્યની વૃદ્ધિ માટે ફાઈવ-જી, આર્ટિફિશિયલ ઈન્ટેલિજન્સ (એઆઈ), બ્રોડબેન્ડ અને પોતાની ટેકનોલોજી વિકસાવવાની વ્યૂહરચના પર ભાર મૂકવામાં આવ્યો છે. જિયો માત્ર ટેલિકોમ સર્વિસિઝ પૂરતી મર્યાદિત રહેવા માંગતું નથી. કંપની ગ્રાહકોને વધુ ડિજિટલ સર્વિસિઝ આપીને પ્રતિ ગ્રાહક આવક વધારવા માગે છે.\nચીન સિવાય જિયો વિશ્વનો સૌથી મોટો ફાઈવ-જી ગ્રાહક",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2068, 460, 2068, 1318, swatch="[Black]", weight_pt=0.75)
place_png(2080, 462, 2705, 800, "jio_ipo_photo.png")
place_exact_body_column(
    2080, 806, 2705, 1318,
    text="બેઝ ધરાવે છે. આ ઉપરાંત તેમણે કહ્યું હતું કે, કંપની પોતાની સંપૂર્ણ ટેકનોલોજી સિસ્ટમ્સનો ઉપયોગ કરીને વિદેશી ટેલિકોમ કંપનીઓ સાથે ભાગીદારી કરવા માગે છે. કંપનીનો ઉદ્દેશ ટેકનોલોજી વેચવાનો નહીં, પરંતુ મેનેજ્ડ સર્વિસિઝ દ્વારા વૈશ્વિક બજારમાં સ્થાન મજબૂત કરવાનો છે. કંપનીએ ૬જીના વ્યવસાયિક અમલીકરણની શરૂઆત ૨૦૩૦ના દાયકાના પ્રારંભમાં થવાની અપેક્ષા તેમણે વ્યક્ત કરી હતી.\nકંપનીના ડિરેક્ટર ઈશા અંબાણીએ જણાવ્યું હતું કે, આઈપીઓનું મૂલ્યાંકન લાંબાગાળાના રોકાણકારો માટે આકર્ષક બનાવવાનો પ્રયાસ કરવામાં આવ્યો છે. કોટક મહિન્દ્રા બેંકના સ્થાપક ઉદય કોટકે જણાવ્યું હતું કે, જિયો પ્લેટફોર્મ્સના આઈપીઓનું વેલ્યુએશન નાણાકીય વર્ષ ૨૦૨૫-૨૬ની કમાણીના આધારે લગભગ ૩૪ ગણું પી/ઈ થાય છે, જ્યારે તેના નજીકના સ્પર્ધકનું વેલ્યુએશન લગભગ ૪૧ ટાઈમ્સ-ગણું છે. આઈપીઓના શેર ભાવ નિર્ધારિત કરતી વખતે વૈશ્વિક સંસ્થાકીય રોકાણકારો સાથેની મીટિંગો અને તેમના પ્રતિસાદને ધ્યાનમાં લેવામાં આવ્યા હતા.",
    target_lines=17,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1754, 1324, 2705, 1440,
    lines=[
        "આઈપીઓનું વેલ્યુએશન લાંબાગાળાના રોકાણકારો",
        "માટે આકર્ષક બનાવવાનો પ્રયાસ : ઈશા અંબાણી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# ==============================================================================
# 6. STORY 5: GLOBAL UREA PRICE DROP (COLS 6-8 MIDDLE)
# ==============================================================================
print("Building Story 5 (Global Urea Price Drop, Cols 6-8 Middle)...")
place_exact_display_lines(
    1744, 1456, 2715, 1630,
    lines=[
        "પૂરવઠો વધવા સાથે યુરિયાની",
        "વૈશ્વિક કિંમતમાં નોંધપાત્ર ઘટાડો"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1744, 1636, 2222, 1726,
    text="મુંબઈ, તા. ૧૯\nપૂરવઠામાં વધારાને પગલે યુરિયાનો આયાત ખર્ચ મેની સરખામણીએ ૬૦ ટકા જેટલો નીચે આવી ગયાનું સરકારી",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 1638, 2229, 1724, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 1636, 2715, 1726,
    text="સૂત્રોએ જણાવ્યું હતું. મેમાં યુરિયાનો ટન દીઠ ભાવ જે ૯૪૫ ડોલર હતો તે હાલમાં ઘટી ૩૯૦ ડોલર આસપાસ આવી ગયો છે.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1732, 2715, 1796,
    lines=["દેશમાં ખરીફ વાવણીની કામગીરી સમાપ્ત થતા માગ પણ ઘટી"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1802, 2052, 1995,
    text="સપ્ટેમ્બરમાં યુરિયાના આંતરરાષ્ટ્રીય ભાવમાં ૧૫ ટકા ઘટાડો નોંધાયો છે એમ ફર્ટિલાઈઝર મંત્રાલયના સૂત્રોએ જણાવ્યું હતું. આયાત સ્રોતો વધારવાના સરકારના પ્રયાસોને કારણે યુરિયાની આયાત હવે ઓમાન, મલેશિયા, વિયેતનામ, જ્યોર્જિયા, નાઈજિરિયા, રશિયા સહિતના",
    target_lines=7,
    first_indent_pt=9.0,
)
draw_line(2064, 1804, 2064, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1802, 2382, 1995,
    text="વિવિધ દેશો ખાતેથી થઈ રહી છે.\nમેમાં ખરીફ મોસમની વાવણી પહેલા યુરિયાની માગ વધતા ભાવમાં વધારો જોવા મળ્યો હતો. જો કે હવે ખરીફ મોસમનું વાવેતર પૂરુ થયું છે ભારતની યુરિયાની માગ ઘટી જતા આંતરરાષ્ટ્રીય ભાવ નરમ પડ્યા હોવાનું સૂત્રોએ વધુમાં",
    target_lines=7,
    first_indent_pt=0.0,
)
draw_line(2395, 1804, 2395, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1802, 2715, 1995,
    text="જણાવ્યું હતું.\nગત નાણાં વર્ષમાં ખાતર સબસિડી પેટે રૂપિયા ૨.૧૭ લાખ કરોડનો ખર્ચ થયો હતો તેની સરખામણીએ વર્તમાન વર્ષમાં આ આંક રૂપિયા ૨૦,૦૦૦થી રૂપિયા ૨૨૦૦૦ કરોડ વધુ રહેવાનો અંદાજ મુકાઈ રહ્યો છે.",
    target_lines=7,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. PLACE BOTTOM HONDA AD (PNG)
# ==============================================================================
print("Placing Bottom Honda Half-Page Advertisement...")
place_png(0, 2005, 2800, 3974, "ad_honda_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_07_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_07_SameToSame.dns"
    png_path = target_dir / "Page_07_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_07_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_07_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
