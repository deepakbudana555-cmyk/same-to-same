from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 2 BUILDER ('आस-पास' — हिंदी गुजरात समाचार)
=================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt (37.04 x 52.57 cm)
- Exact same layout, exact same frame positions/sizes, and accurate Hindi translation of Page 2.
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi' Bold/Regular).
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
ASSETS_DIR = DIR_SMAE / "Page_02_Assets"

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


LIVE_DRAW = "--fast" not in sys.argv
FRAME_DELAY = 0.10 if LIVE_DRAW else 0.0
CONTENT_DELAY = 0.18 if LIVE_DRAW else 0.0
LINE_DELAY = 0.05 if LIVE_DRAW else 0.0

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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 02 (100% Same-to-Same Editable Hindi)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCrimsonText", "color": "#d11116"}},
    {"command": "view.fitPage", "params": {}},
])
if LIVE_DRAW:
    time.sleep(0.3)


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
            if st.get("overset") is None:
                lines_got = st.get("lines") or 0
                diff = abs(lines_got - target_lines)
                if lines_got == target_lines:
                    best_cfg = (pt, hs, 0.0)
                    best_diff = 0
                    break
                elif diff < best_diff:
                    best_diff = diff
                    best_cfg = (pt, hs, 0.0)
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
    return fid, sid, pt, hs


# ==============================================================================
# 1. TOP RUNNING HEADER BAR & MAJOR VERTICAL COLUMN DIVIDERS
# ==============================================================================
print("Placing Page 2 Hindi running header & main vertical rules...")
build_hindi_running_header(2, place_png, draw_box, place_exact_display_lines)
draw_line(1068, 200, 1068, 3792, swatch="[Black]", weight_pt=0.9)
draw_line(1732, 200, 1732, 3792, swatch="[Black]", weight_pt=0.9)
place_png(84, 3805, 2718, 3858, "cmyk_footer_bar_p2.png")


