"""
Pipeline — glue the pieces into one call.

process_sample(): one image + pH + temperature -> full result for display.
process_pendrive(): a whole pendrive folder -> a list of results.

The result dict is the single contract the dashboards (CLI + Streamlit) render,
so both front-ends stay dumb and consistent.
"""
from __future__ import annotations

import csv
from pathlib import Path

from . import classifier, config, fusion

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def process_sample(image_path, ph=None, temperature=None, sample_id=None,
                   true_label=None) -> dict:
    cls = classifier.classify(image_path)
    org = config.ORGANISMS[cls["label"]]
    verdict = fusion.assess(cls, ph, temperature)

    return {
        "sample_id": sample_id or Path(image_path).stem,
        "image_path": str(image_path),
        "organism": org["label"],
        "organism_key": cls["label"],
        "kind": org["kind"],
        "disease": org["disease"],
        "confidence": cls["confidence"],
        "probs": cls["probs"],
        "ph": ph,
        "temperature": temperature,
        "true_label": true_label,
        "correct": (true_label == cls["label"]) if true_label else None,
        **verdict,
    }


def load_readings(pendrive_dir) -> dict:
    """Map sample_id -> {'ph', 'temperature', 'true_label'} from readings.csv."""
    path = Path(pendrive_dir) / "readings.csv"
    readings = {}
    if not path.exists():
        return readings
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            sid = row.get("sample_id", "").strip()
            if not sid:
                continue
            readings[sid] = {
                "ph": _to_float(row.get("ph")),
                "temperature": _to_float(row.get("temperature")),
                "true_label": (row.get("true_label") or "").strip() or None,
            }
    return readings


def process_pendrive(pendrive_dir) -> list[dict]:
    root = Path(pendrive_dir)
    img_dir = root / "images" if (root / "images").is_dir() else root
    readings = load_readings(root)

    results = []
    for img in sorted(img_dir.iterdir()):
        if img.suffix.lower() not in IMAGE_EXTS:
            continue
        r = readings.get(img.stem, {})
        results.append(process_sample(
            img, ph=r.get("ph"), temperature=r.get("temperature"),
            sample_id=img.stem, true_label=r.get("true_label"),
        ))
    return results


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
