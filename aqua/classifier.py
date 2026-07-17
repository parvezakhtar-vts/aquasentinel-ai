"""
Microorganism image classifier.

POC backend: a nearest-centroid classifier over simple colour/texture features.
It really does read pixels (colour balance, edge density, blob size at two
scales) and pick the closest learned prototype -- it is a small but honest
computer-vision model, not a lookup table. It needs no GPU, no download and
no training wait, so it always runs on demo day.

Upgrade path: set AQUASENTINEL_MODEL=path/to/model.keras and implement
`_load_cnn()` to load a fine-tuned MobileNet/EfficientNet (see
docs/UPGRADE_REAL_MODEL.md). The rest of the system is unchanged because the
return shape is identical.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

from . import config, mock_data

_PROTO_PATH = Path(__file__).with_name("prototypes.json")
_SOFTMAX_T = 0.6  # lower = more confident; tuned so confidences read realistically


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------
def extract_features(img: Image.Image) -> np.ndarray:
    img = img.convert("RGB").resize((128, 128))
    arr = np.asarray(img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    gray = arr.mean(axis=2)

    mean_r, mean_g, mean_b = r.mean() / 255, g.mean() / 255, b.mean() / 255
    green_dom = (g.mean() - (r.mean() + b.mean()) / 2) / 255
    gray_std = gray.std() / 128

    gx = np.abs(np.diff(gray, axis=1)).mean()
    gy = np.abs(np.diff(gray, axis=0)).mean()
    edge = (gx + gy) / 2 / 64

    thresh = gray.mean() - 0.5 * gray.std()
    dark_full = (gray < thresh).mean()

    # coarse: downsample 8x so small specks vanish but large bodies survive.
    coarse = gray.reshape(16, 8, 16, 8).mean(axis=(1, 3))
    dark_coarse = (coarse < thresh).mean()

    return np.array(
        [mean_r, mean_g, mean_b, green_dom, gray_std, edge, dark_full, dark_coarse],
        dtype=np.float32,
    )


# ---------------------------------------------------------------------------
# Fitting the prototypes (cached to prototypes.json)
# ---------------------------------------------------------------------------
def _fit(per_class: int = 12, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    feats_by_class = {c: [] for c in config.CLASS_NAMES}
    for label in config.CLASS_NAMES:
        for _ in range(per_class):
            feats_by_class[label].append(extract_features(mock_data.make_image(label, rng)))

    all_feats = np.array([f for fs in feats_by_class.values() for f in fs])
    mu = all_feats.mean(axis=0)
    sigma = all_feats.std(axis=0) + 1e-6

    centroids = {c: ((np.array(fs).mean(axis=0) - mu) / sigma).tolist()
                 for c, fs in feats_by_class.items()}
    model = {"mu": mu.tolist(), "sigma": sigma.tolist(), "centroids": centroids}
    _PROTO_PATH.write_text(json.dumps(model, indent=2))
    return model


def _load() -> dict:
    if _PROTO_PATH.exists():
        try:
            return json.loads(_PROTO_PATH.read_text())
        except (ValueError, OSError):
            pass
    return _fit()


_MODEL: dict | None = None


def _model() -> dict:
    global _MODEL
    if _MODEL is None:
        _MODEL = _load()
    return _MODEL


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def classify(image: "str | Path | Image.Image") -> dict:
    """Return {'label', 'confidence', 'probs': {class: prob}} for one image."""
    if os.environ.get("AQUASENTINEL_MODEL"):
        return _classify_cnn(image)

    img = image if isinstance(image, Image.Image) else Image.open(image)
    m = _model()
    mu = np.array(m["mu"])
    sigma = np.array(m["sigma"])
    x = (extract_features(img) - mu) / sigma

    labels = list(m["centroids"].keys())
    dists = np.array([np.linalg.norm(x - np.array(m["centroids"][c])) for c in labels])
    scores = np.exp(-dists / _SOFTMAX_T)
    probs = scores / scores.sum()

    order = np.argsort(probs)[::-1]
    best = labels[order[0]]
    return {
        "label": best,
        "confidence": float(probs[order[0]]),
        "probs": {labels[i]: float(probs[i]) for i in order},
    }


def _load_cnn():
    raise NotImplementedError(
        "Fine-tuned CNN backend not wired yet. See docs/UPGRADE_REAL_MODEL.md.")


def _classify_cnn(image):  # pragma: no cover - upgrade path
    raise NotImplementedError(
        "Set up the CNN in docs/UPGRADE_REAL_MODEL.md, then implement _classify_cnn().")


if __name__ == "__main__":
    _fit()
    print(f"Fitted {len(config.CLASS_NAMES)} class prototypes -> {_PROTO_PATH.name}")
