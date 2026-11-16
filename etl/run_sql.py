import sys

from etl.db import run_sql_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python -m etl.run_sql <fichier.sql>")
    run_sql_file(sys.argv[1])
    print(f"OK – {sys.argv[1]} exécuté.")
