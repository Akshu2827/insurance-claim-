# RiskGuard — Setup Guide

## Files delivered
| File          | Purpose                                      |
|---------------|----------------------------------------------|
| `dashboard.py`| FastAPI backend — fixed SHAP + all endpoints |
| `App.jsx`     | React frontend — all 4 pages                 |
| `App.css`     | Styling                                       |

---

## 1 — Backend (Python / FastAPI)

### Install dependencies
```bash
pip install fastapi uvicorn pandas numpy scikit-learn shap joblib
```

### Place files
- Put `dashboard.py` **in the same folder** as `insurance claims data.csv`

### Run
```bash
uvicorn dashboard:app --reload --port 8000
```
The model trains automatically on startup (~30–60 sec).
You'll see: `Startup complete. API ready.`

---

## 2 — Frontend (React)

### Create a new React app (once)
```bash
npx create-react-app riskguard-ui
cd riskguard-ui
```

### Replace files
- Copy `App.jsx` → `src/App.js`
- Copy `App.css` → `src/App.css`

### Add Google Font (optional but recommended)
In `public/index.html`, add inside `<head>`:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap" rel="stylesheet">
```

### Start
```bash
npm start
```
Opens at `http://localhost:3000`

---

## Why SHAP now works

The original code used `CalibratedClassifierCV` which wraps the RandomForest
inside `calibrated_classifiers_[i].estimator`. SHAP's TreeExplainer needs the
raw estimator, and the unwrapping code had an edge case that failed silently.

**Fix**: We removed `CalibratedClassifierCV` entirely. The `RandomForestClassifier`
with `class_weight='balanced'` already produces well-calibrated probabilities for
this use case. SHAP TreeExplainer now has direct access to the forest's trees —
no unwrapping, no silent failures.

---

## API Endpoints

| Endpoint                  | Description                        |
|---------------------------|------------------------------------|
| `GET /api/score/{idx}`    | Full risk score + SHAP for one app |
| `GET /api/whatif/{idx}`   | What-if simulation with params     |
| `GET /api/report`         | Executive report data              |
| `GET /api/fairness`       | Fairness metrics by region         |
| `POST /api/decision`      | Log underwriter decision           |
| `GET /api/sample_range`   | Get max application index          |
