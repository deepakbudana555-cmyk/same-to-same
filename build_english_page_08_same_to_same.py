from gs_english_running_header import build_english_running_header
# -*- coding: utf-8 -*-
"""
100% SAME-TO-SAME ENGLISH PAGE 8 BUILDER FOR INDIAN POST (ENGLISH GUJARAT SAMACHAR)
===================================================================================
- Page Size: 2800 x 3974 px mapped at S = 0.375 pt/px -> 1050.0 x 1490.25 pt
- News Content: 100% Editable English Text ('Indian Post Mast', 'Georgia', 'Times New Roman')
  across all 6 Editorial & Column Features on Page 8:
  1. EDITORIAL: The Dawn of Corporate Agriculture (Cols 1-2 Top)
  2. ALPVIRAM: A Changing Climate Will No Longer Let the World Rest Easy (Cols 3-6 Top)
  3. TO THE POINT (Ajit Popat): What Was in Their Hearts Came to Their Lips—We Want Regime Change... (Cols 7-8 Top)
  4. PRASANGPAT: Mappls, India's Indigenous Alternative to Google Maps—Held Back by Weak Marketing (Cols 1-3 Bottom)
  5. BOJ VINANI MOJ (Akshay Antani): Crows Are Hard to Find, So Demand Keeps Rising! (Cols 4-7 Bottom)
  6. KALPAVRUKSHA: Timeless Thoughts (Col 8 Bottom)
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
        "title": "INDIAN POST (English Gujarat Samachar) — Page 08 (100% Same-to-Same Editable English)"
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
print("Placing Page 8 English Running Header...")
build_english_running_header(8, draw_box, place_exact_display_lines)

# ==============================================================================
# 2. EDITORIAL: THE DAWN OF CORPORATE AGRICULTURE (COLS 1-2 TOP)
# ==============================================================================
print("Building Editorial (The Dawn of Corporate Agriculture, Cols 1-2 Top)...")
draw_box(82, 194, 720, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.8)
draw_box(85, 196, 717, 294, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    96, 192, 706, 276,
    lines=["INDIAN POST"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    target_hscale=0.88,
    custom_font_family="Indian Post Mast",
)
draw_box(85, 294, 717, 336, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    96, 298, 706, 332,
    lines=["FOUNDER EDITOR: SHANTILAL SHAH • TUESDAY, OCT 20, 2026"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    94, 344, 708, 412,
    lines=["The Dawn of Corporate Agriculture"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
    target_hscale=0.90,
)
place_exact_body_column(
    92, 420, 710, 2066,
    text=(
        "The last two quarterly corporate earnings cycles have painted an encouraging picture for agriculture and value-added farm products. India has witnessed a sudden surge in corporate enterprises linked to agricultural commodities, and many of these firms are now establishing international supply-chain linkages. Much water has flowed down the Ganga and Yamuna since the current financial year began, and just like the myriad hues of spring blossoms, citizens are witnessing diverse shades of the economy this year. India today stands at a historic crossroads facing complex challenges across multiple spheres of national life. Regardless of who is at the helm, overcoming these hurdles is no easy task. Several impoverished nations, including countries across Africa, are looking toward India for relief amid a severe global downturn.\n"
        "To ensure that children at home do not go hungry, the government has naturally exercised caution in exporting flour and foodgrains abroad. Even so, lakhs of tonnes of grain have been exported and gifted as humanitarian aid to date. The primary reason behind the Centre's export restrictions on certain varieties of rice is an erratic monsoon. In Uttarakhand and Himachal Pradesh, the very word 'rain' now sends shivers down people's spines after this year's devastating cloudbursts. While the state provides relief to victims, only those who have lost their homes to nature's fury know what it takes to rebuild an entire life from scratch. Domestic production of foodgrains and pulses is set to fall short of demand this year, placing immense weight on the delayed Rabi sowing season. Shortfalls from the previous harvest mean that prices of cumin, onions and oilseeds will test household budgets this winter.\n"
        "Shifting weather patterns brought dense clouds and heavy downpours during the final leg of the monsoon, inflicting severe damage on inundated farmlands. Historically, a bountiful Kharif harvest sets the stage for a prosperous Rabi season. Even so, rural liquidity from farm output is beginning to circulate through the broader market, sparking a visible revival across allied industrial sectors. At a time when recessionary gloom hangs over much of the world, the resilience of the Indian economy has surprised observers across Asia. Global investors pulling capital out of China are increasingly deploying funds into India—and remarkably, incoming foreign investors are showing heightened interest in agri-processing and farm-linked industrial ventures. That is an auspicious sign.\n"
        "The Reserve Bank Governor has projected a 10.5 percent growth rate for the upcoming Rabi season. Though ambitious at first glance, the pace at which industry and services are clearing the backlog of 2025-26 makes this target achievable. Mr. Shaktikanta Das has repeatedly emphasized that the Indian economy is back on track and that structural reforms are yielding steady gains. Yet while the government prefers to present a rosy macroeconomic picture, the wallets of ordinary middle-class families have grown thinner. If nature's blessing in the form of winter rain remains favorable, agriculture will power the economy forward. Meanwhile, the Centre has held high-level meetings with 12 high-burden states to curb surging dengue cases.\n"
        "By contrast, the much-touted Start-Up India wave has stumbled across nearly every sector. Having begun with heroic fanfare, many start-ups met a premature end: total funding across Indian start-ups fell from $7.5 billion in 2015 to $3.5 billion in 2016, and the 2016 demonetization shock shattered the foundations of more than half of them."
    ),
    target_lines=54,
    font_style="Bold",
    first_indent_pt=9.0,
)

# ==============================================================================
# 3. ALPVIRAM: A CHANGING CLIMATE WILL NO LONGER LET THE WORLD REST EASY (COLS 3-6 TOP)
# ==============================================================================
print("Building Alpviram (Climate Change Essay, Cols 3-6 Top)...")
draw_box(736, 194, 2060, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    746, 200, 2050, 304,
    lines=["A Changing Climate Will No Longer Let the World Rest Easy"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    746, 312, 1051, 2066,
    text=(
        "Torrential rains are still lashing parts of northern and southern India even as Sharad Purnima—traditionally the season of crystal-clear autumn skies—approaches. Over Gujarat too, massive cloud formations resembling an army of elephants are gathering once again. The seasons are changing their colors. Unpleasant as it may sound, nature has turned a corner. Over the past year, Japan and Europe experienced sweltering humidity and heatwaves beyond anything they had ever imagined, followed by relentless storms and floods. The average number of cyclones striking the Earth over the past twelve months is the highest in fifty years. Across India, wherever it rains, it now pours beyond measure.\n"
        "For eastern India, the monsoon has turned into a recurring calamity. If every individual were to introspect honestly on how much they actually changed their lifestyle after the arrival of Covid-19, it would become clear that ingrained human habits rarely change after a few tremors. Gulping down herbal decoctions every day out of fear of death was hardly a pact of friendship with nature or the environment. Right at the outset, the World Health Organization had urged humanity to give up dietary and consumption habits that harm the body and the planet; only when demand for destructive products ceases will their production stop.\n"
        "Reckless consumption invites internal crises inside the human body that only physicians can diagnose. While the world has praised the natural immunity of the average Indian citizen during the pandemic, the toll of lives lost during Covid remains deeply tragic. Even today, the incidence of dengue and cardiac ailments remains alarmingly high. When a life is cut short in its prime, an entire caravan of dreams perishes with it. Death is the sharpest blow in the world, and clouds of grief still hang over thousands of homes that lost loved ones prematurely.\n"
        "Indeed, this third decade of the twenty-first century began amidst millions of acres of burning forests. It took the Australian"
    ),
    target_lines=58,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1078, 312, 1385, 520,
    text="government a full year just to calculate the ecological and economic damage inflicted by wildfires across fifty thousand square kilometers. It took us a year to reckon the toll of the Kutch and Latur earthquakes too. People go about their lives concerned only with private affairs, thinking that if Australian",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 312, 1718, 520,
    text="Last winter was so biting that it did the marketing for room heaters all by itself. No season brings joy when pushed to extremes. Lovers of crisp winter breezes who wander carelessly into the woods in such volatile weather end up paying for it with their health.",
    target_lines=7,
    first_indent_pt=9.0,
)
place_png(1078, 529, 1718, 966, "alpviram_illus.png")
place_exact_body_column(
    1078, 974, 1385, 1170,
    text="forests burn, how could those flames ever reach us here? Yet that fire can reach us—because it is burning inside our shared planetary home, Earth, not on some distant planet or moon. Recent reports from the World Meteorological Organization under the United Nations",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 974, 1718, 1170,
    text="Even the simple pleasure of enjoying nature is fading because humanity has contributed nothing to nurturing and preserving it! Nature grants serene joy only to those who live in harmony with it; those who treat natural wealth with",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1178, 1242, 1350,
    text="are enough to rob humanity of its sleep.",
    target_lines=6,
    first_indent_pt=0.0,
)
draw_box(1249, 1179, 1552, 1343, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(1255, 1185, 1546, 1275, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1262, 1180, 1540, 1265,
    lines=["ALPVIRAM"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    1262, 1282, 1540, 1335,
    lines=["Special Editorial Reflection"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1558, 1178, 1718, 1350,
    text="purely consumerist greed all their lives will inevitably face its wrath.",
    target_lines=6,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1078, 1356, 1385, 1524,
    text="In the years ahead, nature's displeasure will only intensify. Notice how rescue operations increasingly struggle to keep pace with each new disaster as extreme weather events grow fiercer.",
    target_lines=6,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 1356, 1718, 1524,
    text="Last winter, middle-class families and tenants rushed to buy room heaters, and despite viral reports of gas and electric geyser accidents,",
    target_lines=6,
    first_indent_pt=9.0,
)
draw_box(1089, 1531, 1712, 1757, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1100, 1538, 1700, 1750,
    lines=[
        "Now Is the Time to Wake Up to the Shift in",
        "Nature's Mood: The Alignment Between Calendar",
        "Months and Actual Weather Patterns Is",
        "Rapidly Disappearing Across the Globe"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)
place_exact_body_column(
    1078, 1764, 1385, 2066,
    text="Nature refuses to bow to human forecasts. Despite advances in meteorological technology, predictions repeatedly falter. Last year the Pune observatory declared that winter would remain mild—only for biting cold to sweep the country! After all, global warming itself means harsher winters alongside scorching summers.",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 1764, 1718, 2066,
    text="their sales surged even amid an economic slowdown. Among all creations, nature endowed human beings with the gift of intellect—yet humanity has used that intellect to treat every natural resource merely as a tool for material comfort, failing to maintain any balance in consuming",
    target_lines=10,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 312, 2050, 2066,
    text=(
        "the priceless ecological wealth gifted to it free of cost.\n"
        "As a result, the natural cycles that once turned with clockwork precision are now faltering. Fury, too, is one of nature's forms. The eternal truth that 'the nurturer can also become the destroyer' now confronts human society as a lived reality. Just as household appliances break down when neglected without regular maintenance, the global environment is showing the strain of relentless abuse. Japanese environmentalists have warned that humanity has inflicted such severe disruption upon the Earth that nature will need this entire century to return to its natural equilibrium.\n"
        "Recognizing the shifting winds and nature's altered temperament, humanity must act before time runs out. Alignment between calendar months and actual weather will become increasingly rare. Deluges that turn deserts into rivers and droughts that reduce green heartlands to dust bowls signal that nature has opened its ledger of accounts with mankind. Across India, rainfall this season has broken 125-year historical records.\n"
        "Researchers working under the aegis of the United Nations have concluded after exhaustive study that the decade from 2010 to 2019 was the hottest in recorded human history. Every nation must now brace for both blistering heatwaves and punishing winters. Rising global mean temperatures have thrown water cycles, winds, forests, rivers, lakes and agriculture into turmoil—making the current decade from 2020 to 2029 even more perilous than the last."
    ),
    target_lines=58,
    first_indent_pt=0.0,
)

# ==============================================================================
# 4. TO THE POINT (AJIT POPAT): WHAT WAS IN THEIR HEARTS CAME TO THEIR LIPS... (COLS 7-8 TOP)
# ==============================================================================
print("Building To The Point (Ajit Popat Column, Cols 7-8 Top)...")
draw_box(2070, 194, 2718, 2074, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    2076, 200, 2712, 344,
    lines=[
        "What Was in Their Hearts Spilled Onto Their Lips:",
        "'We Want Regime Change,' Cry the Anarchists..."
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    2076, 350, 2382, 1020,
    text=(
        "At last, what was hidden in their hearts spilled out onto their lips. On Friday, October 16, during the so-called Tiranga Yatra in New Delhi, bespectacled leftist activist Neha Bora shouted from the window of a police van: 'We want regime change! Bangladesh has shown us the way...' Utter nonsense! Just last week in this very column, I wrote that Chief Election Commissioner Gyanesh Kumar is merely an excuse—the real targets are the Prime Minister and the Home Minister. A few readers found that observation harsh at the time, but now the truth is out in the open.\n"
        "First, let us talk about Bangladesh. Neither Pakistan nor Bangladesh ever achieved stable democracy; military rule always lurked behind a democratic facade. By contrast,"
    ),
    target_lines=22,
    first_indent_pt=9.0,
)
place_exact_body_column(
    2408, 350, 2712, 1020,
    text=(
        "I strongly disagree with those calling for regime change.' At the root of this agitation lies the protesters' resentment against the tightening of the Foreign Contribution Regulation Act (FCRA).\n"
        "Certain self-styled NGOs in our country receive vast sums of money from abroad and brazenly misuse those funds. Let me remind you of one small example: in Uttar Pradesh, not one or two, but 17,000 bogus madrasas were unearthed. Even if 10 to 12 children studied in a genuine school, imagine how crores of rupees in central grants were being siphoned off by 17,000 ghost institutions before Yogi Adityanath shut down the racket.\n"
        "Hundreds of such dubious NGOs across the country openly spend foreign money on anti-national activities."
    ),
    target_lines=22,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1026, 2240, 1280,
    text="there has never been any possibility of military rule in India—a fact that became crystal clear when Indira Gandhi was Prime Minister.",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_box(2247, 1028, 2553, 1280, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(2253, 1034, 2547, 1146, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    2260, 1030, 2540, 1134,
    lines=["TO THE POINT"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    2260, 1158, 2540, 1268,
    lines=["Ajit Popat", "Current Affairs Analysis"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    2560, 1026, 2712, 1280,
    text="Consider Abhishek Deepak: an unemployed Boston University post-graduate who",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 1286, 2382, 2066,
    text=(
        "Indiraji once asked the then Army Chief, the ever-smiling Parsi general Sam Manekshaw, whether the army could ever stage a coup in India. Sam laughed in his trademark style and explained to Madam that young men from every state, language and community form the backbone of the Indian Army; because our armed forces are truly cosmopolitan, a military coup is impossible here.\n"
        "Opposition leaders know this reality very well, which is why they have chosen the dangerous path of street anarchy to destabilize a democratically elected government. In Pakistan and Bangladesh, the armed forces are homogeneous, making military takeovers easy. Here, a coordinated attempt is underway to foment unrest using foreign funds. Even Asaduddin Owaisi stated bluntly on social media: 'Although I oppose Narendra Modi on multiple issues,"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2408, 1286, 2712, 2066,
    text=(
        "returned to Delhi to lead street protests. Where did he get the money to sustain himself, pay rent in Delhi and fund daily demonstrations? Think about it, dear readers. Several such operatives are active in this agitation. Put plainly, just as stone-pelters in Jammu & Kashmir were once paid Rs 500 a day to target security forces, a fixed daily allowance is being paid to mobilize crowds every evening in Delhi. Otherwise, who has the leisure to stage street ruckus every single evening?\n"
        "Even if fifty thousand or a lakh protesters gather in a nation of 140 crore citizens, that is not even a fraction of one percent of the population—and yet they daydream of 'regime change'! Such professional anarchists inventing new pretexts every week must be dealt with firmly under the law. What do you say?"
    ),
    target_lines=25,
    first_indent_pt=0.0,
)

# ==============================================================================
# 5. PRASANGPAT: MAPPLS, INDIA'S INDIGENOUS ALTERNATIVE TO GOOGLE MAPS (COLS 1-3 BOTTOM)
# ==============================================================================
print("Building Prasangpat (Mappls vs Google Maps, Cols 1-3 Bottom)...")
draw_box(82, 2092, 1055, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
draw_box(92, 2102, 1045, 2178, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    100, 2108, 1038, 2172,
    lines=["Navigation Glitches Linked to Fatal Road Accidents Across India"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_display_lines(
    94, 2186, 1042, 2378,
    lines=[
        "Mappls Is India's Indigenous Alternative",
        "to Google Maps—But Lacks Marketing"
    ],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    92, 2386, 388, 3622,
    text=(
        "No one knows from which direction tragedy may strike. While a partial pandal collapse in Kolkata triggered a stampede that claimed 17 lives, in Gwalior an overloaded truck following Google Maps directions lost control and killed 15 devotees.\n"
        "At 1:30 AM, the sugarcane-laden truck plowed into a crowd of pilgrims walking toward the Sheetla Mata temple. Because the driver was unfamiliar with the local terrain, he relied blindly on Google Maps, crashing through a police barricade before skidding down a steep gradient.\n"
        "In this bizarre tragedy, faulty digital navigation has been blamed as the villain. Across the country, almost every four-wheeler and three-wheeler now relies on Google Maps to navigate unfamiliar routes.\n"
        "Real-time location sharing and turn-by-turn directions have made digital navigation an indispensable part of modern travel, guiding motorists to their destinations within a predicted time.\n"
        "Yet blind faith in navigation apps can prove fatal: in a 2024 incident, three young men—including two doctors—drove their car off an unfinished bridge into a river while following Google Maps at night.\n"
        "India's homegrown rival capable of challenging Google Maps is Mappls."
    ),
    target_lines=38,
    first_indent_pt=9.0,
)
place_exact_body_column(
    414, 2386, 720, 2602,
    text="Google's grip over the internet ecosystem is vise-like. From email to mobile operating systems and everyday utility apps, Google is deeply entrenched, and India has struggled to popularize domestic alternatives to Chrome, Gmail or",
    target_lines=7,
    first_indent_pt=0.0,
)
place_png(414, 2609, 720, 2842, "mappls_vs_google.png")
place_exact_body_column(
    414, 2848, 720, 3064,
    text="Google Maps.\nWhile users say they are open to swadeshi apps, free services like Gmail and Google Maps have become so deeply habitual for Indian smartphone users that they feel like an extension of the human body.",
    target_lines=7,
    first_indent_pt=0.0,
)
draw_box(418, 3071, 719, 3250, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(424, 3077, 713, 3172, fill_swatch="GsRedBanner", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    432, 3072, 705, 3162,
    lines=["PRASANGPAT"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    432, 3180, 705, 3240,
    lines=["Contemporary Affairs"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    414, 3256, 720, 3622,
    text=(
        "It is not that Indian innovators have not built alternatives to Gmail or Google Maps, but matched against Google's massive marketing muscle and pre-installed Android defaults, few citizens switch to indigenous apps.\n"
        "Before Gmail dominated email, services like Hotmail were widely used, and though browsers like Firefox and Edge exist, Chrome commands overwhelming market share"
    ),
    target_lines=12,
    first_indent_pt=9.0,
)
place_exact_body_column(
    746, 2386, 1045, 3622,
    text=(
        "across India.\n"
        "To compete with Gmail, Sridhar Vembu's Zoho launched a free email suite, yet it has remained largely confined to enterprise users. Similarly, MapmyIndia launched its indigenous navigation app Mappls to rival Google Maps, and Union IT Minister Ashwini Vaishnaw himself publicly endorsed Mappls after testing its 3D junction views.\n"
        "Digital mapping experts note that accurately charting India's interior rural roads and narrow lanes poses a unique challenge. Last February, Parliament also discussed the need to promote indigenous navigation platforms. Google Maps does not always suggest safe routes for heavy vehicles, yet its monopoly remains unchallenged.\n"
        "In another recorded incident, a family driving from Bihar to Goa chose the shortest route suggested by Google Maps and ended up stranded deep inside a dense Karnataka forest at night.\n"
        "Nearly 5 crore Indians use Google Maps every day. Whenever navigation mishaps occur, calls for 'de-Googling' and adopting swadeshi apps grow louder—yet without aggressive marketing and public adoption, India's own Mappls remains underutilized."
    ),
    target_lines=38,
    first_indent_pt=0.0,
)
draw_box(96, 3633, 1042, 3784, fill_swatch="GsGreenTint", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    106, 3640, 1032, 3776,
    lines=[
        "Calls for 'De-Googling' Surface After Every Mishap, Yet Google's",
        "Ecosystem Dominance Keeps Indigenous Apps on the Sidelines"
    ],
    font_style="Bold",
    align="center",
    stretch_lines=True,
    target_hscale=0.86,
)

# ==============================================================================
# 6. BOJ VINANI MOJ (AKSHAY ANTANI): CROWS ARE HARD TO FIND... (COLS 4-7 BOTTOM)
# ==============================================================================
print("Building Boj Vinani Moj (Akshay Antani Humor Column, Cols 4-7 Bottom)...")
draw_box(1070, 2092, 2390, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_exact_display_lines(
    1080, 2100, 2380, 2206,
    lines=["Crows Are Hard to Find, So Demand Keeps Rising!"],
    font_style="Bold",
    align="left",
    stretch_lines=True,
    target_hscale=0.84,
)
place_exact_body_column(
    1080, 2214, 1385, 3784,
    text=(
        "‘In this multi-party sanctuary of Indian politics, partisan squabbles never cease, turncoats trigger political paralysis by jumping ship, and ruling and opposition flocks peck at each other non-stop. Which party ('paksha') should one praise, Kaka?’\n"
        "Hearing my question, Pathukaka shot back instantly: ‘Beyond partisan politics, only one noble paksha remains in our country—the Shraddha-Paksha (fortnight of ancestors)! Because all honorable members of that wing have already departed for heaven. Once a year during Shraddha-Paksha, our wise ancestors send their official representative down to Earth. And who do they send? The humble crow! That way nobody can accuse our ancestors of still craving rich 'malai' (cream) from heaven—unlike earthly politicians who prowl around 365 days a year just to lap up the cream of power!’\n"
        "I smiled, ‘Kaka, true Unity in Diversity is visible only during Shraddha-Paksha, isn't it?’\n"
        "‘How so?’ Kaka asked. I replied, ‘A living person may belong to any caste, creed or community, but after death everyone's ancestor is awaited in the form of a single black crow cawing 'Kaa-Kaa' on the terrace! That is true unity in diversity!’\n"
        "Kaka chuckled, ‘Does that mean Darwin Dada's theory that humans descended from apes was wrong?’ I said, ‘Darwin formulated evolution after decades of scientific research, whereas feeding kheer-puri to crows during Shraddha-Paksha to satisfy our forefathers is a matter of faith.’\n"
        "‘Ah,’ sighed Kaka, ‘in concrete metropolises like Mumbai, where do crows have the time to eat kheer-puri anymore? In childhood we sang rhymes inviting crows, and today"
    ),
    target_lines=48,
    first_indent_pt=9.0,
)
place_exact_body_column(
    1412, 2214, 1718, 2496,
    text="grown-ups stand on rooftops holding plates of kheer-puri waiting for a crow just like passengers staring at their phones waiting for an app-based cab! And just like cab drivers who cancel trips at the last minute, a passing crow often ignores your terrace and lands on the neighbor's roof instead! What a strange shortage of crows",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2214, 2050, 2496,
    text="became immortal as 'Kekarav' (the peacock's cry). Now that you are so moved by the dwindling population of crows, you should compose an anthology of poems dedicated to crows and title it 'Kaka-Rav'—under the pen name 'Cola-Pee' in honor of your fondness for cola!’",
    target_lines=9,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2504, 1572, 2765,
    text="we have come to!’\nPathukaka mused, ‘While India's human population grows by leaps and bounds,",
    target_lines=8,
    first_indent_pt=0.0,
)
draw_box(1578, 2504, 1884, 2765, fill_swatch="GsYellowTint", fill_tint=1.0, stroke_swatch="GsRedBanner", stroke_weight_pt=2.0)
draw_box(1584, 2510, 1878, 2635, fill_swatch="[Black]", fill_tint=1.0, stroke_weight_pt=0.0)
place_exact_display_lines(
    1590, 2510, 1872, 2624,
    lines=["LIGHTHEARTED", "HUMOR"],
    font_style="Bold",
    fill_swatch="[Paper]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_display_lines(
    1590, 2645, 1872, 2755,
    lines=["Akshay Antani", "Satire & Humor Column"],
    font_style="Bold",
    align="center",
    stretch_lines=False,
)
place_exact_body_column(
    1890, 2504, 2050, 2765,
    text="tell me honestly: has the crow population really shrunk, or have their names been deleted from the 'Maut-daar' (mortal) rolls",
    target_lines=8,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2772, 1718, 2980,
    text="the crow population is shrinking fast—no wonder there is an acute crow shortage during Shraddha-Paksha!’\nAgreeing with Kaka, I pointed out a recent news report: in cities like Mumbai, expanding concrete jungles, felled",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 2772, 2050, 2980,
    text="just like crores of names vanish from voter rolls? After all, crows fly around all day, so their names fly away too!’\nLaughing heartily, Kaka recalled how",
    target_lines=7,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1412, 2986, 1535, 3282,
    text="trees and vanishing greenery have left crows with nowhere to build nests. Moreover,",
    target_lines=9,
    first_indent_pt=0.0,
)
place_png(1541, 2986, 2046, 3282, "crow_cartoon.png")
place_exact_body_column(
    1412, 3288, 1718, 3784,
    text="covered garbage bins and sealed compactor trucks have replaced open dumps, leaving urban crows with little food amid rising air and noise pollution.\nPathukaka exclaimed, ‘If the crow population keeps falling, who will clean up urban waste? Who will eat the Shraddha kheer-puri? And more importantly, who will perch on my balcony every morning calling out my name—'Kaka... Kaka... Kaka'?’\nI teased him, ‘Just as the royal poet Kalapi poured his heartache into a famous poetry collection that",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    1744, 3288, 2050, 3784,
    text="Emperor Akbar once pointed to a flock of crows perched along the ramparts of the Red Fort and asked Birbal: ‘Tell me, Birbal, how many crows live in our Delhi?’ Without blinking, witty Birbal replied: ‘Your Majesty, there are exactly 11,11,111 crows in Delhi right now!’\nAstonished, the Emperor asked what if a recount showed more crows? Birbal smiled: ‘If there are more, Your Majesty, then outstation crows are visiting their Delhi relatives; and if there are fewer, then Delhi's crows have flown out of town on a family summer",
    target_lines=16,
    first_indent_pt=0.0,
)
place_exact_body_column(
    2076, 2214, 2380, 3784,
    text=(
        "vacation!’ Delighted by Birbal's wit, the Emperor rewarded him with ten gold mohurs on the spot.\n"
        "I told Kaka, ‘Do you know that enterprising operators have turned the urban crow shortage into a thriving business by renting out crows?’\n"
        "Stunned, Kaka asked, ‘Who rents out crows?!’ I explained that during Shraddha-Paksha, ‘Rent-a-Crow’ operators have gone viral on social media in parts of Maharashtra. They trap wild crows from forest fringes, tie a long thread to one leg, perch two crows on their shoulders, and walk down city lanes calling out: ‘Rent a crow for Shraddha! Rent a crow!’ Families waiting in vain on sun-baked terraces with plates of kheer-puri call the crow-wallah upstairs; his trained crow pecks at the offering, the ritual is completed in minutes, and he pockets Rs 100 to Rs 150 per terrace! How is that for a profitable seasonal startup?\n"
        "Hearing about rented crows, Pathukaka burst into song: ‘Jhooth bole kauwa kaate, kaale kauwe se dariyo!’ I laughed and reminded him how that iconic song from Raj Kapoor's film 'Bobby' was born. While making 'Mera Naam Joker', the big-hearted food lover Raj Kapoor visited his assistant director's home for dinner. After relishing puris, vegetables and dal tadka served by the assistant director's mother, she affectionately insisted, ‘Beta, you have hardly eaten anything!’ Showman Raj Kapoor grinned and replied, ‘Mummyji, jhooth bole kauwa kaate—don't you see how much I've eaten?’ That playful phrase stayed in his mind and later became the unforgettable chartbuster in 'Bobby'!"
    ),
    target_lines=48,
    first_indent_pt=0.0,
)

# ==============================================================================
# 7. KALPAVRUKSHA: TIMELESS THOUGHTS (COL 8 BOTTOM)
# ==============================================================================
print("Building Kalpavruksha (Quotes Column, Col 8 Bottom)...")
draw_box(2402, 2092, 2718, 3794, stroke_swatch="[Black]", stroke_weight_pt=1.5)
place_png(2408, 2096, 2715, 2439, "kalpavruksha_header_photo.png")
place_exact_display_lines(
    2436, 2110, 2684, 2196,
    lines=["KALPAVRUKSHA"],
    font_style="Bold",
    fill_swatch="[Black]",
    align="center",
    stretch_lines=False,
    custom_font_family="Indian Post Mast",
)
place_exact_body_column(
    2410, 2448, 2710, 3784,
    text=(
        "All knowledge is already inherent within the human mind. Education and experience merely lift the veil to bring that inner wisdom to light.\n- Swami Vivekananda\n*\n"
        "True education is not mere bookish information, but the building of character. Self-knowledge and moral values stand far above mere literacy.\n- Mahatma Gandhi\n*\n"
        "Your greatest illusion is thinking that you have endless time. Life is fleeting; whatever good must be done should be done in this very moment.\n- Gautama Buddha\n*\n"
        "When you live completely in the present moment, time disappears—and that is true meditation. The mind wanders into past and future, but life exists only 'Now'.\n- Osho\n*\n"
        "The life we receive is not short, capabilities are wasted when we squander time. Used wisely, a human life is long and deeply meaningful.\n- Seneca\n*\n"
        "Patience and time are the two most powerful warriors. When the right moment arrives, everything falls into place—one only needs patience.\n- Leo Tolstoy\n*\n"
        "Lost time is never found again. If you love life, do not squander time, for time is the very stuff life is made of.\n- Benjamin Franklin"
    ),
    target_lines=41,
    font_style="Bold",
    first_indent_pt=0.0,
)

# ==============================================================================
# 8. PLACE BOTTOM CMYK BAR (.WEBP)
# ==============================================================================
place_png(0, 3810, 2800, 3974, "bottom_cmyk_bar.png")

cmd("edit.deselectAll")
cmd("view.fitPage")

for target_dir in (DIR_SMAE, DIR_SAME):
    target_dir.mkdir(parents=True, exist_ok=True)
    pd_path = target_dir / "Page_08_English_SameToSame.pagedesigner"
    dns_path = target_dir / "Page_08_English_SameToSame.dns"
    png_path = target_dir / "Page_08_English_SameToSame_Rendered.png"
    pdf_path = target_dir / "Page_08_English_SameToSame_Rendered.pdf"
    rpc("app.save", {"path": str(pd_path)})
    shutil.copyfile(pd_path, dns_path)
    rpc("app.export", {"path": str(png_path), "page": 0, "scale": 2.6667})
    rpc("app.export", {"path": str(pdf_path), "page": 0})

shutil.copyfile(
    DIR_SAME / "Page_08_English_SameToSame_Rendered.png",
    r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\Page_08_English_SameToSame_Rendered.png"
)

print(f"DONE in {time.perf_counter() - t0:.2f}s! Saved Page_08_English_SameToSame.pagedesigner & rendered PNG/PDF.")
sock.close()
