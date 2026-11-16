import io
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

REQUIRED = ["PG_USER", "PG_PASSWORD", "PG_HOST", "PG_PORT", "PG_DB"]
missing = [v for v in REQUIRED if not os.getenv(v)]
if missing:
    raise SystemExit(f"Variables manquantes dans .env : {', '.join(missing)}")

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
)


def run_sql_file(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.execute(sql)
        raw.commit()
    finally:
        raw.close()


def copy_df(df: pd.DataFrame, table: str, schema: str) -> None:
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)
    cols = ", ".join(f'"{c}"' for c in df.columns)
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            cur.copy_expert(
                f'COPY {schema}."{table}" ({cols}) FROM STDIN WITH (FORMAT csv, NULL \'\')', buffer
            )
        raw.commit()
    finally:
        raw.close()


def scalar(query: str):
    with engine.connect() as conn:
        return conn.execute(text(query)).scalar()
