import duckdb
import os
import logging
import time

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)
logger = logging.getLogger(__name__)

months = [f"{i:02d}" for i in range(1, 13)]
years = range(2015, 2025)

def load_parquet_files():

    con = None

    try:
            # Connect to local DuckDB instance
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # Drop existing tables if they exist
            con.execute(f""" DROP TABLE IF EXISTS trip_data; """)
            logger.info("Dropped existing trip_data table if it existed")

            first = True
            
            # Loop through each year and month to load in data
            for year in years:
                for month in months:
                    # Basic url pattern
                    yellow_url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month}.parquet"
                    green_url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month}.parquet"
                    # Make sure the query only selects the needed columns and adds a vehicle type column
                    query = f"""
                        -- Select columns from yellow data
                        SELECT tpep_pickup_datetime AS pickup_datetime, tpep_dropoff_datetime AS dropoff_datetime,
                               passenger_count, trip_distance, 'yellow_taxi' AS vehicle_type
                        FROM read_parquet('{yellow_url}')
                        UNION ALL
                        -- Select columns from green data
                        SELECT lpep_pickup_datetime AS pickup_datetime, lpep_dropoff_datetime AS dropoff_datetime,
                               passenger_count, trip_distance, 'green_taxi' AS vehicle_type
                        FROM read_parquet('{green_url}');
                    """
                    logger.info(f"Processing data for {year}-{month}")

                    # If first iteration, create table, else insert data
                    if first:
                        con.execute(f""" CREATE TABLE trip_data AS {query} """)
                        first = False
                    else:
                        con.execute(f""" INSERT INTO trip_data {query} """)

                    logger.info(f"Loaded data for {year}-{month}")
                    print(f"Processed and loaded data for {year}-{month}")
                    time.sleep(60)

            logger.info("All years and months loaded into trip_data table")
            print("All years and months loaded into trip_data table")

            # Load vehicle emissions csv into table
            csv_path = "./data/vehicle_emissions.csv"

            con.execute(f"""
                -- Add vehicle emissions as a table
                DROP TABLE IF EXISTS vehicle_emissions;
                CREATE TABLE vehicle_emissions AS SELECT * FROM read_csv_auto('{csv_path}');
            """)
            logger.info("Added vehicle emissions table")
            print("Added vehicle emissions table")

            # BASIC DATA SUMMARIZATION
            print("BASIC DATA SUMMARIZATION")
            logger.info("BASIC DATA SUMMARIZATION")
            tables = ['trip_data', 'vehicle_emissions']
            # Display the row and column counts for each table
            for table in tables:
                row_count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                logger.info(f"Rows in {table}: {row_count}")
                print(f"Rows in {table}: {row_count}")

                col_count = con.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_name = '{table}';").fetchone()[0]
                logger.info(f"Columns in {table}: {col_count}")
                print(f"Columns in {table}: {col_count}")

            # Show that vehicle emissions csv is loaded: print the column names
            cols = con.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'vehicle_emissions'
                """).fetchall()
            print("Columns in vehicle_emissions:", [c[0] for c in cols])
            logger.info(f"Columns in vehicle_emissions: {[c[0] for c in cols]}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    load_parquet_files()

