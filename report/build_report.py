"""Build the Week 7 lab report PDF from the notebook outputs.

Run from the repository root after executing the notebook:
    python report/build_report.py

Tables are read from outputs/*.csv and figures from outputs/*.png, so they always match the last notebook run.
The prose quotes numbers from the full-dataset run (SAMPLE_PER_CLASS = None); update it if you re-run with
different settings.
"""
from pathlib import Path

import matplotlib
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
PDF_PATH = ROOT / "report" / "CS413_Week7_FER_Report.pdf"
REPO_URL = "https://github.com/potakaaa/fer2013-lab"

# Values printed by the notebook (sections 2.2, 2.3, 3.3) that are not saved to a CSV.
RUN = {
    "extract_seconds": 443,
    "fallback": {"train": (357, 28709), "test": (83, 7178)},
    "iterations": {"Logistic Regression": (611, 2000), "Linear SVM": (2326, 5000)},
    "model_kb": 68,
}

# ── Fonts (DejaVu ships with matplotlib, which the notebook already requires) ──────────────────────────────
FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
for name, file in [("Serif", "DejaVuSerif.ttf"), ("Serif-Bold", "DejaVuSerif-Bold.ttf"),
                   ("Serif-Italic", "DejaVuSerif-Italic.ttf"), ("Sans", "DejaVuSans.ttf"),
                   ("Sans-Bold", "DejaVuSans-Bold.ttf"), ("Sans-Oblique", "DejaVuSans-Oblique.ttf"),
                   ("Mono", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic",
                              boldItalic="Serif-Bold")
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Oblique",
                              boldItalic="Sans-Bold")

INK, MUTED, RULE, HEAD_BG = (colors.HexColor(c) for c in ("#0b0b0b", "#52514e", "#c3c2b7", "#f0efec"))

STYLES = {
    "title": ParagraphStyle("title", fontName="Sans-Bold", fontSize=17, leading=22, textColor=INK, spaceAfter=4),
    "subtitle": ParagraphStyle("subtitle", fontName="Sans", fontSize=11.5, leading=15, textColor=MUTED,
                               spaceAfter=10),
    "meta": ParagraphStyle("meta", fontName="Sans", fontSize=9, leading=13, textColor=MUTED),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=13, leading=17, textColor=INK, spaceBefore=12,
                         spaceAfter=5, keepWithNext=True),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=10.5, leading=14, textColor=INK, spaceBefore=8,
                         spaceAfter=3, keepWithNext=True),
    "body": ParagraphStyle("body", fontName="Serif", fontSize=9.6, leading=14, textColor=INK, spaceAfter=6),
    "bullet": ParagraphStyle("bullet", fontName="Serif", fontSize=9.6, leading=14, textColor=INK, leftIndent=12,
                             bulletIndent=2, spaceAfter=3),
    "abstract": ParagraphStyle("abstract", fontName="Serif-Italic", fontSize=9.4, leading=13.5, textColor=INK,
                               leftIndent=8 * mm, rightIndent=8 * mm, spaceAfter=8),
    "caption": ParagraphStyle("caption", fontName="Sans", fontSize=8.2, leading=11, textColor=MUTED,
                              alignment=TA_CENTER, spaceBefore=3, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="Sans", fontSize=8.2, leading=10.5, textColor=INK),
    "ref": ParagraphStyle("ref", fontName="Serif", fontSize=8.8, leading=12.5, textColor=INK, leftIndent=12,
                          firstLineIndent=-12, spaceAfter=4),
}
TEXT_WIDTH = A4[0] - 40 * mm


def code(text):
    return f'<font face="Mono" size="8.6">{text}</font>'


def p(text, style="body"):
    return Paragraph(text, STYLES[style])


def bullets(items):
    return [Paragraph(item, STYLES["bullet"], bulletText="•") for item in items]


def figure(png, caption, width_frac=1.0):
    """Image scaled to a fraction of the text width (aspect ratio kept) plus caption, kept on one page."""
    path = OUT / png
    w_px, h_px = ImageReader(str(path)).getSize()
    width = TEXT_WIDTH * width_frac
    return KeepTogether([Image(str(path), width=width, height=width * h_px / w_px), p(caption, "caption")])


