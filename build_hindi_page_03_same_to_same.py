from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 3 BUILDER ('आस-पास' — हिंदी गुजरात समाचार)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi' Bold/Regular)
- Graphics/Ads (PNG): Top Running Header Bar, Kalamandir & Aakar Ad, Lokmanya College Ad,
  TBZ Half-Right Ad, and Bajaj Pulsar Bottom Half-Page Ad.
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
ASSETS_DIR = DIR_SMAE / "Page_03_Assets"

LIVE_DRAW = "--fast" not in sys.argv
FRAME_DELAY = 0.08 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.14 if LIVE_DRAW else 0.0
LINE_DELAY = 0.04 if LIVE_DRAW else 0.0

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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 03 (100% Same-to-Same Editable Hindi)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.25)


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

    if font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 18.0:
        ffam = "DB Madhurima"
        fsty = "Regular"
    else:
        ffam = "DB Hindi"
        fsty = font_style

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
                "fontFamily": ffam,
                "fontStyle": fsty,
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
                        "fontFamily": ffam,
                        "fontStyle": fsty,
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
            "fontFamily": ffam,
            "fontStyle": fsty,
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
    default_hscale: float = 0.90,
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

    best_cfg = (9.6, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.06:
            continue
        for hs100 in (96, 92, 88, 84, 80, 76):
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
# 1. PLACE RUNNING HEADER & ADVERTISEMENTS (PNG)
# ==============================================================================
print("Placing Page 3 Hindi Running Header & Advertisements...")
build_hindi_running_header(3, place_png, draw_box, place_exact_display_lines)

# Story 1: Cols 1-3 (Online Courses Internship & Training Policy)
print("Building Story 1 (Online Courses Internship Policy, Cols 1-3)...")
place_exact_display_lines(
    82, 200, 1050, 244,
    lines=["गुजरात में सर्वप्रथम गुजरात विवि द्वारा शुरू किए गए"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
    target_hscale=0.88,
)
place_exact_display_lines(
    82, 250, 1050, 412,
    lines=[
        "ऑनलाइन कोर्सेज में इंटर्नशिप और",
        "ट्रेनिंग के लिए नई पॉलिसी तय होगी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
)
place_exact_body_column(
    82, 418, 398, 594,
    text="अहमदाबाद, सोमवार\nगुजरात में प्रथम ऐसे गुजरात विश्वविद्यालय द्वारा शुरू किए गए ऑनलाइन कोर्स में नई शिक्षा नीति के प्रावधान के अनुसार अनिवार्य इंटर्नशिप और ऑन-जॉब ट्रेनिंग किस प्रकार कराई जाए, इसके लिए नई पॉलिसी तय की जाएगी। क्योंकि फिलहाल तो",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(406, 420, 406, 592, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 418, 1050, 594,
    text="राज्य के सभी विश्वविद्यालयों में ऑफलाइन रेगुलर कोर्स चलते हैं और उनमें विद्यार्थियों ने पांचवें सेमेस्टर में ऑफलाइन इंटर्नशिप ही की थी। परंतु ऑनलाइन कोर्स में ऑफलाइन-फिजिकल इंटर्नशिप-ट्रेनिंग संभव नहीं है, इसलिए ऑनलाइन इंटर्नशिप कहां और कैसे कराई जाए इसके लिए पॉलिसी बनेगी।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 602, 1050, 718,
    lines=[
        "अनिवार्य ट्रेनिंग-इंटर्नशिप रेगुलर कोर्स की तरह फिजिकल",
        "संभव न होने से ऑनलाइन कराने की अनुमति दी जाएगी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 724, 386, 822,
    text="यूजीसी द्वारा गुजरात विश्वविद्यालय को यूजी में तीन और पीजी में कुल छह कोर्स ऑनलाइन",
    target_lines=3,
    first_indent_pt=9.0,
)
draw_line(400, 726, 400, 820, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 724, 718, 822,
    text="शुरू किए थे। गत वर्ष अक्टूबर में पहली बार छह ऑनलाइन कोर्स में प्रवेश दिए गए",
    target_lines=3,
    first_indent_pt=0.0,
)
# Callout Box: BA-BCom Online Demand
draw_box(82, 830, 718, 1158, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    94, 838, 706, 932,
    lines=[
        "BA-BCom में ऑनलाइन कोर्स की डिमांड",
        "बढ़ी : एक ही वर्ष में ५० प्रतिशत प्रवेश बढ़े"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    94, 938, 706, 1150,
    text="गुजरात विवि में कुल छह ऑनलाइन कोर्सेज में ११४३ प्रवेश हुए हैं। विशेषकर बीए-बीकॉम में ऑनलाइन कोर्स की डिमांड बढ़ने से ५० प्रतिशत प्रवेश बढ़े हैं। गत वर्ष अक्टूबर में छह कोर्स में १५४ प्रवेश हुए थे और फरवरी इनटेक में ३४३ तथा उसके बाद इस वर्ष जुलाई में ६४६ प्रवेश हुए थे। कुल ११४३ प्रवेश में बीए में २४३ और बीकॉम में ३०१ प्रवेश हैं। विवि द्वारा अब एमबीए, जर्नलिज्म, एमसीए और लाइब्रेरी साइंस कोर्स भी ऑनलाइन शुरू करने की अनुमति मांगी गई है।",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=10.0,
)
place_exact_body_column(
    82, 1164, 386, 1236,
    text="पढ़ाने की अनुमति मिलने के तीन वर्ष बाद अंततः गत वर्ष विवि ने ये",
    target_lines=2,
    first_indent_pt=0.0,
)
draw_line(400, 1166, 400, 1236, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 1164, 718, 1236,
    text="थे। इनमें बीए अंग्रेजी, बीकॉम जनरल, बीसीए, एमए अंग्रेजी,",
    target_lines=2,
    first_indent_pt=0.0,
)
draw_line(732, 726, 732, 1468, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 724, 1050, 1468,
    text="एमकॉम जनरल और एमएससी मैथ्स शामिल हैं। इन कोर्सेज में गत वर्ष अक्टूबर के बाद फरवरी में दूसरी बार प्रवेश हुए थे और उसके बाद इस वर्ष जुलाई इनटेक के प्रवेश हुए थे। इस प्रकार कुल तीन बार हुए प्रवेश में ११४३ विद्यार्थियों ने प्रवेश लिया है।\nनई शिक्षा नीति में यूजी के विद्यार्थियों को पांचवें सेमेस्टर में करनी पड़ने वाली अनिवार्य इंटर्नशिप इस ऑनलाइन कोर्स पर भी लागू होगी। इसलिए गत वर्ष प्रवेश लेने वाले विद्यार्थी फिलहाल तीसरे सेमेस्टर में हैं परंतु इस वर्ष पांचवें सेमेस्टर में आने वाले १५४ विद्यार्थियों को अनिवार्य इंटर्नशिप और ऑन-जॉब ट्रेनिंग करनी होगी। गुजरात में फिलहाल केवल गुजरात विवि में ही ये ऑनलाइन कोर्सेज चलते हैं, ऐसे में ऑनलाइन कोर्सेज में किस तरह इंटर्नशिप और ऑन-जॉब ट्रेनिंग विद्यार्थियों को कराई जाए इसके लिए विवि द्वारा पॉलिसी तय की जाएगी।",
    target_lines=23,
    first_indent_pt=9.0,
)
draw_line(1064, 198, 1064, 1482, swatch="[Black]", weight_pt=0.75)

# Story 2: Col 4 Top (PSI Non-Bailable Warrant)
print("Building Story 2 (PSI Non-Bailable Warrant, Col 4 Top)...")
place_exact_display_lines(
    1078, 200, 1382, 286,
    lines=[
        "गवाही में लगातार गैरहाजिर PSI",
        "के खिलाफ गैर-जमानती वारंट"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 292, 1382, 745,
    text="अहमदाबाद, सोमवार\nसरकारी काम में बाधा डालने के करीब छह साल पुराने एक मामले में कोर्ट के समक्ष गवाही देने के लिए बार-बार गैरहाजिर रहने वाले निकोल पुलिस थाने के तत्कालीन पीएसआई एस.वी. छासठिया के रवैये को गंभीरता से लेते हुए अहमदाबाद ग्रामीण कोर्ट ने पीएसआई छासठिया के खिलाफ गैर-जमानती वारंट जारी किया था। इसके चलते घबराए पीएसआई ने वारंट रद्द कराने के लिए अर्जी दी जिस पर कोर्ट ने पीएसआई के खिलाफ वारंट तो रद्द कर दिया परंतु सबक के तौर पर रु. एक हजार का जुर्माना लगाने का आदेश दिया।",
    target_lines=14,
    first_indent_pt=9.0,
)
draw_line(1078, 753, 1382, 753, swatch="[Black]", weight_pt=0.85)

# Story 3: Col 4 Bottom (21,000 Cr Narco-Terror Case)
print("Building Story 3 (21,000 Cr Narco-Terror Drugs Case, Col 4 Bottom)...")
place_exact_display_lines(
    1078, 760, 1382, 844,
    lines=[
        "२१ हजार करोड़ के नार्को-टेरर-ड्रग्स",
        "केस में सरबजीत सिंह को जमानत नहीं"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1078, 850, 1382, 1472,
    text="अहमदाबाद, सोमवार\nमुंद्रा पोर्ट से पकड़े गए रु. २१,००० करोड़ के अंतरराष्ट्रीय नार्को-टेरर ड्रग्स घोटाले में शामिल और पंजाब से ४५० ग्राम हेरोइन के साथ रंगेहाथ पकड़े गए आरोपी सरबजीत सिंह उर्फ सेठी की नियमित जमानत अर्जी यहां की स्पेशल एनआईए कोर्ट ने कड़े रुख के साथ खारिज कर दी है। एनआईए कोर्ट ने स्पष्ट किया कि आरोपी के खिलाफ प्रथम दृष्टया मजबूत केस बनता है और उस पर राष्ट्रीय सुरक्षा तथा अंतरराष्ट्रीय ड्रग्स नेटवर्क से जुड़े गंभीर आरोप हैं। अंतरराष्ट्रीय नार्को-टेरर सिंडिकेट के साथ गहरे तार जुड़े होने की बात सामने आने पर आरोपी को जमानत पर रिहा नहीं किया जा सकता। गत १३ सितंबर २०२१ को कच्छ के मुंद्रा पोर्ट पर अफगानिस्तान से ईरान होकर आए सेमी-प्रोसेस्ड टाल्क स्टोन्स के कंटेनरों से २९८८.२१ किलो हेरोइन जब्त की गई थी।",
    target_lines=20,
    first_indent_pt=9.0,
)
draw_line(1395, 198, 1395, 1482, swatch="[Black]", weight_pt=0.75)
draw_line(746, 1482, 1382, 1482, swatch="[Black]", weight_pt=0.85)

# Place Advertisements (Kalamandir/Aakar, Lokmanya, TBZ, Bajaj Pulsar)
place_png(75, 1260, 726, 2005, "ad_kalamandir_aakar.png")
place_png(740, 1490, 1400, 2005, "ad_lokmanya.png")
place_png(1402, 188, 2725, 2005, "ad_tbz_right.png")
place_png(0, 2005, 2800, 3974, "ad_bajaj_pulsar_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_03_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_03_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_03_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_03_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_03_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
