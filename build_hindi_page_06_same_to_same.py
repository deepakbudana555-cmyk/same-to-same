from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 6 BUILDER FOR AAS-PAAS (HINDI GUJARAT SAMACHAR)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  for Gauchar Land Encroachment PIL, Gujarat Power Crisis Continuation,
  4 Obituaries (शोक संदेश), and 15 Public Notices (सार्वजनिक सूचना)!
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 06 (100% Same-to-Same Editable Hindi)"
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


# ==============================================================================
# 1. RUNNING HEADER
# ==============================================================================
print("Placing Page 6 Hindi Running Header...")
build_hindi_running_header(6, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: GAUCHAR LAND ENCROACHMENT PIL (COLS 2-4 TOP)
# ==============================================================================
print("Building Story 1 (Gauchar Land Encroachment PIL, Cols 2-4 Top)...")
place_exact_display_lines(
    414, 200, 1382, 245,
    lines=["वाव के आंत्रोल गांव में गौचर भूमि पर अतिक्रमण के मुद्दे पर PIL"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    414, 250, 1382, 412,
    lines=[
        "गौचर की भूमि से अतिक्रमण हटाने",
        "के मुद्दे पर हाईकोर्ट ने रिपोर्ट मांगी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    414, 418, 718, 902,
    text="अहमदाबाद, सोमवार\nबनासकांठा जिले के वाव-थराद के आंत्रोल गांव में गावतल और गौचर की भूमि पर कथित अवैध अतिक्रमण और स्थानीय स्कूल के कैंपस में कॉमर्शियल दुकानें बनाकर किराए पर देने के प्रकरण में गुजरात हाईकोर्ट के समक्ष जनहित याचिका (रिट) दाखिल हुई है। जिसकी सुनवाई में एक्टिंग चीफ जस्टिस मानस रंजन पाठक और जस्टिस निखिल एस. केरियल की खंडपीठ ने जिला विकास अधिकारी (डीडीओ) से गौचर की भूमि से अतिक्रमण हटाने के संबंध में अधिकारियों द्वारा क्या कदम उठाए गए, इसकी रिपोर्ट मांगी है।",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(732, 420, 732, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 418, 1050, 1094,
    text="वाव-थराद के आंत्रोल गांव में गौचर और गावतल की भूमि पर अवैध अतिक्रमण के मामले में हाईकोर्ट में दायर जनहित याचिका में यह दलील दी गई थी कि गांव की गावतल और गौचर की जमीनों पर अवैध रूप से कच्चे-पक्के मकान बनाकर अवैध कब्जा कर लिया गया है। इतना ही नहीं, गांव के ही स्थानीय स्कूल के कैंपस की जगह में कॉमर्शियल निर्माण कर उसमें दुकानें सीधे किराए पर दे दी गई हैं। इस प्रकार, गांव की गौचर और गावतल की भूमि के अलावा स्कूल के प्रांगण में नियमों और कानूनी प्रावधानों का उल्लंघन कर व्यावसायिक उपयोग की आड़ में आर्थिक लाभ कमाया गया है।\nइस पूरे मामले में याचिकाकर्ता पक्ष द्वारा स्थानीय सरपंच से लेकर तलाटी, तालुका विकास अधिकारी, जिला विकास अधिकारी और बनासकांठा जिला कलेक्टर तक",
    target_lines=21,
    first_indent_pt=9.0,
)
draw_line(1064, 420, 1064, 1094, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 418, 1382, 1094,
    text="बार-बार अभ्यावेदन देकर उचित कदम उठाने की मांग की गई थी, लेकिन अब तक कोई कार्रवाई नहीं होने पर अंततः याचिकाकर्ता को हाईकोर्ट का दरवाजा खटखटाने के लिए मजबूर होना पड़ा है। याचिकाकर्ता पक्ष की ओर से सरकारी अधिकारियों को तत्काल प्रभाव से आंत्रोल गांव की गावतल और गौचर की भूमि से अवैध अतिक्रमण और निर्माण हटाकर गौचर की भूमि खाली कराने सहित अन्य राहत की मांग की गई थी। जिसके चलते हाईकोर्ट ने स्थानीय जिला विकास अधिकारी को आदेश दिया कि याचिकाकर्ताओं के आरोप के अनुसार क्या आंत्रोल गांव की गौचर भूमि पर अवैध अतिक्रमण हैं...? और यदि हैं, तो उन्हें हटाने के संबंध में स्थानीय अधिकारियों द्वारा क्या कदम उठाए गए, इस बारे में जिला विकास अधिकारी को अगली तारीख तक रिपोर्ट पेश करनी होगी। हाईकोर्ट ने मामले की अगली सुनवाई ३० अक्टूबर को तय की है।",
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
    lines=["गुजरात में बिजली संकट", "(अंतिम पृष्ठ का शेष)"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1412, 300, 1718, 548,
    text="भड़क उठा है। महत्वपूर्ण बात यह है कि बिजली के संकट को छिपाने के लिए सरकार अब 'लोड शेडिंग' और 'स्टैगरिंग हॉलिडे' जैसे अंग्रेजी शब्दों का सहारा ले रही है। ऐसी भी चर्चा है कि राजकोट, जामनगर, जूनागढ़, भावनगर और सूरत सहित अन्य शहरों में सप्ताह में एक बार ४ से ८ घंटे तक उद्योग बंद",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(1731, 200, 1731, 548, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 200, 2052, 548,
    text="रखने के लिए दबाव बनाया जा रहा है। दिवाली और नववर्ष का सीजन व्यापारियों के लिए पूरे साल की कमाई करने का होता है। बिजली के बिना प्रोडक्शन कैसे किया जाए, यह सवाल उठा है। ऐसे समय में ही बिजली कटौती के कारण करोड़ों रुपये के ऑर्डर कैंसिल होने की आशंका है, जिससे छोटे उद्योगपतियों की मुश्किलें बढ़ गई हैं। यदि यही स्थिति रही तो दिवाली के समय लाखों श्रमिकों की रोजी-रोटी छिन जाने का भी भय सता रहा है।",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_box(1412, 556, 2052, 602, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 560, 2046, 598,
    lines=["गांवों में बिजली कटौती, केवडिया कॉलोनी में रोशनी की जगमगाहट होगी"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 608, 2052, 822,
    text="गुजरात के सिर पर बिजली संकट आकर खड़ा हो गया है। बिजली की मांग बढ़ने से राज्य सरकार को केंद्र सरकार के सामने हाथ फैलाना पड़ा है और अतिरिक्त बिजली की मांग करनी पड़ी है। राज्य सरकार ने गुजरात की जनता से बिजली का किफायती उपयोग करने की अपील की है, लेकिन दूसरी तरफ खुद सरकार ही सरकारी तामझाम करके बिजली की भारी खपत कर रही है। हर साल की तरह इस साल भी केवडिया कॉलोनी में एकता परेड के उत्सव की तैयारियां हो रही हैं, तब किसान नेताओं का आरोप है कि जनता को सलाह देने वाली सरकार खुद सरकारी कार्यक्रमों में बिजली की खपत कम क्यों नहीं करती।",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_box(1412, 828, 2052, 874, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1418, 832, 2046, 870,
    lines=["बिजली संकट के बाद अब सौराष्ट्र पर पानी का संकट मंडराएगा"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 880, 2052, 1096,
    text="बिजली की अव्यवस्था के बाद अब राजकोट सहित पूरे सौराष्ट्र पर पीने के पानी का गंभीर संकट मंडरा रहा है। कमजोर मानसून के कारण जलाशय और नहरें खाली पड़ी हैं। सरकार की बहुप्रचारित 'सौनी योजना' की पाइपलाइनों में भी पानी सूख रहा है। यदि सर्दियों की शुरुआत में ही यह स्थिति है, तो आगामी गर्मियों में पीने के पानी के लिए हाहाकार मचने की आशंका दिख रही है। एक ओर त्योहारों का माहौल है, रबी बुवाई का सीजन है और दिवाली के त्योहार में अब कुछ ही दिन बाकी हैं, तब किसानों की चिंता बढ़ गई है क्योंकि बिजली संकट के बाद अब पानी का संकट भी पैदा होगा।",
    target_lines=8,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(746, 1100, 2052, 1100, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 4. OBITUARIES (शोक संदेश) & PUBLIC NOTICES (सार्वजनिक सूचना) — 100% EDITABLE TEXT
# ==============================================================================
print("Building Page 6 Obituaries & Public Notices (100% Editable Hindi Text)...")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=22, right_lines=24, header_h=50):
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
    lines=["दिल से दिलदार और हर उलझन के डॉक्टर,", "B.K.", "हमेशा हमारी स्मृतियों में जीवित रहेंगे।"],
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
        "पढ़े-लिखे तो थे ही, पर समझदार भी खरे!\n"
        "सबकी मदद करने को सदैव तत्पर ऐसे\n"
        "उनके नेक व्यक्तित्व को कभी\n"
        "भुलाया नहीं जा सकेगा।\n"
        "“हंसी की फुहारें बिखेरने वाले और\n"
        "मित्रों के साथ महफिल जमाने वाले”\n"
        "B.K. की स्मृति को कोटि-कोटि नमन।"
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
        "नृपेश शाह, मयूर शाह,\n"
        "योगेश शाह, कमल सतिया,\n"
        "जिगर शाह, सौरभ झवेरी,\n"
        "उत्पल शाह, स्व. सौरीन शेठ।"
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

# --- OBITUARY 2: अनाविल निधन (Cols 1-2: 82..718, 924..1284) ---
draw_box(82, 924, 718, 1284, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(96, 934, 292, 1136, "obit2_vinodbhai_photo.png")
draw_box(300, 932, 710, 976, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    308, 936, 702, 972,
    lines=["अनाविल निधन"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    300, 980, 710, 1052,
    text="अत्यंत दुःख के साथ सूचित करना है कि हमारे स्वजन विनोदभाई हरिप्रसाद देसाई का ता. १८ अक्टूबर, रविवार को दुःखद निधन हो गया है। ईश्वर की इच्छा सर्वोपरि।",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(300, 1056, 710, 1134, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    306, 1060, 704, 1130,
    lines=[
        "दिवंगत की प्रार्थना सभा ता. २१ अक्टूबर, २०२६ बुधवार को",
        "वसंत वाडी, जिराफ सर्कल के पास, बालवाटिका के पीछे, मणिनगर",
        "में सुबह ९ से ११ बजे के दौरान रखी गई है।"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 1140, 708, 1280,
    text=(
        "शोकाकुल: नीताबेन (नीलाबेन) विनोदभाई देसाई (पत्नी)\n"
        "राहुल विनोदभाई देसाई (पुत्र)    हेमंतभाई हरिप्रसाद देसाई (भाई)\n"
        "हिरल राहुल देसाई (पुत्रवधू)    गिरीश हरिप्रसाद देसाई (भाई)\n"
        "अलय विनोदभाई देसाई (पुत्र)    स्व. मुकेश हरिप्रसाद देसाई (भाई)\n"
        "श्वेता अलय देसाई (पुत्रवधू)    सुजल (पौत्र), पृथल (पौत्री)\n"
        "हरिप्रसाद गांडाभाई देसाई परिवार (खारा अब्रामा)"
    ),
    target_lines=6,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 3: कृणाल अजीतकूमार चोकसी (Cols 1-2: 82..718, 1296..1654) ---
draw_box(82, 1296, 718, 1654, stroke_swatch="[Black]", stroke_weight_pt=2.0)
place_png(86, 1300, 250, 1560, "obit3_krunal_photo.png")
draw_box(254, 1300, 714, 1330, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    260, 1302, 708, 1328,
    lines=["दुःखद निधन"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    256, 1334, 712, 1444,
    text=(
        "मेरे सुपुत्र कृणाल अजीतकूमार चोकसी\n"
        "का ता. ०७/१०/२०२६ बुधवार को दुःखद निधन हो गया है।\n"
        "दिवंगत की प्रार्थना सभा ता. २०/१०/२०२६ मंगलवार को\n"
        "सुबह ९.३० से ११.३० बजे नीचे दिए स्थान पर रखी गई है।"
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
        "स्थान: ग्राउंड फ्लोर, चंद्रमौलेश्वर हॉल,",
        "रंगसागर रोड, नारायण नगर, पालडी, अहमदाबाद"
    ],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    256, 1508, 712, 1558,
    lines=[
        "अजीतकूमार नटवरलाल चोकसी",
        "वीणाबेन अजीतकूमार चोकसी"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    90, 1564, 710, 1648,
    text=(
        "धारा पलक शाह | वियेता आलाप शाह | स्वीटी कृणाल चोकसी (पत्नी)\n"
        "पलक निलेशभाई शाह | आलाप कीर्तिभाई शाह | सारा कृणाल चोकसी (पुत्री)\n"
        "(बहन-बहनोई) | (बहन-बहनोई) | क्लारा कृणाल चोकसी (पुत्री)"
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)

# --- OBITUARY 4: स्व. सीताबा गिरधरलाल पटेल (Cols 1-2: 82..718, 1666..2236) ---
draw_box(82, 1666, 718, 2236, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(210, 1668, 590, 1712, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    220, 1672, 580, 1708,
    lines=["दुःखद निधन"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_png(306, 1720, 495, 1952, "obit4_sitaba_photo.png")
place_exact_body_column(
    90, 1958, 710, 2036,
    text=(
        "हमारी मातुश्री स्व. सीताबा गिरधरलाल पटेल ता. १८-१०-२०२६ रविवार को\n"
        "देवलोक सिधार गई हैं। दिवंगत की इच्छा अनुसार बैठना तथा लौकिक क्रिया नहीं रखी है।\n"
        "दिवंगत के प्रति आपके स्नेह तथा भावना को हम हृदयपूर्वक स्वीकार करते हैं।"
    ),
    target_lines=3,
    font_style="Bold",
    align="center",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    140, 2040, 660, 2070,
    lines=["शोकाकुल: स्व. गिरधरलाल विठ्ठलदास पटेल"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    92, 2074, 392, 2180,
    text=(
        "मनुभाई गिरधरलाल पटेल\n"
        "दिलीपभाई गिरधरलाल पटेल\n"
        "जितेश मनुभाई पटेल\n"
        "अंकित मनुभाई पटेल"
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
        "समीर दिलीपभाई पटेल\n"
        "रॉय जितेश पटेल\n"
        "वीणाबेन चंदूलाल पटेल\n"
        "हसुमतीबेन दिनेशकुमार पटेल"
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
        "तथा समस्त विठ्ठलदास रणछोड़दास पटेल परिवार",
        "गुलाबपार्क, एस.टी. रोड, सिद्धपुर"
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
        "मौजे-जासपुर\n"
        "डिस्ट्रिक्ट गांधीनगर रजिस्ट्रेशन सब-डिस्ट्रिक्ट कलोल तालुका के मौजे-जासपुर गांव की सीम के ब्लॉक नं. ६८३ वगैरह की गैर-कृषि भूमि पर शिल्पस ग्रीन एग्रो ओनर्स एसोसिएशन (शिल्पग्राम-१) नामक आवासीय प्लॉटों की योजना स्थित है। उसमें सेक्टर नं. १६ में स्थित (ए) निजी सब-प्लॉट नं. १६/जे के ८९२ वर्ग मीटर (७३२ वर्ग मीटर नेट प्लॉट एरिया) तथा (बी) निजी सब-प्लॉट नं. १६/के के ८९२ वर्ग मीटर (७३२ वर्ग मीटर नेट प्लॉट एरिया) रोड-रास्ते तथा कॉमन प्लॉट के अविभाजित हक सहित खुले प्लॉट वाली संपत्ति कल्पन शंकरलाल शाह के स्वतंत्र स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमारे पास टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त"
    ),
    right_text=(
        "संपत्ति में किसी का किसी भी प्रकार का बोझ, चार्ज, लियन, बाना हक, कब्जा हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त संपत्ति में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त संपत्ति का टाइटल क्लीयरेंस संबंधी अभिप्राय प्रमाणपत्र जारी कर देंगे और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=22,
    right_lines=24,
)

place_public_notice_2col(
    82, 3014, 718, 3792,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-५ (नारोल) के तालुका मणिनगर के मौजे गांव ईसनपुर की सीम के सर्वे नं. ४९०/२, ४९१/२ तथा ४९२/२, टी.पी. स्कीम नं. ५५ के फा. प्लॉट नं. ८३/५ (पुराना फा. प्लॉट नं. १५८) की सर्वे नंबर के अनुसार ६३९.८६ वर्ग गज यानी ५३५ वर्ग मीटर भूमि में से सर्वे नंबर के अनुसार ३९३.८६ वर्ग गज यानी ३२९.३१ वर्ग मीटर भूमि तथा उसमें स्थित सेलर, ग्राउंड फ्लोर तथा फर्स्ट फ्लोर के कुल ३९४.६० वर्ग मीटर निर्माण वाली तथा खुली भूमि सहित संपत्ति तथा उस संबंधी अन्य सभी आनुषंगिक हकों सहित आकाश से पाताल तक की संपत्ति हमारे मुवक्किल परमार शैलेशभाई रमणिकभाई ने अपने स्वतंत्र स्वामित्व, कब्जे, भोगवटे की होने का बताकर हम एडवोकेट से उक्त संपत्ति के"
    ),
    right_text=(
        "टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। इसलिए उक्त संपत्ति में किसी भी बैंक, व्यक्ति, संस्था, फर्म, कंपनी आदि का लागभाग, हक, हित, हिस्सा, दावा, अलाखा, लियन या अन्य कोई चार्ज हो तो दिन-७ (सात) में हम एडवोकेट को नीचे बताए पते पर लिखित सबूतों सहित सूचित करें। यदि ऐसा नहीं किया गया तो मियाद समाप्त होने पर हम एडवोकेट उक्त संपत्ति में किसी भी व्यक्ति का लागभाग, हक, हित, हिस्सा नहीं है अथवा यदि हो तो त्याग (वेव) दिया है, ऐसा समझकर उक्त संपत्ति का टाइटल क्लीयरेंस सर्टिफिकेट जारी करेंगे, उसके बाद किसी की आपत्ति नहीं चलेगी।\n"
        "अहमदाबाद। ता. १७/१०/२०२६\n"
        "परेश सुरेशभाई अढीया\n"
        "एडवोकेट एंड नोटरी\n"
        "९०१, मेपल ट्रेड सेंटर, सुरधारा सर्कल के पास, साल हॉस्पिटल रोड, थलतेज, अहमदाबाद-३८००५४।\n"
        "(मो.) ९८९८४५८२०१"
    ),
    left_lines=23,
    right_lines=25,
)

# --- COLS 3-4 PUBLIC NOTICES (4 Notices: y=1082..1684, 1698..2354, 2368..3054, 3076..3792) ---
place_public_notice_2col(
    746, 1082, 1382, 1684,
    left_text=(
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद के सब-डिस्ट्रिक्ट और तालुका बावला के गांव मौजे दुर्गा की सीम के नए सर्वे/ब्लॉक नंबर-२३८ (पुराने सर्वे/ब्लॉक नंबर-९३) की कुल ४१८९५ वर्ग मीटर कृषि भूमि नटवरभाई उकाभाई तथा गोविंदभाई उकाभाई ने अपने पूर्णतः संयुक्त स्वामित्व, कब्जे, भोगवटे की एवं सभी बोझों से मुक्त होने का बताकर हमसे उक्त भूमि के टाइटल क्लीयर और मार्केटेबल होने के प्रमाणपत्र की मांग की है। अतः उक्त भूमि पर यदि किसी का किसी भी प्रकार का लाग-भाग, हक, हित, हिस्सा, दावा या बोझ हो तो वे इस नोटिस के प्रसिद्ध होने से दिन-७ (सात) में हमें उस"
    ),
    right_text=(
        "संबंधी आवश्यक सबूतों सहित लिखित में नीचे दिए पते पर सूचित करें। यदि ऐसा नहीं किया गया तो उक्त भूमि पर अन्य किसी भी व्यक्ति का किसी भी प्रकार का लाग-भाग, हक, हित, हिस्सा, दावा या बोझ नहीं है और यदि हो तो वह त्याग दिया है, ऐसा मानकर हम उक्त भूमि का टाइटल क्लीयरेंस सर्टिफिकेट जारी करेंगे और उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी।\n"
        "तारीख-२०/१०/२०२६\n"
        "कौशिक जी. पटेल\n"
        "(एडवोकेट एंड नोटरी)\n"
        "(बी.एससी., एल.एल.बी.)\n"
        "ऑफिस :- १२, दूसरी मंजिल, जे.बी.आर. आर्केड, आर.के. रॉयल हॉल के बाजू में, साइंस सिटी रोड, सोला, अहमदाबाद-३८००६०।\n"
        "मो.नं. ९८२४६७८७६९"
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    746, 1698, 1382, 2354,
    left_text=(
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-९ (बोपल) तालुका - घाटलोडिया के मौजे - घुमा गांव की सीम के ब्लॉक नं. ७८९ की गैर-कृषि भूमि पर स्थित आरोही प्लॉट्स ओनर्स एसोसिएशन के विभाग-ए के सब प्लॉट नं. ए/८४ की ४०० वर्ग गज यानी ३३४.४६ वर्ग मीटर आवासीय हेतु की गैर-कृषि खुली भूमि रमेशभाई माधवलाल पटेल के स्वतंत्र स्वामित्व और कब्जे-भोगवटे की होने का बताकर उक्त संपत्ति के टाइटल क्लीयर और मार्केटेबल होने के प्रमाणपत्र की हमसे मांग की है। अतः उक्त संपत्ति पर यदि अन्य किसी भी व्यक्ति, बैंक, फर्म या संस्था इत्यादि का किसी भी प्रकार का लाग, भाग, हक, हित, हिस्सा, दावा"
    ),
    right_text=(
        "या अन्य कोई भी बोझ हो तो वे इस सार्वजनिक सूचना के प्रसिद्ध होने से दिन-७ (सात) में हमें उस संबंधी सबूत की प्रमाणित प्रति सहित लिखित सूचना नीचे दिए पते पर रजिस्टर्ड पोस्ट ए.डी. से भेजें। (सबूत के बिना आपत्तियों पर ध्यान नहीं दिया जाएगा) यदि ऐसा नहीं किया गया तो उक्त संपत्ति पर अन्य किसी का किसी भी प्रकार का लाग, भाग, हक, हित, हिस्सा, दावा या बोझ नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर हम उक्त संपत्ति का टाइटल क्लीयरेंस सर्टिफिकेट जारी कर देंगे। कृपया ध्यान दें।\n"
        "ता. १९/१०/२०२६\n"
        "मनोज के. सिधव, एडवोकेट\n"
        "३०१-३०२, एलाइट, शपथ हेक्सा के सामने, सोला ओवरब्रिज के बाजू में, एस.जी. हाईवे, सोला, अहमदाबाद-३८००६०।\n"
        "ऑफिस फोन नं. ०७९-३५८५६३१४"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 2368, 1382, 3054,
    left_text=(
        "मौजे-जासपुर\n"
        "डिस्ट्रिक्ट गांधीनगर रजिस्ट्रेशन सब-डिस्ट्रिक्ट कलोल तालुका के मौजे-जासपुर गांव की सीम के ब्लॉक नं. ६०६/३ वगैरह की गैर-कृषि भूमि पर शिल्पस ग्रीन एग्रो ओनर्स एसोसिएशन (शिल्पग्राम-१) नामक आवासीय प्लॉटों की योजना स्थित है। उसमें स्थित निजी सब-प्लॉट नं. १/जे के २५८९ वर्ग मीटर रोड-रास्ते तथा कॉमन प्लॉट के अविभाजित हक सहित खुले प्लॉट वाली संपत्ति वत्सल सूर्यकांत पटेल के स्वतंत्र स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त संपत्ति में किसी का किसी भी प्रकार का बोझ, चार्ज, लियन, बाना हक,"
    ),
    right_text=(
        "कब्जा हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त संपत्ति में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त संपत्ति का टाइटल क्लीयरेंस संबंधी अभिप्राय प्रमाणपत्र जारी कर देंगे और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    746, 3076, 1382, 3792,
    left_text=(
        "मौजे-वांसजडा (ढे.)\n"
        "डिस्ट्रिक्ट गांधीनगर रजिस्ट्रेशन सब-डिस्ट्रिक्ट कलोल तालुका के मौजे-वांसजडा (ढे.) गांव की सीम के री-सर्वे के अनुसार ब्लॉक नं. १७८ तथा १७९ (पुराने ब्लॉक नं. ७० तथा ७१) वगैरह की गैर-कृषि भूमि पर रोड-रास्ते, कॉमन प्लॉट तथा क्लब हाउस जैसी सुविधाएं रखकर ‘द अदर साइड’ के नाम से योजना प्रस्तुत की गई है। उसमें स्थित प्लॉट/विला नं. सी/२९६ के ३५४ वर्ग मीटर प्लॉट एरिया तथा उसमें स्थित १३२ वर्ग मीटर कार्पेट एरिया के निर्माण वाली संपत्ति शैलेष रमणिकलाल मेहता के स्वतंत्र स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त संपत्ति में किसी का किसी भी प्रकार का बोझ, चार्ज,"
    ),
    right_text=(
        "लियन, बाना हक, कब्जा हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त संपत्ति में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त संपत्ति का टाइटल क्लीयरेंस संबंधी अभिप्राय प्रमाणपत्र जारी कर देंगे और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=21,
    right_lines=23,
)

# --- COLS 5-6 PUBLIC NOTICES (4 Notices: y=1162..1794, 1810..2414, 2434..3090, 3104..3792) ---
place_public_notice_2col(
    1412, 1162, 2052, 1794,
    left_text=(
        "जि-अहमदाबाद ता-घाटलोडिया मौजे-घुमा की सीम के ब्लॉक नं. ६५८ (पुराने सर्वे नं. ५२२/४) - ड्राफ्ट टी.पी. स्कीम नं. ३ (घुमा), फाइनल प्लॉट नं. ११९ की गैर-कृषि भूमि में स्थित \"SPARSH\" के ब्लॉक ‘ए’ के थर्ड फ्लोर, फ्लैट नं. ३०४ के लगभग ८०.०३ वर्ग मीटर (कार्पेट एरिया) तथा उक्त स्कीम की कुल भूमि में से अविभाजित लगभग ३३.३७ वर्ग मीटर वाली संपत्ति के मालिकों बृजपालसिंह भूपतसिंह वाघरोला, दत्ताकुंवरबा बृजपालसिंह वाघरोला, भूपतसिंह वाघरोला, कंचनबेन भूपतसिंह वाघरोला ने उक्त संपत्ति का टाइटल क्लीयर, मार्केटेबल तथा सभी प्रकार के बोझों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। उक्त संपत्ति पर"
    ),
    right_text=(
        "किसी भी बैंक, संस्था या व्यक्ति का किसी भी प्रकार का हक, दावा, हिस्सा, गिरवी, बोझ, लागभाग हो तो इस सार्वजनिक सूचना के प्रसिद्ध होने से दिन-७ (सात) में हमें लिखित सबूतों के साथ नीचे दिए पते पर सूचित करें। यदि ऐसा करने में चूक हुई तो मियाद समाप्त होने पर उक्त संपत्ति पर किसी का किसी भी प्रकार का बोझ, हक, दावा या अधिकार नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर उक्त संपत्ति के संबंध में टाइटल क्लीयरेंस सर्टिफिकेट हम जारी करेंगे और उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी। अहमदाबाद।\n"
        "ता- १९/१०/२०२६\n"
        "सतीश एच. पुजारा\n"
        "(एडवोकेट एंड नोटरी)\n"
        "एफ.एफ./५, हरे-कृष्णा कॉम्प्लेक्स, SBI बैंक के सामने, बोपल, अहमदाबाद।\n"
        "मो.नं. ९०३३०३३८९०"
    ),
    left_lines=19,
    right_lines=21,
)

place_public_notice_2col(
    1412, 1810, 2052, 2414,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट गांधीनगर सब-डिस्ट्रिक्ट दहेगाम के तालुका दहेगाम के मौजे हरसोली की सीम के खाता नं. १५१५ में दर्ज री-सर्वे/ब्लॉक नं. ८७६ (पुराने सर्वे नं. ४९८) की ०-८५-६४ हे.आरे.चो.मी., आकार रु. ४.५० पैसे क्षेत्रफल वाली पुरानी शर्त की कृषि भूमि रमेशभाई रवजीभाई डोबरिया के स्वतंत्र स्वामित्व, कब्जे-भोगवटे की एवं बोझों से मुक्त टाइटल क्लीयर और मार्केटेबल है, ऐसा बताकर उन्होंने हमारे मुवक्किल को बेचने का तय करके हमसे उक्त भूमि के टाइटल क्लीयर और मार्केटेबल होने के अभिप्राय संबंधी सर्टिफिकेट की मांग की है। अतः उक्त भूमि में किसी व्यक्ति या संस्था का"
    ),
    right_text=(
        "किसी भी प्रकार का हक, हित, हिस्सा, दावा, बोझ, आपत्ति हो तो दिन-७ (सात) में प्रमाणित सबूत सहित लिखित में रजि. ए.डी. से सूचित करें (प्रमाणित सबूत के बिना आपत्तियों पर ध्यान नहीं दिया जाएगा) और यदि ऐसा करने में चूक हुई तो किसी व्यक्ति या संस्था का किसी भी प्रकार का हक, हित, हिस्सा, दावा, बोझ, आपत्ति इत्यादि नहीं है और यदि हो तो वह त्याग (वेव) दिया है, ऐसा समझकर टाइटल क्लीयरेंस के अभिप्राय संबंधी सर्टिफिकेट जारी करेंगे, उसके बाद किसी की कोई आपत्ति नहीं चलेगी।\n"
        "दिनेश बी. पटेल, एडवोकेट\n"
        "ऑफिस : ४०३ तथा ४०४, ब्लॉक-सी, फोर्थ फ्लोर, रेवती प्लाजा, भक्ति सर्कल के पास, ऑफ एस.पी. रिंग रोड, न्यू निकोल, अहमदाबाद - ३८००४९।\n"
        "मो. नं. ९८७९० ५७२९०."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    1412, 2434, 2052, 3090,
    left_text=(
        "मौजे - शेरथा\n"
        "डिस्ट्रिक्ट गांधीनगर रजिस्ट्रेशन सब-डिस्ट्रिक्ट गांधीनगर (जोन - १) गांधीनगर तालुका के मौजे - शेरथा गांव की री-सर्वे के अनुसार ब्लॉक नं. ८५८ (पुराने ब्लॉक नं. १५५०) की हे.आरे.चो.मी. ०-९२-७५ कृषि भूमि रमीबेन उर्फ रमीलाबेन पिता भीखाजी एवं पत्नी रजनीकांत ठाकोर तथा लसीबेन उर्फ लीलाबेन पिता भीखाजी एवं पत्नी भोडाजी ठाकोर के संयुक्त स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त भूमि पर किसी का बोझ, चार्ज, काश्तकारी हक, गणोत हक, ईजमेंट राइट्स या अन्य किसी भी प्रकार का कब्जा"
    ),
    right_text=(
        "हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त भूमि में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त भूमि का टाइटल क्लीयरेंस संबंधी अभिप्राय प्रमाणपत्र जारी करेंगे और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    1412, 3104, 2052, 3792,
    left_text=(
        "मौजे - फुलेत्रा\n"
        "डिस्ट्रिक्ट महेसाणा रजिस्ट्रेशन सब-डिस्ट्रिक्ट कडी तालुका के मौजे-फुलेत्रा गांव की सीम के री-सर्वे के अनुसार सर्वे नं. ११९६ (पुराने सर्वे नं. ९९३) की हे.आरे.चो.मी. : ०-२७-६७ में से दक्षिण दिशा की ओर के भाग की हे.आरे.चो.मी. ०-१३-८३.५० कृषि भूमि (१) रबारी शांताबेन विधवा नाथाभाई, (२) रबारी विष्णुभाई नाथाभाई, (३) रबारी विक्रमभाई नाथाभाई, (४) रबारी सीताबेन नाथाभाई के संयुक्त स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त भूमि पर किसी का बोझ, चार्ज, काश्तकारी हक, गणोत हक, ईजमेंट राइट्स या अन्य किसी भी प्रकार का"
    ),
    right_text=(
        "कब्जा हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त भूमि में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त भूमि का टाइटल क्लीयरेंस संबंधी अभिप्राय प्रमाणपत्र जारी करेंगे और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=20,
    right_lines=22,
)

# --- COLS 7-8 PUBLIC NOTICES (5 Notices: y=202..658, 680..1282, 1312..1968, 1988..2850, 2868..3792) ---
place_public_notice_2col(
    2076, 202, 2715, 658,
    left_text=(
        "जिला अहमदाबाद, तालुका दस्क्रोई, मौजे बारेजा की सीम के सर्वे/ब्लॉक नं. ७२१ (प्रमोल्गेशन से पूर्व का पुराना सर्वे/ब्लॉक नं. ११७८) की हे.आरे.चो.मी. २-५४-८७ क्षेत्रफल वाली कृषि योग्य भूमि में से उत्तर दिशा की ओर की हे.आरे.चो.मी. ०-९४-०९ क्षेत्रफल वाली पुरानी शर्त की कृषि भूमि मेहंदीरजा आरिफअली नूरानी के स्वतंत्र स्वामित्व, कब्जे, भोगवटे में होने का बताकर टाइटल क्लीयर सर्टिफिकेट मांगा है, इसलिए उक्त भूमि में अन्य किसी भी"
    ),
    right_text=(
        "व्यक्ति का किसी भी प्रकार का लागभाग, हक, हित, हिस्सा हो तो नीचे दिए पते पर दिन-७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें, उसके बाद किसी की किसी भी प्रकार की आपत्ति या विवाद मान्य नहीं होगा और संबंधित व्यक्ति का लागभाग, हक, हित, हिस्सा त्याग यानी वेव किया गया समझकर टाइटल क्लीयर सर्टिफिकेट दिया जाएगा।\n"
        "नीलेश एन. पटेल, एसोसिएट्स\n"
        "परेशा बी. पटेल (एडवोकेट)\n"
        "५०७, पांचवीं मंजिल, शिवालिक सत्यमेव, एस.पी. रिंग रोड, आंबली, अहमदाबाद। मो. ९०५४६८४१५९"
    ),
    left_lines=14,
    right_lines=16,
)

place_public_notice_2col(
    2076, 680, 2715, 1282,
    left_text=(
        "रजिस्ट्रेशन डिस्ट्रिक्ट गांधीनगर सब-डिस्ट्रिक्ट दहेगाम के तालुका दहेगाम के मौजे हरसोली की सीम के खाता नं. १५१४ में दर्ज री-सर्वे/ब्लॉक नं. ८७९ (पुराने सर्वे नं. ४९३) की ०-६४-६० हे.आरे.चो.मी., आकार रु. ३.२५ पैसे क्षेत्रफल वाली पुरानी शर्त की कृषि भूमि रमेशभाई रवजीभाई डोबरिया के स्वतंत्र स्वामित्व, कब्जे-भोगवटे की एवं बोझों से मुक्त टाइटल क्लीयर और मार्केटेबल है, ऐसा बताकर उन्होंने हमारे मुवक्किल को बेचने का तय करके हमसे उक्त भूमि के टाइटल क्लीयर और मार्केटेबल होने के अभिप्राय संबंधी सर्टिफिकेट की मांग की है। अतः उक्त भूमि में किसी व्यक्ति या संस्था का"
    ),
    right_text=(
        "किसी भी प्रकार का हक, हित, हिस्सा, दावा, बोझ, आपत्ति हो तो दिन-७ (सात) में प्रमाणित सबूत सहित लिखित में रजि. ए.डी. से सूचित करें (प्रमाणित सबूत के बिना आपत्तियों पर ध्यान नहीं दिया जाएगा) और यदि ऐसा करने में चूक हुई तो किसी व्यक्ति या संस्था का किसी भी प्रकार का हक, हित, हिस्सा, दावा, बोझ, आपत्ति इत्यादि नहीं है और यदि हो तो वह त्याग (वेव) दिया है, ऐसा समझकर टाइटल क्लीयरेंस के अभिप्राय संबंधी सर्टिफिकेट जारी करेंगे, उसके बाद किसी की कोई आपत्ति नहीं चलेगी।\n"
        "दिनेश बी. पटेल, एडवोकेट\n"
        "ऑफिस : ४०३ तथा ४०४, ब्लॉक-सी, फोर्थ फ्लोर, रेवती प्लाजा, भक्ति सर्कल के पास, ऑफ एस.पी. रिंग रोड, न्यू निकोल, अहमदाबाद - ३८००४९।\n"
        "मो. नं. ९८७९० ५७२९०."
    ),
    left_lines=18,
    right_lines=20,
)

place_public_notice_2col(
    2076, 1312, 2715, 1968,
    left_text=(
        "मौजे - ल्होर\n"
        "डिस्ट्रिक्ट महेसाणा रजिस्ट्रेशन सब-डिस्ट्रिक्ट कडी तालुका के मौजे - ल्होर गांव की सीम के री-सर्वे के अनुसार सर्वे नं. ७५४ (पुराने सर्वे नं. ४५१) की भूमि को सिटी सर्वे वार्ड : ल्होर (गैर-कृषि) में शामिल कर आवंटित सिटी सर्वे नं. NA754 की ३१६४ वर्ग मीटर गैर-कृषि भूमि दक्षिणी रोमी शैलेष के स्वतंत्र स्वामित्व, कब्जे, भोगवटे की सभी प्रकार के बोझों तथा कानूनी विवादों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस संबंधी अभिप्राय की मांग की है, उक्त भूमि पर किसी का बोझ, चार्ज, बाना हक, डेवलपमेंट हक या अन्य किसी भी प्रकार का कब्जा हक या लागभाग यानी हक-हिस्सा हो तो हमें नीचे दिए पते पर दिन-"
    ),
    right_text=(
        "७ में लिखित सबूत सहित रजि. ए.डी. से सूचित करें और ऐसा न करने पर उक्त भूमि में किसी का किसी भी प्रकार का हक नहीं है और यदि हो तो वह त्याग दिया है, ऐसा समझकर मियाद समाप्त होने पर उक्त भूमि का टाइटल क्लीयरेंस संबंधी अभिप्राय सर्टिफिकेट जारी किया जाएगा और उसके बाद किसी की कोई आपत्ति या विवाद मान्य नहीं होगा।\n"
        "ता. २०-१०-२०२६\n"
        "मनीष कनुभाई पटेल, एडवोकेट,\n"
        "चिराग दशरथभाई पटेल, एडवोकेट,\n"
        "अमित दशरथभाई पटेल, एडवोकेट,\n"
        "हेत शंकरभाई पटेल, एडवोकेट,\n"
        "BALCHANDBHAI ASSOCIATES\n"
        "पता: ए/२०२, सेकंड फ्लोर, एस.जी. बिजनेस हब, गोता ओवरब्रिज के पास, एस.जी. हाईवे, गोता, अहमदाबाद।\n"
        "मो. ८८७९३४४३३३"
    ),
    left_lines=20,
    right_lines=22,
)

place_public_notice_2col(
    2076, 1988, 2715, 2850,
    left_text=(
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि डिस्ट्रिक्ट अहमदाबाद रजिस्ट्रेशन सब-डिस्ट्रिक्ट तथा तालुका बावला के गांव मौजे रजोडा की सीम के सर्वे नंबर-६७१ (पुराने सर्वे/ब्लॉक नंबर-८७७/२ पैकी) के क्षेत्रफल-१६२९४ वर्ग मीटर में से क्षेत्रफल-५३० वर्ग मीटर ने.हा. नंबर-८-ए में संपादित होने के बाद शेष क्षेत्रफल-१५७६४ वर्ग मीटर गैर-कृषि अनुमति वाली भूमि, शिल्पाबेन राकेशभाई शाह, निवासी : २०, ‘पारस’, विद्यानगर सोसायटी, उस्मानपुरा, अहमदाबाद ने अपने पूर्ण स्वतंत्र स्वामित्व, प्रत्यक्ष कब्जे-भोगवटे में तथा सभी प्रकार के बोझों से मुक्त होने का बताकर हमारे मुवक्किल को बेचने का तय कर हमसे उपरोक्त भूमि के टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। अतः सभी व्यक्ति, फर्म, बैंक, वित्तीय संस्था या अन्य कोई भी जो विक्रय, विरासत, उपहार, लाइसेंस, कब्जा, गिरवी, लियन, चार्ज, भरण-पोषण, ईजमेंट, विनिमय, डेवलपर या फाइनेंसर के रूप में या"
    ),
    right_text=(
        "बानाखत करार, पावर ऑफ अटॉर्नी, कब्जा करार, समझौता करार, डिक्री या अन्य किसी लेख के तहत या कोर्ट कार्यवाही के तहत या परिवार के सदस्य या वारिस के रूप में या किसी भी अन्य प्रकार से उपरोक्त भूमि पर हक, दावा या अधिकार रखते हों, वे इसकी लिखित सूचना सबूत की प्रमाणित प्रति के साथ इस नोटिस के प्रसिद्ध होने से दिन-७ (सात) के भीतर नीचे दिए पते पर स्पीड पोस्ट से करें। यदि ऐसा नहीं किया गया तो उपरोक्त भूमि में किसी का किसी भी प्रकार का लागभाग, हक, हिस्सा नहीं है और यदि हो तो वह त्याग यानी वेव (WAIVE) किया गया समझकर मियाद समाप्त होने पर टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा तथा हमारे मुवक्किल विक्रय विलेख संबंधी कार्यवाही पूर्ण करेंगे और उसके बाद किसी की कोई आपत्ति नहीं चलेगी।\n"
        "तारीख : १८/१०/२०२६,\n"
        "फाइल नंबर- २४००९\n"
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
        "मौजे: शाहवाडी, तालुका वटवा, जिला अहमदाबाद की सीम के (१) सर्वे/ब्लॉक नंबर: २५५/१ के खाता नंबर: २४१ में समाविष्ट कुल ०-३९-४६ हे.आरे.चो.मी. भूमि वर्तमान में मृदुलाबेन दीपककुमार शेठ के स्वामित्व कब्जे-भोगवटे की (२) सर्वे/ब्लॉक नंबर: २६८ के खाता नंबर: २४३ में समाविष्ट कुल ०-६१-७१ हे.आरे.चो.मी. भूमि वर्तमान में कीर्तिकुमार उर्फ किरीटभाई जमनादास शेठ के स्वामित्व कब्जे-भोगवटे की तथा (३) सर्वे/ब्लॉक नंबर: २७७ के खाता नंबर: २४२ में समाविष्ट कुल ०-४२-४९ हे.आरे.चो.मी. भूमि वर्तमान में दीपककुमार जमनादास शेठ के स्वामित्व कब्जे-भोगवटे की तथा (४) सर्वे/ब्लॉक नंबर: २७८/१ के खाता नंबर: १७० में समाविष्ट कुल ०-२०-२३ हे.आरे.चो.मी. की समग्र भूमि में से ८२५ वर्ग मीटर भूमि वर्तमान में राजेश्रीबेन कीर्तिकुमार शेठ के स्वामित्व कब्जे-भोगवटे की मिलाकर कुल १-५१-९१ हे.आरे.चो.मी. भूमि जिसका टी.पी. स्कीम नंबर: १२५ (सैजपुर-गोपालपुर-शाहवाडी) में आवंटित संयुक्त फा. प्लॉट नंबर: ७७/१+८६+९३+९४ की समग्र भूमि"
    ),
    right_text=(
        "में से मिलने योग्य गैर-कृषि भूमि पर अन्य किसी के स्वामित्व हक, हिस्से, विरासत लागभाग या बोझ से मुक्त होने का बताकर हमारे मुवक्किल को बेचने के हेतु से उक्त सभी भूमियों के टाइटल क्लीयर होने के संबंध में अभिप्राय की मांग हमसे की है। उक्त सभी भूमियों या किसी भी भूमि पर किसी का किसी भी प्रकार का विरासत हक, हिस्सा, दावा, बोझ, बानाखत हक, लियन या अटैचमेंट या लागभाग हो तो इस नोटिस के प्रसिद्ध होने से दिन ७ (सात) में उसकी सच्ची प्रतियों वाले दस्तावेजी सबूत सहित लिखित सूचना हमें नीचे दिए पते पर करें अन्यथा उक्त भूमि पर ऐसे हक, हिस्से, बोझ या लागभाग उन्होंने स्वेच्छा से त्याग (वेव) दिए हैं, ऐसा समझकर मियाद समाप्त होने पर टाइटल सर्टिफिकेट दिया जाएगा तथा विक्रय विलेख की कार्यवाही पूर्ण करा ली जाएगी।\n"
        "तारीख: २०/१०/२०२६\n"
        "निमिष वी. देसाई, एडवोकेट,\n"
        "V.D. DESAI & CO.\n"
        "२१२, ‘आकाशरथ’ दूसरी मंजिल, नेशनल हैंडलूम के सामने, लॉ गार्डन, अहमदाबाद\n"
        "फोन: (मो) ९९९८२ १७३५४"
    ),
    left_lines=27,
    right_lines=29,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_06_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_06_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_06_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_06_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_06_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
