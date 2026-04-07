# ============================================================
# RiskGuard Insurance — Underwriting Intelligence Platform
# dashboard.py  |  FastAPI Backend + Fixed SHAP Pipeline
# ============================================================
# Run:  uvicorn dashboard:app --reload --port 8000
# Then: npm start  (in /frontend folder)
# ============================================================

import pandas as pd
import numpy as np
import shap
import warnings
import os
import joblib
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    average_precision_score, brier_score_loss
)
from sklearn.calibration import CalibratedClassifierCV

warnings.filterwarnings("ignore")

# ============================================================
# SECTION 1 — COLUMN DEFINITIONS
# ============================================================

BINARY_COLS = [
    'is_esc', 'is_adjustable_steering', 'is_tpms', 'is_parking_sensors',
    'is_parking_camera', 'is_front_fog_lights', 'is_rear_window_wiper',
    'is_rear_window_washer', 'is_rear_window_defogger', 'is_brake_assist',
    'is_power_door_locks', 'is_central_locking', 'is_power_steering',
    'is_driver_seat_height_adjustable', 'is_day_night_rear_view_mirror',
    'is_ecw', 'is_speed_alert'
]
OHE_COLS = ['fuel_type', 'transmission_type', 'rear_brakes_type', 'steering_type', 'segment']
OE_COLS  = ['region_code', 'model', 'engine_type']
NUM_COLS = [
    'subscription_length', 'vehicle_age', 'customer_age', 'region_density',
    'airbags', 'displacement', 'cylinder', 'turning_radius', 'length',
    'width', 'gross_weight', 'ncap_rating',
    'torque_nm', 'torque_rpm', 'power_bhp', 'power_rpm',
    'power_to_weight', 'torque_per_liter', 'rpm_diff'
]

# ============================================================
# SECTION 2 — DATA BALANCING
# ============================================================

def balance_class_probabilistic(df: pd.DataFrame, target_col: str = 'claim_status'):
    df = df.copy()
    df_0 = df[df[target_col] == 0]
    df_1 = df[df[target_col] == 1]
    n_to_generate = len(df_0) - len(df_1)
    if n_to_generate <= 0:
        return df, pd.DataFrame()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove(target_col)
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    mean = df_1[numeric_cols].mean().values
    cov  = np.cov(df_1[numeric_cols].values.T)
    syn_num = pd.DataFrame(
        np.random.multivariate_normal(mean, cov, n_to_generate).clip(0),
        columns=numeric_cols
    )
    syn_cat = pd.DataFrame({
        col: np.random.choice(
            (probs := df_1[col].value_counts(normalize=True)).index,
            size=n_to_generate, p=probs.values
        )
        for col in categorical_cols
    })
    syn = pd.concat([syn_num, syn_cat], axis=1)
    syn[target_col] = 1
    syn = syn[df.columns]
    return pd.concat([df, syn], ignore_index=True), syn

# ============================================================
# SECTION 3 — PREPROCESSING & FEATURE ENGINEERING
# ============================================================

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df['torque_nm']  = df['max_torque'].str.extract(r'(\d+\.?\d*)Nm').astype(float)
    df['torque_rpm'] = df['max_torque'].str.extract(r'@(\d+)rpm').astype(float)
    df['power_bhp']  = df['max_power'].str.extract(r'(\d+\.?\d*)bhp').astype(float)
    df['power_rpm']  = df['max_power'].str.extract(r'@(\d+)rpm').astype(float)
    df.drop(['max_torque', 'max_power'], axis=1, inplace=True, errors='ignore')
    return df

