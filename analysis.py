import duckdb
import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
    filename='analysis.log'
)
logger = logging.getLogger(__name__)

def calculate_largest_co2():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- What was the single largest carbon producing trip of all years for YELLOW and GREEN trips? 
            # Sort co2 output in descending order and keep the one with the highest co2 output 
            query = """
                SELECT vehicle_type, trip_distance, pickup_datetime, dropoff_datetime, trip_co2_kgs FROM (
                SELECT *, RANK() OVER (PARTITION BY vehicle_type ORDER BY trip_co2_kgs DESC) AS rank_co2
                FROM trip_data
                WHERE vehicle_type in ('yellow_taxi', 'green_taxi'))
                WHERE rank_co2 = 1
            """
            results = con.execute(query).fetchdf()
            logger.info("Queried highest CO2 producing trips")
            # Present the largest co2 trip, making sure to include its taxi color, and other identifying attributes
            for _, row in results.iterrows():
                vehicle_type = row['vehicle_type']
                distance = row['trip_distance']
                duration = row['dropoff_datetime'] - row['pickup_datetime']
                co2 = row['trip_co2_kgs']
                print(f"Largest CO2 trip for {vehicle_type}: {co2:.2f} kgs, Distance: {distance} miles, Duration: {duration}")
                logger.info(f"Largest CO2 trip for {vehicle_type}: {co2:.2f} kgs, Distance: {distance} miles, Duration: {duration}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")



