select
    weather.week_key,
    weather.iso_year,
    weather.iso_week,
    weather.date_day,
    mapping.county_name,
    avg(weather.avg_temp) as avg_temp,
    avg(weather.max_temp) as max_temp,
    avg(weather.min_temp) as min_temp,
    avg(weather.total_precip) as total_precip,
    avg(weather.avg_wind) as avg_wind,
    avg(weather.total_sunshine) as total_sunshine
from {{ ref('int_ilm_daily_station') }} as weather
join {{ ref('station_county_map') }} as mapping
  on weather.station_code = mapping.station_code
group by
    weather.week_key,
    weather.iso_year,
    weather.iso_week,
    weather.date_day,
    mapping.county_name
