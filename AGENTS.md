# AGENTS.md — integration guide for coding agents

This file is the source of truth for wiring AquaSentinel's moving pieces
together. Human-friendly usage is in `README.md`; this file is the precise
contract. **If you change a contract here, update every consumer listed.**

## System shape

Four layers. The Python `result object` is the single contract every front-end
renders — keep it stable.

```
microscope image ┐
pH sensor        ├─► aqua/pipeline.py ─► result object ─► front-ends (CLI / Streamlit / React)
temperature      ┘        (classify → fuse)
```

| Layer | Path | Language | Runtime |
| --- | --- | --- | --- |
| Firmware (pH+temp) | `arduino/ph_sensor_uno/` | C++/.ino | Arduino Uno |
| Firmware (Wi-Fi bridge) | `arduino/nodemcu_wifi/` | C++/.ino | NodeMCU/ESP8266 |
| AI core | `aqua/` | Python 3.11+ | library |
| CLI front-end | `run.py` | Python | terminal |
| Streamlit front-end | `dashboard.py` | Python | http://localhost:8501 |
| REST API | `api.py` | Python/FastAPI | http://localhost:8000 |
| React front-end | `frontend/` | React 19 + Vite | http://localhost:5173 |

## THE result object (the contract)

Produced by `aqua/pipeline.py:process_sample()` and `process_pendrive()`.
Every field below is always present unless noted.

```python
{
  "sample_id":     str,            # e.g. "sample_001"
  "image_path":    str,            # absolute path on disk
  "organism":      str,            # display name, e.g. "E. coli"
  "organism_key":  str,            # config key, e.g. "ecoli" (use for logic/CSS)
  "kind":          str,            # e.g. "Bacteria"
  "disease":       str,
  "confidence":    float,          # 0.0–1.0
  "probs":         dict[str,float],# organism_key -> prob, sorted desc
  "ph":            float | None,   # None if no reading
  "temperature":   float | None,   # Celsius; None if no reading
  "true_label":    str | None,     # only when readings.csv has a true_label column
  "correct":       bool | None,    # pred == true_label, else None
  # --- from aqua/fusion.py:assess() ---
  "risk":          "LOW" | "MODERATE" | "HIGH",
  "score":         int,            # 0..8, see fusion rule
  "status":        str,            # e.g. "Needs Purification"
  "recommendation":str,
  "reasons":       list[str],      # human-readable explanation lines
  "low_confidence":bool,           # confidence < 0.45
}
```

`api.py` adds one field for the web client: `"image_url": str` (absolute
`http://localhost:8000/images/<filename>`).

**Consumers to update if this schema changes:** `run.py`, `dashboard.py`,
`api.py`, `frontend/src/App.jsx`.

## Fusion rule (aqua/fusion.py)

```
score = 2 * organism_danger        # danger from config.ORGANISMS: 0 clean … 3 severe
      + 1 if pH outside 6.5–8.5
      + 1 if temperature > 30 °C
score <= 1 -> LOW    2–3 -> MODERATE    >= 4 -> HIGH
```
Organism danger + thresholds live in `aqua/config.py` (`ORGANISMS`,
`PH_SAFE_MIN/MAX`, `TEMP_WARM_C`). Edit rules there, not in front-ends.

## Input sources & their formats

1. **Mock pendrive (default demo).** Folder `data/pendrive/`:
   - `images/<sample_id>.png`
   - `readings.csv` columns: `sample_id, true_label, ph, temperature`
   - Generate: `python -m aqua.mock_data data/pendrive 3`
2. **Real pendrive.** Same layout; point any consumer at the folder.
   `true_label` optional.
3. **Arduino Uno over USB serial** (9600 baud). Emits one line/second:
   ```
   PH:7.24 TEMP:26.5
   ```
   Read via `aqua/serial_reader.py:read_from_serial(port, baud=9600)`.
4. **NodeMCU over Wi-Fi.** HTTP `GET http://<ip>/ph` returns:
   ```json
   {"ph": 7.24, "temperature": 26.5}
   ```
   Read via `aqua/serial_reader.py:read_from_nodemcu(url)`.

## How to run each piece

```bash
python run.py                       # CLI; --pendrive DIR | --image IMG --ph P --temp T
                                    #      --serial PORT | --nodemcu URL
streamlit run dashboard.py          # -> :8501
python api.py                       # -> :8000  (GET /api/results, static /images/<f>)
cd frontend && npm run dev          # -> :5173  (needs api.py running on :8000)
```
Windows one-click: `setup.bat` (once) then `start.bat`. Details in
`docs/WINDOWS_SETUP.md`.

## Swapping the prototype classifier for a real CNN

`aqua/classifier.py:classify()` returns the `{label, confidence, probs}` used by
the pipeline. To use a fine-tuned model, set env `AQUASENTINEL_MODEL=<path>` and
implement `_load_cnn()` / `_classify_cnn()` (same return shape). Full recipe:
`docs/UPGRADE_REAL_MODEL.md`. Nothing downstream changes.

Get real training/test images: `python download_images.py` (Wikimedia Commons,
saved to `data/real_samples/`, git-ignored, attributions recorded).

## Known issues to fix during integration (React front-end, from review)

- `frontend/src/index.css`: `.risk-MODERATE` and `.risk-HIGH` use the **same**
  background/text colour → the two risk levels are visually identical. Give
  MODERATE a distinct amber (e.g. `#8a5300` on `#fff4ce`).
- `frontend/src/App.jsx`: section headings use `style={{display:'none'}}` for
  "sr-only" — this hides them from screen readers too. Use a real visually-hidden
  class (`position:absolute;width:1px;height:1px;clip-path:inset(50%)`).
- Hero metrics omit the **MODERATE** count (only Total/Low/High shown).
- No skip-to-content link; no `prefers-reduced-motion` handling.
- `api.py` CORS: `allow_origins=["*"]` + `allow_credentials=True` is an invalid
  combo; drop credentials or list explicit origins.
- Hardcoded `http://localhost:8000` in `api.py` and `App.jsx`; no error-state UI
  if the API is unreachable (page silently renders empty).

## Ground rules

- `data/` is git-ignored and regenerated; never rely on committed sample data.
- Keep the result object stable; it is the integration seam.
- The prototype classifier is validated on synthetic data (self-consistent, not
  real-world accuracy). Say so; don't claim lab-grade accuracy.
