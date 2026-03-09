"""
Metal Sustainability Impact Analyzer
Train Model Script
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ─── Paths ────────────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join("dataset", "metal_dataset.csv")
MODEL_PATH   = os.path.join("model",   "metal_model.pkl")

# ─── Load Dataset ─────────────────────────────────────────────────────────────
print("=" * 55)
print("   🔩  Metal Sustainability Impact Analyzer")
print("        Model Training")
print("=" * 55)

df = pd.read_csv(DATASET_PATH)
print(f"\n✅ Dataset loaded  →  {len(df)} rows\n")
print(df.head())

# ─── Encode Categorical Columns ───────────────────────────────────────────────
le_metal   = LabelEncoder()
le_process = LabelEncoder()

df["Metal_enc"]   = le_metal.fit_transform(df["Metal"])
df["Process_enc"] = le_process.fit_transform(df["Process"])

# ─── Features & Targets ───────────────────────────────────────────────────────
FEATURES = ["Metal_enc", "Process_enc", "Quantity(kg)"]
TARGETS  = ["Energy(kwh)", "Water(liters)", "CO2(kg)", "Waste(kg)"]

X = df[FEATURES]
y = df[TARGETS]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n📊 Train samples : {len(X_train)}")
print(f"📊 Test  samples : {len(X_test)}")

print("\n⚙️  Training Random Forest model …")

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ─── Evaluate ─────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
print("\n📈 Model Evaluation on Test Set:")
print("-" * 45)
for i, col in enumerate(TARGETS):
    mae = mean_absolute_error(y_test.values[:, i], y_pred[:, i])
    r2  = r2_score(y_test.values[:, i], y_pred[:, i])
    print(f"  {col:<18}  MAE={mae:>8.2f}   R²={r2:.4f}")

# ─── Save Model ───────────────────────────────────────────────────────────────
os.makedirs("model", exist_ok=True)

payload = {
    "model":      model,
    "le_metal":   le_metal,
    "le_process": le_process,
    "features":   FEATURES,
    "targets":    TARGETS
}

with open(MODEL_PATH, "wb") as f:
    pickle.dump(payload, f)

print(f"\n✅ Model saved  →  {MODEL_PATH}")
print("\n🎉 Training complete! Run  predict_model.py  to make predictions.\n")
