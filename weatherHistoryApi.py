import requests # type: ignore
import datetime
import json
import argparse

API_KEY = "e5314a3a5d5249d0aff223149252412"
LAT = 48.981917 
LON = -123.545861  
LOCATION = f"{LAT},{LON}"

def fetch_history(date):
    url = "https://api.weatherapi.com/v1/history.json"
    params = {
        "key": API_KEY,
        "q": LOCATION,
        "dt": date
    }
    response = requests.get(url, params=params)
    response.raise_for_status()    
    return response.json()

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--start-date', required=True)
parser.add_argument('--end-date', required=True)
args = parser.parse_args()

start_date = datetime.date.fromisoformat(args.start_date)
end_date = datetime.date.fromisoformat(args.end_date)

date_list = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]

all_data = []

for day in date_list:
    print(f"Fetching {day}...")
    data = fetch_history(day.isoformat())
    all_data.append(data)

print("Finished fetching all days!")

total_true_precip = 0

for day_data in all_data:
    forecast_day = day_data["forecast"]["forecastday"][0]
    date = forecast_day["date"]
    total_precip = forecast_day["day"]["totalprecip_mm"]
    
    total_true_precip += total_precip
    
print("total precipitation for the period: ", total_true_precip, " mm")

# Load forecast and compare
forecasts_file = "forecasts.json"
try:
    with open(forecasts_file, "r") as f:
        forecasts = json.load(f)
except FileNotFoundError:
    forecasts = {}

key = f"{start_date.isoformat()}-{end_date.isoformat()}"
forecasted = forecasts.get(key)
if forecasted is not None:
    difference = total_true_precip - forecasted
    print(f"Actual: {total_true_precip}, Forecasted: {forecasted}, Difference: {difference}")
else:
    print(f"No forecast found for {key}")

filename = "precip.json"

with open(filename, "r") as f:
    data = json.load(f)

# Update only total_true_precip
old_value = data.get("total_true_precip", 0)
data["total_true_precip"] = old_value + total_true_precip

# Write back
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print("Updated total_true_precip:", data["total_true_precip"])
	