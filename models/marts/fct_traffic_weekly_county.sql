select
    weeks.week_key,
    county.county_key,
    traffic.accident_count,
    traffic.injured_count,
    traffic.killed_count
from {{ ref('int_onnetused_weekly_county') }} as traffic
join {{ ref('dim_week') }} as weeks
  on traffic.week_key = weeks.week_key
join {{ ref('dim_county') }} as county
  on traffic.county_name = county.county_name