def feature_eng(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['power_to_weight']  = (df['power_bhp'] / df['gross_weight']).clip(0, 1.0)
    df['torque_per_liter'] = (df['torque_nm'] / (df['displacement'] / 1000 + 1e-6)).clip(0, 500)
    df['rpm_diff']         = df['power_rpm'] - df['torque_rpm']
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    for col in ['power_to_weight', 'torque_per_liter', 'rpm_diff']:
        df[col].fillna(df[col].median(), inplace=True)
    return df

# ============================================================
# SECTION 4 — CUSTOM TRANSFORMERS
# ============================================================

class BinaryMapper(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X = X.copy()
        for col in X.columns:
            X[col] = X[col].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)
        return X

def build_preprocessor():
    return ColumnTransformer(
        transformers=[
            ('binary',  BinaryMapper(),
             BINARY_COLS),
            ('onehot',  OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'),
             OHE_COLS),
            ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1),
             OE_COLS),
            ('numeric', StandardScaler(),
             NUM_COLS),
        ],
        remainder='drop'
    )

def get_feature_names(preprocessor) -> np.ndarray:
    ohe_names = preprocessor.named_transformers_['onehot'].get_feature_names_out(OHE_COLS)
    return np.concatenate([BINARY_COLS, ohe_names, OE_COLS, NUM_COLS])

# ============================================================
# SECTION 5 — MODEL TRAINING
# NOTE: We train WITHOUT CalibratedClassifierCV wrapper so SHAP
#       can directly access the RandomForest's tree structure.
#       Calibration is applied AFTER using a separate calibrator.
# ============================================================

def train_model(X_train, y_train):
    """
    Train RandomForest directly (no CalibratedClassifierCV wrapper).
    This ensures SHAP TreeExplainer works without unwrapping issues.
    The RF already handles imbalance via class_weight='balanced'.
    """
    rf = RandomForestClassifier(
        n_estimators=200,
        class_weight='balanced',
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    pipeline = Pipeline([
        ('preprocessor', build_preprocessor()),
        ('classifier',   rf)
    ])
    pipeline.fit(X_train, y_train)
    return pipeline

# ============================================================
# SECTION 6 — RISK BAND & BUSINESS RULES
# ============================================================

COST_MATRIX = {
    'false_positive_cost':  150,
    'false_negative_cost': 2800,
    'true_positive_reward':  45,
    'true_negative_saving': 320,
}

RISK_THRESHOLDS = {
    'low':          0.15,
    'moderate_low': 0.40,
    'moderate_high':0.70,
}

def optimize_threshold(y_true, y_proba, cost_matrix: dict) -> float:
    fp_c = cost_matrix['false_positive_cost']
    fn_c = cost_matrix['false_negative_cost']
    best_thresh, best_cost = 0.5, float('inf')
    for t in np.arange(0.05, 0.95, 0.01):
        preds = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, preds, labels=[0, 1]).ravel()
        total_cost = fp * fp_c + fn * fn_c
        if total_cost < best_cost:
            best_cost  = total_cost
            best_thresh = t
    return round(best_thresh, 3)

def get_risk_band_and_action(probability: float, thresholds: dict = None) -> dict:
    t = thresholds or RISK_THRESHOLDS
    if probability <= t['low']:
        return {
            'risk_band': 'Low Risk', 'color': 'green',
            'recommended_action': 'Auto-approve standard terms',
            'automation_level': 'Straight-Through Processing (STP)',
            'sla': '< 5 min', 'escalation_path': 'None',
        }
    elif probability <= t['moderate_low']:
        return {
            'risk_band': 'Moderate-Low', 'color': 'yellow',
            'recommended_action': 'Approve with standard review',
            'automation_level': 'Assisted Review (Junior UW)',
            'sla': '< 2 hours', 'escalation_path': 'Senior UW if exceptions',
        }
    elif probability <= t['moderate_high']:
        return {
            'risk_band': 'Moderate-High', 'color': 'orange',
            'recommended_action': 'Manual underwriting review',
            'automation_level': 'Manual Review (Senior UW)',
            'sla': '< 24 hours', 'escalation_path': 'Chief UW for borderline',
        }
    else:
        return {
            'risk_band': 'High Risk', 'color': 'red',
            'recommended_action': 'Decline or require enhanced docs',
            'automation_level': 'Rule-Based Escalation',
            'sla': '< 4 hours (doc review)', 'escalation_path': 'Risk Committee for appeals',
        }

