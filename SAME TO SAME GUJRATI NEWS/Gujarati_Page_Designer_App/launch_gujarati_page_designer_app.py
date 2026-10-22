# -*- coding: utf-8 -*-
r"""
GUJARAT SAMACHAR / AAS-PAAS / INDIAN POST (3 EDITIONS × 10 PAGES SAME-TO-SAME) — LIVE STUDIO SERVER
====================================================================================================
Dedicated standalone server on Port 47898:
  http://127.0.0.1:47898/Gujarati_Page_Designer_App.html

Features 3 Top-Level Edition Menus:
  - Menu 1 (`gujarati`): ગુજરાતી (ગુજરાત સમાચાર — 10 Pages Same-to-Same)
  - Menu 2 (`hindi`):    हिन्दी (आस-पास — 10 Pages Same-to-Same)
  - Menu 3 (`english`):  ENGLISH (INDIAN POST — 10 Pages Same-to-Same, Calligraphic Masthead & .webp Ads)

Capabilities:
  1. Click Any Page (Page 01..10) in Any Edition -> Live Re-Draw in Page Designer 1.0 (Port 47123):
     - Brings Page Designer 1.0 window to the front on `winsta0\default`
     - Ensures Edit Mode (`view.screenMode = "normal"`, `frameEdges = ON`, `guides = ON`)
     - Opens the active edition's 10-page combined `.pagedesigner` document
     - Jumps to the clicked page (`view.goToPage` + `view.fitPage`)
     - Hides all items on that page and progressively re-draws every element from top to bottom
     - Leaves the page in Edit Mode with a headline text frame selected so the user can edit
       any text or frame directly inside Page Designer 1.0.
  2. Right-Side Multi-Column Editor in the Localhost Web App:
     - Organizes every story on Pages 01..10 across all 3 editions into explicit editable columns:
       * HEADLINE
       * SUBHEAD
       * BYLINE
       * INTRO
       * PHOTO CHANGE (Library Picker + 1-Click PC Upload, saved as .webp for English)
       * PHOTO CAPTION
       * BODY COPY
"""

import argparse
import base64
import http.server
import io
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
import zipfile
from pathlib import Path
from PIL import Image, ImageOps

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
DIR_SAME = HERE.parent  # E:\RND\SAME TO SAME GUJRATI NEWS
RND_ROOT = DIR_SAME.parent  # E:\RND
DIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"

if str(RND_ROOT) not in sys.path:
    sys.path.insert(0, str(RND_ROOT))

EDITION_CONFIG = {
    "gujarati": {
        "key": "gujarati",
        "menu_label": "1. ગુજરાતી (ગુજરાત સમાચાર)",
        "masthead_title": "ગુજરાત સમાચાર",
        "combined_name": "Gujarat_Samachar_All_10_Pages_SameToSame",
        "page_file_pattern": "Page_{pnum:02d}_SameToSame",
        "rendered_pattern": "Page_{pnum:02d}_SameToSame_Rendered.png",
        "saved_png_pattern": "Gujarati_Page_{pnum:02d}.png",
        "thumb_pattern": "gujarati_page_{pnum:02d}_thumb.jpg",
        "script_pattern": "build_page_{pnum:02d}_same_to_same.py",
        "combiner_module": "build_all_10_pages_same_to_same",
        "combiner_func": "build_combined_10_page_document",
    },
    "hindi": {
        "key": "hindi",
        "menu_label": "2. हिन्दी (आस-पास)",
        "masthead_title": "आस-पास (हिंदी गुजरात समाचार)",
        "combined_name": "Hindi_Gujarat_Samachar_All_10_Pages_SameToSame",
        "page_file_pattern": "Page_{pnum:02d}_Hindi_SameToSame",
        "rendered_pattern": "Page_{pnum:02d}_Hindi_SameToSame_Rendered.png",
        "saved_png_pattern": "Hindi_Page_{pnum:02d}.png",
        "thumb_pattern": "hindi_page_{pnum:02d}_thumb.jpg",
        "script_pattern": "build_hindi_page_{pnum:02d}_same_to_same.py",
        "combiner_module": "build_all_10_hindi_pages_same_to_same",
        "combiner_func": "build_combined_10_hindi_page_document",
    },
    "english": {
        "key": "english",
        "menu_label": "3. ENGLISH (INDIAN POST)",
        "masthead_title": "INDIAN POST (English Edition)",
        "combined_name": "English_Gujarat_Samachar_All_10_Pages_SameToSame",
        "page_file_pattern": "Page_{pnum:02d}_English_SameToSame",
        "rendered_pattern": "Page_{pnum:02d}_English_SameToSame_Rendered.png",
        "saved_png_pattern": "English_Page_{pnum:02d}.png",
        "thumb_pattern": "english_page_{pnum:02d}_thumb.jpg",
        "script_pattern": "build_english_page_{pnum:02d}_same_to_same.py",
        "combiner_module": "build_all_10_english_pages_same_to_same",
        "combiner_func": "build_combined_10_english_page_document",
    },
}

SAVED_PAGES_DIR = HERE / "saved_pages"
THUMBS_DIR = HERE / "thumbnails"
PHOTOS_DIR = HERE / "photos"
HTML_FILE = HERE / "Gujarati_Page_Designer_App.html"

APP_PORT = 47898
PD_PORT = 47123
PD_PORTS = (47123, 49200)

