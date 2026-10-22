from gs_hindi_running_header import build_hindi_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME HINDI PAGE 8 BUILDER FOR AAS-PAAS (HINDI GUJARAT SAMACHAR)
=============================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable Hindi Text ('DB Madhurima', 'DB Hindi Mast', 'DB Hindi')
  across all 6 Editorial & Column Features on Page 8:
  1. संपादकीय (Editorial): कॉर्पोरेट कृषि का प्रभात (Cols 1-2 Top)
  2. अल्पविराम: बदला हुआ मौसम अब दुनिया को चैन से बैठने नहीं देगा (Cols 3-6 Top)
  3. टू द पॉइंट (अजित पोपट): जो दिल में था वह जुबान पर आया, हमें तो तख्तापलट करना है... (Cols 7-8 Top)
  4. प्रसंगपट: गूगल मैप का स्वदेशी विकल्प मैपल्स: परंतु मार्केटिंग नहीं (Cols 1-3 Bottom)
  5. बोझ बिना की मौज (अक्षय अंताणी): कौए मिलते हैं मुश्किल से, इसलिए बढ़ती जाती है डिमांड (Cols 4-7 Bottom)
  6. कल्पवृक्ष: सुविचार (Col 8 Bottom)
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
        "title": "आस-पास (हिंदी गुजरात समाचार) — Page 08 (100% Same-to-Same Editable Hindi)"
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
print("Placing Page 8 Hindi Running Header...")
build_hindi_running_header(8, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. EDITORIAL (संपादकीय): कॉर्पोरेट कृषि का प्रभात (COLS 1-2 TOP)
# ==============================================================================
print("Building Editorial (Corporate Agriculture Dawn, Cols 1-2 Top)...")
draw_box(82, 194, 720, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.8)
# Editable Hindi Editorial Masthead (replacing editorial_masthead.png)
draw_box(85, 196, 717, 294, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    96, 202, 706, 290,
    lines=["आस-पास • संपादकीय"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.88,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
draw_box(85, 294, 717, 336, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    96, 298, 706, 332,
    lines=["संपादक : शांतिलाल शाह • मंगलवार, २० अक्टूबर २०२६"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    94, 344, 708, 412,
    lines=["कॉर्पोरेट कृषि का प्रभात"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    92, 420, 710, 2066,
    text=(
        "पिछले जो दो तिमाही परिणाम आए हैं, उन्होंने कृषि और मूल्यवर्धित कृषि उत्पादों के लिए आशाजनक चित्र प्रस्तुत किया है। भारत में कृषि उत्पादों से जुड़ी कॉर्पोरेट कंपनियों में अचानक वृद्धि हुई है और उनमें से अनेक कंपनियां अब अंतरराष्ट्रीय लिंकेज रखने लगी हैं। देश में नए वित्त वर्ष का प्रारंभ हुए समय बीत चुका है और इस अवधि में गंगा-यमुना में बहुत पानी बह चुका है। वसंत के फूलों के रंगों की तरह अर्थव्यवस्था के अनेक रंग इस वर्ष जनता को देखने हैं। भारत इस समय काल और परिस्थितियों के एक ऐसे तिराहे पर आकर खड़ा देश है जिसके सामने राष्ट्रीय जीवन के अनेक क्षेत्रों में कई चुनौतियां खड़ी हैं। कैसा भी नेतृत्व हो, इन चुनौतियों से पार पाना आसान काम नहीं है। अफ्रीकी देशों सहित अनेक दरिद्र राष्ट्र भीषण मंदी में मदद के लिए भारत की ओर टकटकी लगाए बैठे हैं।\n"
        "घर के बच्चों को भूखा न रहना पड़े, इसलिए सरकार परायों को आटा देने में स्वाभाविक विलंब कर रही है। फिर भी आज तक लाखों टन अनाज का निर्यात हुआ है और उपहार में भी दिया गया है। अल्पकालिक इस खेल का इतिहास बहुत लंबा है। केंद्र सरकार द्वारा चावल की कुछ किस्मों के निर्यात पर प्रतिबंध लगाने का मुख्य कारण अनियमित मानसून होता है। उत्तराखंड और हिमाचल प्रदेश में बारिश शब्द सुनते ही लोग थर-थर कांपने लगते हैं, ऐसा उनका इस बार का अनुभव है। सरकार पीड़ितों की मदद करती है परंतु पूरी दुनिया फिर से बसानी पड़े तो क्या होता है, यह प्रलय का शिकार बने लोगों से पूछें तो पता चले। जरूरत के मुकाबले चालू वर्ष में अनाज-दालों का उत्पादन बहुत कम आने वाला है। अब इस मानसून की विदाई के बाद देर से शुरू हुए रबी सीजन पर बहुत कुछ निर्भर है। पिछले सीजन की कमी के कारण जीरा, प्याज, तिलहन के दाम आने वाली सर्दियों में जनता को व्याकुल करेंगे।\n"
        "मौसम में बदलाव के कारण बारिश का अंतिम दौर घने बादलों और वर्षा से भरा रहा, परंतु जो खेत बह गए हैं उन्हें गंभीर नुकसान हुआ है। देश में खरीफ की फसल अच्छी हो तभी उसके बाद रबी की फसल भी अच्छी होती है। इसलिए चालू वित्त वर्ष कृषि क्षेत्र के लिए फलदायी तो रहने वाला है, परंतु उसी के परिणामस्वरूप बाजार में रुपया घूमने लगेगा और अन्य औद्योगिक क्षेत्रों में भी इस वर्ष तेजी का असर दिखाई देगा। उस तेजी की वास्तव में अब शुरुआत हो चुकी है। दुनिया भर में जब मंदी का सन्नाटा पसरा हो तब भारतीय अर्थव्यवस्था तेजी का माहौल लेकर आए, यह एशिया के विभिन्न देशों के लिए आश्चर्यजनक है। चीन से वापस लौट रहे अनेक निवेशक अपनी पूंजी के साथ अब भारत में उतरने लगे हैं। आश्चर्य की बात यह है कि आने वाले विदेशी निवेशकों को भारतीय उद्योगों में अब कृषि से जुड़ी औद्योगिक गतिविधियों में अधिक रुचि है। यह एक शुभ संकेत है।\n"
        "रिजर्व बैंक के गवर्नर ने अब शुरू हो रहे रबी सीजन के लिए १०.५ प्रतिशत का विकास अनुमान रखा है। हालांकि पहली नजर में यह कठिन लगता है, परंतु वर्ष २०२५-२०२६ के बैकलॉग की भरपाई करने के लिए उद्योग और सेवाएं जिस तरह काम में जुटे दिखते हैं, उसे देखते हुए यह बिल्कुल असंभव नहीं है। मिस्टर शक्तिकांत पहले भी कह चुके हैं कि भारतीय अर्थव्यवस्था की गाड़ी अब पटरी पर आ गई है और सुधारवादी दृष्टिकोण के माध्यम से अर्थव्यवस्था में चढ़ती कला का चंद्रमा दिखाई देता है। देश में सरकार लगातार गुलाबी चित्र पेश करना चाहती है परंतु छोटे परिवारों के पर्स-बटुए और छोटे तथा खाली हो गए हैं। अर्थव्यवस्था जब संकट की घाटी से गुजर रही है, तब प्राकृतिक कृपा सरीखी बारिश यदि सकारात्मक रहे तो कृषि क्षेत्र की मदद से अर्थव्यवस्था अधिक गतिमान बनेगी। केंद्र सरकार ने देश के अधिक डेंगू संक्रमित १२ राज्यों के साथ उच्चस्तरीय बैठक कर सख्त कदम उठाने का अनुरोध किया है।\n"
        "स्टार्ट-अप की योजना लगभग सभी सेक्टरों में विफलता को प्राप्त हुई है। आरंभ में शूरवीर जैसा रूप रखने वाले स्टार्ट-अप इंडिया प्रोजेक्ट की अकाल मृत्यु हो गई, ऐसा कहना अतिशयोक्ति नहीं माना जाएगा। वर्ष २०१५ में सभी भारतीय स्टार्ट-अप प्रोजेक्ट्स ने देश-विदेश से साढ़े सात अरब डॉलर की फंडिंग जुटाई थी, जो उसके अगले वर्ष यानी २०१६ में घटकर साढ़े तीन अरब डॉलर रह गई थी। वर्ष २०१६ की नोटबंदी ने तो आधे से अधिक स्टार्ट-अप की बुनियाद ही तोड़ डाली थी।"
    ),
    target_lines=54,
    font_style="Bold",
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. ALPVIRAM: बदला हुआ मौसम अब दुनिया को चैन से बैठने नहीं देगा (COLS 3-6 TOP)
# ==============================================================================
print("Building Alpviram (Climate Change Essay, Cols 3-6 Top)...")
draw_box(736, 194, 2060, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    746, 200, 2050, 304,
    lines=["बदला हुआ मौसम अब दुनिया को चैन से बैठने नहीं देगा"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    746, 312, 1051, 2066,
    text=(
        "उत्तर भारत और दक्षिण के कुछ राज्यों में इस समय मूसलाधार बारिश जारी है। शरद पूर्णिमा नजदीक आ रही है जो वास्तव में स्वच्छ आकाश का मौसम है। गुजरात के ऊपर भी आजकल में हाथियों की सेना जैसे विराट बादल छा जाने वाले हैं। मौसम रंग बदल रहा है। सुनना अच्छा न लगे तो भी यह सत्य है कि प्रकृति ने करवट बदल ली है। जापान और यूरोप ने पिछले वर्ष ऐसी उमस और गर्मी का अनुभव किया जिसकी कभी कल्पना भी नहीं की थी। उसके बाद से बारिश और भीषण तूफान अब तक जारी हैं। पिछले एक वर्ष में पृथ्वी पर आए चक्रवातों का औसत पिछले पचास वर्षों में सर्वाधिक है। भारत में जहां भी बारिश हो वहां बेहिसाब हो, ऐसे हालात स्थायी हो गए हैं।\n"
        "पूर्वी भारत के लिए मानसून एक आपदा बन गया है। वास्तव में व्यक्तिगत रूप से प्रत्येक मनुष्य आत्ममंथन करे कि पिछले वर्षों में कोरोना के आगमन के बाद उसने अपनी जीवनशैली को कितना बदला, तो समझ आएगा कि जन्मजात आदतें थोड़े से झटके खाने से नहीं बदलतीं। मृत्यु के भय से डरते-डरते रोज तब काढ़े गटके गए, वह कोई प्रकृति या पर्यावरण के साथ दोस्ती नहीं थी। शरीर को नुकसान पहुंचाने वाले जो भी आहार हैं उन्हें रोकने की बात बहुत शुरुआत में विश्व स्वास्थ्य संगठन ने कही थी। यदि ऐसे त्याज्य आहार का उपयोग रुके तभी उनका उत्पादन बंद होगा।\n"
        "सीमा से बाहर का आहार शरीर के भीतर दुर्घटना को न्योता देता है जिसे डॉक्टर ही देख या सुन सकते हैं। कोरोना ने इम्युनिटी को चुनौती दी है और औसत भारतीय जनता की इम्युनिटी की दुनिया आज सराहना करती है। हालांकि जितनी मौतें कोरोना के समय हुईं वह दुःखद हैं। आज भी डेंगू और हृदय रोग का औसत बहुत ऊंचा है। जिंदगी कम उम्र में सिमट जाए तब सपनों का एक लंबा कारवां भी दिवंगत हो जाता है। मृत्यु संसार का सबसे करारा आघात है। जिन्होंने आकस्मिक रूप से स्वजनों को खोया है उनके घरों पर आज भी शोक के बादल छाए दिखाई देते हैं।\n"
        "वैसे तो नई सदी के इस तीसरे दशक की शुरुआत ही हजारों-लाखों एकड़ के जलते जंगलों के बीच हुई थी। पचास हजार वर्ग किलोमीटर की आग से हुए नुकसान का हिसाब लगाने में ऑस्ट्रेलियाई"
    ),
    target_lines=58,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1078, 312, 1385, 520,
    text="सरकार को एक वर्ष लग गया। कच्छ और लातूर के भूकंप का हिसाब लगाने में हमें भी एक वर्ष लगा था। जरा भी चिंता किए बिना लोग जिंदगी गुजारते हैं। जो चिंता है वह अपनी निजी है, पर्यावरण की नहीं। हमारी मानसिकता ऐसी है कि ऑस्ट्रेलियाई",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 312, 1718, 520,
    text="पिछली बार पहली ऐसी सर्दी थी जिसने रूम हीटर की मार्केटिंग कर दी। कोई भी मौसम उसके अतिरेक के कारण आनंद नहीं दे सकता। ठंडी हवा के शौकीन ऐसे मौसम में यदि वन-प्रांतर में आवारागर्दी शुरू करें तो उन्हें स्वास्थ्य की चपत ही झेलनी",
    target_lines=7,
    first_indent_pt=9.0,
)
place_png(1078, 529, 1718, 966, "alpviram_illus.png")
place_exact_body_column(
    1078, 974, 1385, 1170,
    text="जंगल जले तो वह आग यहां थोड़े ही आने वाली है? परंतु वह आग यहां आ सकती है। क्योंकि यह आग पृथ्वी नामक हमारे साझा घर में लगी आग है। किसी दूसरे ग्रह या उपग्रह पर उठा यह धुआं नहीं है। संयुक्त राष्ट्र संघ",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 974, 1718, 1170,
    text="पड़ेगी। कुदरत का आनंद लेने का मजा भी कम होने लगा है क्योंकि उस कुदरत के पोषण और देखभाल में हमारा तो कोई योगदान नहीं है! प्रकृति उसी को रमणीय अनुभव और आह्लाद का अहसास कराएगी जो उसके अभिमुख",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1178, 1242, 1350,
    text="के अंतर्गत विश्व मौसम संगठन की नई रिपोर्टें वैसे तो मानव जाति की नींद उड़ाने के लिए पर्याप्त हैं।",
    target_lines=6,
    first_indent_pt=0.0,
)
# Editable Hindi Badge for Alpviram (replacing alpviram_badge.png)
draw_box(1249, 1179, 1552, 1343, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(1255, 1185, 1546, 1275, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1262, 1190, 1540, 1270,
    lines=["अल्पविराम"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
place_exact_display_lines(
    1262, 1282, 1540, 1335,
    lines=["विशेष संपादकीय चिंतन"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1558, 1178, 1718, 1350,
    text="होगा। पूरी जिंदगी प्राकृतिक संपदा के साथ केवल भोगवादी नीति रखने वालों को इसकी सजा भुगतनी पड़ेगी।",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1356, 1385, 1524,
    text="अब आने वाले सभी वर्षों में कुदरत रूठी रहने वाली है। एक बात ध्यान देने योग्य यह है कि हर आपदा में अब बचाव कार्य धीमा पड़ता जा रहा है। यानी प्राकृतिक संकट चरम रूप ले रहे हैं। अब",
    target_lines=6,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1356, 1718, 1524,
    text="पिछली सर्दियों में मध्यम वर्ग और किराए के मकानों में रहने वाले लोग दौड़-दौड़ कर रूम हीटर ले आए थे। गैस गीजर और इलेक्ट्रिक गीजर से जुड़ी दुर्घटनाएं बार-बार वायरल होने के",
    target_lines=6,
    first_indent_pt=9.0,
)
draw_box(1089, 1531, 1712, 1757, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1100, 1538, 1700, 1750,
    lines=[
        "कुदरत के मिजाज में आए परिवर्तन को समझ",
        "लेने के बाद समय रहते सावधान होने की यह घड़ी",
        "है। कैलेंडर में दिखने वाले महीनों और वातावरण",
        "के बीच की संगतता अब न के बराबर दिखेगी"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 1764, 1385, 2066,
    text="कुदरत पूर्वानुमानों के वश में नहीं है। भले ही मौसम टेक्नोलॉजी बढ़ी हो परंतु अनुमान गलत साबित होते हैं। पुणे की वेधशाला ने पिछली बार स्पष्ट कहा था कि इस बार सर्दी हल्की रहने वाली है, बहुत ठंड तो पड़ने ही वाली नहीं है! वे कथन बिल्कुल अवैज्ञानिक साबित हुए और सर्दी नियम से कड़ाके की पड़ी। वैसे भी ग्लोबल वार्मिंग का तो अर्थ ही यह है कि भीषण ठंड और असहनीय गर्मी।",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 1764, 1718, 2066,
    text="बावजूद उनकी बिक्री भी मंदी में अचानक बढ़ गई थी। मौसम का आनंद अब सभी नहीं ले सकते। कुदरत ने अपनी सभी रचनाओं में मनुष्य को सर्वोच्च स्थान देते हुए उसे बुद्धिरूपी विशेषता प्रदान की है। इसी बुद्धि के बल पर मनुष्य ने कुदरत की सभी रचनाओं को केवल और केवल अपनी भौतिक सुख-सुविधा के साधन ही मान लिया है। उसे निःशुल्क",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 312, 2050, 2066,
    text=(
        "मिली अमूल्य प्राकृतिक संपदा के उपयोग में वह कोई संतुलन बनाए नहीं रख सका है।\n"
        "जिसके कारण कुदरत का जो चक्र अब तक एक निश्चित गति से चल रहा था, उसमें अब थोड़ी-थोड़ी बाधाएं आने लगी हैं। रौद्र रूप भी कुदरत का ही एक स्वरूप है। ‘पोषण करने वाला ही संहार करता है’ का सनातन सत्य मानो आने वाले भविष्य की वास्तविकता बनकर आज समस्त मानव समाज के सामने आकर खड़ा हो गया है। जिस प्रकार घरेलू उपयोग के यंत्रों का भी समय-समय पर रखरखाव न किया जाए तो जो स्थिति पैदा होती है, वैसी ही स्थिति फिलहाल वैश्विक वातावरण में देखने को मिल रही है। जापान के पर्यावरणविदों ने कहा है कि कुदरत को अपने स्वाभाविक क्रम में लौटने के लिए इस पूरी सदी की जरूरत पड़ेगी, इतना अधिक उपद्रव मनुष्य ने वसुंधरा पर मचाया है।\n"
        "हवा के बदले रुख और प्रकृति के मिजाज में आए परिवर्तन को समझ लेने के बाद समय रहते सावधान होने की यह घड़ी है। कैलेंडर में दिखने वाले महीनों और वातावरण के बीच की संगतता अब बहुत कम देखने को मिलेगी। कभी मूसलाधार बारिश, तो कभी अचानक घिर आने वाली कड़ाके की ठंड और तड़तड़ाते ओलों को देखकर कई अनुभवी आंखें आश्चर्य से चौड़ी हो जाती हैं। रेगिस्तानी प्रदेश में नदियां बह जाएं उतनी बारिश और हरे-भरे क्षेत्र का धूल भरे रेगिस्तान में रूपांतरण इस बात का संकेत है कि कुदरत ने अब मनुष्य के साथ अपने हिसाब का बहीखाता खोल दिया है। बारिश ने इस बार देश के अनेक स्थानों पर पिछले सवा सौ वर्षों के इतिहास का नया रिकॉर्ड रच दिया है।\n"
        "संयुक्त राष्ट्र संघ के तत्वावधान में काम करने वाले शोधकर्ताओं के समूह ने गहन अध्ययन के बाद घोषित किया है कि बीता दशक तपता हुआ था। मानव जाति के इतिहास में वर्ष २०१० से २०१९ तक का एक दशक बहुत ऊंचे तापमान में गुजरा है। इन शोधकर्ताओं ने कहा कि भीषण गर्मी और विकराल ठंड के लिए दुनिया के हर देश को तैयार रहना होगा। पृथ्वी के औसत तापमान में इतनी वृद्धि हुई है कि जल, वायु, जंगल, नदियां, सरोवर और कृषि में भारी उथल-पुथल मची है और आने वाले वर्षों में इसमें नई और अकल्पनीय अराजकताएं विश्व समुदाय को देखनी होंगी। अब २०२० से २०२९ तक का यह चालू दशक पिछले दशक से भी अधिक खतरनाक होगा।"
    ),
    target_lines=58,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. TO THE POINT (अजित पोपट): जो दिल में था वह जुबान पर आया... (COLS 7-8 TOP)
# ==============================================================================
print("Building To The Point (Ajit Popat Column, Cols 7-8 Top)...")
draw_box(2070, 194, 2718, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    2076, 200, 2712, 344,
    lines=[
        "जो दिल में था वह जुबान पर आया, हमें तो तख्तापलट",
        "करना है, अराजकतावादी बोले..."
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    2076, 350, 2382, 1020,
    text=(
        "आखिर जो दिल में था वह जुबान पर आ ही गया। शुक्रवार, १६ अक्टूबर को राजधानी नई दिल्ली में कथित तिरंगा यात्रा के समय पुलिस वैन की खिड़की से वामपंथी चश्माधारी नेत्री नेहा बोरा बोलीं— हमें तो रेजिम चेंज (तख्तापलट) चाहिए। बांग्लादेश ने हमें रास्ता दिखाया है... बकवास! पिछले सप्ताह इसी स्थान से कहा था कि मुख्य चुनाव आयुक्त ज्ञानेश कुमार तो बहाना हैं। असली निशाना प्रधानमंत्री और गृह मंत्री हैं। थोड़े-से, जी हां थोड़े-से पाठकों को यह बात कड़वी लगी थी। परंतु आखिर दूध का दूध और पानी का पानी हो गया। दर्द पेट में है और पीट रहे हैं माथा— इसी का नाम है।\n"
        "सबसे पहले बांग्लादेश की बात करें। पाकिस्तान और बांग्लादेश में कभी लोकतंत्र स्थिर नहीं हुआ। कथित लोकतंत्र की पीठ के पीछे सैन्य शासन था। दूसरी ओर"
    ),
    target_lines=22,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 350, 2712, 1020,
    text=(
        "साथ मैं सहमत नहीं हूं। मूल रूप से कथित आंदोलनकारियों को फॉरेन कंट्रीब्यूशन रेगुलेशन एक्ट (FCRA) से आपत्ति है।\n"
        "हमारे देश में कुछ कथित एनजीओ विदेशों से अथाह पैसा प्राप्त करते हैं और उस धन का बेधड़क दुरुपयोग करते हैं। एक बिल्कुल छोटा-सा मुद्दा याद दिलाऊं। उत्तर प्रदेश में एक-दो नहीं, सत्रह हजार फर्जी मदरसे पकड़े गए थे। एक मदरसे में मान लीजिए कि दस से बारह बच्चे कुरान-ए-शरीफ पढ़ते हों, तो १७ हजार मदरसों में कितने बच्चे हो सकते हैं? लगाइए हिसाब। ये सत्रह हजार फर्जी मदरसे केंद्र सरकार से भारी-भरकम रकम सहायता के रूप में लेते थे। योगी आदित्यनाथ ने वह बंद करवा दिया।\n"
        "ऐसे तो सैकड़ों कथित एनजीओ देश में हैं जो देशविरोधी कार्यों में विदेशी धन खुलेआम खर्च करते"
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1026, 2240, 1280,
    text="भारत में कभी सैन्य शासन स्थापित हो, ऐसी संभावना नहीं थी। जब इंदिरा गांधी प्रधानमंत्री थीं तभी से यह बात स्पष्ट हो गई थी।",
    target_lines=8,
    first_indent_pt=0.0,
)
# Editable Hindi Badge for To The Point (replacing to_the_point_badge.png)
draw_box(2247, 1028, 2553, 1280, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(2253, 1034, 2547, 1146, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    2260, 1040, 2540, 1140,
    lines=["टू द पॉइंट"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
place_exact_display_lines(
    2260, 1158, 2540, 1268,
    lines=["अजित पोपट", "समसामयिक विश्लेषण"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2560, 1026, 2712, 1280,
    text="हैं। फिर याद दिलाऊं। अभिषेक दीपक बोस्टन यूनिवर्सिटी में स्नातकोत्तर होकर काम ढूंढ रहा था। बेरोजगार था। तो",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1286, 2382, 2066,
    text=(
        "इंदिराजी ने तत्कालीन सेनाध्यक्ष हंसमुख पारसी बावा सैम मानेकशॉ से पूछा था कि क्या हमारे देश में सेना विद्रोह कर दे, ऐसा हो सकता है? सैम अपनी आदत के अनुसार हंस पड़े थे। उन्होंने मैडम को समझाया था कि हमारे यहां हर राज्य के युवा सेना का एक अनिवार्य हिस्सा हैं। हमारी सेना सच्चे अर्थों में कॉस्मोपॉलिटन है इसलिए सैन्य तख्तापलट संभव नहीं है....\n"
        "कांग्रेसी नेता यह हकीकत भलीभांति जानते हैं, इसीलिए लोकतांत्रिक तरीके से चुनी गई सरकार को गिराने के लिए अराजकता फैलाने का खतरनाक रास्ता चुना है। पाकिस्तान और बांग्लादेश की सेना में सौ प्रतिशत मुस्लिम युवा हैं इसलिए सैन्य तख्तापलट आसान है, लोकतंत्र को कुचलना चुटकी बजाने जितना सरल है। विदेशी धन के बल पर भारत में अराजकता फैलाने का सुनियोजित प्रयास हो रहा है। सोशल मीडिया पर इस मुद्दे पर असदुद्दीन ओवैसी ने स्पष्ट बात कही है कि भले ही नरेंद्र मोदी से मेरा एक से अधिक मुद्दों पर विरोध है, परंतु जिस तरह तख्तापलट के नारे लगाए जा रहे हैं उसके"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1286, 2712, 2066,
    text=(
        "दिल्ली आकर आंदोलन करने के पैसे कहां से निकाले? दिल्ली में किराए से या पेइंग गेस्ट के रूप में रहता हो तो उसका गुजारा कैसे होता है? रोजमर्रा का खर्च कौन, किस कारण से देता है? विचार कीजिए प्रिय पाठक। ऐसे तो कई दीपक इस कथित आंदोलन में सक्रिय हैं। बिल्कुल सीधी भाषा में कहूं तो जम्मू-कश्मीर में पुलिस और सुरक्षा बलों पर पत्थरबाजी करने के लिए कश्मीरी बच्चों को रोज पांच सौ रुपये दिए जाते थे, उसी तरह दिल्ली में चल रहे तमाशे के लिए जेन-जी को रोज पहले से तय मेहनताना चुकाया जाता है। इसके अलावा कौन खाली बैठा है कि रोज शाम ढलते ही हंगामा करने आ जाए?\n"
        "देश की १४० करोड़ की आबादी में रोज मान लीजिए कि पचास हजार या एक लाख युवा आंदोलन करते हों तो वह कुल आबादी का एक प्रतिशत भी नहीं होता। और फिर ये लोग तख्तापलट की बातें करते हैं! यह मुंह और मसूर की दाल! नित नए बहाने निकालने वाले ऐसे अराजकतावादियों से सख्ती से निपटना ही होगा। क्या कहते हैं?"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. PRASANGPAT: गूगल मैप का स्वदेशी विकल्प मैपल्स (COLS 1-3 BOTTOM)
# ==============================================================================
print("Building Prasangpat (Mappls vs Google Maps, Cols 1-3 Bottom)...")
draw_box(82, 2092, 1055, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
draw_box(92, 2102, 1045, 2178, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    100, 2108, 1038, 2172,
    lines=["गूगल मैप की गड़बड़ी के कारण १७ की जान गई"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    94, 2186, 1042, 2378,
    lines=[
        "गूगल मैप का स्वदेशी विकल्प",
        "मैपल्स: परंतु मार्केटिंग नहीं"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    92, 2386, 388, 3622,
    text=(
        "मौत किस दिशा से आएगी और किसके कारण आएगी, यह पता नहीं चल सकता। कोलकाता में दुर्गा पंडाल का एक हिस्सा गिरने से भगदड़ में १७ दर्शनार्थियों की मौत हो गई, जबकि ग्वालियर में गूगल मैप के निर्देश के अनुसार चल रहे ट्रक के अनियंत्रित होने से १५ लोगों की जान चली गई।\n"
        "ट्रक रात १.३० बजे शीतला माता मंदिर जा रहे श्रद्धालुओं की भीड़ पर चढ़ गया था। कहते हैं कि ड्राइवर इलाके से परिचित नहीं था, इसलिए उसने गूगल मैप के सहारे गन्ने से भरा ओवरलोड ट्रक चलाया था। पहले वह पुलिस बैरिकेड से टकराया और बाद में सड़क की ढलान पर फिसलकर बेकाबू हो गया।\n"
        "इस विचित्र दुर्घटना के पीछे खलनायक की भूमिका में गूगल मैप के होने की बात कही गई है। गूगल मैप के कारण अनेक हादसे हुए हैं। अधिकांश वाहन गूगल मैप के आधार पर चलते हैं। फोर व्हीलर, थ्री व्हीलर आदि किसी भी कोने में गूगल मैप के जरिए आसानी से यात्रा कर सकते हैं।\n"
        "यात्रा के लिए मिला लोकेशन महत्वपूर्ण दिशा-सूचक बन जाता है। वह निश्चित स्थान पर निश्चित समय में पहुंचा देता है। गूगल मैप का उपयोग महत्वपूर्ण होने के साथ बहुत उपयोगी भी बनता जा रहा है। इसका उपयोग आसान होने से अब यह हर वाहन का अहम हिस्सा बन गया है।\n"
        "लोग गूगल मैप पर भरोसा करके वाहन चलाते हैं परंतु २०२४ की एक घटना में गूगल मैप के भरोसे कार चला रहे तीन युवाओं की कार नदी में गिर गई थी, जिनमें दो तो डॉक्टर थे।\n"
        "गूगल मैप को टक्कर दे सके ऐसे भारतीय ऐप का नाम मैपल्स (Mappls) है।"
    ),
    target_lines=38,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2386, 720, 2602,
    text="गूगल का प्रभाव इंटरनेट सिस्टम पर शिकंजे के समान है। ईमेल से लेकर कंप्यूटर के उपयोग के लगभग सभी महत्वपूर्ण ऐप के साथ गूगल जुड़ा हुआ है। भारत गूगल ब्राउजर का विकल्प भी खड़ा नहीं कर सका है और न ही जीमेल या गूगल मैप जैसी सर्विस",
    target_lines=7,
    first_indent_pt=0.0,
)
place_png(363, 2609, 779, 2842, "mappls_vs_google.png")
place_exact_body_column(
    414, 2848, 720, 3064,
    text="खड़ी कर पाया है।\nउपयोगकर्ताओं को कोई स्वदेशी विकल्प मिले तो वे शिफ्ट होने को तैयार हैं परंतु जीमेल सहित अनेक फ्री सर्विसेज के साथ देश के यूजर्स इतने आदी हो गए हैं कि वह शरीर के एक अंग के समान बन गई हैं।",
    target_lines=7,
    first_indent_pt=0.0,
)
# Editable Hindi Badge for Prasangpat (replacing prasangpat_badge.png)
draw_box(418, 3071, 719, 3250, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(424, 3077, 713, 3172, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    432, 3082, 705, 3166,
    lines=["प्रसंगपट"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
place_exact_display_lines(
    432, 3180, 705, 3240,
    lines=["समसामयिक घटनाचक्र"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    414, 3256, 720, 3622,
    text=(
        "ऐसा भी नहीं है कि भारत ने जीमेल या गूगल मैप जैसी सर्विस का विकल्प खड़ा करने का प्रयास नहीं किया, परंतु गूगल की प्रभावशाली मार्केटिंग और वर्षों पुराने सेटअप के आगे स्वदेशी ऐप का उपयोग करने के लिए शायद ही लोग तैयार होते हैं।\n"
        "इंटरनेट की बुनियाद में गूगल है। जीमेल का उपयोग बढ़ने से पहले हॉटमेल जैसे अनेक विकल्प थे परंतु गूगल की टेक्नोलॉजी को लोगों ने सराहा। गूगल के ब्राउजर क्रोम के विकल्प भी अनेक हैं फिर भी इंटरनेट एक्सप्लोरर"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    746, 2386, 1045, 3622,
    text=(
        "और फायरफॉक्स का उपयोग कम देखा जाता है।\n"
        "जीमेल के मुकाबले हाल ही में श्रीधर वेम्बू की कंपनी जोहो (Zoho) ने अपनी फ्री ईमेल सर्विस पेश की थी परंतु वह बहुत चमक नहीं सकी। गूगल मैप को टक्कर दे सके ऐसी स्वदेशी मैप सर्विस मैपल्स (Mappls) शुरू की गई है। खुद सूचना प्रौद्योगिकी के केंद्रीय मंत्री अश्विनी वैष्णव ने कहा था कि मैं स्वयं मैपल्स का उपयोग करता हूं।\n"
        "डिजिटल मैपिंग के विशेषज्ञों ने कहा है कि भारत के भीतरी ग्रामीण मार्गों को खोजना मैपिंग सिस्टम के लिए चुनौती बन जाता है। पिछले फरवरी में संसद में भी मांग रखी गई थी कि स्वदेशी मैपिंग सर्विस को अमल में लाने के लिए प्रयास करना जरूरी है। गूगल मैप हमेशा सही दिशा नहीं देता परंतु उसका उपयोग इस हद तक बढ़ चुका है कि कोई उसके विकल्प का इस्तेमाल करने को तैयार नहीं है।\n"
        "गूगल मैप द्वारा बताई गई गलत दिशा के कारण हादसे हुए हैं और लोगों ने जान भी गंवाई है। एक घटना ऐसी दर्ज है कि बिहार से गोवा जा रहे एक परिवार ने जल्दी गोवा पहुंचने वाला रूट गूगल मैप पर चुना था। बेचारे कर्नाटक के जंगलों में फंस गए थे।\n"
        "भारत में रोज ५ करोड़ लोग गूगल मैप का उपयोग करते हैं। गूगल मैप की गड़बड़ियां बार-बार चर्चा में आई हैं। भारत के पास इसका विकल्प है परंतु उसकी मार्केटिंग नहीं की जाती। जब ऐसे मामले होते हैं तब डी-गूगलिंग की बातें उछलती हैं, जिनमें गूगल की सर्विस बंद कर स्वदेशी ऐप अपनाने की वकालत की जाती है, परंतु स्वदेशी ऐप देश के लोग ही इस्तेमाल करने को तैयार नहीं हैं।"
    ),
    target_lines=38,
    first_indent_pt=0.0,
)
draw_box(96, 3633, 1042, 3784, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    106, 3640, 1032, 3776,
    lines=[
        "डी-गूगलिंग की बातें उछलती हैं परंतु गूगल का प्रभाव",
        "अधिक है इसलिए उसके आगे स्वदेशी ऐप इस्तेमाल नहीं होते"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)

# ==============================================================================
# 6. BOJ VINANI MOJ (अक्षय अंताणी): कौए मिलते हैं मुश्किल से... (COLS 4-7 BOTTOM)
# ==============================================================================
print("Building Boj Vinani Moj (Akshay Antani Humor Column, Cols 4-7 Bottom)...")
draw_box(1070, 2092, 2390, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    1080, 2100, 2380, 2206,
    lines=["कौए मिलते हैं मुश्किल से, इसलिए बढ़ती जाती है डिमांड"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1080, 2214, 1385, 3784,
    text=(
        "‘तरह-तरह की पार्टियों के इस ‘सर्व-पक्षी’ अभयारण्य में लगातार दलगत विवाद चलते हैं, दलबदल करके ‘पक्ष-घात’ होता है और विपक्ष तथा सत्ता-भक्षी के बीच चोंचें लड़ाने की होड़ चलती है। इसमें किस पक्ष की तारीफ करें यह समझ ही नहीं आता, क्या कहते हैं काका?’\n"
        "सवाल सुनते ही पथुकाका ने तपाक से जवाब दिया कि ‘दलगत राजनीति से परे ऐसा एक ही पक्ष अब हमारे देश में बचा है, वह पक्ष है श्राद्ध-पक्ष। क्योंकि इस पक्ष के सभी माननीय सदस्य स्वर्ग सिधार चुके हैं। साल में एक ही बार इस पक्ष का नाम सुनाई देता है, श्राद्धपक्ष में। और हमारे वे पूर्वज भी कितने समझदार होते हैं? स्वर्ग से धरती पर श्राद्धपक्ष में अपने प्रतिनिधि के रूप में किसे भेजते हैं पता है न? कौए को। ताकि कोई आलोचना न करे कि स्वर्ग सिधारने के बाद भी ‘मलाई’ खाने का मोह नहीं छूटा। बाकी धरती पर तो अलग-अलग दलों के ‘पक्षी’ मलाई खाने के लिए घात लगाए ही बैठे रहते हैं। जय-जय रघुराई की, कभी न भूले मलाई की, खाने में क्या शरम भाई की, जय-जय रघुराई की...’\n"
        "मैंने कहा ‘काका विविधता में एकता के दर्शन अब तो केवल श्राद्ध-पक्ष में ही देखने को मिलते हैं न?’\n"
        "काका ने पूछा ‘श्राद्धपक्ष में भला तुझे विविधता में एकता के दर्शन कैसे होते हैं?’ मैंने कहा कि ‘जीवित व्यक्ति भले अलग-अलग जाति का हो, अलग-अलग धर्म का हो, पर मृत्यु के बाद सभी कौए के रूप में ही श्राद्धपक्ष में दिखाई देते हैं न? इसी को कहते हैं विविधता में एकता अथवा कांव... कांव... ऐसा “काका-रव” करते कौओं की एकता...’\n"
        "काका बोले ‘इसका अर्थ यह कि डार्विन दादा ने कहा था कि मनुष्य के पूर्वज बंदर थे, वह थ्योरी गलत?’ मैंने कहा ‘काका वैज्ञानिक डार्विन ने वर्षों के शोध और अध्ययन के आधार पर ऐसी थ्योरी बनाई थी कि मानव के पूर्वज वानर थे। बाकी श्राद्धपक्ष में कौए को खीर-पूरी खिलाने से पूर्वज तृप्त होते हैं यह श्रद्धा का विषय है।’\n"
        "काका बोले ‘भाई मुंबई जैसे शहरों में कौए भी कहां खाली बैठे हैं खीर-पूरी खाने को? बचपन में हम गाते थे कि आ रे कौए कढ़ी पीने... वैसे ही"
    ),
    target_lines=48,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 2214, 1718, 2496,
    text="बड़े होने पर हमें गाना पड़ता है कि आ रे कौए खीर खाने... पर कौए कहां आते हैं? मानो ऐप-आधारित कैब बुक कराने के बाद जैसे इंतजार में खड़े रहते हैं, वैसे ही कौए की राह देखते खड़े रहना पड़ता है। कई बार कैब वाले ट्रिप कैंसिल करते हैं वैसे ही कौआ भी खीर खाने हमारी छत पर आने के बजाय किसी पास की छत पर उड़कर पहुंच जाता है। कौओं की किल्लत",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2214, 2050, 2496,
    text="केकारव के नाम से विख्यात हुआ। अब कौओं की घटती आबादी देखकर आप व्यथित हो गए हैं, यह भावना व्यक्त करने के लिए आप भी कौओं पर कविताएं लिखकर संग्रह तैयार कीजिए और नाम दीजिए ‘काका-रव।’ आपको कोला पीने की आदत है न? इसलिए इस काव्य-संग्रह पर आपका उपनाम क्या लिखेंगे पता है? कोला-पी।",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2504, 1572, 2765,
    text="पैदा हो जाए यह कैसी विचित्र स्थिति कहलाएगी?’\nपथुकाका कहते हैं कि हमारे देश में मनुष्य की आबादी दिन दूनी रात चौगुनी बढ़ती जा रही है,",
    target_lines=8,
    first_indent_pt=0.0,
)
# Editable Hindi Badge for Boj Vinani Moj (replacing boj_vinani_moj_badge.png)
draw_box(1578, 2504, 1884, 2765, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(1584, 2510, 1878, 2635, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1590, 2516, 1872, 2628,
    lines=["बोझ बिना", "की मौज"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
place_exact_display_lines(
    1590, 2645, 1872, 2755,
    lines=["अक्षय अंताणी", "हास्य-व्यंग्य स्तंभ"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1890, 2504, 2050, 2765,
    text="जवाब दो कि कौओं की आबादी सचमुच घटने लगी है या फिर (मरे चूहे सहित सब कुछ खाने वाले) कौओं की ‘मौत-दार’ सूची से उनके",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2772, 1718, 2980,
    text="और कौओं की आबादी घटती जा रही है, तो फिर श्राद्धपक्ष के समय कौओं की तंगी ही पैदा होगी न?’\nकाका की बात में सुर मिलाते हुए मैंने कहा कि कौओं की आबादी घटती जा रही है यह हकीकत है। अभी अखबार में खबर पढ़ी थी। मुंबई जैसे शहरों में तेजी से बनते कंक्रीट के जंगल, कटते",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2772, 2050, 2980,
    text="नाम उड़ा दिए गए हैं?\nठहाका लगाकर हंसते हुए मैंने कहा ‘काका आपने कौओं के लिए मौत-दार सूची शब्द कमाल का इस्तेमाल किया! हमारी मतदाता सूची से भी करोड़ों नाम उड़ गए हैं न? जबकि कौए तो खुद ही उड़ते रहते हैं इसलिए उनके नाम भी उड़ते ही रहेंगे न?’",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2986, 1535, 3282,
    text="जाते पेड़ और घटती हरियाली के कारण कौओं को घोंसले कहां बनाएं, यह सवाल परेशान करता है। दूसरा",
    target_lines=9,
    first_indent_pt=0.0,
)
place_png(1541, 2986, 2046, 3282, "crow_cartoon.png")
place_exact_body_column(
    1412, 3288, 1718, 3784,
    text="शहरों में खुले कचरे के ढेर की जगह आधुनिक कूड़ेदान लगते जा रहे हैं। कचरा ले जाने वाले ट्रक भी ऊपर से बंद होते हैं। इसलिए बेचारे कौए खाएं क्या? इसके अलावा मुंबई जैसे शहरों में प्रदूषण बढ़ता जा रहा है। इन सभी कारणों से कौओं की आबादी घटती जा रही है।’\nपथुकाका बोले ऐसी बात है? कौओं की पॉपुलेशन घटती जाएगी तो प्रॉब्लम होगी भाई! गंदगी कम करने का काम कौन करेगा? श्राद्धपक्ष में खीर-पूरी खाने कौन आएगा? वह सब तो ठीक पर रोज मुंडेर पर बैठकर मुझे काका... काका... काका... कहकर नाम से कौन बुलाएगा?\nमैंने कहा ‘राजकवि कलापी ने दिल की वेदना और भावना व्यक्त करने वाली कविताओं का संग्रह प्रकाशित किया था जो",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 3288, 2050, 3784,
    text="बादशाह अकबर ने किले की प्राचीर पर कतार में बैठे कौओं की कागसेना को देखकर बीरबल से पूछा कि बीरबल जवाब दो कि हमारी दिल्ली में कौओं की आबादी कितनी है?’ हाजिरजवाब बीरबल ने तपाक से जवाब दिया कि ‘बादशाह सलामत... दिल्ली में इस समय ११,११,१११ कौए हैं।’\nजवाब सुनकर बादशाह तो आश्चर्यचकित रह गए। बीरबल की और परीक्षा लेने के लिए जहांपनाह ने पूछा कि तुम्हारे बताए आंकड़े से कौओं की संख्या अधिक हुई तो? बीरबल बोला कि यदि अधिक हो तो समझना कि कौओं के यहां बाहरगांव से मेहमान आए होंगे और यदि संख्या कम लगे तो समझना कि दिल्ली के कौए समर वेकेशन में फैमिली के साथ बाहरगांव घूमने गए",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2214, 2380, 3784,
    text=(
        "होंगे! बीरबल के जवाब से खुश हुए बादशाह ने उसे दस सोने की मुहरों का ऑनलाइन पेमेंट कर दिया।’\n"
        "मैंने कहा काका आपको पता है? कौओं की आबादी घट गई है इसका लाभ किराए पर कौए उपलब्ध कराने वाले उठाते हैं?\n"
        "आश्चर्यचकित होकर काका बोले ‘क्या बात करते हो? कौए कौन किराए पर देता है?’ मैंने कहा कौए किराए पर देने वालों की श्राद्धपक्ष में असली डिमांड होती है। महाराष्ट्र के कुछ गांवों में श्राद्धपक्ष के समय कौए किराए पर घुमाने वाले ‘रेंट-ए-क्रो’ कंपनी वाले सोशल मीडिया में नजर आए थे। वे क्या करते हैं पता है? जंगल से कौए पकड़ लाते हैं। फिर एक पैर में डोरी बांध देते हैं। फिर एक-एक कंधे पर दो-दो कौए बिठाकर आवाज लगाते निकलते हैं— ‘लो कौआ भाड़े से... लो कौआ भाड़े से...’ उस समय छत पर खीर-पूरी रखकर खड़े लोगों के पास जब कौए नहीं आते तो वे तुरंत किराए के कौए वाले को ऊपर बुलाते हैं। वह छत पर जाकर कौए को खीर-पूरी खिलाता है और बदले में सौ-डेढ़ सौ रुपये किराया वसूल कर निकल जाता है। बोलिए! ‘कौए किराए पर देने का यह मुनाफेदार सीजनल धंधा कैसा है?’\n"
        "किराए के कौए की बात सुनकर पथुकाका बोले सच बोलना भाई! ‘झूठ बोले कौआ काटे... काले कौए से डरियो...’ मैंने हंसकर कहा काका आपने बॉबी फिल्म का यह गीत खूब याद दिलाया! काका बोले ‘तुझे पता है? राज कपूर मेरा नाम जोकर बना रहे थे। खाने के शौकीन और बड़े दिल वाले राज कपूर अपने असिस्टेंट डायरेक्टर के घर खाना खाने गए। पूरी, सब्जी, दाल तड़का सहित कई व्यंजन असिस्टेंट डायरेक्टर की मम्मी ने परोसे थे। राज कपूर चाव से खा रहे थे। उस समय मम्मीजी ने प्यार से कहा बेटा तुम तो कुछ खाते ही नहीं हो... तब शोमैन ने कहा मम्मीजी झूठ बोले कौआ काटे... देखते नहीं कितना सारा खा लिया? बस फिर झूठ बोले कौआ काटे... यह मुखड़ा उनके दिमाग में लगातार घूमता रहा। जब ‘बॉबी’ फिल्म बनाई तब उन्होंने इस मुखड़े पर गीत बनाने को गीतकार से कहा और इस तरह मजेदार गीत बना— झूठ बोले कौआ काटे... काले कौए से डरियो...’"
    ),
    target_lines=48,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. KALPAVRUKSHA: सुविचार (COL 8 BOTTOM)
# ==============================================================================
print("Building Kalpavruksha (Quotes Column, Col 8 Bottom)...")
draw_box(2402, 2092, 2718, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_png(2408, 2096, 2715, 2439, "kalpavruksha_header_photo.png")
# Place editable Hindi header "कल्पवृक्ष" inside the yellow banner of kalpavruksha_header_photo.png
place_exact_display_lines(
    2436, 2118, 2684, 2206,
    lines=["कल्पवृक्ष"],
    font_style="Bold",
    fill_swatch="[Black]",
    align="center",
    stretch_lines=False,
    font_family_override="DB Hindi Mast",
    font_style_override="Regular",
)
place_exact_body_column(
    2410, 2448, 2710, 3784,
    text=(
        "समस्त ज्ञान मनुष्य के मन के भीतर ही निहित है। शिक्षा और अनुभव केवल उस आंतरिक ज्ञान को बाहर लाने (आवरण हटाने) का काम करते हैं।\n- स्वामी विवेकानंद\n*\n"
        "ज्ञान केवल किताबी जानकारी नहीं है, बल्कि चरित्र निर्माण का साधन है। अक्षरज्ञान की तुलना में ‘आत्मज्ञान’ और ‘नैतिक मूल्य’ महत्वपूर्ण और सर्वोपरि हैं।\n- महात्मा गांधी\n*\n"
        "आपकी सबसे बड़ी भूल यह है कि आप सोचते हैं कि आपके पास समय है। जीवन क्षणभंगुर है, इसलिए जो करना है वह वर्तमान क्षण में ही कर लेना चाहिए।\n- भगवान बुद्ध\n*\n"
        "जब आप वर्तमान में पूर्ण रूप से जीते हैं, तब समय अदृश्य हो जाता है - वही सच्चा ध्यान है। मन भूतकाल और भविष्य में भटकता है, पर जीवन केवल ‘अभी’ ही अस्तित्व रखता है।\n- ओशो\n*\n"
        "हमें मिलने वाला जीवन छोटा नहीं है, परंतु हम उसका बहुत-सा समय गंवा देते हैं। यदि समय का सदुपयोग किया जाए तो जीवन बहुत बड़ा और सार्थक प्रतीत होता है।\n- सेनेका\n*\n"
        "धैर्य और समय ये दो सबसे शक्तिशाली योद्धा हैं। उचित समय आने पर सब कुछ अपने आप ठीक हो जाता है। बस, धैर्य रखने की आवश्यकता होती है।\n- लियो टॉल्स्टॉय\n*\n"
        "खोया हुआ समय कभी वापस नहीं मिलता। यदि आपको जीवन प्रिय है तो समय व्यर्थ न गंवाएं, क्योंकि जीवन समय से ही बना है।\n- बेंजामिन फ्रैंकलिन"
    ),
    target_lines=41,
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
    pd_path = target_dir / "Page_08_Hindi_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_08_Hindi_SameToSame.dns"
    png_path = target_dir / "Page_08_Hindi_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_08_Hindi_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_08_Hindi_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
