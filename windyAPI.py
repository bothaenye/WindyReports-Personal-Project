import requests  # type: ignore
import json
import pandas as pd  # type: ignore
from datetime import datetime, timedelta


def build_dataset(data):
    """
    Convert Windy API response into a pandas DataFrame.
    """
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

        # Convert temperature to Celsius
        df["temp_C"] = df["temp_K"] - 273.15

        return df

    except KeyError as e:
        print(f"Missing expected data in response: {e}")
        return None


def update_cumulative_precip(df):
    """
    Update cumulative precipitation stored in precip.json.
    """
    if df is None or df.empty:
        print("No data available for precipitation update.")
        return

    forecast_total = df["precip"].sum()

    # Load existing file if it exists
    try:
        with open("precip.json", "r") as f:
            obj = json.load(f)
    except FileNotFoundError:
        obj = {}

    old_total = obj.get("total_precip", 0)

    new_total = old_total + forecast_total
    obj["total_precip"] = new_total

    with open("precip.json", "w") as f:
        json.dump(obj, f, indent=2)

    print("Previous cumulative:", old_total)
    print("New forecast precip:", forecast_total)
    print("Updated cumulative:", new_total)


def main():
    url = "https://api.windy.com/api/point-forecast/v2"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "lat": 48.981917,
        "lon": -123.545861,
        "model": "gfs",
        "parameters": ["wind", "temp", "precip", "lclouds", "mclouds", "hclouds"],
        "levels": ["surface"],
        "key": "YOUR_API_KEY_HERE"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()

    # Save raw response (useful for debugging)
    with open("windy_response.json", "w") as f:
        json.dump(data, f, indent=2)

    # API error check
    if "message" in data and "error" in data:
        print(f"API error: {data['message']} ({data['error']})")
        return

    # Build dataset
    df = build_dataset(data)

    if df is None:
        print("Dataset creation failed.")
        return

    # Filter next 7 days
    now = datetime.utcnow()
    future_date = now + timedelta(days=7)

    df = df[(df["time"] >= now) & (df["time"] < future_date)]

    if df.empty:
        print("No forecast data in next 7 days.")
        return

    print("Dataset created:")
    print(df.head())

    # Save CSV
    date_str = future_date.strftime("%Y-%m-%dT%H-%M-%SZ")
    filename = f"windy_forecast_{date_str}.csv"

    df.to_csv(filename, index=False)
    print(f"Saved as {filename}")

    # Update cumulative precipitation
    update_cumulative_precip(df)


if __name__ == "__main__":
    main()