select 'fct_deaths_weekly' as model_name, week_key::text as grain_key, deaths_count::numeric as bad_value
from {{ ref('fct_deaths_weekly') }}
where deaths_count < 0

union all

select 'fct_traffic_weekly_county', concat(week_key, ':', county_key), accident_count::numeric
from {{ ref('fct_traffic_weekly_county') }}
where accident_count < 0

union all

select 'fct_traffic_weekly_county', concat(week_key, ':', county_key), injured_count::numeric
from {{ ref('fct_traffic_weekly_county') }}
where injured_count < 0

union all

select 'fct_traffic_weekly_county', concat(week_key, ':', county_key), killed_count::numeric
from {{ ref('fct_traffic_weekly_county') }}
where killed_count < 0

union all

select 'fct_weather_weekly_county', concat(week_key, ':', county_key), total_precip
from {{ ref('fct_weather_weekly_county') }}
where total_precip < 0

union all

select 'fct_weather_weekly_county', concat(week_key, ':', county_key), total_sunshine
from {{ ref('fct_weather_weekly_county') }}
where total_sunshine < 0

union all

select 'fct_weather_weekly_county', concat(week_key, ':', county_key), observed_day_count::numeric
from {{ ref('fct_weather_weekly_county') }}
where observed_day_count < 0

union all

select 'fct_weather_weekly_station', concat(week_key, ':', station_key), total_precip
from {{ ref('fct_weather_weekly_station') }}
where total_precip < 0

union all

select 'fct_weather_weekly_station', concat(week_key, ':', station_key), total_sunshine
from {{ ref('fct_weather_weekly_station') }}
where total_sunshine < 0

union all

select 'fct_weather_weekly_station', concat(week_key, ':', station_key), observed_day_count::numeric
from {{ ref('fct_weather_weekly_station') }}
where observed_day_count < 0
