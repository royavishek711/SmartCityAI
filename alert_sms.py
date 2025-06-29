import os
import pandas as pd
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_FROM = os.getenv("TWILIO_FROM")
TWILIO_TO = os.getenv("TWILIO_TO")

AQI_FILE = "data/aqi_data.csv"
THRESHOLD_PM25 = 100  # Set your alert level

def send_sms_alert(value):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    message = client.messages.create(
        body=f"⚠️ ALERT: PM2.5 level is {value} — Unhealthy air quality! Take precautions.",
        from_=TWILIO_FROM,
        to=TWILIO_TO
    )
    print("✅ SMS sent:", message.sid)

def check_air_quality_and_alert():
    if not os.path.exists(AQI_FILE):
        print("❌ aqi_data.csv not found.")
        return

    df = pd.read_csv(AQI_FILE)
    if 'pm2_5' not in df.columns:
        print("❌ pm2_5 column not in data.")
        return

    latest_value = df['pm2_5'].dropna().iloc[-1]
    print(f"📊 Latest PM2.5: {latest_value}")

    if latest_value > THRESHOLD_PM25:
        send_sms_alert(latest_value)
    else:
        print("✅ PM2.5 is within safe limits.")

if __name__ == "__main__":
    check_air_quality_and_alert()