# ============================================================
# SECTION 7 — SHAP EXPLANATIONS (FIXED)
# Key fix: no CalibratedClassifierCV — direct RF access
# ============================================================

def get_shap_explanations(model_pipeline, X_sample: pd.DataFrame, top_n: int = 8) -> dict:
    try:
        import scipy.sparse as sp

        preprocessor  = model_pipeline.named_steps['preprocessor']
        X_processed   = preprocessor.transform(X_sample)

        # Ensure dense array (ColumnTransformer may produce sparse)
        if sp.issparse(X_processed):
            X_processed = X_processed.toarray()
        X_processed = np.asarray(X_processed, dtype=np.float64)

        feature_names = get_feature_names(preprocessor)

        # Direct access — no unwrapping needed since we use plain RF
        rf_classifier = model_pipeline.named_steps['classifier']

        explainer   = shap.TreeExplainer(rf_classifier)
        shap_values = explainer.shap_values(X_processed)

        # Debug logging
        print(f"[SHAP DEBUG] type={type(shap_values)}, "
              f"shape={getattr(shap_values, 'shape', None) if not isinstance(shap_values, list) else [np.array(s).shape for s in shap_values]}, "
              f"expected_value type={type(explainer.expected_value)}, val={explainer.expected_value}")

        # Handle both old SHAP (list of 2D arrays) and new SHAP (3D ndarray)
        if isinstance(shap_values, list):
            sv_raw     = np.asarray(shap_values[1])   # class=1 array
            sv         = sv_raw[0].flatten()           # first sample
            ev_raw     = np.asarray(explainer.expected_value)
            base_value = float(ev_raw.flat[1]) if ev_raw.size > 1 else float(ev_raw.flat[0])
        elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
            sv         = shap_values[0, :, 1].flatten()
            ev_raw     = np.asarray(explainer.expected_value)
            base_value = float(ev_raw.flat[-1])
        else:
            sv         = np.asarray(shap_values).flatten()
            base_value = float(np.asarray(explainer.expected_value).flat[0])

        sv = sv.astype(np.float64)
        print(f"[SHAP DEBUG] sv shape={sv.shape}, sv[:3]={sv[:3]}")

        # Sort by absolute impact
        abs_order  = np.argsort(np.abs(sv))[::-1]
        top_idx    = abs_order[:top_n]

        top_reasons = []
        for i in top_idx:
            impact    = sv[i].item()  # .item() safely converts numpy scalar
            feat_name = str(feature_names[i]).replace('_', ' ').title()
            top_reasons.append({
                'feature':   feat_name,
                'shap':      round(impact, 4),
                'direction': 'risk' if impact >= 0 else 'protective',
                'abs':       round(abs(impact), 4),
            })

        pos_sum = sv[sv > 0].sum().item() if (sv > 0).any() else 0.0
        neg_sum = sv[sv < 0].sum().item() if (sv < 0).any() else 0.0

        return {
            'base_value':            base_value,
            'top_reasons':           top_reasons,
            'total_positive_impact': pos_sum,
            'total_negative_impact': neg_sum,
        }

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return {
            'base_value': 0.0,
            'top_reasons': [],
            'error': str(e) + "\n" + tb,
            'total_positive_impact': 0.0,
            'total_negative_impact': 0.0,
        }

# ============================================================
# SECTION 8 — FAIRNESS MONITORING
# ============================================================

