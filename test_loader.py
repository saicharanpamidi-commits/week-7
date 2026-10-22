import unittest

import pandas as pd

from loader import *


class TestLoader(unittest.TestCase):
    def test_valid_locations(self):
        # known values from Google Maps
        expected = [
            {"location": "Museum of Modern Art",
             "latitude": 40.7618552, "longitude": -73.9782438,
             "type": "museum"},
            {"location": "USS Alabama Battleship Memorial Park",
             "latitude": 30.684373, "longitude": -88.015316,
             "type": "park"},
        ]

        names = [row["location"] for row in expected]
        df = build_geo_dataframe(names)

        # one row for each location, in the same order
        self.assertEqual(len(df), len(expected))

        for i, row in enumerate(expected):
            result = df.iloc[i]

            self.assertEqual(result["location"], row["location"])

            # Google Maps and OpenStreetMap don't put the pin on the
            # exact same spot, so allow about 1 km of difference
            self.assertAlmostEqual(result["latitude"], row["latitude"],
                                   delta=0.01)
            self.assertAlmostEqual(result["longitude"], row["longitude"],
                                   delta=0.01)

            # Nominatim gives types in lower case ("museum", not "Museum")
            self.assertEqual(str(result["type"]).lower(), row["type"])

    def test_invalid_location(self):
        geolocator = get_geolocator()
        result = fetch_location_data(geolocator, "asdfqwer1234")

        # the location name should be kept
        self.assertEqual(result["location"], "asdfqwer1234")

        # everything else should be NaN, not None
        for key in ["latitude", "longitude", "type"]:
            self.assertTrue(pd.isna(result[key]),
                            f"{key} should be NaN for a fake location.")

        # the same row in the final DataFrame should also be NaN
        df = build_geo_dataframe(["asdfqwer1234"], geolocator)
        self.assertEqual(df.loc[0, "location"], "asdfqwer1234")
        self.assertTrue(df.loc[0, ["latitude", "longitude", "type"]]
                        .isna().all())


if __name__ == "__main__":
    unittest.main()
