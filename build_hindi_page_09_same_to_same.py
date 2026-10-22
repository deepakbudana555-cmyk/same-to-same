from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 9 BUILDER FOR AAS-PAAS (HINDI GUJARAT SAMACHAR)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  across all Page 9 National/International Stories, Page 1 Continuations,
  and 8 Bottom Public Notices (सार्वजनिक सूचना)!
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 09 (100% Same-to-Same Editable Hindi)"
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
# 1. RUNNING HEADER & VERTICAL GRID DIVIDERS
# ==============================================================================
print("Placing Page 9 Hindi Running Header & Dividers...")
build_hindi_running_header(9, draw_box, place_exact_display_lines)

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
# 2. COLS 1-3: दिल्ली की बात (प्रथम पृष्ठ का शेष) + OTHER CONTINUATIONS
# ==============================================================================
print("Building Page 1 Continuations in Cols 1-3...")

place_mixed_paras_column(
    82, 200, 388, 2288,
    paras=[
        ("दिल्ली की बात", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("रखते हुए आरोप लगाया था कि कुछ नेता और भारत विरोधी तत्व मिलकर देश में हिंसा फैलाने के लिए युवाओं को भड़का रहे हैं।", "Regular", "leftJustified", 0.0),
        ("तिहाड़ जेल में सीजेपी नेता हाई सिक्योरिटी वार्ड में", "Subhead", "center", 0.0),
        ("बिना अनुमति जंतर-मंतर में प्रवेश करने की कोशिश करने वाले क्रोधरॉय जनता पार्टी के आशुतोष रांका और सौरव दास को दिल्ली की तिहाड़ जेल में हाई सिक्योरिटी वार्ड में रखा गया है। जेल अधिकारियों ने उनकी कोठरी के बाहर अतिरिक्त सुरक्षाकर्मी तैनात किए हैं तथा दिन के समय दूसरे कैदियों के साथ बाहर निकलकर मिलने न पाएं, इसका भी ध्यान रखा गया है। जेल रिकॉर्ड के अनुसार रांका का कैदी नंबर १७८४ और दास का कैदी नंबर ३७५२ है। शुरुआत में दोनों को जेल नंबर २ में रखा गया था, परंतु बाद में रांका को जेल नंबर ४ में स्थानांतरित कर दिया गया। जेल परिसर के अन्य ब्लॉकों की तुलना में इन दोनों को जहां रखा गया है वहां कैदियों की संख्या कम है। चौबीसों घंटे उन पर नजर रखी जाती है।", "Regular", "leftJustified", 9.0),
        ("‘२०२३ के चुनाव आयोग कानून का समर्थन कर गलती की’", "Subhead", "center", 0.0),
        ("वाईएसआरसीपी के प्रमुख और आंध्र प्रदेश के पूर्व मुख्यमंत्री वाईएस जगन मोहन रेड्डी ने स्वीकार किया है कि मुख्य चुनाव आयुक्त और अन्य चुनाव आयुक्तों की नियुक्ति को लेकर २०२३ में बनाए गए कानून का समर्थन कर उन्होंने गलती की थी। निष्पक्ष चुनाव प्रक्रिया के लिए उन्होंने सुधार करने की मांग की है। रेड्डी का कहना है कि चुनाव कराने की जिम्मेदारी जिन पर है, उन्हें चुनने का अधिकार सत्तारूढ़ दल के पास नहीं होना चाहिए। पहले की पद्धति में चुनाव आयुक्त नियुक्त करने का अधिकार प्रधानमंत्री, नेता प्रतिपक्ष और भारत के मुख्य न्यायाधीश को दिया जाता था। परीक्षक की नियुक्ति विद्यार्थी द्वारा नहीं हो सकती। यदि किसी निष्पक्ष संस्था द्वारा चुनाव आयुक्तों की नियुक्ति नहीं होगी तो चुनाव आयोग को आलोचना का सामना करना पड़ सकता है।", "Regular", "leftJustified", 9.0),
        ("लखनऊ में उलटी गंगा, एबीवीपी का ज्ञानेश कुमार के समर्थन में प्रदर्शन", "Subhead", "center", 0.0),
        ("सीईसी ज्ञानेश कुमार के इस्तीफे के लिए दिल्ली सहित पूरे देश में प्रदर्शन हो रहे हैं। हालांकि अब भाजपा की छात्र इकाई अखिल भारतीय विद्यार्थी परिषद (एबीवीपी) ने लखनऊ में ज्ञानेश कुमार के समर्थन में प्रदर्शन किया है।", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

place_mixed_paras_column(
    414, 200, 720, 2288,
    paras=[
        ("लोकतंत्र कमजोर पड़ता है। एबीवीपी ने ‘अराजकता रोको, लोकतंत्र अपनाओ’ अभियान के तहत ‘छात्र हुंकार’ विरोध प्रदर्शन का आयोजन किया है। लखनऊ विश्वविद्यालय के गेट नंबर ३ के पास एबीवीपी के सैकड़ों कार्यकर्ता एकत्रित हुए और उन्होंने नारे लगाए। उन्होंने कांग्रेस पार्टी मुर्दाबाद के नारे लगाते हुए अभिषेक दीपक और ध्रुव राठी को देशद्रोही बताया।", "Regular", "leftJustified", 0.0),
        ("जुबिन नौटियाल के पिता कांग्रेस में शामिल हुए", "Subhead", "center", 0.0),
        ("देहरादून जिला पंचायत के पूर्व अध्यक्ष और गायक जुबिन नौटियाल के पिता राम शरण नौटियाल कांग्रेस में शामिल हो गए हैं। कुछ दिन पहले उन्होंने भाजपा से इस्तीफा दिया था। जब उन्होंने भाजपा से इस्तीफा दिया था तभी चर्चा थी कि वे कांग्रेस में शामिल होंगे। एआईसीसी की राष्ट्रीय महासचिव कुमारी शैलजा ने उन्हें कांग्रेस की सदस्यता दिलाई। राम शरण नौटियाल ने राजनीति की शुरुआत कांग्रेस से की थी। वे उत्तराखंड कांग्रेस के उपाध्यक्ष भी रहे थे। वर्ष २०१४ में नौटियाल भाजपा में शामिल हुए थे। उसके बाद २०२२ के चुनाव में भाजपा ने उन्हें चकराता सीट से टिकट दिया था, हालांकि वे जीत नहीं सके थे। कांग्रेस में शामिल होने के बाद नौटियाल ने कहा कि, ‘पार्टी मेरे लिए क्या सोचती है यह मैं नहीं कह सकता, परंतु मेरा मन कांग्रेस के बिना नहीं मानता था। इसलिए मैं फिर से कांग्रेस में शामिल हुआ।’", "Regular", "leftJustified", 9.0),
        ("मानहानि नोटिस मामले में सुधाकर सिंह की स्पीकर से गुहार", "Subhead", "center", 0.0),
        ("बिहार के भोजपुर जिले के बौलौटी गांव में भरत भूषण तिवारी के कथित फर्जी एनकाउंटर का मामला अब संसदीय स्तर पर पहुंच गया है। इस मामले में सवाल उठाने वाले आरजेडी सांसद सुधाकर सिंह ने बिहार के वरिष्ठ आईपीएस अधिकारी कुंदन कृष्णन की ओर से भेजे गए मानहानि नोटिस के संदर्भ में लोकसभा अध्यक्ष ओम बिरला से हस्तक्षेप की मांग की है। सुधाकर सिंह ने पत्र लिखकर पूरे मामले की जांच करने तथा प्रथम दृष्टया जो तथ्य सामने आएं उन्हें संसद की विशेषाधिकार समिति के पास भेजने की मांग की है। कुंदन कृष्णन ने अपने निजी वकील के माध्यम से यह नोटिस भेजा था। सांसद का कहना है कि नोटिस में सार्वजनिक माफी के साथ पांच करोड़ रुपये के मुआवजे की मांग भी की गई है।", "Regular", "leftJustified", 9.0),
        ("टाइगर श्रॉफ पर फायरिंग कराने वाला अनिल पंडित कौन है?", "Subhead", "center", 0.0),
        ("अमेरिका में बैठे गैंगस्टर अनिल पंडित का नाम फिर एक बार चर्चा में आया है। रविवार शाम मुंबई के खार इलाके में अभिनेता टाइगर श्रॉफ की कार पर फायरिंग की गई थी। उसके बाद सामने आए वीडियो में अनिल पंडित और हरमन संधू ने इस", "Regular", "leftJustified", 9.0),
    ],
    target_lines=68,
    base_pt=10.6,
)

# Col 3 Top: continuation of दिल्ली की बात (y=200..716)
place_exact_body_column(
    746, 200, 1051, 716,
    text=(
        "घटना की जिम्मेदारी ली है। पंडित ने ऑडियो में सलमान खान और उनके परिवार को भी धमकी दी है। अनिल पंडित का नाम इससे पहले हरियाणा में हुई एक फायरिंग में सामने आया था। इस वर्ष मार्च महीने में पानीपत के एक मनी एक्सचेंज ऑफिस पर दिनदहाड़े गोलीबारी की गई थी। सोशल मीडिया पर लॉरेंस बिश्नोई गैंग से जुड़े लोगों ने यह गोलीबारी कराने की जिम्मेदारी ली थी। उस समय अमेरिका में रहने वाले अनिल पंडित और रणदीप मलिक के नाम सामने आए थे। उस वक्त पंजाब के एक गायक-रैपर बादशाह को भी धमकियां दी गई थीं।"
    ),
    target_lines=17,
    first_indent_pt=0.0,
)

# Col 3 Mid-Top: अमेरिकन (प्रथम पृष्ठ का शेष) (y=732..1188)
place_mixed_paras_column(
    746, 732, 1051, 1188,
    paras=[
        ("अमेरिकन", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("सैटेलाइट को नष्ट करने की होड़ शुरू हो सकती है और तब दुनिया के कम्युनिकेशन सिस्टम के लिए बहुत बड़ा खतरा पैदा हो सकता है। रूस ने कॉसमॉस-२५९२ सैटेलाइट अभी इसी वर्ष अप्रैल में ही लॉन्च किया था। संभव है कि उस समय यूक्रेन की आधुनिक मिसाइलों और ड्रोन के रडार सिस्टम को जाम करने के इरादे से ही इसे लॉन्च किया गया हो।", "Regular", "leftJustified", 0.0),
        ("इस घटना के बाद पहली बार रूस-यूक्रेन के बीच का युद्ध जमीन से ऊपर अंतरिक्ष तक पहुंच गया है।", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)

# Col 3 Mid: फ्रांस में हिंसा (प्रथम पृष्ठ का शेष) (y=1202..1472)
place_mixed_paras_column(
    746, 1202, 1051, 1472,
    paras=[
        ("फ्रांस में हिंसा", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("है। फ्रांस के राष्ट्रपति ने हिंसा रोकने के लिए पुलिस को नई रणनीति बनाने के भी निर्देश दिए हैं। रविवार को अनेक शहरों में प्रदर्शनकारियों ने सड़क पर रखे कूड़ेदानों, साइकिलों और वाहनों को आग के हवाले कर दिया था।", "Regular", "leftJustified", 0.0),
    ],
    target_lines=9,
    base_pt=10.5,
)

# Col 3 Mid-Bot: सहयोगी देशों (प्रथम पृष्ठ का शेष) (y=1486..2288)
place_mixed_paras_column(
    746, 1486, 1051, 2288,
    paras=[
        ("सहयोगी देशों", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("इंफ्रास्ट्रक्चर की १० सुविधाओं को नुकसान पहुंचाया गया है।", "Bold", "leftJustified", 0.0),
        ("इस हमले के कारण पांच लाख से अधिक लोग बिजली, हीटिंग और पानी की आपूर्ति से वंचित हो गए हैं। कीव और उसके आसपास के इलाकों में १६ बैलिस्टिक मिसाइलें दागी गई थीं। रूस ने यूक्रेन में ट्रेनों, शॉपिंग मॉल, गैस स्टेशन, सुपरमार्केट और अन्य स्थानों पर हमले कर सामान्य जनजीवन में बाधा उत्पन्न करने का प्रयास किया है।", "Regular", "leftJustified", 9.0),
        ("इस बीच यूक्रेन युद्ध के संबंध में अमेरिका-चीन-रूस के बीच वार्ता की संभावनाओं को खारिज कर दिया गया है।", "Bold", "leftJustified", 9.0),
        ("लिथुआनिया के प्रधानमंत्री मिंडाउगास सिंकेविसियस ने सोमवार को बताया कि स्टारलिंक बेस पर आग लगाने के प्रयास के बाद लिथुआनिया में सुरक्षा बढ़ा दी गई है।", "Regular", "leftJustified", 9.0),
    ],
    target_lines=26,
    base_pt=10.5,
)

# ==============================================================================
# 3. COLS 4-5 TOP: क्लाइमेट चेंज का बढ़ता खतरा धरती के सात संकेत रिकॉर्ड स्तर पर
# ==============================================================================
print("Building Climate Change Story (Cols 4-5 Top)...")
place_exact_display_lines(
    1078, 200, 1718, 250,
    lines=["वैज्ञानिकों की सोलह मापदंडों का अध्ययन कर चेतावनी"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1078, 256, 1718, 434,
    lines=[
        "क्लाइमेट चेंज का बढ़ता खतरा",
        "धरती के सात संकेत रिकॉर्ड स्तर पर"
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
        "नई दिल्ली, ता. १९\n"
        "१४ अक्टूबर, २०२६ को बायोसाइंस जर्नल में प्रकाशित रिपोर्ट के अनुसार, जलवायु परिवर्तन का खतरा लगातार बढ़ रहा है। वैज्ञानिकों ने पृथ्वी की स्थिति दर्शाने वाले सोलह महत्वपूर्ण संकेतों का अध्ययन किया, जिनमें से सात रिकॉर्ड स्तर पर पहुंच गए हैं। हवा में कार्बन डाइऑक्साइड और मीथेन की बढ़ती मात्रा, पिघलते ग्लेशियर और समुद्र का बढ़ता जलस्तर दर्शाते हैं कि मानवीय गतिविधियां पृथ्वी को लगातार गर्म कर रही हैं।"
    ),
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 600, 1718, 694,
    lines=[
        "ग्रीनहाउस गैसों और पिघलते ग्लेशियरों ने चिंता",
        "बढ़ाई, जीवाश्म ईंधन का उपयोग घटाना अनिवार्य"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 700, 1385, 1092,
    text=(
        "रिपोर्ट के अनुसार वर्ष २०२६ में कार्बन डाइऑक्साइड, मीथेन और नाइट्रस ऑक्साइड का औसत स्तर रिकॉर्ड ऊंचाई पर रहा है। ये ग्रीनहाउस गैसें वातावरण में गर्मी रोकती हैं, जिससे पृथ्वी का तापमान बढ़ता है। ग्रीनलैंड की बर्फ की चादर का वजन और हिमनदियों की मोटाई ऐतिहासिक निचले स्तर पर पहुंच गई है। समुद्र में गर्मी का संचय और जलस्तर बढ़ने से बाढ़, तटीय क्षेत्रों में नुकसान तथा पर्यावरणीय खतरे बढ़ रहे हैं।\n"
        "वैज्ञानिकों ने चेतावनी दी है कि तापमान में लगातार वृद्धि होने से क्लाइमेट"
    ),
    target_lines=13,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 700, 1718, 1092,
    text=(
        "टिपिंग पॉइंट जैसी स्थिति पैदा हो सकती है, जिसमें पर्यावरण में होने वाले बड़े बदलावों को रोकना अथवा पूर्व स्थिति में लाना कठिन हो जाता है। हालांकि ऐसे सभी बदलाव हो चुके होने का दावा रिपोर्ट नहीं करती। दूसरी ओर सौर और पवन ऊर्जा की उत्पादन क्षमता तथा बैटरी में बिजली संचय करने की सुविधा बढ़ी है। वर्ष २०२५ में प्राचीन उष्णकटिबंधीय जंगलों का नुकसान भी घटा था। इस सकारात्मक प्रगति के बावजूद कोयला, तेल और गैस की कुल खपत घटी नहीं है। बढ़ती ऊर्जा मांग के कारण स्वच्छ ऊर्जा की ओर बदलाव को अधिक तेज बनाना जरूरी है।"
    ),
    target_lines=13,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. COLS 4-5 MID: मणिपुर में (प्रथम पृष्ठ का शेष) (y=1106..1568)
# ==============================================================================
print("Building Manipur Continuation (Cols 4-5 Mid)...")
place_mixed_paras_column(
    1078, 1106, 1385, 1568,
    paras=[
        ("मणिपुर में", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("उनकी मौत हो गई, जबकि क्षेत्रिमायुम सुशील (३२) की एक निजी अस्पताल में मृत्यु हुई।", "Regular", "leftJustified", 0.0),
        ("घायल हुए अन्य तीन नागरिकों एन. सूरज (१८), मेडसनाम सोमेंद्रो (५३) और के. बोसन (४५) को उपचार दिया जा रहा है। इन लोगों सहित १६ लोगों का समूह सुबह ७ बजे के करीब अपने गांव के पास की पहाड़ियों से ईंधन के लिए लकड़ियां लेने गया था। उसी समय उन पर हमला कर दिया गया। इससे आक्रोशित", "Regular", "leftJustified", 9.0),
    ],
    target_lines=15,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1106, 1718, 1568,
    text=(
        "जनसमूह द्वारा घटना के विरोध में मुख्यमंत्री के आवास के बाहर प्रदर्शन करने पर मुख्यमंत्री वाई. खेमचंद सिंह ने अस्पताल जाकर घायलों का हालचाल पूछा, परंतु पत्रकारों के किसी सवाल का जवाब नहीं दिया।\n"
        "पुलिस ने प्रदर्शनकारियों को तितर-बितर करने के लिए आंसू गैस के गोले छोड़े। बाद में मृतकों के शवों को जवाहरलाल नेहरू इंस्टीट्यूट ऑफ मेडिकल साइंसेज ले जाया गया। मुख्यमंत्री आवास और वहां तक पहुंचने वाले मार्गों पर सुरक्षा बढ़ा दी गई है। इस घटना के बाद पूरे इंफाल में बाजार और दुकानें बंद रहीं।"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. COLS 4-6 MID-BOT: टाइगर पर (प्रथम पृष्ठ का शेष) (y=1580..2288)
# ==============================================================================
print("Building Tiger Shroff Continuation (Cols 4-6 Mid-Bot)...")
place_mixed_paras_column(
    1078, 1580, 1385, 2288,
    paras=[
        ("टाइगर पर", "Header", "center", 0.0),
        ("(प्रथम पृष्ठ का शेष)", "Bold", "center", 0.0),
        ("किया था। रितिक कुमार उर्फ रोशन रैपिडो बाइक राइडर होने के कारण बाइक चलाने में कुशल था और उसे सभी रास्तों की जानकारी थी। इसलिए उसने बाइक चलाई थी। रितिक ने ही बोरीवली पहुंचकर वहां से ऐप के जरिए सूरत की कैब बुक की थी। डीसीपी ने बताया कि शूटर द्वारा गोलीबारी में प्रयुक्त मोटरसाइकिल अंधेरी इलाके से बरामद हो गई है। तीनों संदिग्धों के पास से कोई हथियार नहीं मिला है। हम आरोपियों को राजस्थान से मुंबई ला रहे हैं।", "Regular", "leftJustified", 0.0),
        ("डीसीपी ने कहा कि टाइगर श्रॉफ द्वारा जान के खतरे की कोई शिकायत पहले नहीं मिली थी। अभिनेता पर गोलीबारी करने के पीछे का मकसद अभी स्पष्ट नहीं हुआ है। संदिग्ध हमलावरों से पूछताछ करने के बाद ही हम गोलीबारी का सटीक कारण जान सकेंगे।", "Regular", "leftJustified", 9.0),
        ("जाहिर तौर पर आरोपियों ने बाइक,", "Regular", "leftJustified", 9.0),
    ],
    target_lines=23,
    base_pt=10.5,
)
place_exact_body_column(
    1412, 1580, 1718, 2260,
    text=(
        "लोकल ट्रेन, कैब और फिर लंबी दूरी की ट्रेन— इस तरह अलग-अलग परिवहन विकल्पों का उपयोग कर जांच एजेंसियों को चकमा देने का प्रयास किया था। परंतु दिल्ली, गुजरात और राजस्थान पुलिस बलों की सक्रिय तकनीकी और ऑपरेशनल सहायता के साथ क्राइम ब्रांच की २० विशेष टीमों द्वारा चलाए गए त्वरित अंतरराज्यीय ऑपरेशन में घटना के १५ घंटे के भीतर राजस्थान के कोटा में ट्रेन से तीनों को दबोच लिया गया।\n"
        "सूरत से वे पुणे-जयपुर ट्रेन में बैठे थे। वे ठीक किस कम्पार्टमेंट में बैठे हैं इसकी जानकारी भी मुंबई पुलिस ने हासिल कर ली थी। सटीक सूचना के आधार पर कोटा पुलिस ने ट्रेन में तुरंत उस कम्पार्टमेंट में पहुंचकर तीनों को पकड़ लिया।\n"
        "रितिक ने हमले में प्रयुक्त बाइक अभी पिछली ११ सितंबर को ही खरीदी थी। उसने उसके मालिकाना कागजात भी ट्रांसफर नहीं कराए थे। २०२२ से इस बाइक का"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 1580, 2050, 2260,
    text=(
        "स्वामित्व अलग-अलग चार लोगों के बीच बदला था। रितिक को बाइक किसने उपलब्ध कराई और उसके पैसे कहां से आए, इसके आधार पर पुलिस इस गोलीबारी के मास्टरमाइंड तक पहुंच सकती है।\n"
        "तीन में से दो आरोपी एक ही स्थान के निवासी और एक-दूसरे के परिचित थे। सीसीटीवी फुटेज में कैप पहने जो आरोपी दिखा है वह रेहान था। गोलीबारी में दो हथियारों का उपयोग हुआ था और कई राउंड फायर किए गए थे। सभी आरोपियों के खिलाफ हत्या के प्रयास सहित विभिन्न धाराएं लगाई गई हैं। पुलिस गोलीबारी की जिम्मेदारी लेने वाली लॉरेंस बिश्नोई गैंग की सोशल मीडिया पोस्ट की सत्यता की भी अभी जांच कर रही है, ऐसा डीसीपी ने बताया। टाइगर श्रॉफ को इससे पहले किसी से धमकी मिलने की कोई शिकायत पुलिस रिकॉर्ड में नहीं है।"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. COLS 6-8 TOP: विश्व के २० सबसे प्रदूषित शहरों में १३ भारत के, दिल्ली शामिल नहीं
# ==============================================================================
print("Building 20 Most Polluted Cities Story (Cols 6-8 Top)...")
place_exact_display_lines(
    1744, 200, 2712, 252,
    lines=["इंडोनेशिया-मलेशिया के शहर भी सूची में शामिल"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
    underline=True,
)
place_exact_display_lines(
    1744, 258, 2712, 434,
    lines=[
        "विश्व के २० सबसे प्रदूषित शहरों में",
        "१३ भारत के, दिल्ली शामिल नहीं"
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
        "नई दिल्ली, ता. १९\n"
        "विश्व के सबसे प्रदूषित शहरों की वैश्विक रैंकिंग में भारत का वर्चस्व देखा गया, जिसमें २० में से १३ शहरों में सर्वाधिक वायु प्रदूषण का स्तर दर्ज हुआ। हालांकि भारत में हवा की गुणवत्ता बिगड़ने के"
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_body_column(
    2238, 440, 2712, 556,
    text=(
        "साथ अक्सर जोड़ी जाने वाली दिल्ली उस समय सूची में नहीं थी। एक्यूआई द्वारा सोमवार को जारी आंकड़ों के अनुसार, उत्तर प्रदेश के बुलंदशहर को वैश्विक स्तर पर तीसरा स्थान मिला, जहां यूएस एक्यूआई रीडिंग १९८ थी, जो अस्वस्थ श्रेणी में आती है।"
    ),
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 562, 2712, 652,
    lines=[
        "प्रदूषण संबंधी रियल टाइम वैश्विक रैंकिंग में",
        "दिल्ली में वायु गुणवत्ता का स्तर बदलता रहा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 658, 2050, 1568,
    text=(
        "त्रिपुरा का अगरतला एक्यूआई १८१ के साथ चौथे स्थान पर रहा। टॉप २० में शामिल अन्य भारतीय शहरों में राजस्थान का पाली और उत्तर प्रदेश का मुजफ्फरनगर शामिल हैं, दोनों में एक्यूआई १७४ दर्ज किया गया। मध्य प्रदेश के बुरहानपुर में भी एक्यूआई १७४ था, जबकि हरियाणा के रोहतक में १७२ रहा। राजस्थान के कोटा में १७०, मुंबई में १६७, हापुड़ में १६६, हिसार में १६५, बीकानेर में १६५ और बरेली में १६४ दर्ज किया गया। इन रीडिंग्स ने भारत के इन शहरों को विश्व के सबसे प्रदूषित शहरी क्षेत्रों में शामिल कर दिया है।\n"
        "इंडोनेशिया के अनेक शहर प्रदूषित शहरों में शीर्ष के करीब थे। मध्य कालिमंतान का पलंगकराया प्रथम स्थान पर रहा, जो यूएस एक्यूआई २४२ के साथ गंभीर श्रेणी में आता है। पालेमबांग में २०७ दर्ज हुआ, जो गंभीर श्रेणी में है। सांपित और जाम्बी क्रमशः १८० और १७६ एक्यूआई के साथ पांचवें और छठे स्थान पर रहे। मलेशिया के पुत्रजया, कुआलालंपुर और पेटालिंग जया भी टॉप २० में शामिल थे। हालांकि दिल्ली वैश्विक टॉप २० शहरों की रैंकिंग में नहीं थी, पर उसकी वायु गुणवत्ता रात में बिगड़ी थी।"
    ),
    target_lines=29,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2076, 658, 2382, 1122,
    text=(
        "राजधानी के ऐतिहासिक एक्यूआई ग्राफ में सोमवार को यूएस एक्यूआई अधिकतम १९१ तक पहुंचा था, फिर दिन के दौरान घटा। १८ अक्टूबर को शाम ५:०१ बजे न्यूनतम १२६ दर्ज किया गया था।\n"
        "दिल्ली का एक्यूआई सुबह के उच्च स्तर से घटकर १९ अक्टूबर की दोपहर १३० के आंकड़े तक आ गया। ये रीडिंग्स दर्शाती हैं कि वायु प्रदूषण शहरों और घंटों के बीच कितना बदल सकता है। रियल टाइम रैंकिंग में किसी शहर की स्थिति केवल एक स्नैपशॉट है और मौसम की स्थिति, उत्सर्जन तथा"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 658, 2712, 1122,
    text=(
        "वायुमंडलीय परिसंचरण बदलने पर वह बदल सकती है। एक्यूआई.इन रैंकिंग यूएस एयर क्वालिटी इंडेक्स का उपयोग करती है, जिसमें १५१ से २०० के बीच की रीडिंग्स अस्वस्थ श्रेणी में आती हैं, जबकि २०० से ऊपर के मूल्य अत्यंत अस्वस्थ अथवा गंभीर प्रदूषण दर्शाते हैं। कोई शहर वैश्विक रैंकिंग से बाहर हो तब भी उच्च प्रदूषण स्वास्थ्य के लिए खतरा पैदा कर सकता है। विशेषकर बच्चों, बुजुर्गों और श्वसन या हृदय संबंधी समस्या वाले लोगों के लिए जोखिम बढ़ सकता है।"
    ),
    target_lines=15,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. COLS 7-8 MID: दक्षिण भारत में दक्षिण-पश्चिम मानसून विफल रहने से जल संकट पैदा हुआ
# ==============================================================================
print("Building South India Monsoon Story (Cols 7-8 Mid)...")
place_exact_display_lines(
    2076, 1136, 2712, 1184,
    lines=["कर्नाटक और आंध्र प्रदेश के कई क्षेत्रों में सूखा घोषित"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    underline=True,
)
place_exact_display_lines(
    2076, 1188, 2712, 1344,
    lines=[
        "दक्षिण भारत में दक्षिण-पश्चिम मानसून",
        "विफल रहने से पानी की किल्लत पैदा हुई"
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
        "नई दिल्ली, ता. १९\n"
        "दक्षिण भारत के जलाशयों में जल संग्रहण कम होने से आगामी महीनों में कृषि, पेयजल और बिजली उत्पादन आदि के लिए समस्या खड़ी होगी। दक्षिण भारत जून से सितंबर के दौरान साउथ-वेस्ट मानसून और अक्टूबर-दिसंबर के दौरान नॉर्थ-ईस्ट मानसून पर निर्भर है। यह नॉर्थ-ईस्ट मानसून तमिलनाडु, पुडुचेरी, आंध्र प्रदेश के तटीय इलाकों के कुछ हिस्से और कर्नाटक के दक्षिणी भाग में बरसता है। साउथ-वेस्ट मानसून और नॉर्थ-ईस्ट मानसून— इस तरह दो बार दक्षिण भारत के कई क्षेत्रों में बारिश होती है।"
    ),
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1560, 2712, 1650,
    lines=[
        "पीने के पानी की किल्लत और फसल",
        "खराब होने जैसी समस्याएं खड़ी हुईं"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1656, 2382, 2142,
    text=(
        "मानसून के बाद जलाशयों में संग्रहित पानी का उपयोग सिंचाई, घरेलू जरूरतों और बिजली उत्पादन के लिए किया जाता है। पानी की डिमांड, भूजल की उपलब्धता और आगे होने वाली बारिश के आधार पर विभिन्न क्षेत्रों के जल संकट की गंभीरता पता चलेगी। आंध्र प्रदेश के सोमशिला जलाशय में कुल क्षमता का केवल २२.०५ प्रतिशत, श्रीशैलम में ३३.६४ प्रतिशत, तमिलनाडु के मेट्टूर में ३२.४९ प्रतिशत, केरल के इडुक्की में १०.६२ प्रतिशत, कर्नाटक के घटप्रभा में २२.५६ प्रतिशत और तुंगभद्रा में २२.५४ प्रतिशत जल है। केरल के शोलायार में २३.६२ प्रतिशत और पेरियार में ४६.४३ प्रतिशत जल संग्रहण हुआ है। कावेरी नदी बेसिन में जल संग्रहण की कुल क्षमता में"
    ),
    target_lines=16,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 1656, 2712, 2142,
    text=(
        "६०.५० प्रतिशत और पेन्नार बेसिन में ७२.३२ प्रतिशत जल संग्रहण कम हुआ है।\n"
        "कृष्णा बेसिन में सामान्य से ३२.५९ प्रतिशत कम संग्रहण हुआ है। पेन्नार से कन्याकुमारी तक बहने वाली नदियों और तादरी से कन्याकुमारी तक बहने वाली नदियों के बेसिन में पानी का संग्रहण कम हुआ है। भारतीय मौसम विभाग (आईएमडी) के आंकड़े दर्शाते हैं कि १ जून और ३० सितंबर के बीच कर्नाटक में बारिश की कमी ३० प्रतिशत और आंध्र प्रदेश में २५ प्रतिशत दर्ज की गई। कर्नाटक के भीतरी इलाकों और आंध्र प्रदेश के रायलसीमा क्षेत्र में बारिश की कमी का गंभीर असर हुआ है।"
    ),
    target_lines=16,
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. BOTTOM PUBLIC NOTICES (सार्वजनिक सूचना) — 100% EDITABLE HINDI TEXT & CMYK BAR
# ==============================================================================
print("Building Page 9 Bottom Public Notices (100% Editable Hindi Text)...")


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


# 1. Cols 1-2 Top Notice (82..718, 2320..3040)
place_public_notice_2col(
    82, 2320, 718, 3040,
    left_text=(
        "डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट और तालुका साणंद के गांव मौजे चेखला की सीम के (पुराने ब्लॉक नंबर - २५३ पैकी, ३१९ पैकी, ३२१, ३२२ पैकी, ३२३ पैकी, ३२४ पैकी, ३२५ पैकी) एकत्रित ब्लॉक नंबर - ३२१ वगैरह की भूमि पर स्थित सिल्वर स्प्रिंग्स के नाम से जानी जाने वाली योजना में स्थित प्लॉटों में से सब प्लॉट नंबर - १२३ की ४२२.२४ वर्ग मीटर क्षेत्रफल की आवासीय हेतु की गैर-कृषि भूमि ज्वलंतभाई वोहरा एच.यू.एफ. के नाम से दर्ज एच.यू.एफ. के कर्ता ज्वलंतभाई वोहरा का ता. १३-१२-२०१५ को निधन होने से माननीय कोर्ट के उत्तराधिकार प्रमाणपत्र के आधार पर नयनाबेन ज्वलंतभाई वोहरा ने अपने स्वतंत्र स्वामित्व, कब्जे-भोगवटे की एवं सभी प्रकार के बोझों से मुक्त होने का बताकर उक्त भूमि हमारे मुवक्किल को बेचने का तय किया है और इस संबंध में हमारे"
    ),
    right_text=(
        "मुवक्किल ने हमसे उक्त भूमि के टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है।\n"
        "उक्त भूमि पर किसी भी व्यक्ति या संस्था का किसी भी प्रकार का हक, दावा, लागभाग, लीज, गिरवी या बोझ हो तो उस संबंधी लिखित सबूत के साथ हमें दिन-७ (सात) में नीचे दिए पते पर सूचित करें और यदि ऐसा करने में चूक हुई तो उक्त भूमि पर किसी का किसी भी प्रकार का बोझ या हक-दावा या अधिकार नहीं है और यदि हो तो वे सभी त्याग दिए हैं, ऐसा समझकर हम उक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी करेंगे। उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी।\n"
        "अहमदाबाद। ता. २०-१०-२०२६।\n"
        "मुकेश जी. पंड्या, एडवोकेट\n"
        "४०३, विश्वनाथ नॉर्थ व्यू, एल.डी. इंजीनियरिंग कॉलेज के सामने, सेंट जेवियर्स कॉलेज के पास, नवरंगपुरा, अहमदाबाद।\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 2. Cols 1-2 Bottom Notice (82..718, 3052..3845)
place_public_notice_2col(
    82, 3052, 718, 3845,
    left_text=(
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद के सब-डिस्ट्रिक्ट और तालुका बावला के गांव मौजे दुर्गा की सीम के नए सर्वे/ब्लॉक नंबर-२६४ (पुराने सर्वे/ब्लॉक नंबर-१६३) की कुल २८८९२ वर्ग मीटर तथा नए सर्वे नंबर-२६६ (पुराने सर्वे/ब्लॉक नंबर-१६४) की कुल ३०३०२ वर्ग मीटर कृषि भूमि हेमुभाई कालुभाई, मधुभाई कालुभाई, मयारामभाई कालुभाई, बुटाभाई कालुभाई, सागरभाई धरमशीभाई, समजुबेन विधवा पोपटभाई, टिलुभाई पोपटभाई, वशुबेन पोपटभाई तथा लाभुभाई पोपटभाई ने अपने पूर्णतः संयुक्त स्वामित्व, कब्जे, भोगवटे की एवं सभी बोझों से मुक्त होने का बताकर हमसे उक्त भूमि के टाइटल क्लीयर और मार्केटेबल होने के प्रमाणपत्र की मांग की है। अतः उक्त भूमि पर यदि किसी का"
    ),
    right_text=(
        "किसी भी प्रकार का लाग-भाग, हक, हित, हिस्सा, दावा या बोझ हो तो वे इस नोटिस के प्रसिद्ध होने से दिन-७ (सात) में हमें उस संबंधी आवश्यक सबूतों सहित लिखित में नीचे दिए पते पर सूचित करें। यदि ऐसा नहीं किया गया तो उक्त भूमि पर अन्य किसी भी व्यक्ति का किसी भी प्रकार का लाग-भाग, हक, हित, हिस्सा, दावा या बोझ नहीं है और यदि हो तो वह त्याग दिया है, ऐसा मानकर हम उक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी करेंगे और उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी।\n"
        "तारीख-२०/१०/२०२६\n"
        "कौशिक जी. पटेल\n"
        "(एडवोकेट एंड नोटरी)\n"
        "ऑफिस :- १२, दूसरी मंजिल, जे.बी.आर. आर्केड, आर.के. रॉयल हॉल के बाजू में, साइंस सिटी रोड, सोला, अहमदाबाद-३८००६०।\n"
        "मो.नं. ९८२४६७८७६९"
    ),
    left_lines=23,
    right_lines=25,
)

# 3. Cols 3-4 Top Notice (746..1385, 2320..2990)
place_public_notice_2col(
    746, 2320, 1385, 2990,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-८ (सोला) के तालुका घाटलोडिया के मौजे गांव सोला की सीम के एकत्रित रेवेन्यू सर्वे नं. ४७७ यानी टी.पी. स्कीम नं. ४२ के फाइनल प्लॉट नं. ५८/१ और ५८/२ की गैर-कृषि भूमि में निर्मित ‘समक बंग्लोज’ नामक योजना में स्थित आवासीय प्लॉट/बंग्लोज टाइप की संपत्तियों में से सब प्लॉट/बंगला नं. ३३ की लगभग २१० वर्ग मीटर यानी २५१ वर्ग गज भूमि में लगभग १४५.७८ वर्ग मीटर (ए.एम.सी. टैक्स बिल के अनुसार) निर्माण वाली संपत्ति तथा योजना की भूमि में अविभाजित भूमि के हक-हिस्से सहित संपत्ति (१) अरुणाबेन रसिकभाई रावल (२) कल्पन रसिकभाई रावल तथा (३) केतकी पुत्री रसिकलाल रावल एवं"
    ),
    right_text=(
        "पत्नी संजयकुमार रावल के कुल संयुक्त स्वामित्व, कब्जे-भोगवटे की है और हमारे मुवक्किल को बेचने का तय किया है, ऐसा बताकर हमसे टाइटल सर्टिफिकेट की मांग की है। इस संबंध में अन्य किसी का किसी भी प्रकार का लागभाग, हक, हिस्सा, बोझ या अधिकार हो तो दिन-७ में रजि. ए.डी. पोस्ट से सबूत सहित लिखित सूचना दें, अन्यथा उन्होंने अपना हक, हित, हिस्सा त्याग दिया है ऐसा मानकर टाइटल क्लीयर सर्टिफिकेट संबंधी कार्यवाही की जाएगी।\n"
        "ता. १९/१०/२०२६\n"
        "स्थान: अहमदाबाद\n"
        "मेरे माध्यम से,\n"
        "महेंद्रसिंह बी. सिसोदिया (एडवोकेट)\n"
        "(मो) ९८२५७८६२२५\n"
        "बी/२२, ऋतुराज सोसायटी, सुभाष चौक के पास, गुरुकुल रोड, मेमनगर, अहमदाबाद-५२।"
    ),
    left_lines=20,
    right_lines=22,
)

# 4. Cols 3-4 Bottom Notice (746..1385, 3002..3845)
place_public_notice_2col(
    746, 3002, 1385, 3845,
    left_text=(
        "एतद्द्वारा हम एडवोकेट श्री एम.एस. काजी हमारे मुवक्किल निर्भयनगर को.ऑ.हा.सो.लि. रजिस्ट्रेशन नं. घ-६४१ के चेयरमैन-सेक्रेटरी की सूचना और निर्देश से यह सार्वजनिक सूचना देकर सूचित करते हैं कि - डिस्ट्रिक्ट सब-डिस्ट्रिक्ट अहमदाबाद-५ (नारोल), मणिनगर तालुका के मौजे दाणीलीमडा के स.नं. २०/२, टी.पी. स्कीम नं. ३७, फा. प्लॉट नं. ८३, सेक्टर-२ में स्थित निर्भयनगर को.ऑ.हा.सो.लि. रजिस्टर नं. घ-६४१ के टेनामेंट नं. ११-बी वाली संपत्ति की मूल अलॉटी मेंबर शांताबेन कांतिलाल सोनी थीं। उन्हें सोसायटी के शेयर नं. २४६ से २५० जारी किए गए थे और ओरिजिनल शेयर सर्टिफिकेट उन्हें दिया गया था। शांताबेन कांतिलाल सोनी का ता. १५-९-२००४ को निधन हो चुका है और उन्हें दिया गया शेयर सर्टिफिकेट भूलवश खो गया है और काफी तलाश करने पर भी मिल"
    ),
    right_text=(
        "नहीं रहा है। उनके वारिसों में से भूपेंद्र कांतिलाल सोनी और सुदीप व्रजवल्लभ सोनी ने सोसायटी में डुप्लीकेट शेयर सर्टिफिकेट प्राप्त करने के लिए आवेदन किया है। उक्त वारिसों को डुप्लीकेट शेयर सर्टिफिकेट देने के प्रति किसी को आपत्ति या विवाद हो तो इस नोटिस के प्रसिद्ध होने से दिन-७ में सोसायटी के चेयरमैन-सेक्रेटरी को तथा हम एडवोकेट को लिखित में आपत्ति भेजें। यदि कोई आपत्ति नहीं आएगी तो उन्हें डुप्लीकेट शेयर सर्टिफिकेट जारी कर दिया जाएगा।\n"
        "अहमदाबाद ता:- २०-१०-२०२६\n"
        "चेयरमैन/सेक्रेटरी के हस्ताक्षर\n"
        "(निर्भयनगर को.ऑ.हा.सो.लि.)\n"
        "मेरे माध्यम से\n"
        "(एम.एस. काजी) एडवोकेट\n"
        "8/A, Nirbhaynagar Co.op. Hou. Society Ltd. Shahalam, Ahmedabad-28"
    ),
    left_lines=24,
    right_lines=26,
)

# 5. Cols 5-6 Top Notice (1412..2050, 2292..3028)
place_public_notice_2col(
    1412, 2292, 2050, 3028,
    left_text=(
        "डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट और तालुका साणंद के गांव मौजे रेथल की सीम के एकत्रित सर्वे/ब्लॉक नंबर - २२० (सर्वे नंबर - १२७, २१२, २१८, २१९, २२१, २२४, २३१, २३७, २४६, २६८, २७४, २९२, २९५, ३९८, ४००, ४१०, ४११, ४१५, ४१६, ४१७, ४२३, ४२४) वगैरह की आवासीय हेतु वाली गैर-कृषि भूमि पर रखी गई प्लॉटिंग स्कीम जो सुरम्य एबोड के नाम से जानी जाती है, उसमें स्थित सब प्लॉट नंबर - एई - २३ की ५३३ वर्ग गज (अलॉटमेंट लेटर के अनुसार - ५७० वर्ग गज सुपर एरिया) आवासीय हेतु की गैर-कृषि भूमि अंकित अजयकुमार मर्चेंट तथा अवनी अंकित मर्चेंट ने अपने संयुक्त स्वामित्व, कब्जे-भोगवटे की एवं सभी प्रकार के बोझों से मुक्त होने का बताकर उक्त भूमि हमारे मुवक्किल को बेचने का तय किया है और इस संबंध में हमारे मुवक्किल ने हमसे"
    ),
    right_text=(
        "उक्त भूमि के टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। उक्त प्लॉट की भूमि पर किसी भी व्यक्ति या संस्था का किसी भी प्रकार का हक, दावा, लागभाग, लीज, गिरवी या बोझ हो तो उस संबंधी लिखित सबूत के साथ हमें दिन-७ (सात) में नीचे दिए पते पर रजि. ए.डी. से सूचित करें और यदि ऐसा करने में चूक हुई तो उक्त भूमि पर किसी का किसी भी प्रकार का बोझ या हक-दावा या अधिकार नहीं है और यदि हो तो वे सभी त्याग दिए हैं, ऐसा समझकर हम उक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी करेंगे। उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी।\n"
        "अहमदाबाद। ता. २०-१०-२०२६।\n"
        "मुकेश जी. पंड्या, एडवोकेट\n"
        "४०३, विश्वनाथ नॉर्थ व्यू, एल.डी. इंजीनियरिंग कॉलेज के सामने, सेंट जेवियर्स कॉलेज के पास, नवरंगपुरा, अहमदाबाद।\n"
        "Mob. : 98259 09777"
    ),
    left_lines=22,
    right_lines=24,
)

# 6. Cols 5-6 Bottom Notice (1412..2050, 3040..3845)
place_public_notice_2col(
    1412, 3040, 2050, 3845,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद के सब-डिस्ट्रिक्ट और तालुका बावला मौजे भायला की सीम के खाता नं. ५९५ के ब्लॉक/सर्वे नं. १५३ पैकी १ की हे-आर-चो.मी. ०-६५-८६ आकार रु. ३.४० वाली यानी ६५८६ वर्ग मीटर क्षेत्रफल वाली पुरानी शर्त की सिंचित कृषि भूमि वाली संपत्ति वनराजसिंह रामसंगभाई परमार के स्वतंत्र स्वामित्व और कब्जे-भोगवटे की तथा दि भायला ग्रुप सेवा सहकारी मंडली लि. से लिए गए ऋण के बोझ के अलावा सभी बोझों से मुक्त होने का बताकर हमारे मुवक्किल को बेचने का तय किया है और उन्होंने उक्त नंबर और माप वाली संपत्ति संबंधी टाइटल क्लीयर सर्टिफिकेट की हमसे मांग की है। इसलिए उक्त संपत्ति पर जिस किसी का हक, दावा, लिस पेंडेंसी, अधिकार, लागभाग, खुराकी-पोशाकी, लियन, बोझ, विवाद या भरण-पोषण का हक-दावा,"
    ),
    right_text=(
        "ईजमेंट राइट, चार्ज, बानाखत का हक या अन्य किसी भी प्रकार का हक, हिस्सा या हित संबंध आदि कुछ भी हो तो वे इस सार्वजनिक सूचना के प्रसिद्ध होने से दिन-७ (सात) में हमें दस्तावेजी लिखित सबूत सहित नीचे दिए पते पर सूचित करें। यदि ऐसा करने में चूक या विलंब हुआ तो उक्त संपत्ति पर किसी का किसी भी प्रकार का लागभाग, हक, हिस्सा, हित संबंध, बोझ, चार्ज नहीं है और यदि हो तो उन्होंने अपना हक त्याग [Waive] दिया है, ऐसा समझकर टाइटल क्लीयर सर्टिफिकेट जारी कर दिया जाएगा। उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी।\n"
        "ता. २०-१०-२०२६।\n"
        "R. D. Savalia (Advocate)\n"
        "ऑफिस : रोहित एस्टेट, उजाला सर्कल के सामने, एस.जी. हाईवे, सरखेज, अहमदाबाद - ३८२२१०।\n"
        "मो.: ९८९८००१७८१"
    ),
    left_lines=23,
    right_lines=25,
)

# 7. Cols 7-8 Top Notice (2076..2712, 2158..2964)
place_public_notice_2col(
    2076, 2158, 2712, 2964,
    left_text=(
        "मौजे विसलपुर\n"
        "डिस्ट्रिक्ट अहमदाबाद, तालुका दस्क्रोई के मौजे गांव विसलपुर की सीम के खाता नंबर २०३३ के ब्लॉक/सर्वे नंबर ७७३ पैकी २ वाली कुल ०-१३-९६ हे.आरे.चो.मी. यानी १३९६ वर्ग मीटर वाली भूमि जो गैर-कृषि होने से पूर्व सर्वे नंबर ७७३ का हिस्सा है, उस सर्वे नंबर ७७३ वाली समग्र २३५९ वर्ग मीटर भूमि का समावेश ड्राफ्ट टी.पी. स्कीम नंबर ४३० में होने पर उसे आवंटित फाइनल प्लॉट नंबर १२७ वाली १३९६ वर्ग मीटर गैर-कृषि भूमि (१) संदीपकुमार जयंतीलाल पटेल (२) मेहुलकुमार अरविंदभाई पटेल के संयुक्त स्वामित्व, कब्जे-भोगवटे की, बिना बोझ की तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है। अतः उक्त"
    ),
    right_text=(
        "भूमि में किसी का बोझ, चार्ज, काश्तकारी हक, गणोत हक, ईजमेंट राइट्स या अन्य किसी भी प्रकार का लागभाग, कब्जा-हक, हित, हिस्सा, दावा, विवाद या बोझ हो तो वे इस नोटिस के प्रसिद्ध होने से नीचे दिए पते पर दिन-१५ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें। यदि ऐसा नहीं किया गया तो मियाद समाप्त होने पर उक्त भूमि पर किसी का किसी भी प्रकार का बोझ, हक-दावा या अधिकार नहीं है और यदि हो तो वह त्याग (वेव) दिया है, ऐसा समझकर उक्त भूमि का टाइटल क्लीयरेंस संबंधी अभिप्राय सर्टिफिकेट जारी कर देंगे और उसके बाद किसी की कोई आपत्ति नहीं चलेगी।\n"
        "अहमदाबाद\n"
        "तारीख : २०/१०/२०२६\n"
        "जैमिन रोहितभाई पटेल, एडवोकेट\n"
        "३१३५, तीसरी मंजिल, टी.आर.पी. मॉल, ईस्ट कोर्ट, बोपल, अहमदाबाद-३८००५८।\n"
        "मो. नं. ९९७८९ ३२१९९"
    ),
    left_lines=22,
    right_lines=24,
)

# 8. Cols 7-8 Bottom Notice (2076..2712, 2978..3845)
place_public_notice_2col(
    2076, 2978, 2712, 3845,
    left_text=(
        "एतद्द्वारा सार्वजनिक सूचना देकर आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट गांधीनगर सब-डिस्ट्रिक्ट गांधीनगर जोन - ३ के तालुका गांधीनगर के मौजे गांव ईसनपुर मोटा की सीम के खाता नंबर १२३६ के ब्लॉक नंबर १२९१ (पुराने ब्लॉक नंबर ६६४ के पुराने रेवेन्यू सर्वे नंबर ६८४) की कुल हे.आरे.चो.मी. ०-२७-३५, आकार रु. १.४५ पैसे वाली कृषि भूमि कपिलाबेन रामाभाई पटेल के कुल स्वतंत्र संयुक्त स्वामित्व और कब्जे-भोगवटे की तथा बोझ रहित होने का बताकर हमारे मुवक्किल को बेचने का तय किया है और हमारे मुवक्किल ने हमसे उक्त भूमि के टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। उक्त भूमि पर कपिलाबेन रामाभाई पटेल ने किसी भी बैंक, व्यक्ति, फर्म या निजी संस्था से ऋण लेकर बोझ उत्पन्न नहीं किया है और न ही वर्तमान में चालू है, तथा उक्त भूमि अन्य किसी भी तीसरे व्यक्ति को लिखकर ट्रांसफर-असाइन नहीं की है और न ही उक्त भूमि में कोई राजस्व या दीवानी विवाद लंबित है"
    ),
    right_text=(
        "और न ही कोई डिक्री या स्थगन आदेश लागू है। तथा उक्त भूमि पर अन्य किसी का किसी भी प्रकार का लागभाग, हक, हित, हिस्सा, दावा, अधिकार, बोझ, चार्ज, लियन हो तो इस सार्वजनिक सूचना के प्रसिद्ध होने से दिन-७ में हमें लिखित सबूतों सहित रजि. ए.डी. से नीचे बताए पते पर सूचित करें और यदि ऐसा करने में चूक हुई तो मियाद समाप्त होने पर उक्त भूमि में अन्य किसी का किसी भी प्रकार का लागभाग, हक, हित, हिस्सा, दावा, बोझ, चार्ज, लियन नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर उक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा और उसके बाद हमारे मुवक्किल विक्रय संबंधी कार्यवाही करेंगे।\n"
        "अहमदाबाद\n"
        "तारीख:- १९/१०/२०२६\n"
        "नेहल एन. शाह एसोसिएट्स\n"
        "सौरिन राजेशभाई शाह, एडवोकेट\n"
        "४०८, शांतिमॉल, नवरंग टावर के सामने, सार्थक स्कूल के पास, सत्ताधार चार रास्ता के पास, घाटलोडिया, अहमदाबाद।\n"
        "मो.नं.- ७९८४९३०१३७"
    ),
    left_lines=25,
    right_lines=27,
)

place_png(0, 3855, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_09_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_09_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_09_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_09_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_09_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
