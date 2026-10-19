# CS 413 Affective Computing: Week 7 Facial Emotion Recognition on FER2013

Track B: face detection (MediaPipe, Haar fallback), frozen MobileNetV2 (ImageNet) features (1280 per image),
then `StandardScaler` + Logistic Regression / Linear SVM, evaluated on the FER2013 test split.

## Setup

```bash
pip install -r requirements.txt
# Linux only, for MediaPipe:
sudo apt-get install -y libegl1 libgles2
```

## Data

FER2013 (35,887 images) is included in `data/`:

```
data/train/{angry,disgust,fear,happy,sad,surprise,neutral}/*.png|jpg
data/test/{angry,disgust,fear,happy,sad,surprise,neutral}/*.png|jpg
```

## Run

Open `CS413_Week7_FER_Lab.ipynb` and choose Kernel > Restart & Run All.
For a quick run, set `SAMPLE_PER_CLASS` in the first code cell to a small number like `50`.

| Folder | Contents |
|---|---|
| `outputs/` | Figures and tables |
| `models/` | Best model (`fer_best_model.joblib`) |
| `features/` | Cached features (git-ignored) |
