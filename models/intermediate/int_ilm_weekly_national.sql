select
    week_key,
    iso_year,
    iso_week,
    avg(avg_temp) as avg_temp,
    avg(total_precip) as total_precip,
    avg(avg_wind) as avg_wind,
    avg(total_sunshine) as total_sunshine
from {{ ref('int_ilm_weekly_station') }}
group by 1, 2, 3
