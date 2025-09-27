{{ config(materialized='table') }}

-- Call on co2_grams_per_mile from the vehicle_emissions table, so we are not hardcoding numerical values
-- Use the equation, trip_co2_kgs = trip_distance * co2_grams_per_mile / 1000
SELECT 
t.*,
e.co2_grams_per_mile,
(t.trip_distance * e.co2_grams_per_mile) / 1000.0 AS trip_co2_kgs,

-- Calculate average miles per hour based on distance / duration of the trip, multiplied by 3600 to convert seconds to hours, 
-- Insert that value as a new column avg_mph
t.trip_distance / (EXTRACT(EPOCH FROM (t.dropoff_datetime - t.pickup_datetime)) / 3600.0) AS avg_mph,

-- Extract the HOUR of the day from the pickup_time AS a new column hour_of_day
hour(t.pickup_datetime) AS hour_of_day,

-- Extract the DAY OF WEEK from the pickup time AS as a new column day_of_week
dayofweek(t.pickup_datetime) AS day_of_week,

-- Extract the WEEK NUMBER from the pickup time AS a new column week_of_year
weekofyear(t.pickup_datetime) AS week_of_year,

-- Extract the MONTH from the pickup time AS a new column month_of_year
month(t.pickup_datetime) AS month_of_year

-- Lastly, join the calculations back to trip_data table
FROM trip_data t
LEFT JOIN vehicle_emissions e
ON lower(trim(t.vehicle_type)) = lower(trim(e.vehicle_type))
WHERE t.dropoff_datetime > t.pickup_datetime