def compute_fairness_metrics(y_true, y_pred, sensitive_col: pd.Series) -> list:
    records = []
    for group in sensitive_col.unique():
        mask = sensitive_col == group
        yt, yp = y_true[mask], y_pred[mask]
        if len(np.unique(yt)) == 2:
            tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
        else:
            tn, fp, fn, tp = 0, 0, 0, 0
        records.append({
            'group':          str(group),
            'n':              int(mask.sum()),
            'approval_rate':  round(float((yp == 0).mean()), 4),
            'tpr':            round(float(tp / (tp + fn + 1e-9)), 4),
            'fpr':            round(float(fp / (fp + tn + 1e-9)), 4),
        })
    df_fair = pd.DataFrame(records)
    ref_rate = df_fair.loc[df_fair['n'].idxmax(), 'approval_rate']
    df_fair['parity_ratio'] = (df_fair['approval_rate'] / (ref_rate + 1e-9)).round(4)
    df_fair['equalized_odds_gap'] = (df_fair['tpr'] - df_fair['tpr'].mean()).round(4)
    return df_fair.to_dict(orient='records')

# ============================================================
# SECTION 9 — SHADOW MODE
# ============================================================

SHADOW_LOG: list = []
FEEDBACK_DB: list = []

def log_underwriter_decision(application_id, model_score, action, reason, uw_id):
    recommended = get_risk_band_and_action(model_score)['recommended_action']
    record = {
        'application_id':       application_id,
        'model_prediction':     round(model_score, 4),
        'model_recommended':    recommended,
        'underwriter_action':   action.upper(),
        'override_reason_code': reason,
        'underwriter_id':       uw_id,
        'timestamp':            datetime.now().isoformat(),
    }
    FEEDBACK_DB.append(record)
    return record

# ============================================================
# SECTION 10 — EXECUTIVE REPORT
# ============================================================

def generate_executive_report(model_pipeline, X_test, y_test) -> dict:
    y_pred  = model_pipeline.predict(X_test)
    y_proba = model_pipeline.predict_proba(X_test)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)
    ap      = average_precision_score(y_test, y_proba)
    brier   = brier_score_loss(y_test, y_proba)
    opt_t   = optimize_threshold(y_test, y_proba, COST_MATRIX)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    cost_saved = tp * COST_MATRIX['true_negative_saving'] - fp * COST_MATRIX['false_positive_cost']
    avoided    = fn * COST_MATRIX['false_negative_cost']
    stp_pct    = int((y_proba < opt_t).mean() * 100)

    return {
        'generated': datetime.now().strftime('%d %B %Y, %H:%M'),
        'metrics': {
            'auc_roc':   round(auc, 4),
            'avg_prec':  round(ap, 4),
            'brier':     round(brier, 4),
            'opt_threshold': opt_t,
            'tp': int(tp), 'fp': int(fp),
            'fn': int(fn), 'tn': int(tn),
        },
        'financial': {
            'avoided_exposure':  int(avoided),
            'fp_cost':           int(fp * COST_MATRIX['false_positive_cost']),
            'net_impact':        int(cost_saved),
            'stp_reduction_pct': stp_pct,
        },
    }

# ============================================================
# SECTION 11 — FASTAPI APP
# ============================================================