def table(rows, caption, col_widths=None, bold_cells=()):
    """rows[0] is the header. bold_cells: (row, col) pairs to emphasise (row index includes the header)."""
    data = [[Paragraph(f"<b>{c}</b>" if (r == 0 or (r, j) in bold_cells) else str(c), STYLES["cell"])
             for j, c in enumerate(row)] for r, row in enumerate(rows)]
    t = Table(data, colWidths=col_widths, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return KeepTogether([p(caption, "caption"), t, Spacer(1, 8)])


def f3(x):
    return f"{float(x):.3f}"


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 12 * mm, "CS 413 Affective Computing · Week 7 Lab · FER2013 (Track B)")
    canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, f"{doc.page}")
    canvas.restoreState()


# ── Data from the notebook outputs ─────────────────────────────────────────────────────────────────────────
counts = pd.read_csv(OUT / "class_counts.csv", index_col=0)
det = pd.read_csv(OUT / "m1_detection_rate.csv", index_col=0)
labels = pd.read_csv(OUT / "label_encoding.csv", index_col=0)
cw = pd.read_csv(OUT / "class_weight_selection.csv", keep_default_na=False)
cmp_ = pd.read_csv(OUT / "model_comparison.csv", index_col=0)
per_class = pd.read_csv(OUT / "per_class_metrics.csv", header=[0, 1], index_col=0)
confusions = pd.read_csv(OUT / "top_confusions.csv")
MODELS = list(cmp_.index)
BEST = cmp_["macro_f1"].idxmax()
# The CSV rounds to 4 decimals; with 7,178 test images that still pins down the exact number of correct
# predictions, so recover the exact accuracy to avoid double rounding (e.g. 0.49053 → 0.4905 → "49.0%").
_n_test = int(counts.loc["TOTAL", "test"])
cmp_["accuracy"] = (cmp_["accuracy"] * _n_test).round() / _n_test

story = []

# ── Title ─────────────────────────────────────────────────────────────────────────────────────────────────
story += [
    p("Facial Emotion Recognition on FER2013 with Frozen CNN Features", "title"),
    p("CS 413 Affective Computing · Week 7 Lab Report · Track B (deep features + classical classifiers)",
      "subtitle"),
    p("Team: [Member 1], [Member 2], [Member 3], [Member 4]  ·  Date: [submission date]", "meta"),
    p(f"Code and outputs: {REPO_URL}", "meta"),
    Spacer(1, 10),
    p("<b>Abstract.</b> We build a facial emotion recognition pipeline that combines MediaPipe face detection, "
      "a frozen ImageNet MobileNetV2 feature extractor and two linear classifiers, and evaluate it on the "
      f"7,178-image FER2013 test set. Logistic Regression reaches {cmp_.loc['Logistic Regression', 'accuracy']:.1%} "
      f"accuracy and {f3(cmp_.loc['Logistic Regression', 'macro_f1'])} macro-F1; a Linear SVM reaches "
      f"{cmp_.loc['Linear SVM', 'accuracy']:.1%} and {f3(cmp_.loc['Linear SVM', 'macro_f1'])}. Happy and surprise "
      "are recognised reliably, while disgust, fear and sad remain difficult and are mostly confused with each "
      "other and with neutral.", "abstract"),
]

# ── 1. Introduction ───────────────────────────────────────────────────────────────────────────────────────
story += [
    p("1  Introduction", "h1"),
    p("Facial emotion recognition (FER) maps a face image to an emotion category and is a core task in affective "
      "computing. In this lab we follow Track B: instead of training a network end to end, we use a pretrained "
      "convolutional network as a fixed feature extractor and train classical classifiers on its embeddings. This "
      "keeps training cheap and shows how far generic ImageNet features carry on a facial-expression task. We "
      "compare Logistic Regression with a linear Support Vector Machine (SVM) on FER2013 and wrap the better model "
      "in a small prediction function."),
]

