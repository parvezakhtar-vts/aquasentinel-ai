# Upgrade: swap the prototype classifier for a fine-tuned CNN

The POC ships a lightweight nearest-centroid classifier so it runs instantly.
When you want a "real" fine-tuned deep-learning model (for a bigger science
fair, or to classify actual microscope photos), follow this. Nothing else in
the system changes — `classifier.classify()` keeps the same return shape.

## 1. Get a real microbe image dataset

Two good public options:

- **Kaggle "Micro_Organism"** — 8 classes (Amoeba, Euglena, Hydra, Paramecium,
  Rod/Spherical/Spiral bacteria, Yeast). Easiest to start with.
  Needs a free Kaggle account + API token (`~/.kaggle/kaggle.json`):
  ```bash
  pip install kaggle
  kaggle datasets download -d <owner>/microorganism-image-classification
  ```
- **EMDS-6** — Environmental Microorganism Dataset, 840 images, 21 classes.
  The research-grade benchmark. Search "EMDS-6 dataset download".
  Paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8924496/

Map the dataset's classes onto the categories in `config.py` (bacteria,
protozoa, amoeba, algae/cyanobacteria, clean) so the risk rules keep working.

## 2. Fine-tune with transfer learning (Google Colab, free GPU)

Transfer learning on MobileNetV2 — ~20–40 min on a Colab GPU:

```python
import tensorflow as tf

IMG = 224
train = tf.keras.utils.image_dataset_from_directory(
    "dataset/train", image_size=(IMG, IMG), batch_size=32)
val = tf.keras.utils.image_dataset_from_directory(
    "dataset/val", image_size=(IMG, IMG), batch_size=32)
class_names = train.class_names

base = tf.keras.applications.MobileNetV2(
    input_shape=(IMG, IMG, 3), include_top=False, weights="imagenet")
base.trainable = False   # freeze; fine-tune top layers in a 2nd pass

model = tf.keras.Sequential([
    tf.keras.layers.Rescaling(1./127.5, offset=-1),
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(len(class_names), activation="softmax"),
])
model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train, validation_data=val, epochs=10)
model.save("aquasentinel_cnn.keras")
# also save class_names order to a json next to it
```

## 3. Wire it into the app

In `aquasentinel/classifier.py`, implement `_load_cnn()` and `_classify_cnn()`:

```python
import tensorflow as tf, numpy as np, json, os
from PIL import Image

_CNN = None
def _load_cnn():
    global _CNN
    if _CNN is None:
        path = os.environ["AQUASENTINEL_MODEL"]
        _CNN = (tf.keras.models.load_model(path),
                json.load(open(path + ".classes.json")))  # class order
    return _CNN

def _classify_cnn(image):
    model, classes = _load_cnn()
    img = (image if isinstance(image, Image.Image) else Image.open(image))
    img = img.convert("RGB").resize((224, 224))
    x = np.expand_dims(np.asarray(img, dtype="float32"), 0)
    probs = model.predict(x, verbose=0)[0]
    order = probs.argsort()[::-1]
    return {"label": classes[order[0]],
            "confidence": float(probs[order[0]]),
            "probs": {classes[i]: float(probs[i]) for i in order}}
```

Then run with the model path set:
```bash
pip install tensorflow
AQUASENTINEL_MODEL=aquasentinel_cnn.keras python3 run.py
```

## 4. (Optional) A real fusion meta-classifier

To make the pH/temperature fusion a trained model instead of rules, collect a
small table of `[class probs..., pH, temperature] -> risk` rows and fit a
`sklearn` `LogisticRegression` or `RandomForestClassifier`, then replace
`fusion.assess()` with a call to it. The rule-based version is a fine default
and is easier to explain to judges.
