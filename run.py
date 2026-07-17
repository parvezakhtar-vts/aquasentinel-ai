#!/usr/bin/env python3
"""
AquaSentinel AI — terminal dashboard (no extra installs needed).

Runs on just Python + Pillow + NumPy + Pandas, which are already present.
This is the safety-net demo: it always works, no Streamlit, no hardware.

Examples
--------
  # Auto-generate a mock pendrive and analyse the whole batch:
  python run.py

  # Analyse a real/other pendrive folder (images/ + readings.csv):
  python run.py --pendrive /Volumes/USB

  # Analyse a single microscope image with manual sensor values:
  python run.py --image sample.png --ph 5.9 --temp 32

  # Pull the pH live from the Arduino (USB) or NodeMCU (Wi-Fi):
  python run.py --image sample.png --serial /dev/cu.usbmodem1101
  python run.py --image sample.png --nodemcu http://192.168.1.50/ph
"""
from __future__ import annotations

import argparse
from pathlib import Path

from aqua import mock_data, pipeline, serial_reader

C = {
    "LOW": "\033[92m", "MODERATE": "\033[93m", "HIGH": "\033[91m",
    "dim": "\033[2m", "bold": "\033[1m", "reset": "\033[0m", "cyan": "\033[96m",
}


def card(r: dict) -> str:
    color = C.get(r["risk"], "")
    conf = f"{r['confidence'] * 100:.1f}%"
    ph = f"{r['ph']:.2f}" if r["ph"] is not None else "--"
    temp = f"{r['temperature']:.1f} C" if r["temperature"] is not None else "--"
    lines = [
        "=" * 45,
        f"{C['bold']}{C['cyan']}        Aqua Sentinel AI Dashboard{C['reset']}",
        "=" * 45,
        f"  Sample             : {r['sample_id']}",
        f"  pH Value           : {ph}",
        f"  Temperature        : {temp}",
        f"  Detected Organism  : {r['organism']}  ({r['kind']})",
        f"  Confidence         : {conf}",
        f"  Water Status       : {color}{C['bold']}{r['status']}{C['reset']}",
        f"  Risk Level         : {color}{C['bold']}{r['risk']}{C['reset']}  "
        f"{C['dim']}(score {r['score']}){C['reset']}",
        "-" * 45,
        f"  {C['bold']}Recommendation:{C['reset']} {r['recommendation']}",
        f"  {C['dim']}Why: " + " ".join(r["reasons"]) + C['reset'],
        "=" * 45,
    ]
    return "\n".join(lines)


def summary(results: list[dict]) -> str:
    counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0}
    for r in results:
        counts[r["risk"]] += 1
    graded = [r for r in results if r["correct"] is not None]
    acc = ""
    if graded:
        n_ok = sum(1 for r in graded if r["correct"])
        acc = f"   |   classifier check: {n_ok}/{len(graded)} match labels"
    return (f"\n{C['bold']}BATCH SUMMARY{C['reset']}  "
            f"({len(results)} samples){acc}\n"
            f"  {C['LOW']}LOW {counts['LOW']}{C['reset']}   "
            f"{C['MODERATE']}MODERATE {counts['MODERATE']}{C['reset']}   "
            f"{C['HIGH']}HIGH {counts['HIGH']}{C['reset']}")


def main():
    ap = argparse.ArgumentParser(description="AquaSentinel AI terminal dashboard")
    ap.add_argument("--pendrive", help="folder with images/ + readings.csv")
    ap.add_argument("--image", help="single microscope image")
    ap.add_argument("--ph", type=float, help="manual pH for --image")
    ap.add_argument("--temp", type=float, help="manual temperature (C) for --image")
    ap.add_argument("--serial", help="read live pH from Arduino USB port")
    ap.add_argument("--nodemcu", help="read live pH from NodeMCU JSON URL")
    args = ap.parse_args()

    if args.image:
        ph, temp = args.ph, args.temp
        if args.serial:
            live = serial_reader.read_from_serial(args.serial)
            ph, temp = live["ph"], live.get("temperature") or temp
        elif args.nodemcu:
            live = serial_reader.read_from_nodemcu(args.nodemcu)
            ph, temp = live["ph"], live.get("temperature") or temp
        r = pipeline.process_sample(args.image, ph=ph, temperature=temp)
        print(card(r))
        return

    pendrive = args.pendrive
    if not pendrive:
        default = Path(__file__).parent / "data" / "pendrive"
        if not (default / "readings.csv").exists():
            print(f"{C['dim']}No pendrive given - generating mock data...{C['reset']}")
            mock_data.generate_pendrive(default, per_class=3)
        pendrive = default

    results = pipeline.process_pendrive(pendrive)
    if not results:
        print("No images found in", pendrive)
        return
    for r in results:
        print(card(r))
    print(summary(results))


if __name__ == "__main__":
    main()
