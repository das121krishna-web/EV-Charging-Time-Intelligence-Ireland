
import os
import csv
import requests
from pathlib import Path
ocm_api_key = os.getenv("OCM_API_KEY")

if not ocm_api_key:
    raise ValueError("Open Charge Map API key is missing!")
url = "https://api.openchargemap.io/v3/poi/"

params = {
    "output": "json",
    "countrycode": "IE",
    "maxresults": 100,
    "opendata": "true",
    "key": ocm_api_key
}

headers = {
    "User-Agent": "EVChargingIrelandAcademicProject/1.0"
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)
print("Status code:", response.status_code)

response.raise_for_status()

data = response.json()

if not isinstance(data, list):
    raise ValueError("Unexpected API response format.")

print("Stations retrieved:", len(data))
project_folder = Path(__file__).resolve().parents[1]
data_folder = project_folder / "data"

data_folder.mkdir(parents=True, exist_ok=True)

csv_file = data_folder / "station_information.csv"
station_rows = []

for station in data:

    address_info = station.get("AddressInfo") or {}
    connections = station.get("Connections") or []
    connector_types = []
    power_values = []
    total_connector_quantity = 0
    operational_connector_quantity = 0

    for connection in connections:

        connector = connection.get("ConnectionType") or {}
        status = connection.get("StatusType") or {}

        connector_name = connector.get("Title")

        if connector_name:
            connector_types.append(connector_name)
        power = connection.get("PowerKW")
        if power is not None:
            power_values.append(str(power))
        quantity = connection.get("Quantity") or 0
        total_connector_quantity += quantity
        if status.get("IsOperational") is True:
            operational_connector_quantity += quantity
    row = {
        "station_id": station.get("ID"),
        "station_name": address_info.get("Title"),
        "address": address_info.get("AddressLine1"),
        "town": address_info.get("Town"),
        "postcode": address_info.get("Postcode"),
        "latitude": address_info.get("Latitude"),
        "longitude": address_info.get("Longitude"),
        "number_of_points": station.get("NumberOfPoints"),
        "connector_types": "; ".join(sorted(set(connector_types))),
        "power_kw_values": "; ".join(sorted(set(power_values))),
        "total_connector_quantity": total_connector_quantity,
        "operational_connector_quantity": operational_connector_quantity,
        "date_last_confirmed": station.get("DateLastConfirmed"),
        "date_last_status_update": station.get("DateLastStatusUpdate"),
        "data_quality_level": station.get("DataQualityLevel")
    }
    station_rows.append(row)
fieldnames = [
    "station_id",
    "station_name",
    "address",
    "town",
    "postcode",
    "latitude",
    "longitude",
    "number_of_points",
    "connector_types",
    "power_kw_values",
    "total_connector_quantity",
    "operational_connector_quantity",
    "date_last_confirmed",
    "date_last_status_update",
    "data_quality_level"
]
with open(csv_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(station_rows)

print("CSV file created successfully!")
print("File location:", csv_file)
print("Rows saved:", len(station_rows))
