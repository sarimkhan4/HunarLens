# What: builds the complete HunarLens presentation and PDF.
# Why: the viva presentation needs consistent numbers and project-grounded visuals.
# Viva: the script uses only saved aggregate evidence and generated project figures.
from pathlib import Path
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, inch
from reportlab.pdfbase.pdfmetrics import stringWidth


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "presentation"
FIGURES = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"

NAVY = "1D2B64"
BLUE = "277DA1"
TEAL = "43AA8B"
RED = "B84A62"
GOLD = "F9C74F"
WHITE = "FFFFFF"
INK = "172033"
LIGHT = "EDF3F7"
PALE = "F7F9FC"
GRAY = "667085"


SLIDES = [
    ("HunarLens",
     ["Youth Unemployment Vulnerability in Pakistan",
      "CT-378 Machine Learning Semester Project",
      "Data, Machine Learning, Explainability and Dashboard"],
     "title"),
    ("Project Team and Presentation Goal",
     ["A beginner-friendly, end-to-end explanation of every major project stage",
      "What we built",
      "Why we made each decision",
      "Where it appears in the code",
      "How the data and model flow through the system",
      "How to demonstrate the app"],
     "bullets"),
    ("The Real-World Problem",
     ["Many Pakistani youth face difficulty finding suitable work",
      "Education level, sex, geography and household context are associated with outcomes",
      "A survey-based project can identify aggregate patterns",
      "It cannot diagnose an individual or prove causation",
      "This project is for research, education and policy exploration"],
     "bullets"),
    ("Our Research Question",
     ["Can we estimate unemployment probability for youth aged 15–24?",
      "Population: youth already in the labour force",
      "Positive class: unemployed",
      "Negative class: employed",
      "Goal: honest, leak-free, explainable binary classification"],
     "bullets"),
    ("What HunarLens Predicts",
     ["Target: is_unemployed",
      "1 = unemployed",
      "0 = employed",
      "Input: approved demographic, education, household and regional fields",
      "Output: a probability rather than a guaranteed outcome",
      "Operating thresholds convert probability into a class"],
     "bullets"),
    ("What HunarLens Does Not Do",
     ["It does not cover every young person",
      "It excludes people outside the labour force",
      "It does not establish cause and effect",
      "It does not measure individual ability",
      "It does not measure employer demand or vacancies",
      "It must not be used for hiring or benefit decisions"],
     "bullets"),
    ("Project Architecture",
     ["1. Official PBS data acquisition",
      "2. Label reproduction and modelling dataset",
      "3. Household-aware split",
      "4. One scikit-learn pipeline",
      "5. Model comparison and validation",
      "6. Frozen model and test evaluation",
      "7. Streamlit dashboard and reports"],
     "bullets"),
    ("Primary Data Source",
     ["Labour Force Survey 2024–25",
      "Pakistan Bureau of Statistics",
      "Person-level survey record",
      "Contains roster, education, literacy, household and labour-market fields",
      "Raw Stata file is kept outside Git",
      "File: data/raw/LFS 2024-25.sav web.dta"],
     "bullets"),
    ("Secondary Data Source",
     ["Population and Housing Census 2023",
      "Regional indicators only",
      "Province-level population density",
      "Province-level urban proportion",
      "Province × area average household size",
      "Output lookup: data/processed/census_lookup.csv"],
     "bullets"),
    ("How the Two Sources Are Used",
     ["LFS supplies individual records and the target",
      "Census supplies aggregate regional context",
      "Join key: province + rural/urban area",
      "No person-level Census merge",
      "Census variables are demographic context, not unemployment labels",
      "Both sources are used for separate analytical purposes"],
     "bullets"),
    ("Official Data Acquisition",
     ["The script discovers files from official PBS landing pages",
      "It does not use guessed or third-party URLs",
      "Downloaded files are recorded in MANIFEST.json",
      "Manifest records URL, access date, size and SHA-256",
      "Raw data remains ignored by Git",
      "Code: scripts/download_data.py"],
     "bullets"),
    ("Unemployment Label",
     ["Employed if the survey route indicates paid work or business/farm work",
      "Unemployed if not employed, currently searching or qualifying as available",
      "Availability within two weeks is part of the route",
      "Future starters are approved as an approximation",
      "Survey weights are used for reproduction, not predictors",
      "Code: scripts/build_modeling_dataset.py"],
     "bullets"),
    ("Why the Label Was Reproduced",
     ["Survey labelling could easily be wrong",
      "PBS publishes weighted labour-force totals",
      "The script compares its weighted result with the PBS report",
      "It stopped while the provisional result differed too much",
      "The final rule produced an approximately 7.1% all-age unemployment rate",
      "This became a label-construction safeguard"],
     "bullets"),
    ("Future-Starter Approximation",
     ["A future starter may have arranged work but not recently searched",
      "PBS asks whether a job or business will start in the near future",
      "The available Stata file lacks a verified start date",
      "Therefore it is not possible to prove the ILO's three-month timing condition",
      "The approved rule is an approximation",
      "It must be described honestly in the report and viva"],
     "bullets"),
    ("Household Feature Construction",
     ["Count the complete household roster",
      "Create group_id from PCode + EBCode + HHNo",
      "Calculate household size",
      "Calculate children under 15",
      "Calculate other youth aged 15–24",
      "Record head sex and head education",
      "Remove identifiers from the final modelling table"],
     "bullets"),
    ("Target Population",
     ["Age 15–24",
      "Employed or unemployed",
      "Youth outside the labour force are excluded",
      "This is not a study of all youth",
      "It is a sample of labour-force youth",
      "Training prevalence: 12.692%",
      "Final modelling rows: 26,653"],
     "bullets"),
    ("Final Data Split",
     ["18,657 training rows",
      "3,997 validation rows",
      "3,999 test rows",
      "Training prevalence: 12.69%",
      "Validation prevalence: 12.68%",
      "Test prevalence: 12.70%",
      "Data file: hunarlens_youth.csv"],
     "bullets"),
    ("Exploratory Data Analysis",
     ["EDA was performed on unweighted modelling records",
      "It examined class balance",
      "It examined age, education and training",
      "It examined sex, area and province",
      "It examined missing values",
      "It identified household-size outliers",
      "EDA did not tune or select the model"],
     "bullets"),
    ("EDA: Class Balance",
     ["23,270 employed records",
      "3,383 unemployed records",
      "Positive prevalence: 12.69%",
      "The positive class is a small minority",
      "Accuracy alone would be misleading",
      "F1 and PR-AUC became the important measures"],
     "figure",
     "class_balance.png"),
    ("EDA: Sex and Area",
     ["The rate varied between 11.1% and 24.5%",
      "Urban women had the highest observed area × sex rate",
      "Rural men had a lower observed rate",
      "These are descriptive subgroup associations",
      "They do not establish cause or discrimination",
      "The model may encode these historical differences"],
     "figure",
     "rate_sex_area.png"),
    ("EDA: Province",
     ["Unemployment rates ranged from 10.8% to 15.7%",
      "Province is retained as an approved categorical feature",
      "Census indicators repeat provincial and province × area information",
      "Census effects were later tested in ablation",
      "Province must not be interpreted as causal"],
     "figure",
     "rate_by_province.png"),
    ("EDA: Education",
     ["Observed rates varied greatly by education code",
      "Some degree categories were rare",
      "The plot includes group sizes",
      "Education is ordered in one numeric branch",
      "It is also retained in a categorical branch",
      "Small-category rates require caution"],
     "figure",
     "rate_by_education_level.png"),
    ("EDA: Training",
     ["The training indicator had two categories",
      "1 means ever/current training",
      "0 means never receiving or receiving no training",
      "Survey timing was discarded",
      "Training is associated with the employment outcome",
      "It must not be called causal"],
     "figure",
     "rate_by_has_training.png"),
    ("EDA: Missing Values",
     ["All 19 retained features had 0% observed NaNs",
      "Imputation is still included in the production pipeline",
      "Unknown source codes were validated",
      "Education code 1 means no formal education",
      "Enrolment code 1 means not enrolled",
      "They are substantive categories, not missing values"],
     "figure",
     "missing_values.png"),
    ("EDA: Household Outlier",
     ["Household size ranged from 1 to 54",
      "Maximum youth per household was 10",
      "The 54-person result needs further household-key review",
      "Identifiers may span survey periods or unusual source structures",
      "It became one reason for 99th-percentile clipping",
      "It was not silently removed"],
     "figure",
     "household_size_distribution.png"),
    ("EDA Decisions",
     ["Use the numeric education code and categorical education",
      "Add age bands",
      "Add children share",
      "Clip household size at the training-fold 99th percentile",
      "Add sex × area interaction",
      "Do not log Census density inside the submitted pipeline"],
     "bullets"),
    ("Feature Allowlist Strategy",
     ["Only config.py::FEATURES may enter X",
      "No employment or search field",
      "No occupation or industry",
      "No wages or hours",
      "No unemployment duration",
      "No survey weights or record identifiers",
      "Allowlist strategy is stronger than a blocklist"],
     "bullets"),
    ("Grouped 70/15/15 Split",
     ["Use 20 StratifiedGroupKFold folds",
      "14 folds become training",
      "3 folds become validation",
      "3 folds become test",
      "Households never cross partitions",
      "Split assignments are saved with a dataset hash",
      "Every experiment reads the same assignment file"],
     "bullets"),
    ("Why Leakage Control Matters",
     ["Ordinary random rows can split a household",
      "Household siblings can look artificially similar",
      "Preprocessing can learn from validation statistics",
      "Label-derived fields can reveal the target",
      "Test results can become optimistic",
      "HunarLens uses pipeline and grouped-split controls"],
     "bullets"),
    ("One Production Pipeline",
     ["ApprovedFeatures",
      "-> ColumnTransformer",
      "-> numeric impute and scale",
      "-> categorical impute and encode",
      "-> machine-learning estimator",
      "Training learns all fitted steps",
      "The app loads the complete pipeline"],
     "bullets"),
    ("Feature Engineering Details",
     ["education_ordinal: raw numeric education code",
      "age_band: 15–17 / 18–20 / 21–24",
      "children_share: children divided by household size",
      "household_size_clipped: 99th-percentile training cutoff",
      "sex_area: sex and area interaction",
      "Census density was retained in original unit"],
     "bullets"),
    ("Baseline Model",
     ["Stratified DummyClassifier",
      "Randomly predicts according to class prevalence",
      "It provides a no-signal reference",
      "Validation PR-AUC approximately equals prevalence",
      "Dummy F1: 0.123",
      "Dummy test PR-AUC: 0.127"],
     "bullets"),
    ("Models Compared",
     ["Logistic Regression",
      "Random Forest",
      "HistGradientBoosting",
      "Stratified DummyClassifier",
      "Models were compared using 5-fold grouped CV",
      "Main selection metric: average precision",
      "Class weight and probability threshold strategies were tested"],
     "bullets"),
    ("Grouped CV Results",
     ["Logistic Regression CV average precision: 0.2811",
      "Random Forest CV average precision: 0.3076",
      "HistGradientBoosting CV average precision: 0.2977",
      "Stratified Dummy: 0.1260",
      "Random Forest led on mean CV",
      "HGB was within the approved 0.01 tie margin"],
     "bullets"),
    ("Why HistGradientBoosting Was Selected",
     ["RF–HGB CV difference was 0.0099",
      "It was inside the approved tie band",
      "HGB had a smaller training-to-CV gap",
      "HGB was smaller to save",
      "HGB made faster predictions",
      "The team preferred HGB for deployability"],
     "bullets"),
    ("Calibration",
     ["Raw HGB Brier score: 0.100341",
      "Sigmoid HGB Brier score: 0.100335",
      "Relative improvement was below 2%",
      "Fixed-bin calibration error did not justify sigmoid",
      "The final pipeline retained raw probabilities",
      "Sigmoid calibration was not fully external evidence"],
     "bullets"),
    ("Threshold Strategy",
     ["Primary threshold: 0.182931",
      "Selected from the validation near-optimal F1 range",
      "Midpoint of thresholds within 0.005 of maximum F1",
      "Screening threshold: 0.154107",
      "Screening threshold targets at least 60% recall",
      "Both thresholds are fixed before test evaluation"],
     "bullets"),
    ("Risk Bands",
     ["Lower than most",
      "Elevated",
      "High",
      "High threshold: 0.268655",
      "Elevated threshold: 0.158568",
      "Bands are relative rankings",
      "They are not medical or legal classifications"],
     "bullets"),
    ("Test Protocol",
     ["The test set was opened once",
      "The approved model hash was checked first",
      "Model, calibration and thresholds were already frozen",
      "Test probabilities were saved",
      "Every later table uses the saved probabilities",
      "No test rescore or model refit is allowed"],
     "bullets"),
    ("Test Results",
     ["3,999 test youth",
      "508 unemployed",
      "Test prevalence: 12.70%",
      "HGB F1: 0.360",
      "Precision: 0.273",
      "Recall: 0.530",
      "PR-AUC: 0.303",
      "ROC-AUC: 0.752",
      "Top-10% lift: 2.81"],
     "bullets"),
    ("Confusion Matrix",
     ["True positives: 269",
      "False negatives: 239",
      "False positives: 716",
      "True negatives: 2,775",
      "The model found 269 of 508 unemployed youth",
      "It also flagged 716 employed youth",
      "Primary and screening thresholds make different trade-offs"],
     "figure",
     "test_confusion_matrix.png"),
    ("Test PR Curve",
     ["HGB PR-AUC: 0.303",
      "Dummy PR-AUC: 0.127",
      "Positive prevalence: 12.70%",
      "The curve shows ranking quality across thresholds",
      "It does not mean 30.3% accuracy",
      "It is the positive-class precision-recall summary"],
     "figure",
     "test_pr_curve.png"),
    ("Top-10% Lift",
     ["HGB top-10% lift: 2.81",
      "Dummy top-10% lift: 0.87",
      "Lift compares top-risk concentration with prevalence",
      "It means the top 10% are 2.81× the overall prevalence",
      "It is useful for resource prioritization in research",
      "It is not a causal or individual guarantee"],
     "figure",
     "test_gain_lift.png"),
    ("Test Bootstrap Uncertainty",
     ["1,000 household-grouped bootstrap resamples",
      "Primary-threshold F1 95% interval: 0.328–0.393",
      "Average precision 95% interval: 0.267–0.343",
      "Whole households stay together",
      "Intervals summarize this test sample",
      "They do not include survey weights or full design uncertainty"],
     "bullets"),
    ("Subgroup Results",
     ["Recall: 48.0% for men",
      "Recall: 68.0% for women",
      "Recall: 49.8% rural",
      "Recall: 58.3% urban",
      "No formal education recall: 17.9%",
      "Intermediate education recall: 94.1%",
      "These differences require fairness discussion"],
     "bullets"),
    ("Why Subgroup Differences Matter",
     ["The overall result can hide unequal coverage",
      "Smaller positive counts are unstable",
      "Balochistan had only 35 positives",
      "Degree-or-higher had 46 positives",
      "Groups above 50 positives may still be uncertain",
      "Subgroups describe performance, not individual diagnosis"],
     "bullets"),
    ("Validation Permutation Importance",
     ["Education: 0.1106",
      "Enrolment: 0.0820",
      "Geography: 0.0618",
      "Sex: 0.0469",
      "Age: 0.0284",
      "Training: 0.0283",
      "Household: 0.0221",
      "Shuffling fields reduced average precision"],
     "figure",
     "grouped_permutation_importance.png"),
    ("How to Interpret Permutation Importance",
     ["It measures reliance of the fitted model",
      "It does not establish causation",
      "Correlated fields can share importance",
      "Error bars show permutation variation",
      "They are not full population confidence intervals",
      "Education, literacy and enrolment are separate but related fields"],
     "bullets"),
    ("Enrolment Finding",
     ["Enrolment was the second-most important group",
      "Removing it lowered grouped-CV average precision",
      "CV average precision fell from 0.297705 to 0.250015",
      "In the labour-force sample, enrolled youth were usually working",
      "Observed enrolled unemployment was much lower",
      "Labour-force selection may contribute to this pattern"],
     "bullets"),
    ("What-If Explanations",
     ["Start with one validated profile",
      "Replace one input by its training median or mode",
      "Keep every other input fixed",
      "Re-run the complete pipeline",
      "Report the probability difference",
      "This is model sensitivity, not a real intervention"],
     "bullets"),
    ("Skills-Gap Analysis",
     ["Separate from the unemployment model",
      "Uses education, training and occupation",
      "Education and training are proxies for skills",
      "It does not measure vacancies",
      "It does not measure employer demand",
      "It uses weighted survey estimates and cluster bootstrap"],
     "bullets"),
    ("Skills-Gap Key Results",
     ["Unemployment by education: 8.2% to 22.6%",
      "Lowest band: no formal education",
      "Highest band: degree or above",
      "Training share is 8.9 percentage points lower among unemployed youth",
      "Approximate NEET: 29.3%",
      "PBS separate NEET measure: 28.4%",
      "Definitions differ"],
     "bullets"),
    ("Skills Mismatch",
     ["A worker's education band is compared with the occupation's typical band",
      "All-employed, 25–44 and youth reference groups are used",
      "Strict above-mode share ranges from 41.0% to 46.0%",
      "Within-one-band share ranges from 75.7% to 80.3%",
      "It is a statistical mismatch definition",
      "It is not a test of personal skills"],
     "bullets"),
    ("Streamlit App",
     ["Profile Explorer",
      "Live unemployment probability",
      "Training base rate",
      "Relative risk band",
      "Validation-percentile ruler",
      "What-if changes",
      "Skills-gap and methodology sections"],
     "bullets"),
    ("App Data Flow",
     ["User enters an approved profile",
      "Python normalizes category codes",
      "Python validates numeric ranges",
      "App checks household consistency",
      "Census values are joined by province and area",
      "Frozen pipeline predicts probability",
      "The interface adds context and warnings"],
     "bullets"),
    ("App Demonstration Plan",
     ["Open the Overview page",
      "Explain the project population and LFS/Census sources",
      "Open the Profile Explorer",
      "Choose a rural, enrolled 18-year-old profile",
      "Select a rural, non-enrolled profile",
      "Compare probability and risk band",
      "Change one input in the alternative profile",
      "Open the explanation chart",
      "Open Model Performance",
      "Open Skills Gap and Data/Methodology"],
     "bullets"),
    ("App Safety and Privacy",
     ["User answers are not saved",
      "App code does not log profile input",
      "Only public aggregate files are cached",
      "Rare combinations receive warnings",
      "No individual decision language is used",
      "The app labels estimates as associations"],
     "bullets"),
    ("Repository and Reproducibility",
     ["src/hunarlens: reusable source code",
      "scripts: lifecycle programs",
      "notebooks: narrative documentation",
      "models: frozen pipeline and metadata",
      "reports: tables and 200-DPI figures",
      "docs: decisions and findings",
      "app: Streamlit interface",
      "tests: project verification when available"],
     "bullets"),
    ("Dependency and Environment Strategy",
     ["Python 3.12",
      "Exact runtime pins",
      "Separate development dependencies",
      "Pandas and NumPy for data",
      "Scikit-learn for modelling",
      "Matplotlib and Altair for visualizations",
      "Joblib for model serialization",
      "Streamlit for deployment"],
     "bullets"),
    ("Main Final Findings",
     ["The project produced a leak-controlled pipeline",
      "The HGB model improved over a stratified dummy",
      "Test F1 was 0.360",
      "Test PR-AUC was 0.303",
      "Top-10% lift was 2.81",
      "Results remain modest and honest",
      "Skills-gap findings provide context beyond prediction"],
     "bullets"),
    ("Important Limitations",
     ["Restricted to labour-force youth",
      "No survey weights in model test metrics",
      "Approximate future-starter label",
      "Sex and geography are model inputs",
      "Subgroup estimates can be unstable",
      "Household key may combine unusual records",
      "Model does not establish causation"],
     "bullets"),
    ("Viva Questions: Data",
     ["Why are these features allowed?",
      "What is target leakage?",
      "Why did you reproduce PBS totals?",
      "What does PCode + EBCode + HHNo mean?",
      "Why use survey weights in reproduction only?",
      "What is the difference between weighted and unweighted results?"],
     "bullets"),
    ("Viva Questions: Modelling",
     ["Why a single pipeline?",
      "How does grouped splitting prevent leakage?",
      "Why StratifiedGroupKFold?",
      "Why is F1 more important than accuracy?",
      "Why HGB over Random Forest?",
      "How was calibration tested?",
      "Why were thresholds chosen on validation?"],
     "bullets"),
    ("Viva Questions: Evaluation",
     ["What does PR-AUC mean?",
      "What does a confusion matrix show?",
      "What is top-10% lift?",
      "Why were test metrics opened once?",
      "What does the bootstrap estimate?",
      "Why can subgroup recall be unequal?",
      "Why is the app not a decision tool?"],
     "bullets"),
    ("Viva Questions: Explainability",
     ["What does permutation importance prove?",
      "What does a what-if change mean?",
      "Why can correlated variables share importance?",
      "What is a partial profile?",
      "Why does enrolment matter?",
      "How should the skills mismatch be interpreted?"],
     "bullets"),
    ("Conclusion",
     ["HunarLens combines survey auditing, grouped machine learning and explainability",
      "It follows a leak-controlled, reproducible process",
      "The model modestly improves over a dummy baseline",
      "The skills-gap analysis provides separate aggregate context",
      "The Streamlit app makes evidence accessible",
      "The project clearly distinguishes association from causation"],
     "bullets"),
    ("Demonstration Summary",
     ["Dashboard overview",
      "Profile explorer",
      "One-profile probability",
      "Risk band and percentile",
      "What-if sensitivity",
      "Model performance",
      "Skills gap",
      "Data and methodology",
      "Limitations"],
     "bullets"),
    ("Thank You",
     ["Questions",
      "Live app: hunar-lens.streamlit.app",
      "Project repository: HunarLens",
      "CT-378 Machine Learning Semester Project"],
     "title"),
]


