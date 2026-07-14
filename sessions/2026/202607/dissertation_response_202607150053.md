# Response to dissertation_query_202607150053.md
*All fixes done, mini variant built, 2 sets of PDF+PNG exported —— verified myself*

## A. branding.md

220. Corrected as instructed, and I see you refined it further (correct product name "Garamond Premiere Pro", moved the Display-weight requirement inline into the main table row) —— kept as you left it, not reverted.

## B. The SA's Work —— All Verified

221. Main `MGTK751_ad.html` —— 3 fixes, each independently confirmed by the SA (not just claimed):
- 221.1. Vertical centring —— was `position:absolute` with no bottom constraint (hence the uneven gap); switched to flex centring, measured top/bottom gaps effectively equal (49.656px vs 49.672px).
- 221.2. Font swap —— "STUDY:" and the italic study-name subtitle moved from Poppins to Garamond (same size, heavier weight per the new branding.md rule); the main title also bumped to Bold, since branding.md now bars thin/light Garamond.
- 221.3. Runts fixed —— non-breaking spaces inserted between the last two words of both culprit lines; no wording changed.
222. `MGTK751_ad_mini.html` —— a genuine mobile-legibility redesign, not a cosmetic tweak: larger/heavier body type, section headings turned into solid dark-teal pill labels (stronger scan-anchors at thumbnail size), the study line turned into a tinted accent-bar card, bigger icon chips, tighter margins to make room for the larger type. Same 3 fixes applied and re-verified.
223. Exports —— 4 files, via headless Chrome (`--print-to-pdf` + `--screenshot`, no wkhtmltopdf/Puppeteer available locally): `MGTK751_ad.pdf`/`.png` and `MGTK751_ad_mini.pdf`/`.png`. Both PDFs confirmed to hold real selectable vector text (`pdftotext` matched the source verbatim, not a rasterised flatten) —— genuinely "reviewer-comfy" as you wanted.
224. I did NOT just take the SA's word for it —— read both PNGs myself. Confirmed: centred, Garamond correctly weighted, no orphaned runt lines, mini variant is a real, distinct, legible redesign. Both are strong; both look ready for your review.

## C. Net

225. All 6 deliverable files (2 HTML, 2 PDF, 2 PNG) sit in `dissertation/ethics/`, plus the original `MGTK751_ad.md`. Your call on which variant's PDF+PNG pair goes to submission.
