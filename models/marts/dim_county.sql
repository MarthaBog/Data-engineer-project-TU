select
    county_key,
    county_name,
    county_code
from {{ ref('county_seed') }}