# ── 2. Dataset ────────────────────────────────────────────────────────────────────────────────────────────
n_train, n_test = int(counts.loc["TOTAL", "train"]), int(counts.loc["TOTAL", "test"])
happy_pct = counts.loc["happy", "train %"]
disgust_n, disgust_pct = int(counts.loc["disgust", "train"]), counts.loc["disgust", "train %"]
story += [
    p("2  Dataset", "h1"),
    p(f"FER2013 (Goodfellow et al., 2013) contains {n_train + n_test:,} grayscale face images of 48×48 pixels, "
      "collected through web image search and labelled with one of seven emotions. We use the standard split: the "
      f"{n_train:,} <i>Training</i> images for training and the {n_test:,} <i>PublicTest</i> and <i>PrivateTest</i> "
      "images as the test set. The faces are already roughly centred and cropped. Table 1 and Figure 1 show the "
      f"class distribution. The data is strongly imbalanced: <i>happy</i> makes up {happy_pct:.1f}% of the training "
      f"set, while <i>disgust</i> has only {disgust_n} images ({disgust_pct:.1f}%). We therefore use macro-averaged "
      "F1, which weights all seven classes equally, as the main metric."),
    table([["Class", "Train", "Test", "Total", "Train %"]] +
          [[c, f"{int(r.train):,}", f"{int(r.test):,}", f"{int(r.total):,}", f"{r['train %']:.1f}"]
           for c, r in counts.iterrows()],
          "Table 1. Images per class and split (outputs/class_counts.csv).",
          col_widths=[30 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm],
          bold_cells={(len(counts), j) for j in range(5)}),
    figure("class_distribution.png", "Figure 1. Class distribution per split.", 0.9),
    figure("sample_grid.png", "Figure 2. Random training images per class (seed 42).", 0.55),
]

# ── 3. Method ─────────────────────────────────────────────────────────────────────────────────────────────
det_total = det.loc["TOTAL"]
story += [
    p("3  Method", "h1"),
    p("3.1  Face detection (Milestone 1)", "h2"),
    p("Face detectors are trained on photos with some background around the face, so they often fail on "
      "FER2013's tiny, tightly cropped images. Each image is therefore upscaled 4× to 192×192 pixels (bicubic) and "
      "surrounded by a black border of 25% of its size before detection, so that the face no longer touches the "
      "image edge. We use MediaPipe's BlazeFace short-range detector (Bazarevsky et al., 2019) through the Tasks API "
      "with a minimum confidence of 0.5; if MediaPipe cannot be loaded, the code falls back to OpenCV's Haar "
      f"cascade (Viola and Jones, 2001). The reusable function {code('detect_and_crop(img)')} crops the largest "
      "detected face with 10% padding; if no face is found it returns the full image and the fallback is counted."),
    p(f"On a seeded sample of 200 training images per class, a face was found in {det_total['detection rate %']:.1f}% "
      f"of images (Table 2). The border matters: on the same sample the detection rate was 92.6% without it, and "
      "wider borders gave no further gain. Figure 3 shows detections and the crops passed to the CNN."),
    table([["Class", "Sampled", "Face found", "Fallback", "Rate %"]] +
          [[c, f"{int(r['sampled']):,}", f"{int(r['face found']):,}", f"{int(r['fallback (full image)']):,}",
            f"{r['detection rate %']:.1f}"] for c, r in det.iterrows()],
          "Table 2. Detection rate on a sample of the training set (outputs/m1_detection_rate.csv).",
          col_widths=[30 * mm, 22 * mm, 24 * mm, 22 * mm, 20 * mm],
          bold_cells={(len(det), j) for j in range(5)}),
    figure("m1_face_detection_grid.png", "Figure 3. Detected faces (green box) and the resulting crops, three random "
           "training images per class.", 0.66),
]

fb_tr, fb_te = RUN["fallback"]["train"], RUN["fallback"]["test"]
story += [
    p("3.2  Feature extraction (Milestone 2)", "h2"),
    p("Every image goes through the same pipeline: load as grayscale → " + code("detect_and_crop") + " → resize to "
      "224×224 → replicate to three channels → " + code("mobilenet_v2.preprocess_input") + " → MobileNetV2. We use "
      "MobileNetV2 (Sandler et al., 2018) with ImageNet weights, " + code("include_top=False") + " and global "
      "average pooling, which yields a 1280-dimensional embedding per image. The network is frozen; none of its "
      "2,257,984 parameters are trained. Images are processed in batches of 64, and the embeddings are cached to "
      "disk together with the configuration and file list, so re-running the notebook skips this step. Extracting "
      f"all {n_train + n_test:,} images took {RUN['extract_seconds']} s on a 4-core CPU. Table 3 verifies the "
      "resulting feature matrices; the label encoding follows the FER2013 convention " +
      ", ".join(f"{i} = {r['class']}" for i, r in labels.iterrows()) + "."),
    table([["Split", "Images", "X shape", "y shape", "No-face fallback"],
           ["train", f"{fb_tr[1]:,}", f"({fb_tr[1]}, 1280)", f"({fb_tr[1]},)",
            f"{fb_tr[0]} ({fb_tr[0] / fb_tr[1]:.1%})"],
           ["test", f"{fb_te[1]:,}", f"({fb_te[1]}, 1280)", f"({fb_te[1]},)",
            f"{fb_te[0]} ({fb_te[0] / fb_te[1]:.1%})"]],
          "Table 3. Train–test split verification (notebook section 2.3). Train and test files do not overlap.",
          col_widths=[18 * mm, 20 * mm, 30 * mm, 24 * mm, 34 * mm]),
]

