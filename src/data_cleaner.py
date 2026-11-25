
import pandas as pd

# 1. Load the new raw observations
input_file = "data/availability_observations_v2.csv"
output_file = "data/cleaned_availability_observations_v2.csv"

df = pd.read_csv(input_file)

print("Original records:", len(df))

# 2. Remove exact duplicate records
df = df.drop_duplicates()

# 3. Convert timestamps into datetime format
df["collected_at"] = pd.to_datetime(
    df["collected_at"],
    errors="coerce",
    utc=True
)

# 4. Check required columns
required_columns = [
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
]

df = df.dropna(subset=required_columns)

# 5. Convert charger counts to numeric values
count_columns = [
    "available",
    "occupied",
    "reserved",
    "out_of_service",
    "unknown",
    "total_chargers"
]

for column in count_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["occupancy_percentage"] = pd.to_numeric(
    df["occupancy_percentage"],
    errors="coerce"
)

df = df.dropna(subset=count_columns + ["occupancy_percentage"])

# 6. Remove invalid negative charger counts
df = df[(df[count_columns] >= 0).all(axis=1)]

# 7. Validate total charger counts
calculated_total = (
    df["available"]
    + df["occupied"]
    + df["reserved"]
    + df["out_of_service"]
    + df["unknown"]
)

df = df[df["total_chargers"] == calculated_total]

# 8. Recalculate occupancy percentage
df["occupancy_percentage"] = (
    df["occupied"] / df["total_chargers"] * 100
).where(df["total_chargers"] > 0, 0).round(2)

# 9. Save cleaned dataset
df.to_csv(output_file, index=False)

print("Cleaning completed successfully!")
print("Cleaned records:", len(df))
print("Removed records:", 90 - len(df))
print("Cleaned file saved:", output_file)
print("Missing values:", df.isnull().sum().sum())
