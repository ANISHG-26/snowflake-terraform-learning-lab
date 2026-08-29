"""Run a read-only Snowflake session identity check.

Credentials are read from environment variables so they are never stored in
the repository. This script does not create or modify Snowflake objects.
"""

import os
import sys

import snowflake.connector
from dotenv import load_dotenv


IDENTITY_QUERY = """
SELECT
  CURRENT_ORGANIZATION_NAME() AS organization_name,
  CURRENT_ACCOUNT_NAME()      AS account_name,
  CURRENT_USER()              AS user_name,
  CURRENT_ROLE()              AS active_role,
  CURRENT_WAREHOUSE()         AS active_warehouse,
  CURRENT_DATABASE()          AS active_database,
  CURRENT_SCHEMA()            AS active_schema;
"""


def required_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    load_dotenv()
    try:
        connection_options = {
            "user": required_setting("SNOWFLAKE_USER"),
            "password": required_setting("SNOWFLAKE_PASSWORD"),
            "account": required_setting("SNOWFLAKE_ACCOUNT"),
        }

        # These are optional connection context settings.
        for setting, variable in (
            ("warehouse", "SNOWFLAKE_WAREHOUSE"),
            ("database", "SNOWFLAKE_DATABASE"),
            ("schema", "SNOWFLAKE_SCHEMA"),
            ("role", "SNOWFLAKE_ROLE"),
        ):
            value = os.getenv(variable)
            if value:
                connection_options[setting] = value

        with snowflake.connector.connect(**connection_options) as connection:
            with connection.cursor() as cursor:
                cursor.execute(IDENTITY_QUERY)
                columns = [description[0] for description in cursor.description]
                row = cursor.fetchone()

        print("Read-only Snowflake identity result:")
        for column, value in zip(columns, row):
            print(f"{column}: {value}")
        return 0
    except (ValueError, snowflake.connector.errors.Error) as error:
        print(f"Connection check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