lr_it, svm_it = RUN["iterations"]["Logistic Regression"], RUN["iterations"]["Linear SVM"]
w_disgust = n_train / (7 * disgust_n)
w_happy = n_train / (7 * counts.loc["happy", "train"])
story += [
    p("3.3  Classifiers", "h2"),
    p("Both classifiers are scikit-learn pipelines whose first step is a " + code("StandardScaler") + ", so the "
      "scaling statistics are learned from the training data only. Model 1 is multinomial Logistic Regression "
      "(L-BFGS, C = 1, " + code("max_iter=2000") + "). Model 2 is " + code("LinearSVC") + " (squared hinge loss, "
      "one-vs-rest, C = 1, " + code("max_iter=5000") + "). We use " + code("LinearSVC") + " rather than "
      + code("SVC(kernel='linear')") + " because kernel SVC scales roughly quadratically with the number of samples, "
      f"which is impractical for {n_train:,} training images. All random seeds are fixed to 42."),
    p("To handle the class imbalance we compared " + code("class_weight=None") + " and " + code("'balanced'") +
      f" (which here weights a disgust sample about {w_disgust / w_happy:.1f} times more than a happy sample) on a "
      "stratified 15% validation split of the training set. The test set was not used for any model choice. "
      "Table 4 shows that <i>balanced</i> won for both models, but only by a small margin. The chosen configuration "
      f"was then refitted on the full training set: Logistic Regression converged after {lr_it[0]} of {lr_it[1]} "
      f"iterations in {cmp_.loc['Logistic Regression', 'train_time_s']:.0f} s, the SVM after {svm_it[0]:,} of "
      f"{svm_it[1]:,} iterations in {cmp_.loc['Linear SVM', 'train_time_s']:.0f} s."),
    table([["Model", "class_weight", "Val. accuracy", "Val. macro-F1", "Selected"]] +
          [[r["model"], r["class_weight"], f3(r["val accuracy"]), f"{r['val macro-F1']:.4f}", r["selected"]]
           for _, r in cw.iterrows()],
          "Table 4. Class-weight selection on the validation split (outputs/class_weight_selection.csv).",
          col_widths=[38 * mm, 26 * mm, 26 * mm, 26 * mm, 18 * mm],
          bold_cells={(i + 1, 4) for i in range(len(cw))}),
]

# ── 4. Results ────────────────────────────────────────────────────────────────────────────────────────────
lr, svm = cmp_.loc["Logistic Regression"], cmp_.loc["Linear SVM"]
happy_test = int(counts.loc["happy", "test"])
best_col = {m: cmp_[m].astype(float).idxmax() for m in ["accuracy", "macro_precision", "macro_recall", "macro_f1"]}
story += [
    p("4  Results (Milestone 3)", "h1"),
    p("4.1  Overall performance", "h2"),
    p(f"Table 5 and Figure 4 compare the two models on the test set. They are almost indistinguishable: Logistic "
      f"Regression is ahead on macro-F1 ({f3(lr.macro_f1)} vs {f3(svm.macro_f1)}) and macro recall, while the SVM "
      f"is ahead on accuracy ({svm.accuracy:.1%} vs {lr.accuracy:.1%}). Because macro-F1 is our selection "
      f"criterion, <b>{BEST}</b> is the best model. It also trains about "
      f"{svm.train_time_s / lr.train_time_s:.0f} times faster and outputs class probabilities, which the deployment "
      f"function uses as a confidence score. For context, always predicting <i>happy</i> would give "
      f"{happy_test / n_test:.1%} accuracy on this test set, and human accuracy on FER2013 is about 65% "
      "(Goodfellow et al., 2013)."),
    table([["Model", "Accuracy", "Macro precision", "Macro recall", "Macro-F1", "Train time"]] +
          [[m, f3(r.accuracy), f3(r.macro_precision), f3(r.macro_recall), f3(r.macro_f1), f"{r.train_time_s:.0f} s"]
           for m, r in cmp_.iterrows()],
          "Table 5. Test-set performance (outputs/model_comparison.csv). Bold marks the better model per metric.",
          col_widths=[36 * mm, 21 * mm, 28 * mm, 25 * mm, 21 * mm, 21 * mm],
          bold_cells={(MODELS.index(m) + 1, j + 1) for j, m in enumerate(best_col.values())}),
    figure("model_comparison.png", "Figure 4. Test-set accuracy and macro-averaged precision, recall and F1.", 0.8),
]

