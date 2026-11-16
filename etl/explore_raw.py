import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_RAW = RACINE / "data" / "raw"
RAPPORT = RACINE / "docs" / "rapport_qualite.md"

FICHIERS = {
    "customers": ("olist_customers_dataset.csv", ["customer_id"]),
    "geolocation": ("olist_geolocation_dataset.csv", None),
    "orders": ("olist_orders_dataset.csv", ["order_id"]),
    "order_items": ("olist_order_items_dataset.csv", ["order_id", "order_item_id"]),
    "order_payments": ("olist_order_payments_dataset.csv", ["order_id", "payment_sequential"]),
    "order_reviews": ("olist_order_reviews_dataset.csv", ["review_id", "order_id"]),
    "products": ("olist_products_dataset.csv", ["product_id"]),
    "sellers": ("olist_sellers_dataset.csv", ["seller_id"]),
    "category_translation": ("product_category_name_translation.csv", ["product_category_name"]),
}

DATES_ORDERS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def charger():
    tables = {}
    for nom, (fichier, _) in FICHIERS.items():
        chemin = DOSSIER_RAW / fichier
        if not chemin.exists():
            raise FileNotFoundError(f"Fichier manquant : {chemin}")
        tables[nom] = pd.read_csv(chemin, dtype={c: str for c in (
            "customer_zip_code_prefix", "seller_zip_code_prefix", "geolocation_zip_code_prefix")})
    tables["orders"][DATES_ORDERS] = tables["orders"][DATES_ORDERS].apply(pd.to_datetime)
    return tables


def tableau_md(df, index=False):
    if index:
        df = df.reset_index()
    entetes = [str(c) for c in df.columns]
    lignes = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for ligne in df.itertuples(index=False):
        lignes.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in ligne) + " |")
    return "\n".join(lignes)


def pct(n, total):
    return f"{n:,} ({n / total:.2%})" if total else "0"


def section_profil(nom, df, cle):
    out = [f"### {nom}", "", f"- Lignes : **{len(df):,}** — colonnes : **{df.shape[1]}**"]
    if cle:
        nb_dup = df.duplicated(subset=cle).sum()
        out.append(f"- Doublons sur la clé naturelle `{', '.join(cle)}` : **{nb_dup:,}**")
    else:
        out.append("- Pas de clé naturelle (table de référence géographique)")
    out.append(f"- Lignes entièrement dupliquées : **{df.duplicated().sum():,}**")
    profil = pd.DataFrame({
        "colonne": df.columns,
        "type": df.dtypes.astype(str).values,
        "manquants": df.isna().sum().values,
    })
    profil["% manquants"] = (profil["manquants"] / len(df) * 100).round(2)
    out += ["", tableau_md(profil), ""]
    return out


def orphelins(enfant, col_enfant, parent, col_parent):
    valeurs = enfant[col_enfant].dropna()
    return int((~valeurs.isin(parent[col_parent])).sum())


def section_coherence(t):
    controles = [
        ("Commandes sans client", t["orders"], "customer_id", t["customers"], "customer_id"),
        ("Articles sans commande", t["order_items"], "order_id", t["orders"], "order_id"),
        ("Articles sans produit", t["order_items"], "product_id", t["products"], "product_id"),
        ("Articles sans vendeur", t["order_items"], "seller_id", t["sellers"], "seller_id"),
        ("Paiements sans commande", t["order_payments"], "order_id", t["orders"], "order_id"),
        ("Avis sans commande", t["order_reviews"], "order_id", t["orders"], "order_id"),
        ("Catégories produit sans traduction", t["products"], "product_category_name",
         t["category_translation"], "product_category_name"),
        ("Codes postaux clients absents de la géolocalisation", t["customers"],
         "customer_zip_code_prefix", t["geolocation"], "geolocation_zip_code_prefix"),
        ("Codes postaux vendeurs absents de la géolocalisation", t["sellers"],
         "seller_zip_code_prefix", t["geolocation"], "geolocation_zip_code_prefix"),
    ]
    lignes = [(lib, orphelins(e, ce, p, cp), len(e)) for lib, e, ce, p, cp in controles]

    o = t["orders"]["order_id"]
    for lib, table in [("Commandes sans article", "order_items"),
                       ("Commandes sans paiement", "order_payments"),
                       ("Commandes sans avis", "order_reviews")]:
        lignes.append((lib, int((~o.isin(t[table]["order_id"])).sum()), len(o)))

    df = pd.DataFrame(lignes, columns=["contrôle", "lignes orphelines", "lignes testées"])
    df["%"] = (df["lignes orphelines"] / df["lignes testées"] * 100).round(2)
    cats = sorted(set(t["products"]["product_category_name"].dropna())
                  - set(t["category_translation"]["product_category_name"]))
    out = ["## 2. Cohérence des clés entre tables", "", tableau_md(df), ""]
    if cats:
        out.append(f"Catégories sans traduction : {', '.join(f'`{c}`' for c in cats)}")
        out.append("")
    return out, df


