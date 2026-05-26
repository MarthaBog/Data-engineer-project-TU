{% macro normalize_county_name(county_expression) -%}
trim(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                lower({{ county_expression }}),
                '\s+maakond$',
                ''
            ),
            '\s+mk$',
            ''
        ),
        '\s+',
        ' '
    )
)
{%- endmacro %}
