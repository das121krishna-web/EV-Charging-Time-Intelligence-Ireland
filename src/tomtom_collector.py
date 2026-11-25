
import os
import csv
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from datetime import datetime, timezone


class ApiResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.text = body.decode("utf-8", errors="replace")

    def json(self):
        return json.loads(self.text)


def get(url, params, timeout):
    request_url = f"{url}?{urlencode(params)}"
    try:
        with urlopen(request_url, timeout=timeout) as response:
            return ApiResponse(response.status, response.read())
    except HTTPError as error:
        return ApiResponse(error.code, error.read())

# 1. Retrieve API key securely
tomtom_api_key = os.getenv("TOMTOM_API_KEY")

if not tomtom_api_key:
    raise ValueError("TomTom API key is missing!")

# 2. Prepare TomTom Search API
url = "https://api.tomtom.com/search/2/search/electric%20vehicle%20station.json"

params = {
    "countrySet": "IE",
    "lat": 53.3498,
    "lon": -6.2603,
    "limit": 100,
    "key": tomtom_api_key
}

# 3. Send API request
response = get(url, params=params, timeout=30)

print("Status code:", response.status_code)

# 4. Process API response
if response.status_code == 200:

    data = response.json()
    results = data.get("results", [])

    print("Number of stations retrieved:", len(results))

    # 5. Count availability references
    availability_count = 0

    for item in results:
        data_sources = item.get("dataSources") or {}
        availability = data_sources.get("chargingAvailability") or {}

        if availability.get("id"):
            availability_count += 1

    print("Stations with availability references:", availability_count)

    # 6. Prepare CSV file
    os.makedirs("data", exist_ok=True)
    csv_file = "data/availability_observations_v2.csv"

    file_exists = os.path.isfile(csv_file)

    # 7. Process all stations
    successful_stations = 0
    failed_stations = 0

    for item in results:

        data_sources = item.get("dataSources") or {}
        availability = data_sources.get("chargingAvailability") or {}
        availability_id = availability.get("id")

        # Skip stations without availability references
        if not availability_id:
            continue

        station_name = item.get("poi", {}).get("name")
        station_id = item.get("id")

        print("\nProcessing station:", station_name)

        # 8. Request live charging availability
        availability_url = (
            "https://api.tomtom.com/search/2/chargingAvailability.json"
        )

        availability_params = {
            "key": tomtom_api_key,
            "chargingAvailability": availability_id
        }

        try:
            availability_response = get(
                availability_url,
                params=availability_params,
                timeout=30
            )

            if availability_response.status_code != 200:
                failed_stations += 1
                print("API error:", availability_response.status_code)
                continue

            availability_data = availability_response.json()

            collected_at = datetime.now(timezone.utc).isoformat()

            # 9. Extract charger counts
            total_available = 0
            total_occupied = 0
            total_reserved = 0
            total_out_of_service = 0
            total_unknown = 0

            for connector in availability_data.get("connectors", []):

                current = (
                    connector.get("availability", {}).get("current", {})
                )

                total_available += current.get("available", 0)
                total_occupied += current.get("occupied", 0)
                total_reserved += current.get("reserved", 0)
                total_out_of_service += current.get("outOfService", 0)
                total_unknown += current.get("unknown", 0)

            total_chargers = (
                total_available
                + total_occupied
                + total_reserved
                + total_out_of_service
                + total_unknown
            )

            occupancy = (
                total_occupied / total_chargers * 100
                if total_chargers > 0 else 0
            )

            # 10. Save observation to CSV
            with open(
                csv_file,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow([
                        "station_name",
                        "station_id",
                        "collected_at",
                        "available",
                        "occupied",
                        "reserved",
                        "out_of_service",
                        "unknown",
                        "total_chargers",
                        "occupancy_percentage"
                    ])


                    file_exists = True

                writer.writerow([
                    station_name,
                    station_id,
                    collected_at,
                    total_available,
                    total_occupied,
                    total_reserved,
                    total_out_of_service,
                    total_unknown,
                    total_chargers,
                    round(occupancy, 2)
                ])
                    

            successful_stations += 1

            print("Observation saved successfully!")
            print("Available:", total_available)
            print("Occupied:", total_occupied)
            print("Total chargers:", total_chargers)
            print("Occupancy:", round(occupancy, 2), "%")

        except (URLError, TimeoutError) as error:
            failed_stations += 1
            print("Request failed:", error)
            continue

    # 11. Collection summary
    print("\n========== COLLECTION SUMMARY ==========")
    print("Stations retrieved:", len(results))
    print("Availability references:", availability_count)
    print("Successful collections:", successful_stations)
    print("Failed collections:", failed_stations)

else:
    print("Search API error:", response.status_code, response.text)