# Mesures DAX du dashboard Olist

34 mesures, réparties en 6 dossiers. Pour chacune : la formule, le format à appliquer et la valeur à retrouver.

## Organisation

- Toutes les mesures sont dans une table dédiée **`_Mesures`**, rangées en dossiers d'affichage.
- L'ordre du fichier respecte les dépendances : certaines mesures en réutilisent d'autres (par exemple `Panier moyen` utilise `[CA produits]`).
- Chaque valeur attendue a été contrôlée dans un visuel *Carte*, sans filtre, contre [`valeurs_reference.md`](valeurs_reference.md).

> Rappel du modèle : `dim_date` a une relation **active** avec `fait_commandes[date_achat_key]` et `fait_lignes_commande[date_achat_key]`, et une relation **inactive** avec `fait_commandes[date_livraison_key]`. Les deux tables de faits ne sont **jamais** reliées entre elles.

## Sommaire

| # | Mesure | Dossier | Valeur attendue (sans filtre) |
|---|---|---|---|
| 1 | CA produits | Ventes | 13 591 643,70 |
| 2 | Frais de port | Ventes | 2 251 909,54 |
| 3 | CA total | Ventes | 15 843 553,24 |
| 4 | Part frais de port | Ventes | 14,21 % |
| 5 | Nb commandes | Ventes | 99 441 |
| 6 | Nb commandes (articles) | Ventes | 98 666 |
| 7 | Panier moyen | Ventes | 137,75 |
| 8 | Montant payé | Ventes | 16 008 872,12 |
| 9 | Nb articles | Ventes | 112 650 |
| 10 | Prix moyen article | Ventes | 120,65 |
| 11 | Frais de port moyen | Ventes | 19,99 |
| 12 | CA N-1 | Temps | 6 155 806,98 sur la ligne 2018 |
| 13 | Croissance CA % | Temps | 137,26 % (janv.–août 2018) |
| 14 | CA cumul annuel | Temps | repart de zéro chaque janvier |
| 15 | CA moyenne mobile 3 mois | Temps | courbe lissée |
| 16 | Montant payé par date de livraison | Temps | 15 421 831,43 |
| 17 | Commandes livrées (date livraison) | Temps | 96 476 |
| 18 | Commandes livrées | Logistique | 96 478 |
| 19 | Délai moyen (jours) | Logistique | 12,56 |
| 20 | Taux de retard | Logistique | 6,77 % |
| 21 | Note moyenne | Satisfaction | 4,09 |
| 22 | Part avis négatifs | Satisfaction | 14,69 % |
| 23 | Note moyenne en retard | Satisfaction | 2,27 |
| 24 | Note moyenne à temps | Satisfaction | 4,29 |
| 25 | Clients uniques | Clients et vendeurs | 96 096 |
| 26 | Clients récurrents | Clients et vendeurs | 2 997 |
| 27 | Taux clients récurrents | Clients et vendeurs | 3,12 % |
| 28 | Nb vendeurs actifs | Clients et vendeurs | 3 095 |
| 29 | Part du CA | Avancé | 100 % au total |
| 30 | Rang catégorie | Avancé | health_beauty = 1 |
| 31 | Note moyenne (produits) | Avancé | varie selon la catégorie |
| 32 | Taux de retard (produits) | Avancé | varie selon la catégorie |
| 33 | Part cumulée CA vendeurs | Avancé | monte jusqu'à 100 % |
| 34 | Part cumulée CA (rang) | Avancé | 82,7 % au rang 619 |

---

## Dossier « Ventes »

### 1. CA produits

```dax
CA produits = SUM ( fait_lignes_commande[prix] )
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : **13 591 643,70**.

### 2. Frais de port

```dax
Frais de port = SUM ( fait_lignes_commande[frais_port] )
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : **2 251 909,54**.

### 3. CA total

