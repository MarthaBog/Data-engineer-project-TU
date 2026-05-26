select
    week_key,
    iso_year,
    iso_week,
    date_day,
    station_code,
    station_name,
    max(case when metric_name = 'Air temperature (daily avg)' then metric_value end) as avg_temp,
    max(case when metric_name = 'Precipitation (daily sum)' then metric_value end) as total_precip,
    max(case when metric_name = 'Wind speed (daily avg)' then metric_value end) as avg_wind,
    max(case when metric_name = 'Sunshine duration (daily sum)' then metric_value end) as total_sunshine
from {{ ref('stg_ilm') }}
group by 1, 2, 3, 4, 5, 6