pc_rows = [["Class"] + [f"{m.split()[0][:3]}. {k}" for m in MODELS for k in ("P", "R", "F1")] + ["Support"]]
for c, r in per_class.iterrows():
    pc_rows.append([c] + [f3(r[(m, k)]) for m in MODELS for k in ("precision", "recall", "f1")]
                   + [int(r.iloc[-1])])
lr_f1 = per_class[("Logistic Regression", "f1")]
svm_f1 = per_class[("Linear SVM", "f1")]
story += [
    p("4.2  Per-class results", "h2"),
    p(f"Table 6 lists precision, recall and F1 per class. <i>Happy</i> (F1 {f3(lr_f1['happy'])} / {f3(svm_f1['happy'])}) "
      f"and <i>surprise</i> ({f3(lr_f1['surprise'])} / {f3(svm_f1['surprise'])}) are recognised best: a smile, or a "
      "wide-open mouth with raised eyebrows, is a large visual change that survives at 48×48 pixels. <i>Disgust</i> "
      f"({f3(lr_f1['disgust'])} / {f3(svm_f1['disgust'])}) and <i>fear</i> ({f3(lr_f1['fear'])} / "
      f"{f3(svm_f1['fear'])}) are the hardest classes. The per-class F1 scores of the two models differ by at most "
      f"{(lr_f1 - svm_f1).abs().max():.3f}. The full classification reports are in notebook sections 4.1 and 4.2."),
    table(pc_rows, "Table 6. Per-class test metrics (Log. = Logistic Regression, Lin. = Linear SVM; "
                   "outputs/per_class_metrics.csv).",
          col_widths=[22 * mm] + [17 * mm] * 6 + [17 * mm]),
]

conf = confusions.copy()
story += [
    p("4.3  Confusion matrices", "h2"),
    p(f"Figure 5 shows the confusion matrix of {BEST} as counts and row-normalised (recall); the SVM's matrix "
      "(Appendix A) has the same structure. Table 7 lists the five largest off-diagonal entries. Most errors stay "
      "within a group of lower-intensity negative expressions: " +
      "; ".join(f"{r['true']} is predicted as {r['predicted as']} for {r['count']} images "
                f"({r['share of true class']:.0%} of {r['true']})" for _, r in conf.head(4).iterrows()) +
      ". Fear is the most scattered class: its errors spread over sad (17%), angry (14%), surprise (13%) and "
      "neutral (13%), and it shares wide eyes and raised brows with surprise."),
    figure("confusion_matrix_logistic_regression.png",
           f"Figure 5. Confusion matrix of {BEST} on the test set: counts (left) and row-normalised (right).", 1.0),
    table([["True class", "Predicted as", "Count", "Share of true class"]] +
          [[r["true"], r["predicted as"], int(r["count"]), f"{r['share of true class']:.1%}"]
           for _, r in conf.iterrows()],
          f"Table 7. Most common confusions of {BEST} (outputs/top_confusions.csv).",
          col_widths=[30 * mm, 30 * mm, 20 * mm, 34 * mm]),
]