for _d in (SAVED_PAGES_DIR, THUMBS_DIR, PHOTOS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

PAGE_META_BY_EDITION = {
    "gujarati": {
        1: {"badge": "PAGE 01", "section": "પહેલું પાનું (FRONT PAGE)", "title": "Front Page — ગુજરાત સમાચાર Masthead, Satellite Lead, Ravana Dahan, Trade Deal, Tiger Firing & Jio IPO", "subtitle": "8-Col Masthead • US-Russia Satellite Lead • Zelensky Box • Delhi Ni Vaat • Tiger Shroff Firing • Jio IPO"},
        2: {"badge": "PAGE 02", "section": "ગુજરાત / અમદાવાદ (CITY P-2)", "title": "Page 02 — Dussehra Jalebi-Fafda Feature, Garba AI QR Pass Scam & Riverfront Parking", "subtitle": "Jalebi-Fafda Box • Vastrapur Ganthiya Seal • Garba QR Scam • 60-Ft Ravana • RTE School • Riverfront Parking"},
        3: {"badge": "PAGE 03", "section": "ગુજરાત (CITY & STATE P-3)", "title": "Page 03 — Gujarat University Online Courses Policy, PSI Warrant & Narco-Terror Case", "subtitle": "GU Online Courses Internship • BA-BCom Demand Box • PSI Warrant • ₹21,000 Cr Narco-Terror • Festive Ads"},
        4: {"badge": "PAGE 04", "section": "ગુજરાત (STATE & NOTICES P-4)", "title": "Page 04 — Porbandar Reel Politics, Vaat Vaatma, Solar Power Cut, Seva Setu & Public Notices", "subtitle": "Gen-Z Reel Politics • Vaat Vaatma • Solar Power Cut • Double Decker Train • MBBS • 100% Editable Public Notices"},
        5: {"badge": "PAGE 05", "section": "ગુજરાત (CIVIC & HEALTH P-5)", "title": "Page 05 — Nava Vadaj Sports Complex, MGNREGA Unpaid Wages, Osteoporosis & Bapunagar Seizure", "subtitle": "Nava Vadaj Sports Complex Fee • MGNREGA ₹3.43 Cr Pending • World Osteoporosis Day • Bapunagar Heroin Case"},
        6: {"badge": "PAGE 06", "section": "ગુજરાત / અવસાન નોંધ (P-6)", "title": "Page 06 — Gauchar Land PIL, Gujarat Power Crisis, Obituaries (અવસાન નોંધ) & Public Notices", "subtitle": "Gauchar Land High Court PIL • Power Crisis & Water Shortage • Editable Obituaries • Editable Public Notices"},
        7: {"badge": "PAGE 07", "section": "વ્યાપાર સમાચાર (BUSINESS P-7)", "title": "Page 07 — Edible Oil Import Surge, Sugar MSP ₹50 Demand, IT Mutual Funds & Jio IPO Box", "subtitle": "Edible Oil Imports +11% • Sugar MSP Hike • IT Mutual Funds Table • Jio ₹30,213 Cr IPO • Global Urea Price Drop"},
        8: {"badge": "PAGE 08", "section": "તંત્રીલેખ / વિચાર (EDITORIAL P-8)", "title": "Page 08 — Editorial (કોર્પોરેટ કૃષિનું પ્રભાત), Alpviram, To The Point, Mappls & Boj Vinani Moj", "subtitle": "Editorial • Alpviram Climate Essay • Ajit Popat (To The Point) • Swadeshi Mappls vs Google Maps • Akshay Antani"},
        9: {"badge": "PAGE 09", "section": "રાષ્ટ્રીય / આંતરરાષ્ટ્રીય (P-9)", "title": "Page 09 — Page-1 Continuations, Climate Record Warning, 20 Most Polluted Cities & Public Notices", "subtitle": "Delhi Ni Vaat Cont. • Climate 7 Indicators • World's 20 Polluted Cities • South India Monsoon • Editable Notices"},
        10: {"badge": "PAGE 10", "section": "વ્યાપાર સમાચાર (MARKETS P-10)", "title": "Page 10 — Sensex Crash (-876 Pts), Gold-Silver Bullion Tables, Garment Exports & Notices", "subtitle": "Sensex 73,853 Crash • FMCG Margins • Gold-Silver & Cash-Future Tables • US Garment Exports • Editable Notices"},
    },
    "hindi": {
        1: {"badge": "PAGE 01", "section": "मुख्य पृष्ठ (FRONT PAGE)", "title": "Front Page — आस-पास Masthead, Satellite Lead, Ravana Dahan, Trade Deal, Tiger Firing & Jio IPO", "subtitle": "8-Col आस-पास Masthead • US-Russia Satellite Lead • Zelensky Box • दिल्ली की बात • Tiger Shroff Firing • Jio IPO"},
        2: {"badge": "PAGE 02", "section": "गुजरात / अहमदाबाद (CITY P-2)", "title": "Page 02 — दशहरा फाफड़ा-जलेबी, गरबा AI QR पास ठगी और रिवरफ्रंट पार्किंग", "subtitle": "फाफड़ा-जलेबी विशेष • वस्त्रपुर गांठिया सील • गरबा पास ठगी • ६० फीट रावण • RTE स्कूल • रिवरफ्रंट पार्किंग"},
        3: {"badge": "PAGE 03", "section": "गुजरात (CITY & STATE P-3)", "title": "Page 03 — गुजरात यूनिवर्सिटी ऑनलाइन कोर्स नीति, PSI वारंट और नार्को-टेरर केस", "subtitle": "GU ऑनलाइन कोर्स इंटर्नशिप • BA-BCom डिमांड • PSI वारंट • ₹२१,००० करोड़ नार्को-टेरर • त्योहारी विज्ञापन"},
        4: {"badge": "PAGE 04", "section": "गुजरात (STATE & NOTICES P-4)", "title": "Page 04 — पोरबंदर रील पॉलिटिक्स, बात-बात में, सोलर पावर कट, सेवा सेतु और सार्वजनिक सूचना", "subtitle": "Gen-Z रील पॉलिटिक्स • बात-बात में • सोलर पावर कट • डबल डेकर ट्रेन • MBBS • १००% एडिटेबल सार्वजनिक सूचना"},
        5: {"badge": "PAGE 05", "section": "गुजरात (CIVIC & HEALTH P-5)", "title": "Page 05 — नवा वाडज स्पोर्ट्स कॉम्प्लेक्स, मनरेगा बकाया वेतन, ऑस्टियोपोरोसिस और बापूनगर जब्ती", "subtitle": "नवा वाडज स्पोर्ट्स कॉम्प्लेक्स शुल्क • मनरेगा ₹३.४३ करोड़ बकाया • ऑस्टियोपोरोसिस दिवस • बापूनगर हेरोइन केस"},
        6: {"badge": "PAGE 06", "section": "गुजरात / शोक संदेश (P-6)", "title": "Page 06 — गौचर भूमि जनहित याचिका, गुजरात बिजली संकट, शोक संदेश और सार्वजनिक सूचना", "subtitle": "गौचर भूमि हाईकोर्ट PIL • बिजली और जल संकट • एडिटेबल शोक संदेश • एडिटेबल सार्वजनिक सूचना"},
        7: {"badge": "PAGE 07", "section": "व्यापार समाचार (BUSINESS P-7)", "title": "Page 07 — खाद्य तेल आयात में उछाल, चीनी MSP ₹५० मांग, IT म्यूचुअल फंड और जियो IPO", "subtitle": "खाद्य तेल आयात +११% • चीनी MSP वृद्धि • IT म्यूचुअल फंड • जियो ₹३०,२१३ करोड़ IPO • वैश्विक यूरिया भाव"},
        8: {"badge": "PAGE 08", "section": "संपादकीय / विचार (EDITORIAL P-8)", "title": "Page 08 — संपादकीय (कॉर्पोरेट कृषि का प्रभात), अल्पविराम, टू द पॉइंट, प्रसंगपट और कल्पवृक्ष", "subtitle": "संपादकीय • अल्पविराम • अजीत पोपट (टू द पॉइंट) • स्वदेशी Mappls बनाम Google Maps • अक्षय अंताणी"},
        9: {"badge": "PAGE 09", "section": "राष्ट्रीय / अंतरराष्ट्रीय (P-9)", "title": "Page 09 — प्रथम पृष्ठ का शेष, क्लाइमेट चेंज चेतावनी, २० सबसे प्रदूषित शहर और सार्वजनिक सूचना", "subtitle": "दिल्ली की बात शेष • क्लाइमेट ७ संकेत • विश्व के २० प्रदूषित शहर • दक्षिण भारत मानसून • सार्वजनिक सूचना"},
        10: {"badge": "PAGE 10", "section": "व्यापार समाचार (MARKETS P-10)", "title": "Page 10 — सेंसेक्स ८७६ अंक टूटा, सोना-चांदी सर्राफा टेबल, गारमेंट निर्यात और सार्वजनिक सूचना", "subtitle": "सेंसेक्स ७३,८५३ • FMCG मार्जिन • सोना-चांदी व कैश-फ्यूचर टेबल • US गारमेंट ऑर्डर • सार्वजनिक सूचना"},
    },
    "english": {
        1: {"badge": "PAGE 01", "section": "FRONT PAGE (INDIAN POST)", "title": "Front Page — INDIAN POST Shaily Masthead, Satellite Lead, Ravana Dahan, Trade Deal, Tiger Firing & Jio IPO", "subtitle": "8-Col INDIAN POST Calligraphic Masthead • US-Russia Satellite • Zelensky Box • Talk of Delhi • Tiger Firing • Jio IPO"},
        2: {"badge": "PAGE 02", "section": "AHMEDABAD / CITY (P-2)", "title": "Page 02 — Dussehra Fafda-Jalebi Feast, Garba AI QR Pass Scam & Riverfront Multi-Level Parking", "subtitle": "Fafda-Jalebi Feature • Vastrapur Ganthiya Sealed • Garba QR Scam • 60-Ft Ravana • RTE School • Riverfront Parking"},
        3: {"badge": "PAGE 03", "section": "GUJARAT (CITY & STATE P-3)", "title": "Page 03 — Gujarat University Online Courses Policy, PSI Warrant & Rs 21,000-Cr Narco-Terror Case", "subtitle": "GU Online Courses Internship • BA-BCom Surge • PSI Warrant • Rs 21,000 Cr Narco-Terror • .webp Festive Ads"},
        4: {"badge": "PAGE 04", "section": "GUJARAT (STATE & NOTICES P-4)", "title": "Page 04 — Porbandar Reel Politics, By The Way, Solar Power Cut, Seva Setu & Public Notices", "subtitle": "Gen-Z Reel Politics • By The Way Humor • Solar Power Curtailment • Double-Decker Train • MBBS • Editable Notices"},
        5: {"badge": "PAGE 05", "section": "GUJARAT (CIVIC & HEALTH P-5)", "title": "Page 05 — Nava Vadaj Sports Complex Fee Hike, MGNREGA Unpaid Wages, Osteoporosis & Bapunagar Raid", "subtitle": "Nava Vadaj Sports Complex • MGNREGA Rs 3.43 Cr Unpaid • World Osteoporosis Day • Bapunagar Heroin Seizure"},
        6: {"badge": "PAGE 06", "section": "GUJARAT / OBITUARIES (P-6)", "title": "Page 06 — Gauchar Land Encroachment PIL, Gujarat Power Crisis, Obituaries & 15 Public Notices", "subtitle": "Gauchar Land High Court PIL • Power & Water Crisis • Editable Obituaries • 15 Editable English Public Notices"},
        7: {"badge": "PAGE 07", "section": "BUSINESS NEWS (P-7)", "title": "Page 07 — Edible Oil Import Surge, Sugar MSP Rs 50 Demand, IT Mutual Funds & Jio Platforms IPO", "subtitle": "Edible Oil Imports +11% • Sugar MSP Hike • IT Mutual Funds • Jio Rs 30,213 Cr IPO • Global Urea Drop • .webp Ad"},
        8: {"badge": "PAGE 08", "section": "EDITORIAL & OPINION (P-8)", "title": "Page 08 — Editorial (The Dawn of Corporate Agriculture), Alpviram, To The Point, Prasangpat & Kalpavruksha", "subtitle": "Editorial • Alpviram Climate Essay • Ajit Popat (To The Point) • Mappls vs Google Maps • Akshay Antani • Kalpavruksha"},
        9: {"badge": "PAGE 09", "section": "NATIONAL / INTERNATIONAL (P-9)", "title": "Page 09 — Page-1 Continuations, Climate Vital Signs Warning, 20 Most Polluted Cities & Public Notices", "subtitle": "Talk of Delhi Cont. • Climate 7 Vital Signs • 13 Indian Cities in Top 20 • South India Monsoon • 8 Public Notices"},
        10: {"badge": "PAGE 10", "section": "BUSINESS & MARKETS (P-10)", "title": "Page 10 — Sensex Plunges 876 Pts, Forex/Bullion/Stock Tables, US Garment Orders & Public Notices", "subtitle": "Sensex 73,853 Crash • FMCG Margins • Forex, Bullion & Top Losers Tables • US Garment Orders • 4 Public Notices"},
    },
}


def normalize_edition(edition: str) -> str:
    ed = str(edition or "gujarati").strip().lower()
    return ed if ed in EDITION_CONFIG else "gujarati"


# ==============================================================================
# INITIAL ASSET & PREVIEW SYNC ACROSS ALL 3 EDITIONS
# ==============================================================================
def sync_initial_previews_and_photos():
    """
    Copies all rendered page PNGs across Gujarati, Hindi, and English editions into
    `saved_pages/` + generates `thumbnails/`, and copies all photo/ad assets (`.png`, `.jpg`, `.webp`)
    from `Page_01_Assets`..`Page_10_Assets` into `photos/`.
    Also ensures `.dns` mirrors exist alongside `.pagedesigner` files on fresh git clones.
    """
    DIR_SAME.mkdir(parents=True, exist_ok=True)
    DIR_SMAE.mkdir(parents=True, exist_ok=True)
    for pd_file in DIR_SAME.glob("*.pagedesigner"):
        dns_file = pd_file.with_suffix(".dns")
        if not dns_file.exists():
            try:
                shutil.copy2(pd_file, dns_file)
            except Exception:
                pass

    for ed_key, cfg in EDITION_CONFIG.items():
        for pnum in range(1, 11):
            ren_name = cfg["rendered_pattern"].format(pnum=pnum)
            src_png = DIR_SAME / ren_name
            if not src_png.exists():
                src_png = DIR_SMAE / ren_name
            dst_png = SAVED_PAGES_DIR / cfg["saved_png_pattern"].format(pnum=pnum)
            thumb_jpg = THUMBS_DIR / cfg["thumb_pattern"].format(pnum=pnum)
            if not src_png.exists() and dst_png.exists():
                try:
                    shutil.copy2(dst_png, DIR_SAME / ren_name)
                    src_png = DIR_SAME / ren_name
                except Exception:
                    src_png = dst_png
            if src_png.exists():
                if not dst_png.exists() or src_png.stat().st_mtime > dst_png.stat().st_mtime:
                    shutil.copy2(src_png, dst_png)
                if not thumb_jpg.exists() or src_png.stat().st_mtime > thumb_jpg.stat().st_mtime:
                    try:
                        with Image.open(src_png) as im:
                            im_rgb = im.convert("RGB")
                            tw = 760
                            th = int(round(im_rgb.height * (tw / float(im_rgb.width))))
                            im_rgb.resize((tw, th), Image.Resampling.LANCZOS).save(thumb_jpg, quality=88)
                    except Exception:
                        pass

    for pnum in range(1, 11):
        for base_dir in (DIR_SMAE, DIR_SAME):
            ad = base_dir / f"Page_{pnum:02d}_Assets"
            if ad.exists():
                for f in ad.iterdir():
                    if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                        dst_f = PHOTOS_DIR / f.name
                        if not dst_f.exists():
                            shutil.copy2(f, dst_f)


# ==============================================================================
# CROSS-PLATFORM FONT INSTALLER & ASSET PATH LOCALIZER (macOS / Windows / Linux)
# ==============================================================================
def install_bundled_fonts_for_os() -> int:
    """
    Automatically installs all bundled .ttf / .otf fonts from `Document Fonts/` into:
      - macOS (`darwin`): `~/Library/Fonts`
      - Windows (`win32`): `%LOCALAPPDATA%/Microsoft/Windows/Fonts`
      - Linux: `~/.local/share/fonts`
    Additionally, Page Designer 1.0 automatically scopes `Document Fonts/` next to `.pagedesigner` files.
    """
    doc_fonts_dir = DIR_SAME / "Document Fonts"
    if not doc_fonts_dir.exists():
        doc_fonts_dir = DIR_SMAE / "Document Fonts"
    if not doc_fonts_dir.exists():
        return 0

    if sys.platform == "darwin":
        user_fonts = Path.home() / "Library" / "Fonts"
    elif sys.platform == "win32":
        local_app = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        user_fonts = Path(local_app) / "Microsoft" / "Windows" / "Fonts"
    else:
        user_fonts = Path.home() / ".local" / "share" / "fonts"

    try:
        user_fonts.mkdir(parents=True, exist_ok=True)
    except Exception:
        return 0

    copied = 0
    for f in doc_fonts_dir.iterdir():
        if f.is_file() and f.suffix.lower() in (".ttf", ".otf", ".ttc"):
            dst = user_fonts / f.name
            try:
                if not dst.exists() or f.stat().st_size != dst.stat().st_size:
                    shutil.copy2(f, dst)
                    copied += 1
            except Exception:
                pass
    return copied


def localize_pagedesigner_asset_links():
    """
    Rewrites any hardcoded `E:/RND/...` or `E:\\RND\\...` asset link paths inside `.pagedesigner`
    and `.dns` files to match the current machine's `RND_ROOT` path on macOS, Windows, or Linux.
    """
    local_root_fwd = str(RND_ROOT).replace("\\", "/").rstrip("/")
    if local_root_fwd.upper() == "E:/RND":
        return

    for folder in (DIR_SAME, DIR_SMAE):
        if not folder.exists():
            continue
        for pd_file in folder.glob("*.pagedesigner"):
            if not zipfile.is_zipfile(pd_file):
                continue
            try:
                with zipfile.ZipFile(pd_file, "r") as zf:
                    if "document.json" not in zf.namelist():
                        continue
                    raw_doc = zf.read("document.json").decode("utf-8")
                    if "E:/RND/" not in raw_doc and "E:\\\\RND\\\\" not in raw_doc and "e:/rnd/" not in raw_doc.lower():
                        continue
                    updated_doc = (
                        raw_doc.replace("E:/RND/", local_root_fwd + "/")
                        .replace("e:/rnd/", local_root_fwd + "/")
                        .replace("E:\\\\RND\\\\", local_root_fwd + "/")
                    )
                    other_items = {
                        info.filename: zf.read(info.filename)
                        for info in zf.infolist()
                        if info.filename != "document.json"
                    }
                with zipfile.ZipFile(pd_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                    if "mimetype" in other_items:
                        zout.writestr("mimetype", other_items["mimetype"], compress_type=zipfile.ZIP_STORED)
                    zout.writestr("document.json", updated_doc.encode("utf-8"))
                    for k, v in other_items.items():
                        if k != "mimetype":
                            zout.writestr(k, v)
                dns_file = pd_file.with_suffix(".dns")
                if dns_file.exists():
                    shutil.copy2(pd_file, dns_file)
            except Exception:
                pass


# ==============================================================================
# DESKTOP FOCUS & PAGE DESIGNER RPC SESSION (macOS + Windows WinSta0\Default)
# ==============================================================================
def _run_python_on_winsta0_default(code_str: str, timeout_ms: int = 3000) -> int:
    """
    Runs a short Python snippet explicitly on the interactive user desktop (`WinSta0\\Default`)
    on Windows. Returns the process exit code (0 = success).
    """
    if sys.platform != "win32":
        return 1
    try:
        kernel32 = ctypes.windll.kernel32

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("lpReserved", wintypes.LPWSTR),
                ("lpDesktop", wintypes.LPWSTR),
                ("lpTitle", wintypes.LPWSTR),
                ("dwX", wintypes.DWORD),
                ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD),
                ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD),
                ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD),
                ("cbReserved2", wintypes.WORD),
                ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
                ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE),
                ("hStdError", wintypes.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("hProcess", wintypes.HANDLE),
                ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD),
                ("dwThreadId", wintypes.DWORD),
            ]

        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(STARTUPINFOW)
        si.lpDesktop = "WinSta0\\Default"
        si.dwFlags = 1
        si.wShowWindow = 0  # SW_HIDE helper console
        pi = PROCESS_INFORMATION()

        cmd_line = f'"{sys.executable}" -c "{code_str}"'
        cmd_buf = ctypes.create_unicode_buffer(cmd_line)
        if kernel32.CreateProcessW(
            None,
            cmd_buf,
            None,
            None,
            False,
            0x08000000,  # CREATE_NO_WINDOW
            None,
            None,
            ctypes.byref(si),
            ctypes.byref(pi),
        ):
            kernel32.WaitForSingleObject(pi.hProcess, timeout_ms)
            exit_code = wintypes.DWORD(1)
            kernel32.GetExitCodeProcess(pi.hProcess, ctypes.byref(exit_code))
            kernel32.CloseHandle(pi.hProcess)
            kernel32.CloseHandle(pi.hThread)
            return int(exit_code.value)
    except Exception:
        pass
    return 1