def rgb(hex_value):
    return RGBColor(
        int(hex_value[0:2], 16),
        int(hex_value[2:4], 16),
        int(hex_value[4:6], 16),
    )


def set_slide_background(slide, color=PALE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def add_title(slide, title):
    box = slide.shapes.add_textbox(Inches(0.65), Inches(0.38), Inches(11.9), Inches(0.65))
    frame = box.text_frame
    frame.clear()
    p = frame.paragraphs[0]
    p.text = title
    p.font.name = "Aptos Display"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = rgb(NAVY)


def add_footer(slide, number):
    box = slide.shapes.add_textbox(Inches(11.65), Inches(7.1), Inches(0.95), Inches(0.22))
    p = box.text_frame.paragraphs[0]
    p.text = f"{number:02d}"
    p.font.name = "Aptos"
    p.font.size = Pt(9)
    p.font.color.rgb = rgb(GRAY)
    p.alignment = PP_ALIGN.RIGHT


def add_bullets(slide, items):
    box = slide.shapes.add_textbox(Inches(0.85), Inches(1.25), Inches(11.6), Inches(5.55))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.name = "Aptos"
        p.font.size = Pt(21 if len(items) <= 6 else 17)
        p.font.color.rgb = rgb(INK)
        p.space_after = Pt(12)
        p._p.get_or_add_pPr().insert(0, p._p._new_pPr())


def add_title_slide(slide, items):
    set_slide_background(slide, NAVY)
    accent = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(0.18), Inches(7.5))
    accent.fill.solid()
    accent.fill.fore_color.rgb = rgb(GOLD)
    accent.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(11.4), Inches(1.2))
    title_box.text_frame.text = "HunarLens"
    p = title_box.text_frame.paragraphs[0]
    p.font.name = "Aptos Display"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = rgb(WHITE)

    sub = slide.shapes.add_textbox(Inches(0.95), Inches(2.85), Inches(11), Inches(2.2))
    tf = sub.text_frame
    tf.clear()
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.name = "Aptos"
        p.font.size = Pt(22 if i == 0 else 18)
        p.font.color.rgb = rgb(WHITE if i < 2 else "D8E8F2")
        p.space_after = Pt(14)


