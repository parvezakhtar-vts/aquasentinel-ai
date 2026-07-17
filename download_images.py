#!/usr/bin/env python3
"""
Download real microscope images for each organism from Wikimedia Commons.

Only freely-licensed images are fetched (Commons content is CC / public
domain), and the licence + author for every file is recorded in
ATTRIBUTIONS.md so you can credit them.

Images are saved under data/real_samples/<class>/ which is git-ignored, so no
third-party image is ever pushed to the public repo. Use them locally to test
the classifier or to fine-tune the CNN (see docs/UPGRADE_REAL_MODEL.md).

Usage:
    python3 download_images.py            # ~6 images per class
    python3 download_images.py --per 10   # more per class
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = ("AquaSentinelAI/0.1 (https://github.com/parvezakhtar-vts/aquasentinel-ai; "
      "educational science-fair project)")
# Standard cached thumbnail widths Commons serves without on-the-fly rendering.
THUMB_WIDTH = 640

# Search terms per class. Broad enough to return real microscopy hits.
SEARCH_TERMS = {
    "algae": "algae microscope",
    "cyanobacteria": "cyanobacteria microscope",
    "giardia": "Giardia lamblia",
    "cryptosporidium": "Cryptosporidium oocyst",
    "ecoli": "Escherichia coli microscopy",
    "naegleria": "Naegleria fowleri",
    "clean_water": "diatoms light microscope",  # benign freshwater field ("low risk")
}

OUT_ROOT = Path(__file__).parent / "data" / "real_samples"


def _get(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_images(term: str, limit: int) -> list[dict]:
    """Return image records (thumburl + licence metadata) for a search term."""
    data = _get({
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"{term} filetype:bitmap",
        "gsrnamespace": "6",          # File: namespace
        "gsrlimit": str(limit * 3),   # over-fetch; we filter below
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": str(THUMB_WIDTH),   # standard cached width -> no 429
    })
    pages = data.get("query", {}).get("pages", {})
    records = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        mime = info.get("mime", "")
        thumb = info.get("thumburl")
        if not thumb or mime not in ("image/jpeg", "image/png"):
            continue
        meta = info.get("extmetadata", {})
        records.append({
            "title": page.get("title", ""),
            "thumburl": thumb,
            "descurl": info.get("descriptionurl", ""),
            "license": meta.get("LicenseShortName", {}).get("value", "unknown"),
            "author": _strip_html(meta.get("Artist", {}).get("value", "unknown")),
        })
    return records[:limit]


def _strip_html(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s).strip() or "unknown"


def download(rec: dict, dest: Path, retries: int = 4) -> bool:
    delay = 2.0
    for attempt in range(retries):
        try:
            req = urllib.request.Request(rec["thumburl"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            dest.write_bytes(data)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(delay)      # back off on rate limit
                delay *= 2
                continue
            print(f"    ! failed: {e}")
            return False
        except Exception as e:  # noqa: BLE001 - best-effort downloader
            print(f"    ! failed: {e}")
            return False
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=6, help="images per class")
    args = ap.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    attributions = ["# Image attributions\n",
                    "Real microscope images downloaded from Wikimedia Commons.",
                    "Each is used under the licence shown; credit the author when reused.\n"]
    total = 0

    for cls, term in SEARCH_TERMS.items():
        cls_dir = OUT_ROOT / cls
        cls_dir.mkdir(exist_ok=True)
        print(f"[{cls}] searching Commons for '{term}' ...")
        try:
            recs = search_images(term, args.per)
        except Exception as e:  # noqa: BLE001
            print(f"    ! search failed: {e}")
            continue

        attributions.append(f"\n## {cls}  (search: \"{term}\")")
        got = 0
        for i, rec in enumerate(recs, 1):
            ext = ".png" if rec["thumburl"].lower().endswith(".png") else ".jpg"
            dest = cls_dir / f"{cls}_{i:02d}{ext}"
            if download(rec, dest):
                got += 1
                total += 1
                attributions.append(
                    f"- `{dest.name}` — {rec['title']} — "
                    f"licence: {rec['license']} — author: {rec['author']} — {rec['descurl']}")
            time.sleep(1.2)  # be polite to the image server
        print(f"    downloaded {got} image(s)")

    (OUT_ROOT / "ATTRIBUTIONS.md").write_text("\n".join(attributions) + "\n")
    print(f"\nDone. {total} images saved under {OUT_ROOT}")
    print(f"Attributions written to {OUT_ROOT / 'ATTRIBUTIONS.md'}")


if __name__ == "__main__":
    main()
