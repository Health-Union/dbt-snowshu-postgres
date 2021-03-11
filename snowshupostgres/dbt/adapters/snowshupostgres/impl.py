""" Override for the the Adapter class. """
from typing import Optional
import dbt
from dbt.adapters.base.meta import available
from dbt.adapters.base import BaseRelation
from dbt.adapters.postgres import PostgresAdapter
from dbt.adapters.postgres.impl import PostgresConfig
from dbt.adapters.snowshupostgres.relation import SnowshuPostgresColumn, SnowshuPostgresRelation
from dbt.adapters.snowshupostgres.connections import SnowshuPostgresConnectionManager


# TODO reduce this qualification?
# Repoint the macro name since the postgres version is inaccessible
dbt.adapters.postgres.impl.GET_RELATIONS_MACRO_NAME = 'snowshupostgres_get_relations'


class SnowshuPostgresAdapter(PostgresAdapter):
    """
    The Snowshu dbt adapter for postgres replicas that need cross-db support.

    If no cross-db support is required, the base Postgres adapter
    can be used in place of this one.

    Note: Theoretically, this class should inherit all macros
    from the PostgresAdapter. However, there seems to be some
    problem referencing the `postgres__*` macros in the same
    way that the redshift adapter does.
    """

    ConnectionManager = SnowshuPostgresConnectionManager
    Relation = SnowshuPostgresRelation
    Column = SnowshuPostgresColumn
    AdapterSpecificConfigs = PostgresConfig

    @available.parse_none
    def get_relation(self, database: str, schema: str, identifier: str) -> Optional[BaseRelation]:
        """
        Override of the postgres get_relation function for cross-db support.

        The default behavior of supporting cross-database queries in
        snowshu postgres replicas is to use foreign data wrappers and
        create schemas named `external_database__external_schema`.

        These schemas contains all of the sampled data from
        `external_database.external_schema` which allows simulating a
        cross-db query if the relation's schema and database are adjusted
        accordingly.

        Ex:
            If adapter is connected to `postgres.public`,
            the database values are compared to adjust the relation naming.

            adapter.get_relation(database="external_db",
                                    schema="external_schema",
                                    identifier="external_table")

            will return a relation where relation.database=="postgres"
            relation.schema=="external_db__external_schema" and
            relation.identifier=="external_table".
        """
        if database.startswith('"'):
            database = database.strip('"')
        expected_db = self.config.credentials.database
        if database.lower() != expected_db.lower():
            schema = database + "__" + schema
            database = expected_db
        return super().get_relation(database, schema, identifier)
