## dbt-snowshu-postgres

The `dbt-snowshu-postgres` package provides cross-database query support for dbt projects that are tested against snowshu postgres replicas. In the case that no cross-database support is needed for a snowshu replica, the default dbt postgres adapter can be used.

### Example dbt query

If a snowshu postgres replica needs to support a cross-database query, installing this adapter and setting
`type: snowshupostgres` in the `profiles.yml` will adjust the relation's database and schema appropriately
to utilize the foreign data wrappers that snowshu creates.

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

## Adapter Development

A `docker-compose` file is included for easier development. Running the following
will bring up an empty db container as well as give you a shell in the container
that has `dbt-snowshu-postgres` installed.

``` docker-compose run snowshupostgres ```

There is also a test script that will run both `pytest` and `prospector` and display the output.

``` docker-compose run snowshupostgres test ```

Any other specific commands can be issued to the container as normal

``` docker-compose run snowshupostgres <command_and_args> ```

Note that any changes to the `dbt-snowshu-postgres` package will require a rebuild to take effect
since that package is installed during the `docker build` step currently.