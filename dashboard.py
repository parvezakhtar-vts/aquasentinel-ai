#!/usr/bin/env python3
"""
AquaSentinel AI — Streamlit dashboard (the pretty demo screen).

Run with:
    pip install streamlit
    streamlit run dashboard.py

Optional. If you can't install Streamlit, use run.py instead -- same
results, plain terminal. Nothing here needs hardware or internet.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from aqua import mock_data, pipeline

DATA_DIR = Path(__file__).parent / "data" / "pendrive"
RISK_COLOR = {"LOW": "#16a34a", "MODERATE": "#d97706", "HIGH": "#dc2626"}

st.set_page_config(page_title="AquaSentinel AI", page_icon="💧", layout="wide")


def render_sample(r: dict):
    color = RISK_COLOR[r["risk"]]
    left, right = st.columns([1, 2])
    with left:
        if Path(r["image_path"]).exists():
            st.image(r["image_path"], caption=r["sample_id"], width="stretch")
    with right:
        st.markdown(
            f"<div style='background:{color};color:white;padding:10px 16px;"
            f"border-radius:8px;font-size:20px;font-weight:700'>"
            f"{r['risk']} RISK &nbsp;·&nbsp; {r['status']}</div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Detected organism", r["organism"])
        c2.metric("Confidence", f"{r['confidence'] * 100:.1f}%")
        c3.metric("Kind", r["kind"])
        c4, c5 = st.columns(2)
        c4.metric("pH", f"{r['ph']:.2f}" if r["ph"] is not None else "--")
        c5.metric("Temperature", f"{r['temperature']:.1f} °C" if r["temperature"] is not None else "--")
        st.info(r["recommendation"])
        with st.expander("Why this verdict? (image + pH + temperature)"):
            for reason in r["reasons"]:
                st.write("• " + reason)
            st.caption("Disease if untreated: " + r["disease"])
    st.divider()


ORGANISMS_DOC = [
    ("Clean water", "None", 0, "Clear field, few particles"),
    ("Algae", "Algae", 1, "Large green clusters"),
    ("Cyanobacteria", "Blue-green bacteria", 2, "Blue-green filaments / chains"),
    ("Giardia lamblia", "Protozoa", 2, "Tear-drop / oval cysts"),
    ("Cryptosporidium", "Protozoa", 2, "Small round oocysts"),
    ("E. coli", "Bacteria", 2, "Many small dark rods"),
    ("Naegleria fowleri", "Amoeba", 3, "Few large irregular bodies"),
]

PIPELINE_STEPS = [
    ("Capture the inputs",
     "Every sample is one microscope image plus two sensor readings — **pH** and "
     "**temperature**. They come from a mock pendrive (the demo default), manual entry, or "
     "live hardware (Arduino over USB, or a NodeMCU over Wi-Fi)."),
    ("Classify the organism (the image model)",
     "The classifier reads actual pixels — not a lookup table. It reduces each image to "
     "**8 numeric features** (mean colour, green dominance for chlorophyll, texture, edge "
     "density, and dark-pixel fraction at two scales to tell tiny rods from large blobs), then "
     "picks the nearest learned prototype per organism. A softmax over the distances gives the "
     "confidence and per-class probabilities."),
    ("Fuse image + sensors into a risk verdict",
     "A deliberately transparent rule combines the three signals so every verdict can be "
     "explained line by line. The image says *which* organism; the sensors say *how dangerous* "
     "the conditions are."),
    ("Assemble one result object",
     "The classification, organism metadata, raw pH/temperature, and the risk verdict are merged "
     "into a single result object. This one object is the contract every front-end renders — which "
     "is why the terminal, this dashboard, and the web app always agree."),
    ("Show it",
     "The result is rendered as the cards on the Dashboard: organism, confidence, pH, temperature, "
     "the risk badge, a recommendation, and the exact reasons behind the verdict."),
]


def render_docs():
    st.header("How AquaSentinel Works")
    st.write(
        "AquaSentinel screens a water sample for microbial contamination in seconds. Give it a "
        "microscope image of a water drop plus the water's pH and temperature, and it identifies "
        "the microorganism and reports a contamination risk — an early warning, not a lab replacement."
    )

    st.subheader("The pipeline at a glance")
    nodes = [
        ("🔬 Microscope image", "the drop of water"),
        ("🧠 Classifier", "which organism + confidence"),
        ("⚖️ Fusion", "+ pH & temperature → risk"),
        ("📊 Dashboard", "verdict + recommendation"),
    ]
    cols = st.columns(len(nodes))
    for col, (title, sub) in zip(cols, nodes):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(sub)

    st.subheader("Step by step")
    for i, (title, body) in enumerate(PIPELINE_STEPS, start=1):
        with st.container(border=True):
            st.markdown(f"**{i}. {title}**")
            st.markdown(body)
            if title.startswith("Classify"):
                st.markdown("It chooses from seven categories:")
                st.dataframe(
                    pd.DataFrame([
                        {"Organism": o, "Kind": k, "Danger (0-3)": d, "Look": look}
                        for o, k, d, look in ORGANISMS_DOC
                    ]),
                    hide_index=True, width="stretch",
                )
            if title.startswith("Fuse"):
                st.code(
                    "risk_score = 2 * organism_danger      (danger 0=clean ... 3=severe)\n"
                    "           + 1  if pH outside 6.5-8.5\n"
                    "           + 1  if temperature > 30 C\n\n"
                    "score <= 1  ->  LOW        2-3  ->  MODERATE        >= 4  ->  HIGH",
                    language="text",
                )

    st.subheader("What's real and what's simulated")
    st.markdown(
        "- **Real:** the classifier reads real pixels and makes a genuine prediction; the "
        "pH/temperature fusion logic is real.\n"
        "- **Simulated for the demo:** the microscope images and sensor readings are generated "
        "stand-ins, so the demo runs anywhere without hardware.\n"
        "- **Not claimed:** species-level certainty or a replacement for a laboratory. AquaSentinel "
        "is a screening and early-warning tool."
    )
    st.warning(
        "**Honest caveat.** The demo classifier is validated on images from the same generator it "
        "learned from, so the \"matches labels\" count reflects self-consistency on synthetic data "
        "— not real-world accuracy. The system is built so a real image dataset or a fine-tuned CNN "
        "drops in without changing anything downstream."
    )


def main():
    st.title("💧 AquaSentinel AI")
    st.caption("AI-assisted water biosurveillance — microscope image + pH + temperature → contamination risk")

    with st.sidebar:
        page = st.radio("Page", ["Dashboard", "How it works"])
        st.markdown("---")

    if page == "How it works":
        render_docs()
        return

    with st.sidebar:
        st.header("Input")
        mode = st.radio("Source", ["Mock pendrive (demo)", "Pendrive folder", "Single image"])
        st.markdown("---")
        st.caption("Prototype model: nearest-centroid over colour/texture features. "
                   "Upgrade to a fine-tuned CNN via docs/UPGRADE_REAL_MODEL.md.")

    results = []
    if mode == "Mock pendrive (demo)":
        if st.sidebar.button("Regenerate mock samples") or not (DATA_DIR / "readings.csv").exists():
            mock_data.generate_pendrive(DATA_DIR, per_class=3)
        results = pipeline.process_pendrive(DATA_DIR)

    elif mode == "Pendrive folder":
        folder = st.sidebar.text_input("Folder path", value=str(DATA_DIR))
        if folder and Path(folder).exists():
            results = pipeline.process_pendrive(folder)
        else:
            st.warning("Enter a valid folder containing images/ and readings.csv")

    else:  # Single image
        up = st.sidebar.file_uploader("Microscope image", type=["png", "jpg", "jpeg"])
        ph = st.sidebar.slider("pH", 0.0, 14.0, 7.2, 0.1)
        temp = st.sidebar.slider("Temperature (°C)", 5.0, 45.0, 25.0, 0.5)
        if up:
            img = Image.open(up)
            r = pipeline.process_sample(img_path_from_upload(img, up.name), ph=ph, temperature=temp)
            results = [r]

    if not results:
        st.stop()

    counts = {k: sum(1 for r in results if r["risk"] == k) for k in RISK_COLOR}
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Samples", len(results))
    m2.metric("🟢 Low", counts["LOW"])
    m3.metric("🟠 Moderate", counts["MODERATE"])
    m4.metric("🔴 High", counts["HIGH"])
    st.divider()

    for r in results:
        render_sample(r)

    df = pd.DataFrame([{
        "sample": r["sample_id"], "organism": r["organism"],
        "confidence": round(r["confidence"], 3), "pH": r["ph"],
        "temp_C": r["temperature"], "risk": r["risk"],
    } for r in results])
    st.subheader("Batch report")
    st.dataframe(df, width="stretch")
    st.download_button("Download report.csv", df.to_csv(index=False), "report.csv")


def img_path_from_upload(img: Image.Image, name: str) -> str:
    tmp = DATA_DIR.parent / "uploads"
    tmp.mkdir(parents=True, exist_ok=True)
    path = tmp / name
    img.save(path)
    return str(path)


if __name__ == "__main__":
    main()
