# RiskGuard Dashboard: Local Setup Guide

Welcome to the **RiskGuard Insurance Underwriting Intelligence** repository! If you have just cloned this project, follow the steps below to properly set up both the backend API and the frontend user interface.

## Prerequisites
Before you start, make sure you have the following installed on your machine:
* [Python 3.8+](https://www.python.org/downloads/)
* [Node.js and npm](https://nodejs.org/) (Version 16+ is recommended)

---

## Step 1: Clone the Repository
If you haven't already, clone the repository to your local machine and navigate into the folder:
```bash
git clone <your-repository-url>
cd insurance-claim-
```

---

## Step 2: Start the Backend (FastAPI)
The backend is built with Python and utilizes a Random Forest model with SHAP explanations.

1. **Install Dependencies**:
   Open a terminal in the main repository folder and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   Once installed, start the FastAPI server using `uvicorn` (on Windows, you may need to use `py` instead of `python`):
   ```bash
   python -m uvicorn dashboard:app --host 0.0.0.0 --port 8000
   ```
   *Note: On your first startup, the application dynamically trains the machine learning model on the provided CSV data. Please wait ~30-60 seconds until the terminal prints `Startup complete. API ready.`*

---

## Step 3: Start the Frontend (React UI)
The frontend relies on React to visually render the underwriting dashboards and graphs.

1. **Navigate to the UI Folder**:
   Open a **second**, new terminal window and change the directory to the frontend folder:
   ```bash
   cd riskguard-ui
   ```

2. **Install Node Packages**:
   Install all the frontend dependencies required by React:
   ```bash
   npm install
   ```

3. **Run the React App**:
   Start the development server:
   ```bash
   npm start
   ```

---

## Step 4: Open the Dashboard
Running `npm start` should automatically launch a new tab in your default web browser.

If it does not open automatically, simply go to [http://localhost:3000](http://localhost:3000) in your web browser. 

The dashboard is now fully functional! You can browse individual applications, test out the What-If simulations, and check the executive fairness audit reports.


# Insurance Claim Prediction - Dataset Metadata

## Dataset Overview
- **Problem**: Binary Classification (Predict whether a vehicle insurance claim will be made or not)
- **Target Variable**: `claim_status` (0 = No Claim, 1 = Claim)
- **Total Columns**: 44
- **Rows (Sample)**: 6 (shown in the provided data)

## Metadata Table

| Column Name                          | Data Type | Category              | Description                                                                 | Possible Values / Notes                          | Importance |
|--------------------------------------|-----------|-----------------------|-----------------------------------------------------------------------------|--------------------------------------------------|----------|
| `subscription_length`                | float     | Numerical            | Duration of the insurance policy (in years)                                 | 0.1 to 10+ years                                 | High     |
| `vehicle_age`                        | float     | Numerical            | Age of the vehicle in years                                                 | 0.1 to 20+ years                                 | High     |
| `customer_age`                       | int       | Numerical            | Age of the policyholder                                                     | 18 to 80+                                        | Medium   |
| `region_code`                        | object    | Categorical          | Geographic region code of the customer                                      | e.g., C88794C2, C227003C1                        | Medium   |
| `region_density`                     | int       | Numerical            | Population density of the region                                            | Higher = more urban                              | Medium   |
| `segment`                            | object    | Categorical          | Vehicle segment (e.g., B2, C1, M4)                                          | A, B, C, M segments                              | High     |
| `model`                              | object    | Categorical          | Specific car model code                                                     | Many unique values                               | Medium   |
| `fuel_type`                          | object    | Categorical          | Type of fuel used by the vehicle                                            | Diesel, Petrol, CNG                              | High     |
| `max_torque`                         | object    | Categorical/Text     | Maximum torque with RPM (e.g., 250Nm@2750rpm)                               | Needs parsing                                    | Medium   |
| `max_power`                          | object    | Categorical/Text     | Maximum power with RPM (e.g., 113.45bhp@4000rpm)                            | Needs parsing                                    | Medium   |
| `engine_type`                        | object    | Categorical          | Engine model/type                                                           | 1.5 L U2 CRDi, i-DTEC, etc.                      | High     |
| `airbags`                            | int       | Numerical            | Number of airbags in the vehicle                                            | 2, 6, etc.                                       | High     |
| `is_esc`                             | object    | Binary               | Whether Electronic Stability Control is present                             | Yes / No                                         | High     |
| `is_adjustable_steering`             | object    | Binary               | Adjustable steering wheel                                                   | Yes / No                                         | Medium   |
| `is_tpms`                            | object    | Binary               | Tyre Pressure Monitoring System                                             | Yes / No                                         | Medium   |
| `is_parking_sensors`                 | object    | Binary               | Parking sensors                                                             | Yes / No                                         | Medium   |
| `is_parking_camera`                  | object    | Binary               | Rear parking camera                                                         | Yes / No                                         | Medium   |
| `rear_brakes_type`                   | object    | Categorical          | Type of rear brakes                                                         | Disc / Drum                                      | Medium   |
| `displacement`                       | int       | Numerical            | Engine displacement in cc                                                   | 796, 1493, 1497, etc.                            | High     |
| `cylinder`                           | int       | Numerical            | Number of cylinders in engine                                               | 3 or 4                                           | High     |
| `transmission_type`                  | object    | Categorical          | Transmission type                                                           | Manual / Automatic                               | High     |
| `steering_type`                      | object    | Categorical          | Steering mechanism                                                          | Power / Electric / Manual                        | Medium   |
| `turning_radius`                     | float     | Numerical            | Turning radius of the vehicle (in meters)                                   | 4.5 - 5.5                                        | Medium   |
| `length`                             | int       | Numerical            | Length of the vehicle (mm)                                                  | Vehicle dimension                                | Medium   |
| `width`                              | int       | Numerical            | Width of the vehicle (mm)                                                   | Vehicle dimension                                | Medium   |
| `gross_weight`                       | int       | Numerical            | Gross vehicle weight (kg)                                                   | Vehicle weight                                   | Medium   |
| `is_front_fog_lights`                | object    | Binary               | Front fog lights present                                                    | Yes / No                                         | Low      |
| `is_rear_window_wiper`               | object    | Binary               | Rear window wiper                                                           | Yes / No                                         | Low      |
| `is_rear_window_washer`              | object    | Binary               | Rear window washer                                                          | Yes / No                                         | Low      |
| `is_rear_window_defogger`            | object    | Binary               | Rear window defogger                                                        | Yes / No                                         | Low      |
| `is_brake_assist`                    | object    | Binary               | Brake assist system                                                         | Yes / No                                         | High     |
| `is_power_door_locks`                | object    | Binary               | Power door locks                                                            | Yes / No                                         | Medium   |
| `is_central_locking`                 | object    | Binary               | Central locking system                                                      | Yes / No                                         | Medium   |
| `is_power_steering`                  | object    | Binary               | Power steering                                                              | Yes / No                                         | Medium   |
| `is_driver_seat_height_adjustable`   | object    | Binary               | Driver seat height adjustment                                               | Yes / No                                         | Medium   |
| `is_day_night_rear_view_mirror`      | object    | Binary               | Day/Night rear view mirror                                                  | Yes / No                                         | Low      |
| `is_ecw`                             | object    | Binary               | Electronic Crash Warning? (or similar safety feature)                       | Yes / No                                         | Medium   |
| `is_speed_alert`                     | object    | Binary               | Speed alert system                                                          | Yes / No                                         | Medium   |
| `ncap_rating`                        | int       | Numerical            | Global NCAP safety rating (out of 5)                                        | 0 to 5                                           | High     |
| `claim_status`                       | int       | **Target**           | **Whether a claim was filed (1 = Claim, 0 = No Claim)**                     | **0 or 1**                                       | **Target** |

## Complications & Challenges in this Dataset

### 1. **Mixed Data Types**
- Many **binary** features stored as `object` ("Yes"/"No") → Need to convert to 0/1.
- Several **text features** like `max_torque`, `max_power`, `engine_type` need **feature engineering** (extract numeric values and RPM).

### 2. **High Cardinality Categorical Features**
- `region_code`, `model`, `segment` have many unique values → Risk of overfitting if not handled properly.

### 3. **Class Imbalance (Very Likely)**
- Insurance claim datasets are usually highly imbalanced (`claim_status = 1` is rare). Need to check distribution.

### 4. **Feature Engineering Required**
- `max_torque` → Extract Nm value and RPM separately.
- `max_power` → Extract bhp value and RPM separately.
- `engine_type` → Can be grouped or one-hot encoded carefully.

### 5. **Redundant / Highly Correlated Features**
- Many safety features (`is_esc`, `is_brake_assist`, `ncap_rating`, `airbags`) are likely correlated.

### 6. **Domain-Specific Challenges**
- Vehicle age and subscription length have strong business logic (older vehicles + short subscription = higher risk).
- Regional features (`region_code`, `region_density`) may capture fraud patterns or claim culture.

### 7. **Data Quality Issues**
- Some columns like `Unnamed: 0` (index column) should be dropped.
- Need to handle potential missing values (not visible in sample but common in real data).

## Recommended Preprocessing Steps

1. Drop `Unnamed: 0`
2. Convert all "Yes"/"No" columns to 1/0
3. Parse `max_torque` and `max_power`
4. Handle high cardinality columns (`region_code`, `model`)
5. Check class distribution of `claim_status`
6. Create new features (e.g., `power_to_weight_ratio`, `age_bucket`, `safety_score`)

Would you like me to also provide the **full preprocessing code** for this dataset?

Just say **"Give me preprocessing code"**.