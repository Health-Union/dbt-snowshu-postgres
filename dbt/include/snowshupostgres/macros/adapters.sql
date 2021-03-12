
{% macro snowshupostgres__create_table_as(temporary, relation, sql) -%}
  {%- set unlogged = config.get('unlogged', default=false) -%}
  {%- set sql_header = config.get('sql_header', none) -%}

  {{ sql_header if sql_header is not none }}

  create {% if temporary -%}
    temporary
  {%- elif unlogged -%}
    unlogged
  {%- endif %} table {{ relation }}
  as (
    {{ sql }}
  );
{%- endmacro %}


{% macro snowshupostgres__create_schema(relation) -%}
  {% if relation.database -%}
    {{ adapter.verify_database(relation.database) }}
  {%- endif -%}
  {%- call statement('create_schema') -%}
    create schema if not exists {{ relation.without_identifier().include(database=False) }}
  {%- endcall -%}
{% endmacro %}


{% macro snowshupostgres__drop_schema(relation) -%}
  {% if relation.database -%}
    {{ adapter.verify_database(relation.database) }}
  {%- endif -%}
  {%- call statement('drop_schema') -%}
    drop schema if exists {{ relation.without_identifier().include(database=False) }} cascade
  {%- endcall -%}
{% endmacro %}


{% macro snowshupostgres__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      select
          column_name,
          data_type,
          character_maximum_length,
          numeric_precision,
          numeric_scale

      from {{ relation.information_schema('columns') }}
      where table_name = '{{ relation.identifier }}'
        {% if relation.schema %}
        and table_schema = '{{ relation.schema }}'
        {% endif %}
      order by ordinal_position

  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

/* foreign tables don't appear in pg_tables/views use info schema */
{% macro snowshupostgres__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    select
      '{{ schema_relation.database }}' as database,
      table_name as name,
      table_schema as schema,
      lower(case
        when table_type = 'BASE TABLE' then 'table'
        else table_type
      end) as type -- 'foreign' should get mapped to 'external' in dbt
    from information_schema.tables
    where table_schema ilike '{{ schema_relation.schema }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}


{% macro snowshupostgres__information_schema_name(database) -%}
  {% if database_name -%}
    {{ adapter.verify_database(database_name) }}
  {%- endif -%}
  information_schema
{%- endmacro %}


{% macro snowshupostgres__list_schemas(database) %}
  {% if database -%}
    {{ adapter.verify_database(database) }}
  {%- endif -%}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) %}
    select distinct nspname from pg_namespace
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}


{% macro snowshupostgres__check_schema_exists(information_schema, schema) -%}
  {% if information_schema.database -%}
    {{ adapter.verify_database(information_schema.database) }}
  {%- endif -%}
  {% call statement('check_schema_exists', fetch_result=True, auto_begin=False) %}
    select count(*) from pg_namespace where nspname = '{{ schema }}'
  {% endcall %}
  {{ return(load_result('check_schema_exists').table) }}
{% endmacro %}


{% macro snowshupostgres__current_timestamp() -%}
  now()
{%- endmacro %}

{% macro snowshupostgres__snapshot_string_as_time(timestamp) -%}
    {%- set result = "'" ~ timestamp ~ "'::timestamp without time zone" -%}
    {{ return(result) }}
{%- endmacro %}


{% macro snowshupostgres__snapshot_get_time() -%}
  {{ current_timestamp() }}::timestamp without time zone
{%- endmacro %}


{#
  Postgres tables have a maximum length off 63 characters, anything longer is silently truncated.
  Temp relations add a lot of extra characters to the end of table namers to ensure uniqueness.
  To prevent this going over the character limit, the base_relation name is truncated to ensure
  that name + suffix + uniquestring is < 63 characters.  
#}
{% macro snowshupostgres__make_temp_relation(base_relation, suffix) %}
    {% set dt = modules.datetime.datetime.now() %}
    {% set dtstring = dt.strftime("%H%M%S%f") %}
    {% set suffix_length = suffix|length + dtstring|length %}
    {% set relation_max_name_length = 63 %}
    {% if suffix_length > relation_max_name_length %}
        {% do exceptions.raise_compiler_error('Temp relation suffix is too long (' ~ suffix|length ~ ' characters). Maximum length is ' ~ (relation_max_name_length - dtstring|length) ~ ' characters.') %}
    {% endif %}
    {% set tmp_identifier = base_relation.identifier[:relation_max_name_length - suffix_length] ~ suffix ~ dtstring %}
    {% do return(base_relation.incorporate(
                                  path={
                                    "identifier": tmp_identifier,
                                    "schema": none,
                                    "database": none
                                  })) -%}
{% endmacro %}


{#
  By using dollar-quoting like this, users can embed anything they want into their comments
  (including nested dollar-quoting), as long as they do not use this exact dollar-quoting
  label. It would be nice to just pick a new one but eventually you do have to give up.
#}
{% macro snowshupostgres_escape_comment(comment) -%}
  {% if comment is not string %}
    {% do exceptions.raise_compiler_error('cannot escape a non-string: ' ~ comment) %}
  {% endif %}
  {%- set magic = '$dbt_comment_literal_block$' -%}
  {%- if magic in comment -%}
    {%- do exceptions.raise_compiler_error('The string ' ~ magic ~ ' is not allowed in comments.') -%}
  {%- endif -%}
  {{ magic }}{{ comment }}{{ magic }}
{%- endmacro %}


{% macro snowshupostgres__alter_relation_comment(relation, comment) %}
  {% set escaped_comment = snowshupostgres_escape_comment(comment) %}
  comment on {{ relation.type }} {{ relation }} is {{ escaped_comment }};
{% endmacro %}


{% macro snowshupostgres__alter_column_comment(relation, column_dict) %}
  {% for column_name in column_dict %}
    {% set comment = column_dict[column_name]['description'] %}
    {% set escaped_comment = snowshupostgres_escape_comment(comment) %}
    comment on column {{ relation }}.{{ adapter.quote(column_name) if column_dict[column_name]['quote'] else column_name }} is {{ escaped_comment }};
  {% endfor %}
{% endmacro %}
