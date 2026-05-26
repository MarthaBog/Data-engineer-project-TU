select
    deaths.week_key,
    weeks.iso_year,
    weeks.iso_week,
    weeks.week_start_date,
    weeks.week_end_date,
    deaths.age_group_key,
    age_groups.age_group_label,
    age_groups.age_min,
    age_groups.age_max,
    deaths.sex_key,
    sexes.sex_code,
    sexes.sex_label,
    deaths.deaths_count,
    deaths.is_preliminary,
    weather.avg_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine
from {{ ref('fct_deaths_weekly') }} as deaths
join {{ ref('dim_week') }} as weeks
  on deaths.week_key = weeks.week_key
join {{ ref('dim_age_group') }} as age_groups
  on deaths.age_group_key = age_groups.age_group_key
join {{ ref('dim_sex') }} as sexes
  on deaths.sex_key = sexes.sex_key
left join {{ ref('int_ilm_weekly_national') }} as weather
  on deaths.week_key = weather.week_key
