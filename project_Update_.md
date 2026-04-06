### RiskGuard Insurance – ML Underwriting Decision System

**Technical Documentation & Future Roadmap** **Version:** 1.0 | **Date:** April 2026

#### 1\. Project Overview

We have successfully built an end-to-end **insurance claims risk prediction system** that translates raw vehicle + customer application data into **business-ready risk scores** with clear underwriter actions.

The system follows your original flowchart:

*   Application → Feature Engineering → Model Inference → Risk Band → Decision (STP / Junior UW / Senior UW / Escalation)

#### 2\. What Has Been Implemented

**Core ML Pipeline**

*   Probabilistic class balancing (Gaussian + sampling) to handle severe imbalance
*   Robust preprocessing + domain-specific feature engineering (power\_to\_weight, torque\_per\_liter, rpm\_diff)
*   Smart encoding strategy using ColumnTransformer:
    *   Binary flags → direct mapping (Yes=1, No=0)
    *   Low-cardinality nominal → OneHotEncoder
    *   Medium/High-cardinality → OrdinalEncoder
    *   Numerical features → StandardScaler
*   Full Pipeline with RandomForestClassifier (class\_weight='balanced')
*   Strong performance: High AUC-ROC and balanced precision/recall on both classes

**Business Integration Layer (Weeks 3-4)**

*   get\_risk\_band\_and\_action() – Maps probability (0–1) into your exact 4 risk bands with SLA, automation level, and escalation path
*   log\_underwriter\_decision() – Override tracking & feedback loop for continuous model improvement
*   generate\_underwriter\_decision\_payload() – Structured JSON output ready for Underwriting Dashboard (React/Streamlit)


**Monitoring Foundation**

*   Basic structure for ModelMonitor class (drift detection via PSI, performance decay tracking)

#### 3\. Current Capabilities

*   End-to-end training and inference pipeline (dummy + real data compatible)
*   Risk score → Business decision translation (0.00–0.15 → STP, 0.70–1.00 → High Risk)
*   Human-in-the-loop override logging with alert on high override rate (>15%)
*   Real SHAP-based explainability for underwriter trust and regulatory compliance
*   Feature importance + confusion matrix visualization
*   Clean, production-friendly code structure using scikit-learn Pipelines

#### 4\. What We Can Do Next (Recommended Roadmap)

**Phase 3: Production Deployment (Weeks 5-6)**

**Immediate Next Steps (High Priority)**

1.  **Visual SHAP Plots**
    *   Add SHAP waterfall / force plots for the Underwriting Dashboard (visual gauge + reasons)
2.  **What-If Simulator**
    *   Allow underwriters to change one or two inputs and see instant score impact
3.  **Streamlit Underwriting Dashboard Prototype**
    *   Risk gauge (0-1000), color bands, top reasons, action buttons, comment box

**Monitoring & Governance (Very Important)** 4. **Full ModelMonitor Class**

*   PSI / CSI drift detection on critical features
*   Performance decay alerts (AUC, loss ratio)
*   Daily automated report generation

5.  **Feedback Loop Enhancement**
    *   Match overrides with actual claim outcomes after 6–12 months
    *   Monthly retraining trigger based on override rate + drift

**Production Architecture** 6. **Model Serving Layer**

*   Wrap the pipeline in FastAPI + Docker
*   Integrate MLflow for model registry and versioning
*   Separate Explainability Service (SHAP)

7.  **Real-time Feature Store** (Feast or Tecton)
8.  **Full 3-Lines of Defense Governance**
    *   1st Line: Risk Analytics (monitoring)
    *   2nd Line: Model Risk Management (validation + fairness)
    *   3rd Line: Internal Audit

**Advanced Enhancements (Future)**

*   Threshold optimization per risk band (business cost matrix)
*   Fairness monitoring (demographic parity, equalized odds)
*   "Shadow Mode" → Pilot deployment logic (as per your 4-week pilot plan)
*   Loss ratio tracking by risk band