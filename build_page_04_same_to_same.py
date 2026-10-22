from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 4 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all 7 stories/columns/tables on Page 4!
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
ASSETS_DIR = DIR_SMAE / "Page_04_Assets"

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
        "title": "Gujarat Samachar — Page 04 (100% Same-to-Same Editable Gopika)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCyanBorder", "color": "#008bd0"}},
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
print("Placing Page 4 Running Header...")
build_running_header(4, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: PORBANDAR 'REEL POLITICS' (COLS 1-3 TOP)
# ==============================================================================
print("Building Story 1 (Porbandar Reel Politics, Cols 1-3 Top)...")
place_exact_display_lines(
    82, 200, 1050, 246,
    lines=["પોરબંદરમાં કેન્દ્રીય મંત્રીનું ‘રીલ પોલિટિક્સ’"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 254, 1050, 462,
    lines=[
        "ઝેન-ઝીને રીઝવવા મંત્રીની સોશિયલ",
        "મીડિયા ઈન્ફ્લુએન્સર્સ સાથે બેઠક!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 468, 556, 620,
    text="પોરબંદર,સોમવાર\nપોરબંદરની મુલાકાતે આવેલા કેન્દ્રીયમંત્રી ડો.મનસુખ માંડવિયા દ્વારા એક હોટલમાં સોશિયલ મીડિયા કન્ટેન્ટ ક્રિએટરો અને ઈન્ફ્લુએન્સર્સ",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 470, 564, 618, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 468, 1050, 620,
    text="સાથે ખાસ બેઠક યોજવામાં આવતાં તેમણે વાસ્તવિક જનસમસ્યાઓને બદલે પોતાની તરફેણમાં પ્રચાર ઊભો કરવાનો પ્રયાસ કર્યાની તીવ્ર પ્રતિક્રિયા સ્થાનિક રાજકીય વર્તુળોમાં પ્રવર્તી રહી છે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 626, 1050, 742,
    lines=[
        "વાસ્તવિક વિકાસના પ્રશ્નો પડખે મુકાતાં રોષ, ‘રીલ્સથી",
        "નહીં, રિઝલ્ટથી જ મત મળશે’- જનતામાં ઉઠેલો સૂર"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 748, 386, 1188,
    text="દિલ્હીથી ઝેન-ઝી અને યુવાનોને આકર્ષવા માટે મળેલી સૂચનાઓ મુજબ પરંપરાગત સભા-સરઘસના બદલે ડિજિટલ માધ્યમનો આશરો લેવાયો હોવાનું સામે આવ્યું છે, જ્યાં કેન્દ્રીયમંત્રીએ ક્રિએટરોને સોશિયલ મીડિયાના યોધ્ધા ગણાવીને ભોજન અને ભેટ-સોગાદો સાથે સંવાદ સાધ્યો હતો.\nપોરબંદરમાં ઉદ્યોગોના વાયદાઓ છતાં વાસ્તવિક અમલવારીનો અભાવ, રોજગારીની તકો, મોંઘવારી, ખેડૂતોના પાકના યોગ્ય ભાવ અને સરકારી હોસ્પિટલમાં સુવિધાઓની કમી જેવા મૂળભૂત પ્રશ્નો આજે પણ અણઉકેલ રહ્યા છે. આ ઉપરાંત, જેતપુરના સાડી ઉદ્યોગનું કેમિકલયુક્ત પ્રદૂષિત પાણી પોરબંદરના",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(400, 750, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 748, 718, 1188,
    text="દરિયામાં ઠાલવવાના વિવાદિત પ્રોજેક્ટ મુદ્દે જળવાઈ રહેલું મૌન, બંદરમાં છેલ્લા કેટલાય મહિનાઓથી છવાયેલું અંધારું તેમજ અસ્માવતી ઘાટ તરફ જતા માર્ગ પર લાઈટોના અભાવે માછીમારો સામે સર્જાતું અકસ્માતનું જોખમ જેવા સળગતા સવાલો સામે પ્રજા જવાબ માંગી રહી છે.\nલોકોમાં ઉઠેલા આક્રોશ મુજબ, માત્ર હા જી હા કરતા મર્યાદિત કન્ટેન્ટ ક્રિએટરો સાથે હસી-મજાક કરીને કે સેલ્ફી અને રીલ્સ બનાવીને જમીની વાસ્તવિકતાઓ બદલાઈ શકતી નથી. પોરબંદરની પ્રજા હવે જાગૃત થઈ ચૂકી છે, અને ખોટા આત્મીય સંવાદો કે સોશિયલ મીડિયાના ચમકતા ફિલ્ટર્સ પાછળ છુપાયેલી મુશ્કેલીઓને ઓળખી ગઈ છે. જનતા",
    target_lines=15,
    first_indent_pt=0.0,
)
draw_line(732, 750, 732, 1348, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 748, 1050, 918,
    text="સ્પષ્ટપણે માની રહી છે કે, લોકોના પાયાના પ્રશ્નોનું નિરાકરણ લાવવાથી જ લોકચાહના મળે છે. તેથી નેતાઓએ એ સ્પષ્ટ સમજવું પડશે કે,ચૂંટણીઓમાં મત રીલ્સથી નહીં પરંતુ પ્રશ્નોના નિરાકરણ માટે લાવેલા રિઝલ્ટથી જ મળશે.",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(746, 925, 1050, 925, swatch="[Black]", weight_pt=0.85)

# Story 2: Col 3 Middle (Ahmedabad Temperature 37C)
print("Building Story 2 (Ahmedabad Temperature, Col 3 Middle)...")
place_exact_display_lines(
    746, 932, 1050, 1012,
    lines=[
        "અમદાવાદમાં હજુ પાંચ દિવસ",
        "તાપમાન ૩૭ની આસપાસ જ રહેશે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1018, 1050, 1348,
    text="અમદાવાદ, સોમવાર\nઅમદાવાદમાં ગરમીનું પ્રમાણ યથાવત્ રહેતાં સરેરાશ મહત્તમ તાપમાનનો પારો ૩૭.૧ ડિગ્રીએ નોંધાયો હતો. હજુ આગામી પાંચ દિવસ અમદાવાદનું તાપમાન ૩૭ ડિગ્રીની આસપાસ જ રહેવાની આગાહી છે. રાજ્યમાંથી અન્યત્ર રાજકોટમાં ૪૦.૮, ભુજમાં ૩૯, સુરતમાં ૩૭.૭, વડોદરામાં ૩૭.૬, ભાવનગરમાં ૩૬.૪ ડિગ્રી સરેરાશ મહત્તમ તાપમાન નોંધાયું હતું.",
    target_lines=11,
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. STORY 3: 'VAAT VAATMA' COLUMN (COLS 4-5 TOP)
# ==============================================================================
print("Building Story 3 (Vaat Vaatma Column, Cols 4-5 Top)...")
draw_box(1078, 195, 1718, 1352, stroke_swatch="GsCyanBorder", stroke_weight_pt=2.5)
place_png(1088, 202, 1708, 308, "vaat_vaatma_banner.png")
place_exact_display_lines(
    1094, 314, 1702, 382,
    lines=["નવરાત્રિ પાસમાં ‘અનામત’ ?"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1092, 388, 1390, 1342,
    text="તમે માર્ક કરજો... નવરાત્રિના પાસ જેની પાસે પહોંચવા જોઈએ એવા તરવરિયા જુવાનિયાઓને તો માંડ સરેરાશ ‘દોઢ’ જ પાસ મળતા હોય છે !\nબીજી બાજુ, ગરબાનાં ત્રણ આંટા મારતાં તો હાંફ ચડી જાય એવા અંકલો અને આન્ટીઓ પાસે રોજના સરેરાશ ચાર પાસ હોય છે !\nએટલે જ અમને લાગે છે કે ગરબાના પાસમાં ‘અનામત’ સિસ્ટમ હોવી જોઈએ!\nજુઓ...\n* * *\n૫૦ ટકા પાસ તો મહિલાઓ માટે જ અનામત રાખો ! કેમકે મહિલાઓ છે, તો જ ગરબાઓ ‘જોવાલાયક’ બને છે !\nછતાં કોઈ યુવક ‘બોબી ડાર્લિંગ’ બનીને આવી જાય તો સીધો એને સ્ટેજ પર ચડાવી દેવાનો !\n* * *\n૧૦ ટકા પાસ કાનના ડોક્ટરો માટે રાખો ! કેમકે સ્પીકરોના ખતરનાક અવાજથી ભલભલાના કાનના પડદા ‘હચમચી’ જાય છે !\nકાનમાં એવી ધાક પડી જાય છે કે સાલું બીજા દિવસે સવારે એમ જ લાગે છે કે બોસ, કંઈ સંભળાતું કેમ નથી ? (મૂળ તો આઠ વાગ્યાનું એલાર્મ નહોતું સંભળાયું.)\nજો ડોક્ટરો ‘ઘટનાસ્થળ’ પર હાજર",
    target_lines=29,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1398, 390, 1398, 1340, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1406, 388, 1704, 1342,
    text="હોય તો એમને શોધીને ટ્રિટમેન્ટ લઈ શકાયને ?\n* * *\nપાંચ ટકા પાસ ગળાનાં ડોક્ટરો માટે રિઝર્વ રખાવો ! કેમકે સ્પીકરોનાં ભયંકર ઘોંઘાટમાં આપણાં ઓળખીતાં જોડે ઝખ મારીને ઊંચા અવાજે બે મિનિટ વાતો કરીએ, એમાં તો ગળાં છોલાઈ જાય છે !\nબીજું, આ ડોક્ટરો ‘ઓન-ધ-સ્પોટ’ ટ્રિટમેન્ટમાં ૧૫ ટકા ડિસ્કાઉન્ટ આપે તો પણ ઘણું છે !\n* * *\nઅચ્છા, ૨૫ ટકા પાસ કોલેજિયનો માટે, ૧૨ ટકા સિનિયર સિટીઝનો માટે, ૧૦ ટકા નાનાં બાળકો માટે અને બે ટકા પાસ મહિલા પોલીસોને આપો. બરાબર છે ?\n* * *\nઅને છેલ્લે... ૫૦ ટકા માત્ર ‘જોવા માટે’ આવનારા ક્રાઉડ માટે અનામત રાખો !\nએક મિનિટ ! તમે કહેશો કે મન્નુભાઈ, તમે ઓલરેડી ૧૧૪ ટકા તો ગણાવી ચૂક્યા છો ! એમાં ઉપરથી બીજા ૫૦ ટકા ક્યાંથી ધૂસાડવાના ?\nતો મિત્રો, આયોજકો એ જ કહે છે ને ? પેલા વધારાના ૫૦ ટકાને એન્ટ્રી આપી દે છે એમાં જ તો ગરબા રમવાની જગ્યા બચતી નથી !\n- મન્નુ શેખચલ્લી",
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
    lines=["બે મેગાવોટથી વધુના સોલાર પ્લાન્ટથી વીજ ઉત્પાદન પર અંકુશ"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1744, 252, 2715, 412,
    lines=[
        "સરકારને સોલાર પાવરમાં રસ નથી, ખાનગી",
        "વીજકંપનીના લાભાર્થે સોલાર પર કાપ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 418, 2222, 594,
    text="(પ્રતિનિધિ તરફથી) અમદાવાદ,સોમવાર\nવીજળીની અછતને કારણેએ વીજકટોકટી તરફ ધકેલાઈ રહેલા ગુજરાતની સરકાર આશ્ચર્યજનક રીતે સૌર ઉર્જાથી વીજળી પેદા કરનારાઓને ૨૦ ટકાથી માંડીને ૭૦ ટકા ઓછી વીજળી પેદા કરવાની ફરજ પાડી રહી છે. આઘાતજનક બાબત તો એ છેકે પ્રદુષણ વિના જ પેદા થતી અને સૂરજ તપતો હોય ત્યારે વીજ ઉત્પાદન અટકાવી ન શકાતું હોવા છતાંય ગુજરાત સરકાર તરફથી બે મેગાવોટથી",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 420, 2229, 592, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 418, 2715, 594,
    text="વધુ વીજળી પેદા કરવાની ક્ષમતા ધરાવતા ઉત્પાદકોને તેમની કુલ ઉત્પાદન ક્ષમતાના ૭૦ ટકાથી માંડીને ૨૦ ટકા જેટલી ઓછી વીજળી પેદા કરવાની ફરજ પાડી રહ્યા છે. સૌર ઉર્જાથી વીજળી પેદા કરનારાઓ પાસે ઓછી વીજળી પેદા કરવાનો કોઈ રસ્તો નથી અને સ્ટોરેજ કરવાનો પણ કોઈ રસ્તો ન હોવા છતાંય ગુજરાત સરકારની વીજ કંપનીઓ તેમને ઈ-મેઈલ પાઠવીને માત્ર ૩૦, ૪૦, ૫૦ ટકા ૮૦ ટકા વીજળીનું જ ઉત્પાદન કરવા જણાવી રહી છે.",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 602, 2715, 720,
    lines=[
        "સોલાર પાવરની વીજળીનો સંગ્રહ ન થઈ શકતો હોવા છતાં",
        "ઉત્પાદકોને વીજ ઉત્પાદનમાં કાપ મૂકવા સરકારની સૂચના"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 726, 2052, 1348,
    text="બીજીતરફ ગુજરાતના ઉદ્યોગો અને રહેઠાણના વીજવપરાશકારોને યુનિટદીઠ રૂા. ૮ના ભાવની વીજળીના ખર્ચનો બોજ વેંઢારવો પડી રહ્યો છે. બે મેગાવોટથી વધુની ઉત્પાદન ક્ષમતા ધરાવતા ગુજરાતના ૧૫૦૦થી ૨૦૦૦ જેટલા સૌર ઉર્જા ઉત્પાદકો સરકારી વીજ પુરવઠા કંપનીઓને યુનિટદીઠ માત્ર રૂા. ૨.૭૬થી ૨.૯૫ના ભાવે વીજળી આપી રહ્યા હોવા છતાંય અને તેમની વીજળી ખરીદી લેવાના સરકારે કરાર કર્યા હોવા છતાંય ખાનગી વીજ કંપનીઓને ઘી કેળાં કરાવવા માટે સૌર ઉર્જાથી વીજળી પેદા કરનારાઓને ઓછી વીજળીનું ઉત્પાદન કરવાની ફરજ પાડવામાં આવી રહી છે. હજી ૧૮મી ઓક્ટોબરે જ તેમને તેમની કુલ ક્ષમતાથી ૨૦ ટકા ઓછી વીજળી પેદા કરવાનો આદેશ કરવામાં આવ્યો હતો. આ અગાઉ તો તેમને કુલ ક્ષમતાના ૭૦",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2064, 728, 2064, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 726, 2382, 1072,
    text="ટકાથી માંડીને ૫૦ ટકા ઓછું ઉત્પાદન કરવાના આદેશો આપવામાં આવ્યા હતા. બીજીતરફ તેમની વીજળીનો સંગ્રહ ન થઈ શકતો હોવાથી વેડફાઈ રહી છે. ૧૫૦૦થી ૨૦૦૦ એકમોનો મળીને રોજના અંદાજે ૧ કરોડ યુનિટ વીજળીનો વેડફાટ થઈ રહ્યો છે.૨૩મી સપ્ટેમ્બરે અંદાજે ૧૫૦૦થી ૨૫૦૦ જેટલા સોલાર પાવર જનરેટર્સને મેઈલ પાઠવીને તેમની સોલાર વીજળીના",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_line(2395, 728, 2395, 1072, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 726, 2715, 1072,
    text="ઉત્પાદનનો સપ્લાય ૫૦ ટકા ઓછો કરી દેવા જણાવ્યું છે. ગુજરાતની વીજ કંપનીઓને વડોદરાથી સ્ટેટ લેવલ ડિસ્પેચ સેન્ટરે કરેલા મેઈલને વાંચતા સ્પષ્ટ થાય છે કે ૨૩મી સપ્ટેમ્બર ૨૦૨૬ પહેલા આ વીજ સપ્લાયમાં ૭૦ ટકા કાપ મૂકવાનો મેસજે આપ્યો હતો. આ ૭૦ ટકા વીજ સપ્લાય કટમાંથી હવે ૫૦ ટકા વીજ સપ્લાય કટ કરવાની સૂચના છે.",
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
    lines=["કથળેલી વહીવટી કામગીરીનો ચિતાર"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    2076, 1140, 2715, 1280,
    lines=[
        "સરકારી લાભો મેળવવા ૨૨,૨૬૪",
        "લોકોએ સેવા સેતુની રાહ જોવી પડી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1286, 2715, 1404,
    text="અમદાવાદ, સોમવાર\nઅમદાવાદ શહેરમાં અત્યાર સુધીમાં યોજાયેલા સેવા સેતુના ૭ કાર્યક્રમોમાં ૨૨,૨૬૪ અરજીઓનો નિકાલ કરાયો હોવાનો દાવો કરાયો છે. જેનો સીધો મતલબ એવો પણ થાય કે, જુદા જુદા સરકારી લાભો મેળવવા માટે આટલી મોટી સંખ્યામાં લોકોએ સેવા સેતુ કાર્યક્રમની રાહ જોવાની ફરજ પડી હતી!",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1410, 2715, 1510,
    lines=[
        "૯૬૦૦ અરજી માત્ર હેલ્થ વેલનેસ કાર્ડની! કાર્યક્રમને",
        "ધરાર સફળ બતાવવા રોજિંદી અરજીઓ અટકાવી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1516, 2382, 2132,
    text="લોકોને સરકારી સેવાઓનો ઝડપી લાભ મળે તેના માટે સરકારે સેવા સેતુ કાર્યક્રમો ચાલુ કર્યા છે. પરંતુ અમદાવાદમાં આ સેવા સેતુ કાર્યક્રમો કથળેલી સરકારી સેવાઓનો ચિતાર આપી રહ્યા છે. બીજી તરફ આવા કાર્યક્રમોને ધરાર સફળ બનાવવા માટે કચેરીઓમાં દરરોજ આવતી અરજીઓને પણ રોકી રાખીને બાદમાં સેવા સેતુ દરમિયાન પ્રક્રીયા કરાઈ રહી છે! જેના કારણે અરજદારોએ ઉલટાની વધારે હેરાનગતિ વેઠવી પડે છે. આમ તો સેવા સેતુમાં ૫૬ પ્રકારની સરકારી, અર્ધ સરકારી સેવાઓ આવરી લેવાઈ હોવાનો દાવો પણ કરાય છે. પરંતુ અમદાવાદના કાર્યક્રમોની કુલ ૨૨ હજાર અરજીઓ પૈકી ૯૬૦૪ તો માત્ર હેલ્થ વેલનેસ કાર્ડની હતી! એટલે કે",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2395, 1518, 2395, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1516, 2715, 1618,
    text="આંકડા મોટા બતાવવા આરોગ્ય કાર્ડની સેવાઓનો ઉપયોગ થઈ રહ્યો છે. હકીકતમાં અધિકારીઓ નિયમિત રીતે",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(2408, 1624, 2715, 2020, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2416, 1630, 2706, 1712,
    lines=["સેવા સેતુના નામે", "અરજીઓના આંકડા"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2416, 1718, 2706, 2012,
    text="પૂર્વનો સંયુક્ત કાર્યક્રમ  ૧૦૨૨૭\nપશ્ચિમ સંયુક્ત કાર્યક્રમ  ૬૧૪૯\nઉત્તર-પશ્ચિમ ઝોન  ૭૨૮\nપૂર્વ ઝોન  ૧૦૯૬\nમધ્ય ઝોન  ૧૨૬૦\nપશ્ચિમ ઝોન  ૧૪૮૫",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2026, 2715, 2132,
    text="યોગ્ય કામ કરે તે ધ્યાન રાખવાની ફરજ લોક પ્રતિનિધિઓએ નિભાવે તો સેવા સેતુના આયોજનની જરૂર જ નથી.",
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
    lines=["માલ પરિવહનની ક્ષમતા વધારવા વધુ એક પગલું"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1412, 1382, 1542,
    lines=[
        "મુંબઈ-અમદાવાદ વચ્ચે ૧.૫ કિમી",
        "લાંબી ડબલ ડેકર માલગાડી દોડી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1548, 1382, 1676,
    text="અમદાવાદ, સોમવાર\nમુંબઈ અને અમદાવાદ ગુજરાતના વેપાર, ઉદ્યોગ અને માલપરિવહન માટે મહત્વના કેન્દ્રો છે. આ બંને શહેરો વચ્ચે માલની હેરફેર ઝડપી અને સરળ બને તે માટે રેલવેએ દોઢ કિલોમીટર લાંબી ડબલ ડેકર કન્ટેનર માલગાડી દોડાવી માલ પરિવહનની ક્ષમતા વધારવા બાબતનું મહત્વનું પગલું ભર્યું છે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1682, 1382, 1782,
    lines=[
        "૩૬૦ કન્ટેનરવાળી માલગાડીમાં ૧૨૦૦૦ અને",
        "વચ્ચે ૯૦૦૦ હોર્સપાવર વાળા બે એન્જિન જોડાયા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1788, 1050, 2175,
    text="પ્રાપ્ત માહિતી મુજબ, તાજેતરમાં રેલવે દ્વારા મુંબઈ-અમદાવાદ માર્ગ પર આશરે ૧.૫ કિલોમીટર લાંબી ડબલ ડેકર કન્ટેનર માલગાડી દોડાવવામાં આવી હતી. જેમાં પહેલી વખત બે સ્તરે કુલ ૩૬૦ કન્ટેનર લઈ જવામાં આવ્યાં હતાં. આ માલગાડીને ખેંચવા માટે આગળ ૧૨,૦૦૦ હોર્સપાવરનું ‘મેક ઈન ઈન્ડિયા’નું એન્જિન અને વચ્ચે ૯,૦૦૦ હોર્સપાવરનું બીજું એન્જિન જોડવામાં આવ્યું હતું. ગુજરાતના ઉદ્યોગો અને",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1064, 1790, 1064, 2175, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 1788, 1382, 2175,
    text="વેપાર માટે મુંબઈ મહત્વનું બજાર અને બંદરો સાથે જોડાણ પૂરું પાડે છે. જ્યારે અમદાવાદ આસપાસના વિસ્તારોમાં ઔદ્યોગિક અને વેપારી પ્રવૃત્તિઓનું મોટું કેન્દ્ર હોવાથી ઈલેક્ટ્રિક એન્જિન સાથેની ડબલ સ્તરની માલગાડીથી બંને શહેરો વચ્ચે માલની હેરફેરમાં સરળતા આવી શકે છે. જોકે, પરિવહનનો ખર્ચ કેટલો ઘટશે અને તેનો લાભ ગુજરાતના વેપારીઓને કેટલો મળશે તે જોવાનું રહેશે.",
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
    lines=["વર્ષ ૨૦૧૯-૨૦ અને તે પછી પ્રવેશ લેનારા"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1412, 1412, 2052, 1542,
    lines=[
        "MBBSના નાપાસ વિદ્યાર્થીઓને",
        "પાસ થવા હવે વધુ એક તક મળશે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1548, 2052, 1676,
    text="અમદાવાદ,સોમવાર\nએમબીબીએસના વિદ્યાર્થીઓને કોવિડ સહિતની પરિસ્થિતિને ધ્યાને રાખીને ફર્સ્ટ પ્રોફેશનલ એમબીબીએસ એક્ઝામ પાસ કરવા માટે હવે વધુ એક તક મળશે. ૨૦૧૯-૨૦માં અને તે પછીના વર્ષોમાં પ્રવેશ મેળવનારા વિદ્યાર્થીઓને કુલ પાંચ તક ફાઈનલ પરીક્ષા પાસ કરવા માટે મળશે.",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1412, 1682, 2052, 1782,
    lines=[
        "અગાઉ કમિશન દ્વારા ફર્સ્ટ એમબીબીએસ ક્લિયર",
        "કરવા માટે ચાર તક અપાતી પરંતુ હવે પાંચ મળશે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1788, 1718, 2302,
    text="નેશનલ મેડિકલ કમિશને કોવિડ ડ્યુટી તેમજ આરોગ્ય સંબંધીત મુશ્કેલીઓને ધ્યાને રાખીને અગાઉ ૨૦૧૯-૨૦ અને ૨૦૨૦-૨૧માં એમબીબીએસમાં પ્રવેશ લેનારા વિદ્યાર્થીઓને ફર્સ્ટ એમબીબીએસ પાસ કરવા માટે વધારાની એક તક આપી હતી. પરંતુ ત્યારબાદ પણ અન્ય વર્ષનો વિદ્યાર્થીઓને લઈને યુનિ.ઓ-કોલેજો તરફથી રજૂઆતો કમિશનને કરવામાં આવી હતી.જેને પગલે નેશનલ મેડિકલ કમિશને ૨૦૧૯-૨૦ અને તે પછીના વર્ષોમાં એમબીબીએસમાં પ્રવેશ મેળવનારા વિદ્યાર્થીઓને ફર્સ્ટ એમબીબીએસ ક્લિયર કરવા માટે પાંચમો એટેમ્પ્ટ આપવામાં આવ્યો છે.\nનિયમ મુજબ વિદ્યાર્થીઓને ચાર તક મળતી હોય છે પરંતુ આ ખાસ પાંચમીવારની",
    target_lines=16,
    first_indent_pt=9.0,
)
draw_line(1731, 1790, 1731, 2302, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 1788, 2052, 2060,
    text="તક કેટલાક નિયમો-શરતોને આધીન જ વિદ્યાર્થીઓને મળશે.જેમાં વિદ્યાર્થીને અગાઉ પાંચમી તક મળેલી ન હોવી જોઈએ કે લીધી ન હોય તો જ આ તક મળશે.ઉપરાંત યુનિ.કે કોલેજે વિદ્યાર્થીનો પ્રવેશ રદ કરેલો ન હોવો જોઈએ તથા ચાર વર્ષ પુરા કરેલા હોવા જોઈએ.આ તક મળ્યા બાદ ઈન્ટર્નશિપ સાથેનો કુલ કોર્સનો કુલ સમયગાળો દસ વર્ષથી વધવો ન જોઈએ.",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_box(1744, 2068, 2052, 2302, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1752, 2076, 2044, 2294,
    text="વાચકોએ નોંધ લેવી કે કોઈપણ જાહેરખબરમાં જણાવેલી માહિતીની સત્યતા બાબતે અમો કોઈ બાંયેધરી આપતા નથી. વાચકોએ પોતાની રીતે પૂરતી ચકાસણી કરીને યોગ્ય નિર્ણય લેવાનો રહેશે.\n- જાહેરખબર મેનેજર",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. PLACE BOTTOM DRAMA ADS, PUBLIC NOTICES & IMPRINT BLOCKS (100% EDITABLE TEXT)
# ==============================================================================
print("Placing Page 4 Drama Ads, Public Notices & Imprint (100% Editable Text)...")
place_png(75, 1210, 726, 3810, "ads_col12_bottom.png")

def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=38, right_lines=40, header_h=54):
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

# Notice 1: Cols 3-4 Bottom (746..1382, 2200..3792)
draw_line(746, 2184, 1382, 2184, swatch="[Black]", weight_pt=0.85)
place_public_notice_2col(
    746, 2200, 1382, 3792,
    left_text=(
        "આથી જાહેર જનતાને જણાવવાનું કે, રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૨ (વાડજ) ના તાલુકા સાબરમતીના ગામ મોજે ચાંદખેડાની સીમનાં રી-સર્વે મુજબના બ્લોક/સર્વે નં. ૪૭૮ (જુના બ્લોક/સર્વે નં. ૨૦૬/૧) ની ૫૦૫૯ ચો.મી. ની જમીન ઉપર આવેલ 'શ્રીનાથ બંગલોઝ' ના નામથી ઓળખાતી સ્કીમમાં આવેલ પ્લોટ નં. ૧૩ ની ૨૨૫ ચો.વાર યાને કે ૧૮૮.૧૨ ચો.મી. ની જમીન તથા તેમાં આવેલ રહેણાંકના બાંધકામ સહીતની મિલ્કત રમેશભાઈ મણીલાલ પટેલ અને શકુંતલાબેન રમેશભાઈ પટેલની સંયુક્ત માલીકી, કબજા, ભોગવટાની તથા તમામ પ્રકારના બોજાઓથી મુક્ત આવેલ હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે અને અમારા અસીલે સદરહુ મિલ્કતના ટાઈટલ ક્લીયર અને માર્કેટેબલ હોવા બદલના પ્રમાણપત્રની અમારી પાસે માંગણી કરેલ છે.\n"
        "સદરહુ મિલ્કત ઉપર કોઈપણ બેંક, નાણાંકીય સંસ્થા, પેઢી કે વ્યક્તિનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિત, હિસ્સો, દાવો, અલાખો, બોજો, લીયન કે બાનાખત હક્ક"
    ),
    right_text=(
        "પોષાતો હોય તો આ નોટિસ પ્રસિદ્ધ થયેથી દિન-૭ (સાત) માં પ્રમાણિત પુરાવા સહીત નીચેના સરનામે રજી.એ.ડી. થી લેખિત જાણ કરવી અને જો તેમ કરવામાં કસૂર કે વિલંબ થશે તો સદરહુ મિલ્કત ઉપર અન્ય કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિત, હિસ્સો કે બોજો નથી અને જો હોય તો તે જતો (વેવ) કરેલ છે તેમ સમજી મુદત વીત્યે સદરહુ મિલ્કતનું ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટ ઈસ્યુ કરવામાં આવશે અને ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં તેની જાહેર જનતાએ નોંધ લેવી.\n"
        "તારીખ : ૨૦/૧૦/૨૦૨૬\n"
        "રાજેશ કે. પટેલ (એડવોકેટ)\n"
        "ઓફિસ : ૩૦૪, ત્રીજો માળ, સત્યમેવ એમીનન્સ, સાયન્સ સીટી રોડ, સોલા, અમદાવાદ-૩૮૦૦૬૦.\n"
        "મો. નં. ૯૮૨૫૦ ૪૫૬૭૮"
    ),
    left_lines=38,
    right_lines=40,
)

# Col 5 Notice (1-col) + Col 6 English Imprint + Cols 5-6 Bottom Gujarati Imprint
draw_box(1412, 2314, 1724, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
draw_box(1412, 2314, 1724, 2368, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1420, 2320, 1716, 2364,
    lines=["જાહેર નોટિસ"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1420, 2374, 1716, 3186,
    text=(
        "ડીસ્ટ્રીકટ ગાંધીનગર સબ-ડીસ્ટ્રીકટ કલોલ તાલુકાના મોજે સઈજ ગામની સીમના બ્લોક/સર્વે નં. ૧૪૨૮ ની બીનખેતીની જમીન ઉપર આવેલ રહેણાંકની યોજનામાં આવેલ પ્લોટ નં. ૨૪ ની ૧૮૦ ચો.વારની મિલ્કત પટેલ કનુભાઈ મગનભાઈની સ્વતંત્ર માલિકી કબજા ભોગવટાની હોવાનું જણાવી અમારી પાસે ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટની માંગણી કરેલ છે. કોઈનો વાંધો કે હક્ક હોય તો દિન-૭ માં નીચેના સરનામે રજી.એ.ડી.થી જાણ કરવી.\n"
        "તા. ૨૦/૧૦/૨૦૨૬\n"
        "અશ્વિન જે. પટેલ (એડવોકેટ)\n"
        "નવરંગપુરા, અમદાવાદ."
    ),
    target_lines=24,
    first_indent_pt=0.0,
    hi_pt=10.2,
    lo_pt=6.8,
)

# Col 6 English Imprint Box (1738..2052, 2314..3194)
draw_box(1738, 2314, 2052, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1748, 2324, 2042, 3184,
    text=(
        "THE GUJARAT SAMACHAR\n"
        "Printed and Published by Shreyans S. Shah on behalf of Lok Prakashan Ltd. and Printed at Lok Prakashan Ltd., Gujarat Samachar Bhavan, Khanpur, Ahmedabad and Published from Gujarat Samachar Bhavan, Khanpur, Ahmedabad.\n"
        "Editor : Shreyans S. Shah\n"
        "(Responsible for selection of news under the PRB Act).\n"
        "RNI No. 1609/57.\n"
        "Phone : (079) 25504010"
    ),
    target_lines=22,
    font_style="Bold",
    align="left",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)

# Cols 5-6 Bottom Gujarati Imprint Box (1412..2052, 3206..3792)
draw_box(1412, 3206, 2052, 3792, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1422, 3216, 1724, 3782,
    text=(
        "લોક પ્રકાશન લિમિટેડ વતી મુદ્રક અને પ્રકાશક : શ્રેયાંસ શાંતિલાલ શાહ\n"
        "લોક પ્રકાશન લિમિટેડના ગુજરાત સમાચાર ભવન, ખાનપુર, અમદાવાદ-૩૮૦૦૦૧ ખાતે છાપ્યું અને ત્યાંથી જ પ્રસિદ્ધ કર્યું.\n"
        "તંત્રી : શ્રેયાંસ શાંતિલાલ શાહ"
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
        "(પી.આર.બી. એક્ટ હેઠળ સમાચારોની પસંદગી માટે જવાબદાર)\n"
        "હેડ ઓફિસ : ગુજરાત સમાચાર ભવન, ખાનપુર, અમદાવાદ-૩૮૦૦૦૧.\n"
        "ફોન : (૦૭૯) ૨૫૫૦૪૦૧૦ (૧૦ લાઈન)\n"
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
        "મોજે - ગોતા\n"
        "ડીસ્ટ્રીકટ અમદાવાદ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૮ (સોલા) તાલુકા ઘાટલોડીયાના ગામ મોજે ગોતાની સીમના બ્લોક/સર્વે નં. ૨૧૫, ટી.પી. સ્કીમ નં. ૩૨ ના ફા.પ્લોટ નં. ૫૪ ની બિનખેતીની જમીન ઉપર આવેલ સ્કીમમાં ફ્લેટ નં. એ/૪૦૨ ની મિલ્કત પટેલ દિનેશભાઈ રમણલાલની સ્વતંત્ર માલિકી કબજા ભોગવટાની તથા બોજા રહિત હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરેલ છે અને ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટની માંગણી કરેલ છે."
    ),
    right_text=(
        "સદરહુ મિલ્કત ઉપર કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિત, હિસ્સો, દાવો કે બોજો હોય તો આ નોટિસ પ્રસિદ્ધ થયેથી દિન-૭ માં લેખિત પુરાવા સહીત રજી.એ.ડી.થી નીચેના સરનામે જાણ કરવી. જો તેમ કરવામાં નહીં આવે તો કોઈનો કોઈપણ પ્રકારનો હક્ક નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટ ઈસ્યુ કરવામાં આવશે.\n"
        "તા. ૨૦/૧૦/૨૦૨૬\n"
        "કેતન એમ. પટેલ (એડવોકેટ)\n"
        "સોલા રોડ, અમદાવાદ."
    ),
    left_lines=22,
    right_lines=24,
)
place_public_notice_2col(
    2076, 2978, 2715, 3792,
    left_text=(
        "મોજે - બોપલ\n"
        "રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૯ (બોપલ) તાલુકા દસ્ક્રોઈના ગામ મોજે બોપલની સીમના બ્લોક નં. ૪૧૨, ટી.પી. સ્કીમ નં. ૩ ના ફા.પ્લોટ નં. ૮૮ ની જમીન ઉપર આવેલ રહેણાંકની યોજનામાં બંગલો નં. ૧૨ ની મિલ્કત શાહ વિનોદચંદ્ર ચીમનલાલની સ્વતંત્ર માલિકી કબજા ભોગવટાની તથા તમામ પ્રકારના બોજાઓથી મુક્ત હોવાનું જણાવી અમારી પાસે ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટની માંગણી કરેલ છે."
    ),
    right_text=(
        "સદરહુ મિલ્કત ઉપર કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિત, હિસ્સો, દાવો કે બોજો હોય તો આ નોટિસ પ્રસિદ્ધ થયેથી દિન-૭ માં લેખિત પુરાવા સહીત રજી.એ.ડી.થી નીચેના સરનામે જાણ કરવી. મુદત વીત્યે કોઈનો વાંધો ચાલશે નહીં અને ટાઈટલ ક્લીયરન્સ સર્ટિફિકેટ ઈસ્યુ કરવામાં આવશે.\n"
        "તા. ૨૦/૧૦/૨૦૨૬\n"
        "નિલેશ આર. શાહ (એડવોકેટ)\n"
        "બોપલ, અમદાવાદ."
    ),
    left_lines=22,
    right_lines=24,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_04_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_04_SameToSame.dns"
    png_path = target_dir / "Page_04_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_04_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_04_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