def _win32_check_and_focus_pagedesigner(focus: bool = True) -> bool:
    """
    Checks on `WinSta0\\Default` whether a visible `Page Designer` window exists,
    and optionally maximizes & brings it to the foreground above all browser windows.
    """
    if sys.platform != "win32":
        return False
    focus_flag = "1" if focus else "0"
    snippet = (
        "import ctypes, sys; u=ctypes.windll.user32; k=ctypes.windll.kernel32; "
        "WNDENUMPROC=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p); "
        "found=[]; "
        "def cb(h,l):\n"
        " if u.IsWindowVisible(h):\n"
        "  b=ctypes.create_unicode_buffer(260); u.GetWindowTextW(h,b,260); t=b.value or ''\n"
        "  if 'Page Designer' in t and 'Studio' not in t and 'Chrome' not in t and 'Edge' not in t:\n"
        "   found.append(h)\n"
        " return True\n"
        "u.EnumWindows(WNDENUMPROC(cb),0)\n"
        "if not found: sys.exit(2)\n"
        f"if {focus_flag}:\n"
        " fg=u.GetForegroundWindow(); fg_tid=u.GetWindowThreadProcessId(fg,None); cur_tid=k.GetCurrentThreadId()\n"
        " if fg_tid and fg_tid!=cur_tid: u.AttachThreadInput(fg_tid,cur_tid,True)\n"
        " for h in found:\n"
        "  if u.IsIconic(h): u.ShowWindow(h,9)\n"
        "  u.ShowWindow(h,3)\n"
        "  u.SetWindowPos(h,-1,0,0,0,0,0x0001|0x0002|0x0040)\n"
        "  u.SetWindowPos(h,-2,0,0,0,0,0x0001|0x0002|0x0040)\n"
        "  u.keybd_event(0x12,0,0,0); u.SetForegroundWindow(h); u.BringWindowToTop(h); u.keybd_event(0x12,0,2,0)\n"
        " if fg_tid and fg_tid!=cur_tid: u.AttachThreadInput(fg_tid,cur_tid,False)\n"
        "sys.exit(0)"
    )
    return _run_python_on_winsta0_default(snippet, timeout_ms=2500) == 0


