"""
Metal Sustainability Impact Analyzer
Predict / Interactive Script
"""

import pickle
import os
import sys
import numpy as np

# ─── Path ─────────────────────────────────────────
MODEL_PATH = os.path.join("model", "metal_model.pkl")

# ─── Load Model ────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("❌ Model not found! Please run  train_model.py  first.")
    sys.exit(1)

with open(MODEL_PATH, "rb") as f:
    payload = pickle.load(f)

model      = payload["model"]
le_metal   = payload["le_metal"]
le_process = payload["le_process"]
TARGETS    = payload["targets"]

VALID_METALS    = list(le_metal.classes_)
VALID_PROCESSES = list(le_process.classes_)

# ─── Helper: sustainability rating ────────────────────────────────────────────
def rate_impact(co2: float) -> str:
    if co2 < 300:
        return "🟢 LOW  impact"
    elif co2 < 1000:
        return "🟡 MEDIUM impact"
    else:
        return "🔴 HIGH impact"

# ─── Banner ───────────────────────────────────────────────────────────────────
def banner():
    print("=" * 55)
    print("   ♻️   Metal Sustainability Impact Analyzer")
    print("=" * 55)

# ─── Main Loop ────────────────────────────────────────────────────────────────
def main():
    banner()
    print(f"\nSupported Metals   : {', '.join(VALID_METALS)}")
    print(f"Supported Processes: {', '.join(VALID_PROCESSES)}\n")

    while True:
        # ── Input: Metal ──────────────────────────────────────────────────────
        metal = input("Enter Metal (or 'quit' to exit): ").strip().title()
        if metal.lower() in ("quit", "exit", "q"):
            print("\n👋 Goodbye!\n")
            break
        if metal not in VALID_METALS:
            print(f"  ⚠️  '{metal}' not recognised. Choose from: {', '.join(VALID_METALS)}\n")
            continue

        # ── Input: Quantity ───────────────────────────────────────────────────
        try:
            quantity = float(input("Enter Quantity (kg): ").strip())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            print("  ⚠️  Please enter a valid positive number for quantity.\n")
            continue

        # ── Input: Process ────────────────────────────────────────────────────
        process = input("Enter Process (Recycling / Mining): ").strip().title()
        if process not in VALID_PROCESSES:
            print(f"  ⚠️  '{process}' not recognised. Choose from: {', '.join(VALID_PROCESSES)}\n")
            continue

        # ── Encode & Predict ──────────────────────────────────────────────────
        metal_enc   = le_metal.transform([metal])[0]
        process_enc = le_process.transform([process])[0]

        X_input = np.array([[metal_enc, process_enc, quantity]])
        prediction = model.predict(X_input)[0]

        energy, water, co2, waste = prediction

        # ── Display Results ───────────────────────────────────────────────────
        print("\n" + "─" * 55)
        print(f"  📋  Sustainability Impact Report")
        print("─" * 55)
        print(f"  Metal        : {metal}")
        print(f"  Process      : {process}")
        print(f"  Quantity     : {quantity:.1f} kg")
        print("─" * 55)
        print(f"  ⚡ Energy Usage  : {energy:>10.2f}  kWh")
        print(f"  💧 Water Usage   : {water:>10.2f}  liters")
        print(f"  🏭 CO₂ Emissions : {co2:>10.2f}  kg")
        print(f"  🗑️  Waste Generated: {waste:>10.2f}  kg")
        print("─" * 55)
        print(f"  🌍 Sustainability : {rate_impact(co2)}")
        print("─" * 55)

        # ── Tip ───────────────────────────────────────────────────────────────
        if process == "Mining":
            print("  💡 Tip: Switching to Recycling can reduce CO₂ by up to 95%!")
        else:
            print("  ✅ Great choice! Recycling significantly reduces environmental impact.")

        print()

if __name__ == "__main__":
    main()