```dax
CA total = [CA produits] + [Frais de port]
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : **15 843 553,24**.

### 4. Part frais de port

```dax
Part frais de port = DIVIDE ( [Frais de port], [CA total] )
```
Format : pourcentage, 2 décimales.
Attendu : **14,21 %**.

### 5. Nb commandes

```dax
Nb commandes = COUNTROWS ( fait_commandes )
```
Format : nombre entier, séparateur de milliers.
Attendu : **99 441**.

Attention : `fait_commandes` n'est filtrée ni par les produits ni par les vendeurs. Pour une analyse par catégorie ou par vendeur, utilise la mesure 6.

### 6. Nb commandes (articles)

```dax
Nb commandes (articles) = DISTINCTCOUNT ( fait_lignes_commande[order_id] )
```
Format : nombre entier, séparateur de milliers.
Attendu : **98 666**.

Nombre de commandes contenant au moins un article. L'écart avec la mesure 5 correspond aux 775 commandes sans article. Celle-ci réagit aux filtres produit et vendeur.

### 7. Panier moyen

```dax
Panier moyen = DIVIDE ( [CA produits], [Nb commandes (articles)] )
```
Format : nombre décimal, 2 décimales.
Attendu : **137,75**.

### 8. Montant payé

```dax
Montant payé = SUM ( fait_commandes[montant_paye] )
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : **16 008 872,12**.

Il est un peu supérieur au CA total, notamment à cause des frais liés aux paiements en plusieurs fois. Pour le chiffre d'affaires, utilise `CA produits`.

### 9. Nb articles

```dax
Nb articles = COUNTROWS ( fait_lignes_commande )
```
Format : nombre entier, séparateur de milliers.
Attendu : **112 650**.

### 10. Prix moyen article

```dax
Prix moyen article = DIVIDE ( [CA produits], [Nb articles] )
```
Format : nombre décimal, 2 décimales.
Attendu : **120,65**.

### 11. Frais de port moyen

```dax
Frais de port moyen = AVERAGE ( fait_lignes_commande[frais_port] )
```
Format : nombre décimal, 2 décimales.
Attendu : **19,99**.

---

## Dossier « Temps »

Une carte sans filtre n'a pas de sens pour ces mesures. Elles se vérifient dans un **Tableau** avec `dim_date[annee]` (ou `annee_mois`).

### 12. CA N-1

```dax
CA N-1 = CALCULATE ( [CA produits], SAMEPERIODLASTYEAR ( dim_date[date] ) )
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : dans un tableau par `annee`, la ligne 2018 affiche **6 155 806,98**, soit le CA de 2017.

`dim_date` doit être marquée comme table de dates.

### 13. Croissance CA %

```dax
Croissance CA % = DIVIDE ( [CA produits] - [CA N-1], [CA N-1] )
```
Format : pourcentage, 2 décimales.
Attendu : **137,26 %**, avec un segment `dim_date[date]` réglé du 01/01/2018 au 31/08/2018.

### 14. CA cumul annuel

```dax
CA cumul annuel = TOTALYTD ( [CA produits], dim_date[date] )
```
Format : nombre décimal, 0 décimale, séparateur de milliers.
Attendu : dans un tableau par `annee_mois`, la valeur augmente chaque mois, puis repart de zéro en janvier. Celle de décembre 2017 est égale au CA de 2017 : **6 155 806,98**.

### 15. CA moyenne mobile 3 mois

```dax
CA moyenne mobile 3 mois =
VAR Periode = DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -3, MONTH )
RETURN DIVIDE ( CALCULATE ( [CA produits], Periode ), 3 )
```
Format : nombre décimal, 0 décimale, séparateur de milliers.
Attendu : dans une courbe par `annee_mois`, à côté de `CA produits`, une ligne plus lisse.

### 16. Montant payé par date de livraison

```dax
Montant payé par date de livraison =
CALCULATE (
    [Montant payé],
    USERELATIONSHIP ( fait_commandes[date_livraison_key], dim_date[date_key] )
)
```
Format : nombre décimal, 2 décimales, séparateur de milliers.
Attendu : **15 421 831,43**, plus bas que le Montant payé (mesure 8), parce que seules les commandes livrées ont une date de livraison.

Elle active la relation inactive : le montant est rattaché au mois de **livraison**, et non au mois d'achat.

### 17. Commandes livrées (date livraison)

```dax
Commandes livrées (date livraison) =
CALCULATE (
    [Nb commandes],
    USERELATIONSHIP ( fait_commandes[date_livraison_key], dim_date[date_key] )
)
```
Format : nombre entier, séparateur de milliers.
Attendu : **96 476** (commandes ayant une date de livraison).

Dans un graphique par mois, elle compte les commandes **arrivées** ce mois-là.

---

## Dossier « Logistique »

### 18. Commandes livrées

```dax
Commandes livrées = CALCULATE ( [Nb commandes], dim_statut[statut] = "delivered" )
```
Format : nombre entier, séparateur de milliers.
Attendu : **96 478**.

Elle compte les commandes au statut `delivered`. Le chiffre diffère de 2 de la mesure 17, à cause de quelques commandes aux dates incohérentes dans la source.

### 19. Délai moyen (jours)

```dax
Délai moyen (jours) =
CALCULATE ( AVERAGE ( fait_commandes[delai_livraison_jours] ), dim_statut[statut] = "delivered" )
```
Format : nombre décimal, 2 décimales.
Attendu : **12,56**.

### 20. Taux de retard

```dax
Taux de retard =
VAR Livrees =
    CALCULATE ( COUNTROWS ( fait_commandes ),
        dim_statut[statut] = "delivered", NOT ISBLANK ( fait_commandes[est_en_retard] ) )
