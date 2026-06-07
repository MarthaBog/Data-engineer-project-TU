select
    week_key,
    iso_year,
    iso_week,
    week_start_date,
    week_end_date
from {{ ref('dim_week') }}
where iso_week not between 1 and 53
   or iso_year < 2020
   or iso_year > extract(year from current_date)::int + 1
   or week_start_date > week_end_date
