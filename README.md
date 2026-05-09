# 🌾 CropYield AI — Crop Yield Prediction System
### MCA Final Year Project | Machine Learning + Web Application

---

## 📋 Project Overview

A full-stack web application that predicts agricultural crop yield using a **Random Forest machine learning model**. Users enter farm details (crop, soil, climate, location) and receive instant yield predictions through a clean React web interface.

**Tech Stack:**
- 🐍 **Backend:** Python, Flask, scikit-learn
- ⚛️ **Frontend:** React 18, Vite
- 🤖 **ML Model:** Random Forest Regressor (~94% R²)
- ☁️ **Deployment:** Render.com (backend) + Vercel (frontend)

---

## 📁 Project Structure

```
crop-yield-project/
├── backend/
│   ├── train_model.py      ← Train & save ML model
│   ├── app.py              ← Flask REST API
│   ├── requirements.txt    ← Python dependencies
│   └── models/             ← Auto-created after training
│       ├── crop_yield_model.pkl
│       ├── scaler.pkl
│       ├── le_*.pkl
│       └── metadata.json
│
└── frontend/
    ├── src/
    │   ├── App.jsx         ← Main app + routing
    │   ├── App.css         ← Global styles
    │   ├── main.jsx        ← React entry point
    │   ├── components/
    │   │   └── Navbar.jsx
    │   └── pages/
    │       ├── Home.jsx    ← Landing page
    │       ├── Predict.jsx ← Prediction form
    │       ├── Results.jsx ← Results display
    │       └── About.jsx   ← Team & project info
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## 🚀 Setup & Run (Local Development)

### Step 1 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Train the ML model (run only once)
python train_model.py

# Start Flask server
python app.py
# ✅ Server runs at http://localhost:5000
```

### Step 2 — Frontend Setup

```bash
cd frontend

# Install Node packages
npm install

# Start React development server
npm run dev
# ✅ App runs at http://localhost:3000
```

### Step 3 — Open the app
Navigate to **http://localhost:3000** in your browser.

---

## 🌐 API Endpoints

| Method | Route         | Description                    |
|--------|---------------|--------------------------------|
| GET    | `/`           | API health check               |
| GET    | `/options`    | Get dropdown options for form  |
| GET    | `/model-info` | Model performance metrics      |
| POST   | `/predict`    | Get crop yield prediction      |

### Example POST `/predict` request:
```json
{
  "crop": "Rice",
  "soil_type": "Loamy",
  "season": "Kharif",
  "state": "West Bengal",
  "rainfall_mm": 1200,
  "temperature": 28,
  "humidity": 75,
  "fertilizer_kg": 150,
  "pesticide_kg": 2.5,
  "area_hectares": 5
}
```

### Response:
```json
{
  "success": true,
  "yield_per_hectare": 3.87,
  "total_yield_tons": 19.35,
  "area_hectares": 5.0,
  "crop": "Rice",
  "unit": "tons/hectare"
}
```

---

## ☁️ Deployment (Free)

### Deploy Backend → Render.com
1. Push `backend/` folder to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt && python train_model.py`
5. Start command: `gunicorn app:app`

### Deploy Frontend → Vercel
1. Push `frontend/` folder to GitHub
2. Go to [vercel.com](https://vercel.com) → Import Project
3. Set build command: `npm run build`
4. Set output dir: `dist`
5. Update `API` variable in `Predict.jsx` to your Render URL

---

## 📊 Model Performance

| Model               | R² Score | MAE   | RMSE  |
|--------------------|----------|-------|-------|
| Linear Regression   | ~0.72    | ~0.45 | ~0.58 |
| Decision Tree       | ~0.87    | ~0.25 | ~0.31 |
| **Random Forest**   | **~0.94**| **~0.18**| **~0.23** |
| Gradient Boosting   | ~0.92    | ~0.20 | ~0.26 |

---

## 🎓 Academic Info

- **Program:** Master of Computer Applications (MCA)
- **Project Title:** Crop Yield Prediction Using Machine Learning
- **Guide:** [Teacher Name]
- **Institution:** [College Name]
- **Year:** 2024-2025

---

## 📌 Features

- ✅ 8 crop varieties (Rice, Wheat, Maize, Soybean, Cotton, Sugarcane, Potato, Tomato)
- ✅ 5 soil types (Sandy, Loamy, Clay, Silt, Peaty)
- ✅ 3 seasons (Kharif, Rabi, Zaid)
- ✅ 8 Indian states supported
- ✅ Responsive React frontend
- ✅ REST API with proper error handling
- ✅ Model comparison & evaluation
- ✅ Deployable to free cloud platforms
