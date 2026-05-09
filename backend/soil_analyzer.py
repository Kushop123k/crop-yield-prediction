"""
Soil Image Analyzer
===================
Classifies soil type from uploaded image using color & texture analysis.
In a real project this would use a trained CNN (MobileNetV2 etc.).
Here we use OpenCV color-space analysis which works well for demonstration.

Install: pip install opencv-python Pillow
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64


SOIL_PROFILES = {
    "Sandy": {
        "description": "Light-colored, loose, gritty texture. Low water retention.",
        "color_hint":  "Light yellow / beige",
        "hue_range":   (15, 35),
        "sat_range":   (20, 120),
        "val_range":   (160, 255),
        "crops":       ["Groundnut", "Watermelon", "Carrot", "Potato", "Cassava"],
        "fertility":   "Low",
        "water_retention": "Very Low",
        "ph_range":    "5.5 – 7.0",
        "tips": "Add organic matter & compost. Requires frequent irrigation."
    },
    "Loamy": {
        "description": "Dark brown, crumbly mix of sand, silt & clay. Best for farming.",
        "color_hint":  "Dark brown",
        "hue_range":   (8, 22),
        "sat_range":   (80, 200),
        "val_range":   (60, 150),
        "crops":       ["Rice", "Wheat", "Maize", "Vegetables", "Cotton", "Soybean"],
        "fertility":   "High",
        "water_retention": "Moderate",
        "ph_range":    "6.0 – 7.0",
        "tips": "Ideal soil. Maintain with crop rotation and minimal tillage."
    },
    "Clay": {
        "description": "Heavy, sticky, reddish-grey soil. High nutrient but poor drainage.",
        "color_hint":  "Reddish grey / dark grey",
        "hue_range":   (0, 12),
        "sat_range":   (30, 160),
        "val_range":   (60, 130),
        "crops":       ["Rice", "Sugarcane", "Wheat", "Mustard", "Jute"],
        "fertility":   "High",
        "water_retention": "High",
        "ph_range":    "6.0 – 8.0",
        "tips": "Improve drainage with sand/organic matter. Avoid overwatering."
    },
    "Silt": {
        "description": "Fine, smooth, greyish soil. Fertile but prone to compaction.",
        "color_hint":  "Light grey / silvery",
        "hue_range":   (10, 30),
        "sat_range":   (5, 60),
        "val_range":   (140, 220),
        "crops":       ["Rice", "Vegetables", "Wheat", "Sugarcane", "Barley"],
        "fertility":   "Moderate-High",
        "water_retention": "High",
        "ph_range":    "6.0 – 7.5",
        "tips": "Good for farming. Add organic matter to prevent compaction."
    },
    "Peaty": {
        "description": "Very dark/black, spongy, high organic matter content.",
        "color_hint":  "Almost black / very dark brown",
        "hue_range":   (5, 20),
        "sat_range":   (40, 130),
        "val_range":   (20, 80),
        "crops":       ["Vegetables", "Root crops", "Blueberries", "Potatoes"],
        "fertility":   "Moderate",
        "water_retention": "Very High",
        "ph_range":    "3.5 – 6.0",
        "tips": "Acidic — add lime to raise pH. Good organic matter base."
    },
}


def analyze_soil_image(image_bytes: bytes) -> dict:
    """
    Analyze soil image and return classified soil type with details.
    
    Args:
        image_bytes: Raw image bytes from upload
    
    Returns:
        dict with soil_type, confidence, details, crop recommendations
    """
    try:
        # Decode image
        img_array = np.frombuffer(image_bytes, np.uint8)
        img_bgr   = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            return {"error": "Could not read image. Please upload a clear soil photo."}

        # Resize for consistent analysis
        img_bgr = cv2.resize(img_bgr, (224, 224))

        # Convert to HSV color space (better for soil color analysis)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Get mean & std of H, S, V channels (ignore very dark/bright pixels)
        mask = cv2.inRange(img_hsv, (0, 10, 20), (180, 255, 235))
        mean_h = float(np.mean(img_hsv[:, :, 0][mask > 0])) if mask.any() else float(np.mean(img_hsv[:, :, 0]))
        mean_s = float(np.mean(img_hsv[:, :, 1][mask > 0])) if mask.any() else float(np.mean(img_hsv[:, :, 1]))
        mean_v = float(np.mean(img_hsv[:, :, 2][mask > 0])) if mask.any() else float(np.mean(img_hsv[:, :, 2]))

        # Score each soil type
        scores = {}
        for soil, profile in SOIL_PROFILES.items():
            h_score = _range_score(mean_h, profile["hue_range"])
            s_score = _range_score(mean_s, profile["sat_range"])
            v_score = _range_score(mean_v, profile["val_range"])
            scores[soil] = (h_score * 0.4 + s_score * 0.3 + v_score * 0.3)

        # Pick best match
        best_soil = max(scores, key=scores.get)
        raw_conf  = scores[best_soil]

        # Normalize confidence to 55–92% range (realistic for color-based analysis)
        total     = sum(scores.values()) or 1
        confidence = min(92, max(55, int((raw_conf / total) * 300)))

        profile = SOIL_PROFILES[best_soil]

        # Build thumbnail base64 for response
        _, enc = cv2.imencode('.jpg', cv2.resize(img_bgr, (120, 120)))
        thumb_b64 = base64.b64encode(enc.tobytes()).decode()

        return {
            "soil_type":        best_soil,
            "confidence":       confidence,
            "description":      profile["description"],
            "fertility":        profile["fertility"],
            "water_retention":  profile["water_retention"],
            "ph_range":         profile["ph_range"],
            "color_hint":       profile["color_hint"],
            "recommended_crops": profile["crops"],
            "tips":             profile["tips"],
            "thumbnail_b64":    thumb_b64,
            "color_analysis": {
                "hue":        round(mean_h, 1),
                "saturation": round(mean_s, 1),
                "brightness": round(mean_v, 1),
            },
            "all_scores": {k: round(v / total * 100, 1) for k, v in scores.items()}
        }

    except Exception as e:
        return {"error": str(e)}


def _range_score(value: float, range_tuple: tuple) -> float:
    lo, hi = range_tuple
    mid = (lo + hi) / 2
    width = (hi - lo) / 2 or 1
    return max(0.0, 1.0 - abs(value - mid) / (width * 2))