"""
Crop Disease Detector — CNN Edition
Uses trained MobileNetV2 (leaf_cnn_model.h5).
Falls back to improved color analysis if model not found.
"""
import cv2, numpy as np, base64, json, os

CNN_MODEL = None; CNN_CLASSES = []
try:
    import tensorflow as tf
    if os.path.exists("models/leaf_cnn_model.h5") and os.path.exists("models/leaf_classes.json"):
        CNN_MODEL = tf.keras.models.load_model("models/leaf_cnn_model.h5")
        with open("models/leaf_classes.json") as f: CNN_CLASSES = json.load(f)
        print(f"✅ Leaf CNN loaded: {CNN_CLASSES}")
    else:
        print("⚠️  Leaf CNN not found — using color fallback. Run: python train_leaf_model.py")
except ImportError:
    print("⚠️  TensorFlow not installed")

DISEASE_PROFILES = {
    "Healthy":              {"description":"Leaf appears healthy.","severity":"None","color_emoji":"🟢","affected_crops":["All crops"],"treatment":"No treatment needed. Continue regular care.","prevention":"Maintain proper spacing, irrigation and balanced fertilization."},
    "Late_Blight":          {"description":"Dark brown/black water-soaked lesions. Caused by Phytophthora infestans.","severity":"High","color_emoji":"🔴","affected_crops":["Potato","Tomato"],"treatment":"Spray Mancozeb 75% WP @ 2 kg/ha or Cymoxanil+Mancozeb.","prevention":"Use resistant varieties, avoid overhead irrigation."},
    "Leaf_Rust":            {"description":"Orange-brown pustules on leaf surface. Caused by Puccinia sp.","severity":"Moderate","color_emoji":"🟠","affected_crops":["Wheat","Rice","Maize"],"treatment":"Propiconazole 25% EC @ 500 ml/ha or Tebuconazole.","prevention":"Grow resistant varieties. Timely fungicide application."},
    "Powdery_Mildew":       {"description":"White powdery coating on leaves. Caused by Erysiphe sp.","severity":"Moderate","color_emoji":"🟡","affected_crops":["Wheat","Vegetables"],"treatment":"Sulphur 80% WP @ 2 kg/ha or Hexaconazole 5% EC.","prevention":"Avoid excess nitrogen, ensure good air circulation."},
    "Bacterial_Blight":     {"description":"Water-soaked yellowing along leaf margins. Caused by Xanthomonas.","severity":"High","color_emoji":"🔴","affected_crops":["Rice","Cotton"],"treatment":"Copper oxychloride 50% WP @ 3 kg/ha.","prevention":"Use certified disease-free seed, balanced fertilization."},
    "Nutrient_Deficiency":  {"description":"Yellowing (chlorosis) of leaves. Indicates N, Fe or Mg deficiency.","severity":"Low-Moderate","color_emoji":"🟡","affected_crops":["All crops"],"treatment":"Soil test and apply deficient nutrient. Foliar spray micronutrients.","prevention":"Regular soil testing, balanced NPK + micronutrients."},
    # PlantVillage class name variants (in case classes differ)
    "Late Blight":          {"description":"Dark brown/black lesions. Phytophthora infestans.","severity":"High","color_emoji":"🔴","affected_crops":["Potato","Tomato"],"treatment":"Spray Mancozeb 75% WP @ 2 kg/ha.","prevention":"Avoid overhead irrigation, remove infected plants."},
    "Leaf Rust":            {"description":"Orange pustules. Caused by Puccinia sp.","severity":"Moderate","color_emoji":"🟠","affected_crops":["Wheat","Rice"],"treatment":"Propiconazole 25% EC @ 500 ml/ha.","prevention":"Grow resistant varieties."},
    "Powdery Mildew":       {"description":"White powder on leaves.","severity":"Moderate","color_emoji":"🟡","affected_crops":["Wheat"],"treatment":"Sulphur 80% WP @ 2 kg/ha.","prevention":"Good air circulation."},
    "Bacterial Blight":     {"description":"Yellowing margins. Xanthomonas.","severity":"High","color_emoji":"🔴","affected_crops":["Rice"],"treatment":"Copper oxychloride @ 3 kg/ha.","prevention":"Certified seed."},
    "Nutrient Deficiency":  {"description":"Leaf chlorosis. Nutrient deficiency.","severity":"Low-Moderate","color_emoji":"🟡","affected_crops":["All crops"],"treatment":"Apply deficient nutrient based on soil test.","prevention":"Balanced fertilization."},
}

