DROP TABLE IF EXISTS dwh.fait_lignes_commande, dwh.fait_commandes,
    dwh.dim_date, dwh.dim_client, dwh.dim_vendeur, dwh.dim_produit,
    dwh.dim_statut, dwh.dim_paiement CASCADE;

CREATE TABLE dwh.dim_date (
    date_key      INTEGER PRIMARY KEY,
    date          DATE NOT NULL UNIQUE,
    jour          SMALLINT NOT NULL,
    mois          SMALLINT NOT NULL,
    nom_mois      TEXT NOT NULL,
    annee_mois    TEXT NOT NULL,
    trimestre     SMALLINT NOT NULL,
    annee         SMALLINT NOT NULL,
    jour_semaine  SMALLINT NOT NULL,
    nom_jour      TEXT NOT NULL,
    est_weekend   BOOLEAN NOT NULL
);
COMMENT ON TABLE dwh.dim_date IS 'Calendrier complet 2016-2018, une ligne par jour';

CREATE TABLE dwh.dim_client (
    client_key          INTEGER PRIMARY KEY,
    customer_unique_id  TEXT NOT NULL UNIQUE,
    code_postal         TEXT,
    ville               TEXT,
    etat                TEXT,
    region              TEXT,
    latitude            NUMERIC(9,6),
    longitude           NUMERIC(9,6)
);
COMMENT ON TABLE dwh.dim_client IS 'Un client réel par customer_unique_id ; -1 = client inconnu';

CREATE TABLE dwh.dim_vendeur (
    vendeur_key  INTEGER PRIMARY KEY,
    seller_id    TEXT NOT NULL UNIQUE,
    code_postal  TEXT,
    ville        TEXT,
    etat         TEXT,
    region       TEXT,
    latitude     NUMERIC(9,6),
    longitude    NUMERIC(9,6)
);

CREATE TABLE dwh.dim_produit (
    produit_key      INTEGER PRIMARY KEY,
    product_id       TEXT NOT NULL UNIQUE,
    categorie        TEXT NOT NULL,
    categorie_pt     TEXT,
    poids_g          NUMERIC(10,1),
    volume_cm3       NUMERIC(12,1),
    nb_photos        SMALLINT
);

CREATE TABLE dwh.dim_statut (
    statut_key  INTEGER PRIMARY KEY,
    statut      TEXT NOT NULL UNIQUE
);

CREATE TABLE dwh.dim_paiement (
    paiement_key   INTEGER PRIMARY KEY,
    type_paiement  TEXT NOT NULL UNIQUE
);

CREATE TABLE dwh.fait_lignes_commande (
    order_id        TEXT NOT NULL,
    order_item_id   SMALLINT NOT NULL,
    date_achat_key  INTEGER NOT NULL REFERENCES dwh.dim_date(date_key),
    client_key      INTEGER NOT NULL REFERENCES dwh.dim_client(client_key),
    produit_key     INTEGER NOT NULL REFERENCES dwh.dim_produit(produit_key),
    vendeur_key     INTEGER NOT NULL REFERENCES dwh.dim_vendeur(vendeur_key),
    statut_key      INTEGER NOT NULL REFERENCES dwh.dim_statut(statut_key),
    prix            NUMERIC(10,2) NOT NULL,
    frais_port      NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);
COMMENT ON TABLE dwh.fait_lignes_commande IS 'Grain : un article d''une commande';

CREATE TABLE dwh.fait_commandes (
    order_id               TEXT PRIMARY KEY,
    date_achat_key         INTEGER NOT NULL REFERENCES dwh.dim_date(date_key),
    date_livraison_key     INTEGER REFERENCES dwh.dim_date(date_key),
    client_key             INTEGER NOT NULL REFERENCES dwh.dim_client(client_key),
    statut_key             INTEGER NOT NULL REFERENCES dwh.dim_statut(statut_key),
    paiement_key           INTEGER NOT NULL REFERENCES dwh.dim_paiement(paiement_key),
    montant_paye           NUMERIC(12,2),
    nb_articles            SMALLINT NOT NULL,
    nb_versements          SMALLINT,
    delai_livraison_jours  NUMERIC(6,1),
    retard_jours           INTEGER,
    est_en_retard          BOOLEAN,
    note_avis              SMALLINT
);
COMMENT ON TABLE dwh.fait_commandes IS 'Grain : une commande';

CREATE INDEX ON dwh.fait_lignes_commande (date_achat_key);
CREATE INDEX ON dwh.fait_lignes_commande (produit_key);
CREATE INDEX ON dwh.fait_lignes_commande (vendeur_key);
CREATE INDEX ON dwh.fait_commandes (date_achat_key);
CREATE INDEX ON dwh.fait_commandes (client_key);
