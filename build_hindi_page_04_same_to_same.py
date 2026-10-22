from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 4 BUILDER FOR AAS-PAAS (GUJARAT SAMACHAR HINDI)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima' & 'DB Hindi')
  across all 7 stories/columns/tables & Public Notices on Page 4!
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
ASSETS_DIR = DIR_SMAE / "Page_04_Assets"

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
        "title": "Aas-Paas (Hindi Gujarat Samachar) — Page 04 (100% Same-to-Same Editable Hindi)"
    }},
    {"command": "swatch.create", "params": {"name": "GsRedBanner", "color": "#ec1c24"}},
    {"command": "swatch.create", "params": {"name": "GsOrangeBorder", "color": "#f27b35"}},
    {"command": "swatch.create", "params": {"name": "GsCyanBorder", "color": "#008bd0"}},
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
print("Placing Page 4 Hindi Running Header...")
build_hindi_running_header(4, place_png, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: PORBANDAR 'REEL POLITICS' (COLS 1-3 TOP)
# ==============================================================================
print("Building Story 1 (Porbandar Reel Politics, Cols 1-3 Top)...")
place_exact_display_lines(
    82, 200, 1050, 246,
    lines=["पोरबंदर में केंद्रीय मंत्री का ‘रील पॉलिटिक्स’"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    82, 254, 1050, 462,
    lines=[
        "जेन-जी को लुभाने मंत्री की सोशल",
        "मीडिया इन्फ्लुएंसर्स के साथ बैठक!"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 468, 556, 620,
    text="पोरबंदर, सोमवार\nपोरबंदर के दौरे पर आए केंद्रीय मंत्री डॉ. मनसुख मांडविया द्वारा एक होटल में सोशल मीडिया कंटेंट क्रिएटर्स और इन्फ्लुएंसर्स",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 470, 564, 618, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 468, 1050, 620,
    text="के साथ विशेष बैठक आयोजित किए जाने से उन्होंने वास्तविक जनसमस्याओं के बजाय अपने पक्ष में प्रचार खड़ा करने का प्रयास किया होने की तीव्र प्रतिक्रिया स्थानीय राजनीतिक हलकों में व्याप्त हो रही है।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 626, 1050, 742,
    lines=[
        "वास्तविक विकास के प्रश्न दरकिनार किए जाने से रोष, ‘रील्स से",
        "नहीं, रिजल्ट से ही वोट मिलेंगे’- जनता में उठा स्वर"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 748, 386, 1188,
    text="दिल्ली से जेन-जी और युवाओं को आकर्षित करने के लिए मिले निर्देशों के अनुसार पारंपरिक सभा-जुलूस के बजाय डिजिटल माध्यम का सहारा लिया गया होने का सामने आया है, जहां केंद्रीय मंत्री ने क्रिएटर्स को सोशल मीडिया के योद्धा बताकर भोजन और भेंट-उपहारों के साथ संवाद साधा था।\nपोरबंदर में उद्योगों के वादों के बावजूद वास्तविक क्रियान्वयन का अभाव, रोजगार के अवसर, महंगाई, किसानों की फसल के उचित दाम और सरकारी अस्पताल में सुविधाओं की कमी जैसे मूलभूत प्रश्न आज भी अनसुलझे रहे हैं। इसके अलावा, जेतपुर के साड़ी उद्योग का केमिकलयुक्त प्रदूषित पानी पोरबंदर के",
    target_lines=15,
    first_indent_pt=9.0,
)
draw_line(400, 750, 400, 1188, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 748, 718, 1188,
    text="समुद्र में डालने के विवादित प्रोजेक्ट के मुद्दे पर बनी हुई चुप्पी, बंदरगाह में पिछले कई महीनों से छाया अंधेरा तथा अस्मावती घाट की तरफ जाने वाले मार्ग पर लाइटों के अभाव में मछुआरों के सामने पैदा होता दुर्घटना का जोखिम जैसे सुलगते सवालों के सामने जनता जवाब मांग रही है।\nलोगों में उठे आक्रोश के अनुसार, केवल हां में हां मिलाने वाले सीमित कंटेंट क्रिएटर्स के साथ हंसी-मजाक करने या सेल्फी और रील्स बनाने से जमीनी वास्तविकताएं बदल नहीं सकतीं। पोरबंदर की जनता अब जागरूक हो चुकी है, और झूठे आत्मीय संवादों या सोशल मीडिया के चमकते फिल्टर्स के पीछे छिपी मुश्किलों को पहचान गई है। जनता",
    target_lines=15,
    first_indent_pt=0.0,
)
draw_line(732, 750, 732, 1348, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 748, 1050, 918,
    text="स्पष्ट रूप से मान रही है कि लोगों के बुनियादी प्रश्नों का निराकरण लाने से ही लोकप्रियता मिलती है। इसलिए नेताओं को यह स्पष्ट समझना पड़ेगा कि चुनावों में वोट रील्स से नहीं बल्कि प्रश्नों के निराकरण के लिए लाए गए रिजल्ट से ही मिलेंगे।",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_line(746, 925, 1050, 925, swatch="[Black]", weight_pt=0.85)

# Story 2: Col 3 Middle (Ahmedabad Temperature 37C)
print("Building Story 2 (Ahmedabad Temperature, Col 3 Middle)...")
place_exact_display_lines(
    746, 932, 1050, 1012,
    lines=[
        "अहमदाबाद में अभी पांच दिन",
        "तापमान ३७ के आसपास ही रहेगा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1018, 1050, 1348,
    text="अहमदाबाद, सोमवार\nअहमदाबाद में गर्मी का स्तर यथावत रहने से औसत अधिकतम तापमान का पारा ३७.१ डिग्री पर दर्ज हुआ था। अभी आगामी पांच दिन अहमदाबाद का तापमान ३७ डिग्री के आसपास ही रहने का पूर्वानुमान है। राज्य में अन्यत्र राजकोट में ४०.८, भुज में ३९, सूरत में ३७.७, वडोदरा में ३७.६, भावनगर में ३६.४ डिग्री औसत अधिकतम तापमान दर्ज हुआ था।",
    target_lines=11,
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. STORY 3: 'BAAT-BAAT MEIN' COLUMN (COLS 4-5 TOP)
# ==============================================================================
print("Building Story 3 (Baat-Baat Mein Column, Cols 4-5 Top)...")
draw_box(1078, 195, 1718, 1352, stroke_swatch="GsCyanBorder", stroke_weight_pt=2.5)
draw_box(1088, 202, 1708, 308, fill_swatch="GsCyanBorder", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1100, 210, 1696, 300,
    lines=["बात-बात में"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
)
place_exact_display_lines(
    1094, 314, 1702, 382,
    lines=["नवरात्रि पास में ‘आरक्षण’ ?"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.88,
)
place_exact_body_column(
    1092, 388, 1390, 1342,
    text="आप गौर कीजिए... नवरात्रि के पास जिनके पास पहुंचने चाहिए ऐसे जोशीले नौजवानों को तो मुश्किल से औसतन ‘डेढ़’ ही पास मिलते हैं !\nदूसरी तरफ, गरबा के तीन चक्कर लगाते ही हांफने लगने वाले अंकलों और आंटियों के पास रोज के औसतन चार पास होते हैं !\nइसीलिए हमें लगता है कि गरबा के पास में ‘आरक्षण’ सिस्टम होना चाहिए!\nदेखिए...\n* * *\n५० प्रतिशत पास तो महिलाओं के लिए ही आरक्षित रखो ! क्योंकि महिलाएं हैं, तभी तो गरबा ‘देखने लायक’ बनते हैं !\nफिर भी कोई युवक ‘बॉबी डार्लिंग’ बनकर आ जाए तो सीधा उसे स्टेज पर चढ़ा देना !\n* * *\n१० प्रतिशत पास कान के डॉक्टरों के लिए रखो ! क्योंकि स्पीकरों की खतरनाक आवाज से अच्छे-अच्छों के कान के पर्दे ‘हिल’ जाते हैं !\nकान में ऐसी सुन्न पड़ जाती है कि दूसरे दिन सुबह ऐसा ही लगता है कि बॉस, कुछ सुनाई क्यों नहीं दे रहा ? (असल में तो आठ बजे का अलार्म नहीं सुनाई दिया था।)\nयदि डॉक्टर ‘घटनास्थल’ पर मौजूद",
    target_lines=29,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1398, 390, 1398, 1340, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1406, 388, 1704, 1342,
    text="हों तो उन्हें ढूंढकर ट्रीटमेंट लिया जा सके न ?\n* * *\nपांच प्रतिशत पास गले के डॉक्टरों के लिए रिजर्व रखवाओ ! क्योंकि स्पीकरों के भयंकर शोरगुल में अपने परिचितों के साथ मजबूरी में ऊंची आवाज में दो मिनट बातें करें, उसी में तो गले छिल जाते हैं !\nदूसरा, ये डॉक्टर ‘ऑन-द-स्पॉट’ ट्रीटमेंट में १५ प्रतिशत डिस्काउंट दें तो भी बहुत है !\n* * *\nअच्छा, २५ प्रतिशत पास कॉलेजियनों के लिए, १२ प्रतिशत सीनियर सिटीजनों के लिए, १० प्रतिशत छोटे बच्चों के लिए और दो प्रतिशत पास महिला पुलिस को दो। ठीक है ?\n* * *\nऔर आखिर में... ५० प्रतिशत केवल ‘देखने के लिए’ आने वाली भीड़ के लिए आरक्षित रखो !\nएक मिनट ! आप कहेंगे कि मन्नूभाई, आप ऑलरेडी ११४ प्रतिशत तो गिनवा चुके हैं ! उसमें ऊपर से दूसरे ५० प्रतिशत कहां से घुसाने हैं ?\nतो मित्रों, आयोजक भी यही कहते हैं न ? वे अतिरिक्त ५० प्रतिशत को एंट्री दे देते हैं, उसी में तो गरबा खेलने की जगह बचती नहीं !\n- मन्नू शेखचिल्ली",
    target_lines=29,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. STORY 4: SOLAR POWER CUT (COLS 6-8 TOP)
# ==============================================================================
print("Building Story 4 (Solar Power Cut, Cols 6-8 Top)...")
place_exact_display_lines(
    1744, 200, 2715, 246,
    lines=["दो मेगावाट से अधिक के सोलर प्लांट से बिजली उत्पादन पर अंकुश"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1744, 252, 2715, 412,
    lines=[
        "सरकार को सोलर पावर में रुचि नहीं, निजी",
        "बिजली कंपनी के लाभार्थ सोलर पर कटौती"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 418, 2222, 594,
    text="(प्रतिनिधि की ओर से) अहमदाबाद, सोमवार\nबिजली की कमी के कारण बिजली संकट की ओर धकेले जा रहे गुजरात की सरकार आश्चर्यजनक रूप से सौर ऊर्जा से बिजली पैदा करने वालों को २० प्रतिशत से लेकर ७० प्रतिशत कम बिजली पैदा करने को मजबूर कर रही है। चौंकाने वाली बात तो यह है कि बिना प्रदूषण के पैदा होने वाली और सूरज तपते समय बिजली उत्पादन रोका न जा सकने के बावजूद गुजरात सरकार की तरफ से दो मेगावाट से",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 420, 2229, 592, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 418, 2715, 594,
    text="अधिक बिजली पैदा करने की क्षमता रखने वाले उत्पादकों को उनकी कुल उत्पादन क्षमता के ७० प्रतिशत से लेकर २० प्रतिशत जितनी कम बिजली पैदा करने को मजबूर किया जा रहा है। सौर ऊर्जा से बिजली पैदा करने वालों के पास कम बिजली पैदा करने का कोई रास्ता नहीं है और स्टोरेज करने का भी कोई रास्ता न होने के बावजूद गुजरात सरकार की बिजली कंपनियां उन्हें ई-मेल भेजकर केवल ३०, ४०, ५० या ८० प्रतिशत बिजली का ही उत्पादन करने को कह रही हैं।",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 602, 2715, 720,
    lines=[
        "सोलर पावर की बिजली का संग्रह न हो सकने के बावजूद",
        "उत्पादकों को बिजली उत्पादन में कटौती करने का सरकारी निर्देश"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 726, 2052, 1348,
    text="दूसरी तरफ गुजरात के उद्योगों और रिहायशी बिजली उपभोक्ताओं को प्रति यूनिट रु. ८ के भाव की बिजली के खर्च का बोझ उठाना पड़ रहा है। दो मेगावाट से अधिक की उत्पादन क्षमता रखने वाले गुजरात के १५०० से २००० जितने सौर ऊर्जा उत्पादक सरकारी बिजली आपूर्ति कंपनियों को प्रति यूनिट केवल रु. २.७६ से २.९५ के भाव पर बिजली दे रहे होने के बावजूद और उनकी बिजली खरीद लेने का सरकार द्वारा करार किए जाने के बावजूद निजी बिजली कंपनियों को मालामाल कराने के लिए सौर ऊर्जा से बिजली पैदा करने वालों को कम बिजली का उत्पादन करने को मजबूर किया जा रहा है। अभी १८ अक्टूबर को ही उन्हें अपनी कुल क्षमता से २० प्रतिशत कम बिजली पैदा करने का आदेश दिया गया था। इससे पहले तो उन्हें कुल क्षमता के ७०",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2064, 728, 2064, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 726, 2382, 1072,
    text="प्रतिशत से लेकर ५० प्रतिशत कम उत्पादन करने के आदेश दिए गए थे। दूसरी तरफ उनकी बिजली का संग्रह न हो सकने के कारण वह बर्बाद हो रही है। १५०० से २००० इकाइयों को मिलाकर रोजाना लगभग १ करोड़ यूनिट बिजली की बर्बादी हो रही है। २३ सितंबर को लगभग १५०० से २५०० जितने सोलर पावर जनरेटर्स को मेल भेजकर उनकी सोलर बिजली के",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_line(2395, 728, 2395, 1072, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 726, 2715, 1072,
    text="उत्पादन की सप्लाई ५० प्रतिशत कम कर देने को कहा गया है। गुजरात की बिजली कंपनियों को वडोदरा से स्टेट लेवल डिस्पैच सेंटर द्वारा किए गए मेल को पढ़ने से स्पष्ट होता है कि २३ सितंबर २०२६ से पहले इस बिजली सप्लाई में ७० प्रतिशत कटौती करने का मैसेज दिया गया था। इस ७० प्रतिशत बिजली सप्लाई कट में से अब ५० प्रतिशत बिजली सप्लाई कट करने का निर्देश है।",
    target_lines=11,
    first_indent_pt=0.0,
)
draw_line(2076, 1080, 2715, 1080, swatch="[Black]", weight_pt=0.85)

# ==============================================================================
# 5. STORY 5: SEVA SETU (COLS 7-8 MIDDLE)
# ==============================================================================
print("Building Story 5 (Seva Setu, Cols 7-8 Middle)...")
place_exact_display_lines(
    2076, 1088, 2715, 1134,
    lines=["बिगड़ी हुई प्रशासनिक कार्यप्रणाली का चित्रण"],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    2076, 1140, 2715, 1280,
    lines=[
        "सरकारी लाभ पाने के लिए २२,२६४",
        "लोगों को सेवा सेतु की राह देखनी पड़ी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1286, 2715, 1404,
    text="अहमदाबाद, सोमवार\nअहमदाबाद शहर में अब तक आयोजित सेवा सेतु के ७ कार्यक्रमों में २२,२६४ आवेदनों का निपटारा किए जाने का दावा किया गया है। जिसका सीधा मतलब यह भी होता है कि विभिन्न सरकारी लाभ पाने के लिए इतनी बड़ी संख्या में लोगों को सेवा सेतु कार्यक्रम की राह देखने को मजबूर होना पड़ा था!",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    2076, 1410, 2715, 1510,
    lines=[
        "९६०० आवेदन केवल हेल्थ वेलनेस कार्ड के! कार्यक्रम को",
        "जबरन सफल दिखाने रोजमर्रा के आवेदन रोके गए"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    2076, 1516, 2382, 2132,
    text="लोगों को सरकारी सेवाओं का त्वरित लाभ मिले इसके लिए सरकार ने सेवा सेतु कार्यक्रम शुरू किए हैं। परंतु अहमदाबाद में ये सेवा सेतु कार्यक्रम बिगड़ी हुई सरकारी सेवाओं का चित्रण प्रस्तुत कर रहे हैं। दूसरी तरफ ऐसे कार्यक्रमों को जबरन सफल बनाने के लिए कार्यालयों में रोजाना आने वाले आवेदनों को भी रोककर रखकर बाद में सेवा सेतु के दौरान प्रक्रिया की जा रही है! जिसके कारण आवेदकों को उल्टे अधिक परेशानी झेलनी पड़ती है। वैसे तो सेवा सेतु में ५६ प्रकार की सरकारी, अर्ध-सरकारी सेवाएं शामिल किए जाने का दावा भी किया जाता है। परंतु अहमदाबाद के कार्यक्रमों के कुल २२ हजार आवेदनों में से ९६०४ तो केवल हेल्थ वेलनेस कार्ड के थे! यानी कि",
    target_lines=19,
    first_indent_pt=9.0,
)
draw_line(2395, 1518, 2395, 2132, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1516, 2715, 1618,
    text="आंकड़े बड़े दिखाने के लिए आरोग्य कार्ड की सेवाओं का उपयोग हो रहा है। हकीकत में अधिकारी नियमित रूप से",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_box(2408, 1624, 2715, 2020, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_display_lines(
    2416, 1630, 2706, 1712,
    lines=["सेवा सेतु के नाम पर", "आवेदनों के आंकड़े"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2416, 1718, 2706, 2012,
    text="पूर्व का संयुक्त कार्यक्रम  १०२२७\nपश्चिम संयुक्त कार्यक्रम  ६१४९\nउत्तर-पश्चिम जोन  ७२८\nपूर्व जोन  १०९६\nमध्य जोन  १२६०\nपश्चिम जोन  १४८५",
    target_lines=6,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 2026, 2715, 2132,
    text="उचित काम करें इसका ध्यान रखने का फर्ज जनप्रतिनिधि निभाएं तो सेवा सेतु के आयोजन की जरूरत ही नहीं है।",
    target_lines=3,
    first_indent_pt=0.0,
)

# ==============================================================================
# 6. STORY 6: DOUBLE DECKER FREIGHT TRAIN (COLS 3-4 MIDDLE)
# ==============================================================================
print("Building Story 6 (Double Decker Freight Train, Cols 3-4 Middle)...")
draw_line(746, 1356, 2052, 1356, swatch="[Black]", weight_pt=0.85)
place_exact_display_lines(
    746, 1364, 1382, 1406,
    lines=["माल परिवहन की क्षमता बढ़ाने के लिए एक और कदम"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    746, 1412, 1382, 1542,
    lines=[
        "मुंबई-अहमदाबाद के बीच १.५ किमी",
        "लंबी डबल डेकर मालगाड़ी दौड़ी"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1548, 1382, 1676,
    text="अहमदाबाद, सोमवार\nमुंबई और अहमदाबाद गुजरात के व्यापार, उद्योग और माल परिवहन के लिए महत्वपूर्ण केंद्र हैं। इन दोनों शहरों के बीच माल की आवाजाही तेज और सरल बने इसके लिए रेलवे ने डेढ़ किलोमीटर लंबी डबल डेकर कंटेनर मालगाड़ी दौड़ाकर माल परिवहन की क्षमता बढ़ाने का महत्वपूर्ण कदम उठाया है।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    746, 1682, 1382, 1782,
    lines=[
        "३६० कंटेनर वाली मालगाड़ी में १२००० और",
        "बीच में ९००० हॉर्सपावर वाले दो इंजन जुड़े"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    746, 1788, 1050, 2175,
    text="प्राप्त जानकारी के अनुसार, हाल ही में रेलवे द्वारा मुंबई-अहमदाबाद मार्ग पर लगभग १.५ किलोमीटर लंबी डबल डेकर कंटेनर मालगाड़ी दौड़ाई गई थी। जिसमें पहली बार दो स्तरों पर कुल ३६० कंटेनर ले जाए गए थे। इस मालगाड़ी को खींचने के लिए आगे १२,००० हॉर्सपावर का ‘मेक इन इंडिया’ का इंजन और बीच में ९,००० हॉर्सपावर का दूसरा इंजन जोड़ा गया था। गुजरात के उद्योगों और",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1064, 1790, 1064, 2175, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 1788, 1382, 2175,
    text="व्यापार के लिए मुंबई महत्वपूर्ण बाजार और बंदरगाहों के साथ जुड़ाव प्रदान करता है। जबकि अहमदाबाद आसपास के क्षेत्रों में औद्योगिक और व्यापारिक गतिविधियों का बड़ा केंद्र होने से इलेक्ट्रिक इंजन के साथ डबल स्तर की मालगाड़ी से दोनों शहरों के बीच माल की आवाजाही में सुगमता आ सकती है। हालांकि, परिवहन का खर्च कितना घटेगा और उसका लाभ गुजरात के व्यापारियों को कितना मिलेगा यह देखना रहेगा।",
    target_lines=13,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. STORY 7: MBBS EXTRA ATTEMPT (COLS 5-6 MIDDLE)
# ==============================================================================
print("Building Story 7 (MBBS Extra Attempt, Cols 5-6 Middle)...")
draw_line(1396, 1360, 1396, 2304, swatch="[Black]", weight_pt=0.75)
place_exact_display_lines(
    1412, 1364, 2052, 1406,
    lines=["वर्ष २०१९-२० और उसके बाद प्रवेश लेने वाले"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1412, 1412, 2052, 1542,
    lines=[
        "MBBS के अनुत्तीर्ण विद्यार्थियों को",
        "पास होने अब एक और अवसर मिलेगा"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1548, 2052, 1676,
    text="अहमदाबाद, सोमवार\nएमबीबीएस के विद्यार्थियों को कोविड सहित की परिस्थितियों को ध्यान में रखकर फर्स्ट प्रोफेशनल एमबीबीएस एग्जाम पास करने के लिए अब एक और अवसर मिलेगा। २०१९-२० में और उसके बाद के वर्षों में प्रवेश पाने वाले विद्यार्थियों को कुल पांच अवसर फाइनल परीक्षा पास करने के लिए मिलेंगे।",
    target_lines=4,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1412, 1682, 2052, 1782,
    lines=[
        "पहले कमीशन द्वारा फर्स्ट एमबीबीएस क्लियर",
        "करने के लिए चार अवसर दिए जाते थे परंतु अब पांच मिलेंगे"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1412, 1788, 1718, 2302,
    text="नेशनल मेडिकल कमीशन ने कोविड ड्यूटी तथा स्वास्थ्य संबंधी मुश्किलों को ध्यान में रखकर पहले २०१९-२० और २०२०-२१ में एमबीबीएस में प्रवेश लेने वाले विद्यार्थियों को फर्स्ट एमबीबीएस पास करने के लिए अतिरिक्त एक अवसर दिया था। परंतु उसके बाद भी अन्य वर्ष के विद्यार्थियों को लेकर विश्वविद्यालयों-कॉलेजों की तरफ से अभ्यावेदन कमीशन को किए गए थे। जिसके चलते नेशनल मेडिकल कमीशन ने २०१९-२० और उसके बाद के वर्षों में एमबीबीएस में प्रवेश पाने वाले विद्यार्थियों को फर्स्ट एमबीबीएस क्लियर करने के लिए पांचवां अटेम्प्ट दिया है।\nनियम के अनुसार विद्यार्थियों को चार अवसर मिलते हैं परंतु यह खास पांचवीं बार का",
    target_lines=16,
    first_indent_pt=9.0,
)
draw_line(1731, 1790, 1731, 2302, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1744, 1788, 2052, 2060,
    text="अवसर कुछ नियमों-शर्तों के अधीन ही विद्यार्थियों को मिलेगा। जिसमें विद्यार्थी को पहले पांचवां अवसर मिला न होना चाहिए या लिया न हो तभी यह अवसर मिलेगा। इसके अलावा विवि या कॉलेज ने विद्यार्थी का प्रवेश रद्द किया न होना चाहिए तथा चार वर्ष पूरे किए होने चाहिए। यह अवसर मिलने के बाद इंटर्नशिप के साथ कुल कोर्स की कुल समयावधि दस वर्ष से बढ़नी नहीं चाहिए।",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_box(1744, 2068, 2052, 2302, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1752, 2076, 2044, 2294,
    text="पाठक ध्यान दें कि किसी भी विज्ञापन में बताई गई जानकारी की सत्यता के संबंध में हम कोई गारंटी नहीं देते हैं। पाठकों को अपने स्तर पर पर्याप्त जांच-पड़ताल करके उचित निर्णय लेना रहेगा।\n- विज्ञापन मैनेजर",
    target_lines=7,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. PLACE BOTTOM DRAMA ADS, PUBLIC NOTICES & IMPRINT BLOCKS (100% EDITABLE TEXT)
# ==============================================================================
print("Placing Page 4 Drama Ads, Public Notices & Imprint (100% Editable Hindi Text)...")
place_png(75, 1210, 726, 3810, "ads_col12_bottom.png")


def place_public_notice_2col(x1_px, y1_px, x2_px, y2_px, left_text, right_text, left_lines=38, right_lines=40, header_h=54):
    x_mid = (x1_px + x2_px) // 2
    draw_box(x1_px, y1_px, x2_px, y2_px, stroke_swatch="[Black]", stroke_weight_pt=1.8)
    draw_box(x1_px, y1_px, x_mid - 4, y1_px + header_h, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
    place_exact_display_lines(
        x1_px + 10, y1_px + 6, x_mid - 14, y1_px + header_h - 4,
        lines=["जाहिर नोटिस"],
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
        hi_pt=10.5,
        lo_pt=6.8,
    )
    place_exact_body_column(
        x_mid + 8, y1_px + 10, x2_px - 10, y2_px - 8,
        text=right_text,
        target_lines=right_lines,
        first_indent_pt=0.0,
        hi_pt=10.5,
        lo_pt=6.8,
    )


# Notice 1: Cols 3-4 Bottom (746..1382, 2200..3792)
draw_line(746, 2184, 1382, 2184, swatch="[Black]", weight_pt=0.85)
place_public_notice_2col(
    746, 2200, 1382, 3792,
    left_text=(
        "एतद्द्वारा आम जनता को सूचित किया जाता है कि रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-२ (वाडज) के तालुका साबरमती के गांव मोजे चांदखेड़ा की सीम के री-सर्वे के अनुसार ब्लॉक/सर्वे नं. ४७८ (पुराना ब्लॉक/सर्वे नं. २०६/१) की ५०५९ चौ.मी. जमीन पर स्थित 'श्रीनाथ बंग्लोज' के नाम से जानी जाने वाली स्कीम में स्थित प्लॉट नं. १३ की २२५ चौ.वार यानी १८८.१२ चौ.मी. जमीन तथा उसमें स्थित आवासीय निर्माण सहित की संपत्ति रमेशभाई मणिलाल पटेल और शकुंतलाबेन रमेशभाई पटेल के संयुक्त स्वामित्व, कब्जे, भोगवटे की तथा सभी प्रकार के बोझों से मुक्त होने का बताकर हमारे मुवक्किल को बेचने का तय किया है और हमारे मुवक्किल ने उक्त संपत्ति के टाइटल क्लियर और मार्केटेबल होने के प्रमाणपत्र की हमसे मांग की है।\n"
        "उक्त संपत्ति पर किसी भी बैंक, वित्तीय संस्था, फर्म या व्यक्ति का किसी भी प्रकार का हिस्सा, हक, हित, दावा, अलाखा, बोझ, लियन या बानाखत हक"
    ),
    right_text=(
        "निहित हो तो इस नोटिस के प्रकाशित होने से दिन-७ (सात) में प्रमाणित सबूतों सहित नीचे के पते पर रजि.ए.डी. से लिखित सूचना दें और यदि ऐसा करने में चूक या विलंब होगा तो उक्त संपत्ति पर अन्य किसी का किसी भी प्रकार का हिस्सा, हक, हित या बोझ नहीं है और यदि हो तो वह त्याग (वेव) दिया है ऐसा समझकर अवधि समाप्त होने पर उक्त संपत्ति का टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा और उसके बाद किसी की किसी भी प्रकार की आपत्ति नहीं चलेगी, आम जनता इसका ध्यान रखे।\n"
        "तारीख : २०/१०/२०२६\n"
        "राजेश के. पटेल (एडवोकेट)\n"
        "ऑफिस : ३०४, तीसरी मंजिल, सत्यमेव एमिनेंस, साइंस सिटी रोड, सोला, अहमदाबाद-३८००६०।\n"
        "मो. नं. ९८२५० ४५६७८"
    ),
    left_lines=38,
    right_lines=40,
)

# Col 5 Notice (1-col) + Col 6 English Imprint + Cols 5-6 Bottom Hindi Imprint
draw_box(1412, 2314, 1724, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
draw_box(1412, 2314, 1724, 2368, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1420, 2320, 1716, 2364,
    lines=["जाहिर नोटिस"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1420, 2374, 1716, 3186,
    text=(
        "डिस्ट्रिक्ट गांधीनगर सब-डिस्ट्रिक्ट कलोल तालुका के मोजे सईज गांव की सीम के ब्लॉक/सर्वे नं. १४२८ की गैर-कृषि जमीन पर स्थित आवासीय योजना में स्थित प्लॉट नं. २४ की १८० चौ.वार की संपत्ति पटेल कनुभाई मगनभाई के स्वतंत्र स्वामित्व कब्जे भोगवटे की होने का बताकर हमसे टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है। किसी को आपत्ति या हक हो तो दिन-७ में नीचे के पते पर रजि.ए.डी. से सूचना दें।\n"
        "ता. २०/१०/२०२६\n"
        "अश्विन जे. पटेल (एडवोकेट)\n"
        "नवरंगपुरा, अहमदाबाद।"
    ),
    target_lines=24,
    first_indent_pt=0.0,
    hi_pt=10.2,
    lo_pt=6.8,
)

# Col 6 Imprint Box (1738..2052, 2314..3194)
draw_box(1738, 2314, 2052, 3194, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1748, 2324, 2042, 3184,
    text=(
        "आस-पास (द गुजरात समाचार हिंदी)\n"
        "लोक प्रकाशन लिमिटेड की ओर से श्रेयांस एस. शाह द्वारा मुद्रित एवं प्रकाशित तथा लोक प्रकाशन लिमिटेड, गुजरात समाचार भवन, खानपुर, अहमदाबाद में मुद्रित एवं गुजरात समाचार भवन, खानपुर, अहमदाबाद से प्रकाशित।\n"
        "संपादक : श्रेयांस एस. शाह\n"
        "(पीआरबी अधिनियम के तहत समाचारों के चयन के लिए उत्तरदायी)।\n"
        "आरएनआई नं. १६०९/५७।\n"
        "फोन : (०७९) २५५०४०१०"
    ),
    target_lines=22,
    font_style="Bold",
    align="left",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)

# Cols 5-6 Bottom Hindi Imprint Box (1412..2052, 3206..3792)
draw_box(1412, 3206, 2052, 3792, stroke_swatch="[Black]", stroke_weight_pt=1.8)
place_exact_body_column(
    1422, 3216, 1724, 3782,
    text=(
        "लोक प्रकाशन लिमिटेड की ओर से मुद्रक एवं प्रकाशक : श्रेयांस शांतिलाल शाह\n"
        "लोक प्रकाशन लिमिटेड के गुजरात समाचार भवन, खानपुर, अहमदाबाद-३८०००१ में मुद्रित और वहीं से प्रकाशित किया।\n"
        "संपादक : श्रेयांस शांतिलाल शाह"
    ),
    target_lines=14,
    font_style="Bold",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)
draw_line(1732, 3216, 1732, 3782, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1742, 3216, 2042, 3782,
    text=(
        "(पी.आर.बी. एक्ट के अंतर्गत समाचारों के चयन के लिए उत्तरदायी)\n"
        "हेड ऑफिस : गुजरात समाचार भवन, खानपुर, अहमदाबाद-३८०००१।\n"
        "फोन : (०७९) २५५०४०१० (१० लाइन)\n"
        "RNI No. 1609/57"
    ),
    target_lines=14,
    font_style="Bold",
    first_indent_pt=0.0,
    hi_pt=10.0,
    lo_pt=6.8,
)

# Cols 7-8 Bottom Two Public Notices (2076..2715, 2152..3792)
draw_line(2076, 2142, 2715, 2142, swatch="[Black]", weight_pt=0.85)
place_public_notice_2col(
    2076, 2154, 2715, 2964,
    left_text=(
        "मोजे - गोता\n"
        "डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-८ (सोला) तालुका घाटलोडिया के गांव मोजे गोता की सीम के ब्लॉक/सर्वे नं. २१५, टी.पी. स्कीम नं. ३२ के फा.प्लॉट नं. ५४ की गैर-कृषि जमीन पर स्थित स्कीम में फ्लैट नं. ए/४०२ की संपत्ति पटेल दिनेशभाई रमणलाल के स्वतंत्र स्वामित्व कब्जे भोगवटे की तथा बोझ रहित होने का बताकर हमारे मुवक्किल को बेचने का तय किया है और टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है।"
    ),
    right_text=(
        "उक्त संपत्ति पर किसी का किसी भी प्रकार का हिस्सा, हक, हित, दावा या बोझ हो तो इस नोटिस के प्रकाशित होने से दिन-७ में लिखित सबूतों सहित रजि.ए.डी. से नीचे के पते पर सूचना दें। यदि ऐसा नहीं किया गया तो किसी का किसी भी प्रकार का हक नहीं है और हो तो वह त्याग दिया है ऐसा समझकर टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा।\n"
        "ता. २०/१०/२०२६\n"
        "केतन एम. पटेल (एडवोकेट)\n"
        "सोला रोड, अहमदाबाद।"
    ),
    left_lines=22,
    right_lines=24,
)
place_public_notice_2col(
    2076, 2978, 2715, 3792,
    left_text=(
        "मोजे - बोपल\n"
        "रजिस्ट्रेशन डिस्ट्रिक्ट अहमदाबाद सब-डिस्ट्रिक्ट अहमदाबाद-९ (बोपल) तालुका दस्क्रोई के गांव मोजे बोपल की सीम के ब्लॉक नं. ४१२, टी.पी. स्कीम नं. ३ के फा.प्लॉट नं. ८८ की जमीन पर स्थित आवासीय योजना में बंगला नं. १२ की संपत्ति शाह विनोदचंद्र चिमनलाल के स्वतंत्र स्वामित्व कब्जे भोगवटे की तथा सभी प्रकार के बोझों से मुक्त होने का बताकर हमसे टाइटल क्लीयरेंस सर्टिफिकेट की मांग की है।"
    ),
    right_text=(
        "उक्त संपत्ति पर किसी का किसी भी प्रकार का हिस्सा, हक, हित, दावा या बोझ हो तो इस नोटिस के प्रकाशित होने से दिन-७ में लिखित सबूतों सहित रजि.ए.डी. से नीचे के पते पर सूचना दें। अवधि समाप्त होने पर किसी की आपत्ति नहीं चलेगी और टाइटल क्लीयरेंस सर्टिफिकेट जारी किया जाएगा।\n"
        "ता. २०/१०/२०२६\n"
        "निलेश आर. शाह (एडवोकेट)\n"
        "बोपल, अहमदाबाद।"
    ),
    left_lines=22,
    right_lines=24,
)

place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_04_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_04_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_04_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_04_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_04_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