def _win32_launch_pagedesigner_on_winsta0(pd_exe: Path, port: int) -> bool:
    """
    Spawns `pagedesigner.exe --control <port>` explicitly on `WinSta0\\Default` (maximized)
    so it is always visible on the user's real interactive desktop screen.
    """
    if sys.platform != "win32":
        return False
    try:
        kernel32 = ctypes.windll.kernel32

        class STARTUPINFOW(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("lpReserved", wintypes.LPWSTR),
                ("lpDesktop", wintypes.LPWSTR),
                ("lpTitle", wintypes.LPWSTR),
                ("dwX", wintypes.DWORD),
                ("dwY", wintypes.DWORD),
                ("dwXSize", wintypes.DWORD),
                ("dwYSize", wintypes.DWORD),
                ("dwXCountChars", wintypes.DWORD),
                ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("wShowWindow", wintypes.WORD),
                ("cbReserved2", wintypes.WORD),
                ("lpReserved2", ctypes.POINTER(wintypes.BYTE)),
                ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE),
                ("hStdError", wintypes.HANDLE),
            ]

        class PROCESS_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("hProcess", wintypes.HANDLE),
                ("hThread", wintypes.HANDLE),
                ("dwProcessId", wintypes.DWORD),
                ("dwThreadId", wintypes.DWORD),
            ]

        os.environ["PAGEDESIGNER_CONTROL_PORT"] = str(port)
        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(STARTUPINFOW)
        si.lpDesktop = "WinSta0\\Default"
        si.dwFlags = 1  # STARTF_USESHOWWINDOW
        si.wShowWindow = 3  # SW_MAXIMIZE
        pi = PROCESS_INFORMATION()

        cmd_line = f'"{pd_exe}" --control {port}'
        cmd_buf = ctypes.create_unicode_buffer(cmd_line)
        ok = kernel32.CreateProcessW(
            None,
            cmd_buf,
            None,
            None,
            False,
            0,
            None,
            str(pd_exe.parent),
            ctypes.byref(si),
            ctypes.byref(pi),
        )
        if ok:
            kernel32.CloseHandle(pi.hProcess)
            kernel32.CloseHandle(pi.hThread)
            return True
    except Exception:
        pass
    return False


def bring_pagedesigner_to_front() -> bool:
    if sys.platform == "darwin":
        try:
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to set frontmost of (first process whose name contains "Page Designer" or name contains "pagedesigner") to true',
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2.5,
            )
            return True
        except Exception:
            return False

    if sys.platform != "win32":
        return False

    return _win32_check_and_focus_pagedesigner(focus=True)


def _find_macos_pagedesigner_executable() -> tuple[Path | None, list[int]]:
    """
    Finds the Page Designer binary or .app bundle on macOS (`darwin`) and any running PIDs
    that were started without `--control 47123`.
    """
    running_pids = []
    running_bin = None
    try:
        out = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            parts = line_str.split(None, 1)
            if len(parts) < 2:
                continue
            pid_str, cmd_str = parts[0], parts[1]
            if ("Page Designer.app" in cmd_str or "/pagedesigner" in cmd_str.lower()) and "launch_gujarati" not in cmd_str and "python" not in cmd_str.lower():
                try:
                    running_pids.append(int(pid_str))
                except ValueError:
                    pass
                if ".app/Contents/MacOS/" in cmd_str:
                    idx = cmd_str.find(".app/Contents/MacOS/")
                    after = cmd_str[idx + len(".app/Contents/MacOS/") :].split()[0]
                    cand = Path(cmd_str[: idx + len(".app/Contents/MacOS/")] + after)
                    if cand.exists():
                        running_bin = cand
    except Exception:
        pass

    if running_bin and running_bin.exists():
        return running_bin, running_pids

    candidates = [
        Path("/Applications/Page Designer.app/Contents/MacOS/pagedesigner"),
        Path("/Applications/Page Designer.app/Contents/MacOS/Page Designer"),
        Path("/Applications/Page Designer 1.0.app/Contents/MacOS/pagedesigner"),
        Path("/Applications/Page Designer 1.0.app/Contents/MacOS/Page Designer"),
        Path.home() / "Applications/Page Designer.app/Contents/MacOS/pagedesigner",
        Path.home() / "Applications/Page Designer.app/Contents/MacOS/Page Designer",
        Path.home() / "Desktop/Page Designer.app/Contents/MacOS/pagedesigner",
        Path.home() / "Desktop/Page Designer.app/Contents/MacOS/Page Designer",
        Path.home() / "Desktop/Page Designer 1.0/Page Designer.app/Contents/MacOS/pagedesigner",
        Path.home() / "Desktop/Page Designer 1.0/pagedesigner",
        RND_ROOT / "Page Designer.app/Contents/MacOS/pagedesigner",
        RND_ROOT / "pagedesigner",
        RND_ROOT.parent / "open page layout software/target/release/pagedesigner",
    ]
    for c in candidates:
        if c.exists() and c.is_file():
            return c, running_pids

    # Try Spotlight (`mdfind`) for `ai.storyteller.pagedesigner` or `Page Designer.app`
    for query in (
        "kMDItemCFBundleIdentifier == 'ai.storyteller.pagedesigner'",
        "kMDItemFSName == 'Page Designer.app'",
        "kMDItemFSName == 'Page Designer 1.0.app'",
    ):
        try:
            out = subprocess.check_output(["mdfind", query], text=True, stderr=subprocess.DEVNULL, timeout=3.0)
            for line in out.splitlines():
                app_p = Path(line.strip())
                if app_p.exists():
                    for bin_name in ("pagedesigner", "Page Designer"):
                        b = app_p / "Contents" / "MacOS" / bin_name
                        if b.exists():
                            return b, running_pids
        except Exception:
            pass

    return None, running_pids


