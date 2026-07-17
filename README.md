# 💧 AquaSentinel AI

**A smart water checker.** You give it a microscope photo of a water drop plus
the water's **pH** and **temperature**, and it tells you what tiny organism it
sees and whether the water looks **safe, risky, or unsafe** — in seconds.

It works right away on your computer with pretend ("mock") samples, so you do
**not** need any hardware or internet to try it.

---

## ▶️ Easiest way on Windows (no Python needed)

Your computer does **not** need Python or anything installed first — the setup
file does all of it for you.

1. **Once, the night before** (needs internet, ~5–15 min):
   double-click **`setup.bat`** and wait until it says **“Setup complete”**.
2. **On demo day:** double-click **`start.bat`** — the dashboard opens in your
   web browser automatically. 🎉 Keep that black window open during the demo.

**Backup plan:** if the browser version ever acts up at the table, double-click
**`start-terminal.bat`** for a plain-text version that always works.

See **`docs/WINDOWS_SETUP.md`** for step-by-step pictures-in-words.

---

## ▶️ If you already have Python (Mac / Linux / Windows)

Open a terminal **in this folder** and type:

```bash
python3 run.py            # plain terminal version (Windows: python run.py)
```

Want the pretty screen version?
```bash
pip install streamlit
streamlit run dashboard.py
```

> **Building on this, or an AI coding agent helping integrate the pieces?**
> Read **`AGENTS.md`** — it has the exact data contract, ports, sensor formats,
> model-swap hooks, and the known issues to fix.

---

## 🧠 What the folders mean

```
aquasentinel/
│
├─ run.py            ⭐ START HERE — the terminal demo
├─ dashboard.py         the pretty screen version (needs: pip install streamlit)
├─ requirements.txt     the list of things to install (optional extras)
│
├─ aqua/             🧠 the "brain" — all the AI code lives here
│   ├─ config.py         the list of organisms + safety rules (read this first!)
│   ├─ mock_data.py      makes the pretend water samples
│   ├─ classifier.py     looks at the photo and guesses the organism
│   ├─ fusion.py         mixes photo + pH + temperature into a risk level
│   ├─ pipeline.py       connects all the steps together
│   └─ serial_reader.py  (optional) reads a real Arduino / NodeMCU
│
├─ arduino/          🔌 the hardware code (Arduino + NodeMCU)
│   ├─ ph_sensor_uno/     Arduino Uno: reads pH + temperature
│   └─ nodemcu_wifi/      NodeMCU: sends the reading over Wi-Fi
│
├─ docs/             📄 the write-up for your project / judges
│   ├─ OVERVIEW.md           ⭐ read this to understand the project + pipeline
│   ├─ PROJECT_STATEMENT.md   how everything works (with diagrams)
│   ├─ DEMO_SCRIPT.md         what to say and click on demo day
│   └─ UPGRADE_REAL_MODEL.md  how to add a bigger AI model later
│
└─ data/            (created automatically — the example samples)
```

---

## 🖼️ Get real microscope images (optional)

Download real, freely-licensed microscope photos of each organism from
Wikimedia Commons (saved to `data/real_samples/<organism>/`, with credits in
`ATTRIBUTIONS.md`):
```bash
python3 download_images.py            # ~6 images per organism
python3 download_images.py --per 10   # more
```
These are for testing the classifier and for fine-tuning a real CNN later
(see `docs/UPGRADE_REAL_MODEL.md`). They are **not** committed to the repo.

## 🔬 Try other things

**One photo, with your own pH and temperature numbers:**
```bash
python3 run.py --image data/pendrive/images/sample_001.png --ph 5.9 --temp 32
```

**Use a real Arduino or NodeMCU (only if you have one):**
```bash
pip install pyserial
python3 run.py --image data/pendrive/images/sample_001.png --serial /dev/cu.usbmodem1101
python3 run.py --image data/pendrive/images/sample_001.png --nodemcu http://192.168.1.50/ph
```

---

## ⚖️ What's real and what's pretend (say this to judges)

- **Pretend:** the microscope photos and sensor numbers are *made up* to stand in
  for the real camera and sensors, so the demo always works.
- **Real:** the AI really looks at the photo's colours and shapes to decide, and
  the safety rules (pH + temperature) are real.
- **Honest limit:** it gives an early **warning**, it does **not** replace a real
  laboratory test.

Read `docs/DEMO_SCRIPT.md` for your demo-day plan and answers to judge questions.
