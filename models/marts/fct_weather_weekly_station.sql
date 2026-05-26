select
    weeks.week_key,
    stations.station_key,
    weather.avg_temp,
    weather.total_precip,
    weather.avg_wind,
    weather.total_sunshine
from {{ ref('int_ilm_weekly_station') }} as weather
join {{ ref('dim_week') }} as weeks
  on weather.week_key = weeks.week_key
join {{ ref('dim_weather_station') }} as stations
  on weather.station_code = stations.station_code
