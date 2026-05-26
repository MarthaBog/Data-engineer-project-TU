select
    {{ generate_week_key('"Vaatlusperiood"', '"Nädal"') }} as week_key,
    "Vaatlusperiood"::int as iso_year,
    "Nädal"::int as iso_week,
    "Sugu"::text as sex_label,
    "Vanuserühm"::text as age_group_label,
    "value"::numeric as deaths_count,
    case
        when "Vaatlusperiood"::int >= 2025 then true
        else false
    end as is_preliminary
from {{ source('raw', 'surmad') }}
where "Näitaja" = 'Surmade arv'
  and "Nädal" <> 'Nädalad kokku'
  and nullif(trim("value"::text), 'NaN') is not null
