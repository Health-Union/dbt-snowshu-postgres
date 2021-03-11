""" Tests for output of `dbt run` on the test project. """
import os
import subprocess
from pathlib import Path
from pytest import fixture


@fixture(scope="session")
def dbt_run(setup_db):
    """ Fixture to call `dbt run`. """
    engine, setup = setup_db
    file_dir = Path(__file__).parent
    os.chdir(file_dir / "./test_project")
    _ = subprocess.run(["dbt", "run"], check=True)
    return engine, setup


def verify_simple_model(model_records, table_vals):
    """ Verification for models that copy tables. """
    assert len(model_records) == len(table_vals)
    assert {rec.id for rec in model_records} == set(table_vals)


def verify_combined_model(model_records):
    """ Verification for joined model on int parity. """
    for rec in model_records:
        assert rec.ext_id % 2 == rec.int_id % 2
        assert (rec.int_id % 2 == 0 and rec.int_parity == "even") \
               or (rec.int_id % 2 == 1 and rec.int_parity == "odd")
        assert (rec.ext_id % 2 == 0 and rec.ext_parity == "even") \
               or (rec.ext_id % 2 == 1 and rec.ext_parity == "odd")


# TODO add sample_profiles
def test_dbt_tables(dbt_run):  # pylint:disable=redefined-outer-name
    """ Tests the table models generate correctly. """
    engine, setup = dbt_run
    with engine.connect() as connection:
        # look in the schema that the dbt project runs in (public) for the models
        info_schema = connection.execute("select * from information_schema.tables where table_schema = 'public'")\
                                .fetchall()
        assert len([rec for rec in info_schema
                    if rec.table_name in ["combined_model_table", "ext_db_model_table", "int_db_model_table"]
                    and rec.table_type == "BASE TABLE"]) == 3

        int_model = connection.execute("select * from int_db_model_table").fetchall()
        verify_simple_model(int_model, setup.int_table_vals)

        ext_model = connection.execute("select * from ext_db_model_table").fetchall()
        verify_simple_model(ext_model, setup.ext_table_vals)

        comb_model = connection.execute("select * from combined_model_table").fetchall()
        verify_combined_model(comb_model)


def test_dbt_views(dbt_run):  # pylint:disable=redefined-outer-name
    """ Tests the view models generate correctly. """
    engine, setup = dbt_run
    with engine.connect() as connection:
        # look in the schema that the dbt project runs in (public) for the models
        info_schema = connection.execute("select * from information_schema.tables where table_schema = 'public'")\
                                .fetchall()
        assert len([rec for rec in info_schema
                    if rec.table_name in ["combined_model_view", "ext_db_model_view", "int_db_model_view"]
                    and rec.table_type == "VIEW"]) == 3

        int_model = connection.execute("select * from int_db_model_view").fetchall()
        verify_simple_model(int_model, setup.int_table_vals)

        ext_model = connection.execute("select * from ext_db_model_view").fetchall()
        verify_simple_model(ext_model, setup.ext_table_vals)

        comb_model = connection.execute("select * from combined_model_view").fetchall()
        verify_combined_model(comb_model)
