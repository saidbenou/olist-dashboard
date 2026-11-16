from etl.db import engine, run_sql_file, scalar
from sqlalchemy import text

if __name__ == "__main__":
    print("Version :", scalar("SELECT version()").split(",")[0])
    print("Base    :", scalar("SELECT current_database()"))
    run_sql_file("sql/00_create_schemas.sql")
    with engine.connect() as conn:
        schemas = [r[0] for r in conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name IN ('staging','dwh') ORDER BY 1"))]
    print("Schémas :", ", ".join(schemas))
    if schemas != ["dwh", "staging"]:
        raise SystemExit("ÉCHEC : les schémas staging et dwh n'existent pas.")
    print("\nOK – connexion réussie, schémas prêts.")