def section_points_connus(t):
    c, o, r, g, p = (t["customers"], t["orders"], t["order_reviews"],
                     t["geolocation"], t["products"])
    out = ["## 3. Points connus", ""]

    nb_id = c.groupby("customer_unique_id")["customer_id"].nunique()
    multi = int((nb_id > 1).sum())
    out += ["### 3.1 Plusieurs customer_id pour un même customer_unique_id", "",
            f"- customer_id : **{c['customer_id'].nunique():,}** — customer_unique_id : "
            f"**{c['customer_unique_id'].nunique():,}**",
            f"- Clients réels avec plusieurs customer_id : **{pct(multi, len(nb_id))}**",
            f"- Maximum de customer_id pour un client : **{nb_id.max()}**", ""]
    loc = c.groupby("customer_unique_id")[["customer_zip_code_prefix", "customer_city",
                                           "customer_state"]].nunique()
    chgt = int((loc.max(axis=1) > 1).sum())
    out += [f"- Clients réels avec plusieurs adresses (code postal, ville ou état différents) : "
            f"**{chgt:,}**", ""]

    nb_avis = r.groupby("order_id")["review_id"].nunique()
    out += ["### 3.2 Plusieurs avis par commande", "",
            f"- Commandes avec plusieurs avis : **{pct(int((nb_avis > 1).sum()), len(nb_avis))}**",
            f"- review_id utilisés sur plusieurs commandes : "
            f"**{int((r.groupby('review_id')['order_id'].nunique() > 1).sum()):,}**", ""]

    nb_pts = g.groupby("geolocation_zip_code_prefix").size()
    hors_bresil = g[~g["geolocation_lat"].between(-34, 6) | ~g["geolocation_lng"].between(-74, -34)]
    etats = g.groupby("geolocation_zip_code_prefix")["geolocation_state"].nunique()
    out += ["### 3.3 Doublons de géolocalisation par préfixe de code postal", "",
            f"- Lignes : **{len(g):,}** — préfixes distincts : **{len(nb_pts):,}**",
            f"- Lignes entièrement dupliquées : **{pct(int(g.duplicated().sum()), len(g))}**",
            f"- Points par préfixe : médiane **{nb_pts.median():.0f}**, maximum **{nb_pts.max():,}**",
            f"- Préfixes rattachés à plusieurs états : **{int((etats > 1).sum()):,}**",
            f"- Coordonnées hors du Brésil : **{len(hors_bresil):,}**",
            f"- Orthographes de ville distinctes : **{g['geolocation_city'].nunique():,}** "
            "(accents et casse non homogènes)", ""]

    sans_cat = p["product_category_name"].isna()
    dims = ["product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]
    out += ["### 3.4 Produits sans catégorie", "",
            f"- Produits sans catégorie : **{pct(int(sans_cat.sum()), len(p))}**",
            f"- Produits sans poids ou dimensions : **{int(p[dims].isna().any(axis=1).sum()):,}**",
            f"- Produits de poids 0 g : **{int((p['product_weight_g'] == 0).sum()):,}**", ""]
    articles_sans_cat = t["order_items"]["product_id"].isin(p.loc[sans_cat, "product_id"])
    out += [f"- Articles vendus dont le produit n'a pas de catégorie : "
            f"**{pct(int(articles_sans_cat.sum()), len(t['order_items']))}**", ""]

    mois = (o.assign(mois=o["order_purchase_timestamp"].dt.to_period("M").astype(str))
            .groupby("mois").size().rename("commandes").to_frame())
    out += ["### 3.5 Distribution des commandes par mois", "",
            f"- Période couverte : **{o['order_purchase_timestamp'].min():%Y-%m-%d}** au "
            f"**{o['order_purchase_timestamp'].max():%Y-%m-%d}**", "",
            tableau_md(mois, index=True), ""]

    statuts = o["order_status"].value_counts().rename("commandes").to_frame()
    livre = o["order_status"] == "delivered"
    incoh = {
        "Livrées sans date de livraison client":
            int((livre & o["order_delivered_customer_date"].isna()).sum()),
        "Non livrées avec date de livraison client":
            int((~livre & o["order_delivered_customer_date"].notna()).sum()),
        "Livraison client avant l'achat":
            int((o["order_delivered_customer_date"] < o["order_purchase_timestamp"]).sum()),
        "Remise au transporteur avant l'achat":
            int((o["order_delivered_carrier_date"] < o["order_purchase_timestamp"]).sum()),
        "Approbation avant l'achat":
            int((o["order_approved_at"] < o["order_purchase_timestamp"]).sum()),
    }
    out += ["### 3.6 Statuts et cohérence des dates de commande", "",
            tableau_md(statuts, index=True), "",
            tableau_md(pd.DataFrame(list(incoh.items()), columns=["contrôle", "commandes"])), ""]

    pay = t["order_payments"]
    out += ["### 3.7 Paiements", "",
            f"- Paiements de montant 0 : **{int((pay['payment_value'] == 0).sum()):,}**",
            f"- Paiements de type `not_defined` : "
            f"**{int((pay['payment_type'] == 'not_defined').sum()):,}**",
            f"- Paiements avec 0 versement : **{int((pay['payment_installments'] == 0).sum()):,}**",
            f"- Commandes payées avec plusieurs moyens de paiement : "
            f"**{int((pay.groupby('order_id')['payment_type'].nunique() > 1).sum()):,}**", ""]
    total_items = (t["order_items"].assign(total=lambda d: d["price"] + d["freight_value"])
                   .groupby("order_id")["total"].sum())
    total_pay = pay.groupby("order_id")["payment_value"].sum()
    ecart = (total_pay - total_items).dropna().abs()
    out += [f"- Commandes où paiements ≠ prix + port (écart > 1 R$) : "
            f"**{pct(int((ecart > 1).sum()), len(ecart))}**", ""]
    return out


def main():
    t = charger()
    rapport = ["# Rapport qualité des données brutes Olist", "",
               f"Généré par `python -m etl.explore_raw` à partir de `data/raw/` "
               f"({len(t)} fichiers).", "", "## 1. Profil des tables", ""]
    for nom, (_, cle) in FICHIERS.items():
        rapport += section_profil(nom, t[nom], cle)
    lignes_coherence, df_coherence = section_coherence(t)
    rapport += lignes_coherence
    rapport += section_points_connus(t)

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(rapport), encoding="utf-8")

    print("Résumé de l'exploration")
    for nom, df in t.items():
        print(f"  {nom:<22} {len(df):>10,} lignes  {df.shape[1]:>3} colonnes")
    print(f"  Contrôles de cohérence en anomalie : "
          f"{int((df_coherence['lignes orphelines'] > 0).sum())}/{len(df_coherence)}")
    print(f"Rapport écrit : {RAPPORT.relative_to(RACINE)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        sys.exit(1)