# ==============================================================================
# 2. STORY 1: TOP-LEFT 3-COL BOXED FEATURE (JALEBI-FAFDA PRICES)
# ==============================================================================
print("Building Story 1 (Jalebi-Fafda Boxed Feature, Cols 1-3)...")
draw_box(84, 204, 1056, 1390, stroke_swatch="[Black]", stroke_weight_pt=2.2)
place_exact_display_lines(
    96, 216, 1044, 376,
    lines=[
        "दशक भर पहले ४५०-५०० रुपये प्रति किलो",
        "बिकने वाली जलेबी का भाव अब रु. ११५० से १५००"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_png(95, 386, 1044, 1065, "jalebi_fafda_photo.png")
place_exact_body_column(
    96, 1072, 1044, 1378,
    text="फाफड़ा-जलेबी की दावत का आनंद लिए बिना विजयादशमी का उत्सव मानो अधूरा ही माना जाता है। कल विजयादशमी का पर्व है, ऐसे में अहमदाबाद में लगभग १५० करोड़ से २०० करोड़ रुपये के फाफड़ा-जलेबी की बिक्री होगी। अहमदाबाद में फाफड़ा ७५० से ८५० रुपये प्रति किलो जबकि जलेबी ११५० से १५०० रुपये प्रति किलो के भाव से बिक रही है। इसमें प्रीमियम केसर जलेबी का भाव १५०० रुपये है। १५०० रुपये प्रति किलो के भाव पर जलेबी के एक पीस के लिए लगभग ३० रुपये चुकाने पड़ते हैं। वर्ष २०१६ में फाफड़ा ३६० से ४५० रुपये प्रति किलो और जलेबी ४५० से ५०० रुपये प्रति किलो बिकती थी। इन दोनों शीर्ष कीमतों की तुलना करें तो फाफड़ा में लगभग १६७ से २३३ प्रतिशत जबकि जलेबी में लगभग २६४ से ३४४ प्रतिशत की वृद्धि हुई है। कल अधिकांश सोसाइटियों में फाफड़ा-जलेबी का मेनू तय कर दिया गया है। कई लोगों ने टाइम स्लॉट के अनुसार फाफड़ा-जलेबी के ऑर्डर दे दिए हैं। कई सोसाइटियां जहां बड़ी संख्या में गरबा प्रेमी एकत्र होते हैं, वहां नाश्ते के काउंटर किराए पर देकर भी कमाई कर ली गई है।                                                          (तस्वीर : सुरेश मिस्त्री)",
    target_lines=10,
    font_style="Bold",
    first_indent_pt=0.0,
)


# ==============================================================================
# 3. STORY 2: MIDDLE-LEFT 3-COL STORY (VASTRAPUR GANTHIYA / HARMFUL FRYING OIL)
# ==============================================================================
print("Building Story 2 (Vastrapur Ganthiya / Harmful Oil, Cols 1-3)...")
place_exact_display_lines(
    86, 1400, 1052, 1446,
    lines=["वस्त्रापुर गांठिया सील, १५ स्थानों से २४ नमूने लिए गए"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(86, 1451, 1054, 1451, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 1456, 1052, 1640,
    lines=[
        "८०० रुपये किलो के फाफड़ा-जलेबी में",
        "भी हानिकारक जले हुए तेल का उपयोग"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    390, 1644, 554, 1670,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 1672, 554, 1796,
    text="अहमदाबाद शहर में दशहरा पर्व पर लोग हजारों किलो फाफड़ा-जलेबी खा जाते हैं। इस मांग का अनुचित लाभ उठाकर मिलावटखोर तत्व जनस्वास्थ्य के साथ खिलवाड़ करने में कोई कसर नहीं छोड़ते। ऐसे में मनपा के फूड विभाग द्वारा आज",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 1650, 568, 1794, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 1646, 1052, 1796,
    text="पूरे शहर में १५ स्थानों से फाफड़ा-जलेबी के २४ नमूने लेकर जांच के लिए भेजे गए हैं। हालांकि जब तक इनका परिणाम आएगा, तब तक दुकानों के फाफड़ा-जलेबी बिक चुके होंगे! दूसरी ओर खाद्य तेल में टीपीसी की मात्रा अधिक मिलने पर वस्त्रापुर तालाब के सामने स्थित वस्त्रापुर गांठिया को सील कर दिया गया है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 1802, 1052, 1918,
    lines=[
        "शहर में गली-गली तैयार हुए हजारों किलो फाफड़ा-",
        "जलेबी में सब सलामत! केवल १० इकाइयों को नोटिस"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    86, 1922, 392, 2010,
    text="अहमदाबाद मनपा के फूड विभाग द्वारा आज शहर में फाफड़ा-जलेबी को लेकर जांच अभियान चलाया गया। इसमें",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(404, 1926, 404, 2008, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 1922, 718, 2010,
    text="पर १० इकाइयों को नोटिस देकर रु. ४० हजार का जुर्माना वसूला गया है। जबकि वस्त्रापुर तालाब के सामने सैलाभ",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(730.5, 1926, 730.5, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 1922, 1052, 2010,
    text="उल्लेखनीय है कि यहां फाफड़ा और जलेबी ८०० रुपये किलो बिकते हैं। इतनी भारी रकम वसूलने के बाद भी हानिकारक",
    target_lines=3,
    first_indent_pt=0.0,
)

# 2-Col Callout Box (x=86..724, y=2017..2401) + Col 3 Oil Meter Photo
draw_box(86, 2017, 724, 2401, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    98, 2024, 712, 2108,
    lines=[
        "बेलगाम मुनाफाखोरी : फाफड़ा की लागत कीमत",
        "१७५ रुपये और जलेबी की मात्र २२५ रुपये!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    98, 2112, 712, 2394,
    text="स्वास्थ्य की बात एक तरफ रखें तो अहमदाबाद शहर में फाफड़ा-जलेबी के नाम पर बेलगाम मुनाफाखोरी भी हो रही है। फरसाण व्यापारियों के अनुसार बेसन, तेल, मसाले, रसोई गैस आदि की कीमत जोड़ी जाए तो एक किलो फाफड़ा की लागत कीमत बढ़कर मुश्किल से रु. १७५ प्रति किलो होती है। आज भी शहर में २५० रुपये किलो शुद्ध फरसाण बिकता ही है। परंतु अधिकांश दुकानों में फाफड़ा के ७०० से ८०० रुपये वसूले जाते हैं। इसी तरह जलेबी की लागत कीमत २२५ रुपये प्रति किलो से अधिक नहीं आती, उसमें भी भारी मुनाफा वसूला जाता है। कलेक्टर कार्यालय के आपूर्ति विभाग द्वारा कभी भी इस दिशा में कोई जांच कर कार्रवाई नहीं की जाती।",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_png(748, 2013, 1055, 2408, "oil_meter_photo.png")

place_exact_body_column(
    86, 2408, 392, 2586,
    text="शहर के नामी-अनामी १४ स्थानों से फाफड़ा, जलेबी, चटनी, खाद्य तेल, मिर्च पाउडर, कढ़ी आदि वस्तुओं के २४ नमूने लेकर जांच के लिए पब्लिक हेल्थ लेबोरेटरी में भेजे गए हैं। इस चेकिंग के दौरान कुछ अनियमितताओं",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(404, 2410, 404, 2584, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 2408, 718, 2586,
    text="कॉम्प्लेक्स में स्थित वस्त्रापुर गांठिया पर जांच करने पर यहां खाद्य तेल में टीपीसी यानी टोटल पोलर कंपाउंड की मात्रा ३२ पाई गई, जो सामान्यतः २५ से अधिक नहीं होनी चाहिए। इस लापरवाही पर यह इकाई सील की गई है।",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    744, 2410, 1052, 2586,
    text="ऐसे जले हुए तेल का उपयोग हो रहा था। दूसरी ओर शहर में गली-गली हजारों किलो फाफड़ा-जलेबी तैयार हुए हैं। परंतु शहर में सब सलामत हो इस तरह उंगलियों पर गिनी जा सकने जितनी इकाइयों पर ही कार्रवाई हुई है।",
    target_lines=6,
    first_indent_pt=0.0,
)


# ==============================================================================
# 4. STORY 3: BOTTOM-LEFT 3-COL STORY (GARBA FAKE PASS AI QR SCAM)
# ==============================================================================
print("Building Story 3 (Garba Fake Pass AI QR Scam, Cols 1-3)...")
draw_line(84, 2592, 1056, 2592, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    187, 2602, 951, 2652,
    lines=["मामला दर्ज होने के बाद भी बेचे कई पास !"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(187, 2657, 951, 2657, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    86, 2664, 1052, 2848,
    lines=[
        "अहमदाबाद के प्रसिद्ध गरबा के नकली",
        "पास पर QR लगाने में AI का उपयोग"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    390, 2858, 554, 2884,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    86, 2886, 554, 3014,
    text="अहमदाबाद और गुजरात के विभिन्न शहरों के २५ से अधिक बड़े गरबा आयोजनों के फर्जी पास इंस्टाग्राम पर बेचने के मामले में राजस्थान से पकड़े गए आरोपियों से पूछताछ में चौंकाने वाला खुलासा हुआ कि वे इंस्टाग्राम",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(568, 2862, 568, 3012, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    582, 2858, 1052, 3014,
    text="से विभिन्न आयोजनों की इमेज लेकर उसे एआई से एडिट कर बुकिंग के क्यूआर कोड लगाते थे। पुलिस को एआई से एडिट की गई विभिन्न इमेज और ग्राहकों के साथ हुई व्हाट्सएप चैट भी मिली है, जिसकी पुलिस आगे जांच कर रही है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    86, 3020, 1052, 3132,
    lines=[
        "आरोपी के पास से चैटजीपीटी सहित एआई टूल्स",
        "और ग्राहकों के साथ हुई व्हाट्सएप चैट बरामद"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    86, 3140, 392, 3792,
    text="नवरात्रि के बड़े आयोजक पास बेचने के लिए ऑनलाइन प्लेटफॉर्म का उपयोग करते हैं। इसका अनुचित लाभ उठाकर कुछ लोगों ने इंस्टाग्राम और फेसबुक पर फर्जी आईडी बनाकर उसके जरिए विभिन्न आयोजनों के टिकट आधी से भी कम कीमत पर बेचने के घोटाले में साइबर क्राइम द्वारा वीरेंद्रसिंह राठौड़ और किशनसिंह राठौड़ को राजस्थान से गिरफ्तार किया गया था। दोनों ने लोगों को विश्वास में लेने के लिए इंस्टाग्राम पर पेड आईडी बनाए थे, ताकि वे प्रोफेशनल लगें और उनकी एक-एक पोस्ट ४० हजार लोगों तक पहुंचती थी। नकली पास तैयार करने के लिए वे चैटजीपीटी एआई एप्लिकेशन का उपयोग करते थे और गरबा के विभिन्न आयोजकों की इंस्टाग्राम आईडी से इमेज का स्क्रीनशॉट लेकर उसे एआई से एडिट कर बीच में बुकिंग का क्यूआर कोड लगाते थे, जिससे पास असली",
    target_lines=21,
    first_indent_pt=10.0,
    hi_pt=10.8,
)
draw_line(404, 3144, 404, 3242, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    416, 3140, 718, 3236,
    text="दिखता था। वे व्हाट्सएप पर विभिन्न आयोजकों के गरबा पास का विवरण भी देते थे। पुलिस को कुछ",
    target_lines=3,
    first_indent_pt=0.0,
)
# Col 2 Event List Table Box (x=416..724, y=3252..3791)
draw_box(416, 3252, 724, 3791, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    424, 3258, 716, 3336,
    lines=[
        "आरोपियों ने किन-किन",
        "इवेंट्स के पास बेचे थे"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(416, 3343, 724, 3343, swatch="[Black]", weight_pt=1.0)
place_exact_display_lines(
    422, 3346, 718, 3376,
    lines=["क्र. इवेंट का नाम          पास संख्या"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
draw_line(416, 3380, 724, 3380, swatch="[Black]", weight_pt=0.8)
place_exact_display_lines(
    422, 3384, 650, 3786,
    lines=[
        "१.   आफ्टर ११ ५९",
        "२.   मंडपम",
        "३.   चौक के गरबा",
        "४.   ऑफबीट",
        "५.   वनरात्रि",
        "६.   रंग मोरला",
        "७.   एईएमएस रात्रि",
        "८.   रातलड़ी",
        "९.   इनर सर्कल",
        "१०. पंचम के गरबा",
        "११. अनंत एक्सपीरियंस",
        "१२. इफेटोन",
        "१३. सफेद परिंदे",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    652, 3384, 716, 3786,
    lines=[
        "११८", "१६७", "१२२", "९७", "५१", "४९", "३१", "३१", "२०", "१२", "६", "६", "६"
    ],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
draw_line(734, 3144, 734, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    744, 3140, 1052, 3792,
    text="ग्राहकों के साथ हुई चैट का विवरण भी मिला है।\nगरबा के नकली पास की बुकिंग होने की सूचना वे ई-मेल से भी देते थे। इसके लिए उन्होंने २० से अधिक फर्जी ई-मेल आईडी भी बनाए थे। साथ ही पैसों के लेन-देन के लिए म्यूल बैंक अकाउंट का उपयोग करते थे। आरोपियों के खिलाफ साइबर क्राइम तथा सांतेज में मामला दर्ज हुआ था। इसलिए पुलिस से बचने और इस दौरान भी पास बेचने के लिए वे जोधपुर, बीकानेर और सीकर में अलग-अलग स्थानों पर छिपते थे। पुलिस को पता चला कि वीरेंद्रसिंह राठौड़ ने अहमदाबाद के एक कॉलेज से बीबीए की पढ़ाई की थी, जिससे उसे अहमदाबाद की नवरात्रि की अच्छी जानकारी थी और उसने अन्य आरोपी के साथ मिलकर यह पूरा घोटाला किया।",
    target_lines=21,
    first_indent_pt=0.0,
)


# ==============================================================================
# 5. STORY 4: COLS 4-5 TOP (VIJAYADASHAMI 60-FT RAVANA DAHAN)
# ==============================================================================
print("Building Story 4 (Vijayadashami 60-ft Ravana Dahan, Cols 4-5)...")
place_exact_display_lines(
    1082, 202, 1716, 246,
    lines=["शस्त्र पूजन, रामलीला सहित विभिन्न आयोजन"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1082, 249, 1716, 249, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 254, 1718, 422,
    lines=[
        "आज विजयादशमी : ६०",
        "फीट के रावण का होगा दहन"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 426, 1718, 452,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 454, 1718, 544,
    text="असत्य पर सत्य की विजय के पर्व ‘विजयादशमी’ को कल आस्था और उल्लासपूर्वक मनाया जाएगा। शास्त्रविदों के अनुसार कल दोपहर १२:५० बजे से विजयादशमी का प्रारंभ होगा।",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 548, 1718, 642,
    lines=[
        "शारदीय नवरात्रि का समापन होगा, दोपहर",
        "१२:५० के बाद विजयादशमी का प्रारंभ"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 646, 1386, 1005,
    text="भाडज के हरेकृष्ण मंदिर में कल रात ८ बजे ६० फीट के रावण के पुतले का दहन किया जाएगा। रावण का पुतला बनाने के लिए पिछले एक महीने से उत्तर प्रदेश के कारीगर आए हुए हैं। रावण दहन से पूर्व शाम ६ बजे सीता-राम स्वर्ण रथयात्रा और शाम ६:३० बजे रामलीला का मंचन किया जाएगा। इस्कॉन मंदिर में शाम ६:३० बजे संध्या आरती के बाद मंदिर के पिछले प्रांगण में शाम ७:३० बजे २५ फीट के रावण के पुतले का दहन किया जाएगा।\nइसके अलावा एईएस ग्राउंड-थलतेज",
    target_lines=12,
    first_indent_pt=10.0,
)
draw_line(1399.5, 650, 1399.5, 1004, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 646, 1718, 1005,
    text="में शाम ५:३० बजे ५१ फीट ऊंचे रावण और ३५-३५ फीट के मेघनाद-कुंभकर्ण के पुतलों का दहन होगा। इसके अलावा आतिशबाजी, डायरा सहित कई कार्यक्रमों का भी आयोजन किया जाएगा। रखियाल और खोखरा में भी रावण दहन का आयोजन किया गया है। कई सोसाइटियों और क्लबों में भी रावण दहन का आयोजन रखा गया है। रावण दहन के मद्देनजर फायर ब्रिगेड द्वारा भी तैयारियां पूरी कर ली गई हैं। जहां से भी रावण दहन के लिए आवेदन आया है वहां फायर ब्रिगेड की गाड़ियां तैनात रहेंगी।",
    target_lines=12,
    first_indent_pt=0.0,
)


# ==============================================================================
# 6. STORY 5: COLS 4-5 UPPER-MID (RTE 54 STUDENTS SOLARIS SCHOOL PENALTY)
# ==============================================================================
print("Building Story 5 (RTE Solaris School Penalty, Cols 4-5)...")
draw_line(1080, 1013, 1720, 1013, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 1018, 1718, 1060,
    lines=["नियम के अनुसार पोर्टल पर एंट्री ही न करके"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1065, 1718, 1065, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1070, 1718, 1220,
    lines=[
        "RTE के ५४ बच्चों को सहायता से",
        "वंचित रखने वाले स्कूल पर पेनल्टी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 1222, 1718, 1246,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 1248, 1718, 1398,
    text="आरटीई में प्रवेश लेने वाले बच्चों को हर वर्ष सरकार द्वारा ३ हजार रुपये की आर्थिक सहायता दी जाती है। परंतु इस सहायता के लिए स्कूल को बच्चों की आरटीई पोर्टल पर अनिवार्य रूप से एंट्री करनी होती है। शहर डीईओ के अनुसार सोला के सोलारिस पब्लिक स्कूल ने बच्चों की एंट्री ही नहीं की जिससे इस वर्ष ५४ बच्चे आरटीई की सहायता से वंचित रह गए हैं। इसलिए इस स्कूल पर दस हजार रुपये का जुर्माना लगाया गया है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 1402, 1718, 1498,
    lines=[
        "सोला क्षेत्र के सोलारिस पब्लिक स्कूल पर एक्ट के",
        "नियम अनुसार डीईओ द्वारा १० हजार रुपये का जुर्माना"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 1504, 1386, 1806,
    text="इस वर्ष आरटीई के तहत कुल ८० हजार से अधिक बच्चों को ३ हजार रुपये की सहायता चुका दी गई है। परंतु सोलारिस पब्लिक स्कूल में बच्चों को सहायता न मिलने पर एक अभिभावक ने शिकायत की थी। इसके आधार पर जांच करने पर सामने आया कि सोलारिस स्कूल ने आरटीई के बच्चों की एंट्री आरटीई डीबीएमएस पोर्टल पर की ही नहीं थी। विभिन्न कक्षाओं के कुल ५४ बच्चे इस स्कूल में",
    target_lines=10,
    first_indent_pt=10.0,
)
draw_line(1399.5, 1508, 1399.5, 1804, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1504, 1718, 1806,
    text="आरटीई के तहत प्रवेश लेकर पढ़ रहे हैं। स्कूल द्वारा लापरवाही बरतते हुए एंट्री न किए जाने से बच्चे सहायता से वंचित रह गए। इसलिए अहमदाबाद शहर डीईओ ने आरटीई एक्ट के प्रावधान के अनुसार स्कूल पर दस हजार रुपये का जुर्माना लगाया है। हालांकि स्कूल की गलती से बच्चे सहायता से वंचित रह गए हैं, इसलिए अब बच्चों की एंट्री कराने का आदेश दिया गया है। अब एंट्री के बाद ही सहायता मिलेगी।",
    target_lines=10,
    first_indent_pt=0.0,
)


# ==============================================================================
# 7. STORY 6: COLS 4-5 LOWER-MID (RAKHIAL AL FALAH ISLAMIC SCHOOL)
# ==============================================================================
print("Building Story 6 (Rakhial Al Falah School, Cols 4-5)...")
draw_line(1080, 1810, 1720, 1810, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 1816, 1718, 1860,
    lines=["रखियाल के अल फलाह इस्लामिक स्कूल में"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 1864, 1718, 1864, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 1868, 1718, 2010,
    lines=[
        "बिना अनुमति कक्षाएं चलाने पर स्कूल की",
        "मान्यता रद्द करने सरकार को रिपोर्ट"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 2012, 1718, 2036,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 2038, 1718, 2188,
    text="अहमदाबाद के रखियाल क्षेत्र के अल फलाह इस्लामिक स्कूल के खिलाफ मिली शिकायत के आधार पर अहमदाबाद शहर डीईओ द्वारा जांच की गई थी। जांच रिपोर्ट के अनुसार स्कूल द्वारा कक्षा १ से ५ में स्वीकृत वर्गों से अधिक विद्यार्थियों को प्रवेश दिया गया है तथा बिना अनुमति कक्षा ६ से ८ में वर्ग चलाए जा रहे हैं। इस जांच रिपोर्ट के आधार पर शहर डीईओ ने प्राथमिक शिक्षा विभाग को इस स्कूल की मान्यता रद्द करने और कानूनी कार्रवाई की अनुमति देने का प्रस्ताव भेजा है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 2192, 1718, 2288,
    lines=[
        "स्कूल के खिलाफ पुलिस शिकायत करने की अनुमति देने",
        "और मान्यता रद्द करने अहमदाबाद डीईओ का प्रस्ताव"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 2294, 1386, 2826,
    text="सरकार के प्राथमिक शिक्षा विभाग के निदेशक कार्यालय को अहमदाबाद शहर डीईओ द्वारा अल फलाह इस्लामिक स्कूल के खिलाफ जांच रिपोर्ट भेजकर मान्यता रद्द करने की सिफारिश की गई है। डीईओ ने बताया कि अधिकारियों द्वारा गत अगस्त में जांच रिपोर्ट पेश की गई थी। इसके बाद स्कूल पर १० हजार का जुर्माना लगाया गया था और २४ अगस्त को सुनवाई में स्कूल के प्रतिनिधियों को बुलाया गया था। इसके बाद आरटीई के अनुसार जांच कमेटी गठित की गई थी, जिसकी रिपोर्ट भी १५ अक्टूबर को पेश की गई। इस रिपोर्ट के अनुसार २०१८ में स्कूल को कक्षा १ से ५ की ही अनुमति मिली है, परंतु प्रत्यक्ष जांच में ६ से ८ के विद्यार्थी अलग-अलग कक्षाओं में पाए गए। कक्षा ६ से ८ के",
    target_lines=17,
    first_indent_pt=10.0,
)
draw_line(1399.5, 2298, 1399.5, 2824, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 2294, 1718, 2826,
    text="विद्यार्थियों के सीटीएस पोर्टल के ट्रैकिंग विवरण के अनुसार फिलहाल अल फलाह इंग्लिश मीडियम स्कूल में जो विद्यार्थी पढ़ते हैं उनकी जांच करने पर यूडायस नंबर के अनुसार चेरी ब्लॉसम इंग्लिश स्कूल के नाम से दिखते हैं। यह स्कूल बंद हो चुका है। इस प्रकार इस स्कूल में कक्षा १ से ५ में स्वीकृत वर्गों से अधिक विद्यार्थियों को प्रवेश दिया गया है और बिना अनुमति कक्षा ६ से ८ का स्कूल चलाया जा रहा है। स्कूल में कुल १२५२ विद्यार्थी कक्षा १ से ५ में हैं। जांच के दौरान सामने आया कि अल फलाह स्कूल द्वारा कई विद्यार्थियों की पढ़ाई और भविष्य के साथ खिलवाड़ किया गया है। अहमदाबाद शहर डीईओ ने इस स्कूल की मान्यता रद्द करने और पुलिस शिकायत की अनुमति देने का प्रस्ताव सरकार को भेजा है।",
    target_lines=17,
    first_indent_pt=0.0,
)


# ==============================================================================
# 8. STORY 7: COLS 4-5 BOTTOM (SARKHEJ-SINDHU BHAVAN GARBA FAKE TICKETS)
# ==============================================================================
print("Building Story 7 (Sankalp Nagari Garba Fake Tickets, Cols 4-5)...")
draw_line(1080, 2832, 1720, 2832, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1080, 2838, 1718, 2880,
    lines=["सरखेज-सिंधु भवन स्थित संकल्प नगरी में"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1080, 2882, 1718, 2882, swatch="[Black]", weight_pt=1.3)
place_exact_display_lines(
    1080, 2888, 1718, 3048,
    lines=[
        "गरबा में अत्यधिक भीड़ देख",
        "नकली टिकट का घोटाला पकड़ाया"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    1500, 3052, 1718, 3078,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1080, 3080, 1718, 3230,
    text="शहर के सरखेज-सिंधु भवन रोड पर आयोजित संकल्पनगरी गरबा के नकली पास छपवाकर अवैध रूप से बेचने का बड़ा घोटाला सामने आया है। इसमें ऑफलाइन बेचे जाने वाले पास से अधिक भीड़ आने पर आयोजकों को संदेह हुआ था। इसलिए उन्होंने शुक्रवार को होने वाले गरबा के पास की डिजाइन बदल दी और उस दिन नकली पास लेकर आए लोग पकड़े गए। ये पास विपुल भीमाणी नामक व्यक्ति द्वारा बेचे जाने की बात सामने आई। इस मामले में सरखेज पुलिस ने केस दर्ज कर जांच शुरू की है।",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=12.0,
)
place_exact_display_lines(
    1080, 3234, 1718, 3334,
    lines=[
        "आयोजकों द्वारा संदेह के बाद पास की डिजाइन बदलते ही",
        "गरबा के नकली पास बनाने वाला आरोपी पकड़ा गया"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1080, 3340, 1386, 3792,
    text="बोपल स्थित अरिहंत कुटीर बंग्लोज में रहने वाले द्रुपददास गांधी ने सरखेज-सिंधु भवन रोड पर औडा के प्लॉट में अपने साझेदारों के साथ मिलकर संकल्पनगरी गरबा का आयोजन किया था। उन्होंने ऑनलाइन पास बिक्री के साथ ऑफलाइन पास बेचने के लिए प्रतिदिन आठ हजार के हिसाब से दस दिनों के ८० हजार पास छपवाए थे, जिनकी बिक्री गरबा ग्राउंड के बाहर की जाती थी। नवरात्रि के पहले तीन दिनों के दौरान आयोजकों के ध्यान में आया कि ऑफलाइन गरबा पास का जिस तरह वितरण होता है उससे कहीं",
    target_lines=15,
    first_indent_pt=10.0,
)
draw_line(1399.5, 3344, 1399.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 3340, 1718, 3792,
    text="अधिक लोग गरबा खेलने के लिए आते हैं। इससे नकली पास बेचे जाने की आशंका जताई गई। बाद में आयोजकों ने शुक्रवार को बिक्री के लिए पहले से तैयार किए गए पास रद्द कर नई डिजाइन तैयार की थी। इस दिन शाम के समय कुछ लोग पहले से रद्द किए गए पास लेकर आए थे। उनमें से कुछ लोगों से पूछने पर पता चला कि उन्होंने विपुल भीमाणी नामक व्यक्ति से ये पास खरीदे थे। इस प्रकार विपुल भीमाणी नामक व्यक्ति संकल्पनगरी के नकली पास छपवाकर बेच रहा था।",
    target_lines=15,
    first_indent_pt=0.0,
)


# ==============================================================================
# 9. STORY 8: COLS 6-8 TOP (RIVERFRONT 60-CR MULTILEVEL PARKING)
# ==============================================================================
print("Building Story 8 (Riverfront Multilevel Parking, Cols 6-8)...")
place_exact_display_lines(
    1744, 202, 2715, 254,
    lines=["भारी खर्च के बाद भी जनता को सुविधा नहीं, किराए की आय भी शून्य"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 258, 2715, 258, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 264, 2715, 448,
    lines=[
        "रिवरफ्रंट का ६० करोड़ का सफेद हाथी समान",
        "मल्टीलेवल पार्किंग एक साल से बंद पड़ा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2030, 456, 2208, 482,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 484, 2208, 604,
    text="अहमदाबाद मनपा के साथ उससे जुड़े एएमटीएस, बीआरटीएस या साबरमती रिवरफ्रंट डेवलपमेंट कॉर्पोरेशन जैसी इकाइयां भी जनता के पैसों को पानी में बहा रही हैं, ऐसे विवरण बार-बार सामने आते रहते हैं।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 460, 2220, 602, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 456, 2715, 604,
    text="एसआरएफडीसीएल तंत्र की नाकामी के नमूने के समान फ्लावर पार्क के सामने स्थित रु. ६० करोड़ का मल्टीलेवल पार्किंग एक साल से बेकार पड़ा है। भारी रकम खर्च करने के बाद जनता को न तो पार्किंग की सुविधा मिल रही है और न ही तंत्र को किराए की आय हो रही है!",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 608, 2715, 724,
    lines=[
        "तंत्र की नाकामी का नमूना : अब एक से पांच मंजिल की",
        "पार्किंग ३६.४२ लाख रुपये में किराए पर देने की कवायद"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 728, 2052, 820,
    text="अहमदाबाद के साबरमती रिवरफ्रंट पर फ्लावर पार्क के सामने स्थित मल्टीलेवल पार्किंग की एक से पांच मंजिल रु. ३६.४२",
    target_lines=3,
    first_indent_pt=10.0,
)
draw_line(2064, 732, 2064, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 728, 2382, 820,
    text="स्मार्ट सिस्टम से लोग पूरी तरह परिचित होते, तब तक तो इसके बुरे दिन शुरू हो गए थे। करीब एक साल पहले जब इस",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(2395.5, 732, 2395.5, 818, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 728, 2715, 820,
    text="यहां पार्किंग की सुविधा बंद है। इसलिए लोगों को इसका लाभ नहीं मिलता, वहीं दूसरी ओर तंत्र को भी कोई आय नहीं हो रही है।",
    target_lines=3,
    first_indent_pt=0.0,
)

# 3-Col Double-Bordered Photo & Story Box (x=1744..2716, y=832..1167)
draw_box(1744, 832, 2716, 1167, stroke_swatch="[Black]", stroke_weight_pt=2.0)
draw_box(1754, 842, 2706, 1157, stroke_swatch="[Black]", stroke_weight_pt=0.8)
place_png(1756, 843, 2167, 1157, "riverfront_parking_photo.png")
place_exact_display_lines(
    2176, 848, 2700, 930,
    lines=[
        "किराया घटाने के लिए तंत्र की तिकड़म : १५० टू-व्हीलर और",
        "३५० फोर-व्हीलर की पार्किंग में कर दी कटौती"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2176, 934, 2700, 1152,
    text="साबरमती रिवरफ्रंट डेवलपमेंट कॉर्पोरेशन के अधिकारियों ने पार्किंग का किराया घटाने के लिए एक तिकड़म लगाई है। इस पार्किंग में वैसे तो १००० से अधिक टू-व्हीलर और ७०० से अधिक फोर-व्हीलर पार्क हो सकें ऐसी व्यवस्था है। परंतु नए टेंडर के अनुसार पहली और दूसरी मंजिल पर ८७६ टू-व्हीलर तथा ३७२ फोर-व्हीलर पार्किंग की व्यवस्था दिखाई गई है। यानी ५०० वाहनों की पार्किंग कम कर दी गई है।",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Parking Rate Table (Cols 6-7, x=1744..2384, y=1179..1441)
draw_box(1825, 1179, 2310, 1228, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1835, 1184, 2300, 1224,
    lines=["मल्टीलेवल पार्किंग के किराए की दर"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
for ry in (1234, 1268, 1302, 1336, 1370, 1404, 1441):
    draw_line(1744, ry, 2384, ry, swatch="[Black]", weight_pt=0.8)
place_exact_display_lines(
    1748, 1236, 2010, 1402,
    lines=[
        "समय",
        "२ घंटे तक",
        "२ से ४ घंटे के लिए",
        "४ घंटे से अधिक",
        "रात १२ बजे के बाद",
    ],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2030, 1236, 2180, 1402,
    lines=["टू-व्हीलर", "रु.१०", "रु.२०", "रु.३०", "रु.३००"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    2210, 1236, 2376, 1402,
    lines=["फोर-व्हीलर", "रु.२०", "रु.४०", "रु.५०", "रु.५००"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.86,
)
place_exact_display_lines(
    1748, 1406, 2376, 1438,
    lines=["(रात्रि के समय की राशि पेनल्टी के रूप में प्रतिदिन की है।)"],
    font_style="Bold",
    align="left",
    stretch_lines=False,
    target_hscale=0.86,
)

# 7th Floor Restaurant Box (Cols 6-7, x=1744..2384, y=1448..1624)
draw_box(1744, 1448, 2384, 1624, stroke_swatch="[Black]", stroke_weight_pt=1.6)
place_exact_display_lines(
    1754, 1454, 2374, 1496,
    lines=["सातवीं मंजिल गार्डन रेस्टोरेंट के लिए आरक्षित रखी गई"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1754, 1500, 2374, 1618,
    text="एसआरएफडीसीएल के सूत्रों के अनुसार पार्किंग की सातवीं मंजिल गार्डन रेस्टोरेंट के लिए रिजर्व रखी गई है। तथा उसकी पार्किंग के लिए छठी मंजिल खाली रखी गई है। इसलिए वाहन पार्किंग की संख्या घट जाने से किराए की कुल राशि में कमी आई है।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=12.0,
)

# Col 8 Smart Parking Box (x=2402..2720, y=1177..1619)
draw_box(2402, 1177, 2720, 1619, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2410, 1184, 2712, 1268,
    lines=[
        "रिवरफ्रंट मल्टीलेवल",
        "पार्किंग की स्मार्ट सुविधाएं"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2410, 1272, 2712, 1612,
    text="इस मल्टीलेवल पार्किंग में सीसीटीवी कैमरे से लेकर इलेक्ट्रिक वाहन के चार्जिंग पॉइंट, क्यूआर कोड वाला टिकट, पेमेंट के लिए डिजिटल मशीन, वाहन पार्किंग के लिए सेंसर, बूम बैरियर सहित स्मार्ट व्यवस्थाएं हैं। यहां कितने वाहन पार्क हैं और कितनी जगह खाली है, यह अपने आप पता चल जाए ऐसा डिजिटल डिस्प्ले बोर्ड भी है। यह पार्किंग स्मार्ट पार्किंग मोबाइल एप्लिकेशन से जुड़ी है।",
    target_lines=12,
    font_style="Bold",
    first_indent_pt=10.0,
)

# Bottom 3 Columns of Riverfront Parking Story (y=1632..1904)
place_exact_body_column(
    1744, 1632, 2052, 1904,
    text="लाख के वार्षिक किराए पर देने की कवायद शुरू की गई है। तंत्र के लिए गले की हड्डी बन चुके इस पार्किंग के अतीत में जाएं तो वर्तमान मेयर जब स्टैंडिंग कमेटी के चेयरमैन थे, तब सितंबर २०२३ में इस मल्टीलेवल स्मार्ट पार्किंग का लोकार्पण किया गया था। रु. ६० करोड़ की लागत से ७०० कार और १००० टू-व्हीलर पार्क हो सकें ऐसे इस पार्किंग के",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2064, 1634, 2064, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1632, 2382, 1904,
    text="पार्किंग को किराए पर देने की कवायद की गई, तब ठेकेदार ने ५० लाख रुपये में पार्किंग किराए पर ली थी। परंतु इसके मुकाबले महीने में एक लाख रुपये की भी आय न होने से ठेकेदार ने यह अनुबंध रद्द करने की गुहार लगाई थी। यह अनुबंध रद्द होने के बाद सात मंजिला मल्टीलेवल पार्किंग की यह पूरी इमारत फिलहाल अनुपयोगी पड़ी है। वर्तमान में",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2395.5, 1634, 2395.5, 1902, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1632, 2715, 1904,
    text="ऐसे में जनता के ६० करोड़ रुपये इस तरह बर्बाद करने के लिए जिम्मेदार कौन? ऐसा सवाल उठा है। उल्लेखनीय है कि इससे पहले सिंधु भवन रोड और प्रहलाद नगर के मल्टीलेवल पार्किंग भी विवादों में आ चुके हैं। अहमदाबाद में विफल रहे मल्टीलेवल पार्किंग के लिए मनपा के अधिकारी और शासक क्यों करोड़ों रुपये बर्बाद करते हैं, यह लोगों की समझ से परे है।",
    target_lines=9,
    first_indent_pt=0.0,
)


# ==============================================================================
# 10. STORY 9: COLS 6-8 MID (DRI 42-HR RAID / 18-CR GOLD SMUGGLING SYNDICATE)
# ==============================================================================
print("Building Story 9 (DRI 18-Cr Gold Smuggling Syndicate, Cols 6-8)...")
draw_line(1744, 1910, 2716, 1910, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1744, 1916, 2715, 1968,
    lines=["डीआरआई द्वारा ४२ घंटे छापेमारी कर की गई कार्रवाई"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1744, 1975, 2715, 1975, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 1982, 2715, 2168,
    lines=[
        "गोल्ड स्मगलिंग करने वाला सिंडिकेट पकड़ाया",
        "१८ करोड़ का सोना जब्त : ३ की गिरफ्तारी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_display_lines(
    2030, 2174, 2208, 2198,
    lines=["अहमदाबाद, सोमवार"],
    font_style="Bold",
    align="right",
    stretch_lines=False,
    target_hscale=0.88,
)
place_exact_body_column(
    1744, 2200, 2208, 2296,
    text="अहमदाबाद और सूरत के इंटरनेशनल एयरपोर्ट के जरिए भारत में विदेश से सोना लाने वाले एक संगठित गोल्ड स्मगलिंग सिंडिकेट का डायरेक्टोरेट ऑफ रेवेन्यू इंटेलिजेंस ने पर्दाफाश किया है और ३",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=10.0,
)
draw_line(2220, 2178, 2220, 2294, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2232, 2174, 2715, 2296,
    text="व्यक्तियों को गिरफ्तार किया है। इस ऑपरेशन में तस्करी किए गए सोने की आवाजाही और निपटान को सुगम बनाने में यात्रियों, हैंडलर्स, बिचौलियों, सोना गलाने की इकाई के ऑपरेटर और ज्वेलरी ट्रेड चैनल की परस्पर जुड़ी भूमिका सामने आई है।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 2300, 2715, 2414,
    lines=[
        "दुबई के फाइनेंसर की संलिप्तता : वडोदरा में अवैध सोना",
        "गलाने की इकाई के साथ अहमदाबाद, सूरत एयरपोर्ट में नेटवर्क"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 2420, 2052, 3058,
    text="डीआरआई के अधिकारियों ने १६ अक्टूबर से ४२ घंटे तक समन्वित छापेमारी की थी। इसमें हवाई यात्रियों द्वारा तस्करी, हैंडलर्स को सौंपना, अवैध रूप से गलाना और ज्वेलरी आउटलेट के जरिए बिक्री सहित पूरे रैकेट का भंडाफोड़ हुआ। कुल रु. १८.४१ करोड़ कीमत के १३.०१७ किलो विदेशी मूल के सोने के सौदे उजागर हुए। इस समन्वित ऑपरेशन के परिणामस्वरूप लगभग ८९० ग्राम सोना जब्त किया गया और ६.४१ किलो अवैध रूप से गलाए गए सोने से संबंधित आपराधिक सबूत रिकवर किए गए।\nइस समन्वित ऑपरेशन के परिणामस्वरूप लगभग ८९० ग्राम सोना जब्त किया गया और ६.४१ किलो अवैध रूप से गलाए गए सोने से संबंधित आपराधिक सबूत रिकवर किए गए। ज्वेलरी शॉप पर आगे की जांच के दौरान",
    target_lines=21,
    first_indent_pt=10.0,
)
draw_line(2064, 2424, 2064, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 2420, 2382, 2542,
    text="बेहिसाबी विदेशी मूल के सोने के बिस्किट (बार्स) और दुबई स्थित सिंडिकेट के मुख्य फाइनेंसर से जुड़े एक अलग हैंडलर द्वारा",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2424, 2395.5, 2540, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2420, 2715, 2542,
    text="सोने के बिस्किट और दुबई स्थित सिंडिकेट के मुख्य फाइनेंसर से जुड़े एक अलग हैंडलर द्वारा भेजे गए लगभग ५.८ किलो",
    target_lines=4,
    first_indent_pt=0.0,
)
draw_box(2070, 2551, 2720, 2891, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2080, 2558, 2710, 2612,
    lines=["गोल्ड स्मगलिंग का नेटवर्क किस तरह चलता था?"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2080, 2616, 2710, 2884,
    text="*  यात्रियों द्वारा सोना छिपाने के अनोखे तरीकों का उपयोग कर देश में सोने की तस्करी की जाती थी।\n*  इसमें रोडियम कोटेड सोने के पतले तार, ट्रॉली बैग की अंदरूनी लाइनिंग में जड़ा सोना और बैग के भीतरी हिस्से में छिपाया गया गोल्ड पेस्ट शामिल था।\n*  आगमन के बाद, यह सोना एयरपोर्ट के बाहर हैंडलर्स को सौंपा जाता था और बिचौलियों के जरिए वडोदरा स्थित सोना गलाने की एक अवैध यूनिट तक पहुंचाया जाता था।\n*  इसके बाद गलाया गया सोना नकद बिक्री के लिए अहमदाबाद की एक ज्वेलरी शॉप में सप्लाई किया जाता था।",
    target_lines=9,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2900, 2382, 3058,
    text="भेजे गए लगभग ५.८ किलो तस्करी किए गए सोने के सौदों से संबंधित रिकॉर्ड्स रिकवर किए गए थे।\nज्वेलरी शॉप पर आगे की जांच के दौरान बेहिसाबी विदेशी मूल के",
    target_lines=5,
    first_indent_pt=0.0,
)
draw_line(2395.5, 2904, 2395.5, 3056, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 2900, 2715, 3058,
    text="तस्करी किए गए सोने के सौदों से संबंधित रिकॉर्ड्स रिकवर किए गए। कस्टम्स एक्ट, १९६२ के प्रावधानों के तहत तीन व्यक्तियों को गिरफ्तार किया गया है।",
    target_lines=5,
    first_indent_pt=0.0,
)


# ==============================================================================
# 11. STORY 10: COLS 6-8 BOTTOM (MANDLI GARBA BOUNCERS SWORD ATTACK)
# ==============================================================================
print("Building Story 10 (Mandli Garba Bouncers Sword Attack, Cols 6-8)...")
draw_line(1744, 3064, 2716, 3064, swatch="[Black]", weight_pt=0.9)
place_exact_display_lines(
    1748, 3068, 2710, 3114,
    lines=["पास स्कैन कराने को लेकर हुआ विवाद खूनी संघर्ष में बदला"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.88,
)
draw_line(1748, 3119, 2710, 3119, swatch="[Black]", weight_pt=1.4)
place_exact_display_lines(
    1744, 3126, 2715, 3304,
    lines=[
        "मंडली गरबा में बाउंसर गरबा प्रेमियों",
        "पर तलवारें लेकर टूट पड़े"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
    lead_ratio=0.92,
    max_pt_scale=0.92,
)
place_exact_body_column(
    1744, 3312, 2052, 3792,
    text="गांधीनगर, कलोल, सोमवार\nकमर्शियल गरबा के बढ़ते चलन के बीच उनमें अव्यवस्था और बाउंसरों की दादागिरी के मामले सामने आ रहे हैं। ऐसे में कलोल के नासमेद स्थित मंडली गरबा में पास स्कैन कराने को लेकर हुए विवाद ने उग्र रूप धारण कर लिया और बाउंसर तलवार तथा लोहे की जंजीरें लेकर गरबा प्रेमियों पर टूट पड़े, जिसमें पांच से अधिक युवक घायल हो गए। इस मामले में फिलहाल सांतेज पुलिस द्वारा केस दर्ज किया गया है।\nप्राप्त विवरण के अनुसार रांचरडा में विलेज कैफे चलाने वाले मौलिक रश्मीजी ठाकोर कल रात एक बजे अपने भाई तुषार और मित्रों अनिल ठाकोर, विवेक ठाकोर, सेतुल ठाकोर, विनोद ठाकोर, हिरेन पटेल,",
    target_lines=16,
    first_indent_pt=10.0,
)
draw_line(2064, 3316, 2064, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 3312, 2382, 3792,
    text="विशाल ठाकोर तथा राहुल ठाकोर के साथ नासमेद गांव की सीमा में आयोजित मंडली गरबा में गरबा देखने गए थे। इन सभी के एंट्री पास मौलिक के मोबाइल में होने से वे गेट पर पास स्कैन करा रहे थे, जबकि उनके कुछ मित्र अंदर गए थे।\nइसी दौरान वहां मौजूद एक सरदारजी बाउंसर ने हिरेन पटेल को अंदर जाने को कहा जिस पर हिरेन ने अपने मित्र के पास स्कैन होने के बाद साथ जाने की बात कही तो बाउंसर भड़क गया और बहस करने लगा। मामला न बिगड़े इसलिए मौलिक और उनके भाई ने बीच-बचाव कर बाउंसर को समझाने का प्रयास किया, परंतु बाउंसर और अधिक आक्रामक हो गए।",
    target_lines=16,
    first_indent_pt=0.0,
)
draw_line(2395.5, 3316, 2395.5, 3790, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 3312, 2715, 3792,
    text="उसी समय अचानक एक सरदारजी बाउंसर ने अपनी कमर से तलवार निकालकर मौलिक पर वार किया जिससे उनके नीचे झुकने पर तलवार की मूठ उनके सिर में लगी और खून बहने लगा। कुछ ही पलों में करीब दस अन्य सरदारजी बाउंसर हाथों में तलवारें, बांस के डंडे और लोहे की जंजीरें लेकर दौड़ पड़े और युवकों पर जानलेवा हमला कर दिया। इस घटना के चलते यहां भारी अफरा-तफरी मच गई और गरबा खेलने आए लोग भी सहम गए।\nशिकायत के आधार पर सांतेज पुलिस ने अज्ञात सरदारजी सिक्योरिटी बाउंसरों के खिलाफ मामला दर्ज कर कानूनी जांच शुरू कर दी है।",
    target_lines=16,
    first_indent_pt=0.0,
)


# ==============================================================================
# 12. SAVE OPEN FILE (.pagedesigner) & EXPORT FULL-RES PNG + PDF
# ==============================================================================
cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_02_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_02_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_02_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_02_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_02_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
