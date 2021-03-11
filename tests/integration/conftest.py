""" Fixtures and config for pytest. """
from pytest import fixture
from sqlalchemy import create_engine


class SetupObject:  # pylint:disable=too-few-public-methods
    """ Container class for db setup values. """

    pg_container = "postgres-container"
    user = "postgres"
    password = "postgres"
    ext_database = "external_db"
    foreign_server = ext_database + "_server"
    ext_schema = "external_schema"
    foreign_schema = ext_database + "__" + ext_schema
    ext_table = "external_table"
    ext_table_vals = range(10)
    int_database = "postgres"
    int_schema = "internal_schema"
    int_table = "internal_table"
    int_table_vals = range(10)


def setup_external_database(connection, setup: SetupObject):
    """ Create the 'external' database objects for testing. """
    # create schema
    connection.execute(f"create schema {setup.ext_schema}")
    # create table
    connection.execute(f"create table {setup.ext_schema}.{setup.ext_table} (id int)")
    # populate table
    val_rows = [f"({v})" for v in setup.ext_table_vals]
    connection.execute(f"insert into {setup.ext_schema}.{setup.ext_table} values {','.join(val_rows)}")


def setup_internal_database(connection, setup: SetupObject):
    """ Set up the 'internal' database objects for testing. """
    # create schema
    connection.execute(f"create schema {setup.int_schema}")
    # create table
    connection.execute(f"create table {setup.int_schema}.{setup.int_table} (id int)")
    # populate table
    val_rows = [f"({v})" for v in setup.int_table_vals]
    connection.execute(f"insert into {setup.int_schema}.{setup.int_table} values {','.join(val_rows)}")


def setup_foreign_data_wrapper(connection, setup: SetupObject):
    """ Set up the foreign data wrapper objects for testing. """
    # add foreign data wrapper
    connection.execute("create extension postgres_fdw")
    # create external server
    connection.execute(f"CREATE SERVER {setup.foreign_server} FOREIGN DATA WRAPPER "
                       f"postgres_fdw OPTIONS (host 'localhost', dbname '{setup.ext_database}', port '5432')")
    # create user mapping
    connection.execute(f"CREATE USER MAPPING FOR {setup.user} SERVER {setup.foreign_server} "
                       f"OPTIONS (user '{setup.user}', password '{setup.password}')")
    # create schema for import (mimicing snowshu naming)
    connection.execute(f"create schema {setup.foreign_schema}")
    # link foreign data
    connection.execute(f"IMPORT FOREIGN SCHEMA {setup.ext_schema} FROM SERVER "
                       f"{setup.foreign_server} INTO {setup.foreign_schema}")


@fixture(scope="session")
def setup_db():
    """ Set up entire test database. """
    setup = SetupObject()
    pg_conn_string = f"postgresql://{setup.user}:{setup.password}@{setup.pg_container}:5432/{setup.int_database}"
    ext_conn_string = f"postgresql://{setup.user}:{setup.password}@{setup.pg_container}:5432/{setup.ext_database}"
    pg_engine = create_engine(pg_conn_string)
    ext_engine = create_engine(ext_conn_string)
    with pg_engine.connect() as connection:
        results = connection.execute(f"SELECT datname FROM pg_catalog.pg_database "
                                     f"WHERE datname='{setup.ext_database}'")\
                            .fetchall()
        if len(results) > 0:
            print("Postgres already has the external_db present. Skipping setup")
            return pg_engine, setup
        connection.execute("commit")
        connection.execute(f"create database {setup.ext_database}")

    with ext_engine.connect() as connection:
        setup_external_database(connection, setup)

    with pg_engine.connect() as connection:
        setup_internal_database(connection, setup)
        setup_foreign_data_wrapper(connection, setup)

    return pg_engine, setup