VAR EnRetard =
    CALCULATE ( COUNTROWS ( fait_commandes ),
        dim_statut[statut] = "delivered", fait_commandes[est_en_retard] = TRUE () )
RETURN DIVIDE ( EnRetard, Livrees )
```
Format : pourcentage, 2 décimales.
Attendu : **6,77 %**.

---

## Dossier « Satisfaction »

### 21. Note moyenne

```dax
Note moyenne = AVERAGE ( fait_commandes[note_avis] )
```
Format : nombre décimal, 2 décimales.
Attendu : **4,09**.

### 22. Part avis négatifs

```dax
Part avis négatifs =
DIVIDE (
    CALCULATE ( COUNTROWS ( fait_commandes ), fait_commandes[note_avis] IN { 1, 2 } ),
    CALCULATE ( COUNTROWS ( fait_commandes ), NOT ISBLANK ( fait_commandes[note_avis] ) )
)
```
Format : pourcentage, 2 décimales.
Attendu : **14,69 %**.

Piège rencontré : il faut `IN { 1, 2 }` et non `<= 2`. En DAX, une note vide vaut 0 dans une comparaison : `<= 2` compterait les 768 commandes sans avis comme négatives, et la carte afficherait **15,47 %**.

### 23. Note moyenne en retard

```dax
Note moyenne en retard = CALCULATE ( [Note moyenne], fait_commandes[est_en_retard] = TRUE () )
```
Format : nombre décimal, 2 décimales.
Attendu : **2,27**.

### 24. Note moyenne à temps

```dax
Note moyenne à temps = CALCULATE ( [Note moyenne], fait_commandes[est_en_retard] == FALSE () )
```
Format : nombre décimal, 2 décimales.
Attendu : **4,29**.

Piège rencontré : il faut `==` (égalité stricte). En DAX, `BLANK () = FALSE ()` est vrai : avec un simple `=`, les commandes non livrées (note moyenne 1,75) seraient comptées « à temps », et la carte afficherait **4,21**.

---

## Dossier « Clients et vendeurs »

### 25. Clients uniques

```dax
Clients uniques = DISTINCTCOUNT ( fait_commandes[client_key] )
```
Format : nombre entier, séparateur de milliers.
Attendu : **96 096**.

### 26. Clients récurrents

```dax
Clients récurrents =
COUNTROWS (
    FILTER ( VALUES ( fait_commandes[client_key] ), CALCULATE ( COUNTROWS ( fait_commandes ) ) > 1 )
)
```
Format : nombre entier, séparateur de milliers.
Attendu : **2 997** (clients ayant passé au moins 2 commandes).

### 27. Taux clients récurrents

```dax
Taux clients récurrents = DIVIDE ( [Clients récurrents], [Clients uniques] )
```
Format : pourcentage, 2 décimales.
Attendu : **3,12 %**.

### 28. Nb vendeurs actifs

```dax
Nb vendeurs actifs = DISTINCTCOUNT ( fait_lignes_commande[vendeur_key] )
```
Format : nombre entier, séparateur de milliers.
Attendu : **3 095**.

---

## Dossier « Avancé »

Ces mesures se vérifient dans un **Tableau** avec `dim_produit[categorie]` et `CA produits`.

### 29. Part du CA

```dax
Part du CA =
DIVIDE ( [CA produits], CALCULATE ( [CA produits], ALLSELECTED ( dim_produit[categorie] ) ) )
```
Format : pourcentage, 2 décimales.
Attendu : le total de la colonne fait **100 %**, et `health_beauty` ≈ **9,26 %**.

### 30. Rang catégorie

```dax
Rang catégorie =
IF (
    HASONEVALUE ( dim_produit[categorie] ),
    RANKX ( ALL ( dim_produit[categorie] ), [CA produits], , DESC, DENSE )
)
```
Format : nombre entier.
Attendu : `health_beauty` = **1**, `watches_gifts` = **2**, `bed_bath_table` = **3**.

### 31. Note moyenne (produits)

`fait_commandes` n'est pas reliée aux produits ni aux vendeurs. `[Note moyenne]` affiche donc **4,09 sur toutes les lignes** d'un tableau par catégorie. Cette mesure transmet le filtre produit ou vendeur aux commandes concernées.

```dax
Note moyenne (produits) =
CALCULATE (
    [Note moyenne],
    TREATAS ( VALUES ( fait_lignes_commande[order_id] ), fait_commandes[order_id] )
)
```
Format : nombre décimal, 2 décimales.
Attendu : une note **différente** pour chaque catégorie ou vendeur, et environ 4,09 sans filtre.

### 32. Taux de retard (produits)

```dax
Taux de retard (produits) =
CALCULATE (
    [Taux de retard],
    TREATAS ( VALUES ( fait_lignes_commande[order_id] ), fait_commandes[order_id] )
)
```
Format : pourcentage, 2 décimales.
Attendu : un taux **différent** pour chaque catégorie ou vendeur, et environ 6,77 % sans filtre.

Les mesures 31 et 32 s'utilisent dès qu'une catégorie ou un vendeur est sur l'axe d'un visuel.

### 33. Part cumulée CA vendeurs

```dax
Part cumulée CA vendeurs =
VAR CAVendeur = [CA produits]
VAR Vendeurs = ADDCOLUMNS ( ALLSELECTED ( dim_vendeur[seller_id] ), "@ca", [CA produits] )
VAR Cumul = SUMX ( FILTER ( Vendeurs, [@ca] >= CAVendeur ), [@ca] )
RETURN DIVIDE ( Cumul, SUMX ( Vendeurs, [@ca] ) )
```
Format : pourcentage, 1 décimale.
Attendu : dans un tableau `dim_vendeur[seller_id]` trié par CA décroissant, la valeur augmente ligne après ligne jusqu'à **100 %**.

Cette mesure sert pour un tableau par `seller_id`. Pour le graphique de Pareto, utilise plutôt la mesure 34.

### 34. Part cumulée CA (rang)

Nécessite deux colonnes calculées dans `dim_vendeur` :

```dax
CA vendeur = CALCULATE ( SUM ( fait_lignes_commande[prix] ) )
```

```dax
Rang vendeur =
IF (
    dim_vendeur[vendeur_key] = -1,
    BLANK (),
    RANKX (
        FILTER ( dim_vendeur, dim_vendeur[vendeur_key] <> -1 ),
        dim_vendeur[CA vendeur], , DESC, Skip
    )
)
```

```dax
Part cumulée CA (rang) =
VAR RangActuel = MAX ( dim_vendeur[Rang vendeur] )
VAR Total = CALCULATE ( [CA produits], ALLSELECTED ( dim_vendeur ) )
VAR Cumul =
    CALCULATE (
        [CA produits],
        ALLSELECTED ( dim_vendeur ),
        dim_vendeur[Rang vendeur] <= RangActuel
    )
RETURN
    IF ( NOT ISBLANK ( RangActuel ), DIVIDE ( Cumul, Total ) )
```
Format : pourcentage, 1 décimale.
Attendu (sans filtre) : rang 310 → **67,6 %**, rang 619 → **82,7 %**, rang 1 548 → **96,8 %**, rang 3 095 → **100 %**.

Pour le graphique de Pareto : `Rang vendeur` en axe X continu, `CA produits` en colonnes et cette mesure en ligne.
