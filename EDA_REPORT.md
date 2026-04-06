# Insurance Claims EDA Report

## Dataset Snapshot

- Source file: `Insurance claims data.csv`
- Raw shape: 58,592 rows x 41 columns
- After dropping the index-like `Unnamed: 0` column and adding engineered features: 58,592 rows x 50 columns
- Missing values: 0
- Full-row duplicates in the raw CSV: 0
- Duplicate rows after removing the index-like `Unnamed: 0` column: 1,894

## Target Distribution

- `claim_status = 0`: 54,844 records
- `claim_status = 1`: 3,748 records
- Claim rate: 6.40%
- Majority/minority ratio: 14.63:1

This dataset is meaningfully imbalanced, so plain accuracy should not be treated as the main success metric in later modeling.

## Key Findings

### 1. Subscription length is the clearest numeric risk signal

Among numeric features, `subscription_length` had the strongest linear relationship with `claim_status` with a Pearson correlation of `0.0787`.

Claim rate by subscription bucket:

- `<2y`: 3.78%
- `2-5y`: 5.15%
- `5-10y`: 7.55%
- `10y+`: 8.40%

Longer-running subscriptions are associated with materially higher claim rates.

### 2. Newer vehicles claim more often in this dataset

Claim rate by vehicle age bucket:

- `0-1y`: 6.75%
- `1-3y`: 6.35%
- `3-5y`: 4.50%
- `5y+`: 3.14% with only 223 policies

The sharp drop in the oldest bucket should be treated carefully because the sample is very small, but the overall pattern suggests claim activity is concentrated in newer vehicles.

### 3. Claim rate increases with customer age

Claim rate by customer age bucket:

- `35-40`: 5.70%
- `41-45`: 6.63%
- `46-50`: 6.62%
- `51-55`: 6.66%
- `56+`: 7.54%

Older policyholders, especially `56+`, show the highest claim frequency in this sample.

### 4. Segment and product mix matter

Claim rate by vehicle segment:

- `B2`: 6.86%
- `C2`: 6.43%
- `C1`: 6.41%
- `A`: 6.04%
- `Utility`: 6.04%
- `B1`: 5.85%

Claim rate by fuel type:

- `Petrol`: 6.64%
- `Diesel`: 6.49%
- `CNG`: 6.07%

Claim rate by steering type:

- `Electric`: 6.69%
- `Power`: 6.20%
- `Manual`: 6.04%

These differences are not huge individually, but they are directionally useful for segmentation and multivariate modeling.

### 5. Regional variation is meaningful

Top regions by claim rate, restricted to groups with at least 500 policies:

- `C14`: 7.68%
- `C4`: 7.67%
- `C19`: 7.46%
- `C3`: 7.10%
- `C2`: 7.08%
- `C8`: 6.99%

Lowest regions by claim rate, restricted to groups with at least 500 policies:

- `C10`: 4.69%
- `C15`: 4.93%
- `C9`: 4.97%
- `C7`: 5.03%
- `C1`: 5.18%

This suggests region is likely useful, but small-volume regions should be regularized or encoded carefully during modeling.

### 6. Model-level variation is also visible

Highest claim-rate models:

- `M2`: 7.41%
- `M5`: 7.26%
- `M7`: 6.84%
- `M6`: 6.82%

Lowest claim-rate models:

- `M11`: 4.13% with 363 policies
- `M3`: 5.39%
- `M8`: 5.85%

Model risk exists, but low-sample models should be interpreted cautiously.

### 7. Claimants differ slightly in profile

Average values by claim status:

- `subscription_length`: 6.03 for non-claimants vs 7.36 for claimants
- `vehicle_age`: 1.40 vs 1.27
- `customer_age`: 44.78 vs 45.41
- `region_density`: 18,909 vs 17,624
- `gross_weight`: 1,385.06 vs 1,388.44
- `ncap_rating`: 1.76 vs 1.78

Most single-feature differences are small except for subscription length, which stands out more clearly.

### 8. Outliers are limited

Using the IQR rule:

- `region_density` had 6.22% outliers
- `customer_age` had 0.48% outliers
- `vehicle_age` had 0.46% outliers
- Most engineered vehicle-spec features showed no major IQR outlier problem

The dataset is relatively clean and structured for tabular modeling, but the repeated feature profiles should be kept in mind during model validation and interpretation.

## Modeling Notes

- Do EDA on the raw data, not a balanced copy.
- Split train and test before any resampling.
- Use imbalance-aware metrics such as ROC-AUC, PR-AUC, recall for claims, and calibrated probabilities.
- Use careful encoding for `region_code`, `model`, and `engine_type` because they have meaningful cardinality.

## Recommended Next Step

Build a leakage-safe baseline model with:

- train/test split first
- class weighting or resampling only on the training set
- proper handling for high-cardinality categorical features
- evaluation centered on recall, precision, ROC-AUC, and calibration