def add_figure_slide(slide, title, items, filename):
    add_title(slide, title)
    text_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.15), Inches(4.15), Inches(5.75))
    tf = text_box.text_frame
    tf.clear()
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.name = "Aptos"
        p.font.size = Pt(15)
        p.font.color.rgb = rgb(INK)
        p.space_after = Pt(9)

    path = FIGURES / filename
    if path.exists():
        slide.shapes.add_picture(str(path), Inches(5.05), Inches(1.15),
                                 width=Inches(7.55), height=Inches(5.65))


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    for number, slide_data in enumerate(SLIDES, 1):
        title = slide_data[0]
        items = slide_data[1]
        kind = slide_data[2]
        slide = prs.slides.add_slide(blank)
        set_slide_background(slide)

        if kind == "title":
            add_title_slide(slide, items)
        elif kind == "figure":
            add_figure_slide(slide, title, items, slide_data[3])
        else:
            add_title(slide, title)
            add_bullets(slide, items)

        add_footer(slide, number)

    path = OUTPUT / "HunarLens_Complete_Presentation.pptx"
    prs.save(path)
    return path


def fit_font(text, font_name, max_width, start=18, minimum=9):
    size = start
    while size > minimum:
        if stringWidth(text, font_name, size) <= max_width:
            return size
        size -= 1
    return minimum


