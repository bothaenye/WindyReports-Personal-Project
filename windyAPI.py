import requests
import json
import pandas as pd
from datetime import datetime, timedelta
#ensure u r in mircrosoft interpreter 3.11.9
def build_dataset(data):
    try:
        times = [datetime.utcfromtimestamp(ts / 1000) for ts in data["ts"]]
        df = pd.DataFrame({
            "time": times,
            "wind_u": data["wind_u-surface"],
            "wind_v": data["wind_v-surface"],
            "temp_K": data["temp-surface"],
            "precip": data["past3hprecip-surface"],
            "lclouds": data["lclouds-surface"],
            "mclouds": data["mclouds-surface"],
            "hclouds": data["hclouds-surface"]
        })
        df["temp_C"] = df["temp_K"] - 273.15
        return df
    except KeyError as e:
        print(f"Missing expected data in response: {e}")
        return None

def main():
    url = "https://api.windy.com/api/point-forecast/v2"
    headers = {"Content-Type": "application/json"}
    payload = {
        "lat": 48.981917,
        "lon": -123.545861,
        "model": "gfs",
        "parameters": ["wind", "temp", "precip", "lclouds", "mclouds", "hclouds"],
        "levels": ["surface"],
        "key": "U9oNWaYnBYGgVjNSE53kA2YjRd48nNwX"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()
    

    with open("windy_response.json", "w") as f:
        json.dump(data, f, indent=2)    
        

    if "message" in data and "error" in data:
        print(f"API error: {data['message']} ({data['error']})")
        return

    # Build dataset
    df = build_dataset(data)
    if df is not None:
        future_date = datetime.utcnow() + timedelta(days=7)
        date_str = future_date.strftime("%Y-%m-%dT%H-%M-%SZ")
        now = datetime.utcnow()
        
        print("Dataset created:")
        df = df[(df["time"] >= now) & (df["time"] < future_date)]
        print(df.head())
    
        df.to_csv(f"windy_forecast_{date_str}.csv", index=False)
        print("Saved as windy_forecast.csv")
        print(df["precip"])

    with open("precip.json", "r") as l:
            obj = json.load(l)
            old_total = obj.get("total_precip", 0) 
            
	
    try:
       with open("precip.json", "r") as l:
           obj = json.load(l)
           old_total = obj.get("total_precip", 0)
           total_precip = sum(df["precip"])
           obj["total_precip"] = old_total + total_precip
           with open("precip.json", "w") as k:
                json.dump(obj, k, indent=2)

    except FileNotFoundError:
        obj = {}



if __name__ == "__main__":
    main()