def heavy_light_hours():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- What on average are the most carbon heavy and carbon light hours of the day
            # Sort the average of each hour in descending order, and pick the highest value as the hour that is most carbon heavy.
            # Repeat with ascending order, to pick the lowest value as the hour that is least carbon heavy
            query = """
                SELECT vehicle_type, hour_of_day, avg_co2,
                CASE WHEN rn_high = 1 THEN 'Most carbon-heavy hour'
                     WHEN rn_low = 1 THEN 'Least carbon-heavy hour'
                END AS label
                FROM (
                SELECT vehicle_type, hour_of_day, AVG(trip_co2_kgs) AS avg_co2,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) DESC) AS rn_high,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) ASC) AS rn_low
                FROM trip_data
                WHERE vehicle_type IN ('yellow_taxi', 'green_taxi')
                GROUP BY vehicle_type, hour_of_day) t 
                WHERE rn_high = 1 OR rn_low = 1
                ORDER BY vehicle_type
            """
            results = con.execute(query).fetchall()
            logger.info("Queried average co2 for each HOUR of day")
            # Present results
            for row in results:
                vehicle_type, hour, avg_co2, label = row
                output_text = f"Cab type: {vehicle_type}, {label}: Hour {hour}, Avg CO2 = {avg_co2:.2f} kg"
                print(output_text)
                logger.info(output_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")



def heavy_light_weekday():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- Which on average are the most carbon heavy and carbon light days of week
            # Sort the average of each weekday in descending order, and pick the highest value as the day that is most carbon heavy.
            # Repeat with ascending order, to pick the lowest value as the day that is least carbon heavy
            query = """
                SELECT vehicle_type, day_of_week, avg_co2,
                CASE WHEN rn_high = 1 THEN 'Most carbon-heavy day'
                     WHEN rn_low = 1 THEN 'Least carbon-heavy day'
                END AS label
                FROM (
                SELECT vehicle_type, day_of_week, AVG(trip_co2_kgs) AS avg_co2,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) DESC) AS rn_high,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) ASC) AS rn_low
                FROM trip_data
                WHERE vehicle_type IN ('yellow_taxi', 'green_taxi')
                GROUP BY vehicle_type, day_of_week) AS subquery 
                WHERE rn_high = 1 OR rn_low = 1
                ORDER BY vehicle_type
            """
            results = con.execute(query).fetchall()
            logger.info("Queried average co2 for each day of week")
            # Add mapping to the weekdays, so we know which is monday, tuesday, ... instead of numbers
            # Use duckdb docmentation for mapping! Sunday is 0, ...
            mapping = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
            # Present the results
            for row in results:
                vehicle_type, day, avg_co2, label = row
                day = mapping[day]
                output_text3 = f"Cab type: {vehicle_type}, {label}: {day}, Avg CO2 = {avg_co2:.2f} kg"
                print(output_text3)
                logger.info(output_text3)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")


def heavy_light_week():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- Which on average are the most carbon heavy and carbon light weeks of year
            # Sort the average of each week in descending order, and pick the highest value as the week that is most carbon heavy.
            # Repeat with ascending order, to pick the lowest value as the week that is least carbon heavy
            query = """
                SELECT vehicle_type, week_of_year, avg_co2,
                CASE WHEN rn_high = 1 THEN 'Most carbon-heavy week of year'
                     WHEN rn_low = 1 THEN 'Least carbon-heavy week of year'
                END AS label
                FROM (
                SELECT vehicle_type, week_of_year, AVG(trip_co2_kgs) AS avg_co2,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) DESC) AS rn_high,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) ASC) AS rn_low
                FROM trip_data
                WHERE vehicle_type IN ('yellow_taxi', 'green_taxi')
                GROUP BY vehicle_type, week_of_year) AS subquery 
                WHERE rn_high = 1 OR rn_low = 1
                ORDER BY vehicle_type
            """
            results = con.execute(query).fetchall()
            logger.info("Queried average co2 for each week of year")
            # Present results
            for row in results:
                vehicle_type, week, avg_co2, label = row
                output_text4 = f"Cab type: {vehicle_type}, {label}: {week}, Avg CO2 = {avg_co2:.2f} kg"
                print(output_text4)
                logger.info(output_text4)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")


def heavy_light_month():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- Which on average are the most carbon heavy and carbon months
            # Sort the average of each month in descending order, and pick the highest value as the month that is most carbon heavy.
            # Repeat with ascending order, to pick the lowest value as the month that is least carbon heavy
            query = """
                SELECT vehicle_type, month_of_year, avg_co2,
                CASE WHEN rn_high = 1 THEN 'Most carbon-heavy month'
                     WHEN rn_low = 1 THEN 'Least carbon-heavy month'
                END AS label
                FROM (
                SELECT vehicle_type, month_of_year, AVG(trip_co2_kgs) AS avg_co2,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) DESC) AS rn_high,
                ROW_NUMBER() OVER (PARTITION BY vehicle_type ORDER BY AVG(trip_co2_kgs) ASC) AS rn_low
                FROM trip_data
                WHERE vehicle_type IN ('yellow_taxi', 'green_taxi')
                GROUP BY vehicle_type, month_of_year) AS subquery 
                WHERE rn_high = 1 OR rn_low = 1
                ORDER BY vehicle_type
            """
            results = con.execute(query).fetchall()
            logger.info("Queried average co2 for each month of year")
            # Add mapping for readability and then present results
            mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                       7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
            for row in results:
                vehicle_type, month, avg_co2, label = row
                month = mapping[month]
                output_text5 = f"Cab type: {vehicle_type}, {label}: {month}, Avg CO2 = {avg_co2:.2f} kg"
                print(output_text5)
                logger.info(output_text5)

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")


def plot_month_co2():
    con = None
    try:
            con = duckdb.connect(database='emissions.duckdb', read_only=False)
            logger.info("Connected to DuckDB instance")

            # -- Matplotlib to make a time-series plot / histogram  
            # -- MONTH along the X-axis and CO2 totals along the Y-axis
            # -- Render two lines/bars/plots of data, one each for YELLOW and GREEN taxi trip CO2 totals
            # First, need to find the monthly totals, cummulative, across the years
            query = """
                SELECT vehicle_type, month_of_year, SUM(trip_co2_kgs) AS total_co2
                FROM trip_data
                WHERE vehicle_type IN ('yellow_taxi', 'green_taxi')
                GROUP BY vehicle_type, month_of_year
                ORDER BY vehicle_type
            """
            results = con.execute(query).fetchall()
            logger.info("Queried monthly totals of co2 for each vehicle type") 
            # Create mapping of months
            # Then initialize arrays to store monthly CO2 totals for each taxi type
            months = range(1, 13)
            mapping = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                       7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
            yellow_co2 = [0]*12
            green_co2 = [0]*12
            
            for row in results:
                vehicle_type, month, total_co2 = row
                if vehicle_type == 'yellow_taxi':
                    yellow_co2[month-1] = total_co2
                elif vehicle_type == 'green_taxi':
                    green_co2[month-1] = total_co2

            # # THIS PRINT OUT THE MONTHLY TOTALS SO I CAN CHECK IF THE GRAPH LOOKS "RIGHT"
            # print("\nMonthly totals (Yellow Taxi):")
            # for i, val in enumerate(yellow_co2, start=1):
            #     print(f"{mapping[i]}: {val:,.0f} kg")
            
            # print("\nMonthly totals (green Taxi):")
            # for i, val in enumerate(green_co2, start=1):
            #     print(f"{mapping[i]}: {val:,.0f} kg")

            # Create plots, yellow and green, and save them
            plt.figure(figsize=(10, 10))
            plt.plot(months, yellow_co2, marker='o', label='Yellow Taxi', color='goldenrod')
            plt.xlabel('Month (Cumulative across 2015–2024)')
            plt.ylabel('Total CO2 Emissions (kg)')
            plt.xticks(months, [mapping[m] for m in months], rotation=45)
            plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.ylim((20000000, 90000000))
            plt.title('Cumulative Monthly CO2 Emissions (2015–2024) For Yellow Taxi')
            plt.savefig('yellow_monthly_co2_emissions.png')
            plt.legend()
            plt.show()
            logger.info("YELLOW: Plotted monthly CO2 emissions and saved to yellow_monthly_co2_emissions.png")
            print("YELLOW: Plotted monthly CO2 emissions and saved to yellow_monthly_co2_emissions.png")
            
            plt.figure(figsize=(10, 10))
            plt.plot(months, green_co2, marker='o', label='Green Taxi', color='green')
            plt.xlabel('Month (Cumulative across 2015–2024)')
            plt.ylabel('Total CO2 Emissions (kg)')
            plt.xticks(months, [mapping[m] for m in months], rotation=45)
            plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.ylim((4000000, 7000000))
            plt.title('Cumulative Monthly CO2 Emissions (2015–2024) For Green Taxi')
            plt.savefig('green_monthly_co2_emissions.png')
            plt.legend()
            plt.show()
            logger.info("GREEN: Plotted monthly CO2 emissions and saved to green_monthly_co2_emissions.png")
            print("GREEN: Plotted monthly CO2 emissions and saved to green_monthly_co2_emissions.png")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    calculate_largest_co2()
    heavy_light_hours()
    heavy_light_weekday()
    heavy_light_week()
    heavy_light_month()
    plot_month_co2()
