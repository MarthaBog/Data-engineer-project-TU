select
    kuupaev,
    kell,
    maakond,
    omavalitsus,
    hukkunud,
    vigastatud,
    count(*) as row_count
from {{ source('raw', 'onnetused') }}
group by 1, 2, 3, 4, 5, 6
having count(*) > 1
