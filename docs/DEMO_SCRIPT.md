# Demo-day script — AquaSentinel AI

A 2-minute walkthrough anyone can run and explain. Practice it twice.

## Before the demo (one time)
Open a terminal in the `aquasentinel/` folder and run:
```bash
python3 run.py           # confirms it works + creates the mock samples
```
If you want the pretty screen: `pip install streamlit && streamlit run dashboard.py`.

## The 90-second story

1. **The problem (say it):** "Water can look clean but still carry harmful
   microbes. Lab tests take hours or days. AquaSentinel gives an early warning
   in seconds by combining a microscope image with pH and temperature sensors."

2. **Show a clean sample.** Point to a LOW result: organism = *Clean water*,
   pH normal, temperature normal → **Status: Safe.**

3. **Show a contaminated sample** (e.g. E. coli or Naegleria). The card flips to
   **HIGH RISK → Needs Purification.** Read the "Why" line — it names the
   organism *and* the pH/temperature that pushed the risk up.

4. **Explain the fusion (the clever bit):** "The AI classifies the organism from
   the image. Then it combines that with the pH and temperature sensors — this
   is sensor fusion. For example, a warm temperature with an amoeba is more
   dangerous than either alone, because *Naegleria* thrives in warm water."

5. **Close:** "The goal is early awareness instead of a late response — an
   affordable screening tool that tells you when to get a proper lab test."

## Answers to judge questions (from the project notes)

- **Can it replace a laboratory?** No. It's an early-warning screening tool that
  *recommends* lab testing. It never claims certainty.
- **Why only broad categories?** Broad classification (bacteria / protozoa /
  amoeba / algae) is reliable for a prototype and still useful for a warning.
- **Why AI?** It spots visual patterns in microscope images far faster than the
  human eye and works consistently.
- **Why pH and temperature?** They're cheap sensors that add context. Abnormal
  pH or warm, stagnant water raises the contamination risk.
- **Is the model real?** Yes — it reads the image's colour and texture and picks
  the closest learned prototype. It's a lightweight version; the same system
  accepts a fine-tuned CNN (show `docs/UPGRADE_REAL_MODEL.md`).
- **What's simulated?** The pendrive images and sensor CSV are generated stand-ins
  for the real capture hardware. The AI and the risk logic are real.

## If something goes wrong
- Streamlit won't start → use `python3 run.py` (no installs needed).
- Hardware not detected → the demo already runs on mock data; just don't pass
  `--serial`/`--nodemcu`.
- "No samples" → run `python3 -m aqua.mock_data data/pendrive`.
