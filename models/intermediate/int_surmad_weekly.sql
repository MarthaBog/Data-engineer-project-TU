select
    week_key,
    iso_year,
    iso_week,
    age_group_label,
    sex_label,
    deaths_count,
    is_preliminary
from {{ ref('stg_surmad') }}
