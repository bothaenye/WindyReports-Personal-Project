import requests # type: ignore
import json
import argparse
from datetime import datetime, timezone

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    args = parser.parse_args()
    
    start_date = datetime.fromisoformat(args.start_date).date()
    end_date = datetime.fromisoformat(args.end_date).date()
    days = (end_date - start_date).days + 1
    
    if days != 7:
        print("Only 7 days supported")
        return
    
    today = datetime.now(timezone.utc).date()
    if start_date != today:
        print("Forecast only for today")
        return
    
    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": "e5314a3a5d5249d0aff223149252412",
        "q": "48.981917,-123.545861",
        "days": days
    }

    response = requests.get(url, params=params)
    data = response.json()
    

    with open("windy_response.json", "w") as f:
        json.dump(data, f, indent=2)
    

    with open("windy_response.json", "w") as f:
        json.dump(data, f, indent=2)    
        

    if "message" in data and "error" in data:
        print(f"API error: {data['message']} ({data['error']})")
        return

    total_precip = 0
    for day_data in data["forecast"]["forecastday"]:
        total_precip += day_data["day"]["totalprecip_mm"]

    print(f"Total forecast precipitation for next 7 days: {total_precip} mm")

    forecasts_file = "forecasts.json"
    try:
        with open(forecasts_file, "r") as f:
            forecasts = json.load(f)
    except FileNotFoundError:
        forecasts = {}
    
    key = f"{start_date.isoformat()}-{end_date.isoformat()}"
    forecasts[key] = total_precip
    with open(forecasts_file, "w") as f:
        json.dump(forecasts, f, indent=2)
    
    print(f"Saved forecast for {key}: {total_precip}")

    try:
        with open("precip.json", "r") as f:
            obj = json.load(f)
    except FileNotFoundError:
        obj = {}

    obj["forecast_range"] = key
    obj["total_precip_future"] = total_precip

    with open("precip.json", "w") as f:
        json.dump(obj, f, indent=2)

    print("Updated forecast_range:", obj["forecast_range"])
    print("Updated total_precip_future:", total_precip)


if __name__ == "__main__":
    main()