def wrap_pdf_text(text, font_name, font_size, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        trial = word if not line else line + " " + word
        if stringWidth(trial, font_name, font_size) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def pdf_rgb(hex_value):
    return tuple(int(hex_value[i:i+2], 16) / 255 for i in (0, 2, 4))


def build_pdf():
    path = OUTPUT / "HunarLens_Complete_Presentation.pdf"
    page_w, page_h = landscape((13.333 * inch, 7.5 * inch))
    c = canvas.Canvas(str(path), pagesize=(page_w, page_h))

    for number, (title, items, kind, *extra) in enumerate(SLIDES, 1):
        if kind == "title":
            c.setFillColorRGB(*pdf_rgb(NAVY))
            c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
            c.setFillColorRGB(*pdf_rgb(GOLD))
            c.rect(0, 0, 0.18 * inch, page_h, fill=1, stroke=0)
            c.setFillColorRGB(*pdf_rgb(WHITE))
            c.setFont("Helvetica-Bold", 34)
            c.drawString(0.9 * inch, 5.2 * inch, "HunarLens")
            c.setFont("Helvetica", 18)
            y = 4.4 * inch
            for i, item in enumerate(items):
                c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 16 if i == 0 else 14)
                c.drawString(0.95 * inch, y, item)
                y -= 0.45 * inch
        else:
            c.setFillColorRGB(*pdf_rgb(PALE))
            c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
            c.setFillColorRGB(*pdf_rgb(NAVY))
            c.setFont("Helvetica-Bold", 24)
            c.drawString(0.65 * inch, 6.75 * inch, title)

            if kind == "figure" and extra:
                left_width = 4.15 * inch
                left_x = 0.65 * inch
                y = 5.95 * inch
                c.setFillColorRGB(*pdf_rgb(INK))
                c.setFont("Helvetica", 12)
                for item in items:
                    size = fit_font(item, "Helvetica", left_width - 0.15 * inch, 12, 9)
                    c.setFont("Helvetica", size)
                    for line in wrap_pdf_text(item, "Helvetica", size, left_width - 0.15 * inch):
                        c.drawString(left_x, y, "• " + line if line == wrap_pdf_text(item, "Helvetica", size, left_width - 0.15 * inch)[0] else "  " + line)
                        y -= 0.18 * inch
                    y -= 0.12 * inch
                image = FIGURES / extra[0]
                if image.exists():
                    c.drawImage(str(image), 5.05 * inch, 1.25 * inch,
                                width=7.45 * inch, height=5.35 * inch,
                                preserveAspectRatio=True, anchor="c")
            else:
                x = 0.85 * inch
                y = 5.95 * inch
                c.setFillColorRGB(*pdf_rgb(INK))
                size = 16 if len(items) <= 7 else 13
                for item in items:
                    c.setFont("Helvetica", size)
                    lines = wrap_pdf_text(item, "Helvetica", size, 11.4 * inch)
                    for i, line in enumerate(lines):
                        prefix = "• " if i == 0 else "  "
                        c.drawString(x, y, prefix + line)
                        y -= 0.32 * inch
                    y -= 0.12 * inch

        c.setFillColorRGB(*pdf_rgb(GRAY))
        c.setFont("Helvetica", 8)
        c.drawRightString(12.7 * inch, 0.22 * inch, f"{number:02d}")
        c.showPage()

    c.save()
    return path


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pptx_path = build_pptx()
    pdf_path = build_pdf()
    print(f"Created: {pptx_path}")
    print(f"Created: {pdf_path}")
    print(f"Slides: {len(SLIDES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
