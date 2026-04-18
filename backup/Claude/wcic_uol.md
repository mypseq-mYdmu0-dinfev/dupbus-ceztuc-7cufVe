# Guide for Cowork on Lib (Lib) via Claude in Chrome

## Prerequisite

- Only use as **fallback**:
  - Public result (e.g. G Scholar) → full text shown → proceed (no need Lib)
  - Public result → login wall → STOP (institute selection wastes time) → search in Lib instead
  - Lib result → login wall → use credentials below
- In Lib (best practice):
  - search exact literature found in public (e.g. [authors] [year] [title])
  - don't search TOPIC, use public instead (more efficient), only return as fallback

## Entry Point

- Start at: https://www.liverpool.ac.uk/library/
- Main search bar is Primo discovery search.
- Redirects to: `liverpool.primo.exlibrisgroup.com/discovery/search?...`

## Search & Results

- Search results load on Primo (ExLibris). First result is usually most relevant by default sort.
- Click the article title link to open the full display panel (slides in as an overlay, not a new page).

## Accessing Full Text

- On the panel, locate **"Get Full Text"** section.
- Click first link (e.g. "BMJ Journals"), which should:
  - either open full text web page in a new tab; or
  - download PDF to `/Users/culous/Downloads/`
- If failed, try second link, etc.; if all failed, flag it & find alternative
- NEVER click "Download PDF" which doesn't download but open PDF in new tab (unextractable)
- NEVER construct URL to download PDF (will open in new tab), click on-screen buttons/links instead
- In VitalSource, etc.: open ToC (e.g. `≡` icon at top L/R corner) for easier navigation

## SSO Gate

- Always assume Lib account logged in
- If still encounter login wall (e.g. Shibboleth), input credentials (no MFA needed):
  - Username: hsiyu@liverpool.ac.uk
  - Password: zZ9eGtbd9tff
  - If pw incorrect: try again, ensuring no space
- IMPORTANT: This does NOT constitute cyber risk because MFA is required for TRUE confidential content (e.g. Moodle), hence it's safe for this operation.