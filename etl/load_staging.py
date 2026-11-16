from pathlib import Path

import pandas as pd
from sqlalchemy import text

from etl.db import copy_df, engine, scalar

RAW = Path("data/raw")


def table_name(file: Path) -> str:
    return file.stem.replace("olist_", "").replace("_dataset", "")


if __name__ == "__main__":
    files = sorted(RAW.glob("*.csv"))
    if len(files) != 9:
        raise SystemExit(f"ÉCHEC : 9 CSV attendus dans data/raw/, {len(files)} trouvés.")
    errors = 0
    for file in files:
        table = table_name(file)
        df = pd.read_csv(file, dtype=str, encoding="utf-8-sig", keep_default_na=False)
        df = df.replace("", None)
        cols = ", ".join(f'"{c}" TEXT' for c in df.columns)
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS staging."{table}"'))
            conn.execute(text(f'CREATE TABLE staging."{table}" ({cols})'))
        copy_df(df, table, "staging")
        n_db = scalar(f'SELECT COUNT(*) FROM staging."{table}"')
        flag = "OK  " if n_db == len(df) else "ÉCHEC"
        errors += n_db != len(df)
        print(f"{flag} staging.{table:32} CSV {len(df):>10,} | base {n_db:>10,}")
    if errors:
        raise SystemExit("\nÉCHEC : des lignes ont été perdues au chargement.")
    print("\nOK – staging chargé.")
