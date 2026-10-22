from gs_english_running_header import build_english_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 7 BUILDER FOR INDIAN POST (ENGLISH GUJARAT SAMACHAR)
===================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable English Text ('Georgia' & 'Times New Roman')
  across all 5 Business News stories (Edible Oil Imports, Sugar MSP, IT Mutual
  Funds, Jio Platforms IPO, Global Urea Prices)!
- Graphics/Ads (.webp): 3 Story Photos/Charts and Honda Bottom Half-Page Ad in .webp!
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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 07 (100% Same-to-Same Editable English)"
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
    asset_file = webp_cand if webp_cand.exists() else (ASSETS_DIR / filename)
    img_path = str(asset_file.resolve()).replace("\\", "/")
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
    custom_font_family: str = None,
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

    if custom_font_family:
        use_font_family = custom_font_family
        use_font_style = "Regular"
    elif font_family_override:
        use_font_family = font_family_override
        use_font_style = font_style_override or "Regular"
    elif font_style == "Bold" and (box_h_pt / max(1, n_lines)) >= 16.0:
        use_font_family = "Georgia"
        use_font_style = "Bold"
    else:
        use_font_family = "Times New Roman"
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
        for try_hs in (0.85, 0.80, 0.75, 0.70, 0.65):
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
    lo_pt: float = 7.2,
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

    best_cfg = (9.5, default_hscale, 0.0)
    best_diff = 999

    for pt10 in range(int(hi_pt * 10), int(lo_pt * 10) - 1, -2):
        pt = round(pt10 / 10.0, 1)
        if pt > lead_pt * 1.08:
            continue
        for hs100 in (94, 90, 87, 84, 81, 78, 75):
            hs = round(hs100 / 100.0, 2)
            st = batch([
                {"command": "text.select", "params": {"story": sid, "anchor": 0, "focus": 99999}},
                {"command": "type.char", "params": {"attrs": {
                    "fontFamily": "Times New Roman",
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
            "fontFamily": "Times New Roman",
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
print("Placing Page 7 English Running Header...")
build_english_running_header(7, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. STORY 1: EDIBLE OIL IMPORTS (COLS 1-5 TOP)
# ==============================================================================
print("Building Story 1 (Edible Oil Imports, Cols 1-5 Top)...")
place_exact_display_lines(
    82, 200, 1718, 340,
    lines=["Edible Oil Imports Rise 3.7%, Prices Jump 11%"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.82,
)
place_exact_body_column(
    82, 346, 1050, 434,
    text="Ahmedabad, Oct 19\nTo meet peak festive season demand, edible oil traders imported substantial volumes of cooking oil. During November–September 2025-26, India's total edible oil imports rose 3.27% to",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(1064, 348, 1064, 432, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 346, 1718, 434,
    text="15.164 million tonnes compared to 14.683 million tonnes a year earlier, with palm oil accounting for the largest share. In September, major edible oil prices surged 9.7% to 11.2% year-on-year, driven primarily by rupee depreciation against the US dollar.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 438, 1718, 496,
    lines=["Weakening Rupee Fuels Cooking Oil Price Surge: Palm Oil Dominates Import Basket"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 504, 386, 1018,
    text="Led by higher arrivals of crude palm oil, total palm oil imports increased 5.32% to 7.352 million tonnes. Soybean oil imports rose 3.25% to 5.176 million tonnes, whereas sunflower oil imports declined 1.90% to 2.624 million tonnes. Refined edible oil imports fell sharply to 0.74 million tonnes, while crude edible oil imports expanded to 14.423 million tonnes.\nA decisive shift from refined oil toward crude oil imports was observed during the period. Refined cooking oil shipments dropped from 1.689 million tonnes to 0.74 million tonnes, cutting their share in total imports from 12% to just 5%.",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 504, 400, 1018, swatch="[Black]", weight_pt=0.75)
place_png(414, 504, 1050, 926, "edible_oil_photo.png")
place_exact_body_column(
    414, 932, 718, 1018,
    text="Crude edible oil imports rose from 12.993 million tonnes to 14.423 million tonnes, mainly",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(732, 934, 732, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 932, 1050, 1018,
    text="as refiners substituted refined palmolein with crude palm oil.\nArgentina emerged as India's",
    target_lines=3,
    first_indent_pt=0.0,
)
draw_line(1064, 504, 1064, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1078, 504, 1382, 1018,
    text="largest single supplier of cooking oil, exporting 3.443 million tonnes in total, including 2.714 million tonnes of crude soybean oil and 7.29 lakh tonnes of sunflower oil.\nMalaysia supplied 2.876 million tonnes of palm oil, while Indonesia exported 2.905 million tonnes. Taking advantage of zero import duty under bilateral trade norms, Nepal also exported 6.82 lakh tonnes of refined oil to India, including 6.05 lakh tonnes of refined soybean oil.\nCompared to the previous year, domestic edible oil prices in September 2026 registered",
    target_lines=17,
    first_indent_pt=0.0,
)
draw_line(1396, 504, 1396, 1018, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 504, 1718, 1018,
    text="a sharp increase due to firm international benchmark rates and currency depreciation. A weaker rupee directly inflated landed import costs.\nAccording to market analysts, the Indian rupee depreciated nearly 8.1% against the US dollar during this period, sliding from Rs 88.32 to Rs 95.51 per dollar and making imported oils significantly costlier. Higher import volumes, firm global prices and rupee weakness have pushed up India's edible oil import bill while reshaping sourcing patterns toward crude oils.",
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
        "Demand Grows to Hike Sugar MSP",
        "From Rs 31 to Rs 50 Per Kilogram"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    82, 1224, 556, 1344,
    text="Ahmedabad, Oct 19\nSugar mill workers in Maharashtra have threatened an indefinite strike from the 22nd in support of farmers' demands. The central demand of both farmers and mill workers is an immediate hike in the Minimum Selling Price (MSP) of sugar.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(564, 1226, 564, 1342, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    572, 1224, 1050, 1344,
    text="Farmers say that weak mill finances have delayed cane payments across the state. Raising the sugar MSP to Rs 50 per kg would provide vital relief to both the sugar industry and sugarcane growers without placing any undue burden on consumers.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    82, 1350, 1050, 1468,
    lines=[
        "Sugar Minimum Selling Price Has Remained Frozen at Rs 31/Kg",
        "for Seven Years Even as Sugarcane FRP Continues to Climb"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    82, 1474, 386, 1995,
    text="Farmers are demanding that the Minimum Selling Price of sugar be raised from the current Rs 31 per kg to Rs 50 per kg, alongside an increase in the ethanol procurement price from Rs 58 to Rs 70 per liter.\nOver the past seven years, the Fair and Remunerative Price (FRP) of sugarcane has increased by more than 26%, yet the sugar MSP has been revised only once. Since February 2019, the sugar MSP has remained unchanged at Rs 31 per kg.",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(400, 1476, 400, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    414, 1474, 718, 1995,
    text="Sugarcane procurement accounts for the largest cost component in the sugar industry. In 2020-21, the sugarcane FRP stood at Rs 2,850 per tonne, which has been raised to Rs 3,650 per tonne for the 2026-27 crushing season. By contrast, the sugar MSP has remained frozen at Rs 3,100 per quintal since February 2019.\nCiting rising conversion and financing costs, the sugar industry has long sought an upward revision in MSP. Sugar mill workers are now preparing to launch an indefinite strike from the 22nd",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_line(732, 1476, 732, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    746, 1474, 1050, 1995,
    text="across Maharashtra.\nSugar mill unions in Maharashtra have warned of an indefinite strike starting on the 22nd, pressing for a Rs 50/kg sugar MSP to restore the financial viability of cooperative and private mills across the state.\nIndustry sources noted that because the Centre has kept the sugar MSP unchanged for seven years, banks have grown cautious when extending working-capital loans against sugar stocks.",
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
        "Mutual Fund Holdings in IT Firms",
        "Sink to Record Low in Sept Quarter"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1078, 1192, 1718, 1318,
    text="Mumbai, Oct 19\nConcerns over Artificial Intelligence (AI) disruption, sluggish discretionary spending by global clients, and muted revenue growth pushed mutual fund holdings in Indian IT companies to an all-time low in the September quarter of the current fiscal year.",
    target_lines=5,
    font_style="Bold",
    first_indent_pt=9.0,
)
place_exact_display_lines(
    1078, 1324, 1718, 1435,
    lines=[
        "Bellwether IT Stocks That Once Topped",
        "Fund Portfolios Slide Down Holdings Ranks"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_png(1078, 1455, 1382, 1585, "it_funds_chart.png")
place_exact_body_column(
    1078, 1592, 1382, 1995,
    text="Owing to persistent pressure on the technology sector, bellwether IT firms such as Infosys and TCS—which once dominated institutional portfolios—have slipped out of the top holdings list.\nAt the end of 2025, IT stocks accounted for 7.60% of mutual funds' total equity Assets Under Management (AUM), a share that dropped to 5.30% by the close of the September quarter.\nAccording to a brokerage research report, the ongoing correction in IT stocks has been driven primarily by valuation de-rating rather than earnings contraction.",
    target_lines=13,
    first_indent_pt=9.0,
)
draw_line(1396, 1442, 1396, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    1412, 1442, 1718, 1995,
    text="At the end of December 2025, the total value of IT shares held by domestic mutual funds stood at Rs 3.88 lakh crore, down from an all-time peak of Rs 4.03 lakh crore in November 2025; by the September quarter, that value had shrunk to Rs 2.97 lakh crore.\nInfosys, which ranked among the top five mutual fund holdings at the start of 2026, slid to the 10th spot in September, with TCS and peer IT majors witnessing a similar pullback.\nFund managers have pared exposure amid concerns that generative AI could compress traditional IT services billing, the report noted.",
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
    lines=["Price Band Fixed at Rs 1,065 to Rs 1,119 Per Equity Share"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    underline=True,
)
place_exact_display_lines(
    1754, 260, 2705, 452,
    lines=[
        "Jio Platforms' Rs 30,213-Crore IPO",
        "Poised to Set All-Time Indian Record"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 460, 2056, 954,
    text="Mumbai, Oct 15\nThe Rs 30,213-crore Initial Public Offering (IPO) of Jio Platforms Limited—the digital and telecom arm of Reliance Industries, comprising an entirely fresh issue of 27 crore equity shares—is set to become the largest IPO in Indian stock market history. The company today announced a price band of Rs 1,065 to Rs 1,119 per share. The issue will open on October 21 and close on October 23, 2026. At the upper end of the price band, Jio Platforms is valued at approximately Rs 10.3 lakh crore (around $108 billion), with a minimum bid lot of 12 shares.\nManaging Director Akash Ambani stated that the entire offering consists of fresh shares and that Jio Platforms is marching toward becoming a net debt-free company. Proceeds from the IPO will be utilized",
    target_lines=17,
    first_indent_pt=9.0,
)
draw_box(1758, 960, 2056, 1066, stroke_swatch="GsRedBanner", stroke_weight_pt=1.8)
place_exact_display_lines(
    1764, 966, 2050, 1060,
    lines=[
        "Company Advancing Toward Becoming",
        "Net Debt-Free: Akash Ambani"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1754, 1072, 2056, 1318,
    text="primarily to repay debt at Reliance Jio Infocomm. For future growth, Jio is focusing on 5G, Artificial Intelligence (AI), home broadband and indigenous technology stacks. Rather than remaining confined to telecom connectivity, Jio aims to expand average revenue per user by delivering integrated digital services.\nOutside China, Jio commands the world's largest 5G subscriber",
    target_lines=9,
    first_indent_pt=0.0,
)
draw_line(2068, 460, 2068, 1318, swatch="[Black]", weight_pt=0.75)
place_png(2080, 462, 2705, 800, "jio_ipo_photo.png")
place_exact_body_column(
    2080, 806, 2705, 1318,
    text="base. He added that the company intends to partner with international telecom operators using its end-to-end proprietary technology stack, focusing on managed services rather than mere equipment sales to build a strong global footprint, while expressing confidence that commercial 6G deployment will begin in the early 2030s.\nDirector Isha Ambani noted that the IPO valuation has been structured to leave attractive upside for long-term investors. Kotak Mahindra Bank founder Uday Kotak pointed out that Jio Platforms' IPO valuation implies a price-to-earnings multiple of roughly 34x FY2025-26 earnings, compared with nearly 41x for its closest listed peer, incorporating feedback from global institutional investors.",
    target_lines=17,
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1754, 1324, 2705, 1440,
    lines=[
        "IPO Valuation Structured to Remain Attractive",
        "for Long-Term Investors: Isha Ambani"
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
        "Global Urea Prices Drop Sharply",
        "as International Supplies Improve"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1744, 1636, 2222, 1726,
    text="Mumbai, Oct 19\nImproved global supplies have brought India's urea import costs down by nearly 60% compared to May levels, government sources",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=9.0,
)
draw_line(2229, 1638, 2229, 1724, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2236, 1636, 2715, 1726,
    text="informed. Global urea prices, which had surged to $945 per tonne in May, have now cooled to around $390 per tonne.",
    target_lines=3,
    font_style="Bold",
    first_indent_pt=0.0,
)
place_exact_display_lines(
    1744, 1732, 2715, 1796,
    lines=["Completion of Domestic Kharif Sowing Also Eases Import Demand"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1744, 1802, 2052, 1995,
    text="International urea prices declined by 15% in September alone, sources in the Ministry of Fertilizers said. Backed by government efforts to diversify import sources, India is now procuring urea from Oman, Malaysia, Vietnam, Georgia, Nigeria and Russia among",
    target_lines=7,
    first_indent_pt=9.0,
)
draw_line(2064, 1804, 2064, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2076, 1802, 2382, 1995,
    text="other nations.\nAhead of Kharif sowing in May, strong seasonal buying had pushed global prices higher. With Kharif sowing now complete and Indian import demand moderating, international benchmark rates have softened considerably, officials added.",
    target_lines=7,
    first_indent_pt=0.0,
)
draw_line(2395, 1804, 2395, 1995, swatch="[Black]", weight_pt=0.75)
place_exact_body_column(
    2408, 1802, 2715, 1995,
    text="Compared with last fiscal year's fertilizer subsidy expenditure of Rs 2.17 lakh crore, the subsidy outgo in the current fiscal year is projected to be Rs 20,000 crore to Rs 22,000 crore higher.",
    target_lines=7,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. PLACE BOTTOM HONDA AD (.WEBP)
# ==============================================================================
print("Placing Bottom Honda Half-Page Advertisement (.webp)...")
place_png(0, 2005, 2800, 3974, "ad_honda_bottom.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_07_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_07_English_SameToSame.dns"
    png_path = target_dir / "Page_07_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_07_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_07_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_07_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_07_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
