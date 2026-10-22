from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 6 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  for Gauchar Land Encroachment PIL & Gujarat Power Crisis Continuation!
- Graphics/Notices (PNG): Top Running Header Bar, Col 1 Obituaries/Notices,
  Cols 7-8 Public Notices, Cols 2-6 Bottom Public Notices, and Bottom CMYK Bar.
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
        "title": "Gujarat Samachar — Page 06 (100% Same-to-Same Editable Gopika)"
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
print("Placing Page 6 Running Header...")
build_running_header(6, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: GAUCHAR LAND ENCROACHMENT PIL (COLS 2-4 TOP)
# ==============================================================================
print("Building Story 1 (Gauchar Land Encroachment PIL, Cols 2-4 Top)...")
place_exact_display_lines(
    414, 200, 1382, 245,
    lines=["વાવના આંત્રોલ ગામે ગૌચરની જમીનમાં દબાણો મુદ્દે PIL"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    414, 250, 1382, 412,
    lines=[
        "ગૌચરની જમીન પરથી દબાણો દૂર",
        "કરવા મુદ્દે હાઈકોર્ટે રિપોર્ટ માંગ્યો"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    414, 418, 718, 902,
    text="અમદાવાદ, સોમવાર\nબનાસકાંઠા જિલ્લાના વાવ-થરાદના આંત્રોલ ગામે ગામતળ અને ગૌચરની જમીનમાં કથિત ગેરકાયદે દબાણો અને સ્થાનિક સ્કૂલના કેમ્પસમાં કોમર્શીયલ દુકાનો બનાવી ભાડે આપવા દેવાના પ્રકરણમાં ગુજરાત હાઈકોર્ટ સમક્ષ જાહેરહિતની રિટ અરજી દાખલ થઈ છે. જેની સુનાવણીમાં એક્ટીંગ ચીફ જસ્ટિસ માનસ રંજન પાઠક અને જસ્ટિસ નિખિલ એસ.કેરીયલની ખંડપીઠે જિલ્લા વિકાસ અધિકારી(ડીડીઓ) પાસેથી ગૌચરની જમીન પરથી દબાણો દૂર કરવા અંગે સત્તાવાળાઓ દ્વારા શું પગલાં લેવાયા તેનો રિપોર્ટ માંગ્યો છે.",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(732, 420, 732, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 418, 1050, 1094,
    text="વાવ-થરાદના આંત્રોલ ગામે ગૌચરની અને ગામતળની જમીન પર ગેરકાયદે દબાણો મામલે હાઈકોર્ટમાં થયેલી જાહેરહિતની રિટ અરજીમાં એ મતલબની રજૂઆત કરવામાં આવી હતી કે, ગામની ગામતળની અને ગૌચરની જમીનો પર ગેરકાયદેસર રીતે કાચા-પાકા મકાનો બાંધી ગેરકાયદે દબાણો કરી દેવાયા છે. એટલું જ નહી, ગામની જ સ્થાનિક સ્કૂલના કેમ્પસની જગ્યામાં કોમર્શીયલ બાંધકામો કરી તેમાં દુકાનો બારોબાર ભાડે આપી દેવાઈ છે. આમ, ગામની ગૌચરની અને ગામતળની જમીન ઉપરાંત સ્કૂલના પ્રાંગણમાં નિયમો અને કાયદાકીય જોગવાઈઓનો ભંગ કરી વાણિજિયિક વપરાશના ઓઠા હેઠળ આર્થિક લાભ મેળવવામાં આવ્યો છે.\nઆ સમગ્ર મામલે અરજદારપક્ષ દ્વારા સ્થાનિક સરપંચથી લઈ તલાટી, તાલુકા વિકાસ અધિકારી, જિલ્લા વિકાસ અધિકારી અને બનાસકાંઠા જિલ્લા કલેક્ટર સુધી",
    target_lines=21,
    first_indent_pt=9.0,
)
draw_line(1064, 420, 1064, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 418, 1382, 1094,
    text="વારંવાર રજૂઆત કરી યોગ્ય પગલાં લેવા માંગણી કરાઈ હતી પરંતુ હજુ સુધી કોઈ જ કાર્યવાહી નહી થતાં છેવટે અરજદારને હાઈકોર્ટના દ્વાર ખખડાવવાની ફરજ પડી છે. અરજદારપક્ષ તરફથી સરકારના સત્તાવાળાઓને તાત્કાલિક ધોરણે આંત્રોલ ગામની ગામતળની અને ગૌચરની જમીનમાંથી ગેરકાયદે દબાણો અને બાંધકામો દૂર કરી ગૌચરની જમીન ખુલ્લી કરવા સહિતની દાદ માંગવામાં આવી હતી. જેને પગલે હાઈકોર્ટે સ્થાનિક જિલ્લા વિકાસ અધિકારીને હુકમ કર્યો હતો કે, અરજદારોના આક્ષેપ મુજબ, શું આંત્રોલ ગામની ગૌચરની જમીન પર ગેરકાયદે દબાણો છે...? અને જો હોય તો તેને દૂર કરવા બાબતે સ્થાનિક સત્તાવાળાઓ દ્વારા શું પગલાં લેવાયા તે અંગે જિલ્લા વિકાસ અધિકારીએ આગામી મુદત સુધીમાં રિપોર્ટ રજૂ કરવાનો રહેશે. હાઈકોર્ટે કેસની વધુ સુનાવણી તા.૩૦મી ઓક્ટોબરના રોજ મુકરર કરી છે.",
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
    lines=["ગુજરાતમાં વીજસંકટ", "(છેલ્લા પાનાનું ચાલુ)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1412, 300, 1718, 548,
    text="ભભૂક્યો છે. મહત્વની વાત એછેકે, વીજળીની કટોકટી છુપાવવા માટે સરકાર હવે 'લોડ શેડિંગ' અને 'સ્ટેગરિંગ હોલિડે' જેવા અંગ્રેજી શબ્દોનો આશરો લઈ રહી છે. એવી પણ ચર્ચા છેકે, રાજકોટ, જામનગર, જૂનાગઢ, ભાવનગર અને સુરત સહિત અન્ય શહેરોમાં અઠવાડિયામાં એક વાર ૪ થી ૮ કલાક સુધી ઉદ્યોગો બંધ",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(1731, 200, 1731, 548, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 200, 2052, 548,
    text="રાખવા માટે દબાણ કરવામાં આવી રહ્યું છે. દિવાળી અને બેસતા વર્ષની સીઝન વેપારીઓ માટે આખા વર્ષની કમાણી કરવાની હોય છે. વીજળી વિના પ્રોડક્શન કઈ રીતે કરવું એ સવાલ ઉઠ્યો છે. આવા સમયે જ વીજ કાપને લીધે કરોડો રૂપિયાના ઓર્ડર્સ કેન્સલ થવાની શક્યતા છે જેના કારણે નાના ઉદ્યોગકારોની મુશ્કેલી વધી છે. જો આ સ્થિતી રહી તો, દિવાળીના સમયે લાખો શ્રમિકોની રોજીરોટી છીનવાઈ જાય તેવી પણ ભીતિ સેવાઈ રહી છે.",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_box(1412, 556, 2052, 602, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 560, 2046, 598,
    lines=["ગામડાઓમાં વીજકાપ, કેવડિયા કોલોનીમાં રોશનીનો ઝળહળાટ થશે"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 608, 2052, 822,
    text="ગુજરાતના માથે વીજસંકટ આવી ને ઉભુ રહ્યુ છે. વીજળીની માંગ વધતાં રાજ્ય સરકારે કેન્દ્ર સરકાર સામે હાથ લંબાવવો પડ્યો છે. વધારાની વીજળી માંગ કરવી પડી છે. રાજ્ય સરકારે ગુજરાતની જનતાને વીજળીનો કરકસર રીતે વપરાશ કરવા અપીલ છે પણ બીજી તરફ, ખુદ સરકાર જ સરકારી તાયફા કરીને વીજળીનો ધૂમ વપરાશ કરી રહી છે. દર વર્ષની જેમ આ વર્ષે પણ કેવડિયા કોલોનીમાં એકતા પરેડની ઉજવણીની તૈયારીઓ થઈ રહી છે ત્યારે ખેડૂત આગેવાનોનો આક્ષેપ છેકે, પ્રજાને સલાહ આપતી સરકાર જ સરકારી કાર્યક્રમોમાં વીજળીનો ઓછો વપરાશ કેમ કરતી નથી.",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_box(1412, 828, 2052, 874, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 832, 2046, 870,
    lines=["વીજ સંકટ બાદ હવે સૌરાષ્ટ્ર પર પાણીનું સંકટ સર્જાશે"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 880, 2052, 1096,
    text="વીજળીના ધાંધિયા બાદ હવે રાજકોટ સહિત સમગ્ર સૌરાષ્ટ્ર પર પીવાના પાણીનું ગંભીર સંકટ તોળાઈ રહ્યું છે. નબળા ચોમાસાના કારણે જળાશયો અને કેનાલો ખાલીખમ પડ્યાં છે. સરકારની બહુ ગાજેલી 'સૌની યોજના'ની પાઈપલાઈનોમાં પણ પાણી સુકાઈ રહ્યું છે. જો શિયાળાની શરૂઆતમાં જ આ સ્થિતિ હોય, તો આગામી ઉનાળામાં પીવાના પાણી માટે બૂમરાણ મચે તેવી શક્યતા જોવાઈ રહી છે. એક બાજુ, તહેવારોના માહોલ છે, શિયાળુ વાવણીની સિઝન છે અને દિવાળીના તહેવારોને આડે હવે થોડાક દિવસો જ બાકી રહયા છે ત્યારે ખેડૂતોની ચિંતા વધી છે કેમકે, વીજ સંકટ બાદ હવે પાણીનું સંકટ પણ સર્જાશે.",
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(746, 1100, 2052, 1100, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 4. OBITUARIES (અવસાન નોંધ) & PUBLIC NOTICES (જાહેર નોટિસ) — 100% EDITABLE TEXT
# ==============================================================================
print("Building Page 6 Obituaries & Public Notices (100% Editable Gopika Text)...")

def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=50):
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
    lines=["દિલથી દિલદાર અને ડખાના ડૉક્ટર,", "B.K.", "હંમેશાં અમારી સ્મૃતિઓમાં જીવંત રહેશે."],
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
        "ભણેલા તો ખરા જ, પણ ગણેલા પણ ખરા!\n"
        "સૌને મદદ કરવા સદાય તત્પર એવા\n"
        "તેમના ઉમદા વ્યક્તિત્વને ક્યારેય\n"
        "ભૂલી શકાશે નહીં.\n"
        "“હાસ્યની છોળો ઉછાડનાર અને\n"
        "મિત્રો સાથે રંગત જમાવનાર”\n"
        "B.K.ની સ્મૃતિને કોટિ કોટિ વંદન."
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
        "નૃપેષ શાહ, મયુર શાહ,\n"
        "યોગેશ શાહ, કમલ સતિયા,\n"
        "જિગર શાહ, સૌરભ ઝવેરી,\n"
        "ઉત્પલ શાહ, સ્વ. સૌરીન શેઠ."
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

# --- OBITUARY 2: અનાવિલ અવસાન (Cols 1-2: 82..718, 924..1284) ---
draw_box(82, 924, 718, 1284, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(96, 934, 292, 1136, "obit2_vinodbhai_photo.png")
draw_box(300, 932, 710, 976, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    308, 936, 702, 972,
    lines=["અનાવિલ અવસાન"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    300, 980, 710, 1052,
    text="દિલગીરી સાથે જણાવવાનું કે, અમારા સ્વજન વિનોદભાઈ હરિપ્રસાદ દેસાઈનું તા.૧૮ ઓક્ટોબરને રવિવારના રોજ દુઃખદ અવસાન થયું છે. પ્રભુને ગમ્યું એ ખરું.",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(300, 1056, 710, 1134, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    306, 1060, 704, 1130,
    lines=[
        "સદ્ગતનું બેસણું તા.૨૧ ઓક્ટોબર, ૨૦૨૬ને બુધવારના રોજ",
        "વસંત વાડી, જિરાફ સર્કલ પાસે, બાલવાટિકા પાછળ, મણિનગર",
        "ખાતે સવારે ૯ થી ૧૧ દરમિયાન રાખવામાં આવ્યું છે."
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 1140, 708, 1280,
    text=(
        "લિ. નીતાબેન (નીલાબેન) વિનોદભાઈ દેસાઈ (પત્ની)\n"
        "રાહુલ વિનોદભાઈ દેસાઈ (પુત્ર)    હેમંતભાઈ હરિપ્રસાદ દેસાઈ (ભાઈ)\n"
        "હિરલ રાહુલ દેસાઈ (પુત્રવધુ)    ગિરીશ હરિપ્રસાદ દેસાઈ (ભાઈ)\n"
        "અલય વિનોદભાઈ દેસાઈ (પુત્ર)    સ્વ. મુકેશ હરિપ્રસાદ દેસાઈ (ભાઈ)\n"
        "શ્વેતા અલય દેસાઈ (પુત્રવધુ)    સુજલ (પૌત્ર), પૃથલ (પૌત્રી)\n"
        "હરિપ્રસાદ ગાંડાભાઈ દેસાઈ પરિવાર (ખારા અબ્રામા)"
    ),
    target_lines=6,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 3: કૃણાલ અજીતકુમાર ચોકસી (Cols 1-2: 82..718, 1296..1654) ---
draw_box(82, 1296, 718, 1654, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(86, 1300, 250, 1560, "obit3_krunal_photo.png")
draw_box(254, 1300, 714, 1330, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    260, 1302, 708, 1328,
    lines=["દુઃખદ અવસાન"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    256, 1334, 712, 1444,
    text=(
        "મારા સુપુત્ર કૃણાલ અજીતકુમાર ચોકસી\n"
        "નું તા.૦૭/૧૦/૨૦૨૬ ને બુધવારના રોજ દુઃખદ અવસાન થયેલ છે.\n"
        "સદ્ગતની પ્રાર્થનાસભા તા.૨૦/૧૦/૨૦૨૬ ને મંગળવારના\n"
        "રોજ સવારે ૯.૩૦ થી ૧૧.૩૦ કલાકે નીચેના સ્થળે રાખેલ છે."
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
        "સ્થળઃ ગ્રાઉન્ડ ફ્લોર, ચંદ્રમૌલેશ્વર હોલ,",
        "રંગસાગર રોડ, નારાયણ નગર, પાલડી, અમદાવાદ"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    256, 1508, 712, 1558,
    lines=[
        "અજીતકુમાર નટવરલાલ ચોકસી",
        "વીણાબેન અજીતકુમાર ચોકસી"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    90, 1564, 710, 1648,
    text=(
        "ધારા પલક શાહ | વિયેતા આલાપ શાહ | સ્વીટી કૃણાલ ચોકસી (પત્નિ)\n"
        "પલક નિલેશભાઈ શાહ | આલાપ કિર્તિભાઈ શાહ | સારા કૃણાલ ચોકસી (પુત્રી)\n"
        "(બહેન-બનેવી) | (બહેન-બનેવી) | ક્લારા કૃણાલ ચોકસી (પુત્રી)"
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 4: સ્વ.સીતાબા ગિરધરલાલ પટેલ (Cols 1-2: 82..718, 1666..2236) ---
draw_box(82, 1666, 718, 2236, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(210, 1668, 590, 1712, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    220, 1672, 580, 1708,
    lines=["દુઃખદ અવસાન"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_png(306, 1720, 495, 1952, "obit4_sitaba_photo.png")
place_exact_body_column(
    90, 1958, 710, 2036,
    text=(
        "અમારા માતુશ્રી સ્વ.સીતાબા ગિરધરલાલ પટેલ તા.૧૮-૧૦-૨૦૨૬ રવિવારના રોજ\n"
        "દેવલોક પામ્યા છે. સદ્ગતની ઈચ્છા અનુસાર બેસણું તથા લૌકિકક્રિયા રાખેલ નથી.\n"
        "સદ્ગત માટેના આપના સ્નેહ તથા લાગણીને અમો હૃદયપૂર્વક સ્વીકારીએ છીએ."
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    140, 2040, 660, 2070,
    lines=["લિ. સ્વ.ગિરધરલાલ વિઠ્ઠલદાસ પટેલ"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 2074, 392, 2180,
    text=(
        "મનુભાઈ ગિરધરલાલ પટેલ\n"
        "દિલીપભાઈ ગિરધરલાલ પટેલ\n"
        "જીતેશ મનુભાઈ પટેલ\n"
        "અંકિત મનુભાઈ પટેલ"
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
        "સમીર દિલીપભાઈ પટેલ\n"
        "રોય જીતેશ પટેલ\n"
        "વીણાબેન ચંદુલાલ પટેલ\n"
        "હસુમતીબેન દિનેશકુમાર પટેલ"
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
        "તથા સમસ્ત વિઠ્ઠલદાસ રણછોડદાસ પટેલ પરિવાર",
        "ગુલાબપાર્ક, એસ.ટી.રોડ, સિધ્ધપુર"
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
        "મોજે-જાસપુર\n"
        "ડીસ્ટ્રીકટ ગાંધીનગર રજીસ્ટ્રેશન સબ - ડીસ્ટ્રીકટ કલોલ તાલુકાના મોજે-જાસપુર ગામની સીમના બ્લોક નં.૬૮૩ વિગેરેની બિનખેતીની જમીન ઉપર શીલ્પસ ગ્રીન એગ્રો ઓનર્સ એસોસીએશન (શિલ્પગ્રામ-૧) નામની રહેણાંકીય પ્લોટોની યોજના આવેલ છે. તેમાં સેક્ટર નં. ૧૬ માં આવેલ (એ) ખાનગી સબ-પ્લોટ નં. ૧૬/ જે ની ચો.મી. ૮૯૨(ચો.મી. ૭૩૨ નેટ પ્લોટ એરીયા) તથા (બી) ખાનગી સબ-પ્લોટ નં. ૧૬/ કે ની ચો.મી. ૮૯૨(ચો.મી. ૭૩૨ નેટ પ્લોટ એરીયા) રોડ-રસ્તા તથા કોમનપ્લોટના વગર વહેચાયેલ હક્કસહિતના ખુલ્લા પ્લોટવાળી મીલકત કલ્પન શંકરલાલ શાહની સ્વતંત્ર માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાયની માંગણી કરેલ છે, સદર"
    ),
    right_text=(
        "મીલકતમાં કોઈનો કોઈપણ પ્રકારનો બોજો, ચાર્જ, લીયન, બાના હક્ક, કબજા હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર મીલકતમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર મીલકતનું ટાઈટલ કલીયરન્સ અંગેના અભિપ્રાયનુ સર્ટિફિકેટ ઈસ્યુ કરી દઈશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=22,
    right_lines=24,
)

place_public_notice_2col(
    82, 3014, 718, 3792,
    left_text=(
        "રજીસ્ટ્રેશન ડીસ્ટ્રીકટ અમદાવાદ સબ-ડીસ્ટ્રીકટ અમદાવાદ-૫ (નારોલ)ના તાલુકા મણીનગરના મોજે ગામ ઈસનપુરની સીમનાં સર્વે નં.૪૯૦/૨, ૪૯૧/૨ તથા ૪૯૨/૨, ટી.પી.સ્કીમ નં.૫૫ ના ફા.પ્લોટ નં.૮૩/૫ (જુનો ફા.પ્લોટ નં.૧૫૮) ની સર્વે નંબર મુજબ ૬૩૯.૮૬ ચો.વાર યાને કે ૫૩૫ ચો.મી.ની જમીન પૈકી સર્વે નંબર મુજબ ૩૯૩.૮૬ ચો.વાર યાને કે ૩૨૯.૩૧ ચો.મી.ની જમીન તથા તેમાં આવેલ સેલર, ગ્રાઉન્ડ ફ્લોર તથા ફર્સ્ટ ફ્લોરનું મળી ૩૯૪.૬૦ ચો.મી.નાં બાંધકામવાળી તથા ખુલ્લી જમીન સહીતની મિલ્કત તથા તે અંગે બીજા જે કોઈ આનુષાંગિક હક્કો હોય તે તમામ હક્કો સહીતની આકાશથી તે પાતાળ સુધીની મિલ્કત અમારા અસીલ પરમાર શૈલેશભાઈ રમણીકભાઈ નાઓએ તેઓની સ્વતંત્ર માલીકી, કબજા, ભોગવટાની આવેલ હોવાનું જણાવી અમો એડવોકેટ પાસે સદરહુ મિલ્કતના"
    ),
    right_text=(
        "ટાઈટલ કલીયરન્સ સર્ટીફીકેટની માંગણી કરેલ છે. તેથી સદરહુ મિલ્કતમાં કોઈપણ બેંક, વ્યક્તિ, સંસ્થા, પેઢી, કંપની વિગેરેનો લાગભાગ, હક્ક, હીત, હીસ્સો, દાવો, અલાખો, લિયન કે અન્ય કોઈ ચાર્જ પોષાતો હોય તો દિન-૭(સાત)માં અમો એડવોકેટને નીચે જણાવેલ સરનામે લેખીત પુરાવાઓ સહીત જાણ કરવી. જો આમ કરવામાં નહીં આવે તો મુદ્દત વીતે અમો એડવોકેટ સદર મિલ્કતમાં કોઈપણ વ્યક્તિનો લાગભાગ, હક્ક, હીત, હિસ્સો પોષાતો નથી અથવા પોષાતો હોય તો જતો(વેવ) કરેલ છે, એમ સમજી સદર મિલ્કત અંગેનું ટાઈટલ કલીયરન્સ સર્ટીફીકેટ ઈસ્યુ કરીશું, ત્યારબાદ કોઈની તકરાર ચાલશે નહીં તેની નોંધ લેવી.\n"
        "અમદાવાદ. તા.૧૭/૧૦/૨૦૨૬\n"
        "પરેશ સુરેશભાઈ અઢીયા\n"
        "એડવોકેટ એન્ડ નોટરી\n"
        "૯૦૧, મેપલ ટ્રેડ સેન્ટર, સુરધારા સર્કલ પાસે, સાલ હોસ્પિટલ રોડ, થલતેજ, અમદાવાદ-૩૮૦૦૫૪.\n"
        "(મો.) ૯૮૯૮૪૫૮૨૦૧"
    ),
    left_lines=23,
    right_lines=25,
)

# --- COLS 3-4 PUBLIC NOTICES (4 Notices: y=1082..1684, 1698..2354, 2368..3054, 3076..3792) ---
place_public_notice_2col(
    746, 1082, 1382, 1684,
    left_text=(
        "આથી જાહેર જનતાને જણાવવાનું કે, રજીસ્ટ્રેશન ડિસ્ટ્રીકટ અમદાવાદના સબ-ડિસ્ટ્રીકટ અને તાલુકા બાવળાના ગામ મોજે દુર્ગા ની સીમના નવા સર્વે/બ્લોક નંબર-૨૩૮(જુના સર્વે/બ્લોક નંબર-૯૩)ની કુલ ૪૧૮૯૫ ચોરસમીટર ખેતીની જમીન નટવરભાઈ ઉકાભાઈ તથા ગોવિંદભાઈ ઉકાભાઈ એ તેઓની સંપુર્ણપણે સંયુક્ત, માલિકી, કબજા,ભોગવટાની તમામ બોજા રહીત હોવાનું જણાવી અમારી પાસેથી સદરહુ જમીનના ટાઈટલ્સ કલીયર અને માર્કેટેબલ હોવા બદલના પ્રમાણપત્રની માંગણી કરેલ છે. તો સદરહુ જમીન ઉપર જો કોઈનો કોઈપણ પ્રકારનો લાગ-ભાગ,હક્ક,હીત,હીસ્સો,દાવો કે બોજો હોય તો તેઓએ આ નોટીસ પ્રસિધ્ધ થયેથી દિન-૭(સાત)માં અમોને તે"
    ),
    right_text=(
        "બદલના જરૂરી પુરાવાઓ સહીત લેખિતમાં જાણ નીચેના સરનામે કરવી જો તેમ કરવામાં નહીં આવે તો સદરહુ જમીન ઉપર અન્ય કોઈપણ વ્યક્તિનો કોઈપણ પ્રકારનો લાગ-ભાગ,હક્ક, હીત,હીસ્સો,દાવો કે બોજો નથી અને હોય તો તે જતો કરેલ છે તેમ માનીને અમો સદરહુ જમીનનું ટાઈટલ્સ કલીયરન્સ સર્ટીફીકેટ આપીશું અને ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં.\n"
        "તારીખ-૨૦/૧૦/૨૦૨૬\n"
        "કૌશિક.જી.પટેલ\n"
        "(એડવોકેટ એન્ડ નોટરી)\n"
        "(બી.એસ.સી.,એલ.એલ.બી.)\n"
        "ઓફીસ :-૧૨,બીજો માળ, જે. બી. આર.આર્કેડ,આર.કે.રોયલ હોલની બાજુમાં,સાયન્સ સીટી રોડ, સોલા, અમદાવાદ-૩૮૦૦૬૦.\n"
        "મો.નં.૯૮૨૪૬૭૮૭૬૯"
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    746, 1698, 1382, 2354,
    left_text=(
        "આથી જાહેર જનતાને જણાવવાનું કે, રજીસ્ટ્રેશન ડિસ્ટ્રીકટ અમદાવાદ સબ-ડિસ્ટ્રીકટ અમદાવાદ-૯ (બોપલ) તાલુકા - ઘાટલોડીયા ના મોજે - ઘુમા ગામની સીમના બ્લોક નં. ૭૮૯ ની બિનખેતીની જમીન ઉપર આવેલ આરોહી પ્લોટસ ઓનર્સ એસોસીએશન ના વિભાગ-એ ના સબ પ્લોટ નં. એ/૮૪ ની ૪૦૦ ચોરસવાર યાને કે ૩૩૪.૪૬ ચોરસમીટર રહેણાંક હેતુની બિનખેતીની ખુલ્લી જમીન રમેશભાઈ માધવલાલ પટેલની સ્વતંત્ર માલિકી અને કબજા ભોગવટાની હોવાનુ જણાવી સદર મિલકત પરત્વેનાં ટાઈટલ કલીયર અને માર્કેટેબલ હોવા બદલનાં પ્રમાણપત્રની અમારી પાસે માંગણી કરેલ છે તો સદરહું મિલકત ઉપર જો અન્ય કોઈપણ વ્યક્તિ, બેંક, પેઢી કે સંસ્થા ઈત્યાદીનો કોઈપણ પ્રકારનો લાગ, ભાગ, હક્ક, હિત, હિસ્સો દાવો"
    ),
    right_text=(
        "કે અન્ય કોઈપણ બોજો હોય તો તેઓએ આ જાહેર નોટિસ પ્રસિધ્ધ થયેથી દિન-૭ (સાત) માં અમોને તે બદલનાં પુરાવાની સર્ટીફાઈડ નકલ સહીત લેખિત જાણ નીચેના સરનામે રજીસ્ટર્ડ પોસ્ટ એ.ડી. થી કરવી. (પુરાવા સિવાયનાં વાંધા ધ્યાને લેવામાં આવશે નહી) જો તેમ કરવામાં નહીં આવે તો સદરહું મિલકત ઉપર અન્ય કોઈનો કોઈપણ પ્રકારનો લાગ, ભાગ, હક્ક, હિત, હિસ્સો દાવો કે બોજો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી અમો સદરહું મિલકતનું ટાઈટલ કલીયરન્સ સર્ટીફીકેટ ઈસ્યુ કરી આપીશું. જેની નોંધ લેવી.\n"
        "તા.૧૯/૧૦/૨૦૨૬\n"
        "મનોજ કે. સિંધવ, એડવોકેટ\n"
        "૩૦૧-૩૦૨, ઈલાઈટ, શપથ હેક્સાની સામે, સોલા ઓવર બ્રીજની બાજુમાં, એસ.જી. હાઈવે, સોલા, અમદાવાદ- ૩૮૦૦૬૦.\n"
        "ઓફિસ ફોન નં.૦૭૯-૩૫૮૫૬૩૧૪"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 2368, 1382, 3054,
    left_text=(
        "મોજે-જાસપુર\n"
        "ડીસ્ટ્રીકટ ગાંધીનગર રજીસ્ટ્રેશન સબ - ડીસ્ટ્રીકટ કલોલ તાલુકાના મોજે-જાસપુર ગામની સીમના બ્લોક નં.૬૦૬/૩ વિગેરેની બિનખેતીની જમીન ઉપર શીલ્પસ ગ્રીન એગ્રો ઓનર્સ એસોસીએશન (શિલ્પગ્રામ-૧) નામની રહેણાંકીય પ્લોટોની યોજના આવેલ છે. તેમાં આવેલ ખાનગી સબ-પ્લોટ નં. ૧/જે ની ચો.મી. ૨૫૮૯ રોડ-રસ્તા તથા કોમનપ્લોટના વગર વહેચાયેલ હક્કસહિતના ખુલ્લા પ્લોટવાળી મીલકત વત્સલ સુર્યકાન્ત પટેલની સ્વતંત્ર માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાયની માંગણી કરેલ છે, સદર મીલકતમાં કોઈનો કોઈપણ પ્રકારનો બોજો, ચાર્જ, લીયન, બાના હક્ક,"
    ),
    right_text=(
        "કબજા હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર મીલકતમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર મીલકતનું ટાઈટલ કલીયરન્સ અંગેના અભિપ્રાયનુ સર્ટિફિકેટ ઈસ્યુ કરી દઈશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 3076, 1382, 3792,
    left_text=(
        "મોજે-વાંસજડા (ઢે.)\n"
        "ડીસ્ટ્રીકટ ગાંધીનગર રજીસ્ટ્રેશન સબ - ડીસ્ટ્રીકટ કલોલ તાલુકાના મોજે-વાંસજડા (ઢે.) ગામની સીમના રી-સર્વે મુજબના બ્લોક નં. ૧૭૮ તથા ૧૭૯ (જુના બ્લોક નં. ૭૦ તથા ૭૧) વિગેરેની બિનખેતીની જમીન ઉપર રોડ રસ્તા, કોમન પ્લોટ તથા કલબ હાઉસ જેવી સુવિધાઓ મુકીને ‘ધ અઘર સાઈડ’ના નામથી યોજના રજુ કરવામાં આવેલ છે. તેમાં આવેલ પ્લોટ/વીલા નં. સી/૨૯૬ ની ચો.મી. ૩૫૪ ના પ્લોટ એરીયા તથા તેમાં આવેલ ચો.મી. ૧૩૨ ના કાર્પેટ એરીયાના બાંધકામવાળી મિલકત શૈલેષ રમણીકલાલ મહેતાની સ્વતંત્ર માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાયની માંગણી કરેલ છે, સદર મીલકતમાં કોઈનો કોઈપણ પ્રકારનો બોજો, ચાર્જ,"
    ),
    right_text=(
        "લીયન, બાના હક્ક, કબજા હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર મીલકતમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર મીલકતનું ટાઈટલ કલીયરન્સ અંગેના અભિપ્રાયનુ સર્ટિફિકેટ ઈસ્યુ કરી દઈશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=21,
    right_lines=23,
)

# --- COLS 5-6 PUBLIC NOTICES (4 Notices: y=1162..1794, 1810..2414, 2434..3090, 3104..3792) ---
place_public_notice_2col(
    1412, 1162, 2052, 1794,
    left_text=(
        "જી-અમદાવાદ તા-ઘાટલોડીયા મોજે-ઘુમાની સીમના બ્લોક નં.૬૫૮ (જુના સર્વે નં. ૫૨૨/૪) - ડ્રાફ્ટ ટી.પી. સ્કીમ નં. ૩ (ઘુમા),ફાઈનલ પ્લોટ નં. ૧૧૯ ની બીનખેતીની જમીનમાં આવેલ \"SPARSH\" ના બ્લોક ‘એ’ ના થર્ડ ફ્લોર, ફ્લેટ નં.૩૦૪ ની આશરે ૮૦.૦૩ચો.મી.(કાર્પેટ એરીયા) તથા સદરહુ સ્કીમની કુલ જમીન પૈકી વ.વ. આશરે ૩૩.૩૭ ચો.મી. વાળી મિલકતના માલિકો બ્રિજપાલસિંહ ભુપતસિંહ વાઘરોલા, દત્તાકુંવરબા બ્રિજપાલસિંહ વાઘરોલા, ભુપતસિંહ વાઘરોલા, કંચનબેન ભુપતસિંહ વાઘરોલાએ સદર મિલકતના ટાઈટલ કલીયર,માર્કેટેબલ તથા તમામ પ્રકારના બોજા મુક્ત હોવાનું જણાવી અમારી પાસે ટાઈટલ કલીયરન્સ સર્ટીફીકેટની માંગણી કરેલ છે. સદરહુ મિલકત ઉપર"
    ),
    right_text=(
        "કોઈપણ બેંક, સંસ્થા કે વ્યકિતનો કોઈપણ પ્રકારનો હક્ક, દાવો, હિસ્સો, ગીરો, બોજો, લાગભાગ હોય તો આ જાહેર નોટીસ પ્રસિધ્ધ થયેથી દિન-૭ (સાત) માં અમોને લેખીત પુરાવાઓ સાથે નીચેના સરનામે જાણ કરવી. જો તેમ કરવામાં કસૂર થશે તો મુદત વિત્યે સદરહુ મિલકત ઉપર કોઈનો કોઈપણ પ્રકારનો બોજો હક્ક દાવો કે અધિકાર નથી અને જો હોય તો તે જતો કરેલ છે તેવું સમજી સદરહુ મિલકત અંગે ટાઈટલ કલીયરન્સ સર્ટીફીકેટ અમો આપીશું અને ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં જેની નોંધ લેવી. અમદાવાદ.\n"
        "તા- ૧૯/૧૦/૨૦૨૬\n"
        "સતીષ એચ.પુજારા\n"
        "(એડવોકેટ & નોટરી)\n"
        "એફ.એફ/૫, હરે-કિષ્ના કોમ્પલેક્ષ, SBI બેંક ની સામે, બોપલ, અમદાવાદ.\n"
        "મો.નં. ૯૦૩૩૦૩૩૮૯૦"
    ),
    left_lines=19,
    right_lines=21,
)

place_public_notice_2col(
    1412, 1810, 2052, 2414,
    left_text=(
        "જત રજીસ્ટ્રેશન ડિસ્ટ્રીકટ ગાંધીનગર સબ-ડિસ્ટ્રીકટ દહેગામ ના તાલુકા દહેગામ ના મોજે હરસોલીની સીમના ખાતા નં.૧૫૧૫ માં ચાલતા રિ-સર્વે/બ્લોક નં.૮૭૬ (જુના સર્વે નં. ૪૯૮) ની ૦-૮૫-૬૪ હે.આરે.ચો.મી., આકાર રૂા.૪.૫૦ પૈસાના ક્ષેત્રફળવાળી જુની શરતની ખેતીની જમીન રમેશભાઈ રવજીભાઈ ડોબરીયાની સ્વતંત્ર માલિકી, કબજા-ભોગવટાની બોજાઓથી મુક્ત ટાઈટલ કલીયર અને માર્કેટેબલ આવેલી છે તેમ જણાવી તેઓએ અમારા અસીલને વેચાણ આપવાનું નક્કી કરીને અમારી પાસે સદરહુ જમીનના ટાઈટલ કલીયર અને માર્કેટેબલ હોવાના અભિપ્રાય અંગેના સર્ટીફીકેટ ની માંગણી કરેલ છે તો સદરહુ જમીનમાં કોઈ વ્યક્તિ કે સંસ્થાનો"
    ),
    right_text=(
        "કોઈપણ પ્રકારનો હક્ક, હિત, હિસ્સો, દાવો, બોજો, વાંધો હોય તો દિન-૭ (સાત) માં પ્રમાણીત પુરાવા સહિત લેખીતમાં રજી.એ.ડી. થી જાણ કરવી (પ્રમાણિત પુરાવા વગરનાં વાંધા ધ્યાને લેવાશે નહી) અને જો તેમ કરવામાં કસુર થશે તો કોઈ વ્યક્તિ કે સંસ્થાનો કોઈપણ પ્રકારનો હક્ક, હિત, હિસ્સો, દાવો, બોજો, વાંધો ઈત્યાદી નથી અને જે હોય તો તે જતો (વેવ) કરેલ છે તેમ સમજી ટાઈટલ કલીયરન્સના અભિપ્રાય અંગેનું સર્ટીફીકેટ આપીશું ત્યારબાદ કોઈની કોઈ તકરાર ચાલશે નહી.\n"
        "દિનેશ બી. પટેલ, એડવોકેટ\n"
        "ઓફીસ : ૪૦૩ તથા ૪૦૪, બ્લોક-સી, ફોર્થ ફલોર, રેવતી પ્લાઝા, ભક્તિ સર્કલ પાસે, ઓફ એસ. પી. રીંગ રોડ, ન્યુ નિકોલ, અમદાવાદ - ૩૮૦૦૪૯.\n"
        "મો. નં. ૯૮૭૯૦ ૫૭૨૯૦."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    1412, 2434, 2052, 3090,
    left_text=(
        "મોજે - શેરથા\n"
        "ડીસ્ટ્રીકટ ગાંધીનગર રજીસ્ટ્રેશન સબ-ડીસ્ટ્રીકટ ગાંધીનગર (ઝોન - ૧) ગાંધીનગર તાલુકાના મોજે - શેરથા ગામની રી-સર્વે મુજબના બ્લોક નં. ૮૫૮ (જુના બ્લોક નં. ૧૫૫૦) ની હે.આરે.ચો.મી. ૦-૯૨-૭૫ ની ખેતીની જમીન રમીબેન ઉર્ફે રમીલાબેન તે ભીખાજીના દીકરી તે રજનીકાંત ઠાકોરના પત્ની તથા લસીબેન ઉર્ફે લીલાબેન તે ભીખાજી ના દીકરી તે ભોડાજી ઠાકોરના પત્નીની સંયુક્ત માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાયની માંગણી કરેલ છે, સદરહુ જમીન ઉપર કોઈનો બોજો, ચાર્જ, ખેડહક્ક, ગણોતહક્ક, ઈઝમેન્ટ રાઈટસ કે અન્ય કોઈપણ પ્રકારનો કબજા"
    ),
    right_text=(
        "હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર જમીનમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર જમીનનું ટાઈટલ કલીયરન્સ અંગેના અભિપ્રાયનું પ્રમાણપત્ર આપીશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    1412, 3104, 2052, 3792,
    left_text=(
        "મોજે - ફુલેત્રા\n"
        "ડીસ્ટ્રીકટ મહેસાણા રજીસ્ટ્રેશન સબ-ડીસ્ટ્રીકટ કડી તાલુકાના મોજે- ફુલેત્રા ગામની સીમનાં રી-સર્વે મુજબના સર્વે નં. ૧૧૯૬ (જુના સર્વે નં. ૯૯૩) ની હે.આરે.ચો.મી. : ૦-૨૭-૬૭ પૈકી દક્ષિણ દિશા તરફના ભાગની હે.આરે.ચો.મી. ૦-૧૩-૮૩.૫૦ ની ખેતીની જમીન (૧) રબારી શાંતાબેન તે નાથાભાઈની વિધવા, (૨) રબારી વિષ્ણુભાઈ નાથાભાઈ, (૩) રબારી વિક્રમભાઈ નાથાભાઈ, (૪) રબારી સીતાબેન નાથાભાઈની સંયુક્ત માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેના અભિપ્રાયની માંગણી કરેલ છે, સદરહુ જમીન ઉપર કોઈનો બોજો, ચાર્જ, ખેડહક્ક, ગણોતહક્ક, ઈઝમેન્ટ રાઈટસ કે અન્ય કોઈપણ પ્રકારનો"
    ),
    right_text=(
        "કબજા હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર જમીનમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર જમીનનું ટાઈટલ કલીયરન્સ અંગેના અભિપ્રાયનું પ્રમાણપત્ર આપીશું અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=20,
    right_lines=22,
)

# --- COLS 7-8 PUBLIC NOTICES (5 Notices: y=202..658, 680..1282, 1312..1968, 1988..2850, 2868..3792) ---
place_public_notice_2col(
    2076, 202, 2715, 658,
    left_text=(
        "જીલ્લો અમદાવાદ, તાલુકો દશક્રોઈ, મોજે બારેજા ની સીમના સરવે/બ્લોક નં.૭૨૧ (પ્રમોલગેશન અગાઉનો જુનો સરવે/બ્લોક નં. ૧૧૭૮) ની હે.આરે.ચો.મી. ૨-૫૪-૮૭ ક્ષેત્રફળ વાળી ખેતી લાયક જમીન પૈકીની ઉત્તર દિશા તરફની હે.આરે.ચો.મી. ૦-૯૪-૦૯ ક્ષેત્રફળ વાળી જુની શરતની ખેતીની જમીન મેંહદીરઝા આરીફઅલી નુરાની ની સ્વતંત્ર માલીકીપણા, કબજા, ભોગવટામાં આવેલી હોવાનું જણાવી ટાઈટલ ક્લીયર સર્ટીફીકેટ માંગેલ છે જેથી મજકુર જમીનમાં અન્ય કોઈપણ"
    ),
    right_text=(
        "શખ્સનો કોઈપણ પ્રકારનો લાગભાગ હક્ક, હિત, હિસ્સો પોષાતો હોયતો નીચેના સરનામે દિન-૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી ત્યારબાદ કોઈનો કોઈપણ પ્રકારનો વાંધો તકરાર ચાલશે નહીં અને જે તે શખ્સનો પોષાતો લાગભાગ હક્ક, હીત, હીસ્સો જતો યાને વેવ કરેલ છે તેમ સમજી ટાઈટલ ક્લીયર સર્ટિફિકેટ આપવામાં આવશે.\n"
        "નીલેશ એન. પટેલ, એસોસીએટ્સ\n"
        "પરેશા બી. પટેલ (એડવોકેટ)\n"
        "૫૦૭, પાંચમો માળ, શીવાલીક સત્યમેવ, એસ.પી. રીંગ રોડ, આંબલી, અમદાવાદ. મો. ૯૦૫૪૬૮૪૧૫૯"
    ),
    left_lines=14,
    right_lines=16,
)

place_public_notice_2col(
    2076, 680, 2715, 1282,
    left_text=(
        "જત રજીસ્ટ્રેશન ડિસ્ટ્રીકટ ગાંધીનગર સબ-ડિસ્ટ્રીકટ દહેગામ ના તાલુકા દહેગામ ના મોજે હરસોલીની સીમના ખાતા નં.૧૫૧૪ માં ચાલતા રિ-સર્વે/બ્લોક નં.૮૭૯ (જુના સર્વે નં. ૪૯૩) ની ૦-૬૪-૬૦ હે.આરે.ચો.મી., આકાર રૂા.૩.૨૫ પૈસાના ક્ષેત્રફળવાળી જુની શરતની ખેતીની જમીન રમેશભાઈ રવજીભાઈ ડોબરીયાની સ્વતંત્ર માલિકી, કબજા-ભોગવટાની બોજાઓથી મુક્ત ટાઈટલ કલીયર અને માર્કેટેબલ આવેલી છે તેમ જણાવી તેઓએ અમારા અસીલને વેચાણ આપવાનું નક્કી કરીને અમારી પાસે સદરહુ જમીનના ટાઈટલ કલીયર અને માર્કેટેબલ હોવાના અભિપ્રાય અંગેના સર્ટીફીકેટ ની માંગણી કરેલ છે તો સદરહુ જમીનમાં કોઈ વ્યક્તિ કે સંસ્થાનો"
    ),
    right_text=(
        "કોઈપણ પ્રકારનો હક્ક, હિત, હિસ્સો, દાવો, બોજો, વાંધો હોય તો દિન-૭ (સાત) માં પ્રમાણીત પુરાવા સહિત લેખીતમાં રજી.એ.ડી. થી જાણ કરવી (પ્રમાણિત પુરાવા વગરનાં વાંધા ધ્યાને લેવાશે નહી) અને જો તેમ કરવામાં કસુર થશે તો કોઈ વ્યક્તિ કે સંસ્થાનો કોઈપણ પ્રકારનો હક્ક, હિત, હિસ્સો, દાવો, બોજો, વાંધો ઈત્યાદી નથી અને જે હોય તો તે જતો (વેવ) કરેલ છે તેમ સમજી ટાઈટલ કલીયરન્સના અભિપ્રાય અંગેનું સર્ટીફીકેટ આપીશું ત્યારબાદ કોઈની કોઈ તકરાર ચાલશે નહી.\n"
        "દિનેશ બી. પટેલ, એડવોકેટ\n"
        "ઓફીસ : ૪૦૩ તથા ૪૦૪, બ્લોક-સી, ફોર્થ ફલોર, રેવતી પ્લાઝા, ભક્તિ સર્કલ પાસે, ઓફ એસ. પી. રીંગ રોડ, ન્યુ નિકોલ, અમદાવાદ - ૩૮૦૦૪૯.\n"
        "મો. નં. ૯૮૭૯૦ ૫૭૨૯૦."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    2076, 1312, 2715, 1968,
    left_text=(
        "મોજે - લ્હોર\n"
        "ડીસ્ટ્રીકટ મહેસાણા રજીસ્ટ્રેશન સબ-ડીસ્ટ્રીકટ કડી તાલુકાના મોજે - લ્હોર ગામની સીમના રી-સર્વે મુજબના સર્વે નં. ૭૫૪ (જુના સર્વે નં. ૪૫૧) ની જમીનને સીટી સર્વે વોર્ડ : લ્હોર (બીનખેતી) માં સમાવેશ કરી ફાળવેલ સીટી સર્વે નં.NA754 ની ચો.મી.૩૧૬૪ ની બિનખેતીની જમીન દક્ષિણી રોમી શૈલેષની સ્વતંત્ર માલિકી, કબજા, ભોગવટાની તમામ પ્રકારના બોજાઓથી તેમજ કાનુની વિવાદોથી મુક્ત હોવાનું જણાવીને અમારી પાસે ટાઈટલ્સ કલીયરન્સ અંગેનાં અભિપ્રાયની માંગણી કરેલ છે, સદરહુ જમીન ઉપર કોઈનો બોજો, ચાર્જ, બાનાહક્ક, ડેવલપમેન્ટ હક્ક કે અન્ય કોઈપણ પ્રકારનો કબજા હક્ક કે લાગભાગ યાને હક્ક હિસ્સો પોષાતો હોય તો અમોને નીચેના સરનામે દિન-"
    ),
    right_text=(
        "૭ માં લેખીત પુરાવા સહિત રજી.એ.ડી.થી જાણ કરવી અને તેમ કરવામાં નહી આવે તો સદર જમીનમાં કોઈનો કોઈપણ જાતનો હક્ક રહેલો નથી અને હોય તો તે જતો કરેલ છે તેમ સમજી મુદત વીત્યે સદર જમીનનું ટાઈટલ કલીયરન્સ અંગેનાં અભિપ્રાયનું સર્ટિફિકેટ ઈસ્યુ કરવામાં આવશે અને તે પછીથી કોઈનો કોઈપણ જાતનો વાંધો તકરાર ચાલશે નહી.\n"
        "તા.૨૦-૧૦-૨૦૨૬\n"
        "મનીષ કનુભાઈ પટેલ, એડવોકેટ,\n"
        "ચિરાગ દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "અમીત દશરથભાઈ પટેલ, એડવોકેટ,\n"
        "હેત શંકરભાઈ પટેલ, એડવોકેટ,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "ઠે. એ / ૨૦૨, સેકન્ડ ફલોર, એસ. જી. બીઝનેશ હબ, ગોતા ઓવરબ્રિજ પાસે, એસ.જી. હાઈવે, ગોતા, અમદાવાદ.\n"
        "મો.૮૮૭૯૩૪૪૩૩૩"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    2076, 1988, 2715, 2850,
    left_text=(
        "આથી જાહેર જનતાને જણાવવાનું કે, ડિસ્ટ્રીકટ અમદાવાદ રજીસ્ટ્રેશન સબ-ડિસ્ટ્રીકટ તથા તાલુકા બાવળાનાં ગામ મોજે રજોડાની સીમનાં સર્વે નંબર-૬૭૧ (જુના સર્વે/બ્લોક નંબર- ૮૭૭/૨ પૈકી)નાં ક્ષેત્રફળ- ૧૬૨૯૪ સમચોરસમીટર પૈકી ક્ષેત્રફળ- ૫૩૦ સમચોરસમીટર ને.હા.નંબર- ૮-એ માં સંપાદન થતા બાકી રહેતા ક્ષેત્રફળ- ૧૫૭૬૪ સમચોરસમીટર બીનખેતીની પરવાનગીવાળી જમીન, શિલ્પાબેન રાકેશભાઈ શાહ, રહેવાસી : ૨૦, ‘પારસ’, વિદ્યાનગર સોસાયટી, ઉસ્માનપુરા, અમદાવાદનાંએ તેઓનાં કુલ સ્વતંત્ર માલિકી પ્રત્યક્ષ કબજા ભોગવટામાં તેમજ તમામ પ્રકારનાં બોજાઓથી મુક્ત આવેલ હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાનું નક્કી કરી અમારી પાસે ઉપરોક્ત જમીનનાં ટાઈટલ કલીયરન્સ સર્ટીફિકેટની માંગણી કરેલ છે. સબબ સર્વે શખ્સો, વ્યક્તિ, પેઢી, બેંક, નાણાંકીય સંસ્થા કે અન્ય કોઈપણ કે જેઓ વેચાણ, વારસો, ભેટ, લાયસન્સ, કબજો, ગીરો, લીયન, ચાર્જ, ભરણપોષણ, ઈઝમેન્ટ, અદલાબદલો, ડેવલપર કે ફાઈનાન્સર તરીકે કે"
    ),
    right_text=(
        "બાનાખતના કરાર, પાવર ઓફ એટર્ની, કબજા કરાર, સમજૂતી કરાર, હુકમનામું કે અન્ય કોઈ લખાણ હેઠળ કે કોર્ટ કાર્યવાહી હેઠળ કે કુટુંબના સભ્ય કે વારસદાર તરીકે કે બીજી કોઈપણ રીતે ઉપરોક્ત જમીન પર હક્ક, દાવો કે અલાખો ધરાવતા હોય તેમણે તેની લેખિત જાણ પુરાવાની સર્ટીફાઈડ નકલ સાથે આ નોટિસ પ્રસિધ્ધ થયેથી દિન-૭ (સાત)ની અંદર નીચેના સરનામે સ્પીડ પોસ્ટથી કરવી. જો તેમ કરવામાં નહીં આવે તો ઉપરોક્ત જમીનમાં કોઈનો કોઈપણ પ્રકારનો લાગભાગ, હક્ક, હિસ્સો પોષાતો નથી અને પોષાતો હોય તો તે જતો યાને કે વેઈવ (WAIVE) કરેલ છે તેમ સમજી મુદત વિત્યે ટાઈટલ કલીયરન્સ સર્ટીફિકેટ ઈશ્યુ કરવામાં આવશે તેમજ અમારા અસીલ વેચાણ દસ્તાવેજને લગતી કાર્યવાહી પૂર્ણ કરશે અને ત્યારબાદ કોઈની કોઈપણ પ્રકારની તકરાર ચાલશે નહીં જેની આથી નોંધ લેવી.\n"
        "તારીખ : ૧૮/૧૦/૨૦૨૬,\n"
        "ફાઈલ નંબર- ૨૪૦૦૯\n"
        "B R PATEL & Co.\n"
        "Advocates, Solicitors & Corporate Attorney's\n"
        "15, Dolly apartment, Ambawadi Circle, Ahmedabad-380006.\n"
        "Phone : 26466400, 26466401"
    ),
    left_lines=25,
    right_lines=27,
)

place_public_notice_2col(
    2076, 2868, 2715, 3792,
    left_text=(
        "મોજેઃ શાહવાડી, તાલુકા વટવા, જીલ્લા અમદાવાદની સીમના (૧) સર્વે/બ્લોક નંબરઃ ૨૫૫/૧ ની ખાતા નંબરઃ ૨૪૧ થી સમાવેશ કુલ ૦-૩૯-૪૬ હે.આર.ચો.મી.ની જમીન હાલ મૃદુલાબેન દિપકકુમાર શેઠના માલીકી કબજા ભોગવટાની (૨) સર્વે/બ્લોક નંબરઃ ૨૬૮ ની ખાતા નંબરઃ ૨૪૩ થી સમાવેશ કુલ ૦-૬૧-૭૧ હે.આર.ચો.મી.ની જમીન હાલ કિર્તીકુમાર ઉર્ફે કિરીટભાઈ જમનાદાસ શેઠના માલીકી કબજા ભોગવટાની તથા (૩) સર્વે/બ્લોક નંબરઃ ૨૭૭ ની ખાતા નંબરઃ ૨૪૨ થી સમાવેશ કુલ ૦-૪૨-૪૯ હે.આર.ચો.મી.ની જમીન હાલ દિપકકુમાર જમનાદાસ શેઠ ના માલીકી કબજા ભોગવટાની તથા (૪) સર્વે/બ્લોક નંબરઃ ૨૭૮/૧ ની ખાતા નંબરઃ ૧૭૦ થી સમાવેશ કુલ ૦-૨૦-૨૩ હે.આર.ચો.મી.ની સમગ્ર જમીન પૈકી ૮૨૫ ચો.મીની જમીન હાલ રાજેશ્રીબેન કિર્તીકુમાર શેઠ ના માલીકી કબજા ભોગવટાની મળી કુલ ૧-૫૧-૯૧ હે.આર.ચો.મી.ની જમીન કે જેનો ટી.પી. સ્કીમ નંબરઃ ૧૨૫ (સૈજપુર-ગોપાલપુર-શાહવાડી) માં ફાળવવામાં આવેલ સંયુક્ત ફા.પ્લોટ નંબરઃ ૭૭/૧+૮૬+૯૩+૯૪ ની સમગ્ર જમીન"
    ),
    right_text=(
        "પૈકી મળવાપાત્ર બીનખેતીની જમીન ઉપર અન્ય કોઈના માલીકી હકક, હિસ્સા, વારસાઈ લાગભાગ કે બોજા રહીત હોવાનું જણાવી અમારા અસીલને વેચાણ આપવાના હેતુથી મજકુર તમામ જમીનોના ટાઈટલ કલીયર હોવા બાબતના અભિપ્રાય ની માંગણી અમો પાસે કરેલ છે. મજકુર તમામ જમીનો કે કોઈપણ જમીન ઉપર કોઈનો કોઈપણ જાતનો વારસાઈ હકક, હિસ્સો, દાવો, બોજો બાનાખતના હકકો, લીયન કે એટેચમેન્ટ કે લાગભાગ હોય તો આ નોટીસ પ્રસિધ્ધ થયેથી દિન ૭ (સાત) માં તેની ખરી નકલોવાળા દસ્તાવેજી પુરાવા સહીતની લેખીત જાણ અમોને નીચેના સરનામે કરવી અન્યથા મજકુર જમીન ઉપર આવા હકક, હીસ્સા, બોજા કે લાગભાગ તેઓએ સ્વેચ્છાએ જતા (વેઈવ) કરેલ છે તેમ સમજી મુદત વીત્યે ટાઈટલ સર્ટીફીકેટ આપવામાં આવશે તથા વેચાણ દસ્તાવેજની કાર્યવાહી પુર્ણ કરાવી લેવામાં આવશે જેની જાહેર જનતાએ નોંધ લેવી.\n"
        "તારીખઃ ૨૦/૧૦/૨૦૨૬\n"
        "નિમિષ વી. દેશાઈ, એડવોકેટ,\n"
        "V.D. DESAI & CO.\n"
        "૨૧૨, ‘આકાશરથ’ બીજો માળ, નેશનલ હેન્ડલુમ સામે, લો ગાર્ડન, અમદાવાદ\n"
        "ફોનઃ (મો) ૯૯૯૮૨ ૧૭૩૫૪"
    ),
    left_lines=27,
    right_lines=29,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_06_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_06_SameToSame.dns"
    png_path = target_dir / "Page_06_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_06_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_06_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
