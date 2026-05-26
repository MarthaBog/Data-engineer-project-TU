with typed as (
    select
        id as accident_id,
        nullif(kuupaev, '')::date as date_day,
        nullif(kell, '')::time as accident_time,
        trim(maakond) as county_name_raw,
        trim(omavalitsus) as municipality_name,
        coalesce(hukkunud, 0)::int as killed_count,
        coalesce(vigastatud, 0)::int as injured_count
    from {{ source('raw', 'onnetused') }}
    where nullif(kuupaev, '') is not null
),
enriched as (
    select
        accident_id,
        date_day,
        accident_time,
        initcap({{ normalize_county_name('county_name_raw') }}) as county_name,
        municipality_name,
        extract(isoyear from date_day)::int as iso_year,
        extract(week from date_day)::int as iso_week,
        killed_count,
        injured_count
    from typed
)
select
    accident_id,
    date_day,
    accident_time,
    county_name,
    municipality_name,
    iso_year,
    iso_week,
    {{ generate_week_key('iso_year', 'iso_week') }} as week_key,
    killed_count,
    injured_count
from enriched
where county_name is not null
