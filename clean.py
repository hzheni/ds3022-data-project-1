import duckdb
import logging


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log'
)
logger = logging.getLogger(__name__)

def clean_parquet():

    con = None

    try:
            # Connect to local DuckDB instance
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # REMOVE DUPLICATE TRIPS ----------------------------------------------------
            # For each query: count the number of rows before and after, and log the difference
            # First count the initial number of rows
            row_count = con.execute(f"SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Total rows in trip_data initially: {row_count}")
            print(f"Total rows in trip_data initially: {row_count}")

            # Only keep unique rows
            con.execute(f"""
                CREATE TABLE trip_data_unique AS SELECT DISTINCT * FROM trip_data;
                DROP TABLE trip_data;
                ALTER TABLE trip_data_unique RENAME TO trip_data;
            """)
            logger.info("Removed duplicate entries")

            # Count number of rows left
            row_count_2 = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Total rows in trip_data after removing duplicates: {row_count_2}")
            print(f"Total rows in trip_data after removing duplicates: {row_count_2}")
            print(f"Number of duplicates: {row_count - row_count_2}")

            # REMOVE TRIPS WITH 0 PASSENGERS ----------------------------------------------------

            count_before = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]

            con.execute(f"""
                DELETE FROM trip_data WHERE passenger_count = 0; 
            """)
            logger.info("Removed trips with 0 passengers")

            count_after = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Removed {count_before - count_after} trips with 0 passengers. Total now: {count_after}")
            print(f"Removed {count_before - count_after} trips with 0 passengers. Total now: {count_after}")

            # REMOVE TRIPS 0 MILES IN LENGTH ----------------------------------------------------

            con.execute(f"""
                DELETE FROM trip_data WHERE trip_distance <= 0; 
            """)
            logger.info("Removed trips with 0 miles")

            count_after2 = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Removed {count_after - count_after2} trips with 0 miles. Total now: {count_after2}")
            print(f"Removed {count_after - count_after2} trips with 0 miles. Total now: {count_after2}")


            # REMOVE TRIPS GREATER THAN 100 MILES ----------------------------------------------------

            con.execute(f"""
                DELETE FROM trip_data WHERE trip_distance >= 100; 
            """)
            logger.info("Removed trips over 100 miles")

            count_after3 = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Removed {count_after2 - count_after3} trips over 100 miles. Total now: {count_after3}")
            print(f"Removed {count_after2 - count_after3} trips over 100 miles. Total now: {count_after3}")


            # REMOVE TRIPS OVER 1 DAY ------------------------------------------------------------------
            
            con.execute(f"""
                -- Calculate the length of trips and then subset
                DELETE FROM trip_data WHERE date_diff('day', pickup_datetime, dropoff_datetime) >= 1;
            """)
            logger.info("Removed trips over 1 day")

            count_after4 = con.execute("SELECT COUNT(*) FROM trip_data").fetchone()[0]
            logger.info(f"Removed {count_after3 - count_after4} trips over 1 day. Total now: {count_after4}")
            print(f"Removed {count_after3 - count_after4} trips over 1 day. Total now: {count_after4}")

            # FINALLY, VERIFY THE CONDITIONS DON'T EXIST ANYMORE ----------------------------------------------------
            # test1 is memory intensive, so commented out for now, but you can check the results by seeing the decrease in rows from removing duplicates earlier!
            # test1 = con.execute(f"SELECT COUNT(*) - COUNT(DISTINCT COLUMNS(*)) AS duplicate_row_count FROM trip_data;").fetchone()[0]
            test2 = con.execute(f"SELECT COUNT(*) FROM trip_data WHERE passenger_count = 0;" ).fetchone()[0]
            test3 = con.execute(f"SELECT COUNT(*) FROM trip_data WHERE trip_distance = 0;" ).fetchone()[0]
            test4 = con.execute(f"SELECT COUNT(*) FROM trip_data WHERE trip_distance >= 100;" ).fetchone()[0]
            test5 = con.execute(f"SELECT COUNT(*) FROM trip_data WHERE date_diff('day', pickup_datetime, dropoff_datetime) >= 1;" ).fetchone()[0]
 
            logger.info("Verify conditions")
            # logger.info(f"Unique trips: {test1}")
            logger.info(f"Trips with 0 passengers: {test2}")
            logger.info(f"Trips with 0 miles: {test3}")
            logger.info(f"Trips over 100 miles: {test4}")
            logger.info(f"Trips over 1 day: {test5}")
            # print(f"Unique trips: {test1}")
            print(f"Trips with 0 passengers: {test2}")
            print(f"Trips with 0 miles: {test3}")
            print(f"Trips over 100 miles: {test4}")
            print(f"Trips over 1 day: {test5}")


    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    clean_parquet()
