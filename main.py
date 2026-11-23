
print("EV Charging Time Intelligence System")
print("Project: Ireland")
print("Development environment: GitHub Codespaces")
print("Python is working successfully!")
#station_information variables
station_name = "Dublin Central"
station_id = 205
charging_power = 22.5
available_chargers = 5
occupied_chargers = 3

# Display station information

print("\n--- EV Station Information ---")

print("Station Name:", station_name)
print("Station ID:", station_id)
print("Charging Power:", charging_power, "kW")
print("Available Chargers:", available_chargers)
print("Occupied Chargers:", occupied_chargers)

# Calculation for total chargers

total_chargers = available_chargers + occupied_chargers

# Calculation for occupancy percentage

occupancy = (occupied_chargers / total_chargers) * 100
print("Total Chargers:", total_chargers)
print("Occupancy:", occupancy,)

