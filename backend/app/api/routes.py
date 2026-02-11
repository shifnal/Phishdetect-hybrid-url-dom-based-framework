"""
API Routes Module - Fixed Version
FastAPI endpoints with stable DOM + Visual analysis and dynamic phishing probability
"""

import os
import json
import subprocess
from urllib.parse import urlparse
from typing import Optional
import requests
import ssl

from fastapi import APIRouter
from pydantic import BaseModel

from app.ml.url_predictor import get_url_score
from app.core.dom_analysis import dom_score
from app.core.visual_analysis import calculate_visual_score

router = APIRouter()

# Paths - will be set from main.py
STATIC_DIR = None
SCRIPTS_DIR = None


class URLRequest(BaseModel):
    url: str
    brand: Optional[str] = ""


def set_paths(static_dir: str, scripts_dir: str):
    """Set the paths for static files and scripts."""
    global STATIC_DIR, SCRIPTS_DIR
    STATIC_DIR = static_dir
    SCRIPTS_DIR = scripts_dir


# -----------------------------
# Site Reachability Check
# -----------------------------
def is_site_reachable(url, timeout=10, retries=2):
    """
    Returns True if the site responds with status < 500.
    Retries on failure. Disables SSL verification to avoid edu/SSL issues.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/144.0.0.0 Safari/537.36"
    }
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, verify=False)
            return r.status_code < 500
        except Exception as e:
            print(f"DEBUG: Attempt {attempt + 1} failed for {url}: {e}")
    # fallback: assume reachable, let Puppeteer handle
    return True


# -----------------------------
# Puppeteer DOM Extraction
# -----------------------------
def extract_dom_via_puppeteer(url: str, output_path: str, timeout=60):
    """Extract DOM tree from a URL using Puppeteer."""
    puppeteer_path = os.path.join(SCRIPTS_DIR, "puppeteer_script.js")
    try:
        print(f"PUPPETEER START: {url}")
        result = subprocess.run(
            ["node", puppeteer_path, url, output_path],
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        print("Puppeteer stdout:", result.stdout[:500])
        print("Puppeteer stderr:", result.stderr[:500])

        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                dom_tree = json.load(f)
            print(f"PUPPETEER SUCCESS: {output_path}")
            return dom_tree
        else:
            return None
    except subprocess.TimeoutExpired:
        print("Puppeteer timeout!")
        return None
    except Exception as e:
        print(f"Puppeteer error: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return None


# -----------------------------
# DOM + Visual Scoring
# -----------------------------

def get_dom_and_visual_score(url: str, brand: str):
    """
    Get DOM similarity and visual similarity scores.
    
    Returns:
        tuple: (dom_score, visual_score, detected_brand)
    """
    debug_dir = os.path.join(STATIC_DIR, "debug_visuals")
    os.makedirs(debug_dir, exist_ok=True)

    temp_test_path = os.path.join(debug_dir, "temp_test_dom.json")
    temp_brand_path = os.path.join(debug_dir, "temp_brand_dom.json")
    temp_test_img = temp_test_path.replace(".json", ".png")
    temp_brand_img = temp_brand_path.replace(".json", ".png")

    # Clean previous temp files
    for f in [temp_test_path, temp_brand_path, temp_test_img, temp_brand_img]:
        if os.path.exists(f):
            os.remove(f)

    # Extract DOM & Screenshot for the target URL
    dom_tree = extract_dom_via_puppeteer(url, temp_test_path)
    if not dom_tree:
        print(f"DEBUG: Site unreachable or failed to fetch DOM: {url}")
        return 0.0, 0.0, brand  # Safe fallback: 0 similarity

    # Auto-detect brand if missing
    if not brand and isinstance(dom_tree, dict):
        title = dom_tree.get("title", "").lower()
        for b in ["google", "paypal", "amazon", "facebook", "instagram", "netflix", "microsoft"]:
            if b in title:
                brand = b
                break
        if not brand:
            print("DEBUG: Brand could not be auto-detected.")
            return 0.0, 0.0, None

    # Fetch brand DOM & Screenshot
    # Only compute brand DOM if brand is known AND domain matches
    if brand and brand.lower() in url.lower():
        brand_url = f"https://www.{brand}.com"
        extract_dom_via_puppeteer(brand_url, brand_dom_path)
    else:
        # Skip brand comparison, force low similarity
        brand_dom_path = None
        brand_img_path = None

    if not brand_tree:
        print(f"DEBUG: Brand site unreachable: {brand_url}")
        return 0.0, 0.0, brand

    # Compute scores
    d_score = dom_score(temp_test_path, temp_brand_path)
    v_score = calculate_visual_score(temp_test_img, temp_brand_img)
    print(f"DEBUG: DOM Score={d_score:.4f}, Visual Score={v_score:.4f}")

    # Cleanup JSONs only (keep images for debugging)
    for f in [temp_test_path, temp_brand_path]:
        if os.path.exists(f):
            os.remove(f)

    return d_score, v_score, brand




def get_dom_and_visual_score(url: str, brand: str):
    """
    Get DOM similarity and visual similarity scores.

    Returns:
        tuple: (dom_score, visual_score, detected_brand)
    """
    debug_dir = os.path.join(STATIC_DIR, "debug_visuals")
    os.makedirs(debug_dir, exist_ok=True)

    test_dom_path = os.path.join(debug_dir, "temp_test_dom.json")
    brand_dom_path = os.path.join(debug_dir, "temp_brand_dom.json")
    test_img_path = test_dom_path.replace(".json", ".png")
    brand_img_path = brand_dom_path.replace(".json", ".png")

    # Extract DOM + screenshot for test site
    dom_tree = extract_dom_via_puppeteer(url, test_dom_path)
    if not dom_tree:
        return None, None, brand

    # Auto-detect brand if not provided
    if not brand and isinstance(dom_tree, dict):
        title = dom_tree.get("title", "").lower()
        brand_keywords = [
    "google", "apple", "microsoft", "amazon", "facebook", "meta",
    "instagram", "whatsapp", "twitter", "linkedin", "youtube", "netflix",
    "paypal", "visa", "mastercard", "stripe", "coinbase",
    "sbi", "hdfc", "icici", "axis", "pnb", "kotak", "yesbank",
    "paytm", "phonepe", "gpay", "upi",
    "swiggy", "zomato", "flipkart", "myntra", "meesho",
    "airtel", "jio", "vodafone", "bsnl",
    "ktu", "ugc", "nta", "aicte", "uidai", "aadhaar", "pan", "digilocker",
    "irctc", "makemytrip", "uber", "ola"
    ]

        for b in brand_keywords:
            if b in title:
                brand = b
                break

    # Even if brand is unknown, continue analysis
    if not brand:
        print("DEBUG: Brand unknown, proceeding without brand-specific DOM")

    # Extract DOM + screenshot for brand reference (if known)
    if brand:
        brand_url = f"https://www.{brand}.com"
        extract_dom_via_puppeteer(brand_url, brand_dom_path)
    else:
        # Skip brand DOM for unknown brand
        brand_dom_path = test_dom_path  # fallback to same DOM
        brand_img_path = test_img_path

    # Compute DOM score
    try:
        d_score = dom_score(test_dom_path, brand_dom_path)
    except Exception as e:
        print(f"DEBUG: DOM score failed: {e}")
        d_score = 0.0

    # Compute Visual score
    try:
        v_score = calculate_visual_score(test_img_path, brand_img_path)
    except Exception as e:
        print(f"DEBUG: Visual score failed: {e}")
        v_score = 0.0

    # Cleanup JSONs but keep screenshots for debug
    for f in [test_dom_path, brand_dom_path]:
        if os.path.exists(f):
            os.remove(f)

    return d_score, v_score, brand


# -----------------------------
# PREDICT ROUTE
# -----------------------------
@router.post("/predict")
def predict(data: URLRequest):
    """
    Analyze a URL for phishing indicators.
    Combines URL-based ML prediction with DOM and visual similarity analysis.
    """
    try:
        url = data.url
        brand = data.brand.lower() if data.brand else ""

        # Phase 1: URL Score
        url_result = get_url_score(url)
        url_score = float(url_result.get("url_score", 0.0))
        if url_result.get("detected_brand"):
            brand = url_result["detected_brand"]

        # Phase 2: DOM + Visual Score
        d_score, v_score, detected_brand = get_dom_and_visual_score(url, brand)
        if detected_brand:
            brand = detected_brand

        # Domain validation
        domain = urlparse(url).netloc.lower()
        is_domain_match = brand in domain if brand else False

        # Fusion Logic
        if d_score is None or d_score == 0:
            # Unreachable or failed site
            similarity_score = 0.0
            d_score = 0.0
            v_score = 0.0

            if brand and not is_domain_match:
                phishing_prob = max(url_score, 0.6)
            else:
                phishing_prob = url_score
        else:
            similarity_score = (d_score * 0.5) + (v_score * 0.5)
            if is_domain_match:
                phishing_prob = url_score * 0.1
            else:
                phishing_prob = (url_score * 0.2) + (similarity_score * 0.8)

        # Clamp probability
        phishing_prob = min(max(phishing_prob, 0.0), 1.0)
        threshold = 0.5
        label = "Phishing" if phishing_prob > threshold else "Legitimate"

        return {
            "url": url,
            "brand": brand or "",
            "domain_match": is_domain_match,
            "url_score": round(url_score, 4),
            "dom_score": round(d_score, 4),
            "visual_score": round(v_score, 4),
            "similarity_score": round(similarity_score, 4),
            "hybrid_score": round(phishing_prob, 4),
            "threshold": threshold,
            "final_label": label
        }

    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}
