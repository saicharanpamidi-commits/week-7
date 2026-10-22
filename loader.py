"""
Script to load geographical data into a pandas DataFrame,
and save it as a CSV file.
"""

import time

import numpy as np
import pandas as pd
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


def get_geolocator(agent='h501-spamidi-week7'):
    """
    Initiate a Nominatim geolocator instance given an `agent`.

    Parameters
    ----------
    agent : str, optional
        Agent name for Nominatim, by default 'h501-spamidi-week7'
    """
    # a longer timeout so a slow reply from Nominatim is not an error
    return Nominatim(user_agent=agent, timeout=10)


def fetch_location_data(geolocator, loc):
    """
    Geocode one location and return its data as a dictionary.

    If the location can't be found, or the request fails, the location
    name is kept and the other values are NaN.
    """
    # this is what we return when there is no result
    empty_result = {"location": loc, "latitude": np.nan,
                    "longitude": np.nan, "type": np.nan}

    # only the API call goes inside try, so other bugs are not hidden
    try:
        location = geolocator.geocode(loc)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Request failed for {loc}: {e}")
        return empty_result

    # geocode returns None when nothing matches the search
    if location is None:
        return empty_result

    # Location has no geo_type attribute, the type is in the raw data
    return {"location": loc,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "type": location.raw.get("type", np.nan)}


def build_geo_dataframe(locations, geolocator=None):
    """Geocode a list of locations and return them as a DataFrame."""
    # geolocator was never defined inside this function before
    if geolocator is None:
        geolocator = get_geolocator()

    geo_data = []
    for loc in locations:
        geo_data.append(fetch_location_data(geolocator, loc))
        # Nominatim allows at most one request per second
        time.sleep(1)

    return pd.DataFrame(geo_data,
                        columns=["location", "latitude", "longitude", "type"])


if __name__ == "__main__":
    geo = get_geolocator()

    locations = ["Museum of Modern Art", "iuyt8765(*&)", "Alaska",
                 "Franklin's Barbecue", "Burj Khalifa"]

    df = build_geo_dataframe(locations, geo)

    df.to_csv("./geo_data.csv", index=False)
