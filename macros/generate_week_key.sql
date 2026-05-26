{% macro generate_week_key(iso_year, iso_week) -%}
(
    ({{ iso_year }})::int * 100
    + lpad(({{ iso_week }})::text, 2, '0')::int
)
{%- endmacro %}
