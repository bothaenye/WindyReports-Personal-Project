import requests # type: ignore
import datetime
import json

API_KEY = "e5314a3a5d5249d0aff223149252412"
LAT = 43.6532 
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

# Get last 7 days
today = datetime.date.today()
last_week_dates = [(today - datetime.timedelta(days=i)).isoformat()
                    for i in range(1, 8)]

all_data = []

for day in last_week_dates:
    print(f"Fetching {day}...")
    data = fetch_history(day)
    all_data.append(data)

print("Finished fetching all 7 days!")

total_true_precip = 0

for day_data in all_data:
    forecast_day = day_data["forecast"]["forecastday"][0]
    date = forecast_day["date"]
    total_precip = forecast_day["day"]["totalprecip_mm"]
    
    total_true_precip += total_precip
    
print("total precipitation for the week: ", total_true_precip, " mm")

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
	