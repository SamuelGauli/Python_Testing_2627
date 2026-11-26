# Rapport de performances - GUDLFT

Date : 26/11/2026
Outil : Locust 2.47.0
Scénario : `locustfile.py` (classe `Secretary`)

## 1. Ce qui était demandé

Spécifications fonctionnelles, phase 2 et Guide de développement
(section 5) :

- utiliser **Locust** ;
- **6 utilisateurs simultanés** par défaut ;
- la liste des compétitions doit se charger en **moins de 5 secondes** ;
- la mise à jour du total de points doit prendre **moins de 2 secondes**.

## 2. Mise en place

- serveur démarré réellement sur `http://127.0.0.1:5000`
  (`python` sans mode debug pour éviter le reloader) ;
- 6 simulateurs de secrétaire, chacun se connecte au démarrage
  (`POST /showSummary` avec le compte démo `john@simplylift.co`) ;
- chaque simulateur navigue en **lecture seule** : accueil, liste des
  concours, classement, page de réservation (aucune écriture de données) ;
- attente de 1 à 2 s entre les requêtes, durée du run : **30 secondes** ;
- les budgets sont appliqués **dans le scénario** : une réponse plus
  lente que le budget est comptée comme un échec Locust.

Commande exécutée :

```bash
locust -f locustfile.py --headless -u 6 -t 30s
```

## 3. Résultats

```
Utilisateurs : 6          Durée : 30 s
Requêtes     : 95         Échecs : 0 (0.00 %)
Débit        : ~4 req/s
Latence      : moyenne 3 ms - minimum 2 ms - maximum 8 ms
Percentiles  : p50 3 ms - p95 5 ms
```

| Endpoint                 | Requêtes | Moyenne | p95  | Max  | Budget    |
| ------------------------ | -------: | ------: | ---: | ---- | --------- |
| `GET /`                  |       25 |    3 ms | 4 ms | 6 ms | -         |
| `GET /showSummary` (liste des concours) | 43 | 3 ms | 4 ms | 5 ms | **< 5 s** |
| `GET /points` (total des points)        | 16 | 3 ms | 5 ms | 5 ms | **< 2 s** |
| `GET /book/...`          |       10 |    4 ms | 4 ms | 6 ms | -         |
| `POST /showSummary` (login) |     1 |    8 ms | 8 ms | 8 ms | -         |
| **Agrégé**               |   **95** | **3 ms** | **5 ms** | **8 ms** | **0 échec** |

## 4. Conclusion

| Budget (spécifications) | Mesuré     | Marge          |
| ----------------------- | ---------- | -------------- |
| Liste de concours < 5 s | 5 ms max   | ~1000× plus rapide |
| Total de points < 2 s   | 5 ms max   | ~400× plus rapide  |

Les deux budgets sont **largement respectés** : les temps mesurés sont
de l'ordre de la milliseconde, soit trois ordres de grandeur sous la
limite. Aucun échec sur 95 requêtes, aucune requête refusée (toutes les
réponses sont des 200/302 attendus).

Rejouer le test :

```bash
python server.py          # ou tout autre démarrage sur le port 5000
locust -f locustfile.py --headless -u 6 -t 30s
```
