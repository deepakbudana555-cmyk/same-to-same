# -*- coding: utf-8 -*-
"""
Builds and installs `Indian Post Mast.ttf` (`family = "Indian Post Mast"`), an authentic
Gujarat Samachar Calligraphic Style ('Shaily') English Masthead Font:
- Tall, monumental architectural vertical pillars (`CAP_H = 620`, `STEM_W = 146`)
- Narrow, high-contrast vertical counter slits (matching `ગુજરાત સમાચાર`)
- Signature Gujarat Samachar rounded shoulders & circular inward teardrop curl-hooks
- Installed into `%LOCALAPPDATA%\\Microsoft\\Windows\\Fonts\\Indian Post Mast.ttf` + HKCU Registry
  + `Document Fonts\\Indian Post Mast.ttf` so Page Designer 1.0 loads it natively!
"""

import ctypes
import os
import shutil
import winreg
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

SCALE = 2.0
X0 = 200
Y0 = 1250

CAP_H = 610      # Tall, monumental broadsheet masthead height
STEM_W = 142     # Ultra-bold architectural vertical pillar
BAR_H = 122      # Heavy horizontal top/bottom bar


def fu_to_px(x_fu: float, y_fu: float) -> tuple[int, int]:
    return int(round(X0 + x_fu * SCALE)), int(round(Y0 - y_fu * SCALE))


def rect_px(x1: float, y1: float, x2: float, y2: float) -> list[int]:
    px1, py2 = fu_to_px(x1, y1)
    px2, py1 = fu_to_px(x2, y2)
    return [min(px1, px2), min(py1, py2), max(px1, px2), max(py1, py2)]


def draw_gs_top_left_curl(draw: ImageDraw.ImageDraw, x_left: float, y_top: float, stem_x: float):
    """Signature Gujarat Samachar ('ગુજરાત સમાચાર') top-left calligraphic curl hook: solid round inward ball + open white notch."""
    draw.rounded_rectangle(rect_px(x_left, y_top - 152, stem_x + 40, y_top), radius=int(68 * SCALE), fill=255)
    draw.rounded_rectangle(rect_px(x_left + 56, y_top - 230, stem_x, y_top - 76), radius=int(16 * SCALE), fill=0)
    draw.ellipse(rect_px(x_left + 2, y_top - 156, x_left + 74, y_top - 82), fill=255)


def draw_gs_bottom_left_curl(draw: ImageDraw.ImageDraw, x_left: float, y_bot: float, stem_x: float):
    """Signature Gujarat Samachar bottom-left upward-curling hook: solid round ball + open white notch from above."""
    draw.rounded_rectangle(rect_px(x_left, y_bot, stem_x + 40, y_bot + 152), radius=int(68 * SCALE), fill=255)
    draw.rounded_rectangle(rect_px(x_left + 56, y_bot + 76, stem_x, y_bot + 230), radius=int(16 * SCALE), fill=0)
    draw.ellipse(rect_px(x_left + 2, y_bot + 82, x_left + 74, y_bot + 156), fill=255)


def draw_gs_bottom_right_curl(draw: ImageDraw.ImageDraw, stem_right: float, y_bot: float, x_right: float):
    """Mirrored signature Gujarat Samachar bottom-right upward-curling hook."""
    draw.rounded_rectangle(rect_px(stem_right - 40, y_bot, x_right, y_bot + 152), radius=int(68 * SCALE), fill=255)
    draw.rounded_rectangle(rect_px(stem_right, y_bot + 76, x_right - 56, y_bot + 230), radius=int(16 * SCALE), fill=0)
    draw.ellipse(rect_px(x_right - 74, y_bot + 82, x_right - 2, y_bot + 156), fill=255)


def draw_gs_top_right_curl(draw: ImageDraw.ImageDraw, stem_right: float, y_top: float, x_right: float):
    """Mirrored signature Gujarat Samachar top-right downward-curling hook."""
    draw.rounded_rectangle(rect_px(stem_right - 40, y_top - 152, x_right, y_top), radius=int(68 * SCALE), fill=255)
    draw.rounded_rectangle(rect_px(stem_right, y_top - 230, x_right - 56, y_top - 76), radius=int(16 * SCALE), fill=0)
    draw.ellipse(rect_px(x_right - 74, y_top - 156, x_right - 2, y_top - 82), fill=255)


