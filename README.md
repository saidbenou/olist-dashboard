# Olist E-commerce Dashboard · PostgreSQL, Star Schema and Power BI

I built this end-to-end project for my Data Analyst / BI portfolio. It starts from a raw dataset of 1.5 million rows and ends with a 5-page Power BI dashboard. In between: a PostgreSQL data warehouse modelled as a star schema, loaded by a Python ETL, with every KPI checked in SQL.

**My analysis reports:** [🇬🇧 English](docs/analysis_report_en.md) · [🇫🇷 Français](docs/rapport_analyse_fr.md)

![Dashboard overview](docs/images/01_vue_ensemble.png)

## Key findings

| | |
|---|---|
| **R$ 13.59 M** product revenue · **99,441** orders · **96,096** customers | **+137%** revenue (January–August 2018 vs 2017) |
| Review score **4.29/5** on time vs **2.27/5** when late | Average delivery **10.8 days** in the Southeast vs **22.6 days** in the North |
| **20%** of sellers make **83%** of revenue | Only **3.1%** repeat customers |

## Architecture

```
data/raw/*.csv ──► staging (raw copy) ──► Python ETL ──► dwh (star schema) ──► Power BI
   9 files         load_staging.py        transform_load.py    8 tables         34 DAX measures
                                                 │
                                  automated checks + SQL reference values
```

**Stack:** Python 3.10+ (pandas, SQLAlchemy, psycopg2) · PostgreSQL 17 · Power BI Desktop (DAX, Power Query)

## My modelling choices

![Power BI model](docs/images/modele_power_bi.png)

| Table | Grain | Content |
|---|---|---|
| `fait_lignes_commande` | 1 item (112,650 rows) | price, shipping fee |
| `fait_commandes` | 1 order (99,441 rows) | amount paid, delivery time, lateness, review score, payment type |
| `dim_date` | 1 day | 2016–2018 calendar |
| `dim_client` | 1 real customer | `customer_unique_id`, city, state, region, coordinates |
| `dim_vendeur` | 1 seller | city, state, region, coordinates |
| `dim_produit` | 1 product | category (English and Portuguese), weight, photos |
| `dim_statut` | 1 status | delivered, shipped, canceled… |
| `dim_paiement` | 1 type | credit_card, boleto, voucher, debit_card |

Table and column names are in French (*fait* = fact, *commande* = order, *client* = customer, *vendeur* = seller, *produit* = product).

- **I identify customers by `customer_unique_id`.** In the Olist data, `customer_id` changes with every order: using it would have hidden all repeat customers.
- **I split the data into two fact tables at different grains.** Payments and reviews belong to an order. Joining them at item grain would have duplicated amounts, so I aggregate them at order grain.
- **I use integer surrogate keys**, with an "unknown" member (key `-1`) in every dimension, so no fact row is lost.
- **Delivery date is an inactive relationship**, which I activate in DAX with `USERELATIONSHIP` when analysing by delivery date.
- **I use `TREATAS`** so that product and seller filters also apply to review score and lateness, which are measured at order grain.

## The dashboard (5 pages)

| Page | Question it answers | Preview |
|---|---|---|
| Vue d'ensemble (Overview) | How much do we sell, and how is it changing? | [screenshot](docs/images/01_vue_ensemble.png) |
| Produits (Products) | Which categories drive revenue? | [screenshot](docs/images/02_produits.png) |
| Logistique (Logistics) | Where and when are deliveries late? | [screenshot](docs/images/03_logistique.png) |
| Satisfaction | What lowers the review score? | [screenshot](docs/images/04_satisfaction.png) |
| Vendeurs et clients (Sellers and customers) | Who sells, who buys, and where? | [screenshot](docs/images/05_vendeurs_clients.png) |

## How I checked the numbers

- [`docs/rapport_qualite.md`](docs/rapport_qualite.md): before any transformation, I profiled the raw data (missing values, duplicates, inconsistencies).
- `etl/transform_load.py` compares staging and warehouse after every load: total prices and payments, item and order counts, uniqueness of orders and customers.
- [`docs/valeurs_reference.md`](docs/valeurs_reference.md): for every KPI, I computed the expected value in SQL. Each DAX measure must display exactly the same value.

![staging vs dwh checks in pgAdmin](docs/images/pg_04_controles.png)

The other PostgreSQL screenshots (schemas, ERD, row counts, analysis queries) are in my [analysis report](docs/analysis_report_en.md#checks-in-postgresql).

## Repository structure

```
olist-dashboard/
├── data/raw/                  # 9 Kaggle CSV files (not versioned)
├── etl/
│   ├── db.py                  # PostgreSQL connection (reads .env) and COPY loading
│   ├── test_connexion.py      # connection test
│   ├── check_raw.py           # CSV presence and row counts
│   ├── explore_raw.py         # raw data quality report
│   ├── load_staging.py        # CSV files into the staging schema
│   ├── run_sql.py             # runs a SQL file
│   ├── transform_load.py      # staging to dwh ETL, with checks
│   └── verify.py              # KPI reference values
├── sql/
│   ├── 00_create_schemas.sql
│   ├── 01_create_dwh.sql      # star schema (tables, keys, indexes)
│   └── 02_verifications.sql   # one check query per KPI
├── powerbi/
│   └── olist_dashboard.pbix   # the dashboard
├── docs/
│   ├── analysis_report_en.md  # analysis report (English)
│   ├── rapport_analyse_fr.md  # analysis report (French)
│   ├── installation.md        # step-by-step setup (French)
│   ├── mesures_dax.md         # the 34 DAX measures
│   ├── rapport_qualite.md     # raw data quality
│   ├── valeurs_reference.md   # SQL reference values
│   └── images/                # dashboard and PostgreSQL screenshots
├── .env.example               # credentials file template
└── requirements.txt
```

## Run it yourself

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env        # then fill in your PostgreSQL password

python -m etl.test_connexion
python -m etl.check_raw
python -m etl.load_staging
python -m etl.run_sql sql/01_create_dwh.sql
python -m etl.transform_load
python -m etl.verify
```

Then open `powerbi/olist_dashboard.pbix` and refresh. Every step and its checks are detailed in [`docs/installation.md`](docs/installation.md).

## Data

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), licensed CC BY-NC-SA 4.0. The files are not included in this repository.

## Author

**Said Ben Oukhanchouch** · Data Analyst / BI

- Email: benoukhanchouch.said@gmail.com
- GitHub: [@Saidbenou](https://github.com/Saidbenou)
- LinkedIn: [Said Ben Oukhanchouch](https://www.linkedin.com/in/said-ben-oukhanchouch-aa91bb205/)

Feel free to reach out to discuss this project.
