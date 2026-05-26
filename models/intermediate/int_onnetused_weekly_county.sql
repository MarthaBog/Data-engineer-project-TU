select
    week_key,
    iso_year,
    iso_week,
    county_name,
    count(*)::int as accident_count,
    sum(injured_count)::int as injured_count,
    sum(killed_count)::int as killed_count
from {{ ref('int_onnetused_daily') }}
group by 1, 2, 3, 4
