select
    'fct_weather_weekly_county' as model_name,
    concat(week_key, ':', county_key) as grain_key,
    observed_day_count
from {{ ref('fct_weather_weekly_county') }}
where observed_day_count not between 1 and 7

union all

select
    'fct_weather_weekly_station' as model_name,
    concat(week_key, ':', station_key) as grain_key,
    observed_day_count
from {{ ref('fct_weather_weekly_station') }}
where observed_day_count not between 1 and 7
