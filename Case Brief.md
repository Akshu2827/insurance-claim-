# RiskGuard Insurance - Intelligent Underwriting System

**Case Study | Risk Analytics & Predictive Modeling**

---

## Company Background

RiskGuard Insurance is a mid-sized insurance company struggling with:

- **Risk Assessment**: Accurately pricing policies based on individual risk profiles
- **Claims Prediction**: Identifying high-risk applicants likely to file claims
- **Fraud Detection**: Detecting potentially fraudulent claims
- **Customer Segmentation**: Distinguishing profitable vs. unprofitable customer segments

---

## Your Role

You are a **Data Scientist** on the Risk Analytics Team. Your mission is to:

1. Build predictive models for risk classification
2. Develop claims severity and frequency models
3. Create a customer risk scoring system
4. Recommend underwriting policy improvements

**Timeline**: 8 weeks  
**Stakeholders**: Chief Risk Officer, Underwriting Team, Actuarial Department, Claims Department

---

## Practice Assignment – 8-Step Data Science Framework

### 🔍 Step 1: Problem Identification

**Deliverable**: Risk Assessment Problem Brief (1-2 pages)

**Tasks**:
- Write a **SMART** objective statement for risk prediction
- Apply the **"5 Whys"** technique to understand claim patterns
- List **3 key business questions** this analysis must answer
- Identify **2 major financial risks** if risk assessment is inaccurate

**Prompt**:
> "How might we build a risk classification system that achieves ≥80% accuracy in predicting high-risk applicants while maintaining fairness across demographic groups, enabling better pricing decisions and reducing claim losses by 15%?"

**Key Considerations**:
- Business Impact on profitability and competitiveness
- Regulatory compliance (no discriminatory practices)
- Customer experience and fair treatment

---

### 📋 Step 2: Gather Requirements

**Deliverable**: Risk Analytics Requirements Specification

**Tasks**:
- Define **functional requirements** (Binary classification, Risk score 0-100, Claims probability)
- Define **data requirements** (3-5 years historical data, quality thresholds)
- Define **success metrics**:
  - Primary: **AUC-ROC ≥ 0.80**
  - Secondary: **Precision ≥ 0.75** for high-risk class
  - Constraint: Fairness metrics (Demographic Parity)
- List **constraints** (GDPR, interpretability, real-time scoring)

**Prompt**:
> "If you could only use 10 features for risk prediction, which features would provide the strongest predictive power while ensuring regulatory compliance?"

**Suggested Priority Features**:
1. Demographics (Age, Gender – if permitted)
2. Behavioral (Smoking status, Driving history)
3. Historical (Past claims frequency)
4. Geographic (Region risk levels)

---

### 🗄️ Step 3: Data Collection & Preparation

**Deliverable**: Data Processing Pipeline + EDA Report

**Tasks**:
1. Load and explore the dataset
2. Perform quality checks (missing values, outliers, inconsistencies)
3. Handle data issues:
   - Missing values strategy (Imputation vs Removal)
   - Class imbalance handling (SMOTE, Class Weights)
   - Categorical encoding (One-hot / Target Encoding)
4. Feature Engineering:
   - `claims_per_year`
   - `age_groups`
   - Interaction terms (Age × Smoking)

**Insurance-Specific Considerations**:
- Severe class imbalance (High-risk customers <20%)
- Temporal patterns in claims
- Policy censoring

---

### 📊 Step 4: Measure KPIs

**Deliverable**: Risk Model Evaluation Dashboard

**Key Metrics**:
- **Primary**: AUC-ROC
- **Business**: Loss Ratio, Combined Ratio
- **Fairness**: Demographic Parity, Equal Opportunity
- **Visualization**: ROC Curve, Precision-Recall Curve, Risk Score Distribution

**Prompt**:
> "If your model achieves 85% accuracy but only 45% recall on high-risk customers, is this acceptable? Calculate the financial impact."

---

### 🔬 Step 5: Perform Analytics (EDA)

**Deliverable**: Visual EDA Report with Risk Insights

**Recommended Analyses**:
- Claim frequency by age group and smoking status
- Geographic risk hotspots
- Correlation analysis
- Outlier & fraud pattern detection
- Class imbalance visualization

**Prompt**:
> "Create one visualization that reveals the relationship between age, smoking status, and claim frequency."

---

### 🤖 Step 6: Prediction Modeling

**Deliverable**: Model Architecture & Training Plan

**Recommended Models**:
1. Logistic Regression (Baseline + Interpretability)
2. Random Forest
3. XGBoost / LightGBM (Best performance)
4. Neural Networks (if data volume is large)

**Techniques**:
- Cross-validation
- Hyperparameter tuning
- Class imbalance handling
- Model calibration

---

### 📑 Step 7: Report Generation

**Deliverable**: Executive Risk Assessment Report

**Suggested Structure**:
- Executive Summary (150 words)
- Model Performance
- Business Impact & Financial Savings
- Fairness & Compliance Assessment
- Recommendations for Underwriting Policy
- Next Steps

---

### ⚠️ Step 8: Analyze the Risk

**Deliverable**: Model Risk Assessment Matrix

**Major Risks**:
- Data Bias
- Model Overfitting
- Fairness / Discrimination Risk
- Regulatory Non-Compliance
- Model Drift
- Reputational Risk

**Prompt**:
> "If your model systematically assigns higher risk scores to customers from a specific region, what are the legal and ethical implications?"

---

## Bonus Challenge Questions

**Technical**:
1. How to handle severe class imbalance (only 15% high-risk)?
2. How to create a composite risk score?
3. How to calibrate probability predictions?
4. How to validate across different time periods?

**Business & Ethical**:
5. How to explain individual risk scores to regulators and customers?
6. How to prevent adverse selection?

---

**Ready to Begin?**

Start with **Step 1** – Write your SMART objective and 5 Whys analysis.

Would you like me to create:
- A ready-to-use Jupyter Notebook template?
- Full preprocessing code for this insurance dataset?
- Executive report template?

Just say the word!