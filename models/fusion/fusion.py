"""
Fusion Engine (Adaptive XGBoost-based)

Combines:
- URL-based ML score
- DOM similarity score
- Visual similarity score (SSIM)

Uses a lightweight XGBoost classifier trained on-the-fly
for adaptive, non-linear fusion (no saved model).
"""

import os
import sys
import numpy as np
from xgboost import XGBClassifier

# -------------------------
# Path fixes
# -------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOM_ANALYZER_DIR = os.path.join(CURRENT_DIR, "..", "dom_analyzer")
VISUAL_ANALYZER_DIR = os.path.join(CURRENT_DIR, "..", "visual_analyzer")

sys.path.append(DOM_ANALYZER_DIR)
sys.path.append(VISUAL_ANALYZER_DIR)

from dom_analysis import dom_score  # Fixed import to match file name
from visual_analysis import calculate_visual_score  # Fixed import to match file name


# =========================
# XGBOOST FUSION MODEL
# =========================
def build_fusion_model():
    """
    Trains a lightweight XGBoost model using weak supervision.
    This model is created at runtime (no saved weights).
    """

    # Features: [url_score, dom_score, visual_score]
    X = np.array([
        # Legitimate
        [0.90, 0.90, 0.85],
        [0.85, 0.80, 0.88],
        [0.75, 0.70, 0.72],

        # Obvious phishing
        [0.10, 0.00, 0.00],
        [0.25, 0.10, 0.05],
        [0.30, 0.00, 0.10],

        # Brand spoofing
        [0.85, 0.00, 0.00],
        [0.80, 0.10, 0.05],
        [0.78, 0.05, 0.00],

        # Partial similarity attacks
        [0.60, 0.40, 0.20],
        [0.55, 0.30, 0.25],
    ])

    # 1 = Legitimate, 0 = Phishing
    y = np.array([
        1, 1, 1,
        0, 0, 0,
        0, 0, 0,
        0, 0
    ])

    model = XGBClassifier(
        n_estimators=40,
        max_depth=3,
        learning_rate=0.3,
        subsample=1.0,
        colsample_bytree=1.0,
        eval_metric="logloss",
        use_label_encoder=False
    )

    model.fit(X, y)
    return model


# Build once at import
FUSION_MODEL = build_fusion_model()


# =========================
# DOM SCORE
# =========================

def compute_dom_score(test_dom_path: str, brand_dom_path: str) -> float:
    """
    Computes DOM similarity score using runtime-extracted DOMs.
    Returns 0.0 safely if files are missing or invalid.
    """

    if not test_dom_path or not brand_dom_path:
        return 0.0

    if not os.path.exists(test_dom_path):
        print(f"⚠️ DOM skipped: invalid path -> {test_dom_path}")
        return 0.0

    if not os.path.exists(brand_dom_path):
        print(f"⚠️ Brand DOM missing -> {brand_dom_path}")
        return 0.0

    try:
        return float(dom_score(test_dom_path, brand_dom_path))
    except Exception as e:
        print(f"❌ DOM scoring failed: {e}")
        return 0.0

# =========================
# VISUAL SCORE
# =========================
def compute_visual_score(brand: str, screenshot_path: str) -> float:
    brand_image = os.path.join(
        VISUAL_ANALYZER_DIR, "brands", f"{brand}.png"
    )

    if not screenshot_path or not os.path.exists(screenshot_path):
        return 0.0

    if not os.path.exists(brand_image):
        return 0.0

    try:
        return float(calculate_visual_score(screenshot_path, brand_image))
    except Exception:
        return 0.0


# =========================
# MAIN FUSION FUNCTION
# =========================
def run_fusion(url, brand, url_score, screenshot_path=None, test_dom_path=None, brand_dom_path=None):
    d_score = 0.0
    v_score = 0.0
    
    if test_dom_path and brand_dom_path:
        d_score = dom_score(test_dom_path, brand_dom_path)
    
    if brand and screenshot_path:
        # Assuming brand reference images are in a specific folder
        brand_ref = f"static/brands/{brand}.png"
        if os.path.exists(brand_ref):
            v_score = calculate_visual_score(screenshot_path, brand_ref)

    features = np.array([[url_score, d_score, v_score]])
    # 1 = Legitimate, 0 = Phishing. Frontend usually wants phishing probability.
    legit_prob = float(FUSION_MODEL.predict_proba(features)[0][1])
    phishing_prob = 1.0 - legit_prob

    return {
        "url": url,
        "brand": brand,
        "url_score": url_score,
        "dom_score": d_score,
        "visual_score": v_score,
        "hybrid_score": phishing_prob, # Higher = More likely phishing
        "prediction": "Phishing" if phishing_prob > 0.5 else "Legitimate"
    }


# =========================
# CLI TEST
# =========================
if __name__ == "__main__":
    result = run_fusion(
        url="https://paypa1.com/login",
        brand="paypal",
        url_score=0.88,
        screenshot_path=None
    )
    print(result)