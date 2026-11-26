# Rapport de tests - GUDLFT

Date : 26/11/2026
Branche : `feature/tests-pytest-coverage`
Outils : pytest 9.1.1, pytest-cov 7.1.0, coverage 7.17.0, flake8 7.4.1

## 1. Ce qui était demandé

D'après le **Guide de développement** des spécifications fonctionnelles
(section 4) et le **README** (section 5) :

- tous les tests dans un dossier `tests/`, exécutables en ligne de commande ;
- séparer les tests **unitaires / d'intégration / fonctionnels** dans des
  dossiers distincts ;
- écrire **au moins deux fois plus de tests unitaires** que de tests
  d'intégration ou fonctionnels ;
- couvrir au minimum **60 % du code** ;
- tester les **happy paths et les sad paths** de toutes les
  fonctionnalités ;
- flake8 sans erreur (section 6 du README) ;
- produire un rapport de test et un rapport de performances.

## 2. Stratégie retenue

```
tests/
├── conftest.py          fixtures partagées (isolation, client, login)
├── unit/                45 tests - logique pure, aucun HTTP
│   ├── test_loaders.py              (7)
│   ├── test_savers.py               (5)
│   ├── test_competition_is_past.py  (5)
│   ├── test_current_club.py         (4)
│   ├── test_login_required.py       (4)
│   └── test_views.py                (20)
├── integration/         12 tests - client HTTP complet, un parcours à la fois
│   ├── test_auth_flow.py            (4)
│   ├── test_booking_flow.py         (3)
│   ├── test_purchase_flow.py        (4)
│   └── test_points_page.py          (1)
└── functional/          11 tests - parcours bout en bout + tous les sad paths
    ├── test_journey.py              (2)
    └── test_sad_paths.py            (9)
```

**Ratio unitaires / autres : 45 / 23 ≈ 2×**, comme demandé par les
spécifications.

### Isolation des données (le point clé)

L'application écrit dans `clubs.json` et `competitions.json` après chaque
achat. Pour que les tests ne salissent jamais les vraies données :

1. la fixture `isolated_data` (automatique pour **chaque** test) copie les
   deux fichiers dans un `tmp_path` pytest ;
2. elle redirige `server.CLUBS_FILE` et `server.COMPETITIONS_FILE` vers ces
   copies (`monkeypatch`) ;
3. elle sauvegarde les listes en mémoire `clubs` / `competitions`, puis les
   restaure après le test.

Résultat : les tests peuvent acheter, écrire sur disque et muter les
données autant qu'ils veulent - les fichiers du projet ne sont **jamais**
modifiés (vérifié : `git status` sur les JSON reste inchangé après la
série complète).

### Fixtures

- `app` : application en mode `TESTING` ;
- `client` : client HTTP Flask (cookies de session conservés) ;
- `login(email)` : se connecte via `POST /showSummary`.

## 3. Comment exécuter les tests

```bash
# tous les tests
pytest tests/

# avec la couverture de code
pytest --cov=server --cov-report=term-missing

# par niveau
pytest tests/unit/
pytest tests/integration/
pytest tests/functional/
```

## 4. Résultats

### Pytest

```
68 passed in ~1.0s
```

| Dossier         | Tests | Rôle                                  |
| --------------- | ----: | ------------------------------------- |
| `tests/unit/`   |    45 | loaders, sauvegardes, règles, vues    |
| `tests/integration/` | 12 | flux HTTP complets (login, book, buy) |
| `tests/functional/`  | 11 | parcours bout en bout + sad paths     |
| **Total**       |    **68** | **tous verts**                   |

### Couverture (objectif : ≥ 60 %)

```
Name        Stmts   Miss  Cover   Missing
-----------------------------------------
server.py     137      1    99%   206
TOTAL         137      1    99%
```

**99 %** de couverture. La seule ligne non couverte est la ligne 206
(`app.run(debug=True)`), qui n'est pas exécutable dans un test.

### Happy paths couverts

- connexion avec un email connu → résumé du club ;
- réservation d'un concours à venir → formulaire ;
- achat valide → confirmation, décrément des lieux **et** des points,
  écriture sur disque relue après coup ;
- classement public consultable sans connexion ;
- déconnexion propre.

### Sad paths couverts

- email inconnu sur la page de connexion ;
- accès sans connexion aux pages protégées ;
- réservation pour un autre club (usurpation) ;
- club ou concours inconnu dans l'URL ;
- concours terminé (badge « Finished » + refus serveur) ;
- nombre de places : texte, 0, négatif, > 12, > disponibles, concours complet ;
- points insuffisants ;
- ressources inconnues sur `POST /purchasePlaces` ;
- re-soumission F5 (pattern Post/Redirect/Get : la redirection évite le
  double achat - vérifié par le fait que le POST n'est jamais rendu
  directement).

## 5. Qualité de code

```
flake8 .      → 0 erreur (rapport : flake8-report.txt, fichier vide
                 = sortie attendue « no output at all »)
```

Les tests et le `locustfile.py` respectent la limite de 79 caractères.

## 6. Notes

- Aucun fichier de données du projet n'a été modifié par la suite de
  tests (les JSON ont été laissés dans l'état choisi par l'utilisateur).
- Les performances sont détaillées dans
  `docs/rapport-de-performances.md`.
