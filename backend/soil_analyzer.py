"""
Soil Image Analyzer — CNN Edition
Uses trained MobileNetV2 (soil_cnn_model.h5).
Falls back to color analysis if model not found.
"""
import cv2, numpy as np, base64, json, os

CNN_MODEL = None; CNN_CLASSES = []
try:
    import tensorflow as tf
    if os.path.exists("models/soil_cnn_model.h5") and os.path.exists("models/soil_classes.json"):
        CNN_MODEL = tf.keras.models.load_model("models/soil_cnn_model.h5")
        with open("models/soil_classes.json") as f: CNN_CLASSES = json.load(f)
        print(f"✅ Soil CNN loaded: {CNN_CLASSES}")
    else:
        print("⚠️  Soil CNN not found — using color fallback. Run: python train_soil_model.py")
except ImportError:
    print("⚠️  TensorFlow not installed")

SOIL_INFO = {
    "Sandy":{"description":"Light-colored, loose, gritty. Very low water retention.","fertility":"Low","water_retention":"Very Low","ph_range":"5.5–7.0","color_hint":"Light yellow/beige","crops":["Groundnut","Watermelon","Potato","Cassava"],"tips":"Add organic matter. Frequent irrigation needed.","hue_range":(15,35),"sat_range":(20,120),"val_range":(160,255)},
    "Loamy":{"description":"Dark brown, crumbly mix. Best farming soil.","fertility":"High","water_retention":"Moderate","ph_range":"6.0–7.0","color_hint":"Dark brown","crops":["Rice","Wheat","Maize","Vegetables","Cotton"],"tips":"Ideal soil. Maintain with crop rotation.","hue_range":(8,22),"sat_range":(80,200),"val_range":(60,150)},
    "Clay": {"description":"Heavy, sticky, reddish-grey. High nutrients, poor drainage.","fertility":"High","water_retention":"High","ph_range":"6.0–8.0","color_hint":"Reddish grey","crops":["Rice","Sugarcane","Wheat","Jute"],"tips":"Add sand/compost for drainage. Avoid overwatering.","hue_range":(0,12),"sat_range":(30,160),"val_range":(60,130)},
    "Silt": {"description":"Fine, smooth, greyish. Fertile but compacts easily.","fertility":"Moderate-High","water_retention":"High","ph_range":"6.0–7.5","color_hint":"Light grey","crops":["Rice","Vegetables","Wheat","Barley"],"tips":"Add organic matter to prevent compaction.","hue_range":(10,30),"sat_range":(5,60),"val_range":(140,220)},
    "Peaty":{"description":"Very dark, spongy, high organic matter.","fertility":"Moderate","water_retention":"Very High","ph_range":"3.5–6.0","color_hint":"Almost black","crops":["Vegetables","Root crops","Potatoes"],"tips":"Acidic — add lime. Good organic base.","hue_range":(5,20),"sat_range":(40,130),"val_range":(20,80)},
}

def _range_score(v, r):
    lo,hi=r; mid=(lo+hi)/2; w=(hi-lo)/2 or 1
    return max(0.0, 1.0-abs(v-mid)/(w*2))

def _color_fallback(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,(0,10,20),(180,255,235))
    mh=float(np.mean(hsv[:,:,0][mask>0]) if mask.any() else np.mean(hsv[:,:,0]))
    ms=float(np.mean(hsv[:,:,1][mask>0]) if mask.any() else np.mean(hsv[:,:,1]))
    mv=float(np.mean(hsv[:,:,2][mask>0]) if mask.any() else np.mean(hsv[:,:,2]))
    scores={s:(_range_score(mh,p["hue_range"])*0.4+_range_score(ms,p["sat_range"])*0.3+_range_score(mv,p["val_range"])*0.3) for s,p in SOIL_INFO.items()}
    best=max(scores,key=scores.get); total=sum(scores.values()) or 1
    return best, min(75,max(50,int((scores[best]/total)*300))), {k:round(v/total*100,1) for k,v in scores.items()}, "Color Analysis (fallback)"

def analyze_soil_image(image_bytes:bytes)->dict:
    try:
        img=cv2.imdecode(np.frombuffer(image_bytes,np.uint8),cv2.IMREAD_COLOR)
        if img is None: return {"error":"Cannot read image."}
        img=cv2.resize(img,(224,224))
        if CNN_MODEL is not None:
            rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            preds=CNN_MODEL.predict(np.expand_dims(rgb/255.0,0).astype(np.float32),verbose=0)[0]
            soil=CNN_CLASSES[int(np.argmax(preds))]; conf=int(np.max(preds)*100)
            scores={CNN_CLASSES[i]:round(float(preds[i])*100,1) for i in range(len(CNN_CLASSES))}
            method="CNN (MobileNetV2)"
        else:
            soil,conf,scores,method=_color_fallback(img)
        info=SOIL_INFO.get(soil,{})
        _,enc=cv2.imencode('.jpg',cv2.resize(img,(120,120)))
        return {"soil_type":soil,"confidence":conf,"method":method,"description":info.get("description",""),
                "fertility":info.get("fertility","—"),"water_retention":info.get("water_retention","—"),
                "ph_range":info.get("ph_range","—"),"color_hint":info.get("color_hint","—"),
                "recommended_crops":info.get("crops",[]),"tips":info.get("tips",""),
                "thumbnail_b64":base64.b64encode(enc.tobytes()).decode(),"all_scores":scores}
    except Exception as e:
        return {"error":str(e)}