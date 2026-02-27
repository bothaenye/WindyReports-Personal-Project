import requests
import datetime
import json

API_KEY = "YOUR_API_KEY"
LAT = 48.981917
LON = -123.545861
LOCATION = f"{LAT},{LON}"

FILENAME = "precip.json"


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


today = datetime.date.today()

total_true_precip = 0

for i in range(1, 8):
    date = (today - datetime.timedelta(days=i)).isoformat()
    print(f"Fetching {date}...")

    data = fetch_history(date)
    forecast_day = data["forecast"]["forecastday"][0]

    total_true_precip += forecast_day["day"]["totalprecip_mm"]

print("Total precipitation for the week:", total_true_precip, "mm")

# Load existing cumulative value
try:
    with open(FILENAME, "r") as f:
        obj = json.load(f)
except FileNotFoundError:
    obj = {}

old_value = obj.get("total_true_precip", 0)
obj["total_true_precip"] = old_value + total_true_precip

with open(FILENAME, "w") as f:
    json.dump(obj, f, indent=2)

print("Updated cumulative precipitation:", obj["total_true_precip"])