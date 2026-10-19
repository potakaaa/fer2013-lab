# CS 413 Affective Computing — Week 7: Facial Emotion Recognition on FER2013

Track B: face detection (MediaPipe, Haar fallback) → frozen MobileNetV2 (ImageNet) 1280-d embeddings →
`StandardScaler` → Logistic Regression / Linear SVM, evaluated on the FER2013 test split.

## Setup

```bash
pip install -r requirements.txt
# Linux only, for MediaPipe:
sudo apt-get install -y libegl1 libgles2
```

## Data

FER2013 is not included in this repository. Place it as:

```
data/train/{angry,disgust,fear,happy,sad,surprise,neutral}/*.png|jpg
data/test/{angry,disgust,fear,happy,sad,surprise,neutral}/*.png|jpg
```

## Run

Open `CS413_Week7_FER_Lab.ipynb` and choose *Kernel → Restart & Run All*.
Set `SAMPLE_PER_CLASS` in the first code cell to a small number (e.g. `50`) for a quick run.

| Folder | Contents |
|---|---|
| `outputs/` | Figures and tables for the report |
| `models/` | Best model (`fer_best_model.joblib`) |
| `features/` | Cached embeddings (git-ignored) |
