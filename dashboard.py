import streamlit as st
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# ------------------------------
# 🔧 Configuration
# ------------------------------
st.set_page_config(page_title="SmartCityAI Dashboard", layout="wide")
st.title("🌆 SmartCityAI - Air Quality Dashboard")

aqi_file = "data/aqi_data.csv"
pred_file = "data/predicted_aqi.csv"
reports_file = "data/citizen_reports.csv"

load_dotenv()
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# ------------------------------
# 📤 Helper: Send Email to Admin
# ------------------------------
def send_report_email(name, email, issue_type, location, description):
    msg = EmailMessage()
    msg['Subject'] = f"🆘 New Citizen Report: {issue_type}"
    msg['From'] = EMAIL
    msg['To'] = TO_EMAIL

    body = f"""
A new citizen report has been submitted.

Name: {name}
Email: {email}
Issue Type: {issue_type}
Location: {location}
Description:
{description}

View in SmartCityAI dashboard.
"""
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Email error:", e)

# ------------------------------
# 📊 Sidebar Filters
# ------------------------------
st.sidebar.header("📊 Filters")
pollutants = ["pm2_5", "pm10", "co", "no2", "aqi"]
selected_pollutant = st.sidebar.selectbox("Select Pollutant", pollutants)
date_range = st.sidebar.date_input("Select Date Range", [])

# ------------------------------
# 📈 Real-Time AQI Visualization
# ------------------------------
col1, col2 = st.columns(2)

if os.path.exists(aqi_file):
    df = pd.read_csv(aqi_file, on_bad_lines='skip')
    if 'datetime' in df.columns and selected_pollutant in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.sort_values('datetime')

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df = df[(df['datetime'] >= start) & (df['datetime'] <= end)]

        col1.subheader(f"📈 {selected_pollutant.upper()} Over Time")
        col1.line_chart(df.set_index('datetime')[selected_pollutant])
        col1.dataframe(df.tail(10))

        # AQI Classification (fixed type error)
        def classify_aqi(aqi):
            try:
                aqi = float(aqi)
                if aqi <= 50:
                    return "🟢 Good"
                elif aqi <= 100:
                    return "🟡 Moderate"
                elif aqi <= 150:
                    return "🟠 Unhealthy (Sensitive)"
                elif aqi <= 200:
                    return "🔴 Unhealthy"
                elif aqi <= 300:
                    return "🟣 Very Unhealthy"
                else:
                    return "⚫ Hazardous"
            except:
                return "❓ Unknown"

        if 'aqi' in df.columns:
            latest_aqi = df['aqi'].dropna().iloc[-1]
            col1.metric("Current AQI", int(float(latest_aqi)), classify_aqi(latest_aqi))
    else:
        col1.warning(f"Missing 'datetime' or '{selected_pollutant}' in data.")
else:
    col1.error("❌ aqi_data.csv not found.")

# ------------------------------
# 🔮 AI Predictions
# ------------------------------
if os.path.exists(pred_file):
    pred_df = pd.read_csv(pred_file)
    pred_df['timestamp'] = pd.to_datetime(pred_df['timestamp'])
    pred_df = pred_df.set_index('timestamp')

    col2.subheader("🔮 Predicted Pollutants (24h)")

    # Let user pick pollutant from actual columns
    predicted_pollutants = ["aqi", "pm2_5", "pm10", "co", "no2"]
    selected_predicted = col2.selectbox("Select Predicted Pollutant", predicted_pollutants)

    if selected_predicted in pred_df.columns:
        col2.line_chart(pred_df[selected_predicted])
        col2.dataframe(pred_df[[selected_predicted]].tail(10))
    else:
        col2.warning(f"'{selected_predicted}' not found in predictions.")
else:
    col2.info("Prediction file not available.")


# ------------------------------
# 🗺️ Map Multiple Zones
# ------------------------------
if 'latitude' in df.columns and 'longitude' in df.columns and 'zone' in df.columns:
    st.subheader("📍 City Zones Air Quality Map")
    map_df = df[['latitude', 'longitude', 'zone', selected_pollutant, 'datetime']].copy()
    map_df = map_df.rename(columns={selected_pollutant: "value"})
    latest_map_df = map_df.sort_values('datetime').drop_duplicates(subset='zone', keep='last')
    st.map(latest_map_df[['latitude', 'longitude']])

    with st.expander("📌 Zone-Wise AQI"):
        st.dataframe(latest_map_df.sort_values("zone"))
else:
    st.info("No zone or geo-coordinates found in data.")

# ------------------------------
# 📝 Citizen Engagement Form
# ------------------------------
st.markdown("---")
st.header("🙋 Report an Issue (Citizen)")

with st.form("report_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    issue_type = st.selectbox("Issue Type", ["Air Pollution", "Noise", "Garbage", "Water Logging", "Traffic"])
    location = st.text_input("Location / Area")
    description = st.text_area("Describe the issue")
    submitted = st.form_submit_button("Submit Report")

    if submitted:
        report_data = {
            "datetime": pd.Timestamp.now(),
            "name": name,
            "email": email,
            "issue_type": issue_type,
            "location": location,
            "description": description
        }
        report_df = pd.DataFrame([report_data])

        if not os.path.exists(reports_file):
            report_df.to_csv(reports_file, index=False)
        else:
            report_df.to_csv(reports_file, mode='a', index=False, header=False)

        send_report_email(name, email, issue_type, location, description)
        st.success("✅ Report submitted and emailed to city admin!")

# ------------------------------
# 📋 Admin View of Reports
# ------------------------------
with st.expander("📋 Admin - Latest Citizen Reports"):
    if os.path.exists(reports_file):
        reports_df = pd.read_csv(reports_file)
        st.dataframe(reports_df.tail(10))
    else:
        st.info("No reports submitted yet.")
