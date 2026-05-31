with sexes as (
    select distinct sex_label
    from {{ ref('stg_surmad') }}
)
select
    row_number() over (
        order by
            case sex_label
                when 'Mehed ja naised' then 1
                when 'Mehed' then 2
                when 'Naised' then 3
                else 99
            end
    ) as sex_key,
    case
        when sex_label = 'Mehed ja naised' then 'all'
        when sex_label = 'Mehed' then 'male'
        when sex_label = 'Naised' then 'female'
        else lower(sex_label)
    end as sex_code,
    sex_label
from sexes
