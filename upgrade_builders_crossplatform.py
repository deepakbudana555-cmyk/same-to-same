from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

for pnum in range(1, 11):
    for pat in (
        f"build_page_{pnum:02d}_same_to_same.py",
        f"build_hindi_page_{pnum:02d}_same_to_same.py",
        f"build_english_page_{pnum:02d}_same_to_same.py",
    ):
        fp = ROOT / pat
        if not fp.exists():
            continue
        txt = fp.read_text(encoding="utf-8")

        # 1. Replace hardcoded DIR_SMAE / DIR_SAME / sys.path with cross-platform Path(__file__).resolve().parent
        txt = txt.replace(
            'DIR_SMAE = Path(r"E:\\RND\\SAME TO SMAE GUJRATI NEWS")\nDIR_SAME = Path(r"E:\\RND\\SAME TO SAME GUJRATI NEWS")',
            'RND_ROOT = Path(__file__).resolve().parent\nDIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"\nDIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"',
        )
        txt = txt.replace(
            'sys.path.insert(0, r"E:\\RND\\SAME TO SAME GUJRATI NEWS\\Gujarati_Page_Designer_App")',
            'sys.path.insert(0, str(DIR_SAME / "Gujarati_Page_Designer_App"))',
        )

        # 2. Ensure auto-launch fallback if Page Designer socket isn't open yet
        old_sock = 'sock = socket.create_connection(("127.0.0.1", PORT), timeout=15)'
        new_sock = """try:
    sock = socket.create_connection(("127.0.0.1", PORT), timeout=2.0)
except Exception:
    sys.path.insert(0, str(DIR_SAME / "Gujarati_Page_Designer_App"))
    import launch_gujarati_page_designer_app as _launcher
    _launcher.ensure_visible_pagedesigner(bring_to_front=False)
    sock = socket.create_connection(("127.0.0.1", PORT), timeout=15)"""
        if 'import launch_gujarati_page_designer_app as _launcher' not in txt and old_sock in txt:
            txt = txt.replace(old_sock, new_sock, 1)

        # 3. Upgrade Hindi masthead ('आस-पास') to use 'Indian Post Mast' (with Gujarat Samachar Calligraphic Shaily Hindi glyphs!)
        if "build_hindi_page_" in pat:
            txt = txt.replace('custom_font_family="DB Hindi Mast"', 'custom_font_family="Indian Post Mast"')

        # 4. Upgrade place_png to prefer .webp for fast drawing in Page Designer
        old_place = 'def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):\n    img_path = str((ASSETS_DIR / filename).resolve()).replace("\\\\", "/")'
        new_place = """def place_png(x1_px, y1_px, x2_px, y2_px, filename: str):
    webp_cand = ASSETS_DIR / (Path(filename).stem + ".webp")
    use_file = webp_cand if webp_cand.exists() else (ASSETS_DIR / filename)
    img_path = str(use_file.resolve()).replace("\\\\", "/")"""
        if old_place in txt:
            txt = txt.replace(old_place, new_place)

        # 5. Remove any hardcoded Windows artifact copy path that would fail on macOS
        txt = re.sub(
            r'shutil\.copy2\([^\n]+C:\\Users\\ADMIN\\\.gemini\\antigravity\\brain[^\n]+\)',
            'pass  # Cross-platform build complete',
            txt,
        )

        fp.write_text(txt, encoding="utf-8")
        print("Upgraded:", fp.name)

for comb in (
    "build_all_10_pages_same_to_same.py",
    "build_all_10_hindi_pages_same_to_same.py",
    "build_all_10_english_pages_same_to_same.py",
):
    fp = ROOT / comb
    if fp.exists():
        txt = fp.read_text(encoding="utf-8")
        txt = txt.replace(
            'DIR_SAME = Path(r"E:\\RND\\SAME TO SAME GUJRATI NEWS")\nDIR_SMAE = Path(r"E:\\RND\\SAME TO SMAE GUJRATI NEWS")',
            'RND_ROOT = Path(__file__).resolve().parent\nDIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"\nDIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"',
        )
        txt = txt.replace(
            'DIR_SMAE = Path(r"E:\\RND\\SAME TO SMAE GUJRATI NEWS")\nDIR_SAME = Path(r"E:\\RND\\SAME TO SAME GUJRATI NEWS")',
            'RND_ROOT = Path(__file__).resolve().parent\nDIR_SMAE = RND_ROOT / "SAME TO SMAE GUJRATI NEWS"\nDIR_SAME = RND_ROOT / "SAME TO SAME GUJRATI NEWS"',
        )
        txt = txt.replace(
            'for ext in (".png", ".jpg", ".jpeg", ".tif"):',
            'for ext in (".webp", ".png", ".jpg", ".jpeg", ".tif"):',
        )
        fp.write_text(txt, encoding="utf-8")
        print("Upgraded combiner:", fp.name)
