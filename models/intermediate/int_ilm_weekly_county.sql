select
    week_key,
    iso_year,
    iso_week,
    county_name,
    avg(avg_temp) as avg_temp,
    avg(max_temp) as avg_max_temp,
    avg(min_temp) as avg_min_temp,
    sum(total_precip) as total_precip,
    avg(avg_wind) as avg_wind,
    sum(total_sunshine) as total_sunshine,
    sum(case when max_temp > 30 then 1 else 0 end)::int as hot_day_count,
    sum(case when min_temp < -10 then 1 else 0 end)::int as cold_day_count,
    count(*)::int as observed_day_count
from {{ ref('int_ilm_daily_county') }}
group by
    week_key,
    iso_year,
    iso_week,
    county_name
