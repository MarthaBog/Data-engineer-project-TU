select
    week_key,
    iso_year,
    iso_week,
    station_code,
    station_name,
    avg(avg_temp) as avg_temp,
    sum(total_precip) as total_precip,
    avg(avg_wind) as avg_wind,
    sum(total_sunshine) as total_sunshine
from {{ ref('int_ilm_daily_station') }}
group by 1, 2, 3, 4, 5
