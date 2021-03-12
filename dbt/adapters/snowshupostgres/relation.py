""" Override for the the Relation and Column classes. """
from dataclasses import dataclass
from dbt.adapters.postgres import PostgresColumn
from dbt.adapters.postgres.relation import PostgresRelation


@dataclass(frozen=True, eq=False, repr=False)
class SnowshuPostgresRelation(PostgresRelation):  # pylint: disable=too-many-ancestors
    """ Override for postgres relation. No changes needed. """


class SnowshuPostgresColumn(PostgresColumn):
    """ Override for postgres column. No changes needed. """
