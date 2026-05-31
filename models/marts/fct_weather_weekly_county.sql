select
    weeks.week_key,
    county.county_key,
    weather.avg_temp,
    weather.avg_max_temp,
    weather.avg_min_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine,
    weather.hot_day_count,
    weather.cold_day_count,
    weather.observed_day_count
from {{ ref('int_ilm_weekly_county') }} as weather
join {{ ref('dim_week') }} as weeks
  on weather.week_key = weeks.week_key
join {{ ref('dim_county') }} as county
  on weather.county_name = county.county_name
