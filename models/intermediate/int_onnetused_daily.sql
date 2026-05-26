select
    accident_id,
    date_day,
    accident_time,
    county_name,
    municipality_name,
    iso_year,
    iso_week,
    week_key,
    killed_count,
    injured_count
from {{ ref('stg_onnetused') }}
