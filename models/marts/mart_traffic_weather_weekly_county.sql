select
    traffic.week_key,
    weeks.iso_year,
    weeks.iso_week,
    weeks.week_start_date,
    weeks.week_end_date,
    traffic.county_key,
    county.county_name,
    county.county_code,
    traffic.accident_count,
    traffic.injured_count,
    traffic.killed_count,
    weather.avg_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine
from {{ ref('fct_traffic_weekly_county') }} as traffic
join {{ ref('dim_week') }} as weeks
  on traffic.week_key = weeks.week_key
join {{ ref('dim_county') }} as county
  on traffic.county_key = county.county_key
left join {{ ref('fct_weather_weekly_county') }} as weather
  on traffic.week_key = weather.week_key
 and traffic.county_key = weather.county_key
