## fetch_data.py for downloading historical temperature data for Hoquiam and Spokane from the Open-Meteo Historical Weather API.

import requests
import pandas as pd

URL = "https://archive-api.open-meteo.com/v1/archive"
START = "2006-01-01"
END = "2025-12-31"

CITIES = {
    "Hoquiam": (46.98, -123.89),
    "Spokane": (47.6588, -117.4260),
}

# Fetch in 5-year chunks so a single request never gets too large.
CHUNKS = [("2006-01-01", "2010-12-31"),
          ("2011-01-01", "2015-12-31"),
          ("2016-01-01", "2020-12-31"),
          ("2021-01-01", "2025-12-31")]


def fetch_city(name, lat, lon):
    frames = []
    for start, end in CHUNKS:
        print(f"  {name}: {start} to {end} ...")
        r = requests.get(URL, params={
            "latitude": lat,
            "longitude": lon,
            "start_date": start,
            "end_date": end,
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "America/Los_Angeles",
        }, timeout=120)
        r.raise_for_status()
        js = r.json()
        frames.append(pd.DataFrame({
            "time": pd.to_datetime(js["hourly"]["time"]),
            "temp_f": js["hourly"]["temperature_2m"],
        }))
    print(f"  {name}: grid elevation = {js.get('elevation')} m")
    df = pd.concat(frames, ignore_index=True)
    df["city"] = name
    return df


def main():
    data = pd.concat([fetch_city(n, *c) for n, c in CITIES.items()],
                     ignore_index=True)
    data.to_csv("hoquiam_spokane_temp.csv", index=False)
    print("\nSaved hoquiam_spokane_temp.csv")
    print(data.groupby("city")["temp_f"].agg(["count", "min", "max"]))
    print("Missing values per city:")
    print(data[data["temp_f"].isna()].groupby("city").size())


if __name__ == "__main__":
    main()