story += [
    p("4.4  Error analysis", "h2"),
    p("Figure 6 shows five misclassified test images, one per true class. Several are hard even for a person: an "
      "exaggerated, statue-like grin labelled happy; a fearful face partly covered by a text watermark; an extreme "
      "close-up of a child that shows little more than the eyes; a crying infant labelled sad but predicted neutral; "
      "and a frown with a wrinkled nose labelled disgust but predicted angry, two cues the classes share. Four of the "
      "five predictions have a confidence below 0.5, so the model is visibly unsure on these cases."),
    figure("misclassified_examples.png", f"Figure 6. Misclassified test images ({BEST}): true label, predicted "
           "label and confidence.", 1.0),
]

# ── 5. Discussion ─────────────────────────────────────────────────────────────────────────────────────────
story += [
    p("5  Discussion", "h1"),
    p("5.1  Key insights", "h2"),
    *bullets([
        "<b>The two classifiers are effectively tied.</b> Both are linear models on the same standardised "
        "embeddings, so they learn very similar decision boundaries. Logistic Regression is preferred because it "
        "wins on macro-F1, trains about nine times faster and produces probabilities.",
        "<b>Expression intensity drives difficulty.</b> Classes with large, distinctive facial changes (happy, "
        "surprise) are recognised well; subtle negative expressions (sad, fear, angry) and neutral absorb most of "
        "the errors.",
        f"<b>Disgust is often found but rarely predicted correctly.</b> With balanced class weights its recall is "
        f"{f3(per_class.loc['disgust', ('Logistic Regression', 'recall')])}, yet only 53 of the 267 disgust "
        f"predictions are correct (precision {f3(per_class.loc['disgust', ('Logistic Regression', 'precision')])}), "
        "and 24% of true disgust faces are labelled angry.",
        "<b>Class weighting barely matters here.</b> On the validation split, <i>balanced</i> improved macro-F1 by "
        "only 0.0015 (Logistic Regression) and 0.0001 (SVM).",
        f"<b>Face detection is not the bottleneck.</b> Faces were found in {det_total['detection rate %']:.1f}% of "
        "sampled training images and only 1.2% of each split fell back to the full frame, so the remaining error "
        "comes from the features and the labels rather than from cropping.",
    ]),
    p("5.2  Limitations", "h2"),
    *bullets([
        "The features are frozen and come from ImageNet object classification, not faces. The 48×48 images are "
        "also upscaled more than four times to 224×224, so the network mostly sees interpolated pixels.",
        "FER2013 labels are noisy; human accuracy is only about 65% (Goodfellow et al., 2013), which caps what any "
        "model can reach on this test set.",
        "Only linear classifiers were evaluated, on a single train/test split with one seed, so no confidence "
        "intervals are reported.",
        "For the SVM, the confidence is a softmax over decision scores rather than a calibrated probability. This "
        "does not affect the deployed model, which is Logistic Regression.",
    ]),
    p("5.3  Possible improvements", "h2"),
    *bullets([
        "Fine-tune the CNN end to end with data augmentation (flips, small rotations and crops). Fine-tuned "
        "networks reach about 73% on FER2013 (Khaireddin and Chen, 2021).",
        "Train on the FER+ relabelled annotations (Barsoum et al., 2016) to reduce label noise.",
        "Try a non-linear classifier, such as a small multilayer perceptron, on the same embeddings.",
    ]),
]

# ── 6. Deployment ─────────────────────────────────────────────────────────────────────────────────────────
story += [
    p("6  Deployment", "h1"),
    p("The function " + code("predict_emotion(image_path) -> (label, confidence)") + " reuses exactly the functions "
      "that produced the training features (" + code("load_gray") + " → " + code("preprocess_for_cnn") + " → "
      + code("embed") + ") and the saved scikit-learn pipeline (scaler and classifier), loaded from "
      + code("models/fer_best_model.joblib") + f" ({RUN['model_kb']} KB). Figure 7 shows it on four random test "
      "images: two are correct (neutral 0.57, happy 0.92), which is in line with the test accuracy of about 49%. "
      "For all four images the prediction matches the batch evaluation, which confirms that deployment and training "
      "use identical preprocessing."),
    figure("deployment_demo.png", "Figure 7. predict_emotion() on four unseen test images: file name, predicted "
           "label with confidence, and true label.", 1.0),
]

# ── 7. Conclusion ─────────────────────────────────────────────────────────────────────────────────────────
story += [
    p("7  Conclusion", "h1"),
    p("A frozen MobileNetV2 with a linear classifier reaches about 49% accuracy and 0.45 macro-F1 on FER2013, about "
      "twice the majority-class baseline but well below human performance. Logistic Regression and a Linear SVM "
      "perform almost identically, and Logistic Regression is the better practical choice. Face detection on "
      "upscaled images works reliably, so further gains will come from learning face-specific features, for "
      "example by fine-tuning the network, rather than from changing the classifier on top of fixed features."),
]

# ── 8. Team contributions ─────────────────────────────────────────────────────────────────────────────────
story += [
    p("8  Team contributions", "h1"),
    table([["Member", "Role", "Contributions"],
           ["[Member 1]", "Data & preprocessing lead", "Dataset checks, face detection (Milestone 1)"],
           ["[Member 2]", "Feature extraction lead", "MobileNetV2 embeddings, feature cache (Milestone 2)"],
           ["[Member 3]", "Modelling & evaluation lead", "Training, metrics, error analysis (Milestone 3)"],
           ["[Member 4]", "Deployment & report lead", "predict_emotion, demo, report write-up"]],
          "Table 8. Team roles (replace the placeholders).",
          col_widths=[26 * mm, 46 * mm, 98 * mm]),
]

# ── References ────────────────────────────────────────────────────────────────────────────────────────────
story += [
    p("References", "h1"),
    *[p(r, "ref") for r in [
        "Barsoum, E., Zhang, C., Canton Ferrer, C., and Zhang, Z. (2016). Training deep networks for facial "
        "expression recognition with crowd-sourced label distribution. <i>ACM International Conference on "
        "Multimodal Interaction (ICMI)</i>.",
        "Bazarevsky, V., Kartynnik, Y., Vakunov, A., Raveendran, K., and Grundmann, M. (2019). BlazeFace: "
        "Sub-millisecond neural face detection on mobile GPUs. <i>arXiv:1907.05047</i>.",
        "Goodfellow, I. J., Erhan, D., Carrier, P. L., Courville, A., Mirza, M., Hamner, B., et al. (2013). "
        "Challenges in representation learning: A report on three machine learning contests. <i>International "
        "Conference on Neural Information Processing (ICONIP)</i>.",
        "Khaireddin, Y., and Chen, Z. (2021). Facial emotion recognition: State of the art performance on FER2013. "
        "<i>arXiv:2105.03588</i>.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. <i>Journal of Machine Learning "
        "Research</i>, 12, 2825–2830.",
        "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., and Chen, L.-C. (2018). MobileNetV2: Inverted residuals "
        "and linear bottlenecks. <i>IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)</i>.",
        "Viola, P., and Jones, M. (2001). Rapid object detection using a boosted cascade of simple features. "
        "<i>IEEE Conference on Computer Vision and Pattern Recognition (CVPR)</i>.",
    ]],
]

# ── Appendices ────────────────────────────────────────────────────────────────────────────────────────────
story += [
    PageBreak(),
    p("Appendix A  Linear SVM confusion matrix", "h1"),
    figure("confusion_matrix_linear_svm.png",
           "Figure A1. Confusion matrix of the Linear SVM on the test set: counts (left) and row-normalised (right).",
           1.0),
    p("Appendix B  Reproducibility", "h1"),
    p(f"All code, figures and tables are in the repository {REPO_URL}. The notebook "
      + code("CS413_Week7_FER_Lab.ipynb") + " runs top to bottom with <i>Restart &amp; Run All</i> (about 36 minutes "
      "on a 4-core CPU without a GPU, of which feature extraction takes about 7 minutes and the Linear SVM fits most "
      "of the rest). The environment is pinned in " + code("requirements.txt") + ": Python 3.13, TensorFlow 2.21, "
      "MediaPipe 1.1.1, OpenCV 4.14, scikit-learn 1.9.1. The seed is 42 for " + code("random") + ", NumPy, "
      "TensorFlow and every scikit-learn " + code("random_state") + "; re-extracting the features and retraining "
      "reproduces identical metrics. This report is generated from the notebook outputs by "
      + code("report/build_report.py") + "."),
]

doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                        bottomMargin=20 * mm, title="Facial Emotion Recognition on FER2013 — CS 413 Week 7 Lab",
                        author="[Team names]", subject="CS 413 Affective Computing, Week 7 lab report")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Wrote {PDF_PATH.relative_to(ROOT)}")