def _color_fallback(img_bgr, crop):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    bg   = cv2.inRange(hsv,(36,60,60),(85,255,255))
    leaf = cv2.bitwise_not(bg)
    dark = cv2.inRange(hsv,(0,0,0),(180,255,30))
    leaf = cv2.bitwise_and(leaf,cv2.bitwise_not(dark))
    tot  = float(np.sum(leaf>0)) or 1.0
    def ratio(mask): return float(np.sum(cv2.bitwise_and(mask,leaf)>0))/tot
    green  = ratio(cv2.inRange(hsv,(30,30,40),(85,180,200)))
    brown  = ratio(cv2.inRange(hsv,(5,40,30),(22,220,180)))
    dark_b = ratio(cv2.inRange(hsv,(0,20,15),(25,200,80)))
    rust   = ratio(cv2.inRange(hsv,(8,100,100),(20,255,220)))
    white  = ratio(cv2.inRange(hsv,(0,0,200),(180,40,255)))
    yellow = ratio(cv2.inRange(hsv,(22,50,120),(35,255,255)))
    dmg    = brown+dark_b+rust
    if   dmg>0.45 or dark_b>0.25: d,c="Late_Blight",   min(88,int(55+dmg*80))
    elif rust>0.12:                d,c="Leaf_Rust",      min(86,int(55+rust*250))
    elif white>0.15:               d,c="Powdery_Mildew", min(84,int(55+white*200))
    elif yellow>0.20 and green<0.25:d,c="Bacterial_Blight",min(82,int(55+yellow*150))
    elif yellow>0.12 or (brown>0.10 and green<0.40): d,c="Nutrient_Deficiency",min(80,int(55+(yellow+brown)*100))
    elif dmg>0.15:                 d,c="Late_Blight",   min(76,int(55+dmg*120))
    elif green>0.50 and dmg<0.05:  d,c="Healthy",        min(90,int(60+green*60))
    else:                          d,c="Healthy",        60
    scores={"green_%":round(green*100,1),"brown_%":round(brown*100,1),"dark_%":round(dark_b*100,1),"rust_%":round(rust*100,1),"yellow_%":round(yellow*100,1),"white_%":round(white*100,1),"damage_%":round(dmg*100,1)}
    return d,c,scores,"Color Analysis (fallback)"

def analyze_disease(image_bytes:bytes, crop:str="Unknown")->dict:
    try:
        img=cv2.imdecode(np.frombuffer(image_bytes,np.uint8),cv2.IMREAD_COLOR)
        if img is None: return {"error":"Cannot read image."}
        img=cv2.resize(img,(224,224))
        if CNN_MODEL is not None:
            rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            preds=CNN_MODEL.predict(np.expand_dims(rgb/255.0,0).astype(np.float32),verbose=0)[0]
            disease=CNN_CLASSES[int(np.argmax(preds))]; conf=int(np.max(preds)*100)
            scores={CNN_CLASSES[i]:round(float(preds[i])*100,1) for i in range(len(CNN_CLASSES))}
            method="CNN (MobileNetV2)"
            pixel_analysis=scores
        else:
            disease,conf,pixel_analysis,method=_color_fallback(img,crop)
        profile=DISEASE_PROFILES.get(disease,DISEASE_PROFILES["Healthy"])
        _,enc=cv2.imencode('.jpg',cv2.resize(img,(120,120)))
        return {"disease":disease,"confidence":conf,"method":method,
                "severity":profile["severity"],"color_emoji":profile["color_emoji"],
                "description":profile["description"],"treatment":profile["treatment"],
                "prevention":profile["prevention"],"affected_crops":profile.get("affected_crops",["All"]),
                "pixel_analysis":pixel_analysis,"crop":crop,
                "thumbnail_b64":base64.b64encode(enc.tobytes()).decode()}
    except Exception as e:
        return {"error":str(e)}