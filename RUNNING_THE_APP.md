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
