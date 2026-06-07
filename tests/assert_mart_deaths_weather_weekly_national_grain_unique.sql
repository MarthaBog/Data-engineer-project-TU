select
    week_key,
    age_group_key,
    sex_key,
    count(*) as row_count
from {{ ref('mart_deaths_weather_weekly_national') }}
group by 1, 2, 3
having count(*) > 1
