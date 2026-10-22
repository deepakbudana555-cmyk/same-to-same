from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 7 BUILDER FOR AAS-PAAS (HINDI GUJARAT SAMACHAR)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  across all 5 Business News stories (Edible Oil Imports, Sugar MSP, IT Mutual
  Funds, Jio Platforms IPO, Global Urea Prices)!
- Graphics/Ads (PNG): 3 Story Photos/Charts and Honda Bottom Half-Page Ad.
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 07 (100% Same-to-Same Editable Hindi)"
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
print("Placing Page 7 Hindi Running Header...")
build_hindi_running_header(7, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: EDIBLE OIL IMPORTS (COLS 1-5 TOP)
# ==============================================================================
print("Building Story 1 (Edible Oil Imports, Cols 1-5 Top)...")
place_exact_display_lines(
    82, 200, 1718, 340,
    lines=["खाद्य तेल के आयात में ३.७%, कीमत में ११% की वृद्धि"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.82,
)
place_exact_body_column(
    82, 346, 1050, 434,
    text="अहमदाबाद, ता. १९\nत्योहारों के मौसम की मांग को पूरा करने के लिए खाद्य तेल व्यापारियों ने उल्लेखनीय मात्रा में खाद्य तेल का आयात किया था। नवंबर-सितंबर २०२५-२६ के दौरान भारत का खाद्य तेल आयात ३.२७% बढ़कर",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1064, 348, 1064, 432, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 346, 1718, 434,
    text="१५.१६४ मिलियन टन हो गया, जो एक वर्ष पूर्व १४.६८३ मिलियन टन था। इस आयात में पाम तेल का हिस्सा सबसे बड़ा रहा। सितंबर में प्रमुख खाद्य तेलों के दामों में पिछले वर्ष की तुलना में ९.७ से ११.२% की वृद्धि हुई है। डॉलर के मुकाबले रुपये का कमजोर होना इसका मुख्य कारण था।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 438, 1718, 496,
    lines=["कमजोर रुपये के कारण खाद्य तेल के दामों में उछाल : आयात में पाम तेल का हिस्सा सबसे बड़ा"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 504, 386, 1018,
    text="क्रूड पाम तेल की अधिक आवक के कारण पाम तेल का आयात ५.३२% बढ़कर ७.३५२ मिलियन टन हो गया है। सोयाबीन तेल का आयात ३.२५% बढ़कर ५.१७६ मिलियन टन, जबकि सूरजमुखी तेल का आयात १.९०% घटकर २.६२४ मिलियन टन रहा। रिफाइंड खाद्य तेल का आयात घटकर ०.७४ मिलियन टन, जबकि क्रूड तेल का आयात बढ़कर १४.४२३ मिलियन टन हो गया।\nरिफाइंड तेल की तुलना में क्रूड तेल के आयात में बड़ा बदलाव देखा गया है। रिफाइंड खाद्य तेल का आयात १.६८९ मिलियन टन से घटकर ०.७४ मिलियन टन रह गया, जिससे कुल आयात में इसका हिस्सा १२% से घटकर ५% रह गया।",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 504, 400, 1018, swatch="[Black]", weight_pt=0.75)
place_png(414, 504, 1050, 926, "edible_oil_photo.png")
place_exact_body_column(
    414, 932, 718, 1018,
    text="क्रूड खाद्य तेल का आयात १२.९९३ मिलियन टन से बढ़कर १४.४२३ मिलियन टन हो गया। यह मुख्य रूप से इसलिए",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(732, 934, 732, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 932, 1050, 1018,
    text="था क्योंकि रिफाइंड पामोलिन आयात के स्थान पर क्रूड पाम तेल का आयात बढ़ा।\nअर्जेंटीना भारत में खाद्य तेल का",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(1064, 504, 1064, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 504, 1382, 1018,
    text="सबसे बड़ा आपूर्तिकर्ता रहा है। उसने कुल ३.४४३ मिलियन टन खाद्य तेल का निर्यात किया है, जिसमें २.७१४ मिलियन टन क्रूड सोयाबीन तेल और ७.२९ लाख टन सूरजमुखी तेल शामिल है।\nमलेशिया ने २.८७६ मिलियन टन पाम तेल उपलब्ध कराया, जबकि इंडोनेशिया ने २.९०५ मिलियन टन निर्यात किया। नेपाल ने भी भारत को ६.८२ लाख टन रिफाइंड तेल का निर्यात किया, जिसमें ६.०५ लाख टन रिफाइंड सोयाबीन तेल शामिल है। नेपाल ने शून्य आयात शुल्क का लाभ उठाया।\nपिछले वर्ष की तुलना में सितंबर २०२६ में खाद्य तेल के दामों में",
    target_lines=17,
    first_indent_pt=0.0,
)
draw_line(1396, 504, 1396, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 504, 1718, 1018,
    text="उल्लेखनीय वृद्धि हुई थी। अंतरराष्ट्रीय कीमतों में तेजी और रुपये का अवमूल्यन इसके पीछे मुख्य कारण थे। कमजोर रुपये के कारण खाद्य तेल के दामों में वृद्धि हुई।\nजानकारों के अनुसार, इस दौरान रुपया अमेरिकी डॉलर के मुकाबले रु. ८८.३२ से रु. ९५.५१ पर कमजोर हुआ, जो लगभग ८.१% गिरा। इससे आयातित तेल की लागत और बढ़ गई। उच्च आयात मात्रा, अंतरराष्ट्रीय कीमतों में तेजी और गिरते रुपये के कारण भारत के लिए खाद्य तेल आयात का खर्च बढ़ रहा है। साथ ही क्रूड तेल की ओर झुकाव से सोर्सिंग के तरीके भी बदल रहे हैं।",
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
        "चीनी का MSP रु. ३१ से बढ़ाकर",
        "रु. ५० करने की मांग तेज हुई"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    82, 1224, 556, 1344,
    text="अहमदाबाद, ता. १९\nमहाराष्ट्र में चीनी मिल मजदूरों ने किसानों की मांगों के समर्थन में २२ तारीख से अनिश्चितकालीन हड़ताल की चेतावनी दी है। किसानों और मजदूरों दोनों की प्रमुख मांग चीनी के न्यूनतम बिक्री मूल्य (MSP) में वृद्धि करने की है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 1226, 564, 1342, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 1224, 1050, 1344,
    text="किसानों का कहना है कि चीनी मिलों की कमजोर आर्थिक स्थिति के कारण उन्हें गन्ने का समय पर भुगतान नहीं मिल पाता है। उनका मानना है कि चीनी का न्यूनतम बिक्री मूल्य रु. ५० प्रति किलो करने से चीनी उद्योग और गन्ना किसानों को राहत मिलेगी। साथ ही उपभोक्ताओं पर भी खास असर नहीं पड़ेगा।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1350, 1050, 1468,
    lines=[
        "चीनी का न्यूनतम बिक्री मूल्य सात वर्षों से प्रति किलो रु. ३१",
        "पर अटका हुआ है, जबकि गन्ने का FRP लगातार बढ़ रहा है"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1474, 386, 1995,
    text="किसान चीनी के न्यूनतम बिक्री मूल्य को वर्तमान रु. ३१ प्रति किलो से बढ़ाकर रु. ५० प्रति किलो करने की मांग कर रहे हैं। वे एथेनॉल के खरीद मूल्य को भी रु. ५८ से बढ़ाकर रु. ७० प्रति लीटर करने की मांग कर रहे हैं।\nपिछले सात वर्षों में गन्ने के उचित एवं लाभकारी मूल्य (FRP) में २६ प्रतिशत से अधिक की वृद्धि हुई है, लेकिन चीनी के न्यूनतम बिक्री मूल्य में केवल एक ही बार संशोधन किया गया है। फरवरी २०१९ के बाद से चीनी का न्यूनतम बिक्री मूल्य नहीं बढ़ा है और यह ३१ रुपये प्रति किलो पर स्थिर बना हुआ है।",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 1476, 400, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 1474, 718, 1995,
    text="चीनी उद्योग का सबसे बड़ा खर्च गन्ने की खरीद पर होता है। २०२०-२१ में गन्ने का उचित एवं लाभकारी मूल्य २,८५० रुपये प्रति टन था, जिसे २०२६-२७ के पेराई सीजन के लिए बढ़ाकर ३,६५० रुपये प्रति टन कर दिया गया है। इसके विपरीत, फरवरी २०१९ से चीनी का न्यूनतम बिक्री मूल्य प्रति क्विंटल रु. ३,१०० पर स्थिर रहा है।\nउत्पादन लागत और अन्य खर्चों में लगातार वृद्धि को देखते हुए चीनी उद्योग लंबे समय से न्यूनतम बिक्री मूल्य में बढ़ोतरी की मांग कर रहा है। चीनी उद्योग के मजदूर २२ तारीख से अनिश्चितकालीन हड़ताल पर जाने की",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(732, 1476, 732, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 1474, 1050, 1995,
    text="तैयारी कर रहे हैं।\nमहाराष्ट्र में चीनी उद्योग के कर्मचारियों ने २२ तारीख से अनिश्चितकालीन हड़ताल पर जाने की चेतावनी दी है, जिसमें चीनी का न्यूनतम बिक्री मूल्य प्रति किलो रु. ५० करना शामिल है। उनका कहना है कि न्यूनतम बिक्री मूल्य बढ़ाने से राज्य की चीनी मिलों की वित्तीय स्थिति में सुधार होगा।\nउद्योग सूत्रों ने बताया कि केंद्र सरकार ने पिछले सात वर्षों से चीनी के न्यूनतम बिक्री मूल्य में वृद्धि नहीं की है। परिणामस्वरूप, बैंक चीनी के स्टॉक के बदले गारंटी पर चीनी मिलों को ऋण देते समय सतर्कता बरतते हैं।",
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
        "सितंबर तिमाही में IT कंपनियों में",
        "म्यू. फंडों की होल्डिंग्स निचले स्तर पर"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1078, 1192, 1718, 1318,
    text="मुंबई, ता. १९\nआर्टिफिशियल इंटेलिजेंस (एआई) से जुड़ी चिंता, वैश्विक ग्राहकों द्वारा कमजोर खर्च तथा विकास पर प्रतिकूल असर के परिणामस्वरूप चालू वित्त वर्ष की सितंबर तिमाही में आईटी कंपनियों में म्यूचुअल फंडों की होल्डिंग्स ऑल-टाइम निचले स्तर पर पहुंच गई है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 1324, 1718, 1435,
    lines=[
        "फंडों की सूची में पहले अग्रणी रहने वाली",
        "आईटी कंपनियां अब निचले पायदान पर"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_png(1078, 1455, 1382, 1585, "it_funds_chart.png")
place_exact_body_column(
    1078, 1592, 1382, 1995,
    text="आईटी क्षेत्र पर दबाव के परिणामस्वरूप इंफोसिस तथा टीसीएस जैसी शीर्ष आईटी कंपनियां, जो एक समय फंडों की सूची में सबसे आगे रहती थीं, अब शीर्ष सूची से बाहर हो गई हैं।\n२०२५ के अंत में फंडों के इक्विटी एसेट अंडर मैनेजमेंट (एयूएम) में आईटी शेयरों का हिस्सा जो ७.६० प्रतिशत था, वह सितंबर तिमाही के अंत में घटकर ५.३० प्रतिशत पर आ गया है।\nआईटी शेयरों में मौजूदा करेक्शन के लिए डी-रेटिंग जिम्मेदार है न कि उनकी आय में गिरावट, ऐसा एक रिसर्च फर्म की",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1396, 1442, 1396, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1442, 1718, 1995,
    text="रिपोर्ट में बताया गया है।\nदिसंबर २०२५ के अंत में फंडों के पास मौजूद आईटी शेयरों का कुल मूल्य जो ३.८८ लाख करोड़ रुपये रहा था, वह सितंबर तिमाही में घटकर २.९७ लाख करोड़ रुपये रह गया। नवंबर २०२५ में यह मूल्य ४.०३ लाख करोड़ रुपये के रिकॉर्ड स्तर पर रहा था।\n२०२६ के प्रारंभ में म्यूचुअल फंडों की शीर्ष पांच होल्डिंग्स में इंफोसिस शामिल थी, जो सितंबर में फिसलकर १०वें स्थान पर पहुंच गई है। ऐसी ही स्थिति टीसीएस तथा अन्य आईटी कंपनियों के शेयरों में देखने को मिली है।\nएआई के कारण आईटी क्षेत्र पर प्रतिकूल असर पड़ेगा, इस आकलन से फंड मैनेजर आईटी क्षेत्र से पीछे हट रहे हैं, ऐसा भी रिपोर्ट में बताया गया है।",
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
    lines=["प्रति शेयर रु.१०६५ से रु.१११९ प्राइस बैंड तय किया गया"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1754, 260, 2705, 452,
    lines=[
        "जियो प्लेटफॉर्म्स का रु.३०,२१३ करोड़ का",
        "IPO भारत में रिकॉर्ड रचने की तैयारी में"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 460, 2056, 954,
    text="मुंबई, ता. १५\nरिलायंस इंडस्ट्रीज की डिजिटल और टेलीकॉम कंपनी जियो प्लेटफॉर्म्स लिमिटेड का संपूर्ण फ्रेश २७ करोड़ शेयरों का रु.३०,२१३ करोड़ का आईपीओ (इनिशियल पब्लिक ऑफरिंग) भारतीय शेयर बाजार के इतिहास में सबसे बड़ा आईपीओ बनने की तैयारी में है। कंपनी ने आज आईपीओ के लिए प्रति शेयर रु.१०६५ से रु.१११९ का प्राइस बैंड तय किया है। आईपीओ २१ अक्टूबर को खुलेगा और २३ अक्टूबर २०२६ को बंद होगा। प्राइस बैंड के ऊपरी भाव पर कंपनी का मूल्यांकन लगभग रु.१०.३ लाख करोड़ यानी करीब १०८ अरब डॉलर बैठता है। आईपीओ में न्यूनतम लॉट १२ शेयरों का रखा गया है।\nकंपनी के मैनेजिंग डायरेक्टर आकाश अंबानी ने बताया कि यह पूरा इश्यू फ्रेश शेयरों का है। जियो प्लेटफॉर्म्स कर्ज मुक्त यानी नेट डेट फ्री कंपनी बनने की दिशा में आगे बढ़ रही है। आईपीओ से मिलने वाली राशि का उपयोग",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_box(1758, 960, 2056, 1066, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    1764, 966, 2050, 1060,
    lines=[
        "कंपनी नेट डेट फ्री बनने की दिशा में",
        "आगे बढ़ रही है : आकाश अंबानी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 1072, 2056, 1318,
    text="मुख्य रूप से रिलायंस जियो इन्फोकॉम के कर्ज के भुगतान के लिए किया जाएगा। जियो की भविष्य की वृद्धि के लिए फाइव-जी, आर्टिफिशियल इंटेलिजेंस (एआई), ब्रॉडबैंड और अपनी स्वदेशी टेक्नोलॉजी विकसित करने की रणनीति पर जोर दिया गया है। जियो केवल टेलीकॉम सेवाओं तक सीमित नहीं रहना चाहता। कंपनी ग्राहकों को अधिक डिजिटल सेवाएं देकर प्रति ग्राहक आय बढ़ाना चाहती है।\nचीन के अलावा जियो विश्व का सबसे बड़ा फाइव-जी ग्राहक",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2068, 460, 2068, 1318, swatch="[Black]", weight_pt=0.75)
place_png(2080, 462, 2705, 800, "jio_ipo_photo.png")
place_exact_body_column(
    2080, 806, 2705, 1318,
    text="आधार रखता है। इसके अलावा उन्होंने कहा कि कंपनी अपने संपूर्ण टेक्नोलॉजी सिस्टम्स का उपयोग कर विदेशी टेलीकॉम कंपनियों के साथ साझेदारी करना चाहती है। कंपनी का उद्देश्य टेक्नोलॉजी बेचना नहीं, बल्कि मैनेज्ड सर्विसेज के माध्यम से वैश्विक बाजार में अपना स्थान मजबूत करना है। उन्होंने उम्मीद जताई कि ६जी का व्यावसायिक कार्यान्वयन २०३० के दशक के प्रारंभ में शुरू होगा।\nकंपनी की डायरेक्टर ईशा अंबानी ने बताया कि आईपीओ का मूल्यांकन दीर्घकालिक निवेशकों के लिए आकर्षक बनाने का प्रयास किया गया है। कोटक महिंद्रा बैंक के संस्थापक उदय कोटक ने बताया कि जियो प्लेटफॉर्म्स के आईपीओ का वैल्यूएशन वित्त वर्ष २०२५-२६ की कमाई के आधार पर लगभग ३४ गुना पी/ई बैठता है, जबकि इसके निकटतम प्रतिस्पर्धी का वैल्यूएशन लगभग ४१ गुना है। आईपीओ के शेयर भाव तय करते समय वैश्विक संस्थागत निवेशकों के साथ बैठकों और उनकी प्रतिक्रिया को ध्यान में रखा गया था।",
    target_lines=17,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1754, 1324, 2705, 1440,
    lines=[
        "आईपीओ का वैल्यूएशन दीर्घकालिक निवेशकों",
        "के लिए आकर्षक बनाने का प्रयास : ईशा अंबानी"
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
        "आपूर्ति बढ़ने के साथ यूरिया की",
        "वैश्विक कीमत में उल्लेखनीय गिरावट"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1744, 1636, 2222, 1726,
    text="मुंबई, ता. १९\nआपूर्ति में वृद्धि के चलते यूरिया की आयात लागत मई की तुलना में ६० प्रतिशत तक नीचे आ जाने की जानकारी सरकारी",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 1638, 2229, 1724, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 1636, 2715, 1726,
    text="सूत्रों ने दी है। मई में यूरिया का प्रति टन भाव जो ९४५ डॉलर था, वह फिलहाल घटकर ३९० डॉलर के आसपास आ गया है।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1732, 2715, 1796,
    lines=["देश में खरीफ बुवाई का कार्य समाप्त होने से मांग भी घटी"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1802, 2052, 1995,
    text="सितंबर में यूरिया के अंतरराष्ट्रीय दामों में १५ प्रतिशत की गिरावट दर्ज की गई है, ऐसा उर्वरक मंत्रालय के सूत्रों ने बताया। आयात के स्रोत बढ़ाने के सरकार के प्रयासों के कारण यूरिया का आयात अब ओमान, मलेशिया, वियतनाम, जॉर्जिया, नाइजीरिया, रूस सहित",
    target_lines=7,
    first_indent_pt=9.0,
)
draw_line(2064, 1804, 2064, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1802, 2382, 1995,
    text="विभिन्न देशों से हो रहा है।\nमई में खरीफ सीजन की बुवाई से पहले यूरिया की मांग बढ़ने से कीमतों में तेजी देखी गई थी। हालांकि अब खरीफ सीजन की बुवाई पूरी हो चुकी है और भारत की यूरिया मांग घटने से अंतरराष्ट्रीय दाम नरम पड़े हैं, ऐसा सूत्रों ने आगे",
    target_lines=7,
    first_indent_pt=0.0,
)
draw_line(2395, 1804, 2395, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1802, 2715, 1995,
    text="बताया।\nपिछले वित्त वर्ष में उर्वरक सब्सिडी के मद में २.१७ लाख करोड़ रुपये का खर्च हुआ था, जिसकी तुलना में चालू वर्ष में यह आंकड़ा २०,००० से २२,००० करोड़ रुपये अधिक रहने का अनुमान लगाया जा रहा है।",
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
    pd_path = target_dir / "Page_07_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_07_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_07_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_07_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_07_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
