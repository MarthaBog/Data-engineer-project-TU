select
    weeks.week_key,
    age_groups.age_group_key,
    sexes.sex_key,
    deaths.deaths_count::int as deaths_count,
    deaths.is_preliminary
from {{ ref('int_surmad_weekly') }} as deaths
join {{ ref('dim_week') }} as weeks
  on deaths.week_key = weeks.week_key
join {{ ref('dim_age_group') }} as age_groups
  on deaths.age_group_label = age_groups.age_group_label
join {{ ref('dim_sex') }} as sexes
  on deaths.sex_label = sexes.sex_label
