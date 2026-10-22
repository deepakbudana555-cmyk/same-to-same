from gs_running_header import build_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME PAGE 8 BUILDER FOR GUJARAT SAMACHAR (Page Designer Live Engine)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Gujarati Text ('Gopika' Bold & 'Gopika' Regular)
  across all 6 Editorial & Column Features on Page 8:
  1. તંત્રીલેખ (Editorial): કોર્પોરેટ કૃષિનું પ્રભાત (Cols 1-2 Top)
  2. અલ્પવિરામ: બદલાયેલું હવામાન હવે જગતને જંપવા દે એમ નથી (Cols 3-6 Top)
  3. ટુ ધ પોઈન્ટ (અજિત પોપટ): હૈયે હતું એ હોઠે આવ્યું, અમારે તો શાસન પલટો કરવો છે... (Cols 7-8 Top)
  4. પ્રસંગપટ: ગુગલ મેપનો સ્વદેશી વિકલ્પ મેપલ્સ: પરંતુ માર્કેટીંગ નથી (Cols 1-3 Bottom)
  5. બોજ વિનાની મોજ (અક્ષય અંતાણી): કાગડા મળે માંડ માંડ એટલે વધતી જાય ડિમાન્ડ (Cols 4-7 Bottom)
  6. કલ્પવૃક્ષ: સુવાક્યો (Col 8 Bottom)
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
ASSETS_DIR = DIR_SMAE / "Page_08_Assets"

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
        "title": "Gujarat Samachar — Page 08 (100% Same-to-Same Editable Gopika)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsGreenTint", "color": "#cde2b8"}},
    {"command": "swatch.create", "params": {"name": "GsYellowTint", "color": "#fdf3d0"}},
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


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 8 Running Header...")
build_running_header(8, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. EDITORIAL (તંત્રીલેખ): કોર્પોરેટ કૃષિનું પ્રભાત (COLS 1-2 TOP)
# ==============================================================================
print("Building Editorial (Corporate Agriculture Dawn, Cols 1-2 Top)...")
draw_box(82, 194, 720, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_png(85, 196, 717, 336, "editorial_masthead.png")
place_exact_display_lines(
    94, 344, 708, 412,
    lines=["કોર્પોરેટ કૃષિનું પ્રભાત"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    92, 420, 710, 2066,
    text=(
        "છેલ્લા જે બે ત્રિમાસિક પરિણામો આવ્યા એણે કૃષિ અને મૂલ્યવર્ધિત કૃષિ પેદાશો માટે આશાવંત ચિત્ર રજૂ કર્યું છે. ભારતમાં કૃષિ પેદાશો સંબંધિત કોર્પોરેટ કંપનીઓમાં એકાએક વધારો થયો છે અને એમાંની અનેક કંપનીઓ હવે આંતરરાષ્ટ્રીય લિન્કેજ ધરાવતી થઈ છે. દેશમાં નવા નાણાંકીય વર્ષનો પ્રારંભ થયો એને સમય વીતી ગયો છે અને આ સમયગાળામાં ગંગા-યમુનામાં ઘણા પાણી વહી ગયા છે. વાસંતિક ફૂલોના રંગની જેમ અર્થતંત્રના અનેક રંગ આ વરસે પ્રજાએ જોવાના છે. ભારત અત્યારે સમય અને સંયોગોના એક એવા ત્રિભેટે આવીને ઊભેલો દેશ છે કે જેની સામે રાષ્ટ્રીય જીવનના અનેક ક્ષેત્રોમાં અનેક પડકારો ઊભા છે. ગમે તેવું નેતૃત્વ હોય તો પણ આ પડકારોને પહોંચી વળવાનું કામ આસાન નથી. આફ્રિકન દેશો સહિતના અનેક દરિદ્ર રાષ્ટ્રો ભીષણ મંદીમાં મદદ માટે ભારત તરફ મીટ માંડીને બેઠા છે.\n"
        "ઘરના છોકરાઓએ ઘંટી ચાટવી ન પડે એ માટે સરકાર પારકાને આટો આપવામાં સ્વાભાવિક વિલંબ કરી રહી છે. તોય આજ સુધીમાં લાખો ટન અનાજ નિકાસ થયા છે ને ભેટ પણ અપાયા છે. ટૂંકાગાળાના આ ખેલનો ઈતિહાસ બહુ લાંબો છે. કેન્દ્ર સરકારે ચોખાની કેટલીક જાતોની નિકાસ પર પ્રતિબંધ મૂકે એનું મુખ્ય કારણ અનિયત ચોમાસા હોય છે. ઉત્તરાખંડ અને હિમાચલ પ્રદેશમાં વરસાદ શબ્દ સાંભળતા જ લોકો થરથર ધ્રૂજવા લાગે છે એવો એમનો આ વખતનો અનુભવ છે. સરકાર પીડિતોને મદદ કરે છે પરંતુ આખી દુનિયા ફરી વસાવવી પડે એટલે શું એ પ્રલયનો ભોગ બનેલા લોકોને પૂછો તો ખબર પડે. જરૂરિયાતની સામે ચાલુ વરસે અનાજ-કઠોળ ઉત્પાદન બહુ જ ઓછું આવવાનું છે. હવે આ ચોમાસાની વિદાય પછી મોડી પડેલી રવિ મોસમ પર ઘણો આધાર છે. પાછલી મોસમની ઘટને કારણે જીરુ, ડુંગળી, તેલીબિયાંના ભાવ આવતા શિયાળે પ્રજાને વ્યાકુળ કરશે.\n"
        "હવામાનમાં ફેરફારોને કારણે વરસાદનો છેલ્લો રાઉન્ડ ઘટાદાર વાદળો અને વર્ષાથી છવાયેલો હતો પરંતુ જે ખેતરો ધોવાઈ ગયા છે એમને ગંભીર નુકસાન થયું છે. દેશમાં ખરીફ પાક સારો હોય તો જ એને અનુસરીને રવિપાક પણ સારો થાય છે. એટલે ચાલુ નાણાકીય વર્ષ કૃષિ ક્ષેત્ર માટે ફળદાયી તો રહેવાનું છે પરંતુ એના પરિણામે જ બજારમાં રૂપિયો ફરતો થવાનો છે અને અન્ય ઔદ્યોગિક સહિતના ક્ષેત્રમાં પણ આ વર્ષે તેજીની અસર દેખાવાની છે. એ તેજીની અત્યારે ખરેખર શરૂઆત થઈ ગઈ છે. દુનિયાભરમાં મંદીના સન્નાટા બોલતા હોય ત્યારે ભારતીય અર્થતંત્ર તેજીના હવામાનને લઈ આવે તે એશિયાના વિવિધ દેશો માટે આશ્ચર્યજનક છે. ચીનથી પાછા ફરી રહેલા અનેક રોકાણકારો પોતાના ભંડોળ સાથે હવે ભારતમાં અવતરણ કરવા લાગ્યા છે. નવાઈની વાત એ છે કે આગંતુક વિદેશી રોકાણકારોને ભારતીય ઉદ્યોગોમાં હવે કૃષિ સંબંધિત ઔદ્યોગિક પ્રવૃત્તિમાં વધુ રસ પડે છે. આ એક શુભ ચિહ્ન છે.\n"
        "રિઝર્વ બેન્કના ગવર્નરે હવે શરૂ થઈ રહેલી રવિ મોસમ માટે ૧૦.૫ ટકાનો વિકાસ અંદાજ મૂક્યો છે. જો કે પહેલી નજરે મુશ્કેલ લાગે છે, પરંતુ ઈ. સ. ૨૦૨૫ - ૨૦૨૬ ના બેકલોગને સરભર કરવા માટે ઉદ્યોગો અને સેવાઓ જે રીતે કામે લાગેલા દેખાય છે, એ જોતાં એ સાવ અસંભવ નથી. મિસ્ટર શક્તિકાન્તે અગાઉ પણ કહ્યું જ હતું કે ભારતીય અર્થતંત્રની ગાડી હવે પાટે ચડી ગઈ છે અને સુધારાવાદી અભિગમ દ્વારા અર્થતંત્રમાં ચડતી કળાનો ચંદ્ર દેખાય છે. દેશમાં સરકાર સતત ગુલાબી ચિત્ર રજૂ કરવા ચાહે છે પરંતુ નાના પરિવારોના પર્સ-પાકિટ વધુ નાના અને ખાલી થઈ ગયા છે. અર્થતંત્ર જ્યારે કટોકટીના ભેડાઘાટમાંથી પસાર થઈ રહ્યું છે, ત્યારે કુદરતી કૃપા સરીખો વરસાદ જો સકારાત્મક રહે તો કૃષિ ક્ષેત્રની મદદથી અર્થતંત્ર વધુ ગતિવાન બને. કેન્દ્ર સરકારે દેશના અધિક ડેન્ગ્યુ સંક્રમિત ૧૨ રાજ્યો સાથે ઉચ્ચસ્તરની એક મિટિંગ યોજીને સખત પગલાં લેવાનો અનુરોધ કર્યો છે. ચીનમાં હવે ઝેરી તાવના રોગચાળાની સ્થિતિ ગંભીર છે. એનો લાભ ભારતને મળે છે.\n"
        "સ્ટાર્ટ અપનો પ્લાન લગભગ બધા જ સેક્ટરમાં નિષ્ફળતાને જઈ વર્યો છે. આરંભે શૂરા જેવો ઘાટ ધરાવતા સ્ટાર્ટ અપ ઈન્ડિયા પ્રોજેક્ટનું બાળમરણ થયું એવું કહેવું અતિશયોક્તિ નહિ ગણાય. ઈ. સ. ૨૦૧૫ માં બધા જ ભારતીય સ્ટાર્ટ અપ પ્રોજેક્ટે દેશાવિદેશમાંથી સાડા સાત અબજ ડોલરનું ફન્ડિંગ ભેગું કર્યું હતું જે એના પછીના વર્ષે એટલે કે ૨૦૧૬ માં ઘટીને સાડા ત્રણ અબજ ડોલર થઈ ગયેલું. ઈ. સ. ૨૦૧૬ ની નોટબંધીએ તો અડધોઅડધ સ્ટાર્ટઅપની બુનિયાદ તોડી નાંખી હતી."
    ),
    target_lines=54,
    font_style="Bold",
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. ALPVIRAM: બદલાયેલું હવામાન હવે જગતને જંપવા દે એમ નથી (COLS 3-6 TOP)
# ==============================================================================
print("Building Alpviram (Climate Change Essay, Cols 3-6 Top)...")
draw_box(736, 194, 2060, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    746, 200, 2050, 304,
    lines=["બદલાયેલું હવામાન હવે જગતને જંપવા દે એમ નથી"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    746, 312, 1051, 2066,
    text=(
        "ઉત્તર ભારત અને દક્ષિણના કેટલાક રાજ્યોમાં અત્યારે ધોધમાર વરસાદ ચાલુ છે. શરદ પૂર્ણિમા નજીક આવી રહી છે તે ખરેખર તો સ્વચ્છ આકાશની મોસમ છે. ગુજરાત ઉપર પણ આજકાલમાં હાથીઓના સૈન્ય જેવા વિરાટ વાદળો છવાઈ જવાના છે. મોસમ રંગ બદલી રહી છે. સાંભળવું ગમે નહિ તો ભલે પણ એ સત્ય છે કે પ્રકૃતિએ પડખું ફેરવ્યું છે. જાપાન અને યુરોપે ગયા વરસે કદી કલ્પના પણ કરી ન હતી એવા ઉકળાટનો અનુભવ કર્યો છે. પછીથી વરસાદ અને ભીષણ ઝંઝાવાત અદ્યાપિ ચાલુ છે. છેલ્લા એક વરસમાં પૃથ્વી પર આવેલા વાવાઝોડાની સરેરાશ પાછલા પચાસ વરસમાં સૌથી વધુ છે. ભારતમાં વરસાદ પડે ત્યાં આડેધડ પડે એ સંયોગો કાયમી થઈ ગયા છે.\n"
        "પૂર્વ ભારત માટે ચોમાસુ એક આપત્તિ છે. ખરેખર વ્યક્તિગત રીતે દરેક મનુષ્ય આત્મદર્શન કરે કે પાછલા વરસોમાં કોરોનાના આગમન પછી એણે પોતાની જીવનશૈલીને કેટલીક બદલાવી તો ખ્યાલ આવશે કે અભિજાત લક્ષણો એમ થોડાક ગોથા ખાવાથી બદલાતા નથી. મૃત્યુના ભયથી ડરતા ડરતા રોજ ત્યારે ઉકાળાઓ ગટગટાવ્યા એ કંઈ પ્રકૃતિ કે પર્યાવરણ સાથેની દોસ્તી ન હતી. શરીરને નુકસાનકારક જે કંઈ આહાર છે તે અટકાવવાની વાત બહુ શરૂઆતમાં વિશ્વ આરોગ્ય સંસ્થાએ કહી હતી. જો એવા ત્યાજ્ય આહારનો ઉપયોગ અટકે તો જ એના ઉત્પાદનો બંધ થાય.\n"
        "મર્યાદા બહારના આહાર શરીરની ભીતર દુર્ઘટના નોતરે છે જે ડાક્ટર જ જોઈ શકે કે સાંભળી શકે. કોરોનાએ ઈમ્યુનિટીને પડકારેલી છે. ને સરેરાશ ભારતીય પ્રજાની ઈમ્યુનિટીને દુનિયા આજે વખાણે છે. જો કે જેટલા મૃત્યુ કોરોના વખતે થયા એ દુઃખદ છે. આજે પણ ડેન્ગ્યુ અને હૃદયરોગની એવરેજ બહુ ઊંચી છે. જિંદગી અલ્પવયે સમેટાઈ જાય ત્યારે સપનાઓની એક લાંબી વણઝાર પણ દિવંગત થઈ જતી હોય છે. મૃત્યુ સંસારનો સૌથી કારમો ઘા છે. જેમણે આકસ્મિક રીતે સ્વજનો ગુમાવ્યા છે તેઓના ઘર હજુ પણ શોકના વાદળો છવાયેલા જોવા મળે છે.\n"
        "આમ તો નવા સૈકાના આ ત્રીજા દાયકાની શરૂઆત જ હજારો-લાખો એકરના સળગતા જંગલો વચ્ચે થઈ હતી. પચાસ હજાર ચોરસ કિલોમીટરની આગથી થયેલા નુકસાનનો હિસાબ કરતા ઓસ્ટ્રેલિયન"
    ),
    target_lines=58,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1078, 312, 1385, 520,
    text="સરકારને એક વરસ લાગ્યું. કચ્છના અને લાતુરના ભૂકંપનો હિસાબ કરતા આપણને પણ એક વરસ લાગ્યું હતું. સહેજ પણ ચિંતા વિના લોકો જિંદગી પસાર કરે છે. જે ચિંતા છે તે પોતાની અંગત છે. પર્યાવરણની નથી. આપણી માનસિકતા એવી છે કે ઓસ્ટ્રેલિયન",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 312, 1718, 520,
    text="ગયા વખતે પહેલો એવો શિયાળો હતો જેણે રૂમ હિટરનું માર્કેટિંગ કર્યું. કોઈ મોસમ એના અતિરેકને કારણે માણી શકાય નહિ. ઠંડા પવનના શોખીનો એવી મોસમમાં જો વનવગડે અલગારીની રખડપટ્ટી આરંભે તો તેઓએ આરોગ્યની પછડાટ જ વેઠવાની",
    target_lines=7,
    first_indent_pt=9.0,
)
place_png(1078, 529, 1718, 966, "alpviram_illus.png")
place_exact_body_column(
    1078, 974, 1385, 1170,
    text="જંગલો સળગ્યા પણ એ આગ અહીં થોડી આવવાની છે ? પરંતુ એ આગ અહીં આવી શકે છે. કારણ કે આ આગ પૃથ્વી નામના આપણા સહિયારા ઘરમાં લાગેલી આગ છે. કોઈ બીજા ગ્રહ કે ઉપગ્રહ પરનો આ ધૂમાડો નથી. સંયુક્ત રાષ્ટ્રસંઘ",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 974, 1718, 1170,
    text="આવે. કુદરતને માણવાની મઝા પણ ઓછી થવા લાગી છે કારણ કે એ કુદરતના ઉછેર અને સંભાળમાં આપણું તો કોઈ યોગદાન નથી ! પ્રકૃતિ એને જ રમણીય અનુભવ અને આહલાદનો અનુભવ કરાવશે કે જે એના અભિમુખ",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1178, 1242, 1350,
    text="અંતર્ગતના વિશ્વ મોસમ સંગઠનના નવા અહેવાલો આમ તો માણસ જાતની ઊંઘ ઉડાડવા માટે પૂરતા છે.",
    target_lines=6,
    first_indent_pt=0.0,
)
place_png(1249, 1179, 1552, 1343, "alpviram_badge.png")
place_exact_body_column(
    1558, 1178, 1718, 1350,
    text="હશે. આખી જિંદગી કુદરતી સંપદા સાથે માત્ર ભોગવાદી નીતિ રાખનારાઓએ એની સજા ભોગવવી પડશે.",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1356, 1385, 1524,
    text="હવે પછી આવનારા તમામ વરસોમાં કુદરત રૂઠેલી રહેવાની છે. એક વાત એ ધ્યાનમાં લેવા જેવી છે કે દરેક આપત્તિમાં હવે બચાવ કામગીરી ધીમી પડતી જાય છે. એટલે કે કુદરતી સંકટ આત્યંતિક હોય છે. હવે",
    target_lines=6,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1356, 1718, 1524,
    text="ગત શિયાળે મધ્યમ વર્ગના અને ભાડાના મકાનમાં વસતા લોકો દોડી દોડીને રૂમ હિટર લઈ આવ્યા હતા. ગેસ ગિઝર અને ઈલેક્ટ્રિક ગિઝર સંબંધિત દુર્ઘટનાઓ અવાર નવાર વાયરલ થતી",
    target_lines=6,
    first_indent_pt=9.0,
)
draw_box(1089, 1531, 1712, 1757, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1100, 1538, 1700, 1750,
    lines=[
        "કુદરતનાના મિજાજમાં આવેલા પરિવર્તનને પામી",
        "ગયા પછી સમયવર્તે સાવધાન થવાની આ ઘડી",
        "છે. કેલેન્ડરમાં દેખાતા મહિનાઓ અને વાતાવરણ",
        "વચ્ચેની સંગતતા હવે નહિવત્ જોવા મળશે"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 1764, 1385, 2066,
    text="કુદરત આગાહીઓને વશ નથી. ભલે હવામાન ટેકનોલોજી વધી પરંતુ અંદાજ ખોટા પડે છે. પૂનાની વેધશાળાએ ગયા વખતે સ્પષ્ટ કહ્યું હતું કે આ વખતે શિયાળો હૂંફાળો રહેવાનો છે, બહુ ઠંડી તો પડવાની જ નથી ! એ વિધાનો સાવ અવૈજ્ઞાનિક સાબિત થયા અને શિયાળો નિયમસરનો કાતિલ નીવડ્યો. જો કે ગ્લોબલ વોર્મિંગનો તો અર્થ જ એ છે કે ખૂબ જ ઠંડી અને અસહ્ય ગરમી.",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 1764, 1718, 2066,
    text="હોવા છતાંય એનું વેચાણ પણ મંદીમાં એકાએક વધી ગયું હતું. મોસમનો આહલાદ હવે બધા માણી શકે એમ નથી. કુદરતે તેના તમામ સર્જનોમાં મનુષ્યને મુઠ્ઠી ઉંચેરુ સ્થાન આપતાં તેને બુદ્ધિરૂપી વિશેષતા બક્ષી છે. આ જ બુદ્ધિને બળે મનુષ્ય પોતાને માટે, કુદરતના તમામ સર્જનોને માત્ર ને માત્ર પોતાની ભૌતિક સુખ-સુવિધાના સાધનો જ માની લીધા છે. તેને વિના મૂલ્યે",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 312, 2050, 2066,
    text=(
        "મળેલી અમૂલ્ય પ્રાકૃતિક સંપદાના વપરાશમાં તે કોઈ પ્રમાણભાન જાળવી શક્યો નથી.\n"
        "જેના કારણે કુદરતનું જે ચક્ર અત્યાર સુધી એક નિયત ગતિએ ચાલી રહ્યું હતું, તેમાં હવે થોડા થોડા અંતરાયો આવવા લાગ્યા છે. રૌદ્ર એ પણ કુદરતનું એક સ્વરૂપ છે. પોષતું તે જ મારતું નું બ્રહ્મ-સનાતન-સત્ય જાણે આવનારા ભવિષ્યની વાસ્તવિકતા બનીને આજે સમસ્ત માનવ સમાજની સામે આવીને ઊભું છે. જે પ્રકારે ઘરવપરાશના યંત્રોની પણ સમયાંતરે જાળવણી કરવામાં ન આવે તો, જે સ્થિતિ સર્જાય છે, તેવી જ સ્થિતિ હાલ વૈશ્વિક વાતાવરણમાં જોવા મળી રહી છે. જાપાનના પર્યાવરણવિદોએ કહ્યું છે કે કુદરતને પોતાના સાવ સ્વાભાવિક ક્રમમાં આવવા માટે આ આખી સદીની જરૂર પડશે, એટલો બધો ઉપદ્રવ માણસે વસુંધરા પર આચરેલો છે.\n"
        "હવાના બદલાયેલા રૂખ અને પ્રકૃતિના મિજાજમાં આવેલા પરિવર્તનને પામી ગયા પછી સમયવર્તે સાવધાન થવાની આ ઘડી છે. કેલેન્ડરમાં દેખાતા મહિનાને અને વાતાવરણ વચ્ચેની સંગતતા હવે ખૂબ જ ઓછી જોવા મળશે. ક્યારેક અનરાધાર વરસાદ, તો કદીક અચાનક જ ઘેરી વળતી કાતિલ ઠંડી અને તડાતડ પડતા કરાને જોઈને ઘણી અનુભવી આંખો આશ્ચર્યથી પહોળી થઈ જતી હોય છે. રણ પ્રદેશમાં નદીઓ વહી જાય તેટલો વરસાદ અને લીલાછમ્મ વિસ્તારનું ધૂળિયા રંગમાં રૂપાંતર એ વાતનો સંકેત છે કે કુદરતે હવે મનુષ્ય સાથેનો તેનો હિસાબનો ચોપડો ખોલી નાંખ્યો છે. વરસાદે આ વખતે દેશના અનેક સ્થળોએ છેલ્લા સવાસો વરસના ઈતિહાસનો નવો વિક્રમ રચી આપ્યો છે.\n"
        "સંયુક્ત રાષ્ટ્રસંઘના નેજાતળે કામ કરતા સંશોધકોના જૂથે ગહન અભ્યાસ પછી જાહેર કર્યું છે કે વીતેલો દાયકો ધગધગતો હતો. માણસજાતના ઈતિહાસમાં ઈ. સ. ૨૦૧૦ થી ઈ. સ. ૨૦૧૯ સુધીનો એક દાયકો બહુ ઊંચા ઉષ્ણતામાનમાં પસાર થયો છે. આ સંશોધકોએ કહ્યું કે ભીષણ ગરમી અને વિકરાળ ઠંડી માટે દુનિયાના દરેક દેશે તૈયાર રહેવું પડશે. પૃથ્વીના સરેરાશ તાપમાનમાં એટલો વધારો થયો છે કે જળ, વાયુ, જંગલો, નદીઓ, સરોવરો અને કૃષિમાં વિવિધ ઉથલપાથલ મચેલી છે અને હવેના વરસોમાં એમાં નવી અને અકલ્પિત અરાજકતાઓ વિશ્વસમુદાયે જોવાની છે. હવે ઈ. સ. ૨૦૨૦ થી ૨૦૨૯ સુધીનો આ ચાલુ દાયકો પાછલા કરતા પણ વધુ ખતરનાક હશે."
    ),
    target_lines=58,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. TO THE POINT (અજિત પોપટ): હૈયે હતું એ હોઠે આવ્યું... (COLS 7-8 TOP)
# ==============================================================================
print("Building To The Point (Ajit Popat Column, Cols 7-8 Top)...")
draw_box(2070, 194, 2718, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    2076, 200, 2712, 344,
    lines=[
        "હૈયે હતું એ હોઠે આવ્યું, અમારે તો શાસન",
        "પલટો કરવો છે, અરાજકતાવાદી બોલ્યા..."
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    2076, 350, 2382, 1020,
    text=(
        "આખરે હૈયે હતું એ હોઠે આવી ગયું. શુક્રવાર, ૧૬મી ઓક્ટોબરે પાટનગર નવી દિલ્હીમાં કહેવાતી તિરંગા યાત્રા વખતે પોલીસ વાનની બારીમાંથી ડાબેરી ચશ્મિસ્ટ નેતી નેહા બોરા બોલી, અમારે તો રેજિમ ચેન્જ જોઈએ છે. બાંગ્લાદેશે અમને માર્ગ દેખાડ્યો છે... બુલ શીટ ! ગયા અઠવાડિયે આ સ્થાનેથી કહેલું કે વડા ચૂંટણી કમિશનર જ્ઞાનેશ કુમાર તો બહાનું છે. અસલી નિશાન વડા પ્રધાન અને ગૃહ પ્રધાન છે. થોડાક, યસ થોડાક, વાચકોને આ વાત આકરી લાગી હતી. પરંતુ આખરે દૂધનું દૂધ અને પાણીનું પાણી થઈ ગયું. દુઃખે છે પેટ અને કૂટે છે માથું એ આનું નામ.\n"
        "સૌથી પહેલાં બાંગ્લા દેશની વાત કરીએ. પાકિસ્તાન અને બાંગ્લાદેશમાં ક્યારેય લોકશાહી સ્થિર થઈ નહોતી. કહેવાતી લોકશાહીની પીઠ પાછળ લશ્કરી શાસન હતું. બીજી બાજુ"
    ),
    target_lines=22,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 350, 2712, 1020,
    text=(
        "જોડે હું સંમત નથી. મૂળ કહેવાતા આંદોલનકારીઓને ફોરેન કોન્ટ્રીબ્યુશન રેગ્યુલેશન એક્ટ સામે વાંધો છે.\n"
        "આપણા દેશમાં કેટલીક કહેવાતી એનજીઓ વિદેશથી અઢળક નાણાં મેળવે છે અને એ નાણાંનો બેધડક દુરુપયોગ કરે છે. એક સાવ નાનકડો મુદ્દો યાદ કરાવું. ઉત્તર પ્રદેશમાં એકાદ બે નહીં, સત્તર હજાર ભૂતિયા મદરેસા પકડાયા હતા. એક મદરેસામાં ધારો કે દસથી બાર બાળકો કુરાન-એ-શરીફ પઢતા હોય એમ માની લઈએ તો ૧૭ હજાર મદરેસામાં કેટલાં બાળકો હોઈ શકે ? માંડો ત્રિરાશિ. આ સત્તર હજાર ભૂતિયા મદરેસા કેન્દ્ર સરકાર પાસેથી માતબર રકમ સહાય રૂપે મેળવતા હતા. યોગી આદિત્યનાથે એ બંધ કરાવ્યા.\n"
        "આવી તો સેંકડો કહેવાતી એનજીઓ દેશમાં છે જે દેશવિરોધી કાર્યોમાં વિદેશી નાણાં છૂટથી વાપરે"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1026, 2240, 1280,
    text="ભારતમાં ક્યારેય લશ્કરી શાસન સ્થપાય એવી શક્યતા નહોતી. છેક ઈંદિરા ગાંધી વડા પ્રધાન હતા ત્યારથી આ વાત સ્પષ્ટ થઈ ગયેલી.",
    target_lines=8,
    first_indent_pt=0.0,
)
place_png(2247, 1028, 2553, 1280, "to_the_point_badge.png")
place_exact_body_column(
    2560, 1026, 2712, 1280,
    text="છે. ફરી યાદ કરાવું. કોકરોચ અભિષેક દીપકે બોસ્ટન યુનિવર્સિટીમાં અનુસ્નાતક થઈને કામ શોધતો હતો. બેકાર હતો. તો",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1286, 2382, 2066,
    text=(
        "ઈંદિરાજીએ ત્યારના લશ્કરી સેનાપતિ હસમુખા પારસી બાવા સામ માણેકશાને પૂછેલું કે આપણા દેશમાં લશ્કર બળવો કરે એવું બને ખરું ? સામ પોતાની ટેવ મુજબ હસી પડેલા. એમણે મેડમને સમજાવેલું કે આપણે ત્યાં દરેક રાજ્યના યુવાનો લશ્કરનો એક અનિવાર્ય હિસ્સો છે. આપણું લશ્કર ખરા અર્થમાં કોસ્મોપોલિટન છે એટલે લશ્કરી બળવો શક્ય નથી....\n"
        "કોંગ્રેસી નેતાઓ આ હકીકત બરાબર જાણે છે એટલે જ લોકશાહી ઢબે ચૂંટાયેલી સરકારને ઊથલાવવા અરાજકતા સર્જવાનો જોખમી રસ્તો પસંદ કર્યો છે. પાકિસ્તાન અને બાંગ્લા દેશના લશ્કરમાં સોએ સો ટકા મુસ્લિમ યુવાનો છે એટલે લશ્કરી બળવો સહેલો છે, લોકશાહીને કચડવી ચપટી વગાડવા જેટલું આસાન છે. વિદેશી નાણાંના જોરે ભારતમાં અરાજકતા સર્જવાનો યોજનાપૂર્વકનો પ્રયાસ થઈ રહ્યો છે. સોશ્યલ મિડિયા પર આ મુદ્દે અસદુદ્દીન ઓવૈસીએ સ્પષ્ટ વાત કરી છે કે ભલે નરેન્દ્ર મોદી સામે મારો એક કરતાં વધુ મુદ્દે વિરોધ છે પરંતુ જે રીતે શાસન પલટાના બૂમબરાડા થઈ રહ્યા છે એની"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1286, 2712, 2066,
    text=(
        "દિલ્હી આવીને આંદોલન કરવાના પૈસા ક્યાંથી કાઢ્યા ? દિલ્હીમાં ભાડેથી કે પેઈંગ ગેસ્ટ તરીકે રહેતો હોય તો એનો નિર્વાહ શી રીતે થાય છે ? રોજિંદો ખર્ચ કોણ, કયા કારણે આપે છે ? વિચાર કરો પ્રિય વાચક. આવા તો ઘણા દીપક આ કહેવાતા આંદોલનમાં સક્રિય છે. સાવ સાદી ભાષામાં કહું તો જમ્મુ કશ્મીરમાં પોલીસ અને સિક્યોરિટી દળો પર પથ્થરમારો કરવા માટે કશ્મીરી બાળકોને રોજ પાંચ રૂપિયા ચૂકવાતા હતા એ જ રીતે દિલ્હીમાં ચાલી રહેલા તાયફા માટે જેન ઝીને રોજ અગાઉથી નક્કી કરાયેલું મહેનતાણું ચૂકવાય છે. એ સિવાય કોણ નવરું હોય કે રોજ સાંજ પડ્યે ધાંધલ કરવા આવી જાય ?\n"
        "દેશની ૧૩૦ કરોડની વસતિમાં રોજ સમજો કે પચાસ હજાર કે લાખ યુવાનો આંદોલન કરતા હોય તો એ કુલ વસતિનો એક ટકોય નથી થતો. અને પાછા આ લોકો શાસન પલટાની વાતો કરે છે. યે મૂંહ ઔર મસૂર કી દાલ ! નીત નવાં બહાનાં કાઢતા આવા અરાજકતાવાદીઓ સામે કડક હાથે કામ લેવું જ રહ્યું. શું કહો છો ?જ"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. PRASANGPAT: ગુગલ મેપનો સ્વદેશી વિકલ્પ મેપલ્સ (COLS 1-3 BOTTOM)
# ==============================================================================
print("Building Prasangpat (Mappls vs Google Maps, Cols 1-3 Bottom)...")
draw_box(82, 2092, 1055, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
draw_box(92, 2102, 1045, 2178, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    100, 2108, 1038, 2172,
    lines=["ગુગલ મેપના લોચાના કારણે ૧૭ના જાન ગયા"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    94, 2186, 1042, 2378,
    lines=[
        "ગુગલ મેપનો સ્વદેશી વિકલ્પ",
        "મેપલ્સ: પરંતુ માર્કેટીંગ નથી"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    92, 2386, 388, 3622,
    text=(
        "મોત કઈ દિશામાંથી આવશે અને કોના કારણે આવશે તે ખબર પડી શકતી નથી. કોલકત્તામાં દુર્ગા પાંડલનો એકભાગ તૂટી પડતાં નાસભાગમાં ૧૭ દર્શનાર્થીઓ મોતને ભેટ્યા હતા જ્યારે ગ્વાલિયરમાં ગુગલ મેપના દોરી સંચાર અનુસાર ચાલતી ટ્રકે કાબુ ગુમાવતા ૧૫ લોકોના મોત થયા હતા.\n"
        "ટ્રક રાત્રે ૧.૩૦ વાગે શિતળા માતાની મંદિરે જતા શ્રધ્ધાળુઓની ભીડ પર ફરી વળી હતી. કહે છે કે ડ્રાઈવર વિસ્તારનો જાણકાર નહોતો એટલે તેણે ગુગલ મેપના સહારે શેરડી ભરેલી ઓવરલોડ ટ્રક ચલાવી હતી. પહેલાં તે પોલીસ બેરીકેડ સાથે ટકરાયા બાદ માર્ગના ઢાળ પર સરકી પડી ને બેકાબુ બની ગઈ હતી.\n"
        "આ વિચિત્ર અકસ્માત પાછળ ખલનાયકની ભૂમિકામાં ગુગલ મેપ હોવાનું કહેવાયું છે. ગુગલ મેપના કારણે અનેક અકસ્માતો થયા છે. મોટા ભાગના વાહનો ગુગલ મેપના આધારે ચાલતા હોય છે. ફોર વ્હીલર, થ્રી વ્હીલર વગેરે કોઈ પણ ખૂણે ગુગલ મેપ મારફતે આસાનીથી ટ્રાવેલ કરી શકે છે.\n"
        "ટ્રાવેલ માટે મળેલું લોકેશન મહત્વનું દિશા સૂચક બની જાય છે. તે ચોક્કસ સ્થળે ચોક્કસ સમયમાં પહોંચાડી દે છે. ગુગલ મેપનો ઉપયોગ મહત્વનો બનવા સાથે બહુ ઉપયોગી પણ બનતો જાય છે. તેનો વપરાશ આસાન હોઈ હવે તે દરેક વ્હીકલનું મહત્વનું અંગ પણ બની ગયું છે.\n"
        "લોકો ગુગલ મેપ પર ભરોસો મુકીને વાહનો હંકારે છે પરંતુ ૨૦૨૪ના વર્ષની એક ઘટનામાં ગુગલ મેપના ભરોસે કાર ચલાવતા ત્રણ યુવાનોની કાર નદીમાં પડી હતી, તેમાં બે તો ડોક્ટર હતા.\n"
        "ગુગલ મેપને ટકરાઈ શકે એવી ભારતની એપનું નામ મેપલ્સ છે."
    ),
    target_lines=38,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2386, 720, 2602,
    text="ગુગલનો પ્રભાવ ઈન્ટરનેટ સિસ્ટમ પર ભરડા સમાન છે. ઈમેલથી માંડીને કોમ્પ્યુટરના ઉપયોગની લગભગ તમામ મહત્વની એપ સાથે ગુગલ જોડાયેલું છે. ભારત ગુગલ બ્રાઉઝરનો વિકલ્પ પણ ઉભું કરી શક્યું નથી કે જી મેલ કે ગુગલ મેપ જેવી સર્વિસ પણ",
    target_lines=7,
    first_indent_pt=0.0,
)
place_png(363, 2609, 779, 2842, "mappls_vs_google.png")
place_exact_body_column(
    414, 2848, 720, 3064,
    text="ઉભું કરી શક્યું નથી.\nવપરાશકારોને કોઈ સ્વદેશી વિકલ્પ મળે તો તે શિફ્ટ થવા તૈયાર છે પરંતુ જીમેલ સહીતની અનેક ફ્રી સર્વિસ સાથે દેશના વપરાશકારો એટલા બધા ટેવાઈ ગયા છે કે તે એક અંગ સમાન બની ગઈ છે.",
    target_lines=7,
    first_indent_pt=0.0,
)
place_png(418, 3071, 719, 3250, "prasangpat_badge.png")
place_exact_body_column(
    414, 3256, 720, 3622,
    text=(
        "એવું પણ નથી કે ભારતે જી-મેલ કે ગુગલ મેપ જેવી સર્વિસનો વિકલ્પ ઉભો કરવા પ્રયાસ નથી કર્યો પરંતુ ગુગલના પ્રભાવ ભર્યા માર્કેટીંગ અને વર્ષો જુના સેટ અપ આગળ સ્વદેશી એપનો વપરાશ કરવા ભાગ્યેજ લોકો તૈયાર થાય છે.\n"
        "ઈન્ટરનેટના પાયામાં ગુગલ છે. જી મેલનો વપરાશ વધ્યો તે પહેલાં હોટ મેલ જેવા અનેક વિકલ્પો હતા પરંતુ ગુગલની ટેકનોલોજીને લોકોએ આવકારી હતી. ગુગલના બ્રાઉઝર ક્રોમના વિકલ્પો પણ અનેક છે છતાં ઈન્ટરનેટ એક્સપ્લોરર"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    746, 2386, 1045, 3622,
    text=(
        "અને ફાયર ફોક્સનો વપરાશ ઓછો જોવા મળે છે.\n"
        "જી મેલની સામે તાજેતરમાં શ્રીધર વામ્બૂની કંપની ઝોહોએ પોતાની ફ્રી ઈમેલ સર્વિસ મુકી હતી પરંતુ તે બહુ ઝળકી શકી નહોતી. ગુગલ મેપની સામે ટક્કર આપી શકે એવી સ્વદેશી મેપ સર્વિસ મેપલ્સ શરૂ કરાઈ છે. ખુદ ઈન્ફોર્મેશન ટેકનોલોજીના કેન્દ્રિય પ્રધાન અશ્વિની વૈશ્નવે કહ્યું હતું કે હું પોતે મેપ્લસનો ઉપયોગ કરું છું.\n"
        "ડિજીટલ મેપીંગના નિષ્ણાતોએ કહ્યું છે કે ભારતના આંતરીયાળ માર્ગો શોધવા મેપીંગ સિસ્ટમ માટે પડકાર સમાન બની જાય છે. ગયા ફેબ્રુઆરી માં સંસદમાં પણ રજૂઆત કરાઈ હતી કે સ્વદેશી મેપીંગ સર્વિસને અમલમાં મુકવા પ્રયાસો કરવા જરૂરી છે. ગુગલ મેપ કાયમ માટે સાચી દિશા નથી આપતું પરંતુ તેનો વપરાશ એટલી હદે વધેલો છે કે કોઈ તેના વિકલ્પનો ઉપયોગ કરવા તૈયાર નથી.\n"
        "ગુગલ મેપે બતાવેલી ખોટી ડીરેક્શનના કારણે અકસ્માતો થયા છે અને લોકોએ જાન પણ ગુમાવ્યા છે. એક ઘટના એવી નોંધાયેલી છે કે બિહારથી ગોવા જઈ રહેલા એક પરિવારે ઝડપથી ગોવા પહોંચાય તેવો રૂટ ગુગલ મેપ પર પસંદ કર્યો હતો. બિચારા કર્ણાટકના જંગલોમાં અટવાઈ ગયા હતા.\n"
        "ભારતમાં રોજ ૫૦ મિલીયન લોકો ગુગલ મેપનો ઉપયોગ કરે છે. ગુગલ મેપના લોચા અવારનવાર ચર્ચામાં આવ્યા છે. ભારત પાસે તેનો વિકલ્પ છે પરંતુ તેનું માર્કેટીંગ નથી કરાતું. જ્યારે આવા કિસ્સા બને ત્યારે ડી-ગુગલીંગની વાતો ઉછળે છે. જેમાં ગુગલની સર્વિસ બંધ કરીને સ્વદેશી એપ વાપરવા ચીપીયો પછાડાય છે પરંતુ સ્વદેશી એપ દેશના લોકોજ વાપરવા તૈયાર નથી."
    ),
    target_lines=38,
    first_indent_pt=0.0,
)
draw_box(96, 3633, 1042, 3784, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    106, 3640, 1032, 3776,
    lines=[
        "ડી-ગુગલીંગની વાતો ઉછળે છે પરંતુ ગુગલનો પ્રભાવ",
        "વધુ છે એટલે આગળ સ્વદેશી એપ વપારતી નથી"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)

# ==============================================================================
# 6. BOJ VINANI MOJ (અક્ષય અંતાણી): કાગડા મળે માંડ માંડ... (COLS 4-7 BOTTOM)
# ==============================================================================
print("Building Boj Vinani Moj (Akshay Antani Humor Column, Cols 4-7 Bottom)...")
draw_box(1070, 2092, 2390, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    1080, 2100, 2380, 2206,
    lines=["કાગડા મળે માંડ માંડ એટલે વધતી જાય ડિમાન્ડ"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1080, 2214, 1385, 3784,
    text=(
        "‘જાત જાતના પક્ષના આ ‘સર્વ-પક્ષી’ અભયારણ્યમાં સતત પક્ષા પક્ષીના વિવાદ જાય પક્ષાંતર કરીને ‘પક્ષ-ઘાત’ થાય અને વિપક્ષી અને સત્તા-ભક્ષી વચ્ચે ચાંચમચાંચ મારવાની ચાંચિયા-ગિરી ચાલે. આમાં કયા પક્ષને વખાણીએ એ જ સમજાતું નથી, શું કહો છો કાકા?’\n"
        "સવાલ સાંભળતાની સાથે જ પથુકાકાએ તડાક કરતો જવાબ આપ્યો કે ‘પક્ષાપક્ષીથી પર એવો એક જ પક્ષ હવે આપણાં દેશમાં રહ્યો છે, એ પક્ષ છે શ્રાદ્ધ-પક્ષ. કારણ કે આ પક્ષના બધા જ માનવંતા મેમ્બરો સ્વર્ગે સીધાવ્યા છે. વર્ષમાં એક જ વાર આ પક્ષનું નામ સંભળાય છે, શ્રાદ્ધપક્ષમાં. અને આપણાં એ પૂર્વજો પણ કેટલાં સમજદાર હોય છે? સ્વર્ગમાંથી ધરતી ઉપર શ્રાદ્ધપક્ષમાં પોતાના પ્રતિનિધિ તરીકે કોને મોકલે છે ખબર છેને? કાગડાને. એટલે કોઈ ટીકા ન કરે કે સ્વર્ગે સીધાવ્યા પછી પણ ‘ખાઈકી’ કરવાનો મોહ નથી છૂટ્યો. બાકી ધરતી પર તો જુદા જુદા પક્ષના ‘પક્ષીઓ’ “ખાઈકી’માટે ટાંપીને જ બેઠાં હોય છે. જય જય રઘુરાઈકી, કભી ન ભૂલે ખાઈકી, ખાને મેં ક્યા શરમ ભાઈકી, જય જય રઘુરાઈકી...’\n"
        "મેં કહ્યું ‘કાકા વિવિધતામાં એકતાના દર્શન હવે તો માત્ર શ્રાદ્ધ-પક્ષમાં જ જોવા મળે છે હો?’\n"
        "કાકાએ પૂછ્યું ‘શ્રાદ્ધપક્ષમાં વળી તને વિવિધતામાં એકતાના દર્શન કેવી રીતે થાય છે?’ મેં કહ્યું કે ‘જીવતી વ્યક્તિ ભલે જુદી જુદી ज्ञाતિની હોય, જુદા જુદા ધર્મની હોય પણ મૃત્યુ પામે પછી બધાં કાગડાના રૂપમાં જ શ્રાદ્ધપક્ષમાં દેખા દે છેને? આને જ કહેવાય વિવિધતામાં એકતા અથવા તો કા... કા... એવો “કાકા-રવ” કરતા કાગડાની કેકતા...’\n"
        "કાકા બોલ્યા ‘એનો અર્થ એવો કે ડાર્વિનદાદાએ કહ્યું હતું કે માણસના પૂર્વજો વાંદરા હતા એ થીયરી ખોટી?’ મેં કહ્યું ‘કાકા વૈજ્ઞાનિક ડાર્વિને વર્ષોના સંશોધન અને અભ્યાસને આધારે એવી થીયરી ઘડી હતી કે માનવના વડવાઓ વાનર હતા. બાકી શ્રાદ્ધપક્ષમાં કાગડાને ખીર-પૂરી ખવડાવવાથી પૂર્વજો તૃપ્ત થાય છે એ શ્રદ્ધાનો વિષય છે.’\n"
        "કાકા બોલ્યા ‘ભાઈ મુંબઈ જેવાં શહેરોમાં કાગડાય ક્યાં નવરા છે ખીર-પૂરી ખાવા? નાનપણમાં આપણે ગાતા કે આવરે કાગડા કઢી પીવા... એમ"
    ),
    target_lines=48,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 2214, 1718, 2496,
    text="મોટપણમાં આપણે ગાવું પડે છે કે આવ રે કાગડા ખીર ખાવા... પણ કાગડા ક્યાં આવે છે? જાણે એપ-આધારિત કેબ બુક કરાવ્યા પછી જેમ રાહ જોઈને ઊભા હોઈએ એવી રીતે કાગડાની રાહ જોઈને ઊભા રહેવું પડે છે. ઘણી વાર કેબવાળા ટ્રીપ કેન્સલ કરે એમ કાગડાય ખીર ખાવા માટે આપણી અગાસીમાં આવવાનું ટાળીને બીજી કોઈ નજીકની અગાસીએ ઉડીને પહોંચી જાય છે. કાગડાની અછત",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2214, 2050, 2496,
    text="કેકારાવ તરીકે વિખ્યાત થયો. હવે કાગડાની ઘટતી જતી આબાદી જોઈને તમે વ્યથિત થઈ ગયા છો એ ભાવના વ્યક્ત કરવા તમે પણ કાગડા ઉપર કવિતાઓ લખી સંગ્રહ તૈયાર કરો અને નામ આપો ‘કાકા-રવ.’ તમને કોલા પીવાની આદત છેને? એટલે આ કાવ્ય-સંગ્રહ ઉપર તમારૂં ઉપનામ શું લખશું ખબર છે? કોલા-પી.",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2504, 1572, 2765,
    text="ઊભી થાય એ કેવી વિચિત્ર સ્થિતિ કહેવાય?’\nપથુકાકા કહે કે આપણાં દેશમાં માણસની વસતી કૂદકે ને ભૂસકે વધતી જાય છે,",
    target_lines=8,
    first_indent_pt=0.0,
)
place_png(1578, 2504, 1884, 2765, "boj_vinani_moj_badge.png")
place_exact_body_column(
    1890, 2504, 2050, 2765,
    text="જવાબ આપ કે કાગડાઓની વસતી ખરેખર ઘટવા માંડી છે કે પછી (મરેલા ઉંદર સહિત બધુ ખાતા) કાગડાઓની ‘મોત-દાર’ યાદીમાંથી એમના",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2772, 1718, 2980,
    text="અને કાગડાની વસતી ઘટતી જાય છે, એટલે પછી શ્રાદ્ધપક્ષ વખતે કાગડાની ખેંચ જ ઊભી થાયને?’\nકાકાની વાતમાં સૂર પૂરાવતા મેં કહ્યું કે કાગડાની આબાદી ઘટતી જાય છે એ હકિકત છે. હમણાં જ છાપામાં સમાચાર વાંચેલા. મુંબઈ જેવાં શહેરોમાં ઝડપથી બંધાતા જતા કોંક્રિટના જંગલો, કપાતા",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2772, 2050, 2980,
    text="નામો ઉડાડી દેવામાં આવ્યા છે?\nખડખડાટ હસીને મેં કહ્યું ‘કાકા તમે કાગડા માટે મોત-દાર યાદી શબ્દ કમાલનો વાપર્યો હો? આપણી મતદાર યાદીમાંથી પણ કરોડો નામો ઉડી ગયા છેને? જ્યારે કાગડા તો પોતે જ ઉડતા હોય છે એટલે એના નામો પણ ઉડતા જ રહેને?’",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2986, 1535, 3282,
    text="જતા વૃક્ષો અને ઘટતી હરિયાળીને કારણે કાગડાને માળા ક્યાં બાંધવા એ સવાલ મૂંઝવે છે. બીજું",
    target_lines=9,
    first_indent_pt=0.0,
)
place_png(1541, 2986, 2046, 3282, "crow_cartoon.png")
place_exact_body_column(
    1412, 3288, 1718, 3784,
    text="શહેરોમાં ખુલ્લા ઉકરડાની જગ્યાએ આધુનિક કચરાપેટીઓ ગોઠવાતી જાય છે. કચરો લઈ જતી ટ્રકો પણ ઉપરથી બંધ હોય છે. એટલે કાગડા બીચારા ખાય શું એ ઉપરાંત મુંબઈ જેવાં શહેરોમાં પ્રદૂષણ વધતું જાય છે. આ બધા કારણોને લીધે કાગડાની વસતી ઘટતી જાય છે.’\nપથુકાકા બોલ્યા એમ વાત છે? કાગડાનું પોપ્યુલેશન ઘટતું જશે તો પ્રોબ્લેમ થશે હો? ગંદકી ઓછી કરવાનું કામ કોણ કરશે? શ્રાદ્ધપક્ષમાં ખીરપૂરી ખાવા કોણ આવશે? એ બધું તો ઠીક પણ રોજ કઠેડા ઉપર બેસીને મને કાકા... કાકા... કાકા... કહી નામથી કોણ બોલાવશે?\nમેં કહ્યું ‘રાજવી કવિ કલાપીએ દિલની વેદના અને ભાવના વ્યક્ત કરતી કવિતનો સંગ્રહ બહાર પાડ્યો હતો જે",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 3288, 2050, 3784,
    text="બાદશાહ અકબરે કિલ્લાની રાંગ ઉપર હારબંધ બેઠેલા કાગડાઓની કાગસેનાને જોઈને બિરબલને પૂછ્યું કે બિરબલ જવાબ આપ કે આપણાં દિલ્હીમાં કાગડાની વસતી કેટલી છે?’ હાજર જવાબી બિરબલે તડાક કરતો જવાબ આપ્યો કે ‘બાદશાહ સલામત... દિલ્હીમાં અત્યારે ૧૧,૧૧,૧૧૧ કાગડા છે.’\nજવાબ સાંભળી બાદશાહ તો આશ્ચર્યચકિત થઈ ગયા. બિરબલની વધુ કસોટી કરવા જહાંપનાહે પૂછ્યું કે તેં આપેલા આંકડા કરતાં કાગડાની સંખ્યા વધુ હશે તો? બિરબલ બોલ્યો કે જો વધુ હશે તો એમ સમજવું કે કાગડાઓને ત્યાં બહારગામથી મહેમાનો આવ્યા હશે અને જો સંખ્યા ઓછી જણાય તો એમ સમજવું કે દિલ્હીના કાગડા સમર વેકેશનમાં ફેમિલી સાથે બહારગામ ફરવા ગયા",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2214, 2380, 3784,
    text=(
        "હશે? બિરબલના જવાબથી ખુશ થયેલા બાદશાહે તેને દસ સોના મહોરનું ઓનલાઈન પેમેન્ટ કરી દીધું.’\n"
        "મેં કહ્યું કાકા તમને ખબર છે? કાગડાની આબાદી ઘટી ગઈ છે એનો લાભ ભાડેથી કાગડા પૂરા પાડનારા ઉઠાવે છે?’\n"
        "નવાઈ પામી કાકા બોલ્યા ‘શું વાત કરે છે? કાગડા કોણ ભાડે આપે છે?’ મેં કહ્યું કાગડા ભાડે આપનારાની શ્રાદ્ધપક્ષમાં ખરી ડિમાન્ડ હોય છે. મહારાષ્ટ્રના કેટલાંક ગામોમાં શ્રાદ્ધપક્ષ વખતે કાગડા ભાડેથી ફેરવવાવાળા ‘રેન્ટ-એ-ક્રો’ કંપનીવાળા સોશ્યલ મિડિયામાં નજરે પડ્યા હતા. એ શું કરે ખબર છે? જંગલમાંથી કાગડા પકડી લ ાવે. પછી એક પગે દોરી બાંધી દે. પછી એક એક ખભા ઉપર બે-બે કાગડા બેસાડીને બૂમ પાડતા નીકળે‘લો કૌઆ ભાડેસે... લો કૌઆ ભાડેસે...’ એ વખતે અગાસીમાં ખીર-પૂરી મૂકીને ઊભા હોય પણ કાગડા ન આવતા હોય એવાં લોકો તરત જ ભાડૂતી કાગડાવાળાને ઉપર બોલાવે છે. પેલો અગાસી કે ધાબા પર જઈને કાગડાને ખીર-પૂરી ખવડાવે છે અને બદલામાં સો-દોઢસો રૂપિયાનું ભાડું વસૂલ કરીને નીકળી જાય છે. બોલો!‘કાગડા ભાડે આપવાનો આ કસદાર સીઝનલ ધંધો કેવો?’\n"
        "ભાડૂતી કાગડાની વાત સાંભળીને પથુકાકા બોલ્યા સાચું બોલજે હો? જૂઠ બોલે કૌઆ કાટે... કાલે કૌએ સે ડરિયો...’ મેં હસીને કહ્યું કાકા તમે બોબી ફિલ્મનું આ ગીત ખરૂં યાદ અપાવ્યું હો?’ કાકા બોલ્યા ‘તને ખબર છે? રાજ કપૂર મેરા નામ જોકર બનાવતા હતા. ખાવાના શોખીન અને મોટા મનના રાજ કપૂર પોતાના આસિસ્ટન્ટ ડિરેક્ટરના ઘરે જમવા ગયા. પૂરી, શાક, દાલ તડકા સહિત કેક વ ાનગી આસિસ્ટન્ટ ડિરેક્ટરના મમ્મીએ પીરસી હતી. રાજ કપૂર ટેસથી ખાતા હતા. એ વખતે મમ્મીજીએ વ્હાલથી કહ્યું બેટા તુમ તો કુછ ખાતે હી નહીં હો... ત્યારે શોમેને કહ્યું મમ્મીજી જૂઠ બોલે કૌઆ કાટે... દેખતે નહીં કિતના સારા ખા લિયા?’ બસ પછી જૂઠ બોલે કૌઆ કાટે... એ મુખડું એમના દિમાગમાં સતત ઘૂમરી લેતું હતું. જ્યારે ‘બોબી’ ફિલ્મ બનાવી ત્યારે તેમણે આ મુખડા પરથી ગીત બનવવાનું ગીતકારને કહ્યું અને આમ મજેદાર ગીત બન્યું જૂઠ બોલે કૌઆ કાટે... કાલે કૌએ સે ડરિયો..."
    ),
    target_lines=48,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. KALPAVRUKSHA: સુવાક્યો (COL 8 BOTTOM)
# ==============================================================================
print("Building Kalpavruksha (Quotes Column, Col 8 Bottom)...")
draw_box(2402, 2092, 2718, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_png(2408, 2096, 2715, 2555, "kalpavruksha_header_photo.png")
place_exact_body_column(
    2410, 2562, 2710, 3784,
    text=(
        "તમામ જ્ઞાન મનુષ્યના મનની અંદર જ રહેલું છે. શિક્ષણ અને અનુભવ માત્ર તે આંતરિક જ્ઞાનને બહાર લાવવાનું (આવરણ હટાવવાનું) કામ કરે છે.\n- સ્વામી વિવેકાનંદ\n*\n"
        "જ્ઞાન માત્ર પુસ્તકિયા માહિતી નથી, પરંતુ ચારિત્ર્યનિર્માણનું સાધન છે. અક્ષરજ્ઞાન કરતાં ‘આત્મજ્ઞાન’ અને ‘નૈતિક મૂલ્યો’ મહત્વના અને સર્વોપરી છે.\n- મહાત્મા ગાંધી\n*\n"
        "તમારી સૌથી મોટી ભૂલ એ છે કે તમે વિચારો છો કે તમારી પાસે સમય છે. જીવન ક્ષણભંગુર છે, તેથી જે કરવાનું છે તે વર્તમાન ક્ષણમાં જ કરી લેવું જોઈએ.\n- ભગવાન બુદ્ધ\n*\n"
        "જ્યારે તમે વર્તમાનમાં સંપૂર્ણ રીતે જીવો છો, ત્યારે સમય અદ્રશ્ય થઈ જાય છે - તે જ સાચું ધ્યાન છે. મન ભૂતકાળ અને ભવિષ્યમાં ભમે છે, પણ જીવન માત્ર ‘અત્યારે’ જ અસ્તિત્વ ધરાવે છે.\n- ઓશો\n*\n"
        "આપણને મળતું જીવન ટૂંકું નથી, પરંતુ આપણે તેનો ઘણો સમય વેડફી નાખીએ છીએ. જો સમયનો યોગ્ય ઉપયોગ કરવામાં આવે તો જીવન ઘણું મોટું અને સાર્થક ભાસે છે.\n- સેનેકા\n*\n"
        "ધૈર્ય અને સમય એ બે સૌથી શક્તિશાળી યોદ્ધાઓ છે. યોગ્ય સમય આવતા બધું જ આપોઆપ ઠીક થઈ જાય છે. બસ, ધીરજ રાખવાની જરૂર હોય છે.\n- લિયો ટોલ્સટોય\n*\n"
        "ગુમાવેલો સમય ક્યારેય પાછો મળતો નથી. જો તમને જીવન વહાલું હોય તો સમય ન વેડફો, કારણ કે જીવન સમયથી જ બનેલું છે.\n- બેન્જામિન ફ્રેન્કલિન"
    ),
    target_lines=38,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. PLACE BOTTOM CMYK BAR
# ==============================================================================
place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_08_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_08_SameToSame.dns"
    png_path = target_dir / "Page_08_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_08_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_08_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
