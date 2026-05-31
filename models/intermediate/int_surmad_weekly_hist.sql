with history as (
    select
        week_key,
        iso_year,
        iso_week,
        age_group_label,
        sex_label,
        avg(deaths_count) over hist_window as deaths_count_hist_avg,
        count(*) over hist_window as hist_year_count
    from {{ ref('stg_surmad') }}
    window hist_window as (
        partition by age_group_label, sex_label, iso_week
        order by iso_year
        rows between unbounded preceding and 1 preceding
    )
)
select
    week_key,
    iso_year,
    iso_week,
    age_group_label,
    sex_label,
    deaths_count_hist_avg,
    hist_year_count::int as hist_year_count
from history
