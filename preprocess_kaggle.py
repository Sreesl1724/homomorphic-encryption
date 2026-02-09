import csv
import json
from datetime import datetime

INPUT_FILE = "data/kaggle/diabetes.csv"
OUTPUT_FILE = "data/kaggle/processed_patients.json"

patients = []

with open(INPUT_FILE, newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for i, row in enumerate(reader):
        patient = {
            "patient_id": f"kaggle_{i:05d}",
            "age": int(row["Age"]),
            "glucose": int(row["Glucose"]),
            "blood_pressure": int(row["BloodPressure"]),
            "risk_label": "High" if int(row["Outcome"]) == 1 else "Low",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        patients.append(patient)

with open(OUTPUT_FILE, "w") as f:
    json.dump(patients, f, indent=2)

print(f"Processed {len(patients)} patients")
