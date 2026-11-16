# Reproduire le projet

Retour au [README](../README.md).

Toutes les commandes se lancent depuis la racine du projet, avec l'environnement virtuel activé. Chaque étape se termine par une **✅ vérification**.

Prérequis : Windows, Python 3.10 ou plus, PostgreSQL 17 avec pgAdmin, Power BI Desktop.

## 1. Environnement Python

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

✅ `python -c "import pandas, sqlalchemy, psycopg2, dotenv, tabulate; print('OK')"` affiche `OK`.

> Si PowerShell bloque l'activation : `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
> Si `pip.exe` est bloqué par Windows (Smart App Control), utilisez toujours `python -m pip`.

## 2. Base de données et identifiants

1. Dans pgAdmin, créez une base nommée `olist`.
2. Copiez `.env.example` en `.env` et renseignez votre mot de passe PostgreSQL. Le fichier `.env` n'est jamais versionné.

```powershell
copy .env.example .env
python -m etl.test_connexion
```

✅ Le script affiche la version de PostgreSQL, `Base : olist`, `Schémas : dwh, staging` et `OK`.

En cas d'erreur :
- `password authentication failed` ou `UnicodeDecodeError` : mot de passe incorrect ou base inexistante. Sur un Windows en français, PostgreSQL renvoie ses messages dans un encodage que Python ne sait pas décoder, d'où cette erreur trompeuse.
- `Connection refused` : le service **postgresql-x64-17** est arrêté (`services.msc`).

## 3. Données brutes

Téléchargez le [dataset Olist sur Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) et placez les 9 CSV directement dans `data/raw/`.

```powershell
python -m etl.check_raw
```

✅ 9 lignes `OK`, puis `OK – les 9 fichiers sont présents.`

## 4. Pipeline complet

```powershell
python -m etl.load_staging                  # CSV vers staging, tout en texte
python -m etl.run_sql sql/01_create_dwh.sql # tables, clés étrangères et index du modèle en étoile
python -m etl.transform_load                # ETL staging vers dwh, puis contrôles
python -m etl.verify                        # valeurs de référence des KPI
```

`transform_load` prend une à deux minutes : la table de géolocalisation compte un million de lignes.

✅ `transform_load` se termine par `OK – modèle en étoile chargé et contrôlé.` après 6 contrôles :

| Contrôle | Ce qu'il garantit |
|---|---|
| Somme des prix staging = dwh | aucun montant perdu ou dupliqué |
| Somme des paiements staging = dwh | agrégation des paiements correcte |
| Même nombre d'articles | aucune ligne d'article perdue |
| Même nombre de commandes | aucune commande perdue |
| Une ligne par commande | pas de duplication par les jointures |
| Un client par `customer_unique_id` | le bon identifiant client est utilisé |

`verify` écrit [`valeurs_reference.md`](valeurs_reference.md) : la valeur attendue de chaque KPI.

## 5. Dashboard Power BI

1. Ouvrez `powerbi/olist_dashboard.pbix`.
2. Si la connexion échoue : **Transformer les données → Paramètres de la source de données**, pointez vers `localhost:5432`, base `olist`, puis saisissez vos identifiants dans l'onglet **Base de données**.
3. **Accueil → Actualiser**.

✅ La carte « CA produits » affiche 13,59 M et la carte « Note moyenne » 4,09, comme dans [`valeurs_reference.md`](valeurs_reference.md).

Les 34 mesures DAX du rapport sont documentées dans [`mesures_dax.md`](mesures_dax.md).
