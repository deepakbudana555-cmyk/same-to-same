# Gujarat Samachar (`ગુજરાત સમાચાર`) / Aas-Paas (`आस-पास`) / INDIAN POST — 3-Column Same-to-Same Comparison & Live Page Designer Studio

Complete **30-Page Editable Broadsheet Newspaper Suite** with a **3-Column Side-by-Side Comparison Studio** (`http://127.0.0.1:47898/Gujarati_Page_Designer_App.html`):
- **◀ LEFT COLUMN:** **हिन्दी (`आस-पास` — 10 Pages)** — `Indian Post Mast` / `DB Hindi Mast` Gujarat Samachar Calligraphic Devanagari Masthead, `DB Hindi`, `DB Madhurima`
- **★ CENTER MASTER COLUMN:** **ગુજરાતી (`ગુજરાત સમાચાર` — 10 Pages Original Master in Center)** — `Gopika`, `Arial`
- **▶ RIGHT COLUMN:** **ENGLISH (`INDIAN POST` — 10 Pages)** — `Indian Post Mast` Gujarat Samachar Calligraphic English Masthead, `Times New Roman`, `Georgia`, `Arial`, `Source Serif 4`

### Key UI Features
1. **3 Front Pages Side-by-Side (`Left: Hindi | Center: Gujarati | Right: English`):** Compare all 3 newspapers side-by-side with synchronized scrolling (`↕️ Sync 3-Column Scroll`).
2. **Top `10 | 10 | 10` Page Menus (`P01..P10` for Hindi, Gujarati & English):** Switch any column (or all 3 columns locked together) across Pages 01 to 10.
3. **1-Click Live Build in Page Designer 1.0:** Clicking **any `P01..P10` button**, **any newspaper page image**, or **`⚡ LIVE BUILD IN PAGE DESIGNER`** immediately opens that exact page in **Page Designer 1.0** (`Page Designer.app` on macOS / `pagedesigner.exe` on Windows) and draws every element live step-by-step from start to finish!

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
   - Opens the **3-Column Comparison Studio** in your browser at:
     **`http://127.0.0.1:47898/Gujarati_Page_Designer_App.html`**

### Option 2: Auto-Run All 30 Pages (Gujarati -> Hindi -> English) Live in Page Designer 1.0
- Double-click **`run_all_3_editions_on_mac.command`** (or click **`🚀 Auto-Run All 30 Pages in PD`** in the top bar of the localhost web app):
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
