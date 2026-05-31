with history as (
    select
        week_key,
        iso_year,
        iso_week,
        avg(avg_temp) over hist_window as avg_temp_hist_avg,
        avg(avg_max_temp) over hist_window as avg_max_temp_hist_avg,
        avg(avg_min_temp) over hist_window as avg_min_temp_hist_avg,
        avg(total_precip) over hist_window as total_precip_hist_avg,
        avg(avg_wind) over hist_window as avg_wind_hist_avg,
        avg(total_sunshine) over hist_window as total_sunshine_hist_avg,
        avg(hot_county_day_count) over hist_window as hot_county_day_count_hist_avg,
        avg(cold_county_day_count) over hist_window as cold_county_day_count_hist_avg,
        count(*) over hist_window as hist_year_count
    from {{ ref('int_ilm_weekly_national') }}
    window hist_window as (
        partition by iso_week
        order by iso_year
        rows between unbounded preceding and 1 preceding
    )
)
select
    week_key,
    iso_year,
    iso_week,
    avg_temp_hist_avg,
    avg_max_temp_hist_avg,
    avg_min_temp_hist_avg,
    total_precip_hist_avg,
    avg_wind_hist_avg,
    total_sunshine_hist_avg,
    hot_county_day_count_hist_avg,
    cold_county_day_count_hist_avg,
    hist_year_count::int as hist_year_count
from history
