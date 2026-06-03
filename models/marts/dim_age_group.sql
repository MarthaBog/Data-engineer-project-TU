with age_groups as (
    select distinct age_group_label
    from {{ ref('stg_surmad') }}
)
select
    row_number() over (
        order by
            case age_group_label
                when 'Vanuserühmad kokku' then 1
                when '0-64' then 2
                when '65-79' then 3
                when '80 ja vanemad' then 4
                else 99
            end
    ) as age_group_key,
    age_group_label,
    case
        when age_group_label = '0-64' then 0
        when age_group_label = '65-79' then 65
        when age_group_label = '80 ja vanemad' then 80
        else null
    end as age_min,
    case
        when age_group_label = '0-64' then 64
        when age_group_label = '65-79' then 79
        else null
    end as age_max
from age_groups
