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
    traffic_history.accident_count_hist_avg,
    traffic.accident_count - traffic_history.accident_count_hist_avg as accident_count_vs_hist,
    traffic_history.injured_count_hist_avg,
    traffic.injured_count - traffic_history.injured_count_hist_avg as injured_count_vs_hist,
    traffic_history.killed_count_hist_avg,
    traffic.killed_count - traffic_history.killed_count_hist_avg as killed_count_vs_hist,
    traffic_history.hist_year_count as traffic_hist_year_count,
    weather.avg_temp,
    weather.avg_max_temp,
    weather.avg_min_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine,
    weather.hot_day_count,
    weather.cold_day_count,
    weather.observed_day_count,
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
    weather_history.hot_day_count_hist_avg,
    weather.hot_day_count - weather_history.hot_day_count_hist_avg as hot_day_count_vs_hist,
    weather_history.cold_day_count_hist_avg,
    weather.cold_day_count - weather_history.cold_day_count_hist_avg as cold_day_count_vs_hist,
    weather_history.hist_year_count as weather_hist_year_count
from {{ ref('fct_traffic_weekly_county') }} as traffic
join {{ ref('dim_week') }} as weeks
  on traffic.week_key = weeks.week_key
join {{ ref('dim_county') }} as county
  on traffic.county_key = county.county_key
left join {{ ref('int_onnetused_weekly_county_hist') }} as traffic_history
  on traffic.week_key = traffic_history.week_key
 and county.county_name = traffic_history.county_name
left join {{ ref('fct_weather_weekly_county') }} as weather
  on traffic.week_key = weather.week_key
 and traffic.county_key = weather.county_key
left join {{ ref('int_ilm_weekly_county_hist') }} as weather_history
  on traffic.week_key = weather_history.week_key
 and county.county_name = weather_history.county_name