def ensure_visible_pagedesigner(bring_to_front: bool = True) -> int:
    for port in PD_PORTS:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=1.0)
            s.close()
            if sys.platform == "win32":
                # Verify that the running Page Designer actually has a visible window on WinSta0\Default!
                if _win32_check_and_focus_pagedesigner(focus=bring_to_front):
                    return port
                # Otherwise, it was spawned on a hidden desktop (MainWindowHandle == 0) — kill & relaunch on WinSta0\Default
                subprocess.run(
                    ["taskkill", "/F", "/IM", "pagedesigner.exe"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(0.5)
                break
            else:
                if bring_to_front:
                    bring_pagedesigner_to_front()
                return port
        except Exception:
            continue

    if sys.platform == "darwin":
        try:
            subprocess.run(
                ["launchctl", "setenv", "PAGEDESIGNER_CONTROL_PORT", str(PD_PORT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass

        mac_bin, running_pids = _find_macos_pagedesigner_executable()
        # If Page Designer was opened without `--control 47123`, restart it with `--control 47123`
        for pid in running_pids:
            try:
                os.kill(pid, 15)
            except Exception:
                pass
        if running_pids:
            time.sleep(0.6)

        env = dict(os.environ, PAGEDESIGNER_CONTROL_PORT=str(PD_PORT))
        if mac_bin and mac_bin.exists():
            subprocess.Popen([str(mac_bin), "--control", str(PD_PORT)], cwd=str(mac_bin.parent), env=env)
        else:
            subprocess.Popen(["open", "-n", "-a", "Page Designer", "--args", "--control", str(PD_PORT)], env=env)

        for _ in range(35):
            time.sleep(0.3)
            try:
                s = socket.create_connection(("127.0.0.1", PD_PORT), timeout=1.0)
                s.close()
                break
            except Exception:
                pass
        if bring_to_front:
            bring_pagedesigner_to_front()
        return PD_PORT

    pd_candidates = [
        RND_ROOT / "open page layout software" / "pagedesigner.exe",
        RND_ROOT / "Gujarat_Samachar" / "Page_Designer_Software" / "pagedesigner.exe",
        Path.home() / "Desktop" / "Page Designer 1.0" / "pagedesigner.exe",
        Path.home() / "Desktop" / "pagedesigner.exe",
        Path(r"E:\RND\open page layout software\pagedesigner.exe"),
        Path(r"E:\RND\Gujarat_Samachar\Page_Designer_Software\pagedesigner.exe"),
    ]
    pd_exe = next((p for p in pd_candidates if p.exists()), None)
    if pd_exe is not None:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/IM", "pagedesigner.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.3)
            launched = _win32_launch_pagedesigner_on_winsta0(pd_exe, PD_PORT)
            if not launched:
                env = dict(os.environ, PAGEDESIGNER_CONTROL_PORT=str(PD_PORT))
                subprocess.Popen([str(pd_exe), "--control", str(PD_PORT)], cwd=str(pd_exe.parent), env=env)
        else:
            env = dict(os.environ, PAGEDESIGNER_CONTROL_PORT=str(PD_PORT))
            subprocess.Popen([str(pd_exe), "--control", str(PD_PORT)], cwd=str(pd_exe.parent), env=env)
        for _ in range(35):
            time.sleep(0.3)
            try:
                s = socket.create_connection(("127.0.0.1", PD_PORT), timeout=1.0)
                s.close()
                break
            except Exception:
                pass
    if bring_to_front:
        bring_pagedesigner_to_front()
    return PD_PORT


def pd_rpc_session():
    port = ensure_visible_pagedesigner(bring_to_front=False)
    sock = socket.create_connection(("127.0.0.1", port), timeout=30.0)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    f_in = sock.makefile("r", encoding="utf-8")
    req_id = [0]

    def call(method: str, params: dict = None):
        req_id[0] += 1
        payload = {"id": req_id[0], "method": method, "params": params or {}}
        sock.sendall((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        line = f_in.readline()
        if not line:
            raise RuntimeError("Page Designer connection closed")
        return json.loads(line)

    return sock, call


# ==============================================================================
# SEGMENT PARSER & ENCODER FOR GUJARATI, HINDI, AND ENGLISH EDITIONS
# ==============================================================================
_DATELINE_RE = re.compile(
    r"^(?:અમદાવાદ|ગાંધીનગર|નવી દિલ્હી|મુંબઈ|રાજકોટ|સુરત|વડોદરા|પોરબંદર|ભાવનગર|જામનગર|જૂનાગઢ|કીવ|પેરિસ|વોશિંગ્ટન|લંડન|મોસ્કો|अहमदाबाद|गांधीनगर|नई दिल्ली|मुंबई|राजकोट|सूरत|वडोदरा|पोरबंदर|भावनगर|जामनगर|जूनागढ़|कीव|पेरिस|वॉशिंगटन|लंदन|मॉस्को|Ahmedabad|Gandhinagar|New Delhi|Mumbai|Rajkot|Surat|Vadodara|Porbandar|Bhavnagar|Jamnagar|Junagadh|Kyiv|Paris|Washington|London|Moscow)[^\n]{0,36}$"
)


def _extract_ui_segments_for_story(raw_text: str, chars: list, frame_category: str) -> list:
    if not chars:
        base_over = {"fontFamily": "Gopika", "fontStyle": "Regular", "size": 11.5, "leading": {"kind": "points", "value": 13.0}}
    else:
        gopika_runs = [c.get("over", {}) for c in chars if c.get("over", {}).get("fontFamily") == "Gopika"]
        base_over = dict(gopika_runs[0] if gopika_runs else chars[0].get("over", {}))
        base_over["fontFamily"] = base_over.get("fontFamily", "Gopika")

    sz = round(float(base_over.get("size", 11.5) or 11.5), 1)
    ld_obj = base_over.get("leading", {})
    ld = round(float(ld_obj.get("value", sz * 1.15) if isinstance(ld_obj, dict) else (ld_obj or sz * 1.15)), 1)
    ff = base_over.get("fontFamily", "Gopika")
    fs = base_over.get("fontStyle", "Regular")
    style_name = chars[0].get("style", "[None]") if chars else "[None]"

    if "\n" in raw_text and frame_category in ("intro", "body"):
        first_line, rest_text = raw_text.split("\n", 1)
        fl_clean = first_line.strip()
        if (
            len(fl_clean) <= 56
            and rest_text.strip()
            and (
                _DATELINE_RE.match(fl_clean)
                or "તા." in fl_clean
                or "ता." in fl_clean
                or "સોમવાર" in fl_clean
                or "सोमवार" in fl_clean
                or "Monday" in fl_clean
                or "Oct " in fl_clean
                or "સંવાદદાતા" in fl_clean
                or "प्रतिनिधि" in fl_clean
                or "Correspondent" in fl_clean
            )
        ):
            return [
                {
                    "seg_index": 0,
                    "role": "byline",
                    "label": "BYLINE / DATELINE",
                    "text": first_line,
                    "has_trailing_nl": True,
                    "font_family": ff,
                    "font_style": "Bold",
                    "size": sz,
                    "leading": ld,
                    "over": dict(base_over, fontStyle="Bold"),
                    "style": style_name,
                },
                {
                    "seg_index": 1,
                    "role": frame_category,
                    "label": "INTRO" if frame_category == "intro" else "BODY COPY",
                    "text": rest_text,
                    "has_trailing_nl": False,
                    "font_family": ff,
                    "font_style": fs,
                    "size": sz,
                    "leading": ld,
                    "over": dict(base_over),
                    "style": style_name,
                },
            ]

    role_labels = {
        "masthead": "RUNNING HEADER / FOLIO",
        "headline": f"HEADLINE ({sz:.0f}pt)",
        "subhead": f"SUBHEAD ({sz:.1f}pt)",
        "byline": f"BYLINE ({sz:.1f}pt)",
        "intro": f"INTRO ({sz:.1f}pt)",
        "caption": f"PHOTO CAPTION ({sz:.1f}pt)",
        "body": f"BODY COPY ({sz:.1f}pt)",
    }

    return [
        {
            "seg_index": 0,
            "role": frame_category,
            "label": role_labels.get(frame_category, "TEXT"),
            "text": raw_text,
            "has_trailing_nl": False,
            "font_family": ff,
            "font_style": fs,
            "size": sz,
            "leading": ld,
            "over": dict(base_over),
            "style": style_name,
        }
    ]


def _build_runs_for_story(text: str, base_over: dict, style_name: str = "[None]") -> list:
    if not text:
        return []
    ff = base_over.get("fontFamily", "Gopika")
    if ff != "Gopika":
        return [{"len": len(text.encode("utf-8")), "style": style_name, "over": dict(base_over)}]

    base_sz = float(base_over.get("size", 11.5) or 11.5)
    eng_sz = round(base_sz * 0.76, 1)
    runs = []
    last_idx = 0
    for m in re.finditer(r"[A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*", text):
        if m.start() > last_idx:
            guj_chunk = text[last_idx : m.start()]
            runs.append({
                "len": len(guj_chunk.encode("utf-8")),
                "style": style_name,
                "over": dict(base_over),
            })
        eng_chunk = m.group(0)
        eng_over = dict(base_over)
        eng_over["fontFamily"] = "Arial"
        eng_over["size"] = eng_sz
        runs.append({
            "len": len(eng_chunk.encode("utf-8")),
            "style": style_name,
            "over": eng_over,
        })
        last_idx = m.end()

    if last_idx < len(text):
        rem_chunk = text[last_idx:]
        runs.append({
            "len": len(rem_chunk.encode("utf-8")),
            "style": style_name,
            "over": dict(base_over),
        })
    return runs


def _encode_ui_segments_to_story(st: dict, updated_segments: list, frame_content: dict = None):
    new_chars = []
    full_parts = []

    for idx, seg in enumerate(updated_segments):
        txt = str(seg.get("text", ""))
        if seg.get("has_trailing_nl") and not txt.endswith("\n"):
            txt = txt + "\n"
        full_parts.append(txt)

        base_over = dict(seg.get("over", {}))
        if "size" in seg and seg["size"]:
            base_over["size"] = float(seg["size"])
        if "leading" in seg and seg["leading"]:
            base_over["leading"] = {"kind": "points", "value": float(seg["leading"])}

        style_name = seg.get("style", "[None]")
        seg_runs = _build_runs_for_story(txt, base_over, style_name)
        new_chars.extend(seg_runs)

    full_text = "".join(full_parts)
    old_text = st.get("text", "")
    st["text"] = full_text
    st["chars"] = new_chars

    para_lines = full_text.split("\n")
    existing_paras = st.get("paras", [])
    if existing_paras:
        if len(para_lines) > len(existing_paras):
            last_p = existing_paras[-1]
            for _ in range(len(para_lines) - len(existing_paras)):
                existing_paras.append(json.loads(json.dumps(last_p)))
        elif len(para_lines) < len(existing_paras) and len(para_lines) >= 1:
            st["paras"] = existing_paras[: len(para_lines)]

    if frame_content is not None and updated_segments:
        frame_content["text"] = full_text
        first_sz = float(updated_segments[0].get("size", frame_content.get("fontSizePt", 11.5)))
        first_ld = float(updated_segments[0].get("leading", frame_content.get("lineHeight", 13.0)))
        frame_content["fontSizePt"] = first_sz
        frame_content["lineHeight"] = first_ld
        for ps in frame_content.get("paragraphStyles", []):
            ps["fontSizePt"] = ps["fontSize"] = ps["size"] = first_sz
            ps["lineHeight"] = ps["leading"] = first_ld
        new_cstyles = []
        b_cursor = 0
        for r in new_chars:
            blen = r["len"]
            ov = r["over"]
            rsz = float(ov.get("size", first_sz))
            rld_obj = ov.get("leading", {})
            rld = float(rld_obj.get("value", first_ld) if isinstance(rld_obj, dict) else (rld_obj or first_ld))
            new_cstyles.append({
                "start": b_cursor,
                "end": b_cursor + blen,
                "len": blen,
                "style": "[None]",
                "fontFamily": ov.get("fontFamily", "Gopika"),
                "fontStyle": ov.get("fontStyle", "Regular"),
                "fontSizePt": rsz,
                "fontSize": rsz,
                "size": rsz,
                "lineHeight": rld,
                "leading": rld,
                "bold": ov.get("fontStyle") == "Bold",
                "italic": False,
                "hScale": round(float(ov.get("hScale", 1.0)) * 100.0, 1),
                "vScale": 100.0,
                "horizontalScale": float(ov.get("hScale", 1.0)),
                "verticalScale": 1.0,
            })
            b_cursor += blen
        frame_content["charStyles"] = new_cstyles

    return old_text, full_text


# ==============================================================================
# EXTRACT ALL 10 PAGES STATE FOR ANY EDITION (`gujarati`, `hindi`, `english`)
# ==============================================================================
def extract_all_pages_state(edition: str = "gujarati") -> dict:
    ed_key = normalize_edition(edition)
    cfg = EDITION_CONFIG[ed_key]
    meta_map = PAGE_META_BY_EDITION[ed_key]
    ts = int(time.time() * 1000)
    pages_out = []

    for pnum in range(1, 11):
        pd_stem = cfg["page_file_pattern"].format(pnum=pnum)
        pd_path = DIR_SAME / f"{pd_stem}.pagedesigner"
        if not pd_path.exists():
            pd_path = DIR_SMAE / f"{pd_stem}.pagedesigner"
        if not pd_path.exists():
            continue

        with zipfile.ZipFile(pd_path, "r") as zf:
            doc = json.loads(zf.read("document.json").decode("utf-8"))

        stories = doc.get("stories", {})
        assets = doc.get("assets", {})
        sp = doc["spreads"][0]
        meta = meta_map.get(pnum, {
            "badge": f"PAGE {pnum:02d}",
            "section": f"PAGE {pnum:02d}",
            "title": f"Page {pnum:02d}",
            "subtitle": cfg["masthead_title"],
        })

        photo_entries = []
        raw_items = sp.get("items", [])

        # Pass 1: Collect all Graphic Photo frames
        for order_idx, it in enumerate(raw_items):
            ct = it.get("content", {})
            if ct.get("type") != "graphic":
                continue
            xf = it.get("xf", [1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
            sub = it.get("path", {}).get("subpaths", [])
            anchors = sub[0].get("anchors", []) if sub else []
            xs = [a["p"][0] + xf[4] for a in anchors] if anchors else [xf[4]]
            ys = [a["p"][1] + xf[5] for a in anchors] if anchors else [xf[5]]
            x0, x1 = round(min(xs), 1), round(max(xs), 1)
            y0, y1 = round(min(ys), 1), round(max(ys), 1)
            w_pt, h_pt = round(x1 - x0, 1), round(y1 - y0, 1)

            aid = str(ct.get("asset", ""))
            ainfo = assets.get(aid, {})
            name = Path(ainfo.get("name", f"p{pnum:02d}_asset_{aid}.png")).name
            px = ainfo.get("pixels", [800, 600])
            lname = name.lower()
            is_logo = (
                "logo" in lname
                or "masthead" in lname
                or "cmyk" in lname
                or "header_bar" in lname
                or (pnum > 1 and y0 < 72)
            )
            if (PHOTOS_DIR / name).exists():
                photo_url = f"/photos/{urllib.parse.quote(name)}?t={ts}"
            elif (PHOTOS_DIR / f"p{pnum:02d}_asset_{aid}.png").exists():
                photo_url = f"/photos/p{pnum:02d}_asset_{aid}.png?t={ts}"
            else:
                photo_url = f"/photos/{urllib.parse.quote(name)}?t={ts}"

            photo_entries.append({
                "order_idx": order_idx,
                "sort_y": round(y0 / 12.0) * 12.0,
                "sort_x": x0,
                "item_id": it["id"],
                "asset_id": aid,
                "name": name,
                "is_logo": is_logo,
                "bbox": [x0, y0, x1, y1],
                "size_pt": [w_pt, h_pt],
                "pixels": px,
                "photo_url": photo_url,
            })

        # Pass 2: Collect and classify all Text frames
        text_entries = []
        for order_idx, it in enumerate(raw_items):
            ct = it.get("content", {})
            if ct.get("type") != "text":
                continue
            sid = str(ct.get("story", ""))
            st = stories.get(sid, {})
            raw_txt = st.get("text", "")
            if not raw_txt or not raw_txt.strip():
                continue

            xf = it.get("xf", [1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
            sub = it.get("path", {}).get("subpaths", [])
            anchors = sub[0].get("anchors", []) if sub else []
            xs = [a["p"][0] + xf[4] for a in anchors] if anchors else [xf[4]]
            ys = [a["p"][1] + xf[5] for a in anchors] if anchors else [xf[5]]
            x0, x1 = round(min(xs), 1), round(max(xs), 1)
            y0, y1 = round(min(ys), 1), round(max(ys), 1)
            w_pt, h_pt = round(x1 - x0, 1), round(y1 - y0, 1)

            chars = st.get("chars", [])
            gopika_runs = [c.get("over", {}) for c in chars if c.get("over", {}).get("fontFamily") == "Gopika"]
            base_over = gopika_runs[0] if gopika_runs else (chars[0].get("over", {}) if chars else {})
            sz = round(float(base_over.get("size", 11.5) or 11.5), 1)
            fs = base_over.get("fontStyle", "Regular")
            clean_txt = raw_txt.strip()

            near_photo = False
            for ph in photo_entries:
                if ph["is_logo"]:
                    continue
                px0, py0, px1, py1 = ph["bbox"]
                hoverlap = min(x1, px1) - max(x0, px0)
                if hoverlap >= 20 and (
                    (y0 >= py1 - 12 and y0 <= py1 + 36)
                    or (abs(y0 - py0) <= 24 and abs(x0 - px1) <= 30)
                ) and sz < 16.0 and len(clean_txt) < 420:
                    near_photo = True
                    break

            if pnum > 1 and y0 < 73.5:
                category = "masthead"
                role_badge = f"RUNNING HEADER ({sz:.1f}pt)"
            elif sz >= 19.5:
                category = "headline"
                role_badge = f"HEADLINE ({sz:.0f}pt)"
            elif sz >= 13.0 and fs == "Bold":
                category = "subhead"
                role_badge = f"SUBHEAD ({sz:.1f}pt)"
            elif len(clean_txt) <= 56 and (
                _DATELINE_RE.match(clean_txt)
                or "તા." in clean_txt
                or "ता." in clean_txt
                or "સોમવાર" in clean_txt
                or "सोमवार" in clean_txt
                or "Monday" in clean_txt
                or "Oct " in clean_txt
                or "સંવાદદાતા" in clean_txt
                or "प्रतिनिधि" in clean_txt
                or "Correspondent" in clean_txt
                or (fs == "Bold" and sz <= 11.2 and "\n" not in clean_txt)
            ):
                category = "byline"
                role_badge = f"BYLINE ({sz:.1f}pt)"
            elif near_photo:
                category = "caption"
                role_badge = f"PHOTO CAPTION ({sz:.1f}pt)"
            elif fs == "Bold" and len(clean_txt) <= 380:
                category = "intro"
                role_badge = f"INTRO ({sz:.1f}pt)"
            else:
                category = "body"
                role_badge = f"BODY COPY ({sz:.1f}pt)"

            segs = _extract_ui_segments_for_story(raw_txt, chars, category)
            preview_title = clean_txt.replace("\n", " ")[:72]

            text_entries.append({
                "order_idx": order_idx,
                "sort_y": round(y0 / 12.0) * 12.0,
                "sort_x": x0,
                "item_id": it["id"],
                "story_id": sid,
                "category": category,
                "role_badge": role_badge,
                "preview_title": preview_title,
                "bbox": [x0, y0, x1, y1],
                "size_pt": [w_pt, h_pt],
                "max_font_size": sz,
                "columns": ct.get("options", {}).get("columns", 1),
                "segments": segs,
            })

        saved_png_name = cfg["saved_png_pattern"].format(pnum=pnum)
        thumb_name = cfg["thumb_pattern"].format(pnum=pnum)
        pages_out.append({
            "page_number": pnum,
            "edition": ed_key,
            "id": f"{ed_key}_page_{pnum:02d}",
            **meta,
            "png_url": f"/saved_pages/{saved_png_name}?t={ts}",
            "thumb_url": f"/thumbnails/{thumb_name}?t={ts}",
            "text_count": len(text_entries),
            "photo_count": len(photo_entries),
            "texts": text_entries,
            "photos": photo_entries,
        })

    exts = {".jpg", ".jpeg", ".png", ".webp"}
    library_photos = [
        p.name
        for p in sorted(PHOTOS_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("p0") and not p.name.startswith("p1")
    ]
    if not library_photos:
        library_photos = [p.name for p in sorted(PHOTOS_DIR.iterdir()) if p.is_file() and p.suffix.lower() in exts]

    return {
        "ok": True,
        "edition": ed_key,
        "edition_label": cfg["menu_label"],
        "masthead_title": cfg["masthead_title"],
        "editions": [
            {"key": k, "menu_label": v["menu_label"], "masthead_title": v["masthead_title"]}
            for k, v in EDITION_CONFIG.items()
        ],
        "pages": pages_out,
        "library_photos": library_photos,
    }


def extract_compare_overview() -> dict:
    """
    Fast overview payload for the 3-Column Comparison UI:
      - Left Column:   `hindi`    (आस-पास — 10 Pages)
      - Center Column: `gujarati` (ગુજરાત સમાચાર — 10 Pages, Original Master in Center)
      - Right Column:  `english`  (INDIAN POST — 10 Pages)
    """
    ts = int(time.time() * 1000)
    by_edition = {}
    for ed_key in ("hindi", "gujarati", "english"):
        cfg = EDITION_CONFIG[ed_key]
        meta_map = PAGE_META_BY_EDITION[ed_key]
        ed_pages = []
        for pnum in range(1, 11):
            meta = meta_map.get(pnum, {
                "badge": f"PAGE {pnum:02d}",
                "section": f"PAGE {pnum:02d}",
                "title": f"Page {pnum:02d}",
                "subtitle": cfg["masthead_title"],
            })
            saved_png_name = cfg["saved_png_pattern"].format(pnum=pnum)
            thumb_name = cfg["thumb_pattern"].format(pnum=pnum)
            ed_pages.append({
                "page_number": pnum,
                "edition": ed_key,
                "badge": meta["badge"],
                "section": meta["section"],
                "title": meta["title"],
                "subtitle": meta["subtitle"],
                "png_url": f"/saved_pages/{saved_png_name}?t={ts}",
                "thumb_url": f"/thumbnails/{thumb_name}?t={ts}",
            })
        by_edition[ed_key] = {
            "key": ed_key,
            "menu_label": cfg["menu_label"],
            "masthead_title": cfg["masthead_title"],
            "pages": ed_pages,
        }
    return {
        "ok": True,
        "column_order": ["hindi", "gujarati", "english"],
        "editions": by_edition,
    }


# ==============================================================================
# LIVE STEP-BY-STEP RE-DRAW IN PAGE DESIGNER 1.0 (ON PAGE CLICK OR BUTTON)
# ==============================================================================
_LIVE_BUILD_LOCK = threading.Lock()
_CANCEL_CURRENT_ANIM = threading.Event()


def _collect_sorted_leaf_item_ids_and_first_headline(spread_items: list):
    leaves = []
    headline_candidates = []

    def walk(items, tx=0.0, ty=0.0):
        for it in items:
            ct = it.get("content", {})
            t = ct.get("type")
            xf = it.get("xf", [1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
            cx = tx + xf[4]
            cy = ty + xf[5]
            if t == "group":
                walk(ct.get("items", []), cx, cy)
            else:
                sub = it.get("path", {}).get("subpaths", [])
                anchors = sub[0].get("anchors", []) if sub else []
                xs = [a["p"][0] + cx for a in anchors] if anchors else [cx]
                ys = [a["p"][1] + cy for a in anchors] if anchors else [cy]
                y0 = min(ys)
                x0 = min(xs)
                type_order = 0 if t not in ("text", "graphic") else (1 if t == "graphic" else 2)
                leaves.append((round(y0 / 16.0) * 16.0, type_order, x0, it["id"]))
                if t == "text" and y0 > 75.0:
                    f_sz = float(ct.get("fontSizePt", 11.5) or 11.5)
                    if f_sz >= 20.0:
                        headline_candidates.append((y0, x0, it["id"]))

    walk(spread_items)
    leaves.sort()
    headline_candidates.sort()
    first_head_id = headline_candidates[0][2] if headline_candidates else (leaves[0][3] if leaves else None)
    return [item_id for _, _, _, item_id in leaves], first_head_id


def _rebuild_combined_for_edition(ed_key: str) -> Path:
    cfg = EDITION_CONFIG[ed_key]
    mod = __import__(cfg["combiner_module"])
    fn = getattr(mod, cfg["combiner_func"])
    return fn()


def run_live_step_by_step_build_in_pagedesigner(
    page_numbers: list[int],
    step_delay: float = 0.035,
    mode: str = "redraw",
    edition: str = "gujarati",
):
    ed_key = normalize_edition(edition)
    cfg = EDITION_CONFIG[ed_key]
    _CANCEL_CURRENT_ANIM.set()

    def _worker():
        with _LIVE_BUILD_LOCK:
            _CANCEL_CURRENT_ANIM.clear()
            try:
                ensure_visible_pagedesigner(bring_to_front=True)

                if mode == "script" and len(page_numbers) == 1:
                    pnum = page_numbers[0]
                    script_path = RND_ROOT / cfg["script_pattern"].format(pnum=pnum)
                    if script_path.exists():
                        subprocess.run([sys.executable, str(script_path)], cwd=str(RND_ROOT))
                        _rebuild_combined_for_edition(ed_key)
                        sync_initial_previews_and_photos()
                        return

                combined_pd = DIR_SAME / f"{cfg['combined_name']}.pagedesigner"
                if not combined_pd.exists():
                    combined_pd = _rebuild_combined_for_edition(ed_key)

                with zipfile.ZipFile(combined_pd, "r") as zf:
                    doc = json.loads(zf.read("document.json").decode("utf-8"))

                sock, call = pd_rpc_session()
                try:
                    call("ui.focus", {})
                except Exception:
                    pass

                ui_info = call("ui.inspect", {}).get("result", {})
                active_docs = ui_info.get("documents", [])
                active_idx = ui_info.get("activeDocument", -1)
                expected_title = f"{cfg['combined_name']}.pagedesigner"
                need_open = True
                if isinstance(active_idx, int) and 0 <= active_idx < len(active_docs):
                    cur_title = str(active_docs[active_idx].get("title", "") or Path(str(active_docs[active_idx].get("path", ""))).name)
                    if cur_title == expected_title or Path(cur_title).stem == cfg["combined_name"]:
                        need_open = False

                if need_open:
                    for _ in range(len(active_docs)):
                        try:
                            call("app.close", {"discard": True})
                        except Exception:
                            break
                    call("engine.execute", {"command": "file.open", "params": {"path": str(combined_pd)}})

                ui_state = call("ui.inspect", {}).get("result", {}).get("ui", {})
                call("engine.execute", {"command": "view.screenMode", "params": {"mode": "normal"}})
                if not ui_state.get("frameEdges", False):
                    call("engine.execute", {"command": "view.frameEdges", "params": {}})
                if not ui_state.get("guides", False):
                    call("engine.execute", {"command": "view.guides", "params": {}})

                bring_pagedesigner_to_front()
                time.sleep(0.08)

                for pnum in page_numbers:
                    if _CANCEL_CURRENT_ANIM.is_set():
                        break
                    if pnum < 1 or pnum > len(doc.get("spreads", [])):
                        continue
                    sp = doc["spreads"][pnum - 1]
                    leaf_ids, first_head_id = _collect_sorted_leaf_item_ids_and_first_headline(sp.get("items", []))
                    if not leaf_ids:
                        continue

                    # Hide all items FIRST so the page opens 100% blank white from the very start!
                    call("engine.execute", {"command": "object.setFlags", "params": {"ids": leaf_ids, "hidden": True}})
                    call("engine.execute", {"command": "view.goToPage", "params": {"page": pnum}})
                    call("engine.execute", {"command": "view.fitPage", "params": {}})
                    call("engine.execute", {"command": "edit.deselectAll", "params": {}})
                    bring_pagedesigner_to_front()
                    time.sleep(0.32)

                    chunk_sz = 2 if len(leaf_ids) > 95 else 1
                    for i in range(0, len(leaf_ids), chunk_sz):
                        if _CANCEL_CURRENT_ANIM.is_set():
                            call("engine.execute", {"command": "object.setFlags", "params": {"ids": leaf_ids[i:], "hidden": False}})
                            break
                        batch_ids = leaf_ids[i : i + chunk_sz]
                        call("engine.execute", {"command": "object.setFlags", "params": {"ids": batch_ids, "hidden": False}})
                        try:
                            call("engine.execute", {"command": "object.select", "params": {"ids": [batch_ids[-1]]}})
                        except Exception:
                            pass
                        time.sleep(step_delay)

                    if first_head_id and not _CANCEL_CURRENT_ANIM.is_set():
                        try:
                            call("engine.execute", {"command": "object.select", "params": {"ids": [first_head_id]}})
                        except Exception:
                            pass
                    time.sleep(0.18)

                sock.close()
            except Exception as exc:
                print(f"[LiveBuild Error] {exc}")

    threading.Thread(target=_worker, daemon=True).start()


def run_live_trio_for_page(page_num: int, step_delay: float = 0.020):
    """
    Sequentially opens and draws Hindi (Left) -> Gujarati (Center) -> English (Right)
    for `page_num` inside Page Designer 1.0 so the user can watch all 3 editions draw live!
    """
    _CANCEL_CURRENT_ANIM.set()

    def _trio_worker():
        with _LIVE_BUILD_LOCK:
            _CANCEL_CURRENT_ANIM.clear()
            try:
                ensure_visible_pagedesigner(bring_to_front=True)
                sock, call = pd_rpc_session()
                try:
                    call("ui.focus", {})
                except Exception:
                    pass

                for ed_key in ("hindi", "gujarati", "english"):
                    if _CANCEL_CURRENT_ANIM.is_set():
                        break
                    cfg = EDITION_CONFIG[ed_key]
                    combined_pd = DIR_SAME / f"{cfg['combined_name']}.pagedesigner"
                    if not combined_pd.exists():
                        combined_pd = _rebuild_combined_for_edition(ed_key)
                    with zipfile.ZipFile(combined_pd, "r") as zf:
                        doc = json.loads(zf.read("document.json").decode("utf-8"))

                    ui_info = call("ui.inspect", {}).get("result", {})
                    for _ in range(len(ui_info.get("documents", []))):
                        try:
                            call("app.close", {"discard": True})
                        except Exception:
                            break
                    call("engine.execute", {"command": "file.open", "params": {"path": str(combined_pd)}})
                    ui_state = call("ui.inspect", {}).get("result", {}).get("ui", {})
                    call("engine.execute", {"command": "view.screenMode", "params": {"mode": "normal"}})
                    if not ui_state.get("frameEdges", False):
                        call("engine.execute", {"command": "view.frameEdges", "params": {}})
                    if not ui_state.get("guides", False):
                        call("engine.execute", {"command": "view.guides", "params": {}})

                    bring_pagedesigner_to_front()
                    if 1 <= page_num <= len(doc.get("spreads", [])):
                        sp = doc["spreads"][page_num - 1]
                        leaf_ids, first_head_id = _collect_sorted_leaf_item_ids_and_first_headline(sp.get("items", []))
                        if leaf_ids:
                            call("engine.execute", {"command": "object.setFlags", "params": {"ids": leaf_ids, "hidden": True}})
                            call("engine.execute", {"command": "view.goToPage", "params": {"page": page_num}})
                            call("engine.execute", {"command": "view.fitPage", "params": {}})
                            call("engine.execute", {"command": "edit.deselectAll", "params": {}})
                            bring_pagedesigner_to_front()
                            time.sleep(0.28)
                            chunk_sz = 3 if len(leaf_ids) > 100 else 2
                            for i in range(0, len(leaf_ids), chunk_sz):
                                if _CANCEL_CURRENT_ANIM.is_set():
                                    call("engine.execute", {"command": "object.setFlags", "params": {"ids": leaf_ids[i:], "hidden": False}})
                                    break
                                batch_ids = leaf_ids[i : i + chunk_sz]
                                call("engine.execute", {"command": "object.setFlags", "params": {"ids": batch_ids, "hidden": False}})
                                try:
                                    call("engine.execute", {"command": "object.select", "params": {"ids": [batch_ids[-1]]}})
                                except Exception:
                                    pass
                                time.sleep(step_delay)
                            if first_head_id and not _CANCEL_CURRENT_ANIM.is_set():
                                try:
                                    call("engine.execute", {"command": "object.select", "params": {"ids": [first_head_id]}})
                                except Exception:
                                    pass
                            time.sleep(0.45)
                sock.close()
            except Exception as exc:
                print(f"[LiveTrio Error] {exc}")

    threading.Thread(target=_trio_worker, daemon=True).start()


# ==============================================================================
# SAVE EDITS FOR ANY EDITION (`gujarati`, `hindi`, `english`)
# ==============================================================================
def handle_save_page_edits(payload: dict) -> dict:
    t0 = time.perf_counter()
    ed_key = normalize_edition(payload.get("edition", "gujarati"))
    cfg = EDITION_CONFIG[ed_key]
    page_number = int(payload.get("page_number", 1))
    story_updates = payload.get("story_updates", {})
    photo_updates = payload.get("photo_updates", {})
    trigger_live_build = bool(payload.get("trigger_live_build", payload.get("live_build_after", True)))
    step_ms = float(payload.get("step_ms", 35.0)) / 1000.0

    pd_stem = cfg["page_file_pattern"].format(pnum=page_number)
    pd_same = DIR_SAME / f"{pd_stem}.pagedesigner"
    dns_same = DIR_SAME / f"{pd_stem}.dns"
    pd_smae = DIR_SMAE / f"{pd_stem}.pagedesigner"
    dns_smae = DIR_SMAE / f"{pd_stem}.dns"

    with zipfile.ZipFile(pd_same, "r") as zf:
        doc = json.loads(zf.read("document.json").decode("utf-8"))
        other_files = {
            info.filename: zf.read(info.filename)
            for info in zf.infolist()
            if info.filename != "document.json"
        }

    stories = doc.get("stories", {})
    assets = doc.get("assets", {})

    story_frames = {}
    for sp in doc.get("spreads", []):
        for it in sp.get("items", []):
            ct = it.get("content", {})
            if ct.get("type") == "text":
                story_frames[str(ct.get("story", ""))] = ct

    replaced_stories = 0
    text_replacements = []
    for sid, seg_list in story_updates.items():
        sid_str = str(sid)
        if sid_str in stories and isinstance(seg_list, list):
            old_txt, new_txt = _encode_ui_segments_to_story(
                stories[sid_str], seg_list, story_frames.get(sid_str)
            )
            if old_txt != new_txt:
                text_replacements.append((old_txt, new_txt))
            replaced_stories += 1

    replaced_photos = 0
    for aid, chosen_filename in photo_updates.items():
        aid_str = str(aid)
        if aid_str in assets and chosen_filename:
            src_img_path = PHOTOS_DIR / Path(chosen_filename).name
            if src_img_path.exists():
                px = assets[aid_str].get("pixels", [1200, 800])
                target_w, target_h = max(int(px[0]), 64), max(int(px[1]), 64)
                with Image.open(src_img_path) as im:
                    im_fit = ImageOps.fit(
                        im.convert("RGB"),
                        (target_w, target_h),
                        method=Image.Resampling.LANCZOS,
                        centering=(0.5, 0.35),
                    )
                    buf = io.BytesIO()
                    if ed_key == "english":
                        im_fit.save(buf, format="WEBP", quality=92)
                        img_bytes = buf.getvalue()
                        new_ext = ".webp"
                        new_mime = "image/webp"
                    else:
                        im_fit.save(buf, format="PNG", optimize=True)
                        img_bytes = buf.getvalue()
                        new_ext = ".png"
                        new_mime = "image/png"

                for old_ext in (".webp", ".png", ".jpg", ".jpeg", ".tif"):
                    other_files.pop(f"assets/{aid_str}{old_ext}", None)
                other_files[f"assets/{aid_str}{new_ext}"] = img_bytes
                assets[aid_str]["mime"] = new_mime
                assets[aid_str]["name"] = src_img_path.name
                assets[aid_str]["link"] = str(src_img_path)
                (PHOTOS_DIR / f"p{page_number:02d}_asset_{aid_str}{new_ext}").write_bytes(img_bytes)
                replaced_photos += 1

    doc_bytes = json.dumps(doc, ensure_ascii=False).encode("utf-8")
    for dst_pd, dst_dns in ((pd_same, dns_same), (pd_smae, dns_smae)):
        with zipfile.ZipFile(dst_pd, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            if "mimetype" in other_files:
                zout.writestr("mimetype", other_files["mimetype"], compress_type=zipfile.ZIP_STORED)
            zout.writestr("document.json", doc_bytes)
            for k, v in other_files.items():
                if k != "mimetype":
                    zout.writestr(k, v)
        shutil.copy2(dst_pd, dst_dns)

    script_path = RND_ROOT / cfg["script_pattern"].format(pnum=page_number)
    if script_path.exists() and text_replacements:
        try:
            src_py = script_path.read_text(encoding="utf-8")
            for old_t, new_t in text_replacements:
                if old_t and old_t in src_py:
                    src_py = src_py.replace(old_t, new_t, 1)
            script_path.write_text(src_py, encoding="utf-8")
        except Exception:
            pass

    combined_pd = _rebuild_combined_for_edition(ed_key)

    sock, call = pd_rpc_session()
    call("engine.execute", {"command": "file.open", "params": {"path": str(pd_same)}})
    saved_png_name = cfg["saved_png_pattern"].format(pnum=page_number)
    thumb_name = cfg["thumb_pattern"].format(pnum=page_number)
    ren_name = cfg["rendered_pattern"].format(pnum=page_number)
    png_path = SAVED_PAGES_DIR / saved_png_name
    call("app.export", {"path": str(png_path)})
    if png_path.exists():
        shutil.copy2(png_path, DIR_SAME / ren_name)
        shutil.copy2(png_path, DIR_SMAE / ren_name)
        with Image.open(png_path) as im:
            im_rgb = im.convert("RGB")
            tw = 760
            th = int(round(im_rgb.height * (tw / float(im_rgb.width))))
            im_rgb.resize((tw, th), Image.Resampling.LANCZOS).save(
                THUMBS_DIR / thumb_name, quality=88
            )

    call("engine.execute", {"command": "file.open", "params": {"path": str(combined_pd)}})
    call("engine.execute", {"command": "view.screenMode", "params": {"mode": "normal"}})
    call("engine.execute", {"command": "view.goToPage", "params": {"page": page_number}})
    call("engine.execute", {"command": "view.fitPage", "params": {}})
    sock.close()

    if trigger_live_build:
        run_live_step_by_step_build_in_pagedesigner(
            [page_number], step_delay=max(0.015, min(step_ms, 0.25)), edition=ed_key
        )

    ts = int(time.time() * 1000)
    return {
        "ok": True,
        "edition": ed_key,
        "page_number": page_number,
        "replaced_stories": replaced_stories,
        "replaced_photos": replaced_photos,
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "png_url": f"/saved_pages/{saved_png_name}?t={ts}",
        "thumb_url": f"/thumbnails/{thumb_name}?t={ts}",
    }


def handle_upload_photo(payload: dict) -> dict:
    raw_name = payload.get("filename", "uploaded_photo.png")
    data_uri = payload.get("data_uri", "")
    if not data_uri or "," not in data_uri:
        raise ValueError("Invalid image data_uri")

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(raw_name).name)
    if not safe_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        safe_name += ".png"

    b64_part = data_uri.split(",", 1)[1]
    raw_bytes = base64.b64decode(b64_part)

    dst_path = PHOTOS_DIR / safe_name
    dst_path.write_bytes(raw_bytes)
    return {"ok": True, "filename": safe_name}


# ==============================================================================
# HTTP SERVER HANDLER
# ==============================================================================
class GujaratiStudioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.path = "/Gujarati_Page_Designer_App.html"
            return super().do_GET()

        if parsed.path == "/api/compare-overview":
            try:
                self._send_json(200, extract_compare_overview())
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc)})
            return

        if parsed.path in ("/api/state", "/api/pages"):
            qs = urllib.parse.parse_qs(parsed.query)
            edition = qs.get("edition", ["gujarati"])[0]
            try:
                self._send_json(200, extract_all_pages_state(edition=edition))
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc)})
            return

        if parsed.path == "/api/live-build-page-trio":
            qs = urllib.parse.parse_qs(parsed.query)
            page_num = int(qs.get("page", ["1"])[0])
            speed_raw = qs.get("speed", qs.get("step_ms", ["22"]))[0]
            speed_ms = float(speed_raw) / 1000.0
            run_live_trio_for_page(page_num=page_num, step_delay=max(0.012, min(speed_ms, 0.25)))
            self._send_json(200, {"ok": True, "page": page_num, "order": ["hindi", "gujarati", "english"]})
            return

        if parsed.path == "/api/live-build-all-editions":
            threading.Thread(
                target=lambda: subprocess.run(
                    [sys.executable, str(RND_ROOT / "run_all_3_editions_live_in_pagedesigner.py")],
                    cwd=str(RND_ROOT),
                ),
                daemon=True,
            ).start()
            self._send_json(200, {"ok": True, "editions": ["gujarati", "hindi", "english"], "total_pages": 30})
            return

        if parsed.path == "/api/live-build":
            qs = urllib.parse.parse_qs(parsed.query)
            edition = qs.get("edition", ["gujarati"])[0]
            page_str = qs.get("page", ["1"])[0]
            all_flag = qs.get("all", ["0"])[0]
            mode = qs.get("mode", ["redraw"])[0]
            speed_raw = qs.get("speed", qs.get("step_ms", ["35"]))[0]
            speed_ms = float(speed_raw) / 1000.0
            if page_str == "all" or all_flag == "1":
                pages = list(range(1, 11))
            else:
                pages = [int(page_str)]
            run_live_step_by_step_build_in_pagedesigner(
                pages, step_delay=max(0.015, min(speed_ms, 0.25)), mode=mode, edition=edition
            )
            self._send_json(200, {"ok": True, "edition": normalize_edition(edition), "pages": pages, "mode": mode})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw_body)
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": f"Invalid JSON: {exc}"})
            return

        try:
            if parsed.path in ("/api/save-page-edits", "/api/save-page"):
                res = handle_save_page_edits(payload)
                self._send_json(200, res)
                return
            if parsed.path == "/api/upload-photo":
                res = handle_upload_photo(payload)
                self._send_json(200, res)
                return
            self._send_json(404, {"ok": False, "error": f"Unknown endpoint: {parsed.path}"})
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-browser", action="store_true")
    args, _ = parser.parse_known_args()

    print("Installing bundled Document Fonts for current OS (macOS / Windows / Linux)...")
    n_fonts = install_bundled_fonts_for_os()
    if n_fonts:
        print(f"  Installed {n_fonts} font file(s) into user font directory.")

    print("Localizing .pagedesigner & .dns asset paths for current workspace...")
    localize_pagedesigner_asset_links()

    print("Syncing Gujarati, Hindi & English (10 Pages Each) previews & photo assets...")
    sync_initial_previews_and_photos()
    try:
        ensure_visible_pagedesigner(bring_to_front=False)
    except Exception:
        pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", APP_PORT), GujaratiStudioRequestHandler)
    url = f"http://127.0.0.1:{APP_PORT}/Gujarati_Page_Designer_App.html"
    print(f"Gujarat Samachar / Aas-Paas / INDIAN POST (3 Editions × 10 Pages) Live Studio running at {url}")
    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
