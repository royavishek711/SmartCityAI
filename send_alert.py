import pandas as pd
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

# Load env variables
load_dotenv()
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# Thresholds
AQI_LIMIT = 1.5  # Moderate and above
PM25_LIMIT = 20.0  # μg/m3

def send_email_alert(subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)
        print("✅ Alert sent.")
    except Exception as e:
        print("❌ Failed to send alert:", e)

def check_air_quality_and_alert(file="data/aqi_data.csv"):
    if not os.path.exists(file):
        print("CSV file not found.")
        return

    df = pd.read_csv(file)
    latest = df.sort_values('datetime', ascending=False).iloc[0]

    aqi = latest['aqi']
    pm25 = latest['pm2_5']

    if aqi >= AQI_LIMIT or pm25 > PM25_LIMIT:
        subject = "⚠️ Air Quality Alert!"
        body = f"""Air Quality has deteriorated!

Datetime: {latest['datetime']}
AQI: {aqi}
PM2.5: {pm25} μg/m³

Please take necessary precautions.
        """
        send_email_alert(subject, body)
    else:
        print("😊 AQI within safe range.")

if __name__ == "__main__":
    check_air_quality_and_alert()
