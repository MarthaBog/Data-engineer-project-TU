with history as (
    select
        week_key,
        iso_year,
        iso_week,
        county_name,
        avg(accident_count) over hist_window as accident_count_hist_avg,
        avg(injured_count) over hist_window as injured_count_hist_avg,
        avg(killed_count) over hist_window as killed_count_hist_avg,
        count(*) over hist_window as hist_year_count
    from {{ ref('int_onnetused_weekly_county') }}
    window hist_window as (
        partition by county_name, iso_week
        order by iso_year
        rows between unbounded preceding and 1 preceding
    )
)
select
    week_key,
    iso_year,
    iso_week,
    county_name,
    accident_count_hist_avg,
    injured_count_hist_avg,
    killed_count_hist_avg,
    hist_year_count::int as hist_year_count
from history
