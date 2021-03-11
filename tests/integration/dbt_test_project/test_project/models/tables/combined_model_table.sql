{{ config(materialized='table') }}

{% set ext_db_relation = adapter.get_relation(database='external_db',
                            schema='external_schema',
                            identifier="external_table") %}
{% set int_db_relation = adapter.get_relation(database='postgres',
                            schema='internal_schema',
                            identifier="internal_table") %}

{%- set ext_columns = adapter.get_columns_in_relation(ext_db_relation) %}
{%- set int_columns = adapter.get_columns_in_relation(int_db_relation) %}


SELECT
    {% for column in int_columns %}
        int_rel.{{ column.name }} as int_{{column.name}},
    {% endfor %}
    {% for column in ext_columns %}
        ext_rel.{{ column.name }} as ext_{{column.name}},
    {% endfor %}
    case when ext_rel.id % 2 = 0 then 'even' else 'odd' end as ext_parity,
    case when int_rel.id % 2 = 0 then 'even' else 'odd' end as int_parity
from {{ int_db_relation }} as int_rel
full outer join {{ ext_db_relation }} as ext_rel
    on int_rel.id % 2 = ext_rel.id % 2