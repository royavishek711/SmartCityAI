import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# File paths
DATA_FILE = "data/aqi_data.csv"
OUTPUT_FILE = "data/predicted_aqi.csv"

if not os.path.exists(DATA_FILE):
    print(f"❌ Data file not found: {DATA_FILE}")
    exit()

# Load the dataset
df = pd.read_csv(DATA_FILE)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

# Define the features and targets (must be numeric)
features = ['co', 'pm2_5', 'pm10', 'no2']
targets = ['aqi', 'pm2_5', 'pm10', 'co', 'no2']

# Remove any rows where required fields are missing or not numeric
for col in features + ['aqi']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=features + ['aqi'])

# Prepare the training data
X = df[features]

# Store predictions
predictions = {}

# Train a separate model for each target
for target in targets:
    y = pd.to_numeric(df[target], errors='coerce')
    valid_rows = y.notna()
    X_valid = X.loc[valid_rows]
    y_valid = y.loc[valid_rows]

    if len(X_valid) < 5:
        print(f"❌ Not enough data to train for {target}")
        continue

    model = LinearRegression()
    model.fit(X_valid, y_valid)

    # Predict next 24 hours using the latest known data
        
    last_known_df = X.iloc[[-1]].copy()  # ← keeps it as DataFrame with column names
    future_preds = []

    for i in range(24):
        pred = model.predict(last_known_df)[0]
        future_preds.append(pred)

    predictions[target] = future_preds

# Generate future timestamps
start_time = df['datetime'].max()
timestamps = [start_time + timedelta(hours=i + 1) for i in range(24)]

# Build final dataframe
pred_df = pd.DataFrame(predictions)
pred_df['timestamp'] = timestamps

# Save to CSV
os.makedirs("data", exist_ok=True)
pred_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Prediction saved successfully to: {OUTPUT_FILE}")

