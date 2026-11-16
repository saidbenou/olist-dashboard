# Rapport qualité des données brutes Olist

Généré par `python -m etl.explore_raw` à partir de `data/raw/` (9 fichiers).

## 1. Profil des tables

### customers

- Lignes : **99,441** — colonnes : **5**
- Doublons sur la clé naturelle `customer_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| customer_id | object | 0 | 0.0 |
| customer_unique_id | object | 0 | 0.0 |
| customer_zip_code_prefix | object | 0 | 0.0 |
| customer_city | object | 0 | 0.0 |
| customer_state | object | 0 | 0.0 |

### geolocation

- Lignes : **1,000,163** — colonnes : **5**
- Pas de clé naturelle (table de référence géographique)
- Lignes entièrement dupliquées : **261,831**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| geolocation_zip_code_prefix | object | 0 | 0.0 |
| geolocation_lat | float64 | 0 | 0.0 |
| geolocation_lng | float64 | 0 | 0.0 |
| geolocation_city | object | 0 | 0.0 |
| geolocation_state | object | 0 | 0.0 |

### orders

- Lignes : **99,441** — colonnes : **8**
- Doublons sur la clé naturelle `order_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| order_id | object | 0 | 0.0 |
| customer_id | object | 0 | 0.0 |
| order_status | object | 0 | 0.0 |
| order_purchase_timestamp | datetime64[ns] | 0 | 0.0 |
| order_approved_at | datetime64[ns] | 160 | 0.16 |
| order_delivered_carrier_date | datetime64[ns] | 1783 | 1.79 |
| order_delivered_customer_date | datetime64[ns] | 2965 | 2.98 |
| order_estimated_delivery_date | datetime64[ns] | 0 | 0.0 |

### order_items

- Lignes : **112,650** — colonnes : **7**
- Doublons sur la clé naturelle `order_id, order_item_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| order_id | object | 0 | 0.0 |
| order_item_id | int64 | 0 | 0.0 |
| product_id | object | 0 | 0.0 |
| seller_id | object | 0 | 0.0 |
| shipping_limit_date | object | 0 | 0.0 |
| price | float64 | 0 | 0.0 |
| freight_value | float64 | 0 | 0.0 |

### order_payments

- Lignes : **103,886** — colonnes : **5**
- Doublons sur la clé naturelle `order_id, payment_sequential` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| order_id | object | 0 | 0.0 |
| payment_sequential | int64 | 0 | 0.0 |
| payment_type | object | 0 | 0.0 |
| payment_installments | int64 | 0 | 0.0 |
| payment_value | float64 | 0 | 0.0 |

### order_reviews

- Lignes : **99,224** — colonnes : **7**
- Doublons sur la clé naturelle `review_id, order_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| review_id | object | 0 | 0.0 |
| order_id | object | 0 | 0.0 |
| review_score | int64 | 0 | 0.0 |
| review_comment_title | object | 87656 | 88.34 |
| review_comment_message | object | 58247 | 58.7 |
| review_creation_date | object | 0 | 0.0 |
| review_answer_timestamp | object | 0 | 0.0 |

### products

