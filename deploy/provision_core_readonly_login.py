"""Create and verify the local SAP_MIRROR API login.

This script operates only on the Core-hosted mirror. It never opens a
connection to SAP production.
"""

import os
import re

import pytds


LOGIN = "foxbrain_core_api"
DATABASE = "SAP_MIRROR"


def literal(value):
    return "N'{}'".format(value.replace("'", "''"))


def connect(database, user, password):
    return pytds.connect(
        server="127.0.0.1", port=11433, database=database,
        user=user, password=password, timeout=20,
    )


def main():
    sa_password = os.environ["TARGET_SA_PASSWORD"]
    api_password = os.environ["CORE_DB_PASSWORD"]
    if not re.fullmatch(r"[A-Za-z0-9]{32,128}", api_password):
        raise RuntimeError("CORE_DB_PASSWORD must be a strong alphanumeric secret")

    master = connect("master", "sa", sa_password)
    cursor = master.cursor()
    cursor.execute(
        "if not exists(select 1 from sys.server_principals where name=%s) "
        "exec('create login [foxbrain_core_api] with password=' + %s + ', check_policy=on')",
        (LOGIN, literal(api_password)),
    )
    cursor.execute(
        "exec('alter login [foxbrain_core_api] with password=' + %s + ', check_policy=on')",
        (literal(api_password),),
    )
    cursor.execute("alter login [foxbrain_core_api] with default_database=[SAP_MIRROR]")
    master.commit()
    master.close()

    mirror = connect(DATABASE, "sa", sa_password)
    cursor = mirror.cursor()
    cursor.execute(
        "if not exists(select 1 from sys.database_principals where name=%s) "
        "create user [foxbrain_core_api] for login [foxbrain_core_api]",
        (LOGIN,),
    )
    cursor.execute("alter role [db_datareader] add member [foxbrain_core_api]")
    cursor.execute("revoke control to [foxbrain_core_api]")
    cursor.execute("grant connect to [foxbrain_core_api]")
    for permission in ("INSERT", "UPDATE", "DELETE", "ALTER", "CREATE TABLE", "CREATE VIEW", "CREATE PROCEDURE"):
        cursor.execute("deny {} to [foxbrain_core_api]".format(permission))
    mirror.commit()
    mirror.close()

    readonly = connect(DATABASE, LOGIN, api_password)
    cursor = readonly.cursor()
    cursor.execute("select top 1 name from sys.tables order by name")
    cursor.fetchone()
    checks = {
        "insert": "insert into dbo.OITM (ItemCode) select ItemCode from dbo.OITM where 1=0",
        "update": "update dbo.OITM set ItemCode=ItemCode where 1=0",
        "delete": "delete from dbo.OITM where 1=0",
        "ddl": "create table dbo.__foxbrain_readonly_probe(id int)",
    }
    failed = []
    for name, statement in checks.items():
        try:
            cursor.execute(statement)
            readonly.rollback()
            failed.append(name)
        except Exception:
            readonly.rollback()
    readonly.close()
    if failed:
        raise RuntimeError("read-only verification failed: {} was allowed".format(",".join(failed)))
    print("SELECT=allowed INSERT=denied UPDATE=denied DELETE=denied DDL=denied")


if __name__ == "__main__":
    main()
