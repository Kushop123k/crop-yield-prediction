"""
CropYield AI — Flask REST API (Advanced Edition)
=================================================
Endpoints:
  GET  /                  Health check
  GET  /options           Dropdown options
  GET  /model-info        ML model metrics
  POST /predict           Yield prediction
  POST /soil-analyze      Soil image analysis
  POST /disease-detect    Crop disease detection
  GET  /seeds             Seed variety recommendations
  GET  /weather           Live weather for West Bengal districts
  GET  /fertilizer        Fertilizer & pesticide guide
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib, numpy as np, json, os, urllib.request

app = Flask(__name__)
CORS(app)

MODEL_DIR = 'models'

def load_artifacts():
    arts = {}
    try:
        arts['model']     = joblib.load(f'{MODEL_DIR}/crop_yield_model.pkl')
        arts['scaler']    = joblib.load(f'{MODEL_DIR}/scaler.pkl')
        arts['le_crop']   = joblib.load(f'{MODEL_DIR}/le_crop.pkl')
        arts['le_soil']   = joblib.load(f'{MODEL_DIR}/le_soil.pkl')
        arts['le_season'] = joblib.load(f'{MODEL_DIR}/le_season.pkl')
        arts['le_state']  = joblib.load(f'{MODEL_DIR}/le_state.pkl')
        with open(f'{MODEL_DIR}/metadata.json') as f:
            arts['metadata'] = json.load(f)
        print("Model loaded")
    except FileNotFoundError:
        print("Run train_model.py first")
    return arts

artifacts = load_artifacts()

try:
    from soil_analyzer    import analyze_soil_image
    from disease_detector import analyze_disease
    IMAGE_MODULES = True
except ImportError:
    IMAGE_MODULES = False

from seed_recommender import get_seed_recommendations, FERTILIZER_DATABASE, PESTICIDE_DATABASE


@app.route('/', methods=['GET'])
def home():
    return jsonify({'name':'CropYield AI API','version':'2.0','status':'running','image_features':IMAGE_MODULES})

@app.route('/options', methods=['GET'])
def options():
    if 'metadata' not in artifacts: return jsonify({'error':'Model not loaded'}),500
    meta = artifacts['metadata']
    return jsonify({'crops':meta['crops'],'soils':meta['soils'],'seasons':meta['seasons'],'states':meta['states']})

@app.route('/model-info', methods=['GET'])
def model_info():
    if 'metadata' not in artifacts: return jsonify({'error':'Model not loaded'}),500
    meta = artifacts['metadata']
    return jsonify({'best_model':meta['best_model'],'metrics':meta['metrics'],'all_results':meta['all_results']})

@app.route('/predict', methods=['POST'])
def predict():
    if 'model' not in artifacts: return jsonify({'error':'Run train_model.py first'}),500
    try:
        data = request.get_json()
        required = ['crop','soil_type','season','state','rainfall_mm','temperature','humidity','fertilizer_kg','pesticide_kg','area_hectares']
        missing = [f for f in required if f not in data]
        if missing: return jsonify({'error':f'Missing: {missing}'}),400
        features = np.array([[
            artifacts['le_crop'].transform([data['crop']])[0],
            artifacts['le_soil'].transform([data['soil_type']])[0],
            artifacts['le_season'].transform([data['season']])[0],
            artifacts['le_state'].transform([data['state']])[0],
            float(data['rainfall_mm']),float(data['temperature']),float(data['humidity']),
            float(data['fertilizer_kg']),float(data['pesticide_kg']),float(data['area_hectares']),
        ]])
        pred = artifacts['model'].predict(artifacts['scaler'].transform(features))[0]
        seeds = get_seed_recommendations(data['crop'],data['season'],data['state'])
        return jsonify({'success':True,'yield_per_hectare':round(float(pred),2),
                        'total_yield_tons':round(float(pred*float(data['area_hectares'])),2),
                        'area_hectares':float(data['area_hectares']),'crop':data['crop'],'unit':'tons/hectare',
                        'top_varieties':seeds['varieties'][:2],'fertilizer_guide':seeds['fertilizer']})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/soil-analyze', methods=['POST'])
def soil_analyze():
    if not IMAGE_MODULES: return jsonify({'error':'pip install opencv-python Pillow'}),503
    if 'image' not in request.files: return jsonify({'error':'No image file (key: image)'}),400
    result = analyze_soil_image(request.files['image'].read())
    return jsonify(result)

@app.route('/disease-detect', methods=['POST'])
def disease_detect():
    if not IMAGE_MODULES: return jsonify({'error':'pip install opencv-python Pillow'}),503
    if 'image' not in request.files: return jsonify({'error':'No image file (key: image)'}),400
    result = analyze_disease(request.files['image'].read(), request.form.get('crop','Unknown'))
    return jsonify(result)

@app.route('/seeds', methods=['GET'])
def seeds():
    return jsonify(get_seed_recommendations(
        request.args.get('crop','Rice'),
        request.args.get('season','Kharif'),
        request.args.get('state','West Bengal')
    ))

WB_DISTRICTS = {
    "Kolkata":{"lat":22.5726,"lon":88.3639},"Darjeeling":{"lat":27.0360,"lon":88.2627},
    "Siliguri":{"lat":26.7271,"lon":88.3953},"Murshidabad":{"lat":24.1800,"lon":88.2700},
    "Burdwan":{"lat":23.2324,"lon":87.8615},"Midnapore":{"lat":22.4224,"lon":87.3191},
    "Howrah":{"lat":22.5958,"lon":88.2636},"Bankura":{"lat":23.2300,"lon":87.0700},
    "Purulia":{"lat":23.3300,"lon":86.3600},"Cooch Behar":{"lat":26.3200,"lon":89.4500},
    "Malda":{"lat":25.0108,"lon":88.1418},"Nadia":{"lat":23.4700,"lon":88.5600},
    "Bangaon":{"lat":23.0500,"lon":88.8300},
}

@app.route('/weather', methods=['GET'])
def weather():
    district = request.args.get('district','Kolkata')
    coords   = WB_DISTRICTS.get(district, WB_DISTRICTS['Kolkata'])
    lat,lon  = coords['lat'],coords['lon']
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
               f"&timezone=Asia/Kolkata&forecast_days=7")
        with urllib.request.urlopen(url,timeout=8) as resp:
            data = json.loads(resp.read())
        current = data.get('current',{}); daily = data.get('daily',{})
        forecast = [{'date':daily['time'][i],'temp_max':daily['temperature_2m_max'][i],
                     'temp_min':daily['temperature_2m_min'][i],'rain_mm':daily['precipitation_sum'][i],
                     'wind_kmh':daily['wind_speed_10m_max'][i]} for i in range(len(daily.get('time',[])))]
        return jsonify({'district':district,'latitude':lat,'longitude':lon,
                        'current':{'temperature':current.get('temperature_2m'),
                                   'humidity':current.get('relative_humidity_2m'),
                                   'precipitation':current.get('precipitation'),
                                   'wind_speed':current.get('wind_speed_10m')},
                        'forecast_7days':forecast,'source':'Open-Meteo'})
    except Exception as e:
        return jsonify({'district':district,'error':str(e),'fallback':{'temperature':30,'humidity':78}})

@app.route('/fertilizer', methods=['GET'])
def fertilizer_guide():
    crop = request.args.get('crop','Rice')
    return jsonify({'crop':crop,'fertilizer':FERTILIZER_DATABASE.get(crop,{'N':100,'P':60,'K':40,'note':'Consult soil test.'}),'pesticides':PESTICIDE_DATABASE.get(crop,[]),'unit':'kg/hectare'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
