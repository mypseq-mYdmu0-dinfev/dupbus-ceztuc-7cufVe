#!/usr/bin/env python3
"""
ocr_reads.py —— OCR batch reader (macOS)

Detects every .jpg / .png / .pdf file sitting BESIDE this script (top level of
gscpt/ only; anything inside parked/ or any other subfolder is ignored, as is
any `❌_`-prefixed filename), OCR-reads each one, and writes one .md per input
(identical basename) into a NEW folder `gscpt/[YYYYMMDDHHmm]/` (current Sydney
time).

OCR means, in preference order (a "means" = one OCR engine/config):
  1. vision-accurate —— Apple Vision framework (pyobjc), accurate recognition
  2. vision-fast     —— Apple Vision framework, fast recognition level
  3. tesseract       —— only if the tesseract CLI is installed
PDFs: pages with a real text layer are extracted via PDFKit; image-only pages
are rendered to bitmaps via Quartz and OCR'd like images.

RE-RUN BEHAVIOUR (within 30 minutes, same input set)
----------------------------------------------------
If a previous run's folder exists whose folder-name TS is within 30 minutes
and whose .md files match the current inputs: that folder is duplicated as
`[current_TS]/` (with `_new` appended if the name is taken, e.g. same minute),
the un-suffixed files inside are renamed by appending `_[means]` (the means
that produced them), and the inputs are re-OCR'd with the NEXT unused means,
written as `[stem]_[means].md` into the duplicated folder. When every
available means has already been used (a third run with only two means on
this Mac), the script prints an error and exits non-zero.

If pyobjc's Vision/Quartz are not importable under the invoking python, the
script re-execs itself with the AJAP repo's venv python (which has them).

Run:  python3 ocr_reads.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).resolve().parent
PARKED_DIR = SCRIPT_DIR / "parked"   # contents ignored by every gscpt script
SYDNEY = ZoneInfo("Australia/Sydney")
INPUT_EXTS = {".jpg", ".png", ".pdf"}
WINDOW_MIN = 30                      # re-run window, minutes
RUN_DIR_RE = re.compile(r"^(\d{12})(?:_new)*$")
PDF_RENDER_SCALE = 2.0               # ~144 dpi for image-only PDF pages

# Python with pyobjc Vision/Quartz installed, used as a fallback interpreter.
VISION_PYTHON = "/Volumes/FURY 2TB/Fury Documents/GitHub/AJAP_repo/.venv/bin/python3"


def die(msg: str) -> None:
    print(f"⛔ ocr_reads: {msg}")
    sys.exit(1)


def ensure_vision() -> None:
    """Import Vision/Quartz, or re-exec under VISION_PYTHON (once)."""
    try:
        import Quartz   # noqa: F401
        import Vision   # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("OCR_READS_REEXEC") != "1" and Path(VISION_PYTHON).exists():
        env = {**os.environ, "OCR_READS_REEXEC": "1"}
        os.execve(VISION_PYTHON,
                  [VISION_PYTHON, str(Path(__file__).resolve()), *sys.argv[1:]],
                  env)
    die("pyobjc Vision/Quartz not importable (install pyobjc, or fix "
        f"VISION_PYTHON —— tried {VISION_PYTHON}).")


# ------------------------------------------------------------------ OCR: Vision
def _cgimage_from_file(path: Path):
    import Quartz
    raw = str(path).encode()
    url = Quartz.CFURLCreateFromFileSystemRepresentation(None, raw, len(raw), False)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return None
    return Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)


def _ocr_cgimage_vision(img, accurate: bool) -> str:
    """OCR one CGImage; observations sorted top-down then left-right."""
    import Vision
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(img, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(
        Vision.VNRequestTextRecognitionLevelAccurate if accurate
        else Vision.VNRequestTextRecognitionLevelFast)
    req.setUsesLanguageCorrection_(accurate)
    ok = handler.performRequests_error_([req], None)
    if not ok:
        return ""
    rows = []
    for obs in (req.results() or []):
        cand = obs.topCandidates_(1)
        if not cand or not len(cand):
            continue
        bb = obs.boundingBox()               # normalised, origin bottom-left
        y_top = 1.0 - (bb.origin.y + bb.size.height)
        rows.append((y_top, float(bb.origin.x), str(cand[0].string())))
    rows.sort(key=lambda r: (round(r[0], 3), r[1]))
    return "\n".join(r[2] for r in rows)


def _pdf_page_cgimage(cg_doc, page_no: int):
    """Render one page (1-based) of a CGPDFDocument to a CGImage."""
    import Quartz
    page = Quartz.CGPDFDocumentGetPage(cg_doc, page_no)
    if page is None:
        return None
    box = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
    w = max(1, int(box.size.width * PDF_RENDER_SCALE))
    h = max(1, int(box.size.height * PDF_RENDER_SCALE))
    cs = Quartz.CGColorSpaceCreateDeviceRGB()
    ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, cs,
                                       Quartz.kCGImageAlphaPremultipliedLast)
    if ctx is None:
        return None
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
    Quartz.CGContextScaleCTM(ctx, PDF_RENDER_SCALE, PDF_RENDER_SCALE)
    Quartz.CGContextTranslateCTM(ctx, -box.origin.x, -box.origin.y)
    Quartz.CGContextDrawPDFPage(ctx, page)
    return Quartz.CGBitmapContextCreateImage(ctx)


def _read_pdf(path: Path, ocr_image_fn) -> str:
    """Per page: PDFKit text layer if present, else render + ocr_image_fn."""
    import Quartz
    raw = str(path).encode()
    url = Quartz.CFURLCreateFromFileSystemRepresentation(None, raw, len(raw), False)
    pk_doc = Quartz.PDFDocument.alloc().initWithURL_(url)
    cg_doc = Quartz.CGPDFDocumentCreateWithURL(url)
    if pk_doc is None and cg_doc is None:
        return ""
    n = (int(pk_doc.pageCount()) if pk_doc is not None
         else int(Quartz.CGPDFDocumentGetNumberOfPages(cg_doc)))
    parts = []
    for i in range(n):
        text = ""
        if pk_doc is not None:
            pg = pk_doc.pageAtIndex_(i)
            s = pg.string() if pg is not None else None
            if s is not None and str(s).strip():
                text = str(s).strip()        # real text layer —— no OCR needed
        if not text and cg_doc is not None:
            img = _pdf_page_cgimage(cg_doc, i + 1)   # CGPDF pages are 1-based
            if img is not None:
                text = ocr_image_fn(img)
        parts.append(text)
    return "\n\n".join(parts).strip()


def _read_any_vision(path: Path, accurate: bool) -> str:
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path, lambda img: _ocr_cgimage_vision(img, accurate))
    img = _cgimage_from_file(path)
    if img is None:
        return ""
    return _ocr_cgimage_vision(img, accurate)


# --------------------------------------------------------------- OCR: tesseract
def _png_from_cgimage(img, dest: Path) -> bool:
    import Quartz
    raw = str(dest).encode()
    url = Quartz.CFURLCreateFromFileSystemRepresentation(None, raw, len(raw), False)
    d = Quartz.CGImageDestinationCreateWithURL(url, "public.png", 1, None)
    if d is None:
        return False
    Quartz.CGImageDestinationAddImage(d, img, None)
    return bool(Quartz.CGImageDestinationFinalize(d))


def _tesseract_file(path: Path) -> str:
    r = subprocess.run(["tesseract", str(path), "stdout"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _read_any_tesseract(path: Path) -> str:
    if path.suffix.lower() != ".pdf":
        return _tesseract_file(path)

    def ocr_img(img):                        # render page -> temp png -> tesseract
        import Quartz  # noqa: F401
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
            tmp = Path(tf.name)
        try:
            return _tesseract_file(tmp) if _png_from_cgimage(img, tmp) else ""
        finally:
            tmp.unlink(missing_ok=True)
    return _read_pdf(path, ocr_img)


# ----------------------------------------------------------------------- means
def available_means() -> list[str]:
    """OCR means on THIS machine, best first."""
    means = ["vision-accurate", "vision-fast"]
    if shutil.which("tesseract"):
        means.append("tesseract")
    return means


def read_with_means(path: Path, means: str) -> str:
    if means == "vision-accurate":
        return _read_any_vision(path, accurate=True)
    if means == "vision-fast":
        return _read_any_vision(path, accurate=False)
    if means == "tesseract":
        return _read_any_tesseract(path)
    die(f"unknown OCR means '{means}'.")


# ------------------------------------------------------------------- run logic
def detect_inputs() -> list[Path]:
    """Top-level gscpt/ only —— parked/ and every other subfolder are ignored,
    as are ❌_-prefixed files (parked in place)."""
    return sorted(p for p in SCRIPT_DIR.iterdir()
                  if p.is_file() and p.suffix.lower() in INPUT_EXTS
                  and not p.name.startswith("❌_"))


def folder_md_bases(folder: Path, all_means: list[str]) -> dict[str, set[str | None]]:
    """{base_stem: {means_or_None(=plain), ...}} for the .md files in folder."""
    out: dict[str, set[str | None]] = {}
    for f in folder.iterdir():
        if not (f.is_file() and f.suffix.lower() == ".md"):
            continue
        stem, used = f.stem, None
        for mn in all_means:
            if stem.endswith(f"_{mn}"):
                stem, used = stem[: -len(mn) - 1], mn
                break
        out.setdefault(stem, set()).add(used)
    return out


def find_prev_run(now: datetime, stems: set[str], all_means: list[str]) -> Path | None:
    """Most recent run folder within WINDOW_MIN whose .md set matches stems."""
    cands = []
    for d in SCRIPT_DIR.iterdir():
        m = RUN_DIR_RE.match(d.name) if d.is_dir() else None
        if not m:
            continue
        try:
            ts = datetime.strptime(m.group(1), "%Y%m%d%H%M").replace(tzinfo=SYDNEY)
        except ValueError:
            continue
        if abs((now - ts).total_seconds()) > WINDOW_MIN * 60:
            continue
        if set(folder_md_bases(d, all_means)) == stems:
            cands.append((ts, len(d.name), d))
    return max(cands)[2] if cands else None


def unique_run_dir(ts: str) -> Path:
    d = SCRIPT_DIR / ts
    while d.exists():
        d = SCRIPT_DIR / (d.name + "_new")
    return d


def ocr_into(inputs: list[Path], out_dir: Path, means: str, suffix: bool) -> None:
    for p in inputs:
        name = f"{p.stem}_{means}.md" if suffix else f"{p.stem}.md"
        text = read_with_means(p, means)
        (out_dir / name).write_text(text + "\n", encoding="utf-8")
        print(f"   {p.name}  ->  {out_dir.name}/{name}"
              + ("" if text else "   (⚠️ no text recognised)"))


def main() -> None:
    ensure_vision()
    now = datetime.now(SYDNEY)
    cur_ts = now.strftime("%Y%m%d%H%M")
    inputs = detect_inputs()
    if not inputs:
        die(f"no .jpg/.png/.pdf files found beside the script in {SCRIPT_DIR}.")
    stems = {p.stem for p in inputs}
    means_list = available_means()

    prev = find_prev_run(now, stems, means_list)
    if prev is None:
        out_dir = unique_run_dir(cur_ts)
        out_dir.mkdir()
        print(f"▶ ocr_reads: fresh run —— means '{means_list[0]}' on "
              f"{len(inputs)} file(s) -> {out_dir.name}/")
        ocr_into(inputs, out_dir, means_list[0], suffix=False)
    else:
        used: set[str] = set()
        for bases in folder_md_bases(prev, means_list).values():
            used |= {means_list[0] if u is None else u for u in bases}
        remaining = [m for m in means_list if m not in used]
        if not remaining:
            print(f"⛔ ocr_reads: all {len(means_list)} available OCR means "
                  f"({', '.join(means_list)}) were already used for these inputs "
                  f"within the last {WINDOW_MIN} min (folder {prev.name}/). "
                  "Nothing further to run —— wait past the window, or install "
                  "another means (e.g. tesseract).")
            sys.exit(1)
        out_dir = unique_run_dir(cur_ts)
        shutil.copytree(prev, out_dir)
        renamed = 0
        for f in list(out_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".md" and f.stem in stems:
                f.rename(out_dir / f"{f.stem}_{means_list[0]}.md")
                renamed += 1
        print(f"▶ ocr_reads: re-run within {WINDOW_MIN} min —— duplicated "
              f"{prev.name}/ as {out_dir.name}/ ({renamed} file(s) renamed "
              f"with _{means_list[0]}); second means '{remaining[0]}':")
        ocr_into(inputs, out_dir, remaining[0], suffix=True)
    print(f"✅ done: {out_dir}")


if __name__ == "__main__":
    main()
