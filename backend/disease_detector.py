"""
Crop Disease Detection from Leaf Image
=======================================
Uses color & texture analysis to detect common crop diseases.
In production, replace with a trained CNN (PlantVillage dataset).

Install: pip install opencv-python Pillow
"""

import cv2
import numpy as np
import base64


DISEASE_PROFILES = {
    "Healthy": {
        "description": "Leaf appears healthy with normal green coloration.",
        "severity": "None",
        "color_emoji": "🟢",
        "green_ratio_min": 0.45,
        "treatment": "No treatment needed. Continue regular care.",
        "prevention": "Maintain proper spacing, irrigation and balanced fertilization.",
    },
    "Late Blight": {
        "description": "Dark brown/black water-soaked lesions on leaves. Caused by Phytophthora infestans.",
        "severity": "High",
        "color_emoji": "🔴",
        "affected_crops": ["Potato", "Tomato"],
        "treatment": "Spray Mancozeb 75% WP @ 2 kg/ha or Cymoxanil + Mancozeb.",
        "prevention": "Use resistant varieties, avoid overhead irrigation, remove infected plants.",
    },
    "Leaf Rust": {
        "description": "Orange-brown pustules on leaf surface. Caused by Puccinia sp.",
        "severity": "Moderate",
        "color_emoji": "🟠",
        "affected_crops": ["Wheat", "Rice", "Maize"],
        "treatment": "Propiconazole 25% EC @ 500 ml/ha or Tebuconazole.",
        "prevention": "Grow resistant varieties. Timely fungicide application.",
    },
    "Powdery Mildew": {
        "description": "White powdery coating on leaves. Caused by Erysiphe sp.",
        "severity": "Moderate",
        "color_emoji": "🟡",
        "affected_crops": ["Wheat", "Vegetable crops"],
        "treatment": "Sulphur 80% WP @ 2 kg/ha or Hexaconazole 5% EC.",
        "prevention": "Avoid excess nitrogen, ensure good air circulation.",
    },
    "Bacterial Leaf Blight": {
        "description": "Water-soaked yellowing along leaf margins, wilting. Caused by Xanthomonas.",
        "severity": "High",
        "color_emoji": "🔴",
        "affected_crops": ["Rice", "Cotton"],
        "treatment": "Copper oxychloride 50% WP @ 3 kg/ha. Remove infected plants.",
        "prevention": "Use certified disease-free seed, balanced fertilization.",
    },
    "Nutrient Deficiency": {
        "description": "Yellowing (chlorosis) of leaves, often inter-veinal. Indicates N, Fe or Mg deficiency.",
        "severity": "Low-Moderate",
        "color_emoji": "🟡",
        "affected_crops": ["All crops"],
        "treatment": "Soil test and apply deficient nutrient. Foliar spray of micronutrients.",
        "prevention": "Regular soil testing, balanced fertilization with NPK + micronutrients.",
    },
}


def analyze_disease(image_bytes: bytes, crop: str = "Unknown") -> dict:
    """
    Analyze crop leaf image for disease detection.
    Returns disease name, severity, treatment and confidence.
    """
    try:
        img_array = np.frombuffer(image_bytes, np.uint8)
        img_bgr   = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            return {"error": "Could not read image. Please upload a clear leaf photo."}

        img_bgr = cv2.resize(img_bgr, (256, 256))

        # ── Color analysis in HSV ──
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # Green pixels (healthy leaf tissue)
        green_mask  = cv2.inRange(img_hsv, (35, 40, 40), (85, 255, 255))
        green_ratio = float(np.sum(green_mask > 0)) / (256 * 256)

        # Brown/dark pixels (necrosis, blight)
        brown_mask  = cv2.inRange(img_hsv, (5, 50, 30), (25, 200, 150))
        brown_ratio = float(np.sum(brown_mask > 0)) / (256 * 256)

        # Orange-rust pixels
        rust_mask   = cv2.inRange(img_hsv, (8, 100, 100), (20, 255, 220))
        rust_ratio  = float(np.sum(rust_mask > 0)) / (256 * 256)

        # White/pale pixels (powdery mildew)
        white_mask  = cv2.inRange(img_hsv, (0, 0, 200), (180, 40, 255))
        white_ratio = float(np.sum(white_mask > 0)) / (256 * 256)

        # Yellow pixels (nutrient deficiency / blight)
        yellow_mask = cv2.inRange(img_hsv, (22, 60, 120), (38, 255, 255))
        yellow_ratio = float(np.sum(yellow_mask > 0)) / (256 * 256)

        # ── Disease classification logic ──
        if green_ratio > 0.50 and brown_ratio < 0.08 and rust_ratio < 0.05:
            disease    = "Healthy"
            confidence = min(90, int(green_ratio * 130))
        elif rust_ratio > 0.10:
            disease    = "Leaf Rust"
            confidence = min(88, int(rust_ratio * 400))
        elif brown_ratio > 0.25:
            disease    = "Late Blight"
            confidence = min(87, int(brown_ratio * 250))
        elif white_ratio > 0.15:
            disease    = "Powdery Mildew"
            confidence = min(85, int(white_ratio * 350))
        elif yellow_ratio > 0.20 and green_ratio < 0.30:
            disease    = "Bacterial Leaf Blight"
            confidence = min(82, int(yellow_ratio * 280))
        elif yellow_ratio > 0.12:
            disease    = "Nutrient Deficiency"
            confidence = min(80, int(yellow_ratio * 300))
        else:
            disease    = "Healthy"
            confidence = 62

        profile = DISEASE_PROFILES.get(disease, DISEASE_PROFILES["Healthy"])

        # Thumbnail
        _, enc    = cv2.imencode('.jpg', cv2.resize(img_bgr, (120, 120)))
        thumb_b64 = base64.b64encode(enc.tobytes()).decode()

        return {
            "disease":        disease,
            "confidence":     confidence,
            "severity":       profile["severity"],
            "color_emoji":    profile["color_emoji"],
            "description":    profile["description"],
            "treatment":      profile["treatment"],
            "prevention":     profile["prevention"],
            "affected_crops": profile.get("affected_crops", ["All crops"]),
            "thumbnail_b64":  thumb_b64,
            "pixel_analysis": {
                "green_%":  round(green_ratio * 100, 1),
                "brown_%":  round(brown_ratio * 100, 1),
                "rust_%":   round(rust_ratio * 100, 1),
                "yellow_%": round(yellow_ratio * 100, 1),
                "white_%":  round(white_ratio * 100, 1),
            },
            "crop": crop
        }

    except Exception as e:
        return {"error": str(e)}