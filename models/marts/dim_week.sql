with all_weeks as (
    select week_key, iso_year, iso_week from {{ ref('stg_surmad') }}
    union
    select week_key, iso_year, iso_week from {{ ref('int_onnetused_weekly_county') }}
    union
    select week_key, iso_year, iso_week from {{ ref('int_ilm_weekly_county') }}
)
select distinct
    week_key,
    iso_year,
    iso_week,
    to_date(iso_year::text || '-' || lpad(iso_week::text, 2, '0') || '-1', 'IYYY-IW-ID') as week_start_date,
    (
        to_date(iso_year::text || '-' || lpad(iso_week::text, 2, '0') || '-1', 'IYYY-IW-ID')
        + interval '6 day'
    )::date as week_end_date
from all_weeks
