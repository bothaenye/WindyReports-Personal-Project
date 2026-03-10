import requests # type: ignore
import json

def main():
    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": "e5314a3a5d5249d0aff223149252412",
        "q": "48.981917,-123.545861",
        "days": 7
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

    try:
        with open("precip.json", "r") as f:
            obj = json.load(f)
    except FileNotFoundError:
        obj = {}

    obj["total_precip_future"] = total_precip

    with open("precip.json", "w") as f:
        json.dump(obj, f, indent=2)

    print("Updated total_precip_future:", total_precip)



if __name__ == "__main__":
    main()