import streamlit as st
import pandas as pd

st.title("🌆 SmartCityAI: Air Quality Dashboard")

# Load saved data
df = pd.read_csv("aqi_data.csv")

st.subheader("Latest Air Quality Reading")
st.write(df.tail(1))

st.subheader("Air Quality Over Time")
st.line_chart(df[['datetime', 'aqi']].set_index('datetime'))

st.subheader("Pollutants")
st.area_chart(df[['datetime', 'pm2_5', 'pm10', 'no2']].set_index('datetime'))
