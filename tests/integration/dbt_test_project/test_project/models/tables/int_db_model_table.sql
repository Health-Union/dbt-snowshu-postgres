{{ config(materialized='table') }}

{% set int_db_relation = adapter.get_relation(database='postgres',
                            schema='internal_schema',
                            identifier="internal_table") %}
select *
from {{ int_db_relation }}




