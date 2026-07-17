"""
Sensor fusion / ensemble decision layer.

This is the "combine the AI with the thermal and pH sensors" step. It is a
decision-level (late) fusion: the image classifier votes with a microorganism
class, the pH and temperature sensors add context, and a small transparent
score turns all three into a single risk verdict.

Kept as explicit rules on purpose -- a student can read and defend every line
to a judge. The score is:

    score = 2 * organism_danger        (0..6)
          + 1 if pH is outside 6.5-8.5
          + 1 if temperature > 30 C

    score <= 1 -> LOW      2-3 -> MODERATE      >= 4 -> HIGH

To upgrade to a trained meta-classifier later, replace `assess()` with a model
that takes [class probabilities..., pH, temperature] -> risk; the return shape
stays the same.
"""
from __future__ import annotations

from . import config


def assess(classification: dict, ph: float | None, temperature: float | None) -> dict:
    label = classification["label"]
    org = config.ORGANISMS[label]
    danger = org["danger"]

    reasons = []
    score = 2 * danger
    if danger == 0:
        reasons.append("No microorganisms detected in the image.")
    else:
        reasons.append(f"Detected {org['label']} ({org['kind']}), a "
                       f"{'severe ' if danger == 3 else ''}risk organism.")

    ph_abnormal = ph is not None and not (config.PH_SAFE_MIN <= ph <= config.PH_SAFE_MAX)
    if ph_abnormal:
        score += 1
        reasons.append(f"pH {ph:.2f} is outside the safe range "
                       f"{config.PH_SAFE_MIN}-{config.PH_SAFE_MAX}.")
    elif ph is not None:
        reasons.append(f"pH {ph:.2f} is within the safe range.")

    temp_warm = temperature is not None and temperature > config.TEMP_WARM_C
    if temp_warm:
        score += 1
        reasons.append(f"Temperature {temperature:.1f} C is warm "
                       f"(>{config.TEMP_WARM_C:.0f} C), favouring microbial growth.")
    elif temperature is not None:
        reasons.append(f"Temperature {temperature:.1f} C is normal.")

    if score <= 1:
        risk = "LOW"
    elif score <= 3:
        risk = "MODERATE"
    else:
        risk = "HIGH"

    low_confidence = classification["confidence"] < 0.45
    if low_confidence:
        reasons.append("Image confidence is low - manual review advised.")

    return {
        "risk": risk,
        "score": int(score),
        "status": config.RISK[risk]["status"],
        "recommendation": config.RISK[risk]["recommendation"],
        "reasons": reasons,
        "low_confidence": low_confidence,
    }
