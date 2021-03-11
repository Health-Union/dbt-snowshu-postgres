{% set ext_db_relation = adapter.get_relation(database='external_db',
                            schema='external_schema',
                            identifier="external_table") %}
select *
from {{ ext_db_relation }}

