with typed as (
    select
        trim("jaam_kood") as station_code,
        trim("jaam_nimi") as station_name,
        make_date("aasta"::int, "kuu"::int, "paev"::int) as date_day,
        "aasta"::int as source_year,
        "kuu"::int as source_month,
        "paev"::int as source_day,
        trim("element_kood") as metric_code,
        trim("element_nimi_eng") as metric_name,
        trim("element_yhik_eng") as metric_unit,
        nullif("vaartus", '')::numeric as metric_value,
        nullif("avaandmed_ts", '')::timestamptz as source_loaded_at
    from {{ source('raw', 'ilm') }}
),
filtered as (
    select *
    from typed
    where metric_name in (
        'Air temperature (daily avg)',
        'Air temperature (daily max)',
        'Air temperature (daily min)',
        'Precipitation (daily sum)',
        'Wind speed (daily avg)',
        'Sunshine duration (daily sum)'
    )
)
select
    station_code,
    station_name,
    date_day,
    extract(isoyear from date_day)::int as iso_year,
    extract(week from date_day)::int as iso_week,
    {{ generate_week_key("extract(isoyear from date_day)::int", "extract(week from date_day)::int") }} as week_key,
    source_year,
    source_month,
    source_day,
    metric_code,
    metric_name,
    metric_unit,
    metric_value,
    source_loaded_at
from filtered
where metric_value is not null