def draw_gs_pillar_foot_curl(draw: ImageDraw.ImageDraw, stem_x: float, y_bot: float = 0.0):
    """Signature calligraphic foot curl on the bottom-left of vertical pillars (matching INDIAN POST & Shaily)."""
    draw.rounded_rectangle(rect_px(stem_x - 54, y_bot, stem_x + 36, y_bot + 116), radius=int(50 * SCALE), fill=255)
    draw.rounded_rectangle(rect_px(stem_x - 16, y_bot + 58, stem_x, y_bot + 172), radius=int(10 * SCALE), fill=0)
    draw.ellipse(rect_px(stem_x - 52, y_bot + 60, stem_x + 2, y_bot + 118), fill=255)


def draw_thick_poly(draw: ImageDraw.ImageDraw, pts_fu: list[tuple[float, float]], fill: int = 255):

    pts_px = [fu_to_px(x, y) for x, y in pts_fu]
    draw.polygon(pts_px, fill=fill)


def build_letter_mask(ch: str) -> tuple[np.ndarray, int]:
    im = Image.new("L", (2400, 1700), 0)
    d = ImageDraw.Draw(im)
    ch_u = ch.upper()

    if ch_u == "I":
        stem_x = 96
        # Monumental flat-topped, flat-bottomed vertical pillar + GS left curls (like 'ગ')
        d.rectangle(rect_px(stem_x, 0, stem_x + STEM_W, CAP_H), fill=255)
        draw_gs_top_left_curl(d, 6, CAP_H, stem_x)
        draw_gs_bottom_left_curl(d, 6, 0, stem_x)
        adv = 266

    elif ch_u == "N":
        lx = 92
        rx = 368
        # Left stem + top-left GS curl; right stem is a pure razor-sharp 'ા' architectural pillar!
        d.rectangle(rect_px(lx, 0, lx + STEM_W - 8, CAP_H), fill=255)
        d.rectangle(rect_px(rx, 0, rx + STEM_W - 6, CAP_H), fill=255)
        draw_thick_poly(d, [
            (lx + 10, CAP_H),
            (lx + STEM_W + 24, CAP_H),
            (rx + STEM_W - 6, 0),
            (rx - 22, 0),
        ], fill=255)
        draw_gs_top_left_curl(d, 2, CAP_H, lx)
        adv = 526

    elif ch_u == "D":
        lx = 92
        rx = 472
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(136 * SCALE), fill=255)
        d.rectangle(rect_px(lx, 0, lx + 175, CAP_H), fill=255)
        # Tall, narrow Gujarat Samachar counter slit
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H, rx - STEM_W + 6, CAP_H - BAR_H), radius=int(38 * SCALE), fill=0)
        draw_gs_top_left_curl(d, 2, CAP_H, lx)
        adv = 498

    elif ch_u == "A":
        lx = 90
        rx = 476
        # 'ત' style rounded top-left arch + razor-sharp right vertical pillar + bottom-left GS curl
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(134 * SCALE), fill=255)
        d.rectangle(rect_px(lx, 0, rx, 300), fill=255)
        d.rectangle(rect_px(rx - STEM_W, 0, rx, CAP_H), fill=255)
        # Upper narrow counter slit
        d.rounded_rectangle(rect_px(lx + STEM_W - 4, 295, rx - STEM_W + 4, CAP_H - BAR_H), radius=int(36 * SCALE), fill=0)
        # Lower counter opening
        d.rounded_rectangle(rect_px(lx + STEM_W - 4, -40, rx - STEM_W + 4, 180), radius=int(24 * SCALE), fill=0)
        draw_gs_bottom_left_curl(d, 0, 0, lx)
        adv = 504

    elif ch_u == "P":
        lx = 92
        rx = 462
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, 225, rx, CAP_H), radius=int(120 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, 335, rx - STEM_W + 10, CAP_H - BAR_H + 4), radius=int(32 * SCALE), fill=0)
        draw_gs_top_left_curl(d, 2, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 2, 0, lx)
        adv = 484

    elif ch_u == "O":
        lx = 24
        rx = 434
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(134 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H, rx - STEM_W, CAP_H - BAR_H), radius=int(38 * SCALE), fill=0)
        adv = 458

    elif ch_u == "S":
        lx = 24
        rx = 428
        # Modeled directly on 'ર' / 'સ' of ગુજરાત સમાચાર!
        d.rounded_rectangle(rect_px(lx, 248, rx, CAP_H), radius=int(116 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 0, rx, 366), radius=int(116 * SCALE), fill=255)
        # Cut upper-right & lower-left openings
        d.rectangle(rect_px(lx + STEM_W - 4, 364, rx + 20, CAP_H - BAR_H + 4), fill=0)
        d.rectangle(rect_px(lx - 20, BAR_H - 4, rx - STEM_W + 4, 250), fill=0)
        # Solid top-right downward curl with open notch from underneath
        d.rounded_rectangle(rect_px(rx - 134, CAP_H - 156, rx, CAP_H), radius=int(56 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(rx - 152, CAP_H - 210, rx - 74, CAP_H - 78), radius=int(14 * SCALE), fill=0)
        d.ellipse(rect_px(rx - 76, CAP_H - 158, rx - 4, CAP_H - 84), fill=255)
        # Solid bottom-left upward curl with open notch from above
        d.rounded_rectangle(rect_px(lx, 0, lx + 134, 156), radius=int(56 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + 74, 78, lx + 152, 210), radius=int(14 * SCALE), fill=0)
        d.ellipse(rect_px(lx + 4, 84, lx + 76, 158), fill=255)
        adv = 452

    elif ch_u == "T":
        lx = 16
        rx = 464
        cx = (lx + rx - STEM_W) / 2.0
        d.rectangle(rect_px(cx, 0, cx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, CAP_H - BAR_H, rx, CAP_H), radius=int(48 * SCALE), fill=255)
        draw_gs_top_left_curl(d, lx, CAP_H, cx)
        draw_gs_top_right_curl(d, cx + STEM_W, CAP_H, rx)
        draw_gs_bottom_left_curl(d, cx - 90, 0, cx)
        adv = 480

    elif ch_u == "C":
        lx = 26
        rx = 426
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(138 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H, rx + 40, CAP_H - BAR_H), radius=int(42 * SCALE), fill=0)
        d.rounded_rectangle(rect_px(rx - 125, CAP_H - 175, rx, CAP_H), radius=int(52 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(rx - 125, 0, rx, 175), radius=int(52 * SCALE), fill=255)
        adv = 452

    elif ch_u == "E":
        lx = 86
        rx = 446
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, CAP_H - BAR_H, rx, CAP_H), radius=int(36 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 250, rx - 45, 360), radius=int(30 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 0, rx, BAR_H), radius=int(36 * SCALE), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 472

    elif ch_u == "R":
        lx = 86
        rx = 460
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, 250, rx, CAP_H), radius=int(118 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, 355, rx - STEM_W + 10, CAP_H - BAR_H + 4), radius=int(32 * SCALE), fill=0)
        # Right leg
        d.rounded_rectangle(rect_px(rx - STEM_W - 10, 0, rx, 290), radius=int(40 * SCALE), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 486

    elif ch_u == "L":
        lx = 86
        rx = 436
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, 0, rx, BAR_H), radius=int(38 * SCALE), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        draw_gs_bottom_right_curl(d, rx - 90, 0, rx)
        adv = 460

    elif ch_u == "M":
        lx = 84
        mx = 278
        rx = 472
        d.rectangle(rect_px(lx, 0, lx + 128, CAP_H), fill=255)
        d.rectangle(rect_px(mx, 80, mx + 120, CAP_H), fill=255)
        d.rectangle(rect_px(rx, 0, rx + 128, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, CAP_H - BAR_H, rx + 128, CAP_H), radius=int(48 * SCALE), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 626

    elif ch_u == "U":
        lx = 84
        rx = 466
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(135 * SCALE), fill=255)
        d.rectangle(rect_px(lx, 180, rx, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H, rx - STEM_W, CAP_H + 40), radius=int(42 * SCALE), fill=0)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        adv = 492

    elif ch_u == "G":
        lx = 26
        rx = 446
        d.rounded_rectangle(rect_px(lx, 0, rx, CAP_H), radius=int(138 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H, rx - STEM_W, CAP_H - BAR_H), radius=int(42 * SCALE), fill=0)
        d.rectangle(rect_px(rx - STEM_W - 10, 290, rx + 20, CAP_H - 165), fill=0)
        d.rounded_rectangle(rect_px(lx + 180, 200, rx, 295), radius=int(28 * SCALE), fill=255)
        adv = 472

    elif ch_u == "B":
        lx = 86
        rx = 462
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, 265, rx - 10, CAP_H), radius=int(110 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 0, rx, 335), radius=int(115 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx + STEM_W, 355, rx - STEM_W, CAP_H - BAR_H + 8), radius=int(30 * SCALE), fill=0)
        d.rounded_rectangle(rect_px(lx + STEM_W, BAR_H - 8, rx - STEM_W + 8, 245), radius=int(32 * SCALE), fill=0)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 488

    elif ch_u == "H":
        lx = 86
        rx = 358
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rectangle(rect_px(rx, 0, rx + STEM_W, CAP_H), fill=255)
        d.rectangle(rect_px(lx, 245, rx + STEM_W, 365), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 526

    elif ch_u == "F":
        lx = 86
        rx = 438
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        d.rounded_rectangle(rect_px(lx, CAP_H - BAR_H, rx, CAP_H), radius=int(36 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 245, rx - 45, 355), radius=int(30 * SCALE), fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 462

    elif ch_u == "K":
        lx = 86
        rx = 462
        d.rectangle(rect_px(lx, 0, lx + STEM_W, CAP_H), fill=255)
        draw_thick_poly(d, [(lx + STEM_W - 20, 270), (rx - STEM_W, CAP_H), (rx, CAP_H), (lx + STEM_W + 40, 220)], fill=255)
        draw_thick_poly(d, [(lx + STEM_W - 10, 340), (lx + STEM_W + 50, 390), (rx, 0), (rx - STEM_W, 0)], fill=255)
        draw_gs_top_left_curl(d, 4, CAP_H, lx)
        draw_gs_bottom_left_curl(d, 4, 0, lx)
        adv = 486

    elif ch_u == "J":
        rx = 260
        d.rounded_rectangle(rect_px(24, 0, rx + STEM_W, CAP_H), radius=int(130 * SCALE), fill=255)
        d.rectangle(rect_px(0, 210, rx, CAP_H + 10), fill=0)
        draw_gs_top_left_curl(d, rx - 82, CAP_H, rx)
        draw_gs_bottom_left_curl(d, 16, 0, 120)
        adv = 428

    elif ch_u == "V":
        lx = 26
        rx = 456
        mx = (lx + rx) / 2.0
        draw_thick_poly(d, [(lx, CAP_H), (lx + STEM_W + 10, CAP_H), (mx + 65, 0), (mx - 65, 0)], fill=255)
        draw_thick_poly(d, [(rx - STEM_W - 10, CAP_H), (rx, CAP_H), (mx + 65, 0), (mx - 65, 0)], fill=255)
        adv = 482

    elif ch_u == "W":
        draw_thick_poly(d, [(20, CAP_H), (150, CAP_H), (225, 0), (110, 0)], fill=255)
        draw_thick_poly(d, [(235, 480), (345, 480), (225, 0), (110, 0)], fill=255)
        draw_thick_poly(d, [(235, 480), (345, 480), (470, 0), (355, 0)], fill=255)
        draw_thick_poly(d, [(430, CAP_H), (560, CAP_H), (470, 0), (355, 0)], fill=255)
        adv = 580

    elif ch_u == "Y":
        lx = 24
        rx = 454
        mx = (lx + rx - STEM_W) / 2.0
        d.rectangle(rect_px(mx, 0, mx + STEM_W, 310), fill=255)
        draw_thick_poly(d, [(lx, CAP_H), (lx + STEM_W, CAP_H), (mx + STEM_W, 260), (mx, 260)], fill=255)
        draw_thick_poly(d, [(rx - STEM_W, CAP_H), (rx, CAP_H), (mx + STEM_W, 260), (mx, 260)], fill=255)
        draw_gs_bottom_left_curl(d, mx - 78, 0, mx)
        adv = 478

    elif ch_u == "Z":
        lx = 26
        rx = 446
        d.rounded_rectangle(rect_px(lx, CAP_H - BAR_H, rx, CAP_H), radius=int(34 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(lx, 0, rx, BAR_H), radius=int(34 * SCALE), fill=255)
        draw_thick_poly(d, [(rx - STEM_W - 20, CAP_H - 40), (rx, CAP_H - 40), (lx + STEM_W + 20, 40), (lx, 40)], fill=255)
        adv = 472

    elif ch == "\u0905" or ch == "\u0906":
        # Devanagari 'अ' (\u0905) and 'आ' (\u0906) in authentic Gujarat Samachar ('ગુજરાત સમાચાર') Shaily Calligraphic Style!
        is_aa = (ch == "\u0906")
        bx_l = 90
        bx_r = 374
        # Upper right-facing arch of 'अ'
        d.rounded_rectangle(rect_px(bx_l, 254, bx_r, CAP_H), radius=int(108 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(-20, 356, bx_r - 128, CAP_H - BAR_H + 4), radius=int(30 * SCALE), fill=0)
        # Lower right-facing arch of 'अ'
        d.rounded_rectangle(rect_px(bx_l, 0, bx_r + 12, 362), radius=int(116 * SCALE), fill=255)
        d.rounded_rectangle(rect_px(-20, 114, bx_r - 122, 256), radius=int(32 * SCALE), fill=0)
        # Signature Gujarat Samachar top-left downward curl & bottom-left upward curl on 'अ'!
        draw_gs_top_left_curl(d, 0, CAP_H, bx_l + 44)
        draw_gs_bottom_left_curl(d, 0, 0, bx_l + 44)
        # Middle waist inward curl ball on the left of 'अ' (matching GS style!)
        d.rounded_rectangle(rect_px(28, 228, bx_r - 56, 346), radius=int(52 * SCALE), fill=255)
        # Middle waist bridge to the first vertical pillar (खड़ी पाई), leaving crisp upper & lower vertical slits!
        stem1_x = 442
        d.rectangle(rect_px(bx_r - 30, 232, stem1_x + 20, 342), fill=255)
        # First monumental architectural vertical pillar (खड़ी पाई) + calligraphic foot curl!
        d.rectangle(rect_px(stem1_x, 0, stem1_x + STEM_W, CAP_H), fill=255)
        draw_gs_pillar_foot_curl(d, stem1_x, 0)
        # Devanagari Shirorekha over the pillars (continuous across the word)
        if is_aa:
            stem2_x = stem1_x + STEM_W + 76
            d.rectangle(rect_px(stem2_x, 0, stem2_x + STEM_W, CAP_H), fill=255)
            draw_gs_pillar_foot_curl(d, stem2_x, 0)
            d.rectangle(rect_px(bx_l + 18, CAP_H - BAR_H, stem2_x + STEM_W + 85, CAP_H), fill=255)
            adv = stem2_x + STEM_W + 28
        else:
            d.rectangle(rect_px(bx_l + 18, CAP_H - BAR_H, stem1_x + STEM_W + 85, CAP_H), fill=255)
            adv = stem1_x + STEM_W + 28

    elif ch == "\u0938":
        # Devanagari 'स' (\u0938) modeled 1:1 on 'સ' of 'ગુજરાત સમાચાર' (સમાચાર)!
        arch_r = 304
        stem_x = 382
        # Upper right-curving arch of 'स'/'સ'
        d.rounded_rectangle(rect_px(68, 240, arch_r, CAP_H), radius=int(100 * SCALE), fill=255)
        d.rectangle(rect_px(-30, 342, arch_r - 128, CAP_H - BAR_H + 4), fill=0)
        # Top-left Gujarat Samachar downward curl hook (exact match to 'સ' in સમાચાર)
        draw_gs_top_left_curl(d, 4, CAP_H, 114)
        # Middle waist left inward curl hook (exact match to the middle curl of 'ર'/'સ' in ગુજરાત સમાચાર!)
        draw_gs_bottom_left_curl(d, 2, 224, 164)
        # Lower vertical leg + bottom-right upward curl foot (exact match to 'ર'/'સ' base in ગુજરાત સમાચાર!)
        leg_x = 132
        d.rectangle(rect_px(leg_x, 0, leg_x + 132, 290), fill=255)
        draw_gs_bottom_right_curl(d, leg_x + 92, 0, arch_r + 24)
        # Middle horizontal bridge connecting waist to right vertical pillar (खड़ी पाई)
        d.rectangle(rect_px(leg_x + 80, 224, stem_x + 20, 334), fill=255)
        # Right monumental architectural vertical pillar (खड़ी पाई) + calligraphic foot curl!
        d.rectangle(rect_px(stem_x, 0, stem_x + STEM_W, CAP_H), fill=255)
        draw_gs_pillar_foot_curl(d, stem_x, 0)
        # Continuous top Shirorekha uniting 'स' cleanly with preceding letter (even with tracking!)
        d.rectangle(rect_px(-110, CAP_H - BAR_H, stem_x + STEM_W + 12, CAP_H), fill=255)
        adv = stem_x + STEM_W + 22

    elif ch == "\u092A":
        # Devanagari 'प' (\u092A) in Gujarat Samachar Shaily Calligraphic Style!
        lx = 92
        rx = 468
        # Rounded bottom U-bowl of 'प' + full-height right vertical pillar
        d.rounded_rectangle(rect_px(lx, 148, rx, CAP_H), radius=int(122 * SCALE), fill=255)
        d.rectangle(rect_px(lx, 260, rx, CAP_H), fill=255)
        d.rectangle(rect_px(rx - STEM_W, 0, rx, CAP_H), fill=255)
        # Narrow Gujarat Samachar vertical counter slit inside 'प'
        d.rounded_rectangle(rect_px(lx + STEM_W - 2, 258, rx - STEM_W + 2, CAP_H - BAR_H + 2), radius=int(32 * SCALE), fill=0)
        # Signature Gujarat Samachar top-left curl hook on 'प' & calligraphic foot curl on pillar!
        draw_gs_top_left_curl(d, 0, CAP_H, lx)
        draw_gs_pillar_foot_curl(d, rx - STEM_W, 0)
        # Continuous heavy Shirorekha across top of 'प'
        d.rectangle(rect_px(lx - 4, CAP_H - BAR_H, rx + 85, CAP_H), fill=255)
        adv = rx + 26

    elif ch == "\u093E":
        # Devanagari 'ा' (\u093E — आ की मात्रा) monumental architectural pillar + foot curl + Shirorekha bridge
        stem_x = 52
        d.rectangle(rect_px(stem_x, 0, stem_x + STEM_W, CAP_H), fill=255)
        draw_gs_pillar_foot_curl(d, stem_x, 0)
        d.rectangle(rect_px(-110, CAP_H - BAR_H, stem_x + STEM_W + 85, CAP_H), fill=255)
        adv = stem_x + STEM_W + 28

    elif ch == "-":
        # Bold Gujarat Samachar calligraphic ribbon hyphen between आस and पास
        lx = 24
        rx = 236
        d.rounded_rectangle(rect_px(lx, 244, rx, 366), radius=int(56 * SCALE), fill=255)
        adv = 260

    else:
        try:
            f_base = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", int(680 * SCALE))
        except Exception:
            f_base = ImageFont.load_default()
        bbox = d.textbbox((0, 0), ch_u, font=f_base)
        w = bbox[2] - bbox[0]
        for dx in range(-22, 23, 6):
            for dy in range(-10, 11, 5):
                d.text((X0 - bbox[0] + 36 + dx, Y0 - bbox[3] + dy), ch_u, font=f_base, fill=255)
        adv = int((w / SCALE) + 84)

    return np.array(im), adv


def mask_to_tt_glyph(mask: np.ndarray, glyf_table):
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    pen = TTGlyphPen(glyf_table)
    if hierarchy is None or len(contours) == 0:
        return pen.glyph()

    hierarchy = hierarchy[0]
    for idx, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < 30:
            continue
        approx = cv2.approxPolyDP(cnt, 1.25, True)
        pts_fu = []
        for pt in approx:
            px, py = float(pt[0][0]), float(pt[0][1])
            xfu = int(round((px - X0) / SCALE))
            yfu = int(round((Y0 - py) / SCALE))
            pts_fu.append((xfu, yfu))
        if len(pts_fu) < 3:
            continue

        area = 0.0
        for i in range(len(pts_fu)):
            x1, y1 = pts_fu[i]
            x2, y2 = pts_fu[(i + 1) % len(pts_fu)]
            area += (x1 * y2 - x2 * y1)

        is_hole = hierarchy[idx][3] != -1
        if not is_hole and area > 0:
            pts_fu.reverse()
        elif is_hole and area < 0:
            pts_fu.reverse()

        pen.moveTo(pts_fu[0])
        for p in pts_fu[1:]:
            pen.lineTo(p)
        pen.closePath()

    return pen.glyph()


def build_and_install_masthead_fonts():
    backup_path = Path(r"E:\RND\HINDI-GUJRAT\Fonts\DB Hindi Mast_orig_backup.ttf")
    font = TTFont(str(backup_path))
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font.getBestCmap()

    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        mask, adv = build_letter_mask(ch)
        tt_glyph = mask_to_tt_glyph(mask, glyf)
        tt_glyph.recalcBounds(glyf)
        lsb = getattr(tt_glyph, "xMin", 0) or 0
        for target_ch in (ch, ch.lower()):
            gname = cmap.get(ord(target_ch))
            if gname and gname in glyf.glyphs:
                glyf[gname] = tt_glyph
                hmtx.metrics[gname] = (adv, lsb)

    # Also build authentic Gujarat Samachar Calligraphic ('Shaily') Devanagari glyphs for 'आस-पास'
    for ch in ("\u0905", "\u0906", "\u0938", "\u092A", "\u093E", "-"):
        mask, adv = build_letter_mask(ch)
        tt_glyph = mask_to_tt_glyph(mask, glyf)
        tt_glyph.recalcBounds(glyf)
        lsb = getattr(tt_glyph, "xMin", 0) or 0
        gname = cmap.get(ord(ch))
        if gname and gname in glyf.glyphs:
            glyf[gname] = tt_glyph
            hmtx.metrics[gname] = (adv, lsb)
            print(f"Updated Devanagari/Masthead glyph {ch!r} ({gname}) -> adv={adv}, lsb={lsb}")

    sp_name = cmap.get(ord(" "))
    if sp_name and sp_name in hmtx.metrics:
        hmtx.metrics[sp_name] = (170, 0)

    local_fonts_dir = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\ADMIN\AppData\Local")) / "Microsoft" / "Windows" / "Fonts"

    # Save updated DB Hindi Mast.ttf
    db_targets = [
        Path(r"C:\Windows\Fonts\DB Hindi Mast.ttf"),
        Path(r"E:\RND\HINDI-GUJRAT\Fonts\DB Hindi Mast.ttf"),
        Path(r"E:\RND\Custom_Fonts\DB Hindi Mast.ttf"),
        Path(r"E:\RND\SAME TO SAME GUJRATI NEWS\Document Fonts\DB Hindi Mast.ttf"),
        Path(r"E:\RND\SAME TO SMAE GUJRATI NEWS\Document Fonts\DB Hindi Mast.ttf"),
        local_fonts_dir / "DB Hindi Mast.ttf",
    ]
    for t in db_targets:
        try:
            for _ in range(3):
                ctypes.windll.gdi32.RemoveFontResourceW(str(t))
            t.parent.mkdir(parents=True, exist_ok=True)
            font.save(str(t))
            ctypes.windll.gdi32.AddFontResourceW(str(t))
        except Exception as e:
            print("Warning saving DB Hindi Mast:", t, e)

    # Also save as 'Indian Post Mast.ttf' with family name 'Indian Post Mast'
    for rec in font["name"].names:
        if rec.nameID in (1, 3, 4, 6, 16):
            txt = "IndianPostMast" if rec.nameID == 6 else "Indian Post Mast"
            rec.string = txt.encode("utf-16-be") if rec.isUnicode() else txt.encode("latin-1", errors="ignore")

    ip_targets = [
        Path(r"E:\RND\Custom_Fonts\Indian Post Mast.ttf"),
        Path(r"E:\RND\Custom_Fonts\Indian_Post_Shaily_v2.ttf"),
        Path(r"E:\RND\SAME TO SAME GUJRATI NEWS\Document Fonts\Indian Post Mast.ttf"),
        Path(r"E:\RND\SAME TO SMAE GUJRATI NEWS\Document Fonts\Indian Post Mast.ttf"),
        local_fonts_dir / "Indian Post Mast.ttf",
    ]
    for t in ip_targets:
        try:
            for _ in range(3):
                ctypes.windll.gdi32.RemoveFontResourceW(str(t))
            t.parent.mkdir(parents=True, exist_ok=True)
            font.save(str(t))
            ctypes.windll.gdi32.AddFontResourceW(str(t))
        except Exception as e:
            print("Warning saving Indian Post Mast:", t, e)

    # Register in HKCU Fonts Registry so Page Designer & Windows see 'Indian Post Mast'
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Indian Post Mast (TrueType)", 0, winreg.REG_SZ, str(local_fonts_dir / "Indian Post Mast.ttf"))
            winreg.SetValueEx(key, "DB Hindi Mast (TrueType)", 0, winreg.REG_SZ, str(local_fonts_dir / "DB Hindi Mast.ttf"))
    except Exception as e:
        print("Registry note:", e)

    # Render 3-tier side-by-side visual comparison: Gujarati ('ગુજરાત સમાચાર'), Hindi ('आस-पास'), and English ('INDIAN POST')!
    orig_guj = Image.open(r"E:\RND\SAME TO SMAE GUJRATI NEWS\Page_01_Assets\masthead_6col.png").convert("RGB")
    comp = Image.new("RGB", (orig_guj.width, orig_guj.height * 3 + 70), (255, 255, 255))
    comp.paste(orig_guj, (0, 0))

    f_mast = ImageFont.truetype(r"E:\RND\Custom_Fonts\Indian_Post_Shaily_v2.ttf", 340)

    # Row 2: Hindi Calligraphic Masthead ('आस-पास')
    tmp_hi = Image.new("RGB", (2350, 340), (255, 255, 255))
    dt_hi = ImageDraw.Draw(tmp_hi)
    dt_hi.text((30, -25), "आस-पास", font=f_mast, fill=(0, 0, 0))
    arr_hi = np.array(tmp_hi)
    ys_h, xs_h = np.where(arr_hi[:, :, 0] < 128)
    crop_hi = tmp_hi.crop((max(0, int(xs_h.min()) - 6), max(0, int(ys_h.min()) - 6), min(tmp_hi.width, int(xs_h.max()) + 6), min(tmp_hi.height, int(ys_h.max()) + 6)))
    stretched_hi = crop_hi.resize((orig_guj.width - 140, 250), Image.Resampling.LANCZOS)
    comp.paste(stretched_hi, (70, orig_guj.height + 35))

    # Row 3: English Calligraphic Masthead ('INDIAN POST')
    tmp = Image.new("RGB", (2350, 320), (255, 255, 255))
    dt = ImageDraw.Draw(tmp)
    dt.text((15, -35), "INDIAN POST", font=f_mast, fill=(0, 0, 0))
    arr = np.array(tmp)
    ys, xs = np.where(arr[:, :, 0] < 128)
    crop_box = (max(0, int(xs.min()) - 6), max(0, int(ys.min()) - 6), min(tmp.width, int(xs.max()) + 6), min(tmp.height, int(ys.max()) + 6))
    tmp_cropped = tmp.crop(crop_box)
    tmp_stretched = tmp_cropped.resize((orig_guj.width - 24, 256), Image.Resampling.LANCZOS)
    comp.paste(tmp_stretched, (12, orig_guj.height * 2 + 65))

    out_preview = Path(r"C:\Users\ADMIN\.gemini\antigravity\brain\5fe0d377-f76e-4a0c-9696-b8a27b48a7d6\indian_post_masthead_comparison.png")
    comp.save(str(out_preview))
    print("Saved 3-Edition Calligraphic Masthead comparison preview to:", out_preview)


if __name__ == "__main__":
    build_and_install_masthead_fonts()
