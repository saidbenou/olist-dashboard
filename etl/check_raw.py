from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
EXPECTED = {
    "olist_customers_dataset.csv": 99_441,
    "olist_geolocation_dataset.csv": 1_000_163,
    "olist_order_items_dataset.csv": 112_650,
    "olist_order_payments_dataset.csv": 103_886,
    "olist_order_reviews_dataset.csv": 99_224,
    "olist_orders_dataset.csv": 99_441,
    "olist_products_dataset.csv": 32_951,
    "olist_sellers_dataset.csv": 3_095,
    "product_category_name_translation.csv": 71,
}

if __name__ == "__main__":
    errors = 0
    for name, expected in EXPECTED.items():
        path = RAW / name
        if not path.exists():
            print(f"MANQUANT  {name}")
            errors += 1
            continue
        n = len(pd.read_csv(path, encoding="utf-8-sig"))
        flag = "OK  " if n == expected else "ATTENTION"
        print(f"{flag}  {name:42} {n:>10,} lignes (attendu ≈ {expected:,})")
    if errors:
        raise SystemExit(f"\nÉCHEC : {errors} fichier(s) manquant(s) dans data/raw/.")
    print("\nOK – les 9 fichiers sont présents.")
