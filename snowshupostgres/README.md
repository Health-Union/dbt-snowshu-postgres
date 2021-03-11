
## dbt-snowshu-postgres

The `dbt-snowshu-postgres` package provides cross-database query support for dbt projects that are tested against snowshu postgres replicas. In the case that no cross-database support is needed for a snowshu replica, the default dbt postgres adapter can be used.

### Example Use Case

Suppose the following query needs to run in a production Snowflake instance

```
SELECT *
FROM customers_db.company1.users as u
INNER JOIN orders_db.company1.service_orders as o
    ON u.id = o.issuing_customer_id
```

If this is rewritten using dbt, we would have the following:

```
{% set users_relation = adapter.get_relation(database="customers_db",
                                             schema="company1",
                                             identifier="users") %}
{% set service_orders_relation = adapter.get_relation(database="orders_db",
                                                      schema="company1",
                                                      identifier="service_orders") %}

SELECT *
FROM {{ users_relation }} as u
INNER JOIN {{ service_orders_relation }} as o
    ON u.id = o.issuing_customer_id
```

But we want to test and develop against a subset of the data preferably out of 
the Snowflake cluster to avoid incurring extra compute costs.

Snowshu can create that sampled testing database in a local Postgres DB, but there is no
way to run the exact same query in it, as it doesn't support cross-database queries.
The foreign data wrappers that postgres provides are setup by snowshu, but they
don't support the exact same `database.schema.table` syntax.

If we use the dbt version of the query along with the `dbt-snowshu-postgres` package,
the query can be executed against a snowshu postgres replica with the same results
as if it was executed against a snowflake instance.

To do this, we would configure the `profiles.yml` file the same as we would for
a normal [postgres profile](https://docs.getdbt.com/reference/warehouse-profiles/postgres-profile),
but change the `type` value from `postgres` to `snowshupostgres`.

A simple example would be
```
default:
  outputs:

    dev:
      type: snowshupostgres
      threads: 1
      host: postgres-container
      port: 5432
      user: postgres
      pass: postgres
      dbname: postgres
      schema: public

  target: dev
```

Combining the `snowshupostgres` type and dbt's `adapter.get_relation` function makes use of
the foreign data wrappers that snowshu sets up by adjusting the `database` and `schema`
values accordingly when the requested relation has a different `database` value than
the connection does.

In our example, if we are issuing the dbt query while connected to the `customers_db`,
the final sql that is run would look like the following where the 
`customers_db.orders_db__company1.service_orders` is a linked foreign table that actually
resides at `orders_db.company1.service_orders`

```
SELECT *
FROM customers_db.company1.users as u
INNER JOIN customers_db.orders_db__company1.service_orders as o
    ON u.id = o.issuing_customer_id
```

If the column list needs to be retrieved using dbt, the expected column names and types
will be returned from the `adapter.get_columns_in_relation` function and can be used as 
normal column objects.

```
{% set column_set = adapter.get_columns_in_relation(service_orders_relation) %}
```

So now you can test your cross-database queries locally against appropriately 
sampled data instead of developing in the cloud or against full production datasets!

