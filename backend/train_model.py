"""
Crop Yield Prediction - Model Training Script
=============================================
Run this script once to train and save the ML model.
Usage: 
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import json
import os

# ─────────────────────────────────────────────
# 1. GENERATE SYNTHETIC DATASET
#    (Replace this with your real CSV dataset)
# ─────────────────────────────────────────────

np.random.seed(42)
n = 2000

crops      = ['Rice', 'Wheat', 'Maize', 'Soybean', 'Cotton', 'Sugarcane', 'Potato', 'Tomato']
soils      = ['Sandy', 'Loamy', 'Clay', 'Silt', 'Peaty']
seasons    = ['Kharif', 'Rabi', 'Zaid']
states     = ['West Bengal', 'Punjab', 'UP', 'Maharashtra', 'Karnataka', 'Bihar', 'MP', 'Haryana']

data = {
    'crop':         np.random.choice(crops, n),
    'soil_type':    np.random.choice(soils, n),
    'season':       np.random.choice(seasons, n),
    'state':        np.random.choice(states, n),
    'rainfall_mm':  np.random.uniform(300, 2500, n),
    'temperature':  np.random.uniform(15, 45, n),
    'humidity':     np.random.uniform(30, 95, n),
    'fertilizer_kg':np.random.uniform(50, 400, n),
    'pesticide_kg': np.random.uniform(0.5, 10, n),
    'area_hectares':np.random.uniform(1, 100, n),
}

df = pd.DataFrame(data)

# Simulate yield based on features (realistic relationships)
base_yield = {
    'Rice': 3.5, 'Wheat': 3.0, 'Maize': 4.0, 'Soybean': 2.0,
    'Cotton': 1.5, 'Sugarcane': 60.0, 'Potato': 20.0, 'Tomato': 25.0
}
df['base'] = df['crop'].map(base_yield)
df['yield_tons_per_hectare'] = (
    df['base']
    + (df['rainfall_mm'] - 900) * 0.001
    + (df['fertilizer_kg'] - 200) * 0.003
    - abs(df['temperature'] - 28) * 0.05
    + (df['humidity'] - 60) * 0.01
    + np.random.normal(0, 0.3, n)
).clip(lower=0.1)

df.drop(columns=['base'], inplace=True)

print(f"✅ Dataset created: {df.shape[0]} rows × {df.shape[1]} columns")
print(df.head())

# ─────────────────────────────────────────────
# 2. PREPROCESSING
# ─────────────────────────────────────────────

le_crop    = LabelEncoder()
le_soil    = LabelEncoder()
le_season  = LabelEncoder()
le_state   = LabelEncoder()

df['crop_enc']   = le_crop.fit_transform(df['crop'])
df['soil_enc']   = le_soil.fit_transform(df['soil_type'])
df['season_enc'] = le_season.fit_transform(df['season'])
df['state_enc']  = le_state.fit_transform(df['state'])

FEATURES = ['crop_enc', 'soil_enc', 'season_enc', 'state_enc',
            'rainfall_mm', 'temperature', 'humidity',
            'fertilizer_kg', 'pesticide_kg', 'area_hectares']

X = df[FEATURES]
y = df['yield_tons_per_hectare']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ─────────────────────────────────────────────
# 3. TRAIN & COMPARE MODELS
# ─────────────────────────────────────────────

models = {
    'Linear Regression':    LinearRegression(),
    'Decision Tree':        DecisionTreeRegressor(max_depth=8, random_state=42),
    'Random Forest':        RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'Gradient Boosting':    GradientBoostingRegressor(n_estimators=100, random_state=42),
}

results = {}
print("\n📊 Model Comparison:")
print(f"{'Model':<25} {'R² Score':>10} {'MAE':>10} {'RMSE':>10}")
print("─" * 60)

best_model = None
best_r2    = -np.inf

for name, model in models.items():
    model.fit(X_train_sc, y_train)
    preds  = model.predict(X_test_sc)
    r2     = r2_score(y_test, preds)
    mae    = mean_absolute_error(y_test, preds)
    rmse   = np.sqrt(mean_squared_error(y_test, preds))
    results[name] = {'r2': round(r2, 4), 'mae': round(mae, 4), 'rmse': round(rmse, 4)}
    print(f"{name:<25} {r2:>10.4f} {mae:>10.4f} {rmse:>10.4f}")
    if r2 > best_r2:
        best_r2    = r2
        best_model = model
        best_name  = name

print(f"\n🏆 Best model: {best_name} (R² = {best_r2:.4f})")

# ─────────────────────────────────────────────
# 4. SAVE MODEL + ARTIFACTS
# ─────────────────────────────────────────────

os.makedirs('models', exist_ok=True)

joblib.dump(best_model, 'models/crop_yield_model.pkl')
joblib.dump(scaler,     'models/scaler.pkl')
joblib.dump(le_crop,    'models/le_crop.pkl')
joblib.dump(le_soil,    'models/le_soil.pkl')
joblib.dump(le_season,  'models/le_season.pkl')
joblib.dump(le_state,   'models/le_state.pkl')

# Save metadata for the API
metadata = {
    'crops':    list(le_crop.classes_),
    'soils':    list(le_soil.classes_),
    'seasons':  list(le_season.classes_),
    'states':   list(le_state.classes_),
    'features': FEATURES,
    'best_model': best_name,
    'metrics':  results[best_name],
    'all_results': results
}
with open('models/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("\n✅ All files saved to /models/")
print("   • crop_yield_model.pkl")
print("   • scaler.pkl")
print("   • le_crop.pkl / le_soil.pkl / le_season.pkl / le_state.pkl")
print("   • metadata.json")
print("\nNow run: python app.py")