- Lignes : **32,951** — colonnes : **9**
- Doublons sur la clé naturelle `product_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| product_id | object | 0 | 0.0 |
| product_category_name | object | 610 | 1.85 |
| product_name_lenght | float64 | 610 | 1.85 |
| product_description_lenght | float64 | 610 | 1.85 |
| product_photos_qty | float64 | 610 | 1.85 |
| product_weight_g | float64 | 2 | 0.01 |
| product_length_cm | float64 | 2 | 0.01 |
| product_height_cm | float64 | 2 | 0.01 |
| product_width_cm | float64 | 2 | 0.01 |

### sellers

- Lignes : **3,095** — colonnes : **4**
- Doublons sur la clé naturelle `seller_id` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| seller_id | object | 0 | 0.0 |
| seller_zip_code_prefix | object | 0 | 0.0 |
| seller_city | object | 0 | 0.0 |
| seller_state | object | 0 | 0.0 |

### category_translation

- Lignes : **71** — colonnes : **2**
- Doublons sur la clé naturelle `product_category_name` : **0**
- Lignes entièrement dupliquées : **0**

| colonne | type | manquants | % manquants |
|---|---|---|---|
| product_category_name | object | 0 | 0.0 |
| product_category_name_english | object | 0 | 0.0 |

## 2. Cohérence des clés entre tables

| contrôle | lignes orphelines | lignes testées | % |
|---|---|---|---|
| Commandes sans client | 0 | 99441 | 0.0 |
| Articles sans commande | 0 | 112650 | 0.0 |
| Articles sans produit | 0 | 112650 | 0.0 |
| Articles sans vendeur | 0 | 112650 | 0.0 |
| Paiements sans commande | 0 | 103886 | 0.0 |
| Avis sans commande | 0 | 99224 | 0.0 |
| Catégories produit sans traduction | 13 | 32951 | 0.04 |
| Codes postaux clients absents de la géolocalisation | 278 | 99441 | 0.28 |
| Codes postaux vendeurs absents de la géolocalisation | 7 | 3095 | 0.23 |
| Commandes sans article | 775 | 99441 | 0.78 |
| Commandes sans paiement | 1 | 99441 | 0.0 |
| Commandes sans avis | 768 | 99441 | 0.77 |

Catégories sans traduction : `pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`

## 3. Points connus

### 3.1 Plusieurs customer_id pour un même customer_unique_id

- customer_id : **99,441** — customer_unique_id : **96,096**
- Clients réels avec plusieurs customer_id : **2,997 (3.12%)**
- Maximum de customer_id pour un client : **17**

- Clients réels avec plusieurs adresses (code postal, ville ou état différents) : **252**

### 3.2 Plusieurs avis par commande

- Commandes avec plusieurs avis : **547 (0.55%)**
- review_id utilisés sur plusieurs commandes : **789**

### 3.3 Doublons de géolocalisation par préfixe de code postal

- Lignes : **1,000,163** — préfixes distincts : **19,015**
- Lignes entièrement dupliquées : **261,831 (26.18%)**
- Points par préfixe : médiane **29**, maximum **1,146**
- Préfixes rattachés à plusieurs états : **8**
- Coordonnées hors du Brésil : **42**
- Orthographes de ville distinctes : **8,011** (accents et casse non homogènes)

### 3.4 Produits sans catégorie

- Produits sans catégorie : **610 (1.85%)**
- Produits sans poids ou dimensions : **2**
- Produits de poids 0 g : **4**

- Articles vendus dont le produit n'a pas de catégorie : **1,603 (1.42%)**

### 3.5 Distribution des commandes par mois

- Période couverte : **2016-09-04** au **2018-10-17**

| mois | commandes |
|---|---|
| 2016-09 | 4 |
| 2016-10 | 324 |
| 2016-12 | 1 |
| 2017-01 | 800 |
| 2017-02 | 1780 |
| 2017-03 | 2682 |
| 2017-04 | 2404 |
| 2017-05 | 3700 |
| 2017-06 | 3245 |
| 2017-07 | 4026 |
| 2017-08 | 4331 |
| 2017-09 | 4285 |
| 2017-10 | 4631 |
| 2017-11 | 7544 |
| 2017-12 | 5673 |
| 2018-01 | 7269 |
| 2018-02 | 6728 |
| 2018-03 | 7211 |
| 2018-04 | 6939 |
| 2018-05 | 6873 |
| 2018-06 | 6167 |
| 2018-07 | 6292 |
| 2018-08 | 6512 |
| 2018-09 | 16 |
| 2018-10 | 4 |

### 3.6 Statuts et cohérence des dates de commande

| order_status | commandes |
|---|---|
| delivered | 96478 |
| shipped | 1107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

| contrôle | commandes |
|---|---|
| Livrées sans date de livraison client | 8 |
| Non livrées avec date de livraison client | 6 |
| Livraison client avant l'achat | 0 |
| Remise au transporteur avant l'achat | 166 |
| Approbation avant l'achat | 0 |

### 3.7 Paiements

- Paiements de montant 0 : **9**
- Paiements de type `not_defined` : **3**
- Paiements avec 0 versement : **2**
- Commandes payées avec plusieurs moyens de paiement : **2,246**

- Commandes où paiements ≠ prix + port (écart > 1 R$) : **249 (0.25%)**
