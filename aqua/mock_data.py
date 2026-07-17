"""
Mock data generator — simulates the pendrive her hardware would produce.

Creates a folder that looks exactly like what the real capture device would
write:

    pendrive/
        images/       sample_XXX.png  (synthetic microscope frames)
        readings.csv  sample_id, true_label, ph, temperature

The images are drawn to match each organism's visual `signature` in config.py,
so the classifier has something real (pixels) to work on rather than a lookup.
Swap this folder for a real pendrive later and nothing downstream changes.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import config

IMG_SIZE = 256


def _background(rng: np.random.Generator, base_rgb) -> Image.Image:
    """A slightly noisy, vignetted field of view, like a real microscope."""
    arr = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.float32)
    for c in range(3):
        arr[:, :, c] = base_rgb[c]
    arr += rng.normal(0, 8, arr.shape)  # sensor grain

    # circular vignette so the frame reads as "through a lens"
    yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
    cx = cy = IMG_SIZE / 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (IMG_SIZE / 2)
    vignette = np.clip(1.15 - 0.35 * dist**2, 0, 1)[:, :, None]
    arr *= vignette

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _draw_blob(draw: ImageDraw.ImageDraw, kind: str, cx, cy, size, color, rng):
    c = tuple(int(v) for v in color)
    if kind == "rod":
        w, h = size * 0.35, size
        ang = rng.uniform(0, 180)
        _rot_ellipse(draw, cx, cy, w, h, ang, c)
    elif kind == "round_small":
        r = size * 0.5
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    elif kind == "oval":
        w, h = size * 0.6, size
        draw.ellipse([cx - w, cy - h, cx + w, cy + h], fill=c)
    elif kind == "amoeba":
        pts = []
        n = 9
        for i in range(n):
            a = 2 * math.pi * i / n
            r = size * (0.7 + rng.uniform(-0.25, 0.35))
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(pts, fill=c)
    elif kind == "filament":
        x, y = cx, cy
        ang = rng.uniform(0, 2 * math.pi)
        for _ in range(int(size)):
            nx = x + 4 * math.cos(ang)
            ny = y + 4 * math.sin(ang)
            draw.line([x, y, nx, ny], fill=c, width=3)
            x, y, ang = nx, ny, ang + rng.uniform(-0.4, 0.4)
    elif kind == "cluster":
        for _ in range(rng.integers(4, 8)):
            r = size * rng.uniform(0.3, 0.7)
            ox, oy = rng.uniform(-size, size), rng.uniform(-size, size)
            draw.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=c)


def _rot_ellipse(draw, cx, cy, w, h, ang_deg, color):
    tmp = Image.new("RGBA", (int(h * 2 + 4), int(h * 2 + 4)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    m = tmp.size[0] / 2
    td.ellipse([m - w, m - h, m + w, m + h], fill=color + (255,))
    tmp = tmp.rotate(ang_deg, expand=False)
    draw._image.paste(tmp, (int(cx - m), int(cy - m)), tmp)


def make_image(label: str, rng: np.random.Generator) -> Image.Image:
    sig = config.ORGANISMS[label]["signature"]
    img = _background(rng, sig["base_rgb"])
    draw = ImageDraw.Draw(img, "RGBA")
    draw._image = img  # used by _rot_ellipse for pasting

    count = int(sig["count"] + rng.integers(-2, 3)) if sig["count"] else 0
    for _ in range(max(count, 0)):
        margin = 40
        cx = rng.uniform(margin, IMG_SIZE - margin)
        cy = rng.uniform(margin, IMG_SIZE - margin)
        base_size = {"rod": 10, "round_small": 8, "oval": 9, "amoeba": 22,
                     "filament": 12, "cluster": 14}.get(sig["blob"], 10)
        size = base_size * rng.uniform(0.8, 1.3)
        color = np.array(sig["blob_color"]) + rng.normal(0, 15, 3)
        _draw_blob(draw, sig["blob"], cx, cy, size, color, rng)

    return img.filter(ImageFilter.GaussianBlur(0.6))


def _reading_for(label: str, rng: np.random.Generator):
    """Plausible pH + temperature, correlated with how dangerous the sample is."""
    danger = config.ORGANISMS[label]["danger"]
    if danger == 0:
        ph = rng.normal(7.2, 0.3)
        temp = rng.normal(24, 2)
    elif danger == 1:
        ph = rng.normal(8.1, 0.6)      # algae blooms push pH up
        temp = rng.normal(27, 3)
    elif danger == 2:
        ph = rng.normal(6.6, 0.9)
        temp = rng.normal(29, 3)
    else:  # 3 - Naegleria loves warm water
        ph = rng.normal(7.0, 0.7)
        temp = rng.normal(33, 2.5)
    return round(float(np.clip(ph, 0, 14)), 2), round(float(np.clip(temp, 5, 45)), 1)


def generate_pendrive(out_dir: str | Path, per_class: int = 3, seed: int = 42) -> Path:
    """Create a simulated pendrive folder and return its path."""
    out = Path(out_dir)
    img_dir = out / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    rows = []
    idx = 0
    order = []
    for label in config.CLASS_NAMES:
        order += [label] * per_class
    rng.shuffle(order)

    for label in order:
        idx += 1
        sid = f"sample_{idx:03d}"
        make_image(label, rng).save(img_dir / f"{sid}.png")
        ph, temp = _reading_for(label, rng)
        rows.append({"sample_id": sid, "true_label": label, "ph": ph, "temperature": temp})

    with open(out / "readings.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sample_id", "true_label", "ph", "temperature"])
        w.writeheader()
        w.writerows(rows)

    return out


if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else "data/pendrive"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    path = generate_pendrive(dest, per_class=n)
    print(f"Simulated pendrive written to: {path.resolve()}")
    print(f"  images/     -> {n * len(config.CLASS_NAMES)} microscope frames")
    print(f"  readings.csv-> pH + temperature per sample")
