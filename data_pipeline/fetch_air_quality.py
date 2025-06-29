# import requests
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import pandas as pd

# # Load API key
# load_dotenv()
# API_KEY = os.getenv("OPENWEATHER_API_KEY")
# LAT, LON = 22.572645, 88.363892  # Example: Kolkata


# def fetch_air_quality():
#     url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         aqi_data = data["list"][0]
#         output = {
#             "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "aqi": aqi_data["main"]["aqi"],
#             "co": aqi_data["components"]["co"],
#             "pm2_5": aqi_data["components"]["pm2_5"],
#             "pm10": aqi_data["components"]["pm10"],
#             "no2": aqi_data["components"]["no2"],
#             "latitude": LAT,
#             "longitude": LON,
#         }

#         return output
#     else:
#         print("Failed to fetch data")
#         return None


# def save_data_to_csv(data):
#     df = pd.DataFrame([data])

#     for file in ["aqi_data.csv", "aqi_log.csv"]:
#         if not os.path.exists(file):
#             df.to_csv(file, index=False)
#         else:
#             df.to_csv(file, mode="a", index=False, header=False)


# # if __name__ == "__main__":
# #     data = fetch_air_quality()
# #     if data:
# #         save_data_to_csv(data)
# #         print("Data saved:", data)

# if __name__ == "__main__":
#     print("Running script...")  # Log for Task Scheduler
#     data = fetch_air_quality()
#     if data:
#         save_data_to_csv(data)
#         print("Data saved successfully:", data)
#     else:
#         print("No data fetched.")

#-----------------------------------------------------------------------------------------------------

import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load API Key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Define multiple city zones (example)
ZONES = [
    {"zone": "North Kolkata", "lat": 22.613, "lon": 88.400},
    {"zone": "South Kolkata", "lat": 22.498, "lon": 88.319},
    {"zone": "City Center",   "lat": 22.5726, "lon": 88.3639}
]

def fetch_zone_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['list'][0]
    else:
        return None

def collect_all_zones():
    rows = []
    for zone in ZONES:
        data = fetch_zone_data(zone['lat'], zone['lon'])
        if data:
            row = {
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "aqi": data["main"]["aqi"],
                "co": data["components"]["co"],
                "pm2_5": data["components"]["pm2_5"],
                "pm10": data["components"]["pm10"],
                "no2": data["components"]["no2"],
                "latitude": zone['lat'],
                "longitude": zone['lon'],
                "zone": zone['zone'],
            }
            rows.append(row)
    return pd.DataFrame(rows)

def save_to_csv(df, file="data/aqi_data.csv"):
    if not os.path.exists(file):
        df.to_csv(file, index=False)
    else:
        df.to_csv(file, mode='a', index=False, header=False)

if __name__ == "__main__":
    df = collect_all_zones()
    if not df.empty:
        save_to_csv(df)
        print("✅ AQI data saved for all zones.")
    else:
        print("❌ Failed to fetch any zone data.")

