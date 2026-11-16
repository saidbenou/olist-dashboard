import numpy as np
import pandas as pd
from sqlalchemy import text

from etl.db import copy_df, engine, scalar

REGIONS = {
    "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}
ETAT_REGION = {etat: region for region, etats in REGIONS.items() for etat in etats}
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
INCONNU = -1


def read(table: str) -> pd.DataFrame:
    return pd.read_sql(f'SELECT * FROM staging."{table}"', engine)


def zip5(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.zfill(5)


def to_dt(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def date_key(s: pd.Series) -> pd.Series:
    return (s.dt.year * 10000 + s.dt.month * 100 + s.dt.day).astype("Int64")


def keys(values) -> dict:
    return {v: i for i, v in enumerate(values, start=1)}


def build_dim_date() -> pd.DataFrame:
    d = pd.Series(pd.date_range("2016-01-01", "2018-12-31", freq="D"))
    return pd.DataFrame({
        "date_key": date_key(d),
        "date": d.dt.date,
        "jour": d.dt.day,
        "mois": d.dt.month,
        "nom_mois": d.dt.month.map(lambda m: MOIS[m - 1]),
        "annee_mois": d.dt.strftime("%Y-%m"),
        "trimestre": d.dt.quarter,
        "annee": d.dt.year,
        "jour_semaine": d.dt.dayofweek + 1,
        "nom_jour": d.dt.dayofweek.map(lambda j: JOURS[j]),
        "est_weekend": d.dt.dayofweek >= 5,
    })


def build_geo() -> pd.DataFrame:
    geo = read("geolocation")
    geo["lat"] = num(geo["geolocation_lat"])
    geo["lng"] = num(geo["geolocation_lng"])
    geo = geo[geo["lat"].between(-34, 5.5) & geo["lng"].between(-74, -34)]
    geo["code_postal"] = zip5(geo["geolocation_zip_code_prefix"])
    return (geo.groupby("code_postal", as_index=False)
               .agg(latitude=("lat", "mean"), longitude=("lng", "mean"))
               .round({"latitude": 6, "longitude": 6}))


def build_dim_client(customers, orders, geo) -> pd.DataFrame:
    c = customers.merge(orders[["customer_id", "achat"]], on="customer_id", how="left")
    c = c.sort_values("achat").drop_duplicates("customer_unique_id", keep="last")
    c["code_postal"] = zip5(c["customer_zip_code_prefix"])
    c = c.merge(geo, on="code_postal", how="left")
    dim = pd.DataFrame({
        "customer_unique_id": c["customer_unique_id"],
        "code_postal": c["code_postal"],
        "ville": c["customer_city"],
        "etat": c["customer_state"],
        "region": c["customer_state"].map(ETAT_REGION),
        "latitude": c["latitude"],
        "longitude": c["longitude"],
    }).sort_values("customer_unique_id")
    dim.insert(0, "client_key", range(1, len(dim) + 1))
    inconnu = pd.DataFrame([{"client_key": INCONNU, "customer_unique_id": "inconnu"}])
    return pd.concat([inconnu, dim], ignore_index=True)


def build_dim_vendeur(sellers, geo) -> pd.DataFrame:
    s = sellers.copy()
    s["code_postal"] = zip5(s["seller_zip_code_prefix"])
    s = s.merge(geo, on="code_postal", how="left").sort_values("seller_id")
    dim = pd.DataFrame({
        "seller_id": s["seller_id"],
        "code_postal": s["code_postal"],
        "ville": s["seller_city"],
        "etat": s["seller_state"],
        "region": s["seller_state"].map(ETAT_REGION),
        "latitude": s["latitude"],
        "longitude": s["longitude"],
    })
    dim.insert(0, "vendeur_key", range(1, len(dim) + 1))
    inconnu = pd.DataFrame([{"vendeur_key": INCONNU, "seller_id": "inconnu"}])
    return pd.concat([inconnu, dim], ignore_index=True)


def build_dim_produit(products, translation) -> pd.DataFrame:
    p = products.merge(translation, on="product_category_name", how="left").sort_values("product_id")
    dim = pd.DataFrame({
        "product_id": p["product_id"],
        "categorie": p["product_category_name_english"]
                      .fillna(p["product_category_name"]).fillna("unknown"),
        "categorie_pt": p["product_category_name"],
        "poids_g": num(p["product_weight_g"]),
        "volume_cm3": num(p["product_length_cm"]) * num(p["product_height_cm"]) * num(p["product_width_cm"]),
        "nb_photos": num(p["product_photos_qty"]).astype("Int64"),
    })
    dim.insert(0, "produit_key", range(1, len(dim) + 1))
    inconnu = pd.DataFrame([{"produit_key": INCONNU, "product_id": "inconnu", "categorie": "unknown"}])
    return pd.concat([inconnu, dim], ignore_index=True)


def load(df: pd.DataFrame, table: str) -> None:
    copy_df(df, table, "dwh")
    print(f"  dwh.{table:22} {len(df):>9,} lignes")


def main() -> None:
    print("Lecture du staging…")
    orders = read("orders")
    customers = read("customers")
    items = read("order_items")
    payments = read("order_payments")
    reviews = read("order_reviews")
    products = read("products")
    sellers = read("sellers")
    translation = read("product_category_name_translation")

    orders["achat"] = to_dt(orders["order_purchase_timestamp"])
    orders["livraison"] = to_dt(orders["order_delivered_customer_date"])
    orders["estimee"] = to_dt(orders["order_estimated_delivery_date"])

    print("Construction des dimensions…")
    geo = build_geo()
    dim_date = build_dim_date()
    dim_client = build_dim_client(customers, orders, geo)
    dim_vendeur = build_dim_vendeur(sellers, geo)
    dim_produit = build_dim_produit(products, translation)
    statuts = keys(sorted(orders["order_status"].dropna().unique()))
    dim_statut = pd.DataFrame({"statut_key": list(statuts.values()), "statut": list(statuts.keys())})
    types = keys(sorted(payments["payment_type"].dropna().unique()) + ["aucun"])
    dim_paiement = pd.DataFrame({"paiement_key": list(types.values()), "type_paiement": list(types.keys())})

    unique_par_commande = customers.set_index("customer_id")["customer_unique_id"]
    client_par_unique = dim_client.set_index("customer_unique_id")["client_key"]
    orders["client_key"] = (orders["customer_id"].map(unique_par_commande)
                            .map(client_par_unique).fillna(INCONNU).astype(int))
    orders["statut_key"] = orders["order_status"].map(statuts).astype(int)
    orders["date_achat_key"] = date_key(orders["achat"])

    print("Construction des faits…")
    li = items.merge(orders[["order_id", "date_achat_key", "client_key", "statut_key"]],
                     on="order_id", how="left")
    fait_lignes = pd.DataFrame({
        "order_id": li["order_id"],
        "order_item_id": num(li["order_item_id"]).astype(int),
        "date_achat_key": li["date_achat_key"],
        "client_key": li["client_key"].fillna(INCONNU).astype(int),
        "produit_key": li["product_id"].map(dim_produit.set_index("product_id")["produit_key"])
                         .fillna(INCONNU).astype(int),
        "vendeur_key": li["seller_id"].map(dim_vendeur.set_index("seller_id")["vendeur_key"])
                         .fillna(INCONNU).astype(int),
        "statut_key": li["statut_key"].astype(int),
        "prix": num(li["price"]),
        "frais_port": num(li["freight_value"]),
    })

    payments["valeur"] = num(payments["payment_value"])
    payments["versements"] = num(payments["payment_installments"])
    pay = payments.groupby("order_id").agg(montant_paye=("valeur", "sum"),
                                           nb_versements=("versements", "max"))
    principal = (payments.groupby(["order_id", "payment_type"], as_index=False)["valeur"].sum()
                 .sort_values(["order_id", "valeur"])
                 .drop_duplicates("order_id", keep="last")
                 .set_index("order_id")["payment_type"])
    reviews["creation"] = to_dt(reviews["review_creation_date"])
    reviews["reponse"] = to_dt(reviews["review_answer_timestamp"])
    dernier_avis = (reviews.sort_values(["creation", "reponse"])
                    .drop_duplicates("order_id", keep="last")
                    .set_index("order_id")["review_score"])
    nb_articles = items.groupby("order_id").size()

    o = orders
    retard = (o["livraison"].dt.normalize() - o["estimee"].dt.normalize()).dt.days
    fait_commandes = pd.DataFrame({
        "order_id": o["order_id"],
        "date_achat_key": o["date_achat_key"],
        "date_livraison_key": date_key(o["livraison"]),
        "client_key": o["client_key"],
        "statut_key": o["statut_key"],
        "paiement_key": o["order_id"].map(principal).fillna("aucun").map(types).astype(int),
        "montant_paye": o["order_id"].map(pay["montant_paye"]).round(2),
        "nb_articles": o["order_id"].map(nb_articles).fillna(0).astype(int),
        "nb_versements": o["order_id"].map(pay["nb_versements"]).astype("Int64"),
        "delai_livraison_jours": ((o["livraison"] - o["achat"]).dt.total_seconds() / 86400).round(1),
        "retard_jours": retard.astype("Int64"),
        "est_en_retard": pd.Series(np.where(retard.isna(), None, retard > 0), dtype="object"),
        "note_avis": num(o["order_id"].map(dernier_avis)).astype("Int64"),
    })

    print("Chargement dans dwh…")
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE dwh.fait_lignes_commande, dwh.fait_commandes, dwh.dim_date, dwh.dim_client, "
            "dwh.dim_vendeur, dwh.dim_produit, dwh.dim_statut, dwh.dim_paiement"))
    for df, table in [(dim_date, "dim_date"), (dim_client, "dim_client"),
                      (dim_vendeur, "dim_vendeur"), (dim_produit, "dim_produit"),
                      (dim_statut, "dim_statut"), (dim_paiement, "dim_paiement"),
                      (fait_lignes, "fait_lignes_commande"), (fait_commandes, "fait_commandes")]:
        load(df, table)

    controles()


def controles() -> None:
    print("\nContrôles :")
    checks = {
        "Somme des prix identique (staging = dwh)":
            ("SELECT ROUND(SUM(price::numeric), 2) FROM staging.order_items",
             "SELECT ROUND(SUM(prix), 2) FROM dwh.fait_lignes_commande"),
        "Somme des paiements identique (staging = dwh)":
            ("SELECT ROUND(SUM(payment_value::numeric), 2) FROM staging.order_payments",
             "SELECT ROUND(SUM(montant_paye), 2) FROM dwh.fait_commandes"),
        "Même nombre d'articles (staging = dwh)":
            ("SELECT COUNT(*) FROM staging.order_items",
             "SELECT COUNT(*) FROM dwh.fait_lignes_commande"),
        "Même nombre de commandes (staging = dwh)":
            ("SELECT COUNT(*) FROM staging.orders",
             "SELECT COUNT(*) FROM dwh.fait_commandes"),
        "Une seule ligne par commande dans fait_commandes":
            ("SELECT COUNT(*) FROM dwh.fait_commandes",
             "SELECT COUNT(DISTINCT order_id) FROM dwh.fait_commandes"),
        "Un client par customer_unique_id":
            ("SELECT COUNT(DISTINCT customer_unique_id) FROM staging.customers",
             f"SELECT COUNT(*) FROM dwh.dim_client WHERE client_key <> {INCONNU}"),
    }
    echecs = 0
    for nom, (q_attendu, q_obtenu) in checks.items():
        attendu, obtenu = scalar(q_attendu), scalar(q_obtenu)
        ok = attendu == obtenu
        echecs += not ok
        print(f"  {'OK   ' if ok else 'ÉCHEC'} {nom} : {obtenu} (attendu {attendu})")

    inconnus = {
        "articles sans produit": f"SELECT COUNT(*) FROM dwh.fait_lignes_commande WHERE produit_key = {INCONNU}",
        "articles sans vendeur": f"SELECT COUNT(*) FROM dwh.fait_lignes_commande WHERE vendeur_key = {INCONNU}",
        "commandes sans client": f"SELECT COUNT(*) FROM dwh.fait_commandes WHERE client_key = {INCONNU}",
    }
    for nom, q in inconnus.items():
        n = scalar(q)
        print(f"  {'OK   ' if n == 0 else 'INFO '} {nom} : {n}")

    print(f"\n{'OK – modèle en étoile chargé et contrôlé.' if not echecs else f'ÉCHEC – {echecs} contrôle(s) en erreur.'}")
    if echecs:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
