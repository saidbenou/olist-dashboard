-- KPI: CA produits total
SELECT ROUND(SUM(prix), 2) AS ca_produits FROM dwh.fait_lignes_commande;

-- KPI: Frais de port total
SELECT ROUND(SUM(frais_port), 2) AS frais_port FROM dwh.fait_lignes_commande;

-- KPI: Nombre de commandes
SELECT COUNT(*) AS nb_commandes FROM dwh.fait_commandes;

-- KPI: Panier moyen (CA produits / commandes contenant au moins un article)
SELECT ROUND(SUM(prix) / COUNT(DISTINCT order_id), 2) AS panier_moyen FROM dwh.fait_lignes_commande;

-- KPI: Montant payé total
SELECT ROUND(SUM(montant_paye), 2) AS montant_paye FROM dwh.fait_commandes;

-- KPI: CA produits par année
SELECT d.annee, ROUND(SUM(f.prix), 2) AS ca_produits
FROM dwh.fait_lignes_commande f JOIN dwh.dim_date d ON d.date_key = f.date_achat_key
GROUP BY d.annee ORDER BY d.annee;

-- KPI: Croissance du CA janvier-août 2018 vs janvier-août 2017
WITH p AS (
  SELECT d.annee, SUM(f.prix) AS ca
  FROM dwh.fait_lignes_commande f JOIN dwh.dim_date d ON d.date_key = f.date_achat_key
  WHERE d.mois BETWEEN 1 AND 8 AND d.annee IN (2017, 2018)
  GROUP BY d.annee)
SELECT ROUND((MAX(ca) FILTER (WHERE annee = 2018) / MAX(ca) FILTER (WHERE annee = 2017) - 1) * 100, 2)
       AS croissance_pct FROM p;

-- KPI: Délai moyen de livraison (commandes livrées, en jours)
SELECT ROUND(AVG(f.delai_livraison_jours), 2) AS delai_moyen_jours
FROM dwh.fait_commandes f JOIN dwh.dim_statut s ON s.statut_key = f.statut_key
WHERE s.statut = 'delivered';

-- KPI: Taux de retard (commandes livrées)
SELECT ROUND(AVG(CASE WHEN f.est_en_retard THEN 1.0 ELSE 0 END) * 100, 2) AS taux_retard_pct
FROM dwh.fait_commandes f JOIN dwh.dim_statut s ON s.statut_key = f.statut_key
WHERE s.statut = 'delivered' AND f.est_en_retard IS NOT NULL;

-- KPI: Note moyenne
SELECT ROUND(AVG(note_avis), 3) AS note_moyenne FROM dwh.fait_commandes;

-- KPI: Part d'avis négatifs (notes 1 et 2)
SELECT ROUND(AVG(CASE WHEN note_avis <= 2 THEN 1.0 ELSE 0 END) * 100, 2) AS avis_negatifs_pct
FROM dwh.fait_commandes WHERE note_avis IS NOT NULL;

-- KPI: Note moyenne selon le retard
SELECT est_en_retard, ROUND(AVG(note_avis), 3) AS note_moyenne, COUNT(*) AS nb_commandes
FROM dwh.fait_commandes WHERE est_en_retard IS NOT NULL
GROUP BY est_en_retard ORDER BY est_en_retard;

-- KPI: Clients uniques et taux de clients récurrents
WITH c AS (SELECT client_key, COUNT(*) AS nb FROM dwh.fait_commandes GROUP BY client_key)
SELECT COUNT(*) AS clients_uniques,
       ROUND(AVG(CASE WHEN nb > 1 THEN 1.0 ELSE 0 END) * 100, 2) AS taux_recurrents_pct
FROM c;

-- KPI: Top 10 des catégories par CA
SELECT p.categorie, ROUND(SUM(f.prix), 2) AS ca_produits
FROM dwh.fait_lignes_commande f JOIN dwh.dim_produit p ON p.produit_key = f.produit_key
GROUP BY p.categorie ORDER BY ca_produits DESC LIMIT 10;

-- KPI: Délai moyen et taux de retard par région du client
SELECT c.region,
       ROUND(AVG(f.delai_livraison_jours), 1) AS delai_moyen_jours,
       ROUND(AVG(CASE WHEN f.est_en_retard THEN 1.0 ELSE 0 END) * 100, 1) AS taux_retard_pct
FROM dwh.fait_commandes f
JOIN dwh.dim_client c ON c.client_key = f.client_key
JOIN dwh.dim_statut s ON s.statut_key = f.statut_key
WHERE s.statut = 'delivered' AND f.est_en_retard IS NOT NULL
GROUP BY c.region ORDER BY delai_moyen_jours DESC;
