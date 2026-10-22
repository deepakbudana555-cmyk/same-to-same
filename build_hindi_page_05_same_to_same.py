from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 5 BUILDER FOR AAS-PAAS (GUJARAT SAMACHAR HINDI)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  across all 4 stories & fee table on Page 5!
- Graphics/Ads (PNG): Top Running Header Bar, Indian Bank Right-Half Ad,
  and Vijay Sales Bottom Half-Page Ad.
"""

import json
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
        "title": "Aas-Paas (Hindi Gujarat Samachar) — Page 05 (100% Same-to-Same Editable Hindi)"
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
):
    n_lines = len(lines)
    full_text = "\n".join(lines)
    box_h_pt = p(y2_px - y1_px)
    if font_family_override:
        use_family = font_family_override
        use_style = "Regular" if font_family_override in ("DB Hindi Mast", "DB Madhurima") else font_style
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 18.0:
        use_family = "DB Madhurima"
        use_style = "Regular"
    else:
        use_family = "DB Hindi"
        use_style = font_style

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
                "fontFamily": use_family,
                "fontStyle": use_style,
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
                        "fontFamily": use_family,
                        "fontStyle": use_style,
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
            "fontFamily": use_family,
            "fontStyle": use_style,
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
print("Placing Page 5 Hindi Running Header...")
build_hindi_running_header(5, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: NAVA VADAJ SPORTS CENTER (COLS 1-2 TOP)
# ==============================================================================
print("Building Story 1 (Nava Vadaj Sports Center, Cols 1-2 Top)...")
place_exact_display_lines(
    82, 200, 718, 244,
    lines=["भाजपा के राज में चहेते मालामाल"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 250, 718, 390,
    lines=[
        "नवा वाडज का स्पोर्ट्स सेंटर मात्र पांच",
        "लाख वार्षिक फीस पर किराए पर दे दिया जाएगा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 396, 718, 550,
    text="अहमदाबाद, सोमवार\nनवा वाडज में एसी बैडमिंटन कोर्ट, वॉलीबॉल कोर्ट और बॉक्स क्रिकेट सहित की सुविधाओं के साथ रु. ४.६७ करोड़ की लागत से तैयार हुआ स्पोर्ट्स सेंटर मात्र पांच लाख रुपये की वार्षिक फीस पर किराए पर दे देने की तैयारियां शुरू हुई हैं। खेलकूद की अन्य सुविधाओं की तरह यह सुविधा भी मामूली फीस में किराए पर लेकर चहेते मालामाल बनेंगे।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    82, 556, 718, 650,
    lines=[
        "४.६७ करोड़ की लागत से तैयार हुए स्पोर्ट्स सेंटर में",
        "बैडमिंटन, वॉलीबॉल और बॉक्स क्रिकेट की सुविधा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 656, 224, 945,
    text="अहमदाबाद म्युनि. द्वारा कॉमनवेल्थ गेम्स के नाम पर खेलकूद के लिए अंधाधुंध खर्च शुरू हुआ है। उससे सामान्य नागरिकों को कोई फायदा हो या नहीं, परंतु",
    target_lines=9,
    first_indent_pt=9.0,
)
draw_box(232, 656, 718, 945, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    240, 662, 710, 704,
    lines=["स्पोर्ट्स संकुल के लिए निर्धारित की गई फीस"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
)
place_exact_body_column(
    240, 708, 710, 938,
    text="बैडमिंटन कोर्ट (एसी)  रु. ५०० से ४०००\nवॉलीबॉल कोर्ट  रु. २०० से ३०००\nयोग-मेडिटेशन (एसी)  रु. २०० से २०००\nचेस  रु. १५० से रु. २०००\nकैरम  रु. १००\nलाइब्रेरी (एसी)  रु. ३००\nबॉक्स क्रिकेट  रु. ७०० से १२००",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    82, 952, 392, 1188,
    text="सत्ताधीशों के चहेते जरूर पैसे वाले बन जाएंगे। क्योंकि शहर में करोड़ों रुपये की लागत से खड़ी की गई खेलकूद की सुविधाएं मामूली दर पर संचालन के लिए किराए पर दी जा रही हैं।\nऊपर से जनता के पैसे से तैयार हुई इन सुविधाओं का उपयोग करने के लिए दरें कमर्शियल इकाइयों जितनी ही रखी जाती हैं! जिसमें अब नवा वाडज स्पोर्ट्स",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_line(400, 954, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 952, 718, 1188,
    text="सेंटर जुड़ने जा रहा है। यह स्पोर्ट्स सेंटर बच्चों और युवाओं को खेलकूद का लाभ मिले ऐसा है। परंतु उसकी फीस की दरें इतनी भारी-भरकम तय की गई हैं कि मध्यम और गरीब वर्ग वहन नहीं कर सकता। इतनी ऊंची फीस की दरों के बावजूद पूरे सेंटर का वार्षिक किराया मात्र पांच लाख रुपये ही तय किया गया है!",
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
    lines=["पसीने की कमाई के बिना त्योहार सूने गए"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 1250, 718, 1390,
    lines=[
        "मनरेगा मजदूरों-सुपरवाइजरों को",
        "अभी रु. ३.४३ करोड़ का भुगतान नहीं"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1396, 392, 1988,
    text="अहमदाबाद, सोमवार\nगुजरात में कड़ी मजदूरी करके पेट भरने वाले गरीब श्रमिकों को अपने हक के पैसों के लिए भटकना पड़ रहा है। गरीब श्रमिकों को रोजगार देने वाली योजना मनरेगा में काम करने वाले श्रमिकों को २० जून २०२६ से आज तक वेतन का भुगतान नहीं किया गया है। कानून के अनुसार काम पूरा होने के १५ दिन में पैसे सीधे खाते में जमा होने चाहिए, परंतु प्रशासनिक तंत्र की लापरवाही के कारण नवरात्रि और दशहरा जैसे त्योहार भी इन गरीब परिवारों के लिए सूने रहे हैं।\nकेवल भावनगर जिले में ही श्रमिकों का २.६९ करोड़ रुपये बकाया है। इसके अलावा, योजना का संचालन करने वाले मनरेगा सुपरवाइजरों को भी १.४४ करोड़ रुपये का भुगतान नहीं किया गया है। इस प्रकार कुल मिलाकर करोड़ों रुपये प्रशासनिक तंत्र की फाइलों में",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(400, 1398, 400, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    408, 1396, 718, 1988,
    text="अटके पड़े हैं। चिलचिलाती धूप में और कड़ी मजदूरी करके खून-पसीना एक करने वाले श्रमिकों के घर में इस समय चूल्हा जलाना भी मुश्किल बना है। गुजरात में कुल मिलाकर मनरेगा के मजदूरों को अभी ४३ करोड़ का भुगतान नहीं किया गया है।\nयूपीए सरकार द्वारा ग्रामीण क्षेत्र के गरीबों को रोजगार की गारंटी देने के लिए मनरेगा कानून लाया गया था। इस कानून के अंतर्गत स्पष्ट प्रावधान है कि श्रमिक द्वारा किए गए काम का मेहनताना १५ ही दिन में चुका देना पड़ता है। यदि इस समयावधि में भुगतान न हो, तो श्रमिक मुआवजा पाने के हकदार बनते हैं। परंतु भाजपा सरकार के राज में नियम केवल कागज पर ही रह गए हों ऐसा स्पष्ट दिखाई दे रहा है। सरकार गरीब श्रमिकों को मेहनताना चुकाने में भी अनदेखी कर रही है।",
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
    lines=["आज ‘ऑस्टियोपोरोसिस दिवस’ है तब"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 250, 1382, 390,
    lines=[
        "हर ३ में से एक वयस्क महिला को",
        "हड्डियां कमजोर पड़ने की समस्या"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 396, 1382, 550,
    text="अहमदाबाद, सोमवार\nऑस्टियोपोरोसिस ऐसा रोग है जिसमें हड्डियां अंदर से खोखली और कमजोर पड़ जाती हैं। साइलेंट किलर माने जाने वाले ऑस्टियोपोरोसिस में प्रारंभ में कोई लक्षण दिखाई नहीं देते। ५० वर्ष से अधिक आयु की हर ३ में से १ महिला और हर पांच में से १ पुरुष को ऑस्टियोपोरोसिस की समस्या है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 556, 1382, 650,
    lines=[
        "घर में रहने की आदत के कारण शहरी क्षेत्र में",
        "७० प्रतिशत से अधिक लोगों में विटामिन डी की कमी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 656, 1056, 1125,
    text="हर वर्ष २० अक्टूबर को ‘ऑस्टियोपोरोसिस डे’ के रूप में मनाया जाता है। चिकित्सकों के मत में शहरी क्षेत्र में बदलती जीवनशैली और घर में रहने की आदत के कारण ७० से ८० प्रतिशत लोगों में विटामिन डी की कमी देखी जाती है। हड्डियों के स्वास्थ्य पर ध्यान देने के लिए फ्रैक्चर होने तक राह नहीं देखनी चाहिए। हड्डियों से संबंधित समस्या को वृद्धावस्था का सामान्य भाग मानकर नजरअंदाज करना भूलभरा है। कई लोग मानते हैं कि ऑस्टियोपोरोसिस और कमजोर हड्डियों की समस्या केवल वृद्धावस्था में ही होती है। परंतु जीवनभर की हमारी आदतें",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(1064, 658, 1064, 1125, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 656, 1382, 1125,
    text="हड्डियों के स्वास्थ्य को प्रभावित करती हैं। एक सर्वेक्षण के अनुसार गुजरात में ४० से ८० के आयु वर्ग में २२ प्रतिशत हिप फ्रैक्चर, २४ प्रतिशत मेजर ऑस्टियोपोरोसिस फ्रैक्चर के उपचार-जोखिम की श्रेणी में थे। पर्याप्त मात्रा में कैल्शियम युक्त संतुलित आहार लेना चाहिए ऐसा बताते हुए डॉ. जतिन वखारिया ने जोड़ा कि विटामिन डी का उचित स्तर, नियमित व्यायाम हड्डियों की मजबूती बनाए रखने में मदद करता है। मेनोपॉज के बाद महिलाओं, वृद्धों और पहले फ्रैक्चर हुआ हो ऐसे जोखिम कारक रखने वाले लोगों को हड्डियों के स्वास्थ्य की जांच के संबंध में चिकित्सीय मार्गदर्शन लेना चाहिए।’",
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
    lines=["बापूनगर में सोनारिया ब्लॉक के पास से"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1190, 1382, 1330,
    lines=[
        "२४ लाख की हेरोइन के साथ दो",
        "पकड़े गए: सड़क पर बिक्री!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1336, 1382, 1465,
    text="अहमदाबाद, सोमवार\nअहमदाबाद में अब खुलेआम सड़क पर बेरोकटोक हेरोइन की बिक्री हो रही होने का पर्दाफाश बापूनगर पुलिस द्वारा दो व्यक्तियों को २४ लाख की हेरोइन के साथ पकड़ लेने से हुआ है। राजस्थान से हेरोइन लाकर गुजरात में बिक्री करने वाली महिला सहित पांच के खिलाफ मामला दर्ज हुआ है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1472, 1382, 1568,
    lines=[
        "राजस्थान में व्हाट्स-एप से संपर्क कर हेरोइन",
        "देने वाले के अलावा महिला सहित पांच आरोपी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1574, 1056, 1988,
    text="बापूनगर पुलिस की टीम ने मुखबिर की सूचना के आधार पर बापूनगर में सोनारिया ब्लॉक के पास सड़क पर बर्गमैन टू-व्हीलर पर बैठकर हेरोइन की बिक्री करते दो व्यक्तियों को पकड़ लिया था। सोनारिया ब्लॉक में ही रहने वाले रोहित भैरोसिंग राजपूत के पास से १०.७७ लाख की कीमत की ५३.८९० ग्राम तथा आनंद सोमाभाई प्रजापति के पास से १४ लाख की कीमत की ७०.२२ ग्राम हेरोइन जब्त की गई थी। दोनों आरोपियों ने कबूल किया था कि सोनारिया ब्लॉक में ही रहने वाले नानू उर्फ भावेश नटवरभाई पटणी और टीनाबहन पप्पूभाई पटणी के कहने पर",
    target_lines=14,
    first_indent_pt=9.0,
)
draw_line(1064, 1576, 1064, 1988, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1072, 1574, 1382, 1988,
    text="राजस्थान के सांचोर जाकर एक व्हाट्स-एप नंबर पर संपर्क करके हेरोइन लाए थे। पहले छह से सात बार हेरोइन लाकर बिक्री कर चुके दोनों आरोपियों को राजस्थान जाकर हेरोइन लाने के लिए रु. १०,००० दिए जाते थे। जबकि, खुदरा बिक्री करने पर भी पैसे दिए जाते थे। बापूनगर पुलिस ने कुल २४.८२ लाख की १२४.१११ ग्राम हेरोइन के साथ दो आरोपियों को पकड़कर हेरोइन बिक्री का काम सौंपने वाली महिला टीनाबहन, नानू पटणी के अलावा राजस्थान में हेरोइन देने वाले अज्ञात व्यक्ति को पकड़ने के लिए कार्रवाई शुरू की है।",
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
    pd_path = target_dir / "Page_05_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_05_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_05_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_05_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_05_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
