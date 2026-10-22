from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 10 BUILDER FOR AAS-PAAS (HINDI GUJARAT SAMACHAR)
==============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  across all 7 Business News Stories, 10 Market Price / Stock Tables,
  and 4 Bottom Public Notices on Page 10!
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 10 (100% Same-to-Same Editable Hindi)"
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
        use_font_family = "DB Madhurima"
        use_font_style = "Regular"
    else:
        use_font_family = "DB Hindi"
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
                    "fontFamily": "DB Hindi",
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
            "fontFamily": "DB Hindi",
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
                    "fontFamily": "DB Hindi",
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
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 10 Hindi Running Header...")
build_hindi_running_header(10, draw_box, place_exact_display_lines)

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
        ("(आस-पास प्रतिनिधि)                                        मुंबई, सोमवार", "Regular", "leftJustified", 0.0),
        ("अमेरिका में बॉन्ड यील्ड फिर बढ़ने तथा यूक्रेन के रूस पर महा-ड्रोन हमले को लेकर जियोपॉलिटिकल टेंशन बढ़ने और अंतरराष्ट्रीय बाजार में क्रूड ऑयल के दाम फिर चढ़ने से वैश्विक बाजारों में गिरावट के चलते भारतीय शेयर बाजारों में भी आज भारी कोहराम मच गया। निजी बैंकों के गत सप्ताहांत तिमाही परिणाम कुल मिलाकर उम्मीद से बेहतर आने के बावजूद देश में बढ़ती महंगाई और ऋण की बढ़ती दरों से आगामी दिनों में डिफॉल्टरों की संख्या बढ़ने के खतरे तथा डूबत ऋण (NPA) का आंकड़ा बढ़ने की आशंका से आज निजी बैंक शेयरों में भारी गिरावट आई। हालांकि पीएसयू बैंक शेयरों में आज रिकवरी देखी गई।", "Regular", "leftJustified", 9.0),
        ("आज-मंगलवार को दशहरा के उपलक्ष्य में शेयर बाजार बंद रहेंगे", "Subhead", "center", 0.0),
        ("कैपिटल गुड्स-पावर, हेल्थकेयर, ऑटोमोबाइल, आईटी-सॉफ्टवेयर सर्विसेज, टेक्नोलॉजी शेयरों तथा मेटल-माइनिंग, कंज्यूमर ड्यूरेबल्स, एफएमसीजी शेयरों में बिकवाली का दबाव बढ़ता दिखा। सेंसेक्स ८७६.३७ अंक टूटकर ७३८५२.९० और निफ्टी ५० स्पॉट इंडेक्स २५७.२० अंक लुढ़ककर २२८८८.९५ पर बंद हुए। अमेरिका और भारत के बीच ट्रेड डील की बातचीत सकारात्मक रहने और कुल मिलाकर परिणाम अच्छे आने के बावजूद वैश्विक कारकों के साथ मेगा आईपीओ की तैयारी में लिक्विडिटी की तंगी को लेकर भी आज बाजार में सेलिंग प्रेशर देखा गया। दशहरा के उपलक्ष्य में आज-मंगलवार २० अक्टूबर २०२६ को शेयर बाजार बंद रहेंगे।", "Regular", "leftJustified", 9.0),
        ("कैपिटल गुड्स इंडेक्स ७३४ अंक टूटा : एलजी\nइक्विपमेंट, सुजलॉन, थर्मेक्स, पॉलीकैब टूटे", "Subhead", "center", 0.0),
        ("कैपिटल गुड्स-पावर शेयरों में आज भारी बिकवाली होने से भाव टूट गए। एलजी इक्विपमेंट रु.२७.९० टूटकर रु.५४६.८०, सुजलॉन रु.१.५८ लुढ़ककर रु.४०.३४, आईनॉक्स विंड रु.२.५४ टूटकर रु.६४.८९, थर्मेक्स रु.९१.१५ टूटकर रु.३२३४.९०, पॉलीकैब रु.१९८ टूटकर रु.८०२०, भारत डायनामिक्स रु.२७ घटकर रु.१०८८, किर्लोस्कर इंजन रु.४८.२० टूटकर रु.१९७३.१०, ज्योति सीएनसी रु.२१.६० घटकर रु.९७५.०५, अपार इंडस्ट्रीज रु.३१७.८० घटकर रु.१५,७३३.९०, वारी एनर्जी रु.४१.९० घटकर रु.२५१३.१०, मझगांव डॉक रु.३७ घटकर रु.२०५४, कार्बोरेंडम यूनिवर्सल रु.२१.८० घटकर रु.१०८८.५० रहे। बीएसई कैपिटल गुड्स इंडेक्स ७३३.५२ अंक लुढ़ककर ७२७८९.७१", "Regular", "leftJustified", 9.0),
    ],
    target_lines=32,
    base_pt=10.6,
)

