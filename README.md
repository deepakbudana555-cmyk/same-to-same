# Gujarat Samachar (`ગુજરાત સમાચાર`) / Aas-Paas (`आस-पास`) / INDIAN POST — 3-Edition × 10-Page Same-to-Same Live Studio

Complete **30-Page Editable Broadsheet Newspaper Suite** (10 Gujarati Pages + 10 Hindi Pages + 10 English Pages) with **Gujarat Samachar (`Shaily`) Calligraphic Mastheads** for:
1. **ગુજરાતી (`ગુજરાત સમાચાર`)** — Pages 01 to 10 (`Gopika`, `Arial`)
2. **हिन्दी (`आस-पास`)** — Pages 01 to 10 (`Indian Post Mast` / `DB Hindi Mast` Gujarat Samachar Calligraphic Devanagari Masthead, `DB Hindi`, `DB Madhurima`)
3. **ENGLISH (`INDIAN POST`)** — Pages 01 to 10 (`Indian Post Mast` Gujarat Samachar Calligraphic English Masthead, `Times New Roman`, `Georgia`, `Arial`, `Source Serif 4`)

---

## Quick Start on macOS (Mac)

> **Prerequisite:** Make sure **Page Designer 1.0** (`Page Designer.app`) is installed on your Mac (e.g., in `/Applications/Page Designer.app` or `~/Desktop`).

### Option 1: Double-Click Launcher (Recommended)
1. Clone this repository on your Mac:
   ```bash
   git clone https://github.com/deepakbudana555-cmyk/same-to-same.git
   cd same-to-same
   ```
2. Double-click **`run_on_mac.command`** (or run `./run_on_mac.command` in Terminal).
   - Automatically copies all **50+ bundled `.ttf` fonts** from `SAME TO SAME GUJRATI NEWS/Document Fonts/` into `~/Library/Fonts/`.
   - Automatically localizes all `.pagedesigner` and `.dns` asset paths to your Mac folder.
   - Starts **Page Designer 1.0** with `--control 47123`.
   - Opens the **Live Newspaper Studio** in your browser at:
     **`http://127.0.0.1:47898/Gujarati_Page_Designer_App.html`**

### Option 2: Auto-Run All 30 Pages (Gujarati -> Hindi -> English) Live in Page Designer 1.0
- Double-click **`run_all_3_editions_on_mac.command`** (or click **`🚀 RUN ALL 3 EDITIONS (30 PAGES) IN PAGE DESIGNER`** in the top bar of the localhost web app):
  ```bash
  ./run_all_3_editions_on_mac.command
  ```

---

## Quick Start on Windows
1. Double-click **`run_on_windows.bat`** or run:
   ```powershell
   python "SAME TO SAME GUJRATI NEWS\Gujarati_Page_Designer_App\launch_gujarati_page_designer_app.py"
   ```
2. Open **`http://127.0.0.1:47898/Gujarati_Page_Designer_App.html`**.

---

## Bundled Fonts (`SAME TO SAME GUJRATI NEWS/Document Fonts/`)
Page Designer 1.0 automatically scopes `Document Fonts/` located alongside the `.pagedesigner` files, and `run_on_mac.command` also installs them into `~/Library/Fonts`:
- `Indian Post Mast.ttf` & `DB Hindi Mast.ttf` — Custom Gujarat Samachar (`Shaily`) Calligraphic Masthead font containing both **Hindi Devanagari (`आस-पास`)** and **English (`INDIAN POST`)** calligraphic letterforms.
- `Gopika-UltraBold.ttf`, `GopikaUltraBold-Regular.ttf`, `GopikaUltraBold-Bold.ttf`, `NotoSansGujarati-*.ttf` — Gujarati headline & body fonts.
- `DB Hindi.ttf`, `DB Hindi Bold.ttf`, `DB Madhurima Regular.ttf`, `NotoSansDevanagari-*.ttf` — Hindi headline & body fonts.
- `times.ttf`, `timesbd.ttf`, `georgia.ttf`, `georgiab.ttf`, `arial.ttf`, `arialbd.ttf`, `SourceSerif4-*.ttf`, `SourceSans3-*.ttf` — English headline & body fonts.
