# =====================================================
# NIC PESHAWAR – CLEAN ML TRAINING PIPELINE
# Graduation Probability Model
# =====================================================

import pandas as pd
import os

from utils import train_graduation_model, generate_predictions

# =====================================================
# CONFIG
# =====================================================
DATA_PATH = "../raw_data/NIC Peshawar Phase 1.xlsx"
MODEL_DIR = "models"
OUTPUT_DIR = "outputs"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# LOAD DATA (STARTUPWISE ONLY)
# =====================================================
print("📥 Loading Startupwise data...")

df_startups = pd.read_excel(
    DATA_PATH,
    sheet_name="Startupwise"
)

print(f"✅ Records loaded: {df_startups.shape[0]}")

# =====================================================
# TRAIN MODEL
# =====================================================
print("\n🤖 Training graduation probability model...")

model, accuracy, df_clean = train_graduation_model(
    df_startups,
    model_path=f"{MODEL_DIR}/graduation_model.pkl"
)

print(f"📊 Model accuracy: {accuracy:.3f}")

# =====================================================
# GENERATE PREDICTIONS
# =====================================================
print("\n📈 Generating predictions...")

df_predictions = generate_predictions(
    df_startups,
    model_path=f"{MODEL_DIR}/graduation_model.pkl"
)

# =====================================================
# SAVE OUTPUTS FOR DASHBOARD
# =====================================================
output_cols = [
    "Startup",
    "Cohort",
    "Vertical",
    "Technology",
    "Graduation",
    "Graduation_Probability",
    "Risk_Band",
    "TotalJobs",
    "Revenue",
    "Investment (In USD)"
]

df_predictions[output_cols].to_csv(
    f"{OUTPUT_DIR}/predictions.csv",
    index=False
)

print("\n🚀 SUCCESS: ML pipeline completed")
print("📁 Saved artifacts:")
print(" - models/graduation_model.pkl")
print(" - outputs/predictions.csv")
print(f"📊 Final accuracy: {accuracy:.3f}")
