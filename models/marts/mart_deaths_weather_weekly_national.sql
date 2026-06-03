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
    death_history.deaths_count_hist_avg,
    death_history.hist_year_count as deaths_hist_year_count,
    deaths.deaths_count - death_history.deaths_count_hist_avg as deaths_count_vs_hist,
    weather.avg_temp,
    weather.avg_max_temp,
    weather.avg_min_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine,
    weather.hot_county_day_count,
    weather.cold_county_day_count,
    weather.observed_county_day_count,
    weather_history.avg_temp_hist_avg,
    weather.avg_temp - weather_history.avg_temp_hist_avg as avg_temp_vs_hist,
    weather_history.avg_max_temp_hist_avg,
    weather.avg_max_temp - weather_history.avg_max_temp_hist_avg as avg_max_temp_vs_hist,
    weather_history.avg_min_temp_hist_avg,
    weather.avg_min_temp - weather_history.avg_min_temp_hist_avg as avg_min_temp_vs_hist,
    weather_history.total_precip_hist_avg,
    weather.total_precip - weather_history.total_precip_hist_avg as total_precip_vs_hist,
    weather_history.avg_wind_hist_avg,
    weather.avg_wind - weather_history.avg_wind_hist_avg as avg_wind_vs_hist,
    weather_history.total_sunshine_hist_avg,
    weather.total_sunshine - weather_history.total_sunshine_hist_avg as total_sunshine_vs_hist,
    weather_history.hot_county_day_count_hist_avg,
    weather.hot_county_day_count - weather_history.hot_county_day_count_hist_avg as hot_county_day_count_vs_hist,
    weather_history.cold_county_day_count_hist_avg,
    weather.cold_county_day_count - weather_history.cold_county_day_count_hist_avg as cold_county_day_count_vs_hist,
    weather_history.hist_year_count as weather_hist_year_count
from {{ ref('fct_deaths_weekly') }} as deaths
join {{ ref('dim_week') }} as weeks
  on deaths.week_key = weeks.week_key
join {{ ref('dim_age_group') }} as age_groups
  on deaths.age_group_key = age_groups.age_group_key
join {{ ref('dim_sex') }} as sexes
  on deaths.sex_key = sexes.sex_key
left join {{ ref('int_surmad_weekly_hist') }} as death_history
  on deaths.week_key = death_history.week_key
 and age_groups.age_group_label = death_history.age_group_label
 and sexes.sex_label = death_history.sex_label
left join {{ ref('int_ilm_weekly_national') }} as weather
  on deaths.week_key = weather.week_key
left join {{ ref('int_ilm_weekly_national_hist') }} as weather_history
  on deaths.week_key = weather_history.week_key
