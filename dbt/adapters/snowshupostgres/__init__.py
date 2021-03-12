"""
dbt adapter plugin for a Snowshu Postgres replica.

This adapter makes the necessary adjustments to the get_relation
functionality to support Snowshu postgres replicas that need to
handle cross-database queries.
"""
from dbt.adapters.snowshupostgres.connections import SnowshuPostgresCredentials
from dbt.adapters.snowshupostgres.impl import SnowshuPostgresAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import snowshupostgres


Plugin = AdapterPlugin(
    adapter=SnowshuPostgresAdapter,
    credentials=SnowshuPostgresCredentials,
    include_path=snowshupostgres.PACKAGE_PATH)