# Sections 2-3 Headline inside top box (746..2050, y=208..424)
place_exact_display_lines(
    746, 208, 2050, 424,
    lines=[
        "निजी बैंक, आईटी, हेल्थकेयर शेयरों में भारी गिरावट",
        ": सेंसेक्स ८७६ अंक लुढ़ककर ७३८५३ पर बंद"
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
        ("पर बंद हुआ।", "Regular", "leftJustified", 0.0),
        ("आईटी शेयरों में फिर बिकवाली : ओरियोनप्रो, ओरम, जेनेसिस\nइंटर., आईजीमो, सारेकन, सोनाटा लुढ़के", "Subhead", "center", 0.0),
        ("आईटी-सॉफ्टवेयर सर्विसेज, टेक्नोलॉजी शेयरों में तेजी थमकर आज फिर फंडों की बिकवाली निकलने से गिरावट आई। केपीआईटी रु.१८.७५ घटकर रु.५३६, सोनाटा सॉफ्टवेयर रु.७.८५ घटकर रु.२४०.०५, एडीएसएल रु.३.३५ घटकर रु.१०३.१५, डेलिवरी रु.१६.९५ घटकर रु.५२७.१५, ईमुद्रा रु.१६.६५ घटकर रु.५३९.४०, टाटा टेक्नोलॉजी रु.१८.०० घटकर रु.७०५.३० रहे। बीएसई आईटी इंडेक्स ४१९.८६ अंक टूटकर २९९७७.१६ पर बंद हुआ।", "Regular", "leftJustified", 9.0),
        ("क्रूड के दाम बढ़ने से ऑटो शेयरों में फंडों की फिर बिकवाली : भारत\nफोर्ज, एक्साइड, टाटा मोटर्स, ह्युंडई घटे", "Subhead", "center", 0.0),
        ("क्रूड ऑयल के अंतरराष्ट्रीय दाम बढ़ने से अब फिर पेट्रोल-डीजल के दामों में संभावित बढ़ोतरी और महंगाई से जनता के त्रस्त होने तथा त्योहारों के सीजन में वाहनों की बुकिंग उम्मीद के अनुरूप न रहने की खबरों के बीच आज फंडों ने ऑटोमोबाइल शेयरों में बिकवाली की। भारत फोर्ज रु.९०.५५ घटकर रु.१७९१.४०, एक्साइड रु.१०.५० घटकर रु.३६०.३५, टाटा मोटर्स पैसेंजर व्हीकल रु.७.५० घटकर रु.२७९.४०, उनो मिंडा रु.२२.७० घटकर रु.१०८७.५०,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Section 3 inside top box (1412..2050, y=428..974)
place_mixed_paras_column(
    1412, 428, 2050, 974,
    paras=[
        ("ह्युंडई मोटर रु.२७.९५ घटकर रु.१९५९.०५, बजाज ऑटो रु.११७ घटकर रु.१०,३००, एमआरएफ रु.९५१.३० घटकर रु.१,२१,८५६.९५ रहे। बीएसई ऑटो इंडेक्स ४१७.९० अंक टूटकर ५६६०६.५७ पर बंद हुआ।", "Regular", "leftJustified", 0.0),
        ("हेल्थकेयर इंडेक्स ५०३ अंक लुढ़का : वन ग्लोबल, थ्रीबी\nब्लैक, सोलारा, फर्मेंटा, थेमिस मेडी घटे", "Subhead", "center", 0.0),
        ("अमेरिका के साथ भारत की ट्रेड डील अंतिम चरण में होने के संकेत के बावजूद हेल्थकेयर क्षेत्र में कोई खास बड़ी डील न होने के अनुमान से आज फंडों ने हेल्थकेयर-फार्मा शेयरों में भारी बिकवाली की। सोलारा रु.४८.८५ घटकर रु.६४७.४५, फर्मेंटा रु.२८.५० घटकर रु.४५९.४०, थेमिस मेडी रु.६.१५ घटकर रु.१००.४०, आरती मेडी रु.४१.३० घटकर रु.८३३.८५ रहे। बीएसई हेल्थकेयर इंडेक्स ५०३.३३ अंक लुढ़ककर ४७७६४.६६ पर बंद हुआ।", "Regular", "leftJustified", 9.0),
        ("निजी बैंकों के अच्छे परिणाम के बावजूद शेयर टूटे : एक्सिस\nरु.५० टूटा : यूनियन बैंक, पीएनबी चढ़े", "Subhead", "center", 0.0),
        ("निजी बैंकों में गत सप्ताहांत एक्सिस बैंक, आईसीआईसीआई बैंक, एचडीएफसी बैंक के उम्मीद से बेहतर परिणाम आने के बावजूद फंडों ने आज निजी बैंक शेयरों में भारी बिकवाली की। हालांकि पीएसयू बैंक शेयरों में चुनिंदा खरीदारी रही। एक्सिस बैंक के अच्छे परिणाम के बावजूद शेयर रु.४९.५५ टूटकर रु.१२३६.९०,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=18,
    base_pt=10.6,
)

# Sections 2-3 Bottom Banner inside top box (746..2050, y=986..1150)
place_exact_display_lines(
    746, 986, 2050, 1150,
    lines=[
        "निफ्टी २५७ अंक लुढ़ककर २२८८९ : निवेशकों की संपत्ति में",
        "रु.४.६९ लाख करोड़ का नुकसान : FII की रु.११४९ करोड़ की बिकवाली"
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
        ("एचडीएफसी बैंक रु.१६.५० घटकर रु.७११.६०, आईसीआईसीआई बैंक रु.१४.८० घटकर रु.१३८२ रहे। पीएसयू बैंक शेयरों में तिमाही परिणाम का आकर्षण रहा। यूनियन बैंक ऑफ इंडिया रु.८.५० बढ़कर रु.१८०.५०, पीएनबी रु.५.५५ बढ़कर रु.१२१.९५, बैंक ऑफ इंडिया रु.४.८५ बढ़कर रु.१३७.१०, बैंक ऑफ बड़ौदा रु.८ बढ़कर रु.२३८, स्टेट बैंक रु.१०.७५ बढ़कर रु.९७२.४५, केनरा बैंक रु.३.४० बढ़कर रु.१२२ रहे। बीएसई बैंकेक्स इंडेक्स २९१.४९ अंक घटकर ६२४७७.९४ पर बंद हुआ।", "Regular", "leftJustified", 0.0),
        ("कंज्यूमर ड्यूरेबल्स शेयरों में बिकवाली : क्रॉम्पटन, अंबर\nएंटर., डिक्सन, वोल्टास, कल्याण ज्वैलर्स घटे", "Subhead", "center", 0.0),
        ("कंज्यूमर ड्यूरेबल्स शेयरों में भी फंडों की आज बिकवाली देखी गई। क्रॉम्पटन रु.८.३० घटकर रु.२०९.९०, अंबर एंटरप्राइजेज रु.१६४.६५ घटकर रु.६५२०.३५, हैवेल्स इंडिया रु.२५.४५ घटकर रु.१०९८.३५, डिक्सन टेक्नोलॉजी रु.२२९ घटकर रु.१२,१००, कल्याण ज्वैलर्स रु.५.५० घटकर रु.५५२, टाइटन रु.३० घटकर रु.४४२० रहे। बीएसई कंज्यूमर ड्यूरेबल्स इंडेक्स ५४५.७१ अंक घटकर ५९९५९.४८ पर बंद हुआ।", "Regular", "leftJustified", 9.0),
        ("FPIs/FII की कैश में रु.११४९ करोड़ की शुद्ध बिकवाली :\nDII की रु.३२०१ करोड़ की शुद्ध खरीदारी", "Subhead", "center", 0.0),
        ("फॉरेन पोर्टफोलियो इन्वेस्टर्स-एफपीआई, एफआईआई ने आज सोमवार को कैश सेगमेंट में रु.११४८.६४ करोड़ के शेयरों की शुद्ध बिकवाली की। कुल रु.११,२४०.६४ करोड़ की खरीदारी के मुकाबले कुल रु.१२,३८९.२८ करोड़ की बिकवाली की। घरेलू संस्थागत निवेशकों-डीआईआई की आज रु.३२०१.१९ करोड़ के शेयरों की शुद्ध खरीदारी रही। कुल रु.१४,७८१.३१ करोड़ की खरीदारी के मुकाबले कुल रु.११,५८०.१२ करोड़ की बिकवाली की।", "Regular", "leftJustified", 9.0),
        ("शेयरों में निवेशकों की संपत्ति-मार्केट कैपिटलाइजेशन रु.४.६९\nलाख करोड़ घटकर रु.४६७.९३ लाख करोड़", "Subhead", "center", 0.0),
        ("शेयरों में व्यापक बिकवाली से निवेशकों की संपत्ति यानी बीएसई में सूचीबद्ध कंपनियों का कुल मार्केट कैपिटलाइजेशन आज एक ही दिन में रु.४.६९ लाख करोड़ घटकर रु.४६७.९३ लाख करोड़ रह गया।", "Regular", "leftJustified", 9.0),
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
# 4. STORY 2 (COLS 1-3, y=1168..1898): FMCG कंपनियों के मार्जिन दबाव में
# ==============================================================================
print("Building Story 2 (FMCG Margins, Cols 1-3)...")
place_exact_display_lines(
    82, 1168, 1051, 1342,
    lines=[
        "FMCG कंपनियों के मार्जिन दबाव",
        "में: दिवाली के बाद दाम बढ़ने की संभावना"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 1348, 556, 1412,
    text="मुंबई, ता. १९\nकच्चे माल के दामों में वृद्धि के परिणामस्वरूप मुनाफे पर दबाव आने के",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    576, 1348, 1051, 1412,
    text="चलते चालू वित्त वर्ष के पिछले छह महीनों में एफएमसीजी क्षेत्र की कंपनियां लगातार मार्जिन दबाव का सामना कर रही हैं।",
    target_lines=2,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1416, 1051, 1462,
    lines=["कच्चे माल में मूल्य वृद्धि से उनकी उत्पादन लागत में इजाफा"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1468, 388, 1898,
    text=(
        "मार्जिन दबाव के बावजूद कंपनियां दिवाली की मांग पर असर न पड़े इसे ध्यान में रखकर फिलहाल दाम बढ़ाने से बच रही हैं और दिवाली के बाद स्थिति में सुधार नहीं आया तो एफएमसीजी उत्पादों में मूल्य वृद्धि होने की संभावना है।\n"
        "जून तिमाही में कमी आने के बाद कच्चे माल की लागत में सितंबर तिमाही में वृद्धि हुई है, जिसके कारण मार्जिन पर दबाव आया है। मार्जिन पर दबाव के बावजूद कंपनियां उपभोक्ता मांग में कमी न आए यह सुनिश्चित करने के लिए मूल्य वृद्धि टाल रही हैं, ऐसा एफएमसीजी"
    ),
    target_lines=15,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 1468, 720, 1898,
    text=(
        "क्षेत्र के एक विश्लेषक ने बताया।\n"
        "एफएमसीजी उत्पादों के उत्पादन में प्रयुक्त कच्चे माल जैसे क्रूड तेल, ऑयल के बाय-प्रोडक्ट्स, पैकेजिंग सामग्री, चीनी तथा खाद्य तेल के दामों में हाल के समय में वृद्धि देखी गई है। कच्चे माल की लागत बढ़ने के कारण एफएमसीजी क्षेत्र की कंपनियों के सितंबर तिमाही के परिणाम कमजोर आने की संभावना से इनकार नहीं किया जा सकता।\n"
        "महंगाई में हो रही वृद्धि एफएमसीजी उद्योग के लिए चिंता का विषय बनी हुई है।\n"
        "तैयार उत्पादों के दाम बढ़ाने के"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 1468, 1051, 1898,
    text=(
        "बजाय कार्यक्षमता बढ़ाकर और कॉस्ट कटिंग के कदमों के माध्यम से कंपनियां कच्चे माल की मूल्य वृद्धि के बोझ को हल्का करने की नीति अपना रही हैं, ऐसा विश्लेषक ने जोड़ा।\n"
        "दिवाली के बाद कृषि कमोडिटीज की कीमतों में वृद्धि होने की संभावना है। कृषि जिंसों के दामों में और वृद्धि से रेडी-टू-ईट जैसे खाद्य पदार्थों के उत्पादकों द्वारा कीमतों में बढ़ोतरी किए जाने की संभावना है। चालू वर्ष में अल नीनो के असर के कारण मानसून कमजोर रहने से कृषि उत्पादों के उत्पादन पर असर पड़ा है।"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. STORY 3 (COLS 1-3, y=1910..2960): दशहरा से पूर्व सोने में दोतरफा उतार-चढ़ाव
# ==============================================================================
print("Building Story 3 (Gold/Crude/Platinum, Cols 1-3)...")
place_exact_display_lines(
    82, 1910, 1051, 2082,
    lines=[
        "दशहरा से पूर्व सोने में दोतरफा उतार-चढ़ाव:",
        "क्रूड में ऊपरी स्तर से गिरावट: प्लैटिनम में तेजी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    82, 2088, 556, 2166,
    text="(वाणिज्य प्रतिनिधि) मुंबई, सोमवार\nमुंबई सर्राफा बाजार में आज सोने-चांदी के भाव ऊंचे खुलने के बाद नीचे बंद हुए। सोने के भाव जीएसटी के बिना",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    576, 2088, 1051, 2166,
    text="९९५ के रु.१४५५०० वाले रु.१४५८२० खुलकर रु.१४५३६० बंद रहे। जबकि ९९९ के भाव रु.१४६१०० वाले रु.१४६४०४ खुलकर रु.१४५९४४ बंद रहे।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 2172, 1051, 2218,
    lines=["विश्व बाजार में सोने के भाव बढ़कर ऊपर में ४२०० डॉलर के करीब"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 2224, 388, 2556,
    text=(
        "मुंबई चांदी के भाव जीएसटी के बिना किलो के रु.२०९५०० वाले रु.२०८७५० बंद रहे। मुंबई सोने-चांदी में जीएसटी सहित भाव हालांकि इन दामों से ३ प्रतिशत ऊंचे रहे। इस बीच मुंबई बाजार में प्लैटिनम के भाव १० ग्राम के रु.५८४८२ वाले आज सुबह रु.५९८८० खुलकर रु.५७०२६ बंद रहे।\n"
        "इस बीच अहमदाबाद सर्राफा बाजार में"
    ),
    target_lines=11,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2224, 720, 2556,
    text=(
        "आज सोने के भाव १० ग्राम के रु.३०० बढ़कर ९९५ के रु.१५०७०० तथा ९९९ के रु.१५१००० रहे। अहमदाबाद चांदी के भाव किलो के रु.२१३००० रहे। विश्व बाजार में आज सोने के भाव प्रति औंस ४१६५ से ४१६६ वाले ऊपर में ४१९० से ४१९१ होकर ४१७५ से ४१७६ डॉलर रहे। सोने के पीछे वैश्विक चांदी के भाव भी औंस के ५६.९९ वाले बढ़कर ऊपर में ५७.८५"
    ),
    target_lines=11,
    first_indent_pt=0.0,
)
place_exact_body_column(
    746, 2224, 1051, 2958,
    text=(
        "होकर ५७.७४ से ५७.७५ डॉलर रहे। प्लैटिनम के भाव १६३५ वाले १६५९ होकर १६५० से १६५१ डॉलर रहे। पैलेडियम के भाव १११६ वाले ऊपर में ११४० होकर ११३८ डॉलर रहे। वैश्विक कॉपर के भाव आज ०.२७ प्रतिशत प्लस में रहे। इस बीच विश्व बाजार में आज क्रूड तेल के भाव बढ़ते थमकर फिर गिरावट पर रहे।\n"
        "ब्रेंट क्रूड के भाव प्रति बैरल जो ऊपर में ११० डॉलर तक पहुंचे थे, वे आज घटकर नीचे में १०६.८२ होकर १०८.६२ डॉलर रहे। यूएस क्रूड के भाव घटकर नीचे में ९९.२४ होकर १०१.३३ डॉलर रहे। नई मांग धीमी थी। भारत में ऑयल इम्पोर्ट बिल सितंबर में १४ प्रतिशत बढ़कर १५.४० अरब डॉलर होने के समाचार थे। पिछले वर्ष सितंबर में यह आंकड़ा १०.५० अरब डॉलर दर्ज हुआ था।\n"
        "देश में सितंबर में क्रूड का आयात ७ प्रतिशत बढ़ा था जबकि इम्पोर्ट बिल में १४ प्रतिशत की वृद्धि हुई थी।"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. STORY 4 (COLS 1-2, y=2568..2958): जून तिमाही के लिए पाकिस्तान की आर्थिक विकास दर दो प्रतिशत रही
# ==============================================================================
print("Building Story 4 (Pakistan GDP Growth, Cols 1-2 Mid-Bot)...")
place_exact_display_lines(
    82, 2568, 720, 2684,
    lines=[
        "जून तिमाही के लिए पाकिस्तान की",
        "आर्थिक विकास दर दो प्रतिशत रही"
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
        "मुंबई, ता. १९\n"
        "चालू वित्त वर्ष के लिए भारत की आर्थिक विकास दर के अनुमान में वैश्विक रेटिंग एजेंसियां बढ़ोतरी कर रही हैं, जबकि पाकिस्तान की आर्थिक विकास दर कमजोर पड़ रही है, ऐसा प्राप्त आंकड़े बताते हैं।\n"
        "२०२६ की जून तिमाही में पाकिस्तान की आर्थिक विकास दर उम्मीद"
    ),
    target_lines=9,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2690, 720, 2958,
    text=(
        "से कम रहकर दो प्रतिशत रही है, जबकि भारत की इस अवधि की जीडीपी उम्मीद से अधिक ७.८० प्रतिशत देखने को मिली है। जून तिमाही के लिए पाकिस्तान का जीडीपी अनुमान ३.५० प्रतिशत रखा गया था।\n"
        "मध्य पूर्व की अशांति ने पाकिस्तान के व्यापार पर असर डाला है, ऐसा स्थानीय सूत्र बता रहे हैं।"
    ),
    target_lines=9,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. STORY 5 (COLS 4-5, y=1168..3030): रुपया फिर संभला + फॉरेक्स भाव + कैश फ्यूचर ऑप्शन + सोना-चांदी बाजार
# ==============================================================================
print("Building Story 5 (Rupee/Euro, Forex Table, Cash Future Option & Gold-Silver Market, Cols 4-5)...")
place_exact_display_lines(
    1078, 1168, 1718, 1310,
    lines=[
        "रुपया फिर संभला: यूरोप में",
        "उपद्रव बढ़ने से यूरो तेजी से टूटा"
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
        "(वाणिज्य प्रतिनिधि) मुंबई, सोमवार\n"
        "मुंबई करेंसी बाजार में आज रुपये के मुकाबले डॉलर के भाव में गिरावट दर्ज की गई। डॉलर के भाव जो शनिवार को बंद बाजार में ऊपर में ८५.०६ तक पहुंचे थे, वे आज सुबह रु. ८४.९९ खुलने के बाद नीचे में रु.८४.७५ तथा ऊपर में रु.८४.९९ होकर रु.८४.९२ बंद रहे।"
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1078, 1464, 1718, 1568,
    lines=[
        "डॉलर इंडेक्स बढ़कर ऊपर में १०२ के पार: भारत में छह",
        "महीने का इम्पोर्ट कवर हो सके उतना फॉरेक्स रिजर्व"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)

# फॉरेक्स भाव Box in Col 4 (1078..1385, y=1575..1818)
draw_box(1078, 1575, 1385, 1818, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
draw_box(1078, 1575, 1385, 1624, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=0.5)
place_exact_display_lines(
    1086, 1580, 1377, 1620,
    lines=["फॉरेक्स भाव"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    1086, 1630, 1210, 1812,
    lines=["डॉलर", "पाउंड", "यूरो", "येन", "ब्रेंट क्रूड"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    1215, 1630, 1378, 1812,
    lines=["रु. ८४.९२", "रु. १२६.५१", "रु. १०६.४०", "रु. ०.६०", "१०८ डॉलर"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
)

place_exact_body_column(
    1078, 1824, 1385, 2396,
    text=(
        "विश्व बाजार में डॉलर के भाव हालांकि यूरोपीय करेंसी के मुकाबले बढ़े थे। यूरोप के विभिन्न शहरों में युवाओं के उपद्रव पर उतरने से विश्व बाजार में यूरोपीय करेंसी यूरो के भाव दबाव में देखे गए। विश्व बाजार में डॉलर का ग्लोबल इंडेक्स आज बढ़ा था। डॉलर का वैश्विक इंडेक्स नीचे में १०१.७७ तथा ऊपर में १०२.०८ रहकर १०१.९३ रहने के समाचार थे।\n"
        "चीन में जारी होने वाले जीडीपी आंकड़ों पर बाजार की नजर रही। इंडोनेशिया की करेंसी के भाव हाल ही में लुढ़ककर एक डॉलर के मुकाबले १९ हजार तक उतर जाने से ३ महीने के निचले स्तर पर पहुंचने की खबर मिली। मुंबई बाजार में रुपये के मुकाबले यूरो के भाव ४६ पैसे लुढ़ककर नीचे में रु.१०६.२१ होकर रु.१०६.४० रहे।"
    ),
    target_lines=20,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1575, 1718, 2396,
    text=(
        "ब्रिटिश पाउंड के भाव नौ पैसे घटकर नीचे में रु.१२६.२६ होकर रु.१२६.५१ रहे। जापान की करेंसी आज रुपये के मुकाबले ०.१७ प्रतिशत घटी। चीन की करेंसी रुपये के मुकाबले ०.०५ प्रतिशत प्लस में रही। मुंबई शेयर बाजार में आज गिरावट तथा विश्व बाजार में क्रूड तेल के दामों में ऊपरी स्तर से गिरावट का असर भी मुंबई करेंसी बाजार में डॉलर तथा रुपये के भाव पर दिखाई दिया।\n"
        "भारत के फॉरेक्स रिजर्व में हाल ही में कमी आने के बाद अब करेंसी बाजार में रिजर्व बैंक की सक्रियता कैसी रहती है, इस पर बाजार के खिलाड़ियों की नजर रही। करेंसी बाजार में सट्टेबाजी के सौदों तथा तत्वों को काबू में रखने के लिए रिजर्व बैंक द्वारा विभिन्न कदम उठाए जा रहे हैं और उसका असर भी करेंसी बाजार में दिखाई दिया।\n"
        "भारत में फिलहाल जो फॉरेक्स रिजर्व है वह लगभग ६ महीने तथा २० दिन के इम्पोर्ट कवर के लिए पर्याप्त है। डॉलर के मुकाबले हाल ही में रुपया भले ही संभला है परंतु आगे चलकर डॉलर के भाव फिर ऊपर जाने तथा शायद रु.१०० को छू लेने की संभावना जानकार जता रहे थे।"
    ),
    target_lines=28,
    first_indent_pt=9.0,
)

# कैश फ्यूचर ऑप्शन Box in Col 4 (1078..1385, y=2410..2958) & Col 5 Top-Bot (1412..1718, y=2410..2639)
draw_box(1078, 2410, 1385, 2488, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1086, 2418, 1377, 2480,
    lines=["कैश फ्यूचर ऑप्शन"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1078, 2494, 1385, 2958,
    paras=[
        ("फ्यूचर मार्केट", "Subhead", "center", 0.0),
        ("- यूनियन बैंक ऑफ इंडिया : (१८१) का अक्टूबर मास का फ्यूचर १८१ के ऊपर १७४ का स्टॉपलॉस रखकर खरीदें। आगामी दिनों में टार्गेट-१ १८६, टार्गेट-२ १८८ तक सुधार की संभावना है।", "Regular", "leftJustified", 9.0),
        ("- अरबिंदो फार्मा : (१६१८) का अक्टूबर मास का फ्यूचर १६१८ के नीचे १६४० का स्टॉपलॉस रखकर बेचें। आगामी दिनों में टार्गेट-१ १५९०, टार्गेट-२ १५६० तक गिरावट की संभावना है।", "Regular", "leftJustified", 9.0),
        ("कैश मार्केट", "Subhead", "center", 0.0),
        ("- गेब्रियल इंडिया : (१४८६) १४८६ के ऊपर १४४५ का स्टॉपलॉस रखकर खरीदें। आगामी दिनों में टार्गेट-१", "Regular", "leftJustified", 9.0),
    ],
    target_lines=16,
    base_pt=9.6,
)
place_mixed_paras_column(
    1412, 2410, 1718, 2639,
    paras=[
        ("१५००, टार्गेट-२ १५३० तक सुधार की संभावना है।", "Regular", "leftJustified", 0.0),
        ("- न्यूलैंड लैबोरेटरीज : (१९२२०) १९२२० के नीचे १९३५० का स्टॉपलॉस रखकर बेचें। आगामी दिनों में टार्गेट-१ १९०००, टार्गेट-२ १८४०० तक गिरावट की संभावना है।", "Regular", "leftJustified", 9.0),
        ("- निलेश कोटक", "Bold", "right", 0.0),
    ],
    target_lines=8,
    base_pt=9.6,
)
draw_line(1412, 2642, 1718, 2642, weight_pt=0.85)

# सोना-चांदी बाजार Box in Col 5 (1412..1718, y=2655..3025)
draw_box(1412, 2655, 1718, 2732, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1420, 2663, 1710, 2724,
    lines=["सोना-चांदी बाजार"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1412, 2738, 1558, 3025,
    paras=[
        ("अहमदाबाद", "Subhead", "center", 0.0),
        ("चांदी चौरसा २१००००-२१३०००\nचांदी रूपा २०९८००-२१२८००\nचांदी सिक्का पुराना २४००-२७००\nसोना (९९.९) १४९०००-१५१०००\nसोना (९९.५) १४८७००-१५०७००\nहॉलमार्क १४७९८०", "Regular", "left", 0.0),
        ("मुंबई", "Subhead", "center", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)
place_mixed_paras_column(
    1566, 2738, 1718, 3025,
    paras=[
        ("चांदी २०८७५०\nसोना (९९.५) १४५३६०\nसोना (९९.९) १४५९४४", "Regular", "left", 0.0),
        ("राजकोट", "Subhead", "center", 0.0),
        ("चांदी २१२०००\n२४ कैरेट १० ग्राम १५२५००\nसिक्का (१ ग्राम) १५३००\n२२ कैरेट १० ग्राम १३९५००", "Regular", "left", 0.0),
    ],
    target_lines=14,
    base_pt=8.4,
)

# ==============================================================================
# 8. STORY 6 (COLS 6-8, y=1168..1862): क्रिसमस तथा नए साल के लिए अमेरिका से गारमेंट्स के ऑर्डर में कमी
# ==============================================================================
print("Building Story 6 (US/EU Garment Orders, Cols 6-8)...")
place_exact_display_lines(
    1744, 1168, 2712, 1342,
    lines=[
        "क्रिसमस तथा नए साल के लिए अमेरिका",
        "से गारमेंट्स के ऑर्डर में कमी आई"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
    lead_ratio=0.90,
)
place_exact_body_column(
    1744, 1348, 2218, 1438,
    text="मुंबई, ता. १९\nआगामी क्रिसमस तथा नए साल के लिए अमेरिका से रेडीमेड गारमेंट्स के भारतीय निर्यातकों को मिलने वाले ऑर्डर में",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 1348, 2712, 1438,
    text="कमी आई है परंतु यूनाइटेड किंगडम (यूके) तथा यूरोप से मांग अच्छी रहने से देश के गारमेंट उद्योग के लिए स्थिति राहत भरी बनी है।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1444, 2712, 1492,
    lines=["यूके तथा यूरोप से मांग अच्छी रहने से निर्यातकों को राहत"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1498, 2050, 1862,
    text=(
        "भू-राजनीतिक अनिश्चितता के बीच अमेरिका में ऊंची महंगाई के कारण खरीदार सतर्कता का रुख अपना रहे हैं।\n"
        "अमेरिकी बाजार में कमजोरी के कारण भारत के अपैरल निर्यातकों के लिए चालू वित्त वर्ष के प्रथम छह महीने डॉलर की दृष्टि से कमजोर रहे हैं, ऐसा अपैरल एक्सपोर्ट प्रमोशन काउंसिल के सूत्रों ने बताया।\n"
        "सितंबर में रेडीमेड गारमेंट का निर्यात १.१० अरब डॉलर रहा था जो"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 1498, 2382, 1862,
    text=(
        "वार्षिक आधार पर १३.७० प्रतिशत वृद्धि दर्शाता है, परंतु अप्रैल से सितंबर की अवधि का कुल निर्यात ६.२० प्रतिशत घटकर ७.२० अरब डॉलर रहा है, ऐसा सूत्रों ने जोड़ा। पिछले वर्ष की समान अवधि में यह आंकड़ा ७.७० अरब डॉलर रहा था।\n"
        "रुपये की दृष्टि से सितंबर में निर्यात वार्षिक आधार पर २२.९० प्रतिशत बढ़कर १०८२४.६० करोड़ रुपये रहा था। चालू वित्त वर्ष के प्रथम छह महीनों में रुपये की दृष्टि से गारमेंट निर्यात ३.४० प्रतिशत बढ़कर ६९३०० करोड़ रुपये रहा है।"
    ),
    target_lines=12,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1498, 2712, 1862,
    text=(
        "आगामी क्रिसमस तथा नए साल के लिए अमेरिका से गारमेंट के ऑर्डर में २५-३० प्रतिशत की कमी देखने को मिली है, ऐसा तिरुपुर के निर्यातक दावा कर रहे हैं।\n"
        "हालांकि यूरोप तथा यूके से ऑर्डर संतोषजनक रहे हैं और भू-राजनीतिक तनाव के परिणामस्वरूप जहाजों की आवाजाही पर पड़े असर को ध्यान में रखकर निर्यातकों ने सामान्य से पहले माल रवाना किया है ताकि वह समय पर पहुंच जाए।"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)

# ==============================================================================
# 9. STORY 7 (COLS 6-8, y=1874..3255): खाद्य तेलों में मिश्रित रुख + MARKET TABLES
# ==============================================================================
print("Building Story 7 (Edible Oil Market & Market/Stock Tables, Cols 6-8)...")
place_exact_display_lines(
    1744, 1874, 2712, 2050,
    lines=[
        "खाद्य तेलों में मिश्रित रुख: दशहरा से पूर्व",
        "मांग बढ़ी: अरंडी तेल तथा अरंडी में तेजी जारी"
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
        "(वाणिज्य प्रतिनिधि)\n"
        "मुंबई, सोमवार\n"
        "मुंबई तेल-तिलहन बाजार में आज विभिन्न देसी तथा आयातित खाद्य तेलों के भाव दोतरफा सीमित उतार-चढ़ाव के बीच टिके रहे। इस बीच अरंडी तेल (दीवेल) तथा हाजिर अरंडी में रिकॉर्ड तेजी आगे बढ़ी। त्योहारों तथा दशहरा से पूर्व बाजार में आज मौसमी मांग बनी रही। विश्व बाजार में आज मलेशिया में पाम तेल वायदा के भाव नवंबर के २२ अंक तथा दिसंबर के १० अंक नरम रहे। विश्व बाजार में क्रूड तेल के भाव ऊपरी स्तर से घटने पर वैश्विक खाद्य तेलों के दामों पर उसका असर दिखाई दिया। मुंबई हाजिर बाजार में अरंडी तेल के भाव १०"
    ),
    target_lines=17,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 2056, 2382, 2155,
    text=(
        "किलो पीछे और रु.१८ उछलने से हाजिर अरंडी के भाव प्रति क्विंटल रु.८४२० वाले रु.८५१५ बोले जाने लगे। सौराष्ट्र"
    ),
    target_lines=3,
    first_indent_pt=0.0,
)

# पाम तेल वायदा में बनी नरमी Red Callout Box in Col 7 (2076..2382, y=2161..2270)
draw_box(2076, 2161, 2382, 2270, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    2086, 2168, 2372, 2262,
    lines=[
        "पाम तेल वायदा में",
        "बनी हुई नरमी"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)

place_exact_body_column(
    2076, 2276, 2382, 2442,
    text=(
        "में मूंगफली तेल के भाव रु.१७७५ से १८०० तथा कॉटन वॉश के भाव रु.१५१० से १५१५ रहने के निर्देश थे।\n"
        "सौराष्ट्र में मूंगफली के भाव २० किलो के किस्मवार रु.१४०० से १७००"
    ),
    target_lines=5,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2056, 2712, 2442,
    text=(
        "रहे। इस बीच मुंबई हाजिर बाजार में आज १० किलो के भाव मूंगफली तेल के रु.१८३० जबकि बिनौला तेल के भाव रु.१५९५ रहे। मुंबई आयातित पाम तेल के भाव रु.१४४५ तथा सोया तेल के भाव रु.१४७० तथा सनफ्लावर के भाव रु.१५८५ तथा रिफाइंड के भाव रु.१६८० बोले जा रहे थे। सौराष्ट्र में देर शाम मूंगफली तेल के भाव रु.१७७५ से १८०० तथा कॉटन वॉश के भाव रु.१५१५ और पाम तेल के भाव रु.१४०२ रहे।"
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# राजकोट अंतिम भाव & चिमनभाई मार्केट in Col 6 (1744..2050, y=2562..3025)
draw_line(1744, 2562, 2050, 2562, weight_pt=0.85)
draw_box(1744, 2580, 2050, 2656, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2588, 2042, 2648,
    lines=["राजकोट अंतिम भाव"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1744, 2662, 2050, 2786,
    text=(
        "राजकोट मूंगफली तेल लूज १८००\n"
        "राजकोट मूंगफली १७८०-१७९०\n"
        "सोना २४ कैरेट १५२५००\n"
        "१ किलो चांदी २१२०००"
    ),
    target_lines=4,
    align="left",
    first_indent_pt=0.0,
)
draw_box(1744, 2795, 2050, 2869, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    1752, 2803, 2042, 2861,
    lines=["चिमनभाई मार्केट"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    1744, 2875, 2050, 3025,
    paras=[
        ("२० किलो", "Subhead", "center", 0.0),
        ("आलू देसी १००-२००\nआलू डीसा २४०-३२०\nप्याज महाराष्ट्र ७००-१०४०\nप्याज एमपी ७००-८४०", "Regular", "left", 0.0),
    ],
    target_lines=5,
    base_pt=9.6,
)

# अहमदाबाद के बाजार in Col 7 (2076..2382, y=2448..2796)
draw_line(2076, 2448, 2712, 2448, weight_pt=0.85)
draw_box(2076, 2464, 2382, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2472, 2374, 2531,
    lines=["अहमदाबाद के बाजार"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_mixed_paras_column(
    2076, 2545, 2224, 2796,
    paras=[
        ("तेल-तिलहन", "Subhead", "left", 0.0),
        ("मूंगफली तेल नया डिब्बा (१५ किलो) २९५०-३१५०\nमूंगफली तेल नया डिब्बा (१५ लीटर) २९५०\nबिनौला तेल नया डिब्बा (१५ किलो) २५८०-२७८०\nराइस ब्रान (१५ किलो) २५५०\nसोयाबीन नया डिब्बा २६००", "Regular", "left", 0.0),
    ],
    target_lines=12,
    base_pt=8.4,
)
place_exact_body_column(
    2232, 2545, 2382, 2796,
    text=(
        "अरंडी तेल २४००\n"
        "पामोलिन पुराना डिब्बा २३३०\n"
        "पामोलिन नया डिब्बा २४५०\n"
        "नारियल तेल ४४००\n"
        "वनस्पति २०००-२३००\n"
        "मीठा सरसों २९००\n"
        "तीखा सरसों ३०५०\n"
        "सनफ्लावर २६५०\n"
        "मक्का तेल २४५०"
    ),
    target_lines=11,
    align="left",
    first_indent_pt=0.0,
)

# अंतिम भाव in Col 8 (2408..2712, y=2464..2796)
draw_box(2408, 2464, 2712, 2539, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2472, 2704, 2531,
    lines=["अंतिम भाव"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2408, 2545, 2712, 2796,
    text=(
        "मुंबई चांदी २०८७५०\n"
        "मुंबई सोना (९९.५) १४५३६०\n"
        "मुंबई सोना (९९.९) १४५९४४\n"
        "अहम. चांदी २१३०००\n"
        "अहम. सोना (९९.९) १५१०००\n"
        "अहम. सोना (९९.५) १५०७००\n"
        "अहम. मूंगफली तेल नया ३१५०\n"
        "अहम. बिनौला नया २७८०"
    ),
    target_lines=8,
    align="left",
    first_indent_pt=0.0,
)

# NSE सर्वाधिक गिरे (Col 7, 2076..2382, y=2805..3255) & BSE सर्वाधिक गिरे (Col 8, 2408..2712, y=2805..3255)
draw_box(2076, 2805, 2382, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2084, 2813, 2374, 2872,
    lines=["NSE सर्वाधिक गिरे"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2076, 2886, 2195, 2916, lines=["कंपनी"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2196, 2886, 2305, 2916, lines=["बंद भाव"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2306, 2886, 2382, 2944, lines=["गिरावट", "(% में)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2076, 2948, 2382, 2948, weight_pt=0.75)
place_exact_display_lines(
    2076, 2954, 2210, 3254,
    lines=[
        "एक्सिस बैंक",
        "टाटा मोटर्स पैसे.",
        "इंफोसिस",
        "बजाज फाय.",
        "अपोलो हॉस्पि.",
        "अल्ट्राटेक",
        "HDFC बैंक",
        "ट्रेंट",
        "हिंद लीवर",
        "NTPC",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2212, 2954, 2318, 3254,
    lines=[
        "१२३६.००",
        "२७८.००",
        "११३०.७०",
        "९५७.३५",
        "७७००.००",
        "१०६५०.००",
        "७१२.००",
        "२८९१.६०",
        "१८५३.२०",
        "३०९.००",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2322, 2954, 2382, 3254,
    lines=[
        "४.१९",
        "३.०९",
        "२.६३",
        "२.५२",
        "२.४१",
        "२.३६",
        "२.३१",
        "२.२७",
        "२.१४",
        "१.९५",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

draw_box(2408, 2805, 2712, 2880, stroke_swatch="GsRedBanner", stroke_weight_pt=1.5)
place_exact_display_lines(
    2416, 2813, 2704, 2872,
    lines=["BSE सर्वाधिक गिरे"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(2408, 2886, 2525, 2916, lines=["कंपनी"], font_style="Bold", align="left", stretch_lines=False)
place_exact_display_lines(2526, 2886, 2635, 2916, lines=["बंद भाव"], font_style="Bold", align="right", stretch_lines=False)
place_exact_display_lines(2636, 2886, 2712, 2944, lines=["गिरावट", "(% में)"], font_style="Bold", align="right", stretch_lines=False)
draw_line(2408, 2948, 2712, 2948, weight_pt=0.75)
place_exact_display_lines(
    2408, 2954, 2542, 3254,
    lines=[
        "एक्सिस बैंक",
        "अल्ट्राटेक",
        "इंफोसिस",
        "बजाज फाय.",
        "ट्रेंट",
        "NTPC",
        "HDFC बैंक",
        "हिंद लीवर",
        "बजाज फिन.",
        "भारती एयरटेल",
    ],
    font_style="Regular",
    align="left",
    stretch_lines=False,
)
place_exact_display_lines(
    2544, 2954, 2650, 3254,
    lines=[
        "१२३६.९०",
        "१०६२०.१०",
        "११३०.००",
        "९५७.००",
        "२८८६.००",
        "३०९.००",
        "७११.६०",
        "१८५६.९५",
        "१७०२.७५",
        "१८७२.७५",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)
place_exact_display_lines(
    2654, 2954, 2712, 3254,
    lines=[
        "३.८५",
        "२.८२",
        "२.७२",
        "२.५४",
        "२.४३",
        "२.३७",
        "२.२७",
        "२.१६",
        "१.९७",
        "१.६९",
    ],
    font_style="Regular",
    align="right",
    stretch_lines=False,
)

# ==============================================================================
# 10. BOTTOM PUBLIC NOTICES (सार्वजनिक सूचना) — 100% EDITABLE HINDI TEXT & CMYK BAR
# ==============================================================================
print("Building Page 10 Bottom Public Notices (100% Editable Hindi Text)...")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=52):
    x_mid = (x1_px + x2_px) // 2
    draw_box(x1_px, y1_px, x2_px, y2_px, stroke_swatch="[Black]", stroke_weight_pt=1.8)
    draw_box(x1_px, y1_px, x_mid - 4, y1_px + header_h, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
    place_exact_display_lines(
        x1_px + 10, y1_px + 6, x_mid - 14, y1_px + header_h - 4,
        lines=["सार्वजनिक सूचना"],
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
        "मौजे शिवपुरा\n"
        "डिस्ट्रिक्ट अहमदाबाद, तालुका विरमगाम के मौजे गांव शिवपुरा की सीम के खाता नंबर ३४१ के ब्लॉक/सर्वे नंबर १०४ (पुराना सर्वे नंबर ७८) की कुल १-०८-२५ हे.आरे.चो.मी. यानी १०८२५ वर्ग मीटर वाली कृषि भूमि (१) भगवानभाई हंसराजभाई (२) जगजीवनभाई हंसराजभाई (३) मीनाबेन पत्नी भवानभाई (४) किन्नरीबेन पुत्री भवानभाई एवं पत्नी अमितकुमार (५) जिग्नेशकुमार भवानभाई पटेल तथा (६) आनंदकुमार जगजीवनभाई पटेल के संयुक्त स्वामित्व और प्रत्यक्ष कब्जे-भोगवटे की तथा उनके स्वयं के काश्तकारी हक की और सभी प्रकार के कानूनी विवादों एवं बोझ से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है। अतः उक्त भूमि या उसके किसी भी भाग पर अन्य किसी का किसी भी प्रकार का हक, हिस्सा, काश्तकारी हक, बोझ, रास्ते का हक, बानाखत का हक,"
    ),
    right_text=(
        "चार्ज, गणोत हक, ईजमेंट राइट्स या अन्य किसी भी प्रकार का लागभाग, कब्जा-हक, हित, हिस्सा, दावा, विवाद आदि कुछ भी हो तो वे उसकी लिखित सूचना, संबंधित लिखित सबूत की प्रमाणित प्रतियों सहित स्पीड पोस्ट, ए.डी. पोस्ट द्वारा इस नोटिस के प्रसिद्ध होने से दिन-१५ (पंद्रह) में हमें नीचे दिए पते पर करें और यदि ऐसा नहीं किया गया तो उक्त भूमि पर अन्य किसी का किसी भी प्रकार का हक, हिस्सा, बोझ, रास्ते या बानाखत का हक या कोई भी दावा आदि नहीं है और यदि हो तो वह त्याग यानी वेव किया गया समझकर मियाद समाप्त होने पर टाइटल संबंधी अभिप्राय का सर्टिफिकेट जारी कर देंगे और उसके बाद किसी की कोई आपत्ति नहीं चलेगी।\n"
        "अहमदाबाद\n"
        "तारीख : २०/१०/२०२६\n"
        "जैमिन रोहितभाई पटेल, एडवोकेट\n"
        "३१३५, तीसरी मंजिल, टी.आर.पी. मॉल, ईस्ट कोर्ट, बोपल, अहमदाबाद-३८००५८।\n"
        "मो. नं. ९९७८९ ३२१९९"
    ),
    left_lines=24,
    right_lines=26,
)

# 2. Cols 3-4 Bottom Notice (746..1385, 2970..3790)
place_public_notice_2col(
    746, 2970, 1385, 3790,
    left_text=(
        "मौजे: वावोल\n"
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट गांधीनगर, सब-डिस्ट्रिक्ट कलोल, तालुका कलोल के मौजे गांव : वावोल की सीम के खाता नंबर: १३०० के ब्लॉक/सर्वे नंबर: ७५८/००४ (पुराने सर्वे नंबर: १९१) की हे.आरे.चो.मी. ०-५९-४५ आकार: ६.०८ की पुरानी शर्त की कृषि भूमि उत्पलभाई जगदीशभाई अमीन निवासी ए/५०१, समस्त अपार्टमेंट, अर्पण मानव मंडल के पीछे, वस्त्रापुर, अहमदाबाद-३८००१५ के स्वतंत्र स्वामित्व और कब्जे-भोगवटे की तथा सभी प्रकार के बोझ से मुक्त होने का बताकर हमारे मुवक्किल को गैर-कृषि करवा कर देने की शर्त पर बेचने का तय किया है और हमसे उक्त संपत्ति के टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। तो उक्त संपत्ति पर किसी का किसी भी प्रकार का लागभाग, हक-हिस्सा, दावा, हित-संबंध, बानाखत, ईजमेंट, राइट्स या गारंटी तथा"
    ),
    right_text=(
        "भरण-पोषण के हक या किसी भी व्यक्ति, बैंक, फर्म या संस्था का बोझ या दावा हो तो इस नोटिस के प्रसिद्ध होने से दिन-७ (सात) में सभी सबूतों की प्रमाणित प्रति सहित लिखित सूचना रजि. ए.डी. से नीचे दिए पते पर करें। यदि मियाद में सूचना नहीं दी गई तो उपरोक्त दर्शित संपत्ति पर किसी का किसी भी प्रकार का लागभाग, बोझ, हक-हिस्सा, हित-संबंध या भरण-पोषण का हक या दावा नहीं है और यदि हो तो वे सभी स्वेच्छा से त्याग (वेव) दिए हैं, ऐसा समझकर मियाद समाप्त होने पर हमारे मुवक्किल को उपरोक्त संपत्ति का टाइटल क्लीयरेंस सर्टिफिकेट दिया जाएगा।\n"
        "तारीख: १९/१०/२०२६\n"
        "हेमराज आर. देसाई (एडवोकेट)\n"
        "(८३४७२ ६३२५३)\n"
        "एफ.एफ.-८, सेंटर प्लाजा, सार्थक चार रास्ता, सोला रोड, घाटलोडिया, अहमदाबाद-३८००६१"
    ),
    left_lines=24,
    right_lines=26,
)

# 3. Cols 5-6 Bottom Notice (1412..2050, 3036..3790)
place_public_notice_2col(
    1412, 3036, 2050, 3790,
    left_text=(
        "डिस्ट्रिक्ट सब-डिस्ट्रिक्ट अहमदाबाद-१४ (वस्त्राल) के तालुका दस्क्रोई के मौजे गांव झाणु की सीम के खाता नं. १६८ के रे. सर्वे नं. १३१८ (पुराने ब्लॉक/सर्वे नं.-४७७/पैकी) की हे.आरे.चो.मी. १-०६-७३ आकार रु. २.०४ पैसे वाली पुरानी शर्त की कृषि योग्य भूमि तथा रे. सर्वे नं.-१३१७ (पुराने ब्लॉक/सर्वे नं.-४७७) की हे.आरे.चो.मी. ०-०१-२४ आकार रु. ०.०६ पैसे वाली पुरानी शर्त की कृषि योग्य भूमि मिलाकर कुल हे.आरे.चो.मी. १-०७-९७ पुरानी शर्त की कृषि योग्य भूमि (१) कांतिभाई मूलजीभाई (२) परषोत्तमभाई उर्फ प्रितेशभाई मूलजीभाई के नाम संयुक्त स्वामित्व, कब्जे-भोगवटे में दर्ज है तथा सभी प्रकार के बोझों से मुक्त होने का बताकर उक्त भूमि हमारे मुवक्किल को बेचने का तय किया है, हमारे मुवक्किल ने हमसे उक्त भूमि के टाइटल क्लीयर और मार्केटेबल होने के"
    ),
    right_text=(
        "अभिप्राय संबंधी सर्टिफिकेट की मांग की है। तो उक्त भूमि में किसी का बानाखत, विक्रय, बख्शीस, पावर, विरासत, हित, गिरवी या कब्जा हक आदि अथवा किसी कोर्ट का स्थगन आदेश चालू हो तो उसकी सूचना लिखित में दस्तावेजी सबूत सहित इस नोटिस के प्रसिद्ध होने से दिवस-१५ (पंद्रह) में नीचे दिए पते पर रजि. पोस्ट से करें (कानून द्वारा मान्य सबूत के बिना भेजे गए आपत्ति आवेदन को ध्यान में लिए बिना सीधे दफ्तर दाखिल किया जाएगा।) उक्त समयसीमा बीतने के बाद आने वाली आपत्ति या दावे पर ध्यान दिए बिना उक्त भूमि का टाइटल क्लीयर सर्टिफिकेट जारी किया जाएगा।\n"
        "19 OCT 2026\n"
        "निलेशकुमार बी. पटेल\n"
        "(एडवोकेट एंड नोटरी)\n"
        "ऑफिस-ए/१, (ग्रा. फ्लोर) मूर्तिधाम पार्क, रसपान चार रास्ता के पास, निकोल, अहमदाबाद-३८२३५०\n"
        "मो.नं.- ७८७४३७४४६६"
    ),
    left_lines=22,
    right_lines=24,
)

# 4. Cols 7-8 Bottom Notice (2076..2712, 3266..3790)
place_public_notice_2col(
    2076, 3266, 2712, 3790,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद, सब-डिस्ट्रिक्ट धोलका के धोलका तालुका के मौजे सरोडा गांव की सीम के ब्लॉक/सर्वे नं. ३२१ की कुल १८२११ वर्ग मीटर (जिसमें ७०८ वर्ग मीटर पोत खराबा सहित) में से अविभाजित हमारे हिस्से की ५९४५ वर्ग मीटर पु.श. की कृषि भूमि, शंकरभाई भीमाभाई मकवाणा द्वारा अपने स्वतंत्र स्वामित्व और प्रत्यक्ष कब्जे-भोगवटे में होने का बताकर हमारे मुवक्किल को बेचने का तय किया है और हमारे मुवक्किल ने उपरोक्त भूमि संबंधी हमसे टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। अतः"
    ),
    right_text=(
        "सभी व्यक्ति जो उपरोक्त भूमि पर किसी भी प्रकार का हक, हित, हिस्सा, बोझ, बानाखत के हक इत्यादि रखते हों तो उन्हें इस सार्वजनिक सूचना के प्रसिद्ध होने से दिन-७ (सात) के भीतर दस्तावेजी सबूत सहित लिखित में नीचे दिए पते पर सूचित करना होगा, और यदि ऐसा करने में चूक या विलंब हुआ तो उपरोक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा, कृपया ध्यान दें।\n"
        "अहमदाबाद\n"
        "ता. २०-१०-२०२६\n"
        "अमित वी. पटेल, एडवोकेट\n"
        "९३, नालंदा कॉम्प्लेक्स, वस्त्रापुर, अहमदाबाद-३८००१५।\n"
        "मो. : ९५१०१८८५०५."
    ),
    left_lines=16,
    right_lines=18,
)

place_png(0, 3796, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_10_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_10_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_10_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_10_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_10_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
