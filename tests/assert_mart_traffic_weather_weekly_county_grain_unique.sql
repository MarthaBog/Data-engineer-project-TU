select
    week_key,
    county_key,
    count(*) as row_count
from {{ ref('mart_traffic_weather_weekly_county') }}
group by 1, 2
having count(*) > 1
