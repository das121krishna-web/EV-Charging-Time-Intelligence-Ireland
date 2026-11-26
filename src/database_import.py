
import os
import pandas as pd
import psycopg

CSV_FILE = "data/cleaned_availability_observations_v2.csv"


def import_data():
    df = pd.read_csv(CSV_FILE)

    print("CSV records:", len(df))

    inserted = 0

    with psycopg.connect(os.environ["SUPABASE_DB_URL"]) as conn:
        with conn.cursor() as cur:

            # Insert unique charging stations
            stations = df[["station_id", "station_name"]].drop_duplicates()

            for _, row in stations.iterrows():
                cur.execute(
                    """
                    INSERT INTO public.stations
                    (station_id, station_name)
                    VALUES (%s, %s)
                    ON CONFLICT (station_id)
                    DO UPDATE SET station_name = EXCLUDED.station_name
                    """,
                    (str(row["station_id"]), str(row["station_name"]))
                )

            # Insert availability observations
            for _, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO public.availability_observations
                    (
                        station_id, collected_at, available,
                        occupied, reserved, out_of_service,
                        unknown, total_chargers, occupancy_percentage
                    )
                    SELECT
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM public.availability_observations
                        WHERE station_id = %s
                        AND collected_at = %s
                    )
                    """,
                    (
                        str(row["station_id"]),
                        row["collected_at"],
                        int(row["available"]),
                        int(row["occupied"]),
                        int(row["reserved"]),
                        int(row["out_of_service"]),
                        int(row["unknown"]),
                        int(row["total_chargers"]),
                        float(row["occupancy_percentage"]),
                        str(row["station_id"]),
                        row["collected_at"]
                    )
                )

                inserted += cur.rowcount

    print("New observations inserted:", inserted)
    print("Data import completed!")


if __name__ == "__main__":
    import_data()
