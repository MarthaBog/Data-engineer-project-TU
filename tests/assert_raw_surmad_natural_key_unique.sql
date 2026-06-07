select
    "Näitaja",
    "Nädal",
    "Vaatlusperiood",
    "Sugu",
    "Vanuserühm",
    count(*) as row_count
from {{ source('raw', 'surmad') }}
group by 1, 2, 3, 4, 5
having count(*) > 1
