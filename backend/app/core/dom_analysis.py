import json
import numpy as np
from .tree_edit_distance import tree_edit_distance  # Implement or import your TED function

def load_dom(path):
    with open(path, "r") as f:
        data = json.load(f)
        return data.get("dom", data)  # Support old and new formats

def dom_score(test_dom_path, brand_dom_path):
    test_dom = load_dom(test_dom_path)
    brand_dom = load_dom(brand_dom_path)

    dist = tree_edit_distance(test_dom, brand_dom)
    score = np.exp(-dist / 100)  # Tune scaling factor if needed
    return float(score)