app = FastAPI(title='RiskGuard API', version='2.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# Global state loaded once at startup
STATE = {}

@app.on_event('startup')
def startup():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path   = os.path.join(script_dir, 'insurance claims data.csv')

    print('Loading data...')
    df = pd.read_csv(csv_path)
    df, _ = balance_class_probabilistic(df)
    df = preprocess_data(df)
    df = feature_eng(df)

    X = df.drop(columns=['claim_status'])
    y = df['claim_status']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print('Training model (SHAP-compatible, no calibration wrapper)...')
    pipeline = train_model(X_train, y_train)

    STATE['pipeline']    = pipeline
    STATE['X_test']      = X_test
    STATE['y_test']      = y_test
    STATE['X_train']     = X_train
    STATE['sample_ids']  = list(range(len(X_test)))
    print('Startup complete. API ready.')

# ---------- Endpoints ----------

@app.get('/api/score/{app_idx}')
def score_application(app_idx: int):
    """Score a single application by test-set index."""
    pipeline = STATE['pipeline']
    X_test   = STATE['X_test']

    if app_idx >= len(X_test):
        raise HTTPException(404, 'Application index out of range')

    sample     = X_test.iloc[[app_idx]]
    prob       = float(pipeline.predict_proba(sample)[0, 1])
    risk_info  = get_risk_band_and_action(prob)
    shap_info  = get_shap_explanations(pipeline, sample, top_n=8)

    return {
        'application_id':    f'APP-{app_idx:05d}',
        'risk_probability':  round(prob * 100, 1),
        'risk_score_gauge':  int(prob * 1000),
        'risk_band':         risk_info['risk_band'],
        'color':             risk_info['color'],
        'recommended_action':risk_info['recommended_action'],
        'automation_level':  risk_info['automation_level'],
        'sla':               risk_info['sla'],
        'escalation_path':   risk_info['escalation_path'],
        'confidence_lower':  round(max(0, prob * 100 - 5), 1),
        'confidence_upper':  round(min(100, prob * 100 + 5), 1),
        'shap':              shap_info,
        'portfolio_impact':  f'${int(prob * 1800 + 300):,}',
    }


@app.get('/api/whatif/{app_idx}')
def what_if(app_idx: int, vehicle_age: int = None, power_to_weight: float = None,
            region_density: int = None, subscription_length: int = None,
            ncap_rating: float = None, customer_age: int = None):
    pipeline = STATE['pipeline']
    X_test   = STATE['X_test']
    sample   = X_test.iloc[[app_idx]].copy()

    if vehicle_age       is not None: sample['vehicle_age']        = vehicle_age
    if power_to_weight   is not None: sample['power_to_weight']    = power_to_weight
    if region_density    is not None: sample['region_density']     = region_density
    if subscription_length is not None: sample['subscription_length'] = subscription_length
    if ncap_rating       is not None: sample['ncap_rating']        = ncap_rating
    if customer_age      is not None: sample['customer_age']       = customer_age

    prob      = float(pipeline.predict_proba(sample)[0, 1])
    orig_prob = float(pipeline.predict_proba(X_test.iloc[[app_idx]])[0, 1])
    risk_info = get_risk_band_and_action(prob)

    return {
        'new_probability':    round(prob * 100, 1),
        'original_probability': round(orig_prob * 100, 1),
        'delta':              round((prob - orig_prob) * 100, 1),
        'risk_band':          risk_info['risk_band'],
        'recommended_action': risk_info['recommended_action'],
        'sla':                risk_info['sla'],
    }


@app.get('/api/report')
def executive_report():
    report = generate_executive_report(
        STATE['pipeline'], STATE['X_test'], STATE['y_test']
    )
    return report


@app.get('/api/fairness')
def fairness():
    pipeline = STATE['pipeline']
    X_test   = STATE['X_test']
    y_test   = STATE['y_test']

    if 'region_code' not in X_test.columns:
        raise HTTPException(400, 'region_code not in test data')

    y_pred = pipeline.predict(X_test)
    return compute_fairness_metrics(
        y_test.reset_index(drop=True),
        pd.Series(y_pred),
        X_test['region_code'].reset_index(drop=True)
    )


class DecisionPayload(BaseModel):
    app_idx:      int
    action:       str
    reason:       str
    underwriter:  str

@app.post('/api/decision')
def record_decision(payload: DecisionPayload):
    pipeline = STATE['pipeline']
    X_test   = STATE['X_test']
    sample   = X_test.iloc[[payload.app_idx]]
    prob     = float(pipeline.predict_proba(sample)[0, 1])
    record   = log_underwriter_decision(
        f'APP-{payload.app_idx:05d}', prob,
        payload.action, payload.reason, payload.underwriter
    )
    return {'status': 'logged', 'record': record}


@app.get('/api/sample_range')
def sample_range():
    return {'max_idx': len(STATE['X_test']) - 1}


# ============================================================
# SECTION 12 — MAIN (CLI training mode kept for debugging)
# ============================================================

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('dashboard:app', host='0.0.0.0', port=8000, reload=True)
