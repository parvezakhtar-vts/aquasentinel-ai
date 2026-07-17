"""
AquaSentinel AI — domain configuration.

One place for the microorganism catalogue, the pH / temperature thresholds,
and the risk rules. Everything the classifier and the fusion layer need to
speak the same language lives here, so a judge (or a student) can read this
single file and understand what the system knows.
"""

# ---------------------------------------------------------------------------
# Microorganism catalogue
# ---------------------------------------------------------------------------
# `danger` is a 0-3 scale used by the fusion layer:
#   0 = harmless / clean, 1 = indicator only, 2 = disease-causing, 3 = severe.
# The visual `signature` fields are what the lightweight classifier matches on
# and what the mock-data generator draws, so detection and generation agree.

ORGANISMS = {
    "clean_water": {
        "label": "Clean water",
        "kind": "None",
        "disease": "None",
        "size": "-",
        "appearance": "Clear field, few or no particles",
        "danger": 0,
        "signature": {"base_rgb": (205, 225, 240), "blob": "none",
                      "blob_color": (180, 200, 220), "count": 0},
    },
    "algae": {
        "label": "Algae",
        "kind": "Algae",
        "disease": "Indicates stagnant / nutrient-rich water",
        "size": "10-100 um",
        "appearance": "Large green clusters",
        "danger": 1,
        "signature": {"base_rgb": (200, 220, 205), "blob": "cluster",
                      "blob_color": (60, 140, 70), "count": 8},
    },
    "cyanobacteria": {
        "label": "Cyanobacteria",
        "kind": "Photosynthetic bacteria (blue-green algae)",
        "disease": "Toxins: skin/liver/GI illness",
        "size": "1-10 um chains",
        "appearance": "Blue-green filaments and chains",
        "danger": 2,
        "signature": {"base_rgb": (200, 215, 210), "blob": "filament",
                      "blob_color": (30, 110, 120), "count": 14},
    },
    "giardia": {
        "label": "Giardia lamblia",
        "kind": "Protozoa",
        "disease": "Giardiasis",
        "size": "10-20 um",
        "appearance": "Tear-drop / oval cysts",
        "danger": 2,
        "signature": {"base_rgb": (222, 210, 200), "blob": "oval",
                      "blob_color": (120, 80, 90), "count": 10},
    },
    "cryptosporidium": {
        "label": "Cryptosporidium",
        "kind": "Protozoa",
        "disease": "Cryptosporidiosis",
        "size": "4-6 um",
        "appearance": "Small round oocysts, many",
        "danger": 2,
        "signature": {"base_rgb": (225, 215, 205), "blob": "round_small",
                      "blob_color": (150, 110, 90), "count": 26},
    },
    "ecoli": {
        "label": "E. coli",
        "kind": "Bacteria",
        "disease": "Diarrhoeal disease",
        "size": "1-2 um rods",
        "appearance": "Many small dark rods",
        "danger": 2,
        "signature": {"base_rgb": (228, 222, 210), "blob": "rod",
                      "blob_color": (70, 55, 60), "count": 34},
    },
    "naegleria": {
        "label": "Naegleria fowleri",
        "kind": "Amoeba",
        "disease": "Primary Amoebic Meningoencephalitis (brain-eating amoeba)",
        "size": "10-35 um",
        "appearance": "Few large irregular amoeboid bodies",
        "danger": 3,
        "signature": {"base_rgb": (218, 208, 210), "blob": "amoeba",
                      "blob_color": (110, 70, 95), "count": 4},
    },
}

CLASS_NAMES = list(ORGANISMS.keys())

# ---------------------------------------------------------------------------
# Sensor thresholds
# ---------------------------------------------------------------------------
PH_SAFE_MIN = 6.5
PH_SAFE_MAX = 8.5
# Warm, stagnant water accelerates microbial growth; Naegleria in particular
# thrives in warm water, which is why temperature feeds the fusion decision.
TEMP_WARM_C = 30.0

# ---------------------------------------------------------------------------
# Risk levels and the recommendation shown to the user
# ---------------------------------------------------------------------------
RISK = {
    "LOW": {
        "status": "Safe",
        "recommendation": "Water appears relatively safe. Continue monitoring.",
    },
    "MODERATE": {
        "status": "Needs Further Testing",
        "recommendation": "Potential contamination detected. Further laboratory testing recommended.",
    },
    "HIGH": {
        "status": "Needs Purification",
        "recommendation": "Possible microbial contamination. Avoid consumption. Purification and lab confirmation recommended.",
    },
}
