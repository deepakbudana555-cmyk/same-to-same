from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 5 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all 4 stories & fee table on Page 5!
- Graphics/Ads (PNG): Top Running Header Bar, Indian Bank Right-Half Ad,
  and Vijay Sales Bottom Half-Page Ad.
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
ASSETS_DIR = DIR_SMAE / "Page_05_Assets"

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
        "title": "Gujarat Samachar — Page 05 (100% Same-to-Same Editable Gopika)"
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
print("Placing Page 5 Running Header...")
build_running_header(5, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: NAVA VADAJ SPORTS CENTER (COLS 1-2 TOP)
# ==============================================================================
print("Building Story 1 (Nava Vadaj Sports Center, Cols 1-2 Top)...")
place_exact_display_lines(
    82, 200, 718, 244,
    lines=["ભાજપના રાજમાં મળતિયાઓ માલામાલ"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 250, 718, 390,
    lines=[
        "નવા વાડજનું સ્પોર્ટ્સ સેન્ટર માત્ર પાંચ",
        "લાખ વાર્ષિક ફીથી ભાડે આપી દેવાશે"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 396, 718, 550,
    text="અમદાવાદ, સોમવાર\nનવા વાડજમાં એસી બેડમિન્ટન કોર્ટ, વોલિબોલ કોર્ટ અને બોક્સ ક્રિકેટ સહિતની સુવિધાઓ સાથે રૂ.૪.૬૭ કરોડના ખર્ચે તૈયાર થયેલું સ્પોર્ટ્સ સેન્ટર માત્ર પાંચ લાખ રૂપિયાની વાર્ષિક ફીથી ભાડે આપી દેવાની તૈયારીઓ શરૂ થઈ છે. રમત-ગમતની અન્ય સુવિધાઓની માફક આ સુવિધા પણ નજીવી ફીમાં ભાડે રાખી મળતિયાઓ માલામાલ બનશે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    82, 556, 718, 650,
    lines=[
        "૪.૬૭ કરોડના ખર્ચે તૈયાર થયેલા સ્પોર્ટ્સ સેન્ટરમાં",
        "બેડમિન્ટન, વોલિબોલ અને બોક્સ ક્રિકેટની સુવિધા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 656, 224, 945,
    text="અમદાવાદ મ્યુનિ. દ્વારા કોમનવેલ્થ ગેમ્સના નામે રમત-ગમત માટે આડેધડ ખર્ચ શરૂ થયો છે. તેનાથી સામાન્ય નાગરિકોને કોઈ ફાયદો થાય કે નહીં, પરંતુ",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_box(232, 656, 718, 945, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    240, 662, 710, 704,
    lines=["સ્પોર્ટ્સ સંકુલ માટે નિયત કરાયેલી ફી"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
)
place_exact_body_column(
    240, 708, 710, 938,
    text="બેડમિન્ટન કોર્ટ(એસી)  રૂ.૫૦૦થી ૪૦૦૦\nવોલિબોલ કોર્ટ  રૂ.૨૦૦થી ૩૦૦૦\nયોગ-મેડિટેશન(એસી)  રૂ.૨૦૦થી ૨૦૦૦\nચેસ  રૂ.૧૫૦થી રૂ.૨૦૦૦\nકેરમ  રૂ.૧૦૦\nલાઈબ્રેરી(એસી)  રૂ.૩૦૦\nબોક્સ ક્રિકેટ  રૂ.૭૦૦થી ૧૨૦૦",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    82, 952, 392, 1188,
    text="સત્તાધીશોના મળતિયાઓ જરૂર પૈસાદાર બની જશે. કારણ કે શહેરમાં કરોડો રૂપિયાના ખર્ચે ઉભી કરાયેલી રમત-ગમતની સુવિધાઓ નજીવા દરથી સંચાલન માટે ભાડે અપાઈ રહી છે.\nવળી પ્રજાના પૈસે તૈયાર થયેલી આ સુવિધાઓનો ઉપયોગ કરવા માટેના દર કમર્શિયલ એકમો જેટલા જ રાખવામાં આવે છે! જેમાં હવે નવા વાડજ સ્પોર્ટ્સ",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(400, 954, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 952, 718, 1188,
    text="સેન્ટરનો ઉમેરો થવા જઈ રહ્યો છે. આ સ્પોર્ટ્સ સેન્ટર બાળકો અને યુવાનોને રમત-ગમતનો લાભ મળે તેવો છે. પરંતુ તેની ફીના દર એટલા તોતિંગ નક્કી કરાયા છે કે, મધ્યમ અને ગરીબ વર્ગને પોષાય તેમ નથી. આટલી ઉંચી ફીના દર છતાં આખુ સેન્ટરનું વાર્ષિક ભાડું માત્ર પાંચ લાખ રૂપિયા જ નક્કી કરાયું છે!",
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
    lines=["પરસેવાની કમાણી વિના તહેવારો કોરા ગયાં"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 1250, 718, 1390,
    lines=[
        "મનરેગા મજૂરો -સુપરવાઈઝરોને",
        "હજુ રૂ.૩.૪૩ કરોડ ચૂકવાયાં નથી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1396, 392, 1988,
    text="અમદાવાદ,સોમવાર\nગુજરાતમાં કાળી મજૂરી કરીને પેટનો ખાડો પૂરતા ગરીબ શ્રમિકોને તેમના હકના નાણાં માટે વલખાં મારવા પડી રહ્યા છે. ગરીબ શ્રમિકોને રોજગાર આપતી યોજના મનરેગામાં કામ કરતા શ્રમિકોને ૨૦ જૂન ૨૦૨૬થી આજ દિન સુધી વેતન ચૂકવવામાં આવ્યું નથી. કાયદા મુજબ કામ પૂરું થયાના ૧૫ દિવસમાં નાણાં સીધા ખાતામાં જમા થવા જોઈએ, પરંતુ વહીવટી તંત્રની બેદરકારીને કારણે નવરાત્રી અને દશેરા જેવા તહેવારો પણ આ ગરીબ પરિવારો માટે કોરા રહ્યાં છે.\nમાત્ર ભાવનગર જિલ્લામાં જ શ્રમિકોનું ૨.૬૯ કરોડ રૂપિયા બાકી છે. આ ઉપરાંત, યોજનાનું સંચાલન કરતા મનરેગા સુપરવાઈઝરોને પણ ૧.૪૪ કરોડ રૂપિયા ચૂકવાયા નથી. આમ, કુલ મળીને કરોડો રૂપિયા વહીવટી તંત્રની ફાઈલોમાં",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(400, 1398, 400, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 1396, 718, 1988,
    text="અટવાઈ પડ્યા છે. ધોમધખતા તડકામાં અને કાળી મજૂરી કરીને લોહીનું પાણી કરનારા શ્રમિકોના ઘરમાં અત્યારે ચૂલો સળગાવવો પણ મુશ્કેલ બન્યો છે. ગુજરાતમાં કુલ મળીને મનરેગાના મજૂરોને હજુ ૪૩ કરોડ ચૂકવાયા નથી.\nયુપીએ સરકાર દ્વારા ગ્રામીણ વિસ્તારના ગરીબોને રોજગારીની ગેરંટી આપવા માટે મનરેગા કાયદો લાવવામાં આવ્યો હતો. આ કાયદા અંતર્ગત સ્પષ્ટ જોગવાઈ છે કે શ્રમિકે કરેલા કામનું મહેનતાણું ૧૫ જ દિવસમાં ચૂકવી દેવું પડે. જો આ સમયગાળામાં ચૂકવણું ન થાય, તો શ્રમિકો વળતર મેળવવા હકદાર બને છે. પરંતુ ભાજપ સરકારના રાજમાં નિયમો માત્ર કાગળ પર જ રહી ગયા હોય તેવું સ્પષ્ટ દેખાઈ રહ્યું છે. સરકારની ગરીબ શ્રમિકોને મહેનતાણું ચૂકવવામાં પણ અનદેખી કરી રહી છે.",
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
    lines=["આજે ‘ઓસ્ટિયોપોરોસિસ દિવસ’ છે ત્યારે"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 250, 1382, 390,
    lines=[
        "દર ૩માંથી એક વયસ્ક મહિલાને",
        "હાડકા નબળા પડવાની સમસ્યા"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 396, 1382, 550,
    text="અમદાવાદ,સોમવાર\nઓસ્ટિયોપોરોસિસ એવો રોગ છે જેમાં હાડકાં અંદરથી પોલાં અને નબળા પડી જાય છે. સાયલન્ટ કિલર ગણાતી એવી ઓસ્ટિયોપોરોસિસમાં પ્રારંભે કોઈ લક્ષણ જોવા મળતા નથી. ૫૦ વર્ષથી વધુ વયની દર ૩માંથી ૧ મહિલા અને દર પાંચમાંથી ૧ પુરુષને ઓસ્ટિયોપોરોસિસની સમસ્યા છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 556, 1382, 650,
    lines=[
        "ઘરમાં રહેવાની આદતને કારણે શહેરી વિસ્તારમાં",
        "૭૦ ટકાથી વધુ લોકોમાં વિટામિન ડીની ઉણપ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 656, 1056, 1125,
    text="દર વર્ષે ૨૦ ઓક્ટોબરની ઉજવણી ‘ઓસ્ટિયોપોરોસિસ ડે’ તરીકે કરવામાં આવે છે. તબીબોના મતે શહેરી વિસ્તારમાં બદલાતી જીવનશૈલી અને ઘરમાં રહેવાની આદતને કારણે ૭૦થી ૮૦ ટકા લોકોમાં વિટામિન ડીની ઉણપ જોવા મળે છે. હાડકાના સ્વાસ્થ્ય પર ધ્યાન આપવા ફ્રેક્ચર થાય ત્યાં સુધી રાહ જોવી જોઈએ નહીં. હાડકા સંબંધિત સમસ્યાને વૃદ્ધાવસ્થાનો સામાન્ય ભાગ માનીને નજરઅંદાજ કરવી ભૂલભરેલું છે. ઘણા લોકો માને છે કે ઓસ્ટિયોપોરોસિસ અને નબળા હાડકાની સમસ્યા માત્ર વૃદ્ધાવસ્થામાં જ થાય છે. પરંતુ જીવનભરની આપણી આદતો",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(1064, 658, 1064, 1125, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 656, 1382, 1125,
    text="હાડકાના સ્વાસ્થ્યને અસર કરે છે. એક સર્વેક્ષણ પ્રમાણે ગુજરાતમાં ૪૦થી ૮૦ની વયજૂથમાં ૨૨ ટકા હિપ ફ્રેક્ચર, ૨૪ ટકાને મેજર ઓસ્ટિયોપોરોસિસ ફ્રેક્ચરના સારવાર-જોખમની શ્રેણીમાં હતા. પૂરતા પ્રમાણમાં કેલ્શિયમ ધરાવતો સંતુલિત આહાર લેવો જોઈએ તેમ જણાવતા ડૉ. જતિન વખારિયાએ ઉમેર્યું કે વિટામિન ડીનું યોગ્ય સ્તર, નિયમિત કસરત હાડકાને મજબૂતી જાળવવામાં મદદ કરે છે. મેનોપોઝ પછી મહિલાઓ, વૃદ્ધો અને અગાઉ ફ્રેક્ચર થયું તેવા જોખમી પરિબળ ધરાવતા લોકોએ હાડકાના સ્વાસ્થ્યની તપાસ અંગે તબીબી માર્ગદર્શન લેવું જોઈએ.’",
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
    lines=["બાપુનગરમાં સોનારિયા બ્લોક પાસેથી"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1190, 1382, 1330,
    lines=[
        "૨૪ લાખના હેરોઈન સાથે બે",
        "ઝડપાયા: રસ્તા ઉપર વેચાણ!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1336, 1382, 1465,
    text="અમદાવાદ, સોમવાર\nઅમદાવાદમાં હવે જાહેરમાં રસ્તા ઉપર બેરોકટોક હેરોઈનનું વેચાણ થઈ રહ્યું હોવાનો ઘટસ્ફોટ બાપુનગર પોલીસે બે શખ્સોને ૨૪ લાખના હેરોઈન સાથે ઝડપી લેતાં થયો છે. રાજસ્થાનથી હેરોઈન લાવીને ગુજરાતમાં વેચાણ કરતી મહિલા સહિત પાંચ સામે ગુનો નોંધાયો છે.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1472, 1382, 1568,
    lines=[
        "રાજસ્થાનમાં વોટ્સ-એપથી સંપર્ક કરી હેરોઈન",
        "આપનાર ઉપરાંત મહિલા સહિત પાંચ આરોપી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1574, 1056, 1988,
    text="બાપુનગર પોલીસની ટીમે બાતમીના આધારે બાપુનગરમાં સોનારિયા બ્લોક પાસે રસ્તા ઉપર બર્ગમેન ટુ વ્હીલર ઉપર બેસીને હેરોઈનનું વેચાણ કરતાં બે શખ્સોને ઝડપી પાડ્યા હતા. સોનારિયા બ્લોકમાં જ રહેતા રોહિત ભેરોસિંગ રાજપુત પાસેથી ૧૦.૭૭ લાખની કિંમતનું ૫૩.૮૯૦ ગ્રામ તેમજ આનંદ સોમાભાઈ પ્રજાપતિ પાસેથી ૧૪ લાખની કિંમતનું ૭૦.૨૨ ગ્રામ હેરોઈન કબજે કરવામાં આવ્યું હતું. બન્ને આરોપીઓએ કેફીયત આપી હતી કે, સોનારિયા બ્લોકમાં જ રહેતા નાનુ ઉર્ફે ભાવેશ નટવરભાઈ પટણી અને ટીનાબહેન પપ્પુભાઈ પટણીના કહેવાથી",
    target_lines=14,
    first_indent_pt=9.0,
)
draw_line(1064, 1576, 1064, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 1574, 1382, 1988,
    text="રાજસ્થાનના સાંચોર ખાતે જઈ એક વોટ્સ-એપ નંબર ઉપર સંપર્ક કરીને હેરોઈન લાવ્યા હતા. અગાઉ છથી સાત વખત હેરોઈન લાવીને વેચાણ કરી ચૂકેલા બન્ને આરોપીઓને રાજસ્થાન જઈને હેરોઈન લાવવા માટે રૂા. ૧૦,૦૦૦ આપવામાં આવતા હતા. જ્યારે, છૂટક વેચાણ કરે તેના ઉપર પણ પૈસા આપવામાં આવતા હતા. બાપુનગર પોલીસે કુલ ૨૪.૮૨ લાખના ૧૨૪.૧૧૧ ગ્રામ હેરોઈન સાથે બે આરોપીને ઝડપી હેરોઈન વેચાણનું કામ સોંપનાર મહિલા ટીનાબહેન, નાનુ પટણી ઉપરાંત રાજસ્થાનમાં હેરોઈન આપનાર અજાણ્યા શખ્સને ઝડપી લેવા કાર્યવાહી હાથ ધરી છે.",
    target_lines=14,
    first_indent_pt=0.0,
)
draw_line(82, 1996, 1382, 1996, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 6. PLACE INDIAN BANK AD & VIJAY SALES AD (PNG)
# ==============================================================================
print("Placing Indian Bank & Vijay Sales Advertisements...")
place_png(1400, 188, 2725, 2010, "ad_indian_bank_right.png")
place_png(0, 2010, 2800, 3974, "ad_vijay_sales_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_05_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_05_SameToSame.dns"
    png_path = target_dir / "Page_05_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_05_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_05_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
