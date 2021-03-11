""" Overrides for Credentials and ConnectionManager classes. """
from dataclasses import dataclass
from dbt.adapters.postgres import PostgresCredentials
from dbt.adapters.postgres import PostgresConnectionManager


@dataclass
class SnowshuPostgresCredentials(PostgresCredentials):
    """ Snowshu postgres crendentials class. """

    @property
    def type(self):
        """ Type override for snowshupostgres. """
        return 'snowshupostgres'


class SnowshuPostgresConnectionManager(PostgresConnectionManager):
    """ Snowshu postgres connection manager. """

    TYPE = 'snowshupostgres'